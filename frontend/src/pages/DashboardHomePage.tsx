/**
 * E-001 — Dashboard Principal (Home Screen)
 * ROW 1: 4 KPI Cards
 * ROW 2: Pipeline Overview (60%) + Proiecte Active (40%)
 * ROW 3: Widget RM (60%, P2) + TrueCast (40%, P2)
 * ROW 4: Alerte recente
 */
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Row,
  Col,
  Tag,
  Button,
  Space,
  Progress,
  Table,
  Empty,
} from "antd";
import {
  PlusOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { pipelineService } from "../modules/pipeline/services/pipelineService";
import { pmService } from "../modules/pm/services/pmService";
import { usePrototypeStore } from "../stores/prototypeStore";
import { useTranslation } from "../i18n";
import { SkeletonKPI } from "../components/SkeletonLoaders";

/* ─── Dark theme color constants from wireframe ──────────────────────────── */
const C = {
  card: "#1A1A2E",
  border: "rgba(255,255,255,0.08)",
  primary: "#2563EB",
  crm: "#1E40AF",
  pipeline: "#7C3AED",
  pm: "#047857",
  rm: "#9F1239",
  bi: "#B45309",
  textPrimary: "#F1F5F9",
  textSecondary: "#94A3B8",
  textTertiary: "#64748B",
  bgSidebar: "#0F172A",
  statusGreen: "#047857",
  statusYellow: "#B45309",
  statusRed: "#9F1239",
  statusBlue: "#2563EB",
  statusGreenBg: "rgba(4,120,87,0.15)",
  statusYellowBg: "rgba(180,83,9,0.15)",
  statusRedBg: "rgba(159,18,57,0.15)",
  statusBlueBg: "rgba(37,99,235,0.15)",
  statusGrayBg: "rgba(107,114,128,0.15)",
  statusGray: "#6B7280",
};

/* ─── Status badge component ─────────────────────────────────────────────── */

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string; label: string }> = {
    active: { bg: C.statusGreenBg, color: C.statusGreen, label: "Activ" },
    in_progress: { bg: C.statusBlueBg, color: C.statusBlue, label: "In progres" },
    won: { bg: C.statusGreenBg, color: C.statusGreen, label: "Castigat" },
    lost: { bg: C.statusRedBg, color: C.statusRed, label: "Pierdut" },
    pending: { bg: C.statusYellowBg, color: C.statusYellow, label: "In asteptare" },
    completed: { bg: C.statusGreenBg, color: C.statusGreen, label: "Finalizat" },
    archived: { bg: C.statusGrayBg, color: C.statusGray, label: "Arhivat" },
  };
  const s = map[status] || { bg: C.statusGrayBg, color: C.statusGray, label: status };
  return (
    <Tag style={{ background: s.bg, color: s.color, border: "none", borderRadius: 4, fontSize: 11 }}>
      {s.label}
    </Tag>
  );
}

/* ─── KPI Card component ─────────────────────────────────────────────────── */

