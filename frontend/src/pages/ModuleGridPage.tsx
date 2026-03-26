/**
 * F157: Grid navigare module cu carduri iconizate
 * Pagină Home cu secțiuni: Internal Activity, CRM, Sales Pipeline,
 * PM, Resource Management, BI, Setări.
 */
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Typography, Space, Badge, Tag, theme } from "antd";
import { usePrototypeStore } from "../stores/prototypeStore";
import { useBrandingStore } from "../stores/brandingStore";
import { useTranslation } from "../i18n";
import {
  TeamOutlined,
  ProjectOutlined,
  BarChartOutlined,
  SettingOutlined,
  ContactsOutlined,
  FileTextOutlined,
  ScheduleOutlined,
  AimOutlined,
  PieChartOutlined,
  FolderOpenOutlined,
  ThunderboltOutlined,
  SolutionOutlined,
  CarOutlined,
  InboxOutlined,
  LineChartOutlined,
  SafetyOutlined,
  AuditOutlined,
  UserOutlined,
} from "@ant-design/icons";

const { Title, Text } = Typography;

/* ─── Module Definitions ──────────────────────────────────────────────────── */

interface ModuleCard {
  key: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  link: string;
  badge?: number;
  /** Minimum prototype required: "P1" = all, "P2" = P2+P3, "P3" = P3 only */
  minPrototype?: "P1" | "P2" | "P3";
}

interface ModuleSection {
  title: string;
  /** Minimum prototype required for the entire section */
  minPrototype?: "P1" | "P2" | "P3";
  cards: ModuleCard[];
}

function buildSections(t: ReturnType<typeof useTranslation>): ModuleSection[] {
  return [
    {
      title: t.nav.crm,
      cards: [
        {
          key: "contacts",
          title: t.nav.contacts,
          description: t.crm.contactsList,
          icon: <ContactsOutlined style={{ fontSize: 28 }} />,
          color: "#1E40AF",
          link: "/crm/contacts",
        },
        {
          key: "crm-dashboard",
          title: "Dashboard CRM",
          description: t.nav.salesDashboard,
          icon: <TeamOutlined style={{ fontSize: 28 }} />,
          color: "#1E40AF",
          link: "/",
        },
      ],
    },
    {
      title: t.nav.pipeline,
      cards: [
        {
          key: "kanban",
          title: t.nav.pipelineKanban,
          description: t.pipeline.stage,
          icon: <AimOutlined style={{ fontSize: 28 }} />,
          color: "#7C3AED",
          link: "/pipeline/board",
        },
        {
          key: "offers",
          title: t.nav.offers,
          description: t.pipeline.offerBuilder,
          icon: <FileTextOutlined style={{ fontSize: 28 }} />,
          color: "#7C3AED",
          link: "/pipeline/offers",
        },
        {
          key: "activities",
          title: t.nav.activities,
          description: t.nav.activities,
          icon: <ScheduleOutlined style={{ fontSize: 28 }} />,
          color: "#7C3AED",
          link: "/pipeline/activities",
        },
        {
          key: "sales-dashboard",
          title: t.nav.salesDashboard,
          description: t.nav.salesDashboard,
          icon: <PieChartOutlined style={{ fontSize: 28 }} />,
          color: "#7C3AED",
          link: "/pipeline/dashboard",
        },
      ],
    },
    {
      title: t.nav.pm,
      cards: [
        {
          key: "projects",
          title: t.nav.projects,
          description: t.pm.projectsList,
          icon: <ProjectOutlined style={{ fontSize: 28 }} />,
          color: "#047857",
          link: "/pm",
        },
        {
          key: "archive",
          title: t.nav.archive,
          description: t.nav.archive,
          icon: <FolderOpenOutlined style={{ fontSize: 28 }} />,
          color: "#047857",
          link: "/pm/archive",
        },
        {
          key: "energy-portfolio",
          title: t.nav.energyPortfolio,
          description: t.pm.energyImpact,
          icon: <ThunderboltOutlined style={{ fontSize: 28 }} />,
          color: "#047857",
          link: "/pm/energy-portfolio",
        },
      ],
    },
    {
      title: t.nav.rm,
      minPrototype: "P2",
      cards: [
        {
          key: "employees",
          title: t.nav.employees,
          description: t.rm.employeesList,
          icon: <SolutionOutlined style={{ fontSize: 28 }} />,
          color: "#9F1239",
          link: "/rm",
        },
        {
          key: "equipment",
          title: t.nav.equipment,
          description: t.rm.equipmentList,
          icon: <CarOutlined style={{ fontSize: 28 }} />,
          color: "#9F1239",
          link: "/rm/equipment",
        },
        {
          key: "materials",
          title: t.nav.materials,
          description: t.rm.materialStock,
          icon: <InboxOutlined style={{ fontSize: 28 }} />,
          color: "#9F1239",
          link: "/rm/materials",
        },
      ],
    },
    {
      title: t.nav.bi,
      cards: [
        {
          key: "bi-dashboard",
          title: t.nav.executiveDashboard,
          description: t.bi.executiveSummary,
          icon: <LineChartOutlined style={{ fontSize: 28 }} />,
          color: "#B45309",
          link: "/bi",
        },
        {
          key: "bi-reports",
          title: t.nav.reports,
          description: t.bi.reportsBuilder,
          icon: <BarChartOutlined style={{ fontSize: 28 }} />,
          color: "#B45309",
          link: "/bi/reports",
        },
      ],
    },
    {
      title: t.nav.settings,
      cards: [
        {
          key: "settings",
          title: t.nav.settings,
          description: t.nav.settings,
          icon: <SettingOutlined style={{ fontSize: 28 }} />,
          color: "#6B7280",
          link: "/settings",
        },
        {
          key: "users",
          title: t.nav.users,
          description: t.nav.users,
          icon: <UserOutlined style={{ fontSize: 28 }} />,
          color: "#6B7280",
          link: "/settings/users",
        },
        {
          key: "roles",
          title: t.nav.roles,
          description: t.nav.roles,
          icon: <SafetyOutlined style={{ fontSize: 28 }} />,
          color: "#6B7280",
          link: "/settings/roles",
        },
        {
          key: "audit",
          title: t.nav.auditLog,
          description: t.nav.auditLog,
          icon: <AuditOutlined style={{ fontSize: 28 }} />,
          color: "#6B7280",
          link: "/settings/audit",
        },
      ],
    },
  ];
}

