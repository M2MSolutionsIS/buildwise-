/**
 * E-014: Project Detail Hub
 * Overview page with KPI cards + tabs/links to all PM sub-modules.
 * Route: /pm/projects/:projectId
 */
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Typography,
  Card,
  Row,
  Col,
  Tag,
  Space,
  Progress,
  Descriptions,
  Divider,
  Button,
  Modal,
  Select,
  App,
} from "antd";
import {
  ProjectOutlined,
  ScheduleOutlined,
  DollarOutlined,
  TeamOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
  SafetyOutlined,
  AimOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  DatabaseOutlined,
  SolutionOutlined,
  InboxOutlined,
  BookOutlined,
  TruckOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import { SkeletonPage } from "../../../components/SkeletonLoaders";
import EmptyState from "../../../components/EmptyState";

const { Title, Text } = Typography;

const HEALTH_COLORS: Record<string, string> = {
  green: "#52c41a",
  yellow: "#faad14",
  red: "#f5222d",
};

const STATUS_COLORS: Record<string, string> = {
  planning: "blue",
  in_progress: "processing",
  on_hold: "warning",
  completed: "success",
  cancelled: "error",
};

export default function ProjectDetailHubPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [newStatus, setNewStatus] = useState<string>("");

  const { data, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => pmService.getProject(projectId!),
    enabled: !!projectId,
  });

  const project = data?.data;
  const base = `/pm/projects/${projectId}`;

  // E-014.M1: Change project status
  const statusMut = useMutation({
    mutationFn: async (status: string) => {
      const endpoint = status === "completed" ? "close" : status === "cancelled" ? "cancel" : null;
      if (endpoint) {
        const { data } = await import("../../../services/api").then((m) => m.default.put(`/pm/projects/${projectId}/${endpoint}`));
        return data;
      }
      const { data: d } = await import("../../../services/api").then((m) => m.default.put(`/pm/projects/${projectId}`, { status }));
      return d;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      message.success("Status proiect actualizat");
      setStatusModalOpen(false);
    },
    onError: () => message.error("Eroare la schimbarea statusului"),
  });

  if (isLoading) return <SkeletonPage />;

  if (!project) {
    return (
      <EmptyState
        icon={<ProjectOutlined style={{ color: "#3B82F6" }} />}
        title="Proiect negăsit"
        description="Proiectul solicitat nu a fost găsit."
        actionLabel="Înapoi la proiecte"
        onAction={() => navigate("/pm")}
      />
    );
  }

  const subModules = [
    { key: "wbs", label: "WBS Editor", icon: <ProjectOutlined />, path: `${base}/wbs`, desc: "Structura arborescenta a proiectului" },
    { key: "deviz", label: "Deviz", icon: <DollarOutlined />, path: `${base}/deviz`, desc: "Estimare costuri și materiale" },
    { key: "gantt", label: "Gantt Chart", icon: <ScheduleOutlined />, path: `${base}/gantt`, desc: "Planificarea în timp a activităților" },
    { key: "timesheet", label: "Timesheet", icon: <ClockCircleOutlined />, path: `${base}/timesheet`, desc: "Pontaj și ore lucrate" },
    { key: "consumption", label: "Consum Materiale", icon: <InboxOutlined />, path: `${base}/consumption`, desc: "Urmărire consum materiale" },
    { key: "subcontractors", label: "Subcontractori", icon: <SolutionOutlined />, path: `${base}/subcontractors`, desc: "Gestionare subcontractori" },
    { key: "deliveries", label: "Livrări", icon: <TruckOutlined />, path: `${base}/deliveries`, desc: "Urmărire livrări materiale" },
    { key: "daily-reports", label: "Rapoarte Zilnice", icon: <FileTextOutlined />, path: `${base}/daily-reports`, desc: "Jurnalul zilnic al proiectului" },
    { key: "progress", label: "Monitorizare Progres", icon: <BarChartOutlined />, path: `${base}/progress`, desc: "EVM, CPI, SPI" },
    { key: "budget", label: "Control Buget", icon: <DollarOutlined />, path: `${base}/budget`, desc: "Buget alocat vs. consumat" },
    { key: "work-situations", label: "Situații de Lucrări", icon: <DatabaseOutlined />, path: `${base}/work-situations`, desc: "Situații cantitative și financiare" },
    { key: "risks", label: "Registru Riscuri", icon: <SafetyOutlined />, path: `${base}/risks`, desc: "Identificare și mitigare riscuri" },
    { key: "reception", label: "Recepție", icon: <AimOutlined />, path: `${base}/reception`, desc: "Punch list și procese verbale" },
    { key: "warranties", label: "Garanții", icon: <SafetyOutlined />, path: `${base}/warranties`, desc: "Urmărire termene garanție" },
    { key: "energy-impact", label: "Impact Energetic", icon: <ThunderboltOutlined />, path: `${base}/energy-impact`, desc: "Analiză PRE/POST eficiență" },
    { key: "resources", label: "Resurse Proiect", icon: <TeamOutlined />, path: `${base}/resources`, desc: "Alocare echipă și echipamente" },
    { key: "wiki", label: "Wiki", icon: <BookOutlined />, path: `${base}/wiki`, desc: "Documentație proiect" },
    { key: "report", label: "Rapoarte", icon: <FileTextOutlined />, path: `${base}/report`, desc: "Rapoarte sintetice proiect" },
  ];

  const budgetUsed = project.budget_allocated
    ? Math.round(((project.budget_actual || 0) / project.budget_allocated) * 100)
    : 0;

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <Space align="center">
            <Title level={3} style={{ margin: 0 }}>{project.name}</Title>
            <Tag color={STATUS_COLORS[project.status] || "default"} style={{ textTransform: "capitalize" }}>
              {project.status.replace(/_/g, " ")}
            </Tag>
            {project.health_indicator && (
              <Tag
                color={HEALTH_COLORS[project.health_indicator]}
                icon={
                  project.health_indicator === "green" ? <CheckCircleOutlined /> :
                  project.health_indicator === "yellow" ? <ExclamationCircleOutlined /> :
                  <ExclamationCircleOutlined />
                }
              >
                {project.health_indicator.toUpperCase()}
              </Tag>
            )}
          </Space>
          <Text type="secondary" style={{ display: "block", marginTop: 4 }}>
            {project.project_number} • {project.project_type}
          </Text>
          {project.description && (
            <Text type="secondary" style={{ display: "block", marginTop: 4, maxWidth: 600 }}>
              {project.description}
            </Text>
          )}
        </div>
        <Button onClick={() => { setNewStatus(project.status); setStatusModalOpen(true); }}>
          Schimbă status
        </Button>
      </div>

      {/* KPI Summary Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Text type="secondary" style={{ fontSize: 12 }}>Progres</Text>
            <div style={{ fontSize: 28, fontWeight: 700, color: "#3B82F6" }}>
              {project.percent_complete}%
            </div>
            <Progress percent={project.percent_complete} size="small" showInfo={false} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Text type="secondary" style={{ fontSize: 12 }}>Buget</Text>
            <div style={{ fontSize: 20, fontWeight: 700, color: budgetUsed > 90 ? "#EF4444" : "#10B981" }}>
              {(project.budget_actual || 0).toLocaleString("ro-RO")} {project.currency}
            </div>
            <Text type="secondary" style={{ fontSize: 11 }}>
              din {(project.budget_allocated || 0).toLocaleString("ro-RO")} ({budgetUsed}%)
            </Text>
            <Progress percent={budgetUsed} size="small" showInfo={false} status={budgetUsed > 90 ? "exception" : "normal"} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Text type="secondary" style={{ fontSize: 12 }}>CPI</Text>
            <div style={{ fontSize: 28, fontWeight: 700, color: (project.cpi || 1) >= 1 ? "#10B981" : "#EF4444" }}>
              {project.cpi?.toFixed(2) || "—"}
            </div>
            <Text type="secondary" style={{ fontSize: 11 }}>Cost Performance Index</Text>
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Text type="secondary" style={{ fontSize: 12 }}>SPI</Text>
            <div style={{ fontSize: 28, fontWeight: 700, color: (project.spi || 1) >= 1 ? "#10B981" : "#EF4444" }}>
              {project.spi?.toFixed(2) || "—"}
            </div>
            <Text type="secondary" style={{ fontSize: 11 }}>Schedule Performance Index</Text>
          </Card>
        </Col>
      </Row>

      {/* Project Details */}
      <Card
        size="small"
        style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)", marginBottom: 24 }}
      >
        <Descriptions column={{ xs: 1, sm: 2, md: 4 }} size="small">
          <Descriptions.Item label="Început planificat">
            {project.planned_start_date ? new Date(project.planned_start_date).toLocaleDateString("ro-RO") : "—"}
          </Descriptions.Item>
          <Descriptions.Item label="Sfârșit planificat">
            {project.planned_end_date ? new Date(project.planned_end_date).toLocaleDateString("ro-RO") : "—"}
          </Descriptions.Item>
          <Descriptions.Item label="Început actual">
            {project.actual_start_date ? new Date(project.actual_start_date).toLocaleDateString("ro-RO") : "—"}
          </Descriptions.Item>
          <Descriptions.Item label="Sfârșit actual">
            {project.actual_end_date ? new Date(project.actual_end_date).toLocaleDateString("ro-RO") : "—"}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Sub-modules Grid */}
      <Divider orientation="left">Module proiect</Divider>
      <Row gutter={[16, 16]}>
        {subModules.map((mod) => (
          <Col xs={12} sm={8} md={6} key={mod.key}>
            <Card
              hoverable
              size="small"
              style={{
                background: "#111827",
                border: "1px solid rgba(255,255,255,0.06)",
                height: "100%",
                cursor: "pointer",
              }}
              onClick={() => navigate(mod.path)}
            >
              <Space direction="vertical" size={4} style={{ width: "100%" }}>
                <div style={{ fontSize: 24, color: "#3B82F6" }}>{mod.icon}</div>
                <Text strong style={{ fontSize: 13 }}>{mod.label}</Text>
                <Text type="secondary" style={{ fontSize: 11 }}>{mod.desc}</Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* E-014.M1: Modal schimbare status proiect */}
      <Modal
        title="Schimbare Status Proiect"
        open={statusModalOpen}
        onCancel={() => setStatusModalOpen(false)}
        onOk={() => newStatus && statusMut.mutate(newStatus)}
        confirmLoading={statusMut.isPending}
        okText="Confirmă"
        cancelText="Anulează"
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          <Select
            value={newStatus}
            onChange={setNewStatus}
            style={{ width: "100%" }}
            options={[
              { label: "Planning", value: "planning" },
              { label: "In Progress", value: "in_progress" },
              { label: "On Hold", value: "on_hold" },
              { label: "Completed", value: "completed" },
              { label: "Cancelled", value: "cancelled" },
            ]}
          />
          {newStatus === "cancelled" && (
            <Tag color="red">Atenție: Proiectul va fi anulat definitiv.</Tag>
          )}
          {newStatus === "completed" && (
            <Tag color="green">Proiectul va fi marcat ca finalizat.</Tag>
          )}
        </Space>
      </Modal>
    </div>
  );
}
