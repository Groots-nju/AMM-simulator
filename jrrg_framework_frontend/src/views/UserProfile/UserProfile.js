import React, { useState, useEffect } from 'react';
import { Layout, Avatar, Descriptions, Card, Divider, Spin, message } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import './UserProfile.scss';
import { $getUserProfile } from '../../api/userApi'; // 引入之前写好的函数

const UserProfile = () => {
    const [userInfo, setUserInfo] = useState(null); // 用于存储用户信息
    const [loading, setLoading] = useState(true);  // 用于控制加载状态

    const { Header, Content, Footer } = Layout;

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const data = await $getUserProfile({ id: 'currentUserId' }); // 假设需要传递用户 ID
                if (data) {
                    setUserInfo(data.data); // 根据 API 返回的数据结构更新用户信息
                    message.success('用户信息加载成功');
                } else {
                    message.error('未能获取用户信息');
                }
            } catch (error) {
                message.error('获取用户信息失败:' + error.message);
            } finally {
                setLoading(false); // 加载结束
            }
        };

        fetchUserInfo();
    }, []);

    if (loading) {
        return (
            <div className="loading-container">
                <Spin tip="加载用户信息中..." size="large" />
            </div>
        );
    }

    if (!userInfo) {
        return <div>未能获取用户信息。</div>;
    }

    return (
        <Layout className="user-profile-layout">
            {/* 头部 */}
            <Header className="header">
                <Avatar
                    className="avatar"
                    size={64}
                    icon={<UserOutlined />}
                    src={userInfo.avatar || null}
                />
                <span className="nickname">{userInfo.nickname}</span>
            </Header>
            {/* 主体内容 */}
            <Content className="content">
                <Card className="user-info-card" bordered={false}>
                    <Descriptions
                        title="用户信息"
                        bordered
                        column={1}
                        layout="horizontal"
                    >
                        <Descriptions.Item label={<UserOutlined />}>
                            {userInfo.username || '未提供'}
                        </Descriptions.Item>
                        <Descriptions.Item label="昵称">
                            {userInfo.nickname || '未提供'}
                        </Descriptions.Item>
                        <Descriptions.Item label={<MailOutlined />}>
                            {userInfo.email || '未提供'}
                        </Descriptions.Item>
                        <Descriptions.Item label={<PhoneOutlined />}>
                            {userInfo.phone || '未提供'}
                        </Descriptions.Item>

                    </Descriptions>
                </Card>

                <Divider />

            </Content>
            {/* 页脚 */}
            <Footer className="footer">
                <div>
                    © 2025 用户信息展示页面 | 基于 Ant Design 设计
                </div>
            </Footer>
        </Layout>
    );
};

export default UserProfile;
