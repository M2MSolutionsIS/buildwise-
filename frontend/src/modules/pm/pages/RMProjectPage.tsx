/**
 * E-014.7: Tab RM Proiect — Mini Dashboard resurse per proiect
 * F083: Alocare resurse per proiect (sync RM bidirecțional)
 * F117: Alocare resurse pe proiecte/faze
 * F118: Urmărire consum resurse real-time
 *
 * Specific P2 (BAHM) — subset filtrat din E-032 Resource Dashboard.
 * KPI: echipe alocate, echipamente, utilizare %, conflicte.
 * Tabel resurse alocate cu status + acțiuni.
 * Link către Dashboard RM complet (E-032).
 */
import { useMemo } from "react";
import {
  Card,
  Table,
  Tag,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Space,
  Spin,
  Button,
  Progress,
  Empty,
  Badge,
  Tooltip,
} from "antd";
import {
  TeamOutlined,
  ToolOutlined,
  DashboardOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { ResourceAllocation } from "../../../types";

const { Title, Text } = Typography;

// ─── Status config ──────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  active: { color: "green", label: "Activ" },
  planned: { color: "blue", label: "Planificat" },
  idle: { color: "default", label: "Inactiv" },
  completed: { color: "geekblue", label: "Finalizat" },
  conflict: { color: "red", label: "Conflict" },
};

const RESOURCE_TYPE_LABELS: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  employee: { label: "Echipă", color: "#1677ff", icon: <TeamOutlined /> },
  equipment: { label: "Echipament", color: "#fa8c16", icon: <ToolOutlined /> },
};

// ─── Semaphore helper ───────────────────────────────────────────────────────