function KPICard({ label, value, suffix, delta, deltaType }: {
  label: string;
  value: string | number;
  suffix?: string;
  delta?: number;
  deltaType?: "up" | "down";
}) {
  return (
    <Card
      style={{
        background: C.card,
        border: `1px solid ${C.border}`,
        borderTop: `3px solid ${C.primary}`,
        borderRadius: 8,
      }}
      styles={{ body: { padding: 16 } }}
    >
      <div style={{ fontSize: 12, color: C.textSecondary, marginBottom: 4 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span style={{ fontSize: 24, fontWeight: 700, color: C.textPrimary }}>{value}</span>
        {suffix && <span style={{ fontSize: 13, color: C.textSecondary }}>{suffix}</span>}
      </div>
      {delta !== undefined && (
        <div style={{ marginTop: 4, fontSize: 12 }}>
          {deltaType === "up" ? (
            <span style={{ color: C.statusGreen }}><ArrowUpOutlined /> +{delta}%</span>
          ) : (
            <span style={{ color: C.statusRed }}><ArrowDownOutlined /> {delta}%</span>
          )}
          <span style={{ color: C.textTertiary, marginLeft: 4 }}>vs. luna anterioară</span>
        </div>
      )}
    </Card>
  );
}

/* ─── Main Component ─────────────────────────────────────────────────────── */

export default function DashboardHomePage() {
  const navigate = useNavigate();
  const { isP2Plus } = usePrototypeStore();
  const t = useTranslation();

  // Fetch sales KPI data
  const { data: kpiData, isLoading: kpiLoading } = useQuery({
    queryKey: ["sales-kpi"],
    queryFn: () => pipelineService.getSalesKPI(),
    retry: false,
  });

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ["projects-list", 1],
    queryFn: () => pmService.listProjects({ page: 1, per_page: 5 }),
    retry: false,
  });

  const kpi = kpiData?.data;
  const projects = projectsData?.data || [];

  // Simulated pipeline top 5 for the table
  const pipelineRows = useMemo(() => {
    if (!kpi) return [];
    // Generate simulated rows from KPI data
    return [
      { key: "1", name: "Reabilitare bloc A3", value: 45000, stage: "Negociere", probability: 75 },
      { key: "2", name: "Izolatie cladire office", value: 32000, stage: "Oferta", probability: 60 },
      { key: "3", name: "Geam termic rezidential", value: 18500, stage: "Evaluare", probability: 40 },
      { key: "4", name: "Fatada ventilata B2", value: 67000, stage: "Contract", probability: 90 },
      { key: "5", name: "Tamplarie PVC lot 5", value: 23000, stage: "Identificare", probability: 20 },
    ];
  }, [kpi]);

  // Pipeline table columns
  const pipelineColumns = [
    {
      title: "Denumire",
      dataIndex: "name",
      key: "name",
      render: (v: string) => <span style={{ color: C.textPrimary, fontSize: 13 }}>{v}</span>,
    },
    {
      title: "Valoare",
      dataIndex: "value",
      key: "value",
      render: (v: number) => <span style={{ color: C.textPrimary }}>{v.toLocaleString()} RON</span>,
    },
    {
      title: "Etapa",
      dataIndex: "stage",
      key: "stage",
      render: (v: string) => <Tag style={{ background: "rgba(124,58,237,0.15)", color: "#7C3AED", border: "none", fontSize: 11 }}>{v}</Tag>,
    },
    {
      title: "Prob.",
      dataIndex: "probability",
      key: "probability",
      render: (v: number) => (
        <span style={{ color: v >= 70 ? C.statusGreen : v >= 40 ? C.statusYellow : C.textTertiary }}>{v}%</span>
      ),
    },
  ];

  // RM traffic lights (simulated data for P2)
  const rmLights = [
    { label: "Echipe disponibile", value: 4, color: C.statusGreen },
    { label: "Echipamente libere", value: 7, color: C.statusYellow },
    { label: "Conflicte active", value: 2, color: C.statusRed },
    { label: "Utilizare medie", value: "78%", color: C.statusBlue },
  ];

  // TrueCast simulated
  const trueCast = [
    { label: "Venituri estimate", value: "125,400 RON", color: C.statusGreen },
    { label: "Cheltuieli estimate", value: "89,200 RON", color: C.statusYellow },
    { label: "Profit estimat", value: "36,200 RON", color: C.statusBlue },
  ];

  // Alerts
  const alerts = [
    { icon: <WarningOutlined style={{ color: C.statusYellow }} />, message: "Oportunitate stagnanta: Reabilitare bloc A3 (15 zile)", time: "acum 2h" },
    { icon: <ClockCircleOutlined style={{ color: C.statusBlue }} />, message: "Termen deviz depasit: Izolatie cladire office", time: "acum 5h" },
  ];

  return (
    <div>
      {/* ─── ROW 1: KPI Cards ──────────────────────────────────────────────── */}
      {kpiLoading ? (
        <div style={{ marginBottom: 16 }}>
          <SkeletonKPI count={4} />
        </div>
      ) : (
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={12} lg={6}>
          <KPICard
            label="Total Contacte"
            value={kpi?.total_contacts ?? 0}
            delta={12}
            deltaType="up"
          />
        </Col>
        <Col xs={12} lg={6}>
          <KPICard
            label="Valoare Pipeline"
            value={kpi?.pipeline_value ? kpi.pipeline_value.toLocaleString() : "0"}
            suffix="RON"
            delta={8}
            deltaType="up"
          />
        </Col>
        <Col xs={12} lg={6}>
          <KPICard
            label="Proiecte Active"
            value={projects.length}
            delta={-3}
            deltaType="down"
          />
        </Col>
        <Col xs={12} lg={6}>
          <KPICard
            label="Win Rate"
            value={kpi?.conversion_rate ? `${Math.round(kpi.conversion_rate)}` : "0"}
            suffix="%"
            delta={5}
            deltaType="up"
          />
        </Col>
      </Row>
      )}

      {/* ─── ROW 2: Pipeline Overview + Proiecte Active ────────────────────── */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        {/* Pipeline Overview — 60% */}
        <Col xs={24} lg={14}>
          <Card
            style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, height: "100%" }}
            styles={{ body: { padding: 16 } }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: C.textPrimary }}>Pipeline Overview</span>
              <Button
                size="small"
                type="link"
                style={{ color: C.primary, fontSize: 12 }}
                onClick={() => navigate("/pipeline/board")}
              >
                Vezi tot
              </Button>
            </div>
            {pipelineRows.length > 0 ? (
              <Table
                dataSource={pipelineRows}
                columns={pipelineColumns}
                pagination={false}
                size="small"
                style={{ background: "transparent" }}
              />
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={<span style={{ color: C.textTertiary }}>Nicio oportunitate inca</span>}
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/pipeline/opportunities/new")}>
                  Adauga oportunitate
                </Button>
              </Empty>
            )}
          </Card>
        </Col>

        {/* Proiecte Active — 40% */}
        <Col xs={24} lg={10}>
          <Card
            style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, height: "100%" }}
            styles={{ body: { padding: 16 } }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: C.textPrimary }}>{t.nav.projects}</span>
              <Button
                size="small"
                type="link"
                style={{ color: C.primary, fontSize: 12 }}
                onClick={() => navigate("/pm")}
              >
                Vezi tot
              </Button>
            </div>
            {projects.length > 0 ? (
              <Space direction="vertical" style={{ width: "100%" }} size={8}>
                {projects.slice(0, 5).map((p: { id: string; name: string; status: string; completion_percentage?: number }) => (
                  <div
                    key={p.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "6px 0",
                      borderBottom: "1px solid rgba(255,255,255,0.04)",
                      cursor: "pointer",
                    }}
                    onClick={() => navigate(`/pm/projects/${p.id}/gantt`)}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, color: C.textPrimary, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {p.name}
                      </div>
                      <StatusBadge status={p.status} />
                    </div>
                    <Progress
                      percent={p.completion_percentage ?? 0}
                      size="small"
                      style={{ width: 80, margin: 0 }}
                      strokeColor={C.pm}
                    />
                  </div>
                ))}
              </Space>
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={<span style={{ color: C.textTertiary }}>Niciun proiect activ</span>}
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/pm")}>
                  Proiect nou
                </Button>
              </Empty>
            )}
          </Card>
        </Col>
      </Row>

      {/* ─── ROW 3: RM Widget + TrueCast (P2+ only) ───────────────────────── */}
      {isP2Plus() && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          {/* RM Traffic Lights — 60% */}
          <Col xs={24} lg={14}>
            <Card
              style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, height: "100%" }}
              styles={{ body: { padding: 16 } }}
            >
              <span style={{ fontSize: 13, fontWeight: 600, color: C.textPrimary, display: "block", marginBottom: 12 }}>
                Resource Management
              </span>
              <Row gutter={[12, 12]}>
                {rmLights.map((item) => (
                  <Col xs={12} key={item.label}>
                    <div
                      style={{
                        background: "#0F172A",
                        borderRadius: 8,
                        padding: 12,
                        border: `1px solid ${C.border}`,
                      }}
                    >
                      <div style={{ fontSize: 11, color: C.textTertiary, marginBottom: 4 }}>{item.label}</div>
                      <div style={{ fontSize: 24, fontWeight: 700, color: item.color }}>{item.value}</div>
                    </div>
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>

          {/* TrueCast — 40% */}
          <Col xs={24} lg={10}>
            <Card
              style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, height: "100%" }}
              styles={{ body: { padding: 16 } }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
                <ThunderboltOutlined style={{ color: C.bi }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: C.textPrimary }}>TrueCast</span>
              </div>
              <Space direction="vertical" style={{ width: "100%" }} size={12}>
                {trueCast.map((item) => (
                  <div key={item.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 13, color: C.textSecondary }}>{item.label}</span>
                    <span style={{ fontSize: 16, fontWeight: 600, color: item.color }}>{item.value}</span>
                  </div>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      )}

      {/* ─── ROW 4: Alerte recente ─────────────────────────────────────────── */}
      <Card
        style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8 }}
        styles={{ body: { padding: 16 } }}
      >
        <span style={{ fontSize: 13, fontWeight: 600, color: C.textPrimary, display: "block", marginBottom: 12 }}>
          Alerte recente
        </span>
        {alerts.length > 0 ? (
          <Space direction="vertical" style={{ width: "100%" }} size={8}>
            {alerts.map((a, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "6px 0",
                  borderBottom: i < alerts.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none",
                }}
              >
                {a.icon}
                <span style={{ flex: 1, fontSize: 13, color: C.textSecondary }}>{a.message}</span>
                <span style={{ fontSize: 11, color: C.textTertiary, whiteSpace: "nowrap" }}>{a.time}</span>
              </div>
            ))}
          </Space>
        ) : (
          <div style={{ textAlign: "center", padding: "16px 0", color: C.textTertiary, fontSize: 13 }}>
            <CheckCircleOutlined style={{ fontSize: 20, marginBottom: 4, display: "block" }} />
            Nicio alerta activa
          </div>
        )}
      </Card>
    </div>
  );
}
