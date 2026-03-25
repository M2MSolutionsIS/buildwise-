/**
 * E-027: App Shell — F157, F158
 * Sidebar complet cu toate modulele și sub-navigare contextual,
 * Breadcrumbs dinamic, Search global (Ctrl+K), Notificări,
 * Layout responsive cu drawer pe mobile.
 */
import { useState, useEffect, useCallback, useMemo } from "react";
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
  FormatPainterOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";
import { useBrandingStore } from "../stores/brandingStore";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../services/authService";
import { systemService } from "../modules/system/services/systemService";
import { usePrototypeStore } from "../stores/prototypeStore";
import { useTranslation } from "../i18n";
import NotificationsDropdown from "../modules/system/components/NotificationsDropdown";
import GlobalSearchModal from "../components/GlobalSearchModal";
import PrototypeSwitcher from "../components/PrototypeSwitcher";

const { Header, Sider, Content } = Layout;
const { useBreakpoint } = Grid;

/* ═══════════════════════════════════════════════════════════════════════════ */
/* F158: Complete sidebar menu with contextual sub-navigation per module      */
/* ═══════════════════════════════════════════════════════════════════════════ */

function buildMenuItems(t: ReturnType<typeof useTranslation>) {
  return [
    {
      key: "/",
      icon: <AppstoreOutlined />,
      label: t.nav.home,
    },
    {
      key: "/crm",
      icon: <TeamOutlined />,
      label: t.nav.crm,
      children: [
        { key: "/crm/contacts", icon: <ContactsOutlined />, label: t.nav.contacts },
        { key: "/", icon: <DashboardOutlined />, label: "Dashboard CRM" },
      ],
    },
    {
      key: "/pipeline",
      icon: <FunnelPlotOutlined />,
      label: t.nav.pipeline,
      children: [
        { key: "/pipeline/board", icon: <AimOutlined />, label: t.nav.pipelineKanban },
        { key: "/pipeline/opportunities/new", icon: <FlagOutlined />, label: t.pipeline.newOpportunity },
        { key: "/pipeline/offers", icon: <FileTextOutlined />, label: t.nav.offers },
        { key: "/pipeline/contracts", icon: <FileTextOutlined />, label: t.nav.contracts },
        { key: "/pipeline/activities", icon: <ScheduleOutlined />, label: t.nav.activities },
        { key: "/pipeline/dashboard", icon: <PieChartOutlined />, label: t.nav.salesDashboard },
      ],
    },
    {
      key: "/pm",
      icon: <ProjectOutlined />,
      label: t.nav.pm,
      children: [
        { key: "/pm", icon: <ProjectOutlined />, label: t.nav.projects },
        { key: "/pm/archive", icon: <FolderOpenOutlined />, label: t.nav.archive },
        { key: "/pm/energy-portfolio", icon: <ThunderboltOutlined />, label: t.nav.energyPortfolio },
      ],
    },
    {
      key: "/rm",
      icon: <ToolOutlined />,
      label: t.nav.rm,
      children: [
        { key: "/rm", icon: <DashboardOutlined />, label: t.rm.dashboard },
        { key: "/rm/employees", icon: <SolutionOutlined />, label: t.nav.employees },
        { key: "/rm/equipment", icon: <CarOutlined />, label: t.nav.equipment },
        { key: "/rm/materials", icon: <InboxOutlined />, label: t.nav.materials },
        { key: "/rm/capacity", icon: <BarChartOutlined />, label: t.nav.capacity },
        { key: "/rm/financial", icon: <DollarOutlined />, label: t.nav.financialPlanning },
      ],
    },
    {
      key: "/bi",
      icon: <BarChartOutlined />,
      label: t.nav.bi,
      children: [
        { key: "/bi", icon: <LineChartOutlined />, label: t.nav.executiveDashboard },
        { key: "/bi/kpi-dashboard", icon: <DashboardOutlined />, label: t.nav.kpiDashboard },
        { key: "/bi/kpi-builder", icon: <SettingOutlined />, label: t.nav.kpiBuilder },
        { key: "/bi/reports", icon: <FileTextOutlined />, label: t.nav.reports },
        { key: "/bi/assistant", icon: <RobotOutlined />, label: "AI Assistant" },
        { key: "/bi/forecast", icon: <ExperimentOutlined />, label: "ML Forecast" },
      ],
    },
    {
      key: "/settings",
      icon: <SettingOutlined />,
      label: t.nav.settings,
      children: [
        { key: "/settings", icon: <SettingOutlined />, label: t.nav.settings },
        { key: "/settings/branding", icon: <FormatPainterOutlined />, label: t.nav.branding },
        { key: "/settings/users", icon: <UserOutlined />, label: t.nav.users },
        { key: "/settings/roles", icon: <SafetyOutlined />, label: t.nav.roles },
        { key: "/settings/audit", icon: <AuditOutlined />, label: t.nav.auditLog },
        { key: "/settings/import", icon: <DatabaseOutlined />, label: t.common.import },
      ],
    },
  ];
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* Breadcrumb map — maps URL segments to readable labels                     */
/* ═══════════════════════════════════════════════════════════════════════════ */

function buildBreadcrumbMap(t: ReturnType<typeof useTranslation>): Record<string, string> {
  return {
    "": t.nav.home,
    crm: t.nav.crm,
    contacts: t.nav.contacts,
    new: t.common.create,
    pipeline: t.nav.pipeline,
    board: t.nav.pipelineKanban,
    dashboard: t.nav.salesDashboard,
    opportunities: t.nav.opportunities,
    activities: t.nav.activities,
    offers: t.nav.offers,
    pm: t.nav.pm,
    projects: t.nav.projects,
    gantt: t.pm.ganttChart,
    timesheet: t.pm.timesheet,
    consumption: t.pm.materialConsumption,
    subcontractors: t.pm.subcontractors,
    deliveries: t.pm.materialConsumption,
    "daily-reports": t.pm.dailyReport,
    progress: t.pm.progressMonitoring,
    budget: t.pm.budgetControl,
    "work-situations": t.pm.workSituations,
    risks: t.pm.riskRegister,
    reception: t.pm.reception,
    warranties: t.pm.warranties,
    "energy-impact": t.pm.energyImpact,
    report: t.nav.reports,
    archive: t.nav.archive,
    "energy-portfolio": t.nav.energyPortfolio,
    rm: t.nav.rm,
    employees: t.nav.employees,
    equipment: t.nav.equipment,
    materials: t.nav.materials,
    capacity: t.nav.capacity,
    financial: t.nav.financialPlanning,
    bi: t.nav.bi,
    executive: t.nav.executiveDashboard,
    "kpi-dashboard": t.nav.kpiDashboard,
    "kpi-builder": t.nav.kpiBuilder,
    reports: t.nav.reports,
    assistant: "AI Assistant",
    forecast: "ML Forecast",
    settings: t.nav.settings,
    branding: t.nav.branding,
    users: t.nav.users,
    roles: t.nav.roles,
    audit: t.nav.auditLog,
    import: t.common.import,
  };
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* PM project context sub-navigation (F158 contextual per project)           */
/* ═══════════════════════════════════════════════════════════════════════════ */

function getProjectSubNav(projectId: string, t: ReturnType<typeof useTranslation>) {
  const base = `/pm/projects/${projectId}`;
  return [
    { key: `${base}/gantt`, icon: <ScheduleOutlined />, label: t.pm.ganttChart },
    { key: `${base}/timesheet`, icon: <AuditOutlined />, label: t.pm.timesheet },
    { key: `${base}/consumption`, icon: <ExperimentOutlined />, label: t.pm.materialConsumption },
    { key: `${base}/subcontractors`, icon: <SolutionOutlined />, label: t.pm.subcontractors },
    { key: `${base}/daily-reports`, icon: <FileTextOutlined />, label: t.pm.dailyReport },
    { key: `${base}/progress`, icon: <LineChartOutlined />, label: t.pm.progressMonitoring },
    { key: `${base}/budget`, icon: <DollarOutlined />, label: t.pm.budgetControl },
    { key: `${base}/work-situations`, icon: <DatabaseOutlined />, label: t.pm.workSituations },
    { key: `${base}/risks`, icon: <SafetyOutlined />, label: t.pm.riskRegister },
    { key: `${base}/reception`, icon: <AimOutlined />, label: t.pm.reception },
    { key: `${base}/warranties`, icon: <SafetyOutlined />, label: t.pm.warranties },
    { key: `${base}/energy-impact`, icon: <ThunderboltOutlined />, label: t.pm.energyImpact },
    { key: `${base}/report`, icon: <PieChartOutlined />, label: t.nav.reports },
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
  const { appName, logoUrl, primaryColor: brandPrimary, whiteLabelEnabled, applyBranding } = useBrandingStore();
  const { isRouteVisible } = usePrototypeStore();
  const t = useTranslation();
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

  // Sync branding from backend Organization (F137)
  useQuery({
    queryKey: ["organization-branding"],
    queryFn: async () => {
      const res = await systemService.getOrganization();
      const org = res.data;
      applyBranding({
        appName: (org.custom_branding?.app_name as string) || org.name || "BuildWise",
        logoUrl: org.logo_url || "",
        primaryColor: org.primary_color || "#1677ff",
        secondaryColor: org.secondary_color || "#52c41a",
        whiteLabelEnabled: !!org.custom_branding?.white_label_enabled,
        fontFamily: (org.custom_branding?.font_family as string) || "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        borderRadius: (org.custom_branding?.border_radius as number) || 6,
      });
      return org;
    },
    staleTime: 5 * 60 * 1000, // 5 min — don't re-fetch too often
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

  const breadcrumbMap = useMemo(() => buildBreadcrumbMap(t), [t]);

  const pathSegments = location.pathname.split("/").filter(Boolean);
  const breadcrumbItems = [
    {
      title: (
        <a onClick={() => navigate("/")}>
          <HomeOutlined style={{ marginRight: 4 }} />
          {t.nav.home}
        </a>
      ),
      key: "home",
    },
    ...pathSegments.map((segment, idx) => {
      const path = "/" + pathSegments.slice(0, idx + 1).join("/");
      const isLast = idx === pathSegments.length - 1;
      const isUuid = segment.length > 20;
      const label = isUuid ? t.common.detail : breadcrumbMap[segment] || segment;
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

  /* ─── Filter menu by active prototype ──────────────────────────────────── */

  const filteredMenuItems = useMemo(() => {
    return buildMenuItems(t)
      .filter((item) => isRouteVisible(item.key))
      .map((item) => {
        if (item.children) {
          return {
            ...item,
            children: item.children.filter((child) => isRouteVisible(child.key)),
          };
        }
        return item;
      })
      .filter((item) => !item.children || item.children.length > 0);
  }, [isRouteVisible, t]);

  /* ─── Detect project context for F158 contextual sub-nav ───────────────── */

  const projectMatch = location.pathname.match(/^\/pm\/projects\/([^/]+)/);
  const projectId = projectMatch?.[1];
  const projectSubNav = projectId ? getProjectSubNav(projectId, t) : null;

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
        {logoUrl ? (
          <img
            src={logoUrl}
            alt={appName}
            style={{ width: 28, height: 28, objectFit: "contain", borderRadius: 4, flexShrink: 0 }}
          />
        ) : (
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              background: `linear-gradient(135deg, ${brandPrimary || token.colorPrimary}, #722ed1)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 700,
              fontSize: 14,
              flexShrink: 0,
            }}
          >
            {whiteLabelEnabled ? appName.charAt(0).toUpperCase() : "B"}
          </div>
        )}
        {(!collapsed || isMobile) && (
          <Typography.Title
            level={5}
            style={{ margin: "0 0 0 10px", whiteSpace: "nowrap" }}
          >
            {whiteLabelEnabled ? appName : "BuildWise"}
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
            {(!collapsed || isMobile) && t.nav.projects}
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
        items={filteredMenuItems}
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
            {/* Prototype Switcher — P1/P2/P3 */}
            {!isMobile && <PrototypeSwitcher />}

            {/* E-026: Global Search Trigger */}
            <Tooltip title={`${t.common.search} (Ctrl+K)`}>
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
                    label: t.nav.settings,
                    onClick: () => navigate("/settings"),
                  },
                  { type: "divider" as const },
                  {
                    key: "logout",
                    icon: <LogoutOutlined />,
                    label: t.common.logout,
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
