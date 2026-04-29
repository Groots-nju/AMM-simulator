from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import app.utils as utils
from app.exchange import (
    ExchangeError,
    add_liquidity,
    execute_swap,
    get_pool_detail,
    get_swap_quote,
    grant_faucet,
    list_events,
    list_pools,
    list_positions,
    list_tokens,
    list_wallet,
    remove_liquidity,
    reset_simulation,
)
from app.exchange.core import AMMValidationError


exchange_controller = Blueprint('exchange_controller', __name__)


@exchange_controller.before_request
def log_request_info():
    current_app.logger.info(f"收到请求: {request.method} {request.url}")


@exchange_controller.after_request
def log_response_info(response):
    current_app.logger.info(f"响应状态码: {response.status_code}")
    return response


@exchange_controller.get('/tokens')
@jwt_required()
def exchange_tokens():
    return _handle(lambda: list_tokens())


@exchange_controller.get('/pools')
@jwt_required()
def exchange_pools():
    return _handle(lambda: list_pools())


@exchange_controller.get('/pools/<pool_id>')
@jwt_required()
def exchange_pool_detail(pool_id):
    return _handle(lambda: get_pool_detail(pool_id))


@exchange_controller.get('/wallet')
@jwt_required()
def exchange_wallet():
    return _handle(lambda: list_wallet(_current_user_id()))


@exchange_controller.post('/faucet')
@jwt_required()
def exchange_faucet():
    payload = request.get_json(silent=True) or {}
    return _handle(lambda: grant_faucet(_current_user_id(), payload.get('amounts')))


@exchange_controller.post('/swap/quote')
@jwt_required()
def exchange_swap_quote():
    payload = request.get_json(force=True)
    return _handle(lambda: get_swap_quote(payload.get('pool_id'), payload.get('token_in_symbol'), payload.get('amount_in')))


@exchange_controller.post('/swap')
@jwt_required()
def exchange_swap():
    payload = request.get_json(force=True)
    return _handle(lambda: execute_swap(_current_user_id(), payload))


@exchange_controller.post('/liquidity/add')
@jwt_required()
def exchange_add_liquidity():
    payload = request.get_json(force=True)
    return _handle(lambda: add_liquidity(_current_user_id(), payload))


@exchange_controller.post('/liquidity/remove')
@jwt_required()
def exchange_remove_liquidity():
    payload = request.get_json(force=True)
    return _handle(lambda: remove_liquidity(_current_user_id(), payload))


@exchange_controller.get('/positions')
@jwt_required()
def exchange_positions():
    return _handle(lambda: list_positions(_current_user_id()))


@exchange_controller.get('/history')
@jwt_required()
def exchange_history():
    return _handle(lambda: list_events(_current_user_id()))


@exchange_controller.post('/simulation/reset')
@jwt_required()
def exchange_reset():
    return _handle(lambda: reset_simulation(_current_user_id()))


def _current_user_id():
    return int(get_jwt_identity())


def _handle(operation):
    try:
        data = operation()
        return utils.success(data=data, message='Success')
    except ExchangeError as exc:
        return utils.error(message=exc.message, code=exc.code, status=exc.status)
    except AMMValidationError as exc:
        return utils.error(message=str(exc), code=1002, status=400)
