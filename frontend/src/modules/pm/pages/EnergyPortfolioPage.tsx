/**
 * Energy Portfolio Dashboard — F161
 * Agregat cross-proiecte: total kWh economisiți, CO₂ redus, suprafață tratată,
 * coeficienți U medii, trend.
 *
 * Surse: F088 (Energy Impact) din toate proiectele finalizate (F090).
 */
import { useRef, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Progress,
  Spin,
  Empty,
} from "antd";
import {
  ThunderboltOutlined,
  CloudOutlined,
  HomeOutlined,
  ExperimentOutlined,
  ArrowDownOutlined,
  ProjectOutlined,
} from "@ant-design/icons";
import type { PMProjectListItem, EnergyImpact } from "../../../types";
import { pmService } from "../services/pmService";

/* ─── Constants ───────────────────────────────────────────────────────────── */

const U_VALUE_BAHM = 0.3; // W/m²K — BAHM thermally treated glass reference

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

function fmtNum(v?: number | null, decimals = 0): string {
  if (v == null) return "—";
  return new Intl.NumberFormat("ro-RO", { maximumFractionDigits: decimals }).format(v);
}

/* ─── Comparison Bar Chart ────────────────────────────────────────────────── */

function PortfolioChart({
  kwhSaved,
  co2Reduced,
  projectCount,
  areaTreated,
}: {
  kwhSaved: number;
  co2Reduced: number;
  projectCount: number;
  areaTreated: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const pad = { top: 40, right: 30, bottom: 50, left: 30 };
    const cW = W - pad.left - pad.right;
    const cH = H - pad.top - pad.bottom;

    // Data
    const bars = [
      { label: "kWh Economisiți", value: kwhSaved, color: "#52c41a", unit: "kWh/an" },
      { label: "CO₂ Redus", value: co2Reduced, color: "#1677ff", unit: "kg/an" },
      { label: "Suprafață", value: areaTreated, color: "#faad14", unit: "m²" },
      { label: "Proiecte", value: projectCount, color: "#722ed1", unit: "" },
    ];

    const maxVal = Math.max(...bars.map((b) => b.value), 1);
    const barWidth = cW / bars.length * 0.6;
    const gap = cW / bars.length;

    // Title
    ctx.fillStyle = "#333";
    ctx.font = "bold 14px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Energy Portfolio — Impact Agregat", W / 2, 22);

    // Bars
    bars.forEach((bar, i) => {
      const x = pad.left + gap * i + (gap - barWidth) / 2;
      const h = (bar.value / maxVal) * cH;
      const y = pad.top + cH - h;

      // Bar
      ctx.fillStyle = bar.color;
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, h, [4, 4, 0, 0]);
      ctx.fill();

      // Value
      ctx.fillStyle = "#333";
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(fmtNum(bar.value), x + barWidth / 2, y - 8);

      // Unit
      if (bar.unit) {
        ctx.fillStyle = "#999";
        ctx.font = "10px sans-serif";
        ctx.fillText(bar.unit, x + barWidth / 2, y - 22);
      }

      // Label
      ctx.fillStyle = "#666";
      ctx.font = "11px sans-serif";
      ctx.fillText(bar.label, x + barWidth / 2, H - 12);
    });
  }, [kwhSaved, co2Reduced, projectCount, areaTreated]);

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={300}
      style={{ width: "100%", height: 300 }}
    />
  );
}

/* ─── Main Component ──────────────────────────────────────────────────────── */

