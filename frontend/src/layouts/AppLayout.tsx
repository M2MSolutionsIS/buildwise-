import { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  Layout,
  Menu,
  Typography,
  theme,
  Breadcrumb,
  Dropdown,
  Avatar,
  Space,
  Badge,
  Button,
  Tooltip,
} from "antd";
import {
  DashboardOutlined,
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  ToolOutlined,
  BarChartOutlined,
  SettingOutlined,
  BellOutlined,
  SearchOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../services/authService";

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
  {
    key: "/crm",
    icon: <TeamOutlined />,
    label: "CRM",
    children: [
      { key: "/crm/contacts", label: "Contacte" },
    ],
  },
  {
    key: "/pipeline",
    icon: <FunnelPlotOutlined />,
    label: "Sales Pipeline",
    children: [
      { key: "/pipeline/offers", label: "Oferte" },
    ],
  },
  { key: "/pm", icon: <ProjectOutlined />, label: "Project Management" },
  { key: "/rm", icon: <ToolOutlined />, label: "Resource Management" },
  { key: "/bi", icon: <BarChartOutlined />, label: "Business Intelligence" },
  { key: "/settings", icon: <SettingOutlined />, label: "Setări" },
];

const BREADCRUMB_MAP: Record<string, string> = {
  "": "Dashboard",
  crm: "CRM",
  contacts: "Contacte",
  new: "Nou",
  pipeline: "Sales Pipeline",
  offers: "Oferte",
  pm: "Project Management",
  rm: "Resource Management",
  bi: "Business Intelligence",
  settings: "Setări",
};

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem("sidebar_collapsed") === "true";
  });
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();
  const { user, setUser, logout } = useAuthStore();

  // Fetch current user on mount
  useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await authService.getMe();
      setUser(res.data);
      return res.data;
    },
    enabled: !user,
    retry: false,
  });

  useEffect(() => {
    localStorage.setItem("sidebar_collapsed", String(collapsed));
  }, [collapsed]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  // Build breadcrumbs from path
  const pathSegments = location.pathname.split("/").filter(Boolean);
  const breadcrumbItems = [
    { title: <a onClick={() => navigate("/")}>Dashboard</a>, key: "home" },
    ...pathSegments.map((segment, idx) => {
      const path = "/" + pathSegments.slice(0, idx + 1).join("/");
      const isLast = idx === pathSegments.length - 1;
      // If segment looks like a UUID, show "Detaliu" instead
      const label =
        segment.length > 20
          ? "Detaliu"
          : BREADCRUMB_MAP[segment] || segment;
      return {
        title: isLast ? label : <a onClick={() => navigate(path)}>{label}</a>,
        key: path,
      };
    }),
  ];

  // Determine selected menu keys
  const selectedKeys = [location.pathname];
  const openKeys = pathSegments.length > 0 ? [`/${pathSegments[0]}`] : [];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        theme="light"
        width={220}
        collapsedWidth={64}
        style={{
          borderRight: `1px solid ${token.colorBorderSecondary}`,
          position: "fixed",
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          overflow: "auto",
        }}
      >
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
            padding: "0 16px",
          }}
        >
          <Typography.Title level={4} style={{ margin: 0, whiteSpace: "nowrap" }}>
            {collapsed ? "B" : "BuildWise"}
          </Typography.Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          defaultOpenKeys={openKeys}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />

        {/* User section at bottom */}
        {!collapsed && user && (
          <div
            style={{
              position: "absolute",
              bottom: 0,
              width: "100%",
              padding: "12px 16px",
              borderTop: `1px solid ${token.colorBorderSecondary}`,
            }}
          >
            <Space>
              <Avatar size="small" icon={<UserOutlined />} />
              <Typography.Text ellipsis style={{ maxWidth: 120 }}>
                {user.first_name} {user.last_name}
              </Typography.Text>
            </Space>
          </div>
        )}
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 64 : 220, transition: "margin-left 0.2s" }}>
        <Header
          style={{
            padding: "0 24px",
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            height: 48,
            lineHeight: "48px",
            position: "sticky",
            top: 0,
            zIndex: 99,
          }}
        >
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
            />
            <Breadcrumb items={breadcrumbItems} />
          </Space>

          <Space size="middle">
            <Tooltip title="Căutare (Ctrl+K)">
              <Button type="text" icon={<SearchOutlined />} />
            </Tooltip>

            <Tooltip title="Notificări">
              <Badge count={0} size="small">
                <Button type="text" icon={<BellOutlined />} />
              </Badge>
            </Tooltip>

            <Dropdown
              menu={{
                items: [
                  {
                    key: "user-info",
                    label: (
                      <div>
                        <Typography.Text strong>
                          {user?.first_name} {user?.last_name}
                        </Typography.Text>
                        <br />
                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                          {user?.email}
                        </Typography.Text>
                      </div>
                    ),
                    disabled: true,
                  },
                  { type: "divider" },
                  {
                    key: "settings",
                    icon: <SettingOutlined />,
                    label: "Setări",
                    onClick: () => navigate("/settings"),
                  },
                  { type: "divider" },
                  {
                    key: "logout",
                    icon: <LogoutOutlined />,
                    label: "Deconectare",
                    danger: true,
                    onClick: handleLogout,
                  },
                ],
              }}
              placement="bottomRight"
            >
              <Avatar
                size="small"
                icon={<UserOutlined />}
                style={{ cursor: "pointer", backgroundColor: token.colorPrimary }}
              />
            </Dropdown>
          </Space>
        </Header>

        <Content style={{ margin: 24, minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
