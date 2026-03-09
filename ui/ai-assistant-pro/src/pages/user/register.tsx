import { ProForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';
import { message } from 'antd';
import React from 'react';
import { useNavigate, Link } from '@umijs/max';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import styles from './index.less';

export default function RegisterPage() {
  const navigate = useNavigate();

  const handleSubmit = async (values: any) => {
    try {
      // 模拟注册请求
      console.log('注册参数:', values);
      
      // 注册成功，跳转到登录页
      message.success('注册成功！请登录');
      navigate('/user/login');
      return true;
    } catch (error) {
      message.error('注册失败，请重试！');
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

            <ProFormText
              name="phone"
              fieldProps={{
                size: 'large',
                prefix: <PhoneOutlined />,
              }}
              placeholder="请输入手机号"
              rules={[
                {
                  required: true,
                  message: '请输入手机号!',
                },
                {
                  pattern: /^1\d{10}$/,
                  message: '手机号格式错误!',
                },
              ]}
            />

            <ProFormSelect
              name="role"
              label="用户类型"
              placeholder="请选择用户类型"
              rules={[{ required: true, message: '请选择用户类型' }]}
              options={[
                { label: '普通用户', value: 'user' },
                { label: '管理员', value: 'admin' },
              ]}
            />

            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined />,
              }}
              placeholder="请输入密码"
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
                },
                {
                  min: 6,
                  message: '密码至少6个字符',
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
              <Link to="/user/login">
                已有账号？立即登录
              </Link>
            </div>
          </ProForm>
        </div>
      </div>
    </div>
  );
}
