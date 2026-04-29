import React from "react";
import { Link } from "react-router-dom";
import './NotFound.scss';

const NotFound = () => {
    const teamMembers = ["朱晗", "陈俊凯", "杨惠文", "欧阳慧婷"];

    return (
        <div className="not-found-page">
            <div className="card">
                <div className="error-code">
                    4
                    <span className="zero">
                        <div className="zero-shadow"></div>
                    </span>
                    4
                </div>
                <h1 className="title">页面未找到</h1>
                <p className="text">抱歉，您访问的页面不存在或已被移除</p>

                <div className="info-container">
                    <div className="box">
                        <span className="label">项目名称</span>
                        <span className="value">SIAP of Manbo</span>
                    </div>
                    <div className="box">
                        <span className="label">开发团队</span>
                        <div className="members">
                            {teamMembers.map((member, index) => (
                                <span key={index} className="member">{member}</span>
                            ))}
                        </div>
                    </div>
                </div>

                <Link to="/" className="home-link">
                    返回首页 <span className="arrow">&rarr;</span>
                </Link>
            </div>
        </div>
    );
};

export default NotFound;
