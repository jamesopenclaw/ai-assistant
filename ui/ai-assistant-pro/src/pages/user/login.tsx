import { ProForm, ProFormText } from '@ant-design/pro-components';
import { message, Tabs } from 'antd';
import React, { useState } from 'react';
import { useNavigate, Link } from '@umijs/max';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import styles from './index.less';

interface LoginValues {
  username?: string;
  password?: string;
  phone?: string;
  code?: string;
}

export default function LoginPage() {
  const [loginType, setLoginType] = useState('account');
  const navigate = useNavigate();

  const handleSubmit = async (values: LoginValues) => {
    try {
      // 调用真实登录 API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: values.username,
          password: values.password,
        }),
      });

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        message.error('服务器响应格式错误，请稍后重试');
        return false;
      }

      if (response.ok && data.token) {
        // 保存 token 到 localStorage
        localStorage.setItem('token', data.token.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        message.success('登录成功！');
        navigate('/chat');
        return true;
      } else {
        message.error(data.detail || '登录失败，请检查用户名和密码');
        return false;
      }
    } catch (error) {
      console.error('登录错误:', error);
      message.error('登录失败，请检查网络连接');
      return false;
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.top}>
          <div className={styles.header}>
            <Link to="/">
              <img alt="logo" className={styles.logo} src="https://img.icons8.com/color/96/artificial-intelligence.png" />
              <span className={styles.title}>小优 AI 助手</span>
            </Link>
          </div>
          <div className={styles.desc}>
            智能助手，让工作更高效
          </div>
        </div>

        <div className={styles.main}>
          <ProForm
            initialValues={{
              autoLogin: true,
            }}
            submitter={{
              searchConfig: {
                submitText: '登录',
              },
              submitButtonProps: {
                block: true,
                size: 'large',
                style: { background: '#FF6B35', borderColor: '#FF6B35' },
              },
            }}
            onFinish={handleSubmit}
          >
            <Tabs
              activeKey={loginType}
              onChange={(key) => setLoginType(key)}
              items={[
                {
                  key: 'account',
                  label: '账号密码登录',
                },
                {
                  key: 'phone',
                  label: '手机号登录',
                },
              ]}
            />

            {loginType === 'account' && (
              <>
                <ProFormText
                  name="username"
                  fieldProps={{
                    size: 'large',
                    prefix: <UserOutlined />,
                  }}
                  placeholder="用户名: admin"
                  rules={[
                    {
                      required: true,
                      message: '请输入用户名!',
                    },
                  ]}
                />
                <ProFormText.Password
                  name="password"
                  fieldProps={{
                    size: 'large',
                    prefix: <LockOutlined />,
                  }}
                  placeholder="密码: ant.design"
                  rules={[
                    {
                      required: true,
                      message: '请输入密码！',
                    },
                  ]}
                />
              </>
            )}

            {loginType === 'phone' && (
              <>
                <ProFormText
                  name="phone"
                  fieldProps={{
                    size: 'large',
                    prefix: <PhoneOutlined />,
                  }}
                  placeholder="手机号"
                  rules={[
                    {
                      required: true,
                      message: '请输入手机号！',
                    },
                    {
                      pattern: /^1\d{10}$/,
                      message: '手机号格式错误！',
                    },
                  ]}
                />
                <ProFormText
                  name="code"
                  fieldProps={{
                    size: 'large',
                    prefix: <MailOutlined />,
                  }}
                  placeholder="验证码"
                  rules={[
                    {
                      required: true,
                      message: '请输入验证码！',
                    },
                  ]}
                />
              </>
            )}

            <div style={{ marginBottom: 24 }}>
              <ProFormText.NoField name="autoLogin" />
              <Link to="/user/register" style={{ float: 'right' }}>
                还没有账号？立即注册
              </Link>
            </div>
          </ProForm>
        </div>
      </div>

    </div>
  );
}