export default function EnergyPortfolioPage() {
  // F161: Aggregated portfolio
  const { data: portfolioResp, isLoading: loadingPortfolio } = useQuery({
    queryKey: ["pm", "energy-portfolio"],
    queryFn: () => pmService.getEnergyPortfolio(),
  });

  // F090: Completed projects for details table
  const { data: projectsResp, isLoading: loadingProjects } = useQuery({
    queryKey: ["pm", "completed-projects", 1, ""],
    queryFn: () => pmService.listCompletedProjects({ page: 1, per_page: 100 }),
  });

  const portfolio = portfolioResp?.data;
  const projects = projectsResp?.data ?? [];
  const isLoading = loadingPortfolio || loadingProjects;

  // U-value improvement
  const uImprovement = useMemo(() => {
    if (!portfolio?.avg_u_value_pre || !portfolio.avg_u_value_post) return null;
    return ((portfolio.avg_u_value_pre - portfolio.avg_u_value_post) / portfolio.avg_u_value_pre) * 100;
  }, [portfolio]);

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!portfolio) {
    return <Empty description="Nu există date Energy Portfolio" />;
  }

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2 style={{ margin: 0 }}>Energy Portfolio Dashboard</h2>
          <span style={{ color: "#888" }}>
            F161 | Impact energetic agregat cross-proiecte | Ref. U-value BAHM = {U_VALUE_BAHM} W/m²K
          </span>
        </Col>
      </Row>

      {/* KPI Cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="kWh Economisiți"
              value={fmtNum(portfolio.total_kwh_saved)}
              suffix="kWh/an"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="CO₂ Redus"
              value={fmtNum(portfolio.total_co2_reduced)}
              suffix="kg/an"
              prefix={<CloudOutlined />}
              valueStyle={{ color: "#1677ff" }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="Nr. Proiecte"
              value={portfolio.total_projects}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="Suprafață Tratată"
              value={fmtNum(portfolio.total_area_treated_sqm)}
              suffix="m²"
              prefix={<HomeOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="U-value Mediu PRE"
              value={portfolio.avg_u_value_pre?.toFixed(2) ?? "—"}
              suffix="W/m²K"
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card size="small">
            <Statistic
              title="U-value Mediu POST"
              value={portfolio.avg_u_value_post?.toFixed(2) ?? "—"}
              suffix="W/m²K"
              prefix={<ArrowDownOutlined />}
              valueStyle={{
                color:
                  portfolio.avg_u_value_post != null &&
                  portfolio.avg_u_value_post <= U_VALUE_BAHM
                    ? "#52c41a"
                    : "#faad14",
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* U-value improvement bar */}
      {uImprovement != null && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Row align="middle" gutter={16}>
            <Col span={6}>
              <strong>Îmbunătățire U-value medie</strong>
            </Col>
            <Col span={14}>
              <Progress
                percent={Math.min(uImprovement, 100)}
                strokeColor="#52c41a"
                format={() => `${uImprovement.toFixed(1)}%`}
              />
            </Col>
            <Col span={4}>
              <Tag color={portfolio.avg_u_value_post! <= U_VALUE_BAHM ? "green" : "orange"}>
                {portfolio.avg_u_value_post! <= U_VALUE_BAHM ? "≤ BAHM" : "> BAHM"}
              </Tag>
            </Col>
          </Row>
        </Card>
      )}

      {/* Chart */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <PortfolioChart
          kwhSaved={portfolio.total_kwh_saved}
          co2Reduced={portfolio.total_co2_reduced}
          projectCount={portfolio.total_projects}
          areaTreated={portfolio.total_area_treated_sqm}
        />
      </Card>

      {/* Projects Table */}
      <Card size="small" title="Proiecte Finalizate cu Impact Energetic">
        <Table
          size="small"
          dataSource={projects}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          scroll={{ x: 900 }}
          columns={[
            {
              title: "Cod",
              dataIndex: "project_number",
              width: 110,
            },
            {
              title: "Nume",
              dataIndex: "name",
              ellipsis: true,
            },
            {
              title: "Tip",
              dataIndex: "project_type",
              width: 120,
              render: (v: string) => <Tag>{v}</Tag>,
            },
            {
              title: "Status",
              dataIndex: "status",
              width: 110,
              render: (v: string) => (
                <Tag color={v === "completed" ? "green" : "blue"}>{v}</Tag>
              ),
            },
            {
              title: "Buget",
              dataIndex: "budget_allocated",
              width: 130,
              align: "right",
              render: (v: number) =>
                v != null
                  ? new Intl.NumberFormat("ro-RO", {
                      style: "currency",
                      currency: "RON",
                      maximumFractionDigits: 0,
                    }).format(v)
                  : "—",
            },
            {
              title: "Progres",
              dataIndex: "percent_complete",
              width: 100,
              render: (v: number) => <Progress percent={v} size="small" />,
            },
            {
              title: "Dată",
              dataIndex: "created_at",
              width: 100,
              render: (v: string) => new Date(v).toLocaleDateString("ro-RO"),
            },
          ]}
        />
      </Card>

      {/* Environmental Summary */}
      <Card size="small" style={{ marginTop: 16 }} title="Impact de Mediu — Echivalențe">
        <Row gutter={16}>
          <Col xs={12} sm={8}>
            <Statistic
              title="Copaci echivalent (CO₂)"
              value={
                portfolio.total_co2_reduced > 0
                  ? Math.round(portfolio.total_co2_reduced / 22)
                  : 0
              }
              suffix="copaci/an"
              valueStyle={{ color: "#52c41a" }}
            />
            <span style={{ color: "#888", fontSize: 12 }}>
              1 copac ≈ 22 kg CO₂/an
            </span>
          </Col>
          <Col xs={12} sm={8}>
            <Statistic
              title="Mașini scoase din circulație"
              value={
                portfolio.total_co2_reduced > 0
                  ? (portfolio.total_co2_reduced / 4600).toFixed(1)
                  : "0"
              }
              suffix="mașini/an"
              valueStyle={{ color: "#1677ff" }}
            />
            <span style={{ color: "#888", fontSize: 12 }}>
              1 mașină ≈ 4.600 kg CO₂/an
            </span>
          </Col>
          <Col xs={12} sm={8}>
            <Statistic
              title="Economie electricitate"
              value={
                portfolio.total_kwh_saved > 0
                  ? new Intl.NumberFormat("ro-RO", {
                      style: "currency",
                      currency: "RON",
                      maximumFractionDigits: 0,
                    }).format(portfolio.total_kwh_saved * 1.3)
                  : "—"
              }
              suffix="/an"
              valueStyle={{ color: "#faad14" }}
            />
            <span style={{ color: "#888", fontSize: 12 }}>
              Preț mediu ≈ 1.3 RON/kWh
            </span>
          </Col>
        </Row>
      </Card>
    </div>
  );
}