function getUtilizationSemaphore(pct: number): { color: string; label: string } {
  if (pct >= 90) return { color: "#ff4d4f", label: "Critic" };
  if (pct >= 70) return { color: "#faad14", label: "Atenție" };
  return { color: "#52c41a", label: "OK" };
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function RMProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // RM summary for project
  const { data: summaryData, isLoading } = useQuery({
    queryKey: ["rm-project-summary", projectId],
    queryFn: () => pmService.getRMProjectSummary(projectId!),
    enabled: !!projectId,
  });

  // Also fetch allocations for the detail table
  const { data: allocData } = useQuery({
    queryKey: ["pm-allocations", projectId],
    queryFn: () => pmService.listAllocations(projectId!),
    enabled: !!projectId,
  });

  const summary = summaryData?.data;
  const allocations = allocData?.data ?? [];

  // Computed KPIs
  const kpis = useMemo(() => {
    if (summary) {
      return {
        teams: summary.teams_allocated,
        equipment: summary.equipment_count,
        utilization: summary.utilization_percent,
        conflicts: summary.conflicts_count,
      };
    }
    // Fallback: compute from allocations
    const employees = allocations.filter((a) => a.resource_type === "employee");
    const equipments = allocations.filter((a) => a.resource_type === "equipment");
    const avgUtil =
      allocations.length > 0
        ? allocations.reduce((s, a) => s + a.allocation_percent, 0) / allocations.length
        : 0;
    const conflictCount = allocations.filter((a) => a.has_conflict).length;
    return {
      teams: employees.length,
      equipment: equipments.length,
      utilization: Math.round(avgUtil),
      conflicts: conflictCount,
    };
  }, [summary, allocations]);

  const utilizationSemaphore = getUtilizationSemaphore(kpis.utilization);

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (allocations.length === 0 && !summary) {
    return (
      <div style={{ padding: 24 }}>
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/pm`)}
              >
                Înapoi la Proiecte
              </Button>
              <Title level={4} style={{ margin: 0 }}>
                Resurse Proiect (E-014.7 / F083)
              </Title>
            </Space>
          </Col>
        </Row>
        <Card>
          <Empty description="Nu există resurse alocate pentru acest proiect">
            <Button
              type="primary"
              onClick={() => navigate("/rm/dashboard")}
            >
              Alocă resurse din Dashboard RM
            </Button>
          </Empty>
        </Card>
      </div>
    );
  }

  // ─── Table columns ────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Tip",
      dataIndex: "resource_type",
      key: "resource_type",
      width: 100,
      render: (v: string) => {
        const cfg = RESOURCE_TYPE_LABELS[v];
        return cfg ? (
          <Space>
            {cfg.icon}
            <Text>{cfg.label}</Text>
          </Space>
        ) : (
          v
        );
      },
      filters: [
        { text: "Echipă", value: "employee" },
        { text: "Echipament", value: "equipment" },
      ],
      onFilter: (value: unknown, record: ResourceAllocation) => record.resource_type === value,
    },
    {
      title: "Resursă",
      key: "resource_name",
      width: 180,
      render: (_: unknown, r: ResourceAllocation) =>
        r.employee_id ?? r.equipment_id ?? "—",
    },
    {
      title: "Perioadă alocată",
      key: "period",
      width: 180,
      render: (_: unknown, r: ResourceAllocation) => (
        <Text>
          {new Date(r.start_date).toLocaleDateString("ro-RO")} —{" "}
          {new Date(r.end_date).toLocaleDateString("ro-RO")}
        </Text>
      ),
    },
    {
      title: "Ore alocate",
      dataIndex: "allocated_hours",
      key: "alloc_hours",
      width: 100,
      align: "right" as const,
      render: (v: number | undefined) => v?.toLocaleString("ro-RO") ?? "—",
    },
    {
      title: "Ore reale",
      dataIndex: "actual_hours",
      key: "actual_hours",
      width: 100,
      align: "right" as const,
      render: (v: number | undefined) => v?.toLocaleString("ro-RO") ?? "—",
    },
    {
      title: "Utilizare %",
      dataIndex: "allocation_percent",
      key: "utilization",
      width: 130,
      render: (v: number) => {
        const sem = getUtilizationSemaphore(v);
        return (
          <Tooltip title={sem.label}>
            <Progress
              percent={v}
              size="small"
              strokeColor={sem.color}
              style={{ width: 90 }}
            />
          </Tooltip>
        );
      },
      sorter: (a: ResourceAllocation, b: ResourceAllocation) =>
        a.allocation_percent - b.allocation_percent,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (v: string, r: ResourceAllocation) => {
        if (r.has_conflict)
          return (
            <Badge dot color="red">
              <Tag color="red" icon={<WarningOutlined />}>
                Conflict
              </Tag>
            </Badge>
          );
        const cfg = STATUS_CONFIG[v] ?? { color: "default", label: v };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(`/pm`)}
            >
              Înapoi
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              Resurse Proiect (E-014.7 / F083)
            </Title>
          </Space>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => navigate("/rm/dashboard")}
          >
            Vizualizare complet Dashboard RM (E-032)
          </Button>
        </Col>
      </Row>

      {/* Conflict alert */}
      {kpis.conflicts > 0 && (
        <Alert
          type="error"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 16 }}
          message={`${kpis.conflicts} conflict${kpis.conflicts > 1 ? "e" : ""} de resurse detectate`}
          description="Există suprapuneri de alocare. Verifică în Gantt Dual-Layer (E-038) pentru detalii."
          action={
            <Button
              size="small"
              danger
              onClick={() => navigate(`/pm/projects/${projectId}/gantt`)}
            >
              Vezi Gantt
            </Button>
          }
        />
      )}

      {/* KPI Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Echipe alocate"
              value={kpis.teams}
              prefix={<TeamOutlined style={{ color: "#1677ff" }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Echipamente"
              value={kpis.equipment}
              prefix={<ToolOutlined style={{ color: "#fa8c16" }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Utilizare medie"
              value={kpis.utilization}
              suffix="%"
              valueStyle={{ color: utilizationSemaphore.color }}
              prefix={
                <DashboardOutlined
                  style={{ color: utilizationSemaphore.color }}
                />
              }
            />
            <Tag
              color={
                utilizationSemaphore.label === "OK"
                  ? "green"
                  : utilizationSemaphore.label === "Atenție"
                  ? "orange"
                  : "red"
              }
              style={{ marginTop: 4 }}
            >
              {utilizationSemaphore.label}
            </Tag>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Conflicte"
              value={kpis.conflicts}
              valueStyle={{
                color: kpis.conflicts > 0 ? "#ff4d4f" : "#52c41a",
              }}
              prefix={
                kpis.conflicts > 0 ? (
                  <WarningOutlined />
                ) : (
                  <CheckCircleOutlined />
                )
              }
            />
          </Card>
        </Col>
      </Row>

      {/* Resource Allocations Table */}
      <Card
        title={
          <Space>
            <Text strong>Resurse alocate proiectului</Text>
            <Badge count={allocations.length} style={{ backgroundColor: "#1677ff" }} />
          </Space>
        }
      >
        <Table
          dataSource={allocations}
          rowKey="id"
          size="small"
          columns={columns}
          scroll={{ x: 900 }}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          rowClassName={(r: ResourceAllocation) =>
            r.has_conflict ? "ant-table-row-error" : ""
          }
        />
      </Card>
    </div>
  );
}
