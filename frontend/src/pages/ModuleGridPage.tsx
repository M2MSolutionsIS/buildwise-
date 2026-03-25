/**
 * F157: Grid navigare module cu carduri iconizate
 * Pagină Home cu secțiuni: Internal Activity, CRM, Sales Pipeline,
 * PM, Resource Management, BI, Setări.
 */
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Typography, Space, Badge, theme } from "antd";
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
}

interface ModuleSection {
  title: string;
  cards: ModuleCard[];
}

const sections: ModuleSection[] = [
  {
    title: "CRM",
    cards: [
      {
        key: "contacts",
        title: "Contacte",
        description: "Gestionare clienți și persoane de contact",
        icon: <ContactsOutlined style={{ fontSize: 28 }} />,
        color: "#1677ff",
        link: "/crm/contacts",
      },
      {
        key: "crm-dashboard",
        title: "Dashboard CRM",
        description: "KPI-uri vânzări și overview pipeline",
        icon: <TeamOutlined style={{ fontSize: 28 }} />,
        color: "#1677ff",
        link: "/",
      },
    ],
  },
  {
    title: "Sales Pipeline",
    cards: [
      {
        key: "kanban",
        title: "Pipeline Kanban",
        description: "Board vizual cu oportunități pe etape",
        icon: <AimOutlined style={{ fontSize: 28 }} />,
        color: "#722ed1",
        link: "/pipeline/board",
      },
      {
        key: "offers",
        title: "Oferte",
        description: "Lista ofertelor și offer builder",
        icon: <FileTextOutlined style={{ fontSize: 28 }} />,
        color: "#722ed1",
        link: "/pipeline/offers",
      },
      {
        key: "activities",
        title: "Activități",
        description: "Planner activități comerciale",
        icon: <ScheduleOutlined style={{ fontSize: 28 }} />,
        color: "#722ed1",
        link: "/pipeline/activities",
      },
      {
        key: "sales-dashboard",
        title: "Sales Dashboard",
        description: "Analitics pipeline și performanță agenți",
        icon: <PieChartOutlined style={{ fontSize: 28 }} />,
        color: "#722ed1",
        link: "/pipeline/dashboard",
      },
    ],
  },
  {
    title: "Project Management",
    cards: [
      {
        key: "projects",
        title: "Proiecte",
        description: "Lista proiectelor active și management",
        icon: <ProjectOutlined style={{ fontSize: 28 }} />,
        color: "#52c41a",
        link: "/pm",
      },
      {
        key: "archive",
        title: "Arhivă Proiecte",
        description: "Baza de date proiecte finalizate",
        icon: <FolderOpenOutlined style={{ fontSize: 28 }} />,
        color: "#52c41a",
        link: "/pm/archive",
      },
      {
        key: "energy-portfolio",
        title: "Energy Portfolio",
        description: "Impact energetic agregat cross-proiecte",
        icon: <ThunderboltOutlined style={{ fontSize: 28 }} />,
        color: "#52c41a",
        link: "/pm/energy-portfolio",
      },
    ],
  },
  {
    title: "Resource Management",
    cards: [
      {
        key: "employees",
        title: "Angajați",
        description: "Resurse umane și alocare personal",
        icon: <SolutionOutlined style={{ fontSize: 28 }} />,
        color: "#fa8c16",
        link: "/rm",
      },
      {
        key: "equipment",
        title: "Echipamente",
        description: "Flotă echipamente și disponibilitate",
        icon: <CarOutlined style={{ fontSize: 28 }} />,
        color: "#fa8c16",
        link: "/rm/equipment",
      },
      {
        key: "materials",
        title: "Materiale",
        description: "Stocuri și gestionare materiale",
        icon: <InboxOutlined style={{ fontSize: 28 }} />,
        color: "#fa8c16",
        link: "/rm/materials",
      },
    ],
  },
  {
    title: "Business Intelligence",
    cards: [
      {
        key: "bi-dashboard",
        title: "Dashboard Executiv",
        description: "KPI-uri agregat la nivel de companie",
        icon: <LineChartOutlined style={{ fontSize: 28 }} />,
        color: "#eb2f96",
        link: "/bi",
      },
      {
        key: "bi-reports",
        title: "Rapoarte",
        description: "Generator rapoarte parametrizabile",
        icon: <BarChartOutlined style={{ fontSize: 28 }} />,
        color: "#eb2f96",
        link: "/bi/reports",
      },
    ],
  },
  {
    title: "Sistem",
    cards: [
      {
        key: "settings",
        title: "Configurare",
        description: "Setări organizație și platformă",
        icon: <SettingOutlined style={{ fontSize: 28 }} />,
        color: "#8c8c8c",
        link: "/settings",
      },
      {
        key: "users",
        title: "Utilizatori",
        description: "Management utilizatori și invitații",
        icon: <UserOutlined style={{ fontSize: 28 }} />,
        color: "#8c8c8c",
        link: "/settings/users",
      },
      {
        key: "roles",
        title: "Roluri & Permisiuni",
        description: "Configurare RBAC per rol",
        icon: <SafetyOutlined style={{ fontSize: 28 }} />,
        color: "#8c8c8c",
        link: "/settings/roles",
      },
      {
        key: "audit",
        title: "Audit Log",
        description: "Istoric acțiuni și audit trail",
        icon: <AuditOutlined style={{ fontSize: 28 }} />,
        color: "#8c8c8c",
        link: "/settings/audit",
      },
    ],
  },
];

/* ─── Component ───────────────────────────────────────────────────────────── */

export default function ModuleGridPage() {
  const navigate = useNavigate();
  const { token } = theme.useToken();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>
          BuildWise
        </Title>
        <Text type="secondary">
          F157 | Selectează un modul pentru a începe
        </Text>
      </div>

      {sections.map((section) => (
        <div key={section.title} style={{ marginBottom: 32 }}>
          <Title
            level={5}
            style={{
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              color: "#555",
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
