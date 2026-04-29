from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from app.exchange.core import (
    AMMValidationError,
    DECIMAL_ONE,
    DECIMAL_ZERO,
    decimal_sqrt,
    format_decimal,
    impermanent_loss_pct,
    mint_liquidity_shares,
    quote_exact_in,
    remove_liquidity_amounts,
    to_decimal,
)
from app.models import db
from app.models.exchange import ExchangeEvent, ExchangeToken, LiquidityPool, LiquidityPosition, WalletBalance


DEMO_TOKENS = [
    {'symbol': 'ETH', 'name': 'Ether', 'decimals': 18, 'display_order': 1},
    {'symbol': 'BTC', 'name': 'Bitcoin', 'decimals': 8, 'display_order': 2},
    {'symbol': 'MANBO', 'name': 'Manbo Token', 'decimals': 18, 'display_order': 3},
    {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6, 'display_order': 4},
]

DEMO_POOLS = [
    {
        'id': 'eth-usdc',
        'name': 'ETH / USDC',
        'token0_symbol': 'ETH',
        'token1_symbol': 'USDC',
        'reserve0': Decimal('500'),
        'reserve1': Decimal('1000000'),
        'fee_rate': Decimal('0.003'),
    },
    {
        'id': 'btc-usdc',
        'name': 'BTC / USDC',
        'token0_symbol': 'BTC',
        'token1_symbol': 'USDC',
        'reserve0': Decimal('80'),
        'reserve1': Decimal('5200000'),
        'fee_rate': Decimal('0.003'),
    },
    {
        'id': 'manbo-usdc',
        'name': 'MANBO / USDC',
        'token0_symbol': 'MANBO',
        'token1_symbol': 'USDC',
        'reserve0': Decimal('1000000'),
        'reserve1': Decimal('250000'),
        'fee_rate': Decimal('0.003'),
    },
]

DEFAULT_FAUCET = {
    'ETH': Decimal('10'),
    'BTC': Decimal('1'),
    'MANBO': Decimal('10000'),
    'USDC': Decimal('50000'),
}


