import { ProForm, ProFormText } from '@ant-design/pro-components';
import { message } from 'antd';
import React from 'react';
import { useNavigate, Link } from '@umijs/max';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import styles from './index.less';

interface RegisterValues {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export default function RegisterPage() {
  const navigate = useNavigate();

  const handleSubmit = async (values: RegisterValues) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: values.username,
          email: values.email,
          password: values.password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        message.success('注册成功！请登录');
        navigate('/user/login');
        return true;
      }

      message.error(data.detail || '注册失败，请重试');
      return false;
    } catch (error) {
      console.error('注册错误:', error);
      message.error('注册失败，请检查网络连接');
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
          <div className={styles.desc}>智能助手，让工作更高效</div>
        </div>

        <div className={styles.main}>
          <ProForm
            initialValues={{}}
            submitter={{
              searchConfig: {
                submitText: '注册',
              },
              submitButtonProps: {
                block: true,
                size: 'large',
                style: { background: '#FF6B35', borderColor: '#FF6B35' },
              },
            }}
            onFinish={handleSubmit}
          >
            <ProFormText
              name="username"
              fieldProps={{
                size: 'large',
                prefix: <UserOutlined />,
              }}
              placeholder="请输入用户名"
              rules={[
                {
                  required: true,
                  message: '请输入用户名!',
                },
                {
                  min: 3,
                  message: '用户名至少3个字符',
                },
              ]}
            />

            <ProFormText
              name="email"
              fieldProps={{
                size: 'large',
                prefix: <MailOutlined />,
              }}
              placeholder="请输入邮箱"
              rules={[
                {
                  required: true,
                  message: '请输入邮箱!',
                },
                {
                  type: 'email',
                  message: '邮箱格式错误!',
                },
              ]}
            />

            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined />,
              }}
              placeholder="请输入密码（至少8位，包含大小写字母和数字）"
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
                },
                {
                  min: 8,
                  message: '密码至少8个字符',
                },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                  message: '密码必须包含大小写字母和数字',
                },
              ]}
            />

            <ProFormText.Password
              name="confirmPassword"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined />,
              }}
              placeholder="请确认密码"
              rules={[
                {
                  required: true,
                  message: '请确认密码！',
                },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致!'));
                  },
                }),
              ]}
            />

            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Link to="/user/login">已有账号？立即登录</Link>
            </div>
          </ProForm>
        </div>
      </div>
    </div>
  );
}