/* ─── Component ───────────────────────────────────────────────────────────── */

function isPrototypeVisible(minProto: "P1" | "P2" | "P3" | undefined, active: "P1" | "P2" | "P3"): boolean {
  if (!minProto || minProto === "P1") return true;
  if (minProto === "P2") return active === "P2" || active === "P3";
  if (minProto === "P3") return active === "P3";
  return true;
}

const PROTO_LABELS = {
  P1: "BuildWise TRL5 — Energy + AI",
  P2: "BAHM Operational — Construcții",
  P3: "M2M ERP Lite — SaaS",
};

const PROTO_COLORS = { P1: "#047857", P2: "#2563EB", P3: "#7C3AED" };

export default function ModuleGridPage() {
  const navigate = useNavigate();
  const { token } = theme.useToken();
  const { activePrototype } = usePrototypeStore();
  const { appName, whiteLabelEnabled } = useBrandingStore();
  const t = useTranslation();

  const sections = useMemo(() => buildSections(t), [t]);

  const filteredSections = useMemo(
    () =>
      sections
        .filter((s) => isPrototypeVisible(s.minPrototype, activePrototype))
        .map((s) => ({
          ...s,
          cards: s.cards.filter((c) => isPrototypeVisible(c.minPrototype, activePrototype)),
        }))
        .filter((s) => s.cards.length > 0),
    [activePrototype, sections]
  );

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Space align="baseline">
          <Title level={3} style={{ margin: 0 }}>
            {whiteLabelEnabled ? appName : "BuildWise"}
          </Title>
          <Tag color={PROTO_COLORS[activePrototype]}>{activePrototype}</Tag>
        </Space>
        <div>
          <Text type="secondary">
            {PROTO_LABELS[activePrototype]}
          </Text>
        </div>
      </div>

      {filteredSections.map((section) => (
        <div key={section.title} style={{ marginBottom: 32 }}>
          <Title
            level={5}
            style={{
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              color: "#94A3B8",
            }}
          >
            {section.title}
          </Title>
          <Row gutter={[16, 16]}>
            {section.cards.map((card) => (
              <Col xs={24} sm={12} md={8} lg={6} key={card.key}>
                <Badge.Ribbon
                  text={card.badge}
                  color="red"
                  style={{ display: card.badge ? "block" : "none" }}
                >
                  <Card
                    hoverable
                    onClick={() => navigate(card.link)}
                    style={{
                      height: "100%",
                      borderTop: `3px solid ${card.color}`,
                      transition: "transform 0.15s, box-shadow 0.15s",
                    }}
                    styles={{
                      body: {
                        padding: 20,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        textAlign: "center",
                        gap: 8,
                      },
                    }}
                  >
                    <div style={{ color: card.color }}>{card.icon}</div>
                    <Space direction="vertical" size={2}>
                      <Text strong style={{ fontSize: 14 }}>
                        {card.title}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {card.description}
                      </Text>
                    </Space>
                  </Card>
                </Badge.Ribbon>
              </Col>
            ))}
          </Row>
        </div>
      ))}
    </div>
  );
}
