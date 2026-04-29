from datetime import datetime, timezone

from app.models import db


def utc_now():
    return datetime.now(timezone.utc)


class ExchangeToken(db.Model):
    __tablename__ = 'exchange_token'

    symbol = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    decimals = db.Column(db.Integer, nullable=False, default=18)
    display_order = db.Column(db.Integer, nullable=False, default=0)


class LiquidityPool(db.Model):
    __tablename__ = 'liquidity_pool'

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    token0_symbol = db.Column(db.String(16), db.ForeignKey('exchange_token.symbol'), nullable=False)
    token1_symbol = db.Column(db.String(16), db.ForeignKey('exchange_token.symbol'), nullable=False)
    reserve0 = db.Column(db.Numeric(36, 18), nullable=False)
    reserve1 = db.Column(db.Numeric(36, 18), nullable=False)
    fee_rate = db.Column(db.Numeric(18, 12), nullable=False, default=0)
    total_lp_shares = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    cumulative_fee0 = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    cumulative_fee1 = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    token0 = db.relationship('ExchangeToken', foreign_keys=[token0_symbol])
    token1 = db.relationship('ExchangeToken', foreign_keys=[token1_symbol])


class WalletBalance(db.Model):
    __tablename__ = 'wallet_balance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token_symbol = db.Column(db.String(16), db.ForeignKey('exchange_token.symbol'), nullable=False)
    balance = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    token = db.relationship('ExchangeToken')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'token_symbol', name='uq_wallet_user_token'),
    )


class LiquidityPosition(db.Model):
    __tablename__ = 'liquidity_position'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pool_id = db.Column(db.String(32), db.ForeignKey('liquidity_pool.id'), nullable=False)
    lp_shares = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    deposited0 = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    deposited1 = db.Column(db.Numeric(36, 18), nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    pool = db.relationship('LiquidityPool')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'pool_id', name='uq_position_user_pool'),
    )


class ExchangeEvent(db.Model):
    __tablename__ = 'exchange_event'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    event_type = db.Column(db.String(32), nullable=False)
    pool_id = db.Column(db.String(32), db.ForeignKey('liquidity_pool.id'), nullable=True)
    summary = db.Column(db.String(255), nullable=False)
    details = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    pool = db.relationship('LiquidityPool')
