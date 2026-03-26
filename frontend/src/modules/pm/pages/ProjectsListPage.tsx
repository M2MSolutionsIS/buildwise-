/**
 * E-013: Projects List — F101, F130
 * Lista proiectelor cu navigare cross-modul.
 * Din Contract semnat → auto-creare proiect ajunge aici.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Table,
  Tag,
  Button,
  Input,
  Space,
  Progress,
  Select,
  Row,
  Col,
  Statistic,
  Tooltip,
} from "antd";
import {
  SearchOutlined,
  ProjectOutlined,
  TeamOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import type { PMProjectListItem, ProjectStatus } from "../../../types";
import { pmService } from "../services/pmService";
import { useTranslation } from "../../../i18n";
import EmptyState from "../../../components/EmptyState";
import { SkeletonKPI } from "../../../components/SkeletonLoaders";

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

const STATUS_COLORS: Record<string, string> = {
  draft: "default",
  kickoff: "processing",
  planning: "cyan",
  in_progress: "blue",
  on_hold: "orange",
  post_execution: "purple",
  closing: "geekblue",
  completed: "green",
  cancelled: "red",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  kickoff: "Kickoff",
  planning: "Planificare",
  in_progress: "În Execuție",
  on_hold: "Suspendat",
  post_execution: "Post-Execuție",
  closing: "Închidere",
  completed: "Finalizat",
  cancelled: "Anulat",
};

function fmtCurrency(v?: number | null): string {
  if (v == null) return "—";
  return new Intl.NumberFormat("ro-RO", {
    style: "currency",
    currency: "RON",
    maximumFractionDigits: 0,
  }).format(v);
}

function healthDot(h?: string): React.ReactNode {
  const colors: Record<string, string> = {
    green: "#52c41a",
    yellow: "#faad14",
    red: "#ff4d4f",
  };
  return (
    <Tooltip title={h ?? "N/A"}>
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: colors[h ?? ""] ?? "#d9d9d9",
          display: "inline-block",
        }}
      />
    </Tooltip>
  );
}

/* ─── Component ───────────────────────────────────────────────────────────── */

