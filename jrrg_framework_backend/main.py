#!/usr/bin/env python3
"""
DeFi AMM 交易所仿真系统 - 一键启动脚本

使用方式:
    python main.py                    # 使用默认配置启动
    python main.py --config demo.yaml # 使用指定配置文件启动
    python main.py --testing          # 使用测试配置启动（内存数据库）

参数说明:
    --config    指定 YAML 配置文件路径
    --testing   启用测试模式（使用内存数据库，数据不持久化）
    --host      自定义服务 host
    --port      自定义服务端口
"""

import argparse
import os
import sys
import yaml


def load_yaml_config(config_path):
    """加载 YAML 配置文件"""
    if not os.path.exists(config_path):
        print(f"[错误] 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def apply_yaml_config(app, config_data):
    """将 YAML 配置应用到 Flask 应用"""
    server = config_data.get('server', {})
    database = config_data.get('database', {})
    jwt = config_data.get('jwt', {})
    simulation = config_data.get('simulation', {})

    # 应用服务配置
    if 'debug' in server:
        app.config['DEBUG'] = server['debug']

    # 应用数据库配置
    db_type = database.get('type', 'sqlite')
    if db_type == 'memory':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif db_type == 'sqlite':
        db_path = database.get('path', 'exchange_simulator.db')
        # 如果路径是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, db_path)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    # 应用 JWT 配置
    if 'secret_key' in jwt:
        app.config['JWT_SECRET_KEY'] = jwt['secret_key']

    # 应用仿真数据配置
    if simulation.get('seed_data', True):
        # seed_data 已在 create_app 中处理，这里仅打印日志
        print("[配置] 自动初始化仿真数据: 已启用")

    return {
        'host': server.get('host', 'localhost'),
        'port': server.get('port', 8080),
    }


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='DeFi AMM 交易所仿真系统 - 一键启动',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    使用默认配置启动
  python main.py --config demo.yaml 使用 demo.yaml 配置启动
  python main.py --testing          使用测试模式启动（内存数据库）
  python main.py --port 5000        自定义端口启动
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='指定 YAML 配置文件路径（默认使用内置配置）'
    )
    parser.add_argument(
        '--testing',
        action='store_true',
        help='启用测试模式（使用内存数据库，数据不持久化）'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='自定义服务 host（覆盖配置文件）'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='自定义服务端口（覆盖配置文件）'
    )

    return parser.parse_args()


def main():
    """主入口函数"""
    args = parse_args()

    print("=" * 60)
    print("  DeFi AMM 交易所仿真系统")
    print("=" * 60)

    # 确定配置模式
    if args.testing:
        print("[模式] 测试模式（内存数据库）")
        from app import create_app
        app = create_app(config_name='testing')
        host = args.host or 'localhost'
        port = args.port or 8080
    else:
        from app import create_app
        app = create_app(config_name='BaseConfig')

        # 如果有配置文件，加载并应用
        if args.config:
            print(f"[配置] 加载配置文件: {args.config}")
            config_data = load_yaml_config(args.config)
            server_config = apply_yaml_config(app, config_data)
            host = args.host or server_config['host']
            port = args.port or server_config['port']
        else:
            print("[配置] 使用默认配置")
            host = args.host or 'localhost'
            port = args.port or 8080

    print(f"[启动] 服务地址: http://{host}:{port}")
    print("-" * 60)

    # 启动服务（禁用 debug，避免在特定环境下 multiprocessing 问题）
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
