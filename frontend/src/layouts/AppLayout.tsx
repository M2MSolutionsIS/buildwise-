/**
 * E-027: App Shell — F157, F158
 * Sidebar complet cu toate modulele și sub-navigare contextual,
 * Breadcrumbs dinamic, Search global (Ctrl+K), Notificări,
 * Layout responsive cu drawer pe mobile.
 */
import { useState, useEffect, useCallback } from "react";
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
  Button,
  Tooltip,
  Drawer,
  Grid,
} from "antd";
import {
  AppstoreOutlined,
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  ToolOutlined,
  BarChartOutlined,
  SettingOutlined,
  SearchOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  MenuOutlined,
  ContactsOutlined,
  DashboardOutlined,
  FileTextOutlined,
  ScheduleOutlined,
  AimOutlined,
  SafetyOutlined,
  DollarOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
  FolderOpenOutlined,
  AuditOutlined,
  DatabaseOutlined,
  SolutionOutlined,
  CarOutlined,
  InboxOutlined,
  LineChartOutlined,
  PieChartOutlined,
  FlagOutlined,
  HomeOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../services/authService";
import NotificationsDropdown from "../modules/system/components/NotificationsDropdown";
import GlobalSearchModal from "../components/GlobalSearchModal";

const { Header, Sider, Content } = Layout;
const { useBreakpoint } = Grid;

/* ═══════════════════════════════════════════════════════════════════════════ */
/* F158: Complete sidebar menu with contextual sub-navigation per module      */
/* ═══════════════════════════════════════════════════════════════════════════ */

const menuItems = [
  {
    key: "/",
    icon: <AppstoreOutlined />,
    label: "Home",
  },
  {
    key: "/crm",
    icon: <TeamOutlined />,
    label: "CRM",
    children: [
      { key: "/crm/contacts", icon: <ContactsOutlined />, label: "Contacte" },
      { key: "/", icon: <DashboardOutlined />, label: "Dashboard CRM" },
    ],
  },
  {
    key: "/pipeline",
    icon: <FunnelPlotOutlined />,
    label: "Sales Pipeline",
    children: [
      { key: "/pipeline/board", icon: <AimOutlined />, label: "Pipeline Kanban" },
      { key: "/pipeline/opportunities/new", icon: <FlagOutlined />, label: "Oportunitate Nouă" },
      { key: "/pipeline/offers", icon: <FileTextOutlined />, label: "Oferte" },
      { key: "/pipeline/contracts", icon: <FileTextOutlined />, label: "Contracte" },
      { key: "/pipeline/activities", icon: <ScheduleOutlined />, label: "Activități" },
      { key: "/pipeline/dashboard", icon: <PieChartOutlined />, label: "Sales Dashboard" },
    ],
  },
  {
    key: "/pm",
    icon: <ProjectOutlined />,
    label: "Project Management",
    children: [
      { key: "/pm", icon: <ProjectOutlined />, label: "Proiecte" },
      { key: "/pm/archive", icon: <FolderOpenOutlined />, label: "Arhivă Proiecte" },
      { key: "/pm/energy-portfolio", icon: <ThunderboltOutlined />, label: "Energy Portfolio" },
    ],
  },
  {
    key: "/rm",
    icon: <ToolOutlined />,
    label: "Resource Management",
    children: [
      { key: "/rm", icon: <SolutionOutlined />, label: "Angajați" },
      { key: "/rm/equipment", icon: <CarOutlined />, label: "Echipamente" },
      { key: "/rm/materials", icon: <InboxOutlined />, label: "Materiale" },
    ],
  },
  {
    key: "/bi",
    icon: <BarChartOutlined />,
    label: "Business Intelligence",
    children: [
      { key: "/bi", icon: <LineChartOutlined />, label: "Dashboard Executiv" },
      { key: "/bi/reports", icon: <FileTextOutlined />, label: "Rapoarte" },
    ],
  },
  {
    key: "/settings",
    icon: <SettingOutlined />,
    label: "Setări",
    children: [
      { key: "/settings", icon: <SettingOutlined />, label: "Configurare" },
      { key: "/settings/users", icon: <UserOutlined />, label: "Utilizatori" },
      { key: "/settings/roles", icon: <SafetyOutlined />, label: "Roluri" },
      { key: "/settings/audit", icon: <AuditOutlined />, label: "Audit Log" },
      { key: "/settings/import", icon: <DatabaseOutlined />, label: "Import Date" },
    ],
  },
];

/* ═══════════════════════════════════════════════════════════════════════════ */
/* Breadcrumb map — maps URL segments to readable labels                     */
/* ═══════════════════════════════════════════════════════════════════════════ */

const BREADCRUMB_MAP: Record<string, string> = {
  "": "Home",
  crm: "CRM",
  contacts: "Contacte",
  new: "Nou",
  pipeline: "Sales Pipeline",
  board: "Pipeline Kanban",
  dashboard: "Sales Dashboard",
  opportunities: "Oportunități",
  activities: "Activități",
  offers: "Oferte",
  pm: "Project Management",
  projects: "Proiecte",
  gantt: "Gantt",
  timesheet: "Pontaj",
  consumption: "Consum Materiale",
  subcontractors: "Subcontractori",
  deliveries: "Recepții Materiale",
  "daily-reports": "Raport Zilnic",
  progress: "Monitorizare Progres",
  budget: "Control Buget",
  "work-situations": "Situații Lucrări",
  risks: "Registru Riscuri",
  reception: "Recepție",
  warranties: "Garanții",
  "energy-impact": "Impact Energetic",
  report: "Raport Proiect",
  archive: "Arhivă Proiecte",
  "energy-portfolio": "Energy Portfolio",
  rm: "Resource Management",
  equipment: "Echipamente",
  materials: "Materiale",
  bi: "Business Intelligence",
  reports: "Rapoarte",
  settings: "Setări",
  users: "Utilizatori",
  roles: "Roluri",
  audit: "Audit Log",
  import: "Import Date",
};

/* ═══════════════════════════════════════════════════════════════════════════ */
/* PM project context sub-navigation (F158 contextual per project)           */
/* ═══════════════════════════════════════════════════════════════════════════ */

function getProjectSubNav(projectId: string) {
  const base = `/pm/projects/${projectId}`;
  return [
    { key: `${base}/gantt`, icon: <ScheduleOutlined />, label: "Gantt" },
    { key: `${base}/timesheet`, icon: <AuditOutlined />, label: "Pontaj" },
    { key: `${base}/consumption`, icon: <ExperimentOutlined />, label: "Consum" },
    { key: `${base}/subcontractors`, icon: <SolutionOutlined />, label: "Subcontractori" },
    { key: `${base}/daily-reports`, icon: <FileTextOutlined />, label: "Raport Zilnic" },
    { key: `${base}/progress`, icon: <LineChartOutlined />, label: "Progres" },
    { key: `${base}/budget`, icon: <DollarOutlined />, label: "Buget" },
    { key: `${base}/work-situations`, icon: <DatabaseOutlined />, label: "Situații" },
    { key: `${base}/risks`, icon: <SafetyOutlined />, label: "Riscuri" },
    { key: `${base}/reception`, icon: <AimOutlined />, label: "Recepție" },
    { key: `${base}/warranties`, icon: <SafetyOutlined />, label: "Garanții" },
    { key: `${base}/energy-impact`, icon: <ThunderboltOutlined />, label: "Energie" },
    { key: `${base}/report`, icon: <PieChartOutlined />, label: "Raport 3-in-1" },
  ];
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* Main Layout Component                                                     */
/* ═══════════════════════════════════════════════════════════════════════════ */

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem("sidebar_collapsed") === "true";
  });
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();
  const { user, setUser, logout } = useAuthStore();
  const screens = useBreakpoint();
  const isMobile = !screens.md;

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

  // Persist sidebar collapsed state
  useEffect(() => {
    localStorage.setItem("sidebar_collapsed", String(collapsed));
  }, [collapsed]);

  // Ctrl+K / Cmd+K global search shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
      // Ctrl+B toggle sidebar
      if ((e.metaKey || e.ctrlKey) && e.key === "b") {
        e.preventDefault();
        setCollapsed((c) => !c);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Close mobile drawer on navigate
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const handleMenuClick = useCallback(
    ({ key }: { key: string }) => {
      navigate(key);
    },
    [navigate]
  );

  /* ─── Breadcrumbs ──────────────────────────────────────────────────────── */

  const pathSegments = location.pathname.split("/").filter(Boolean);
  const breadcrumbItems = [
    {
      title: (
        <a onClick={() => navigate("/")}>
          <HomeOutlined style={{ marginRight: 4 }} />
          Home
        </a>
      ),
      key: "home",
    },
    ...pathSegments.map((segment, idx) => {
      const path = "/" + pathSegments.slice(0, idx + 1).join("/");
      const isLast = idx === pathSegments.length - 1;
      const isUuid = segment.length > 20;
      const label = isUuid ? "Detaliu" : BREADCRUMB_MAP[segment] || segment;
      return {
        title: isLast ? (
          <span style={{ fontWeight: 500 }}>{label}</span>
        ) : (
          <a onClick={() => navigate(path)}>{label}</a>
        ),
        key: path,
      };
    }),
  ];

  /* ─── Menu Keys ────────────────────────────────────────────────────────── */

  const selectedKeys = [location.pathname];
  const openKeys = pathSegments.length > 0 ? [`/${pathSegments[0]}`] : [];

  /* ─── Detect project context for F158 contextual sub-nav ───────────────── */

  const projectMatch = location.pathname.match(/^\/pm\/projects\/([^/]+)/);
  const projectId = projectMatch?.[1];
  const projectSubNav = projectId ? getProjectSubNav(projectId) : null;

  /* ─── Sidebar Content (shared between desktop Sider and mobile Drawer) ── */

  const sidebarContent = (
    <>
      {/* Brand */}
      <div
        style={{
          height: 56,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed && !isMobile ? "center" : "flex-start",
          padding: collapsed && !isMobile ? "0" : "0 20px",
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          cursor: "pointer",
        }}
        onClick={() => navigate("/")}
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 6,
            background: `linear-gradient(135deg, ${token.colorPrimary}, #722ed1)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontWeight: 700,
            fontSize: 14,
            flexShrink: 0,
          }}
        >
          B
        </div>
        {(!collapsed || isMobile) && (
          <Typography.Title
            level={5}
            style={{ margin: "0 0 0 10px", whiteSpace: "nowrap" }}
          >
            BuildWise
          </Typography.Title>
        )}
      </div>

      {/* F158: Project context sub-navigation */}
      {projectSubNav && (
        <>
          <div
            style={{
              padding: "8px 16px 4px",
              fontSize: 11,
              fontWeight: 600,
              color: "#888",
              textTransform: "uppercase",
              letterSpacing: 0.5,
            }}
          >
            {(!collapsed || isMobile) && "Context Proiect"}
          </div>
          <Menu
            mode="inline"
            selectedKeys={selectedKeys}
            items={projectSubNav}
            onClick={handleMenuClick}
            style={{ borderRight: 0, marginBottom: 8 }}
          />
          <div
            style={{
              height: 1,
              background: token.colorBorderSecondary,
              margin: "0 16px 8px",
            }}
          />
        </>
      )}

      {/* Main navigation */}
      <Menu
        mode="inline"
        selectedKeys={selectedKeys}
        defaultOpenKeys={openKeys}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ borderRight: 0, flex: 1 }}
      />

      {/* User section at bottom */}
      <div
        style={{
          padding: "12px 16px",
          borderTop: `1px solid ${token.colorBorderSecondary}`,
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <Avatar
          size="small"
          icon={<UserOutlined />}
          style={{ backgroundColor: token.colorPrimary, flexShrink: 0 }}
        />
        {(!collapsed || isMobile) && user && (
          <div style={{ overflow: "hidden" }}>
            <Typography.Text ellipsis style={{ fontSize: 13, display: "block" }}>
              {user.first_name} {user.last_name}
            </Typography.Text>
            <Typography.Text
              type="secondary"
              ellipsis
              style={{ fontSize: 11, display: "block" }}
            >
              {user.email}
            </Typography.Text>
          </div>
        )}
      </div>
    </>
  );

  /* ─── Render ───────────────────────────────────────────────────────────── */

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Desktop Sidebar */}
      {!isMobile && (
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
            display: "flex",
            flexDirection: "column",
          }}
        >
          {sidebarContent}
        </Sider>
      )}

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          placement="left"
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          width={260}
          styles={{ body: { padding: 0, display: "flex", flexDirection: "column" } }}
          closable={false}
        >
          {sidebarContent}
        </Drawer>
      )}

      <Layout
        style={{
          marginLeft: isMobile ? 0 : collapsed ? 64 : 220,
          transition: "margin-left 0.2s",
        }}
      >
        {/* Header */}
        <Header
          style={{
            padding: "0 16px",
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
            {isMobile ? (
              <Button
                type="text"
                icon={<MenuOutlined />}
                onClick={() => setMobileDrawerOpen(true)}
              />
            ) : (
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
              />
            )}
            {!isMobile && <Breadcrumb items={breadcrumbItems} />}
          </Space>

          <Space size="middle">
            {/* E-026: Global Search Trigger */}
            <Tooltip title="Căutare globală (Ctrl+K)">
              <Button
                type="text"
                icon={<SearchOutlined />}
                onClick={() => setSearchOpen(true)}
              />
            </Tooltip>

            {/* E-025: Notifications */}
            <NotificationsDropdown />

            {/* User Menu */}
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
                  { type: "divider" as const },
                  {
                    key: "settings",
                    icon: <SettingOutlined />,
                    label: "Setări",
                    onClick: () => navigate("/settings"),
                  },
                  { type: "divider" as const },
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

        {/* Mobile breadcrumbs below header */}
        {isMobile && pathSegments.length > 0 && (
          <div
            style={{
              padding: "6px 16px",
              background: token.colorBgContainer,
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
            }}
          >
            <Breadcrumb items={breadcrumbItems} />
          </div>
        )}

        <Content style={{ margin: isMobile ? 12 : 24, minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>

      {/* E-026: Global Search Modal */}
      <GlobalSearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </Layout>
  );
}
