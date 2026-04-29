from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
DISPLAY_QUANT = Decimal('0.000000000001')


class AMMValidationError(ValueError):
    pass


def to_decimal(value, field_name='value'):
    if value is None:
        raise AMMValidationError(f'{field_name}不能为空')
    try:
        resolved = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise AMMValidationError(f'{field_name}必须是数字') from exc
    if not resolved.is_finite():
        raise AMMValidationError(f'{field_name}必须是有限数字')
    return resolved


def require_positive(value, field_name='value'):
    if value <= DECIMAL_ZERO:
        raise AMMValidationError(f'{field_name}必须大于0')


def decimal_sqrt(value):
    require_positive(value, 'sqrt value')
    return value.sqrt()


def format_decimal(value, places=12):
    if value is None:
        return None
    quant = Decimal('1').scaleb(-places)
    rounded = Decimal(value).quantize(quant, rounding=ROUND_HALF_UP)
    text = format(rounded.normalize(), 'f')
    return '0' if text == '-0' else text


def quote_exact_in(reserve_in, reserve_out, fee_rate, amount_in):
    reserve_in = to_decimal(reserve_in, 'reserve_in')
    reserve_out = to_decimal(reserve_out, 'reserve_out')
    fee_rate = to_decimal(fee_rate, 'fee_rate')
    amount_in = to_decimal(amount_in, 'amount_in')

    require_positive(reserve_in, 'reserve_in')
    require_positive(reserve_out, 'reserve_out')
    require_positive(amount_in, 'amount_in')
    if fee_rate < DECIMAL_ZERO or fee_rate >= DECIMAL_ONE:
        raise AMMValidationError('手续费率必须在[0,1)之间')

    fee_amount = amount_in * fee_rate
    effective_amount_in = amount_in - fee_amount
    amount_out = reserve_out * effective_amount_in / (reserve_in + effective_amount_in)
    execution_price = amount_out / amount_in
    spot_price = reserve_out / reserve_in
    slippage = execution_price / spot_price - DECIMAL_ONE
    price_impact = DECIMAL_ONE - execution_price / spot_price
    post_reserve_in = reserve_in + amount_in
    post_reserve_out = reserve_out - amount_out

    if amount_out <= DECIMAL_ZERO or post_reserve_out <= DECIMAL_ZERO:
        raise AMMValidationError('交易会耗尽池子流动性')

    return {
        'amount_in': amount_in,
        'effective_amount_in': effective_amount_in,
        'fee_amount': fee_amount,
        'amount_out': amount_out,
        'spot_price': spot_price,
        'execution_price': execution_price,
        'slippage': slippage,
        'price_impact': price_impact,
        'post_reserve_in': post_reserve_in,
        'post_reserve_out': post_reserve_out,
    }


def mint_liquidity_shares(reserve0, reserve1, total_lp_shares, amount0, amount1):
    reserve0 = to_decimal(reserve0, 'reserve0')
    reserve1 = to_decimal(reserve1, 'reserve1')
    total_lp_shares = to_decimal(total_lp_shares, 'total_lp_shares')
    amount0 = to_decimal(amount0, 'amount0')
    amount1 = to_decimal(amount1, 'amount1')
    require_positive(amount0, 'amount0')
    require_positive(amount1, 'amount1')

    if total_lp_shares <= DECIMAL_ZERO:
        return decimal_sqrt(amount0 * amount1)

    require_positive(reserve0, 'reserve0')
    require_positive(reserve1, 'reserve1')
    expected_amount1 = amount0 * reserve1 / reserve0
    tolerance = max(expected_amount1 * Decimal('0.005'), Decimal('0.000000001'))
    if abs(expected_amount1 - amount1) > tolerance:
        raise AMMValidationError(f'添加流动性必须接近当前池子比例，建议 amount1={format_decimal(expected_amount1, 6)}')
    return amount0 * total_lp_shares / reserve0


def remove_liquidity_amounts(reserve0, reserve1, total_lp_shares, shares):
    reserve0 = to_decimal(reserve0, 'reserve0')
    reserve1 = to_decimal(reserve1, 'reserve1')
    total_lp_shares = to_decimal(total_lp_shares, 'total_lp_shares')
    shares = to_decimal(shares, 'lp_shares')
    require_positive(shares, 'lp_shares')
    require_positive(total_lp_shares, 'total_lp_shares')
    if shares > total_lp_shares:
        raise AMMValidationError('撤出的LP份额不能超过池子总份额')
    ratio = shares / total_lp_shares
    return {
        'ratio': ratio,
        'amount0': reserve0 * ratio,
        'amount1': reserve1 * ratio,
    }


def impermanent_loss_pct(deposited0, deposited1, current_amount0, current_amount1, current_price):
    deposited0 = to_decimal(deposited0, 'deposited0')
    deposited1 = to_decimal(deposited1, 'deposited1')
    current_amount0 = to_decimal(current_amount0, 'current_amount0')
    current_amount1 = to_decimal(current_amount1, 'current_amount1')
    current_price = to_decimal(current_price, 'current_price')
    hodl_value = deposited0 * current_price + deposited1
    lp_value = current_amount0 * current_price + current_amount1
    if hodl_value <= DECIMAL_ZERO:
        return DECIMAL_ZERO
    return lp_value / hodl_value - DECIMAL_ONE
