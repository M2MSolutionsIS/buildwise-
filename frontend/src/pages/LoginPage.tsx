import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Form, Input, Button, Typography, App, Space } from "antd";
import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { authService } from "../services/authService";
import { useAuthStore } from "../stores/authStore";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { message } = App.useApp();
  const setUser = useAuthStore((s) => s.setUser);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const tokens = await authService.login(values.email, values.password);
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);

      const meResponse = await authService.getMe();
      setUser(meResponse.data);

      message.success("Autentificare reușită!");
      navigate("/", { replace: true });
    } catch {
      message.error("Email sau parolă incorectă.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Card style={{ width: 400, boxShadow: "0 8px 32px rgba(0,0,0,0.15)" }}>
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div style={{ textAlign: "center" }}>
            <Typography.Title level={2} style={{ margin: 0 }}>
              BuildWise
            </Typography.Title>
            <Typography.Text type="secondary">
              Platforma ERP pentru eficiență energetică
            </Typography.Text>
          </div>

          <Form layout="vertical" onFinish={onFinish} autoComplete="off" size="large">
            <Form.Item
              name="email"
              rules={[
                { required: true, message: "Introduceți email-ul" },
                { type: "email", message: "Email invalid" },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="Email" />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: "Introduceți parola" }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Parolă" />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button type="primary" htmlType="submit" loading={loading} block>
                Autentificare
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>
    </div>
  );
}
