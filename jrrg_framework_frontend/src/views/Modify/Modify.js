import React, { useState } from "react";
import { Input, Button, message } from "antd";
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  SmileOutlined
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { $userModify } from "../../api/userApi";
import "./Modify.scss";

const Modify = () => {
  const navigate = useNavigate();
  const storedUser = JSON.parse(localStorage.getItem("user_info")) || {};

  const [formData, setFormData] = useState({
    username: storedUser.username || "",
    nickname: storedUser.nickname || "",
    email: storedUser.email || "",
    phone: storedUser.phone || "",
    password: ""
  });

  const [editingField, setEditingField] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFieldModify = async (field) => {
    const token = localStorage.getItem("jwt_token");
    if (!token) {
      message.error("用户未登录");
      navigate("/login");
      return;
    }

    const value = formData[field];

    if (!value || value.length > 255) {
      message.error(`${field} 格式不合法`);
      return;
    }

    try {
      await $userModify({ [field]: value }, token);
      message.success("修改成功，请重新登录");
      localStorage.removeItem("jwt_token");
      localStorage.removeItem("user_info");
      navigate("/login");
    } catch (err) {
      message.error("修改失败：" + (err.response?.data?.message || "请检查输入"));
    }
  };

  const fieldConfig = [
    {
      key: "username",
      label: "用户名",
      icon: <UserOutlined />,
      editable: false
    },
    {
      key: "password",
      label: "密码",
      icon: <LockOutlined />,
      editable: true
    },
    {
      key: "nickname",
      label: "昵称",
      icon: <SmileOutlined />,
      editable: true
    },
    {
      key: "email",
      label: "邮箱",
      icon: <MailOutlined />,
      editable: true
    },
    {
      key: "phone",
      label: "手机号",
      icon: <PhoneOutlined />,
      editable: true
    }
  ];

  return (
    <div className="modify-container">
      <div className="modify-box">
        <h2>修改个人信息</h2>
        {fieldConfig.map(({ key, label, icon, editable }) => (
          <div key={key} className="field-row" style={{ marginBottom: "16px" }}>
            <label style={{ width: "80px", fontWeight: "bold" }}>{label}：</label>
            {editingField === key ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  flex: 1
                }}
              >
                <Input
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  prefix={icon}
                  style={{ flex: 1 }}
                />
                <Button
                  type="primary"
                  onClick={() => {
                    handleFieldModify(key);
                    setEditingField(null);
                  }}
                >
                  确认
                </Button>
                <Button onClick={() => setEditingField(null)}>取消</Button>
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", flex: 1 }}>
                <span className="field-value">{formData[key] || "未设置"}</span>
                {editable ? (
                  <Button type="link" onClick={() => setEditingField(key)}>
                    修改
                  </Button>
                ) : (
                  <span style={{ color: "#aaa" }}>🔒不可修改</span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Modify;

