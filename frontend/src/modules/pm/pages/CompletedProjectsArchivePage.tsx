/**
 * Completed Projects Archive — F090: Baza de date proiecte finalizate
 * + F142: Export rapoarte (Excel & PDF)
 *
 * Arhivă cu căutare, filtrare, statistici, export.
 */
import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Row,
  Col,
  Table,
  Input,
  Tag,
  Button,
  Space,
  Statistic,
  Progress,
  Tooltip,
  message,
  Empty,
} from "antd";
import {
  SearchOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  ProjectOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  FieldTimeOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import type { PMProjectListItem } from "../../../types";
import { pmService } from "../services/pmService";

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

function fmtCurrency(v?: number | null): string {
  if (v == null) return "—";
  return new Intl.NumberFormat("ro-RO", {
    style: "currency",
    currency: "RON",
    maximumFractionDigits: 0,
  }).format(v);
}

function healthColor(h?: string): string {
  switch (h) {
    case "green":
      return "#52c41a";
    case "yellow":
      return "#faad14";
    case "red":
      return "#ff4d4f";
    default:
      return "#d9d9d9";
  }
}

/* ─── Main Component ──────────────────────────────────────────────────────── */

export default function CompletedProjectsArchivePage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const perPage = 20;

  const { data: resp, isLoading } = useQuery({
    queryKey: ["pm", "completed-projects", page, search],
    queryFn: () =>
      pmService.listCompletedProjects({ page, per_page: perPage, search: search || undefined }),
  });

  const projects = resp?.data ?? [];
  const total = resp?.meta?.total ?? 0;

  /* ─── Aggregate Stats ──────────────────────────────────────────────────── */

  const stats = {
    totalProjects: total,
    totalBudget: projects.reduce((s, p) => s + (p.budget_allocated ?? 0), 0),
    totalActual: projects.reduce((s, p) => s + (p.budget_actual ?? 0), 0),
    avgCompletion: projects.length
      ? projects.reduce((s, p) => s + p.percent_complete, 0) / projects.length
      : 0,
  };

  /* ─── Export Handlers ──────────────────────────────────────────────────── */

  const handleExport = useCallback(async (format: "pdf" | "excel") => {
    try {
      const blob = await pmService.exportCompletedProjects(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `arhiva-proiecte.${format === "pdf" ? "pdf" : "xlsx"}`;
      a.click();
      URL.revokeObjectURL(url);
      message.success(`Export ${format.toUpperCase()} descărcat`);
    } catch {
      message.error("Eroare la export. Încercați din nou.");
    }
  }, []);

  /* ─── Table Columns ────────────────────────────────────────────────────── */

  const columns: ColumnsType<PMProjectListItem> = [
    {
      title: "Cod",
      dataIndex: "project_number",
      width: 120,
      sorter: (a, b) => a.project_number.localeCompare(b.project_number),
    },
    {
      title: "Nume Proiect",
      dataIndex: "name",
      ellipsis: true,
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: "Tip",
      dataIndex: "project_type",
      width: 130,
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: "Sănătate",
      dataIndex: "health_indicator",
      width: 90,
      align: "center",
      render: (v: string) => (
        <Tooltip title={v ?? "N/A"}>
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              background: healthColor(v),
              margin: "0 auto",
            }}
          />
        </Tooltip>
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
      sorter: (a, b) => (a.budget_allocated ?? 0) - (b.budget_allocated ?? 0),
      render: (v: number) => fmtCurrency(v),
    },
    {
      title: "Cost Real",
      dataIndex: "budget_actual",
      width: 130,
      align: "right",
      render: (v: number, rec) => {
        const over = rec.budget_allocated && v > rec.budget_allocated;
        return <span style={{ color: over ? "#ff4d4f" : undefined }}>{fmtCurrency(v)}</span>;
      },
    },
    {
      title: "Perioadă",
      key: "period",
      width: 200,
      render: (_: unknown, rec: PMProjectListItem) => {
        const start = rec.planned_start_date
          ? new Date(rec.planned_start_date).toLocaleDateString("ro-RO")
          : "—";
        const end = rec.planned_end_date
          ? new Date(rec.planned_end_date).toLocaleDateString("ro-RO")
          : "—";
        return `${start} → ${end}`;
      },
    },
    {
      title: "Finalizat",
      dataIndex: "created_at",
      width: 110,
      render: (v: string) => new Date(v).toLocaleDateString("ro-RO"),
      sorter: (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      defaultSortOrder: "descend",
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2 style={{ margin: 0 }}>Arhivă Proiecte Finalizate</h2>
          <span style={{ color: "#888" }}>F090 + F142 | Baza de date proiecte finalizate cu export</span>
        </Col>
        <Col>
          <Space>
            <Button icon={<FilePdfOutlined />} onClick={() => handleExport("pdf")}>
              Export PDF
            </Button>
            <Button icon={<FileExcelOutlined />} type="primary" onClick={() => handleExport("excel")}>
              Export Excel
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Total Proiecte"
              value={stats.totalProjects}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Completare Medie"
              value={stats.avgCompletion.toFixed(0)}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Total Buget"
              value={fmtCurrency(stats.totalBudget)}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Total Cost Real"
              value={fmtCurrency(stats.totalActual)}
              prefix={<FieldTimeOutlined />}
              valueStyle={{
                color: stats.totalActual > stats.totalBudget ? "#ff4d4f" : "#52c41a",
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* Search */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Input
          placeholder="Caută după nume proiect, cod, tip..."
          prefix={<SearchOutlined />}
          allowClear
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          style={{ maxWidth: 400 }}
        />
      </Card>

      {/* Table */}
      <Card size="small">
        {projects.length > 0 || isLoading ? (
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
              showTotal: (t) => `${t} proiecte finalizate`,
              showSizeChanger: false,
            }}
            scroll={{ x: 1100 }}
          />
        ) : (
          <Empty description="Niciun proiect finalizat găsit" />
        )}
      </Card>
    </div>
  );
}