class ExchangeError(Exception):
    def __init__(self, message, code=1, status=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


def seed_exchange_data(reset=False):
    if reset:
        ExchangeEvent.query.delete()
        LiquidityPosition.query.delete()
        WalletBalance.query.delete()
        LiquidityPool.query.delete()
        ExchangeToken.query.delete()

    for token in DEMO_TOKENS:
        existing = db.session.get(ExchangeToken, token['symbol'])
        if existing is None:
            db.session.add(ExchangeToken(**token))

    db.session.flush()

    for pool_data in DEMO_POOLS:
        existing = db.session.get(LiquidityPool, pool_data['id'])
        if existing is not None:
            continue
        total_lp_shares = decimal_sqrt(pool_data['reserve0'] * pool_data['reserve1'])
        db.session.add(
            LiquidityPool(
                **pool_data,
                total_lp_shares=total_lp_shares,
                cumulative_fee0=DECIMAL_ZERO,
                cumulative_fee1=DECIMAL_ZERO,
            )
        )
    db.session.commit()


def list_tokens():
    return [
        _serialize_token(token)
        for token in ExchangeToken.query.order_by(ExchangeToken.display_order.asc()).all()
    ]


def list_pools():
    return [_serialize_pool(pool) for pool in LiquidityPool.query.order_by(LiquidityPool.id.asc()).all()]


def get_pool_detail(pool_id):
    pool = _get_pool(pool_id)
    return _serialize_pool(pool, include_recent=True)


def list_wallet(user_id):
    _ensure_wallet_rows(user_id)
    balances = (
        WalletBalance.query.join(ExchangeToken, WalletBalance.token_symbol == ExchangeToken.symbol)
        .filter(WalletBalance.user_id == user_id)
        .order_by(ExchangeToken.display_order.asc())
        .all()
    )
    return [_serialize_balance(balance) for balance in balances]


def grant_faucet(user_id, amounts=None):
    resolved_amounts = _resolve_amount_map(amounts) if amounts else DEFAULT_FAUCET
    changed = []
    for symbol, amount in resolved_amounts.items():
        token = db.session.get(ExchangeToken, symbol)
        if token is None:
            raise ExchangeError(f'不支持的资产: {symbol}', status=404)
        _require_positive(amount, f'{symbol} faucet amount')
        balance = _get_or_create_balance(user_id, symbol)
        balance.balance = _decimal(balance.balance) + amount
        changed.append({'symbol': symbol, 'amount': format_decimal(amount, 6)})
    _record_event(
        user_id=user_id,
        event_type='faucet',
        pool_id=None,
        summary='领取模拟资产',
        details={'amounts': changed},
    )
    db.session.commit()
    return {'wallet': list_wallet(user_id), 'granted': changed}


def get_swap_quote(pool_id, token_in_symbol, amount_in):
    pool = _get_pool(pool_id)
    quote = _quote_for_pool(pool, token_in_symbol, amount_in)
    return _serialize_quote(pool, token_in_symbol, quote)


def execute_swap(user_id, payload):
    pool = _get_pool(payload.get('pool_id'))
    token_in_symbol = str(payload.get('token_in_symbol', '')).upper()
    min_amount_out = payload.get('min_amount_out')
    quote = _quote_for_pool(pool, token_in_symbol, payload.get('amount_in'))
    amount_in = quote['amount_in']
    amount_out = quote['amount_out']
    token_out_symbol = _token_out_symbol(pool, token_in_symbol)

    if min_amount_out not in (None, ''):
        minimum = to_decimal(min_amount_out, 'min_amount_out')
        if amount_out < minimum:
            raise ExchangeError('滑点保护触发：预期输出低于最小可接受数量')

    input_balance = _get_or_create_balance(user_id, token_in_symbol)
    if _decimal(input_balance.balance) < amount_in:
        raise ExchangeError(f'{token_in_symbol}余额不足')
    output_balance = _get_or_create_balance(user_id, token_out_symbol)

    try:
        input_balance.balance = _decimal(input_balance.balance) - amount_in
        output_balance.balance = _decimal(output_balance.balance) + amount_out
        _apply_swap_to_pool(pool, token_in_symbol, quote)
        event_details = _serialize_quote(pool, token_in_symbol, quote)
        event_details['token_out_symbol'] = token_out_symbol
        _record_event(
            user_id=user_id,
            event_type='swap',
            pool_id=pool.id,
            summary=f"Swap {format_decimal(amount_in, 6)} {token_in_symbol} -> {format_decimal(amount_out, 6)} {token_out_symbol}",
            details=event_details,
        )
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ExchangeError('交易提交失败') from exc

    return {
        'quote': _serialize_quote(pool, token_in_symbol, quote),
        'pool': _serialize_pool(pool),
        'wallet': list_wallet(user_id),
        'event': _serialize_event(ExchangeEvent.query.order_by(ExchangeEvent.id.desc()).first()),
    }


def add_liquidity(user_id, payload):
    pool = _get_pool(payload.get('pool_id'))
    amount0 = to_decimal(payload.get('amount0'), 'amount0')
    amount1 = to_decimal(payload.get('amount1'), 'amount1')
    try:
        minted_shares = mint_liquidity_shares(
            _decimal(pool.reserve0),
            _decimal(pool.reserve1),
            _decimal(pool.total_lp_shares),
            amount0,
            amount1,
        )
    except AMMValidationError as exc:
        raise ExchangeError(str(exc)) from exc

    balance0 = _get_or_create_balance(user_id, pool.token0_symbol)
    balance1 = _get_or_create_balance(user_id, pool.token1_symbol)
    if _decimal(balance0.balance) < amount0:
        raise ExchangeError(f'{pool.token0_symbol}余额不足')
    if _decimal(balance1.balance) < amount1:
        raise ExchangeError(f'{pool.token1_symbol}余额不足')

    position = _get_or_create_position(user_id, pool.id)
    try:
        balance0.balance = _decimal(balance0.balance) - amount0
        balance1.balance = _decimal(balance1.balance) - amount1
        pool.reserve0 = _decimal(pool.reserve0) + amount0
        pool.reserve1 = _decimal(pool.reserve1) + amount1
        pool.total_lp_shares = _decimal(pool.total_lp_shares) + minted_shares
        position.lp_shares = _decimal(position.lp_shares) + minted_shares
        position.deposited0 = _decimal(position.deposited0) + amount0
        position.deposited1 = _decimal(position.deposited1) + amount1
        _record_event(
            user_id=user_id,
            event_type='add_liquidity',
            pool_id=pool.id,
            summary=f"Add liquidity {pool.name}",
            details={
                'amount0': format_decimal(amount0, 6),
                'amount1': format_decimal(amount1, 6),
                'minted_lp_shares': format_decimal(minted_shares, 12),
            },
        )
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ExchangeError('添加流动性失败') from exc

    return {
        'pool': _serialize_pool(pool),
        'position': _serialize_position(position),
        'wallet': list_wallet(user_id),
    }


def remove_liquidity(user_id, payload):
    pool = _get_pool(payload.get('pool_id'))
    position = LiquidityPosition.query.filter_by(user_id=user_id, pool_id=pool.id).first()
    if position is None or _decimal(position.lp_shares) <= DECIMAL_ZERO:
        raise ExchangeError('当前用户没有该池子的LP份额')

    current_position_shares = _decimal(position.lp_shares)
    shares = _resolve_remove_shares(payload, current_position_shares)
    if shares > current_position_shares:
        raise ExchangeError('撤出的LP份额不能超过当前持仓')

    try:
        amounts = remove_liquidity_amounts(
            _decimal(pool.reserve0),
            _decimal(pool.reserve1),
            _decimal(pool.total_lp_shares),
            shares,
        )
    except AMMValidationError as exc:
        raise ExchangeError(str(exc)) from exc

    balance0 = _get_or_create_balance(user_id, pool.token0_symbol)
    balance1 = _get_or_create_balance(user_id, pool.token1_symbol)
    reduce_ratio = shares / current_position_shares
    try:
        pool.reserve0 = _decimal(pool.reserve0) - amounts['amount0']
        pool.reserve1 = _decimal(pool.reserve1) - amounts['amount1']
        pool.total_lp_shares = _decimal(pool.total_lp_shares) - shares
        balance0.balance = _decimal(balance0.balance) + amounts['amount0']
        balance1.balance = _decimal(balance1.balance) + amounts['amount1']
        position.lp_shares = current_position_shares - shares
        position.deposited0 = max(_decimal(position.deposited0) * (DECIMAL_ONE - reduce_ratio), DECIMAL_ZERO)
        position.deposited1 = max(_decimal(position.deposited1) * (DECIMAL_ONE - reduce_ratio), DECIMAL_ZERO)
        _record_event(
            user_id=user_id,
            event_type='remove_liquidity',
            pool_id=pool.id,
            summary=f"Remove liquidity {pool.name}",
            details={
                'burned_lp_shares': format_decimal(shares, 12),
                'amount0': format_decimal(amounts['amount0'], 6),
                'amount1': format_decimal(amounts['amount1'], 6),
            },
        )
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise ExchangeError('移除流动性失败') from exc

    return {
        'pool': _serialize_pool(pool),
        'position': _serialize_position(position),
        'wallet': list_wallet(user_id),
    }


def list_positions(user_id):
    positions = LiquidityPosition.query.filter_by(user_id=user_id).all()
    return [_serialize_position(position) for position in positions if _decimal(position.lp_shares) > DECIMAL_ZERO]


def list_events(user_id, limit=80):
    events = (
        ExchangeEvent.query.filter(ExchangeEvent.user_id == user_id)
        .order_by(ExchangeEvent.id.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_event(event) for event in events]


def reset_simulation(user_id):
    seed_exchange_data(reset=True)
    _record_event(
        user_id=user_id,
        event_type='reset',
        pool_id=None,
        summary='重置本地交易所仿真',
        details={'pools': [pool['id'] for pool in DEMO_POOLS]},
    )
    db.session.commit()
    faucet_result = grant_faucet(user_id)
    return {
        'tokens': list_tokens(),
        'pools': list_pools(),
        'wallet': faucet_result['wallet'],
        'positions': list_positions(user_id),
    }


def _quote_for_pool(pool, token_in_symbol, amount_in):
    token_in_symbol = str(token_in_symbol).upper()
    amount = to_decimal(amount_in, 'amount_in')
    try:
        if token_in_symbol == pool.token0_symbol:
            return quote_exact_in(_decimal(pool.reserve0), _decimal(pool.reserve1), _decimal(pool.fee_rate), amount)
        if token_in_symbol == pool.token1_symbol:
            return quote_exact_in(_decimal(pool.reserve1), _decimal(pool.reserve0), _decimal(pool.fee_rate), amount)
    except AMMValidationError as exc:
        raise ExchangeError(str(exc)) from exc
    raise ExchangeError('输入资产不属于该交易池')


def _apply_swap_to_pool(pool, token_in_symbol, quote):
    if token_in_symbol == pool.token0_symbol:
        pool.reserve0 = _decimal(pool.reserve0) + quote['amount_in']
        pool.reserve1 = _decimal(pool.reserve1) - quote['amount_out']
        pool.cumulative_fee0 = _decimal(pool.cumulative_fee0) + quote['fee_amount']
    else:
        pool.reserve1 = _decimal(pool.reserve1) + quote['amount_in']
        pool.reserve0 = _decimal(pool.reserve0) - quote['amount_out']
        pool.cumulative_fee1 = _decimal(pool.cumulative_fee1) + quote['fee_amount']


def _resolve_remove_shares(payload, current_position_shares):
    if payload.get('lp_shares') not in (None, ''):
        shares = to_decimal(payload.get('lp_shares'), 'lp_shares')
    else:
        fraction = to_decimal(payload.get('share_fraction', '1'), 'share_fraction')
        if fraction <= DECIMAL_ZERO or fraction > DECIMAL_ONE:
            raise ExchangeError('share_fraction必须在(0,1]之间')
        shares = current_position_shares * fraction
    if shares <= DECIMAL_ZERO:
        raise ExchangeError('撤出的LP份额必须大于0')
    return shares


def _get_pool(pool_id):
    pool = db.session.get(LiquidityPool, pool_id)
    if pool is None:
        raise ExchangeError('交易池不存在', status=404)
    if not pool.is_active:
        raise ExchangeError('交易池已暂停')
    return pool


def _get_or_create_balance(user_id, token_symbol):
    balance = WalletBalance.query.filter_by(user_id=user_id, token_symbol=token_symbol).first()
    if balance is None:
        balance = WalletBalance(user_id=user_id, token_symbol=token_symbol, balance=DECIMAL_ZERO)
        db.session.add(balance)
        db.session.flush()
    return balance


def _get_or_create_position(user_id, pool_id):
    position = LiquidityPosition.query.filter_by(user_id=user_id, pool_id=pool_id).first()
    if position is None:
        position = LiquidityPosition(
            user_id=user_id,
            pool_id=pool_id,
            lp_shares=DECIMAL_ZERO,
            deposited0=DECIMAL_ZERO,
            deposited1=DECIMAL_ZERO,
        )
        db.session.add(position)
        db.session.flush()
    return position


def _ensure_wallet_rows(user_id):
    for token in ExchangeToken.query.all():
        _get_or_create_balance(user_id, token.symbol)
    db.session.commit()


def _record_event(user_id, event_type, pool_id, summary, details):
    db.session.add(
        ExchangeEvent(
            user_id=user_id,
            event_type=event_type,
            pool_id=pool_id,
            summary=summary,
            details=details,
        )
    )


def _resolve_amount_map(amounts):
    resolved = {}
    for symbol, amount in amounts.items():
        resolved[str(symbol).upper()] = to_decimal(amount, f'{symbol} amount')
    return resolved


def _require_positive(value, field_name):
    if value <= DECIMAL_ZERO:
        raise ExchangeError(f'{field_name}必须大于0')


def _token_out_symbol(pool, token_in_symbol):
    if token_in_symbol == pool.token0_symbol:
        return pool.token1_symbol
    if token_in_symbol == pool.token1_symbol:
        return pool.token0_symbol
    raise ExchangeError('输入资产不属于该交易池')


def _serialize_token(token):
    return {
        'symbol': token.symbol,
        'name': token.name,
        'decimals': token.decimals,
        'display_order': token.display_order,
    }


def _serialize_pool(pool, include_recent=False):
    reserve0 = _decimal(pool.reserve0)
    reserve1 = _decimal(pool.reserve1)
    total_lp_shares = _decimal(pool.total_lp_shares)
    spot_price = reserve1 / reserve0 if reserve0 > DECIMAL_ZERO else DECIMAL_ZERO
    tvl_usdc = reserve0 * spot_price + reserve1
    payload = {
        'id': pool.id,
        'name': pool.name,
        'token0': _serialize_token(pool.token0),
        'token1': _serialize_token(pool.token1),
        'reserve0': format_decimal(reserve0, 6),
        'reserve1': format_decimal(reserve1, 6),
        'fee_rate': format_decimal(_decimal(pool.fee_rate), 6),
        'total_lp_shares': format_decimal(total_lp_shares, 12),
        'cumulative_fee0': format_decimal(_decimal(pool.cumulative_fee0), 6),
        'cumulative_fee1': format_decimal(_decimal(pool.cumulative_fee1), 6),
        'spot_price_token1_per_token0': format_decimal(spot_price, 6),
        'tvl_usdc': format_decimal(tvl_usdc, 2),
        'is_active': pool.is_active,
    }
    if include_recent:
        payload['recent_events'] = [
            _serialize_event(event)
            for event in ExchangeEvent.query.filter_by(pool_id=pool.id).order_by(ExchangeEvent.id.desc()).limit(20).all()
        ]
    return payload


def _serialize_balance(balance):
    return {
        'symbol': balance.token_symbol,
        'name': balance.token.name if balance.token else balance.token_symbol,
        'balance': format_decimal(_decimal(balance.balance), 6),
    }


def _serialize_quote(pool, token_in_symbol, quote):
    token_out_symbol = _token_out_symbol(pool, token_in_symbol)
    post_reserve0 = _decimal(pool.reserve0)
    post_reserve1 = _decimal(pool.reserve1)
    if token_in_symbol == pool.token0_symbol:
        post_reserve0 = quote['post_reserve_in']
        post_reserve1 = quote['post_reserve_out']
    else:
        post_reserve1 = quote['post_reserve_in']
        post_reserve0 = quote['post_reserve_out']
    post_price = post_reserve1 / post_reserve0
    return {
        'pool_id': pool.id,
        'token_in_symbol': token_in_symbol,
        'token_out_symbol': token_out_symbol,
        'amount_in': format_decimal(quote['amount_in'], 6),
        'amount_out': format_decimal(quote['amount_out'], 6),
        'fee_amount': format_decimal(quote['fee_amount'], 6),
        'effective_amount_in': format_decimal(quote['effective_amount_in'], 6),
        'spot_price': format_decimal(quote['spot_price'], 8),
        'execution_price': format_decimal(quote['execution_price'], 8),
        'slippage': format_decimal(quote['slippage'], 8),
        'price_impact': format_decimal(quote['price_impact'], 8),
        'post_price_token1_per_token0': format_decimal(post_price, 8),
    }


def _serialize_position(position):
    pool = position.pool
    shares = _decimal(position.lp_shares)
    total_lp = _decimal(pool.total_lp_shares)
    pool_share = shares / total_lp if total_lp > DECIMAL_ZERO else DECIMAL_ZERO
    amount0 = _decimal(pool.reserve0) * pool_share
    amount1 = _decimal(pool.reserve1) * pool_share
    price = _decimal(pool.reserve1) / _decimal(pool.reserve0)
    current_value = amount0 * price + amount1
    hodl_value = _decimal(position.deposited0) * price + _decimal(position.deposited1)
    il_pct = impermanent_loss_pct(position.deposited0, position.deposited1, amount0, amount1, price)
    return {
        'id': position.id,
        'pool': _serialize_pool(pool),
        'lp_shares': format_decimal(shares, 12),
        'pool_share': format_decimal(pool_share, 8),
        'underlying0': format_decimal(amount0, 6),
        'underlying1': format_decimal(amount1, 6),
        'deposited0': format_decimal(_decimal(position.deposited0), 6),
        'deposited1': format_decimal(_decimal(position.deposited1), 6),
        'current_value_usdc': format_decimal(current_value, 2),
        'hodl_value_usdc': format_decimal(hodl_value, 2),
        'impermanent_loss_pct': format_decimal(il_pct, 8),
    }


def _serialize_event(event):
    if event is None:
        return None
    return {
        'id': event.id,
        'event_type': event.event_type,
        'pool_id': event.pool_id,
        'summary': event.summary,
        'details': event.details or {},
        'created_at': event.created_at.isoformat(),
    }


def _decimal(value):
    if value is None:
        return DECIMAL_ZERO
    return Decimal(str(value))
