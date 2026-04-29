import {
  AppstoreOutlined,
  HistoryOutlined,
  LogoutOutlined,
  SwapOutlined,
  UserOutlined,
  WalletOutlined,
  ApiOutlined,
  PieChartOutlined,
} from '@ant-design/icons';
import { Avatar, Breadcrumb, Dropdown, Layout, Menu, Tooltip } from 'antd';
import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import './Index.scss';
import Logo from '../../assets/img/manbo.png';
import { $userLogout } from '../../api/userApi';

const { Header, Content, Sider, Footer } = Layout;

const menuItems = [
  { key: '/exchange', icon: <AppstoreOutlined />, label: '交易所总览' },
  { key: '/exchange/swap', icon: <SwapOutlined />, label: 'Swap 交易' },
  { key: '/exchange/liquidity', icon: <ApiOutlined />, label: '流动性管理' },
  { key: '/exchange/wallet', icon: <WalletOutlined />, label: '模拟钱包' },
  { key: '/exchange/history', icon: <HistoryOutlined />, label: '交易历史' },
  { key: '/profile', icon: <UserOutlined />, label: '用户信息' },
];

const titleMap = menuItems.reduce((result, item) => ({ ...result, [item.key]: item.label }), {});

const Index = () => {
  const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
  const navigate = useNavigate();
  const location = useLocation();

  const selectedKey = menuItems.find((item) => item.key === location.pathname)?.key || '/exchange';
  const breadcrumbItems = [
    { title: 'AMM Exchange' },
    { title: titleMap[selectedKey] || '交易所总览' },
  ];

  const handleLogoutMenuItemClick = async () => {
    await $userLogout();
    navigate('/login', { replace: true });
  };

  const dropdownMenuItems = [
    {
      key: 'my_account',
      label: '我的账户',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: '注销',
      icon: <LogoutOutlined />,
      onClick: handleLogoutMenuItemClick,
    },
  ];

  return (
    <Layout className="exchange-layout">
      <Header className="exchange-header">
        <div className="brand-cluster" onClick={() => navigate('/exchange')}>
          <img className="brand-logo" src={Logo} alt="AMM Exchange" />
          <div>
            <div className="brand-title">AMM Exchange Simulator</div>
            <div className="brand-subtitle">Local DEX simulation</div>
          </div>
        </div>
        <div className="header-market-strip">
          <span>Localhost</span>
          <span>0.30% LP Fee</span>
          <span>No real assets</span>
        </div>
        <Dropdown menu={{ items: dropdownMenuItems }} placement="bottomRight">
          <div className="account-chip">
            <Avatar size={34} icon={<UserOutlined />} />
            <Tooltip placement="left" title={userInfo.nickname || userInfo.username || 'Trader'}>
              <span>{userInfo.nickname || userInfo.username || 'Trader'}</span>
            </Tooltip>
          </div>
        </Dropdown>
      </Header>
      <Layout className="exchange-main">
        <Sider width={236} className="exchange-sider">
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            className="exchange-menu"
            items={menuItems}
            onClick={(event) => navigate(event.key)}
          />
        </Sider>
        <Layout className="exchange-content-layout">
          <Breadcrumb className="exchange-breadcrumb" items={breadcrumbItems} />
          <Content className="exchange-content">
            <Outlet />
          </Content>
          <Footer className="exchange-footer">
            <PieChartOutlined /> AMM DEX 仿真系统 · 本地模拟资产不代表真实交易
          </Footer>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default Index;