export default function ProjectsListPage() {
  const navigate = useNavigate();
  const t = useTranslation();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const perPage = 20;

  const { data: resp, isLoading } = useQuery({
    queryKey: ["pm", "projects", page, search, statusFilter],
    queryFn: () =>
      pmService.listProjects({
        page,
        per_page: perPage,
        search: search || undefined,
        status: statusFilter,
      }),
  });

  const projects = resp?.data ?? [];
  const total = resp?.meta?.total ?? 0;

  // Quick stats from current page
  const activeCount = projects.filter(
    (p) => !["completed", "cancelled", "draft"].includes(p.status)
  ).length;

  const columns: ColumnsType<PMProjectListItem> = [
    {
      title: "",
      dataIndex: "health_indicator",
      width: 40,
      render: (v: string) => healthDot(v),
    },
    {
      title: "Cod",
      dataIndex: "project_number",
      width: 110,
      sorter: (a, b) => a.project_number.localeCompare(b.project_number),
    },
    {
      title: "Nume Proiect",
      dataIndex: "name",
      ellipsis: true,
      render: (name: string, rec: PMProjectListItem) => (
        <a onClick={() => navigate(`/pm/projects/${rec.id}/gantt`)}>{name}</a>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      width: 130,
      render: (v: ProjectStatus) => (
        <Tag color={STATUS_COLORS[v]}>{STATUS_LABELS[v] ?? v}</Tag>
      ),
    },
    {
      title: "Progres",
      dataIndex: "percent_complete",
      width: 120,
      sorter: (a, b) => a.percent_complete - b.percent_complete,
      render: (v: number) => <Progress percent={v} size="small" />,
    },
    {
      title: "Buget",
      dataIndex: "budget_allocated",
      width: 130,
      align: "right",
      render: (v: number) => fmtCurrency(v),
    },
    {
      title: "Cost",
      dataIndex: "budget_actual",
      width: 130,
      align: "right",
      render: (v: number, rec) => (
        <span
          style={{
            color:
              rec.budget_allocated && v > rec.budget_allocated
                ? "#ff4d4f"
                : undefined,
          }}
        >
          {fmtCurrency(v)}
        </span>
      ),
    },
    {
      title: "Perioadă",
      key: "period",
      width: 200,
      render: (_: unknown, rec: PMProjectListItem) => {
        const s = rec.planned_start_date
          ? new Date(rec.planned_start_date).toLocaleDateString("ro-RO")
          : "—";
        const e = rec.planned_end_date
          ? new Date(rec.planned_end_date).toLocaleDateString("ro-RO")
          : "—";
        return `${s} → ${e}`;
      },
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 180,
      render: (_: unknown, rec: PMProjectListItem) => (
        <Space size="small">
          <Tooltip title="Gantt Chart">
            <Button
              type="link"
              size="small"
              icon={<ProjectOutlined />}
              onClick={() => navigate(`/pm/projects/${rec.id}/gantt`)}
            />
          </Tooltip>
          <Tooltip title="Raport 3-in-1">
            <Button
              type="link"
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => navigate(`/pm/projects/${rec.id}/report`)}
            />
          </Tooltip>
          <Tooltip title="Impact Energetic">
            <Button
              type="link"
              size="small"
              icon={<ThunderboltOutlined />}
              onClick={() => navigate(`/pm/projects/${rec.id}/energy-impact`)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2 style={{ margin: 0 }}>{t.nav.projects}</h2>
          <span style={{ color: "#888" }}>
            E-013 | F101 | Flux: Contract semnat → Proiect auto-creat (F063)
          </span>
        </Col>
      </Row>

      {/* Stats */}
      {isLoading ? (
        <div style={{ marginBottom: 16 }}>
          <SkeletonKPI count={3} />
        </div>
      ) : (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={8}>
            <Card size="small">
              <Statistic title="Total" value={total} />
            </Card>
          </Col>
          <Col xs={8}>
            <Card size="small">
              <Statistic
                title="Active"
                value={activeCount}
                valueStyle={{ color: "#1677ff" }}
              />
            </Card>
          </Col>
          <Col xs={8}>
            <Card size="small">
              <Statistic
                title="Pagina curentă"
                value={projects.length}
                suffix={`/ ${total}`}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="Caută proiecte..."
            prefix={<SearchOutlined />}
            allowClear
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            style={{ width: 280 }}
          />
          <Select
            placeholder="Status"
            allowClear
            value={statusFilter}
            onChange={(v) => {
              setStatusFilter(v);
              setPage(1);
            }}
            style={{ width: 160 }}
            options={Object.entries(STATUS_LABELS).map(([val, label]) => ({
              value: val,
              label,
            }))}
          />
          <Button
            icon={<TeamOutlined />}
            onClick={() => navigate("/pm/archive")}
          >
            Arhivă Finalizate
          </Button>
          <Button
            icon={<ThunderboltOutlined />}
            onClick={() => navigate("/pm/energy-portfolio")}
          >
            Energy Portfolio
          </Button>
        </Space>
      </Card>

      {/* Table */}
      <Card size="small">
        <Table
          loading={isLoading}
          dataSource={projects}
          columns={columns}
          rowKey="id"
          size="small"
          pagination={{
            current: page,
            pageSize: perPage,
            total,
            onChange: setPage,
            showTotal: (t) => `${t} proiecte`,
            showSizeChanger: false,
          }}
          scroll={{ x: 1100 }}
          locale={{
            emptyText: (
              <EmptyState
                icon={<ProjectOutlined style={{ color: "#047857" }} />}
                title="Niciun proiect"
                description="Proiectele se creează automat la semnarea unui contract."
              />
            ),
          }}
        />
      </Card>
    </div>
  );
}
