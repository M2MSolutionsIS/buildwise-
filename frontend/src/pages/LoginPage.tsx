import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Form, Input, Button, Typography, Space } from "antd";
import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { authService } from "../services/authService";
import { useAuthStore } from "../stores/authStore";
import { toast } from "../components/ToastNotifications";
import { useBrandingStore } from "../stores/brandingStore";
import { systemService } from "../modules/system/services/systemService";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const applyBranding = useBrandingStore((s) => s.applyBranding);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const tokens = await authService.login(values.email, values.password);
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);

      const meResponse = await authService.getMe();
      setUser(meResponse.data);

      // Sync branding from backend Organization (F137)
      try {
        const orgResponse = await systemService.getOrganization();
        const org = orgResponse.data;
        applyBranding({
          appName: org.custom_branding?.app_name as string || org.name || "BuildWise",
          logoUrl: org.logo_url || "",
          primaryColor: org.primary_color || "#1677ff",
          secondaryColor: org.secondary_color || "#52c41a",
          whiteLabelEnabled: !!org.custom_branding?.white_label_enabled,
          fontFamily: org.custom_branding?.font_family as string || "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
          borderRadius: (org.custom_branding?.border_radius as number) || 6,
        });
      } catch {
        // Non-blocking — branding falls back to localStorage/defaults
      }

      toast.success("Autentificare reușită!");
      navigate("/", { replace: true });
    } catch {
      toast.error("Email sau parolă incorectă.");
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
        background: "#0B0F19",
      }}
    >
      <Card style={{ width: 400, background: "#1A1A2E", border: "1px solid rgba(255,255,255,0.08)", boxShadow: "0 8px 32px rgba(0,0,0,0.4)" }}>
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ display: "flex", justifyContent: "center", marginBottom: 12 }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: "linear-gradient(135deg, #2563EB, #7C3AED)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 700, fontSize: 18 }}>B</div>
            </div>
            <Typography.Title level={2} style={{ margin: 0, color: "#F1F5F9" }}>
              BuildWise
            </Typography.Title>
            <Typography.Text style={{ color: "#94A3B8" }}>
              Platforma ERP pentru eficienta energetica
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
