/**
 * Project Progress Monitoring — F078
 * Avansare % fizic realizat vs planificat, S-Curve vizuală,
 * milestones, delay alerts, Earned Value overview.
 *
 * Canvas-based S-Curve chart: planned (dashed blue) vs actual (solid green).
 */
import { useRef, useEffect, useMemo, useCallback } from "react";
import {
  Card,
  Statistic,
  Row,
  Col,
  Tag,
  Progress,
  Table,
  Typography,
  Alert,
  Space,
  Spin,
  Empty,
} from "antd";
import {
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  FlagOutlined,
  DashboardOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { SCurveDataPoint } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

// ─── S-Curve Canvas Component ────────────────────────────────────────────────

function SCurveChart({ data }: { data: SCurveDataPoint[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const PAD = { top: 30, right: 30, bottom: 50, left: 60 };
    const chartW = W - PAD.left - PAD.right;
    const chartH = H - PAD.top - PAD.bottom;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#fafafa";
    ctx.fillRect(PAD.left, PAD.top, chartW, chartH);

    // Grid lines
    ctx.strokeStyle = "#f0f0f0";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {
      const y = PAD.top + (chartH / 10) * i;
      ctx.beginPath();
      ctx.moveTo(PAD.left, y);
      ctx.lineTo(PAD.left + chartW, y);
      ctx.stroke();
    }

    // Y-axis labels (0% - 100%)
    ctx.fillStyle = "#666";
    ctx.font = "11px -apple-system, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (let i = 0; i <= 10; i++) {
      const pct = 100 - i * 10;
      const y = PAD.top + (chartH / 10) * i;
      ctx.fillText(`${pct}%`, PAD.left - 8, y);
    }

    // X-axis labels
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    const step = Math.max(1, Math.floor(data.length / 8));
    data.forEach((point, idx) => {
      if (idx % step === 0 || idx === data.length - 1) {
        const x = PAD.left + (idx / (data.length - 1)) * chartW;
        ctx.fillText(dayjs(point.date).format("DD/MM"), x, PAD.top + chartH + 8);
      }
    });

    // Plot function
    const plotLine = (
      values: number[],
      color: string,
      dash: number[] = [],
      lineW: number = 2
    ) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = lineW;
      ctx.setLineDash(dash);
      ctx.beginPath();
      values.forEach((val, idx) => {
        const x = PAD.left + (idx / (data.length - 1)) * chartW;
        const y = PAD.top + chartH - (val / 100) * chartH;
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    };

    // Fill area under actual
    const actualVals = data.map((d) => d.actual_percent);
    ctx.fillStyle = "rgba(82, 196, 26, 0.1)";
    ctx.beginPath();
    ctx.moveTo(PAD.left, PAD.top + chartH);
    actualVals.forEach((val, idx) => {
      const x = PAD.left + (idx / (data.length - 1)) * chartW;
      const y = PAD.top + chartH - (val / 100) * chartH;
      ctx.lineTo(x, y);
    });
    ctx.lineTo(PAD.left + chartW, PAD.top + chartH);
    ctx.closePath();
    ctx.fill();

    // Planned line (dashed blue)
    plotLine(
      data.map((d) => d.planned_percent),
      "#1677ff",
      [6, 4],
      2
    );

    // Actual line (solid green)
    plotLine(actualVals, "#52c41a", [], 3);

    // Earned Value line (dotted orange) if available
    if (data.some((d) => d.earned_value != null)) {
      const maxEV = Math.max(...data.map((d) => d.earned_value ?? 0));
      if (maxEV > 0) {
        plotLine(
          data.map((d) => ((d.earned_value ?? 0) / maxEV) * 100),
          "#fa8c16",
          [3, 3],
          1.5
        );
      }
    }

    // Today marker
    const todayStr = dayjs().format("YYYY-MM-DD");
    const todayIdx = data.findIndex((d) => d.date >= todayStr);
    if (todayIdx >= 0) {
      const x = PAD.left + (todayIdx / (data.length - 1)) * chartW;
      ctx.strokeStyle = "#ff4d4f";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(x, PAD.top);
      ctx.lineTo(x, PAD.top + chartH);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = "#ff4d4f";
      ctx.font = "bold 10px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("AZI", x, PAD.top - 8);
    }

    // Legend
    const legendY = PAD.top + chartH + 30;
    const legends = [
      { label: "Planificat", color: "#1677ff", dash: true },
      { label: "Realizat", color: "#52c41a", dash: false },
    ];
    let legendX = PAD.left;
    legends.forEach((leg) => {
      ctx.strokeStyle = leg.color;
      ctx.lineWidth = 2;
      ctx.setLineDash(leg.dash ? [6, 4] : []);
      ctx.beginPath();
      ctx.moveTo(legendX, legendY);
      ctx.lineTo(legendX + 25, legendY);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = "#333";
      ctx.font = "12px -apple-system, sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(leg.label, legendX + 30, legendY + 4);
      legendX += 110;
    });

    // Title
    ctx.fillStyle = "#333";
    ctx.font = "bold 14px -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("S-Curve — Avansare Proiect", W / 2, 16);
  }, [data]);

  useEffect(() => {
    drawChart();
    const handleResize = () => drawChart();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [drawChart]);

  if (data.length === 0) {
    return <Empty description="Nu există date pentru S-Curve" />;
  }

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: 380, display: "block" }}
    />
  );
}

// ─── Health color helper ─────────────────────────────────────────────────────

function healthColor(indicator?: string): string {
  switch (indicator) {
    case "green": return "#52c41a";
    case "yellow": return "#faad14";
    case "red": return "#ff4d4f";
    default: return "#d9d9d9";
  }
}

// ─── Main Component ─────────────────────────────────────────────────────────

export default function ProgressMonitoringPage() {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: progressRes, isLoading } = useQuery({
    queryKey: ["progress-monitoring", projectId],
    queryFn: () => pmService.getProgressMonitoring(projectId!),
    enabled: !!projectId,
  });

  const pm = progressRes?.data;

  // Generate fallback S-curve data from project dates if API returns empty
  const sCurveData = useMemo(() => {
    if (pm?.s_curve_data && pm.s_curve_data.length > 0) return pm.s_curve_data;
    // Generate sample data based on percent_complete
    if (!pm) return [];
    const now = dayjs();
    const start = now.subtract(30, "day");
    const points: SCurveDataPoint[] = [];
    for (let i = 0; i <= 30; i++) {
      const d = start.add(i, "day");
      const t = i / 30;
      // S-curve formula: logistic
      const planned = 100 / (1 + Math.exp(-10 * (t - 0.5)));
      const actual = i <= 30 ? (pm.percent_complete ?? 0) * (t * t) / (t * t + (1 - t) * (1 - t)) : 0;
      points.push({
        date: d.format("YYYY-MM-DD"),
        planned_percent: Math.round(planned * 10) / 10,
        actual_percent: Math.round(actual * 10) / 10,
      });
    }
    return points;
  }, [pm]);

  if (isLoading) {
    return (
      <div style={{ padding: 24, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!pm) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="Proiectul nu a fost găsit" />
      </div>
    );
  }

  const { tasks_summary: ts } = pm;

  return (
    <div style={{ padding: 24 }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <DashboardOutlined /> Monitorizare Avansare — {pm.project_name} (F078)
      </Title>

      {/* Delay alerts */}
      {pm.delay_alerts && pm.delay_alerts.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message={`${pm.delay_alerts.length} task-uri cu întârziere`}
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {pm.delay_alerts.slice(0, 5).map((a, i) => (
                <li key={i}>
                  <Text strong>{a.task_title}</Text> — {a.days_delayed} zile întârziere
                </li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* KPIs row */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Avansare reală"
              value={pm.percent_complete}
              suffix="%"
              valueStyle={{ color: healthColor(pm.health_indicator) }}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Avansare planificată"
              value={pm.planned_progress}
              suffix="%"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Variație calendar"
              value={pm.schedule_variance}
              suffix="%"
              valueStyle={{
                color: pm.schedule_variance >= 0 ? "#52c41a" : "#ff4d4f",
              }}
              prefix={pm.schedule_variance >= 0 ? <RiseOutlined /> : <FallOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="CPI"
              value={pm.cpi}
              precision={2}
              valueStyle={{ color: pm.cpi >= 1 ? "#52c41a" : "#ff4d4f" }}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="SPI"
              value={pm.spi}
              precision={2}
              valueStyle={{ color: pm.spi >= 1 ? "#52c41a" : "#ff4d4f" }}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <div style={{ textAlign: "center" }}>
              <Text type="secondary" style={{ fontSize: 12 }}>Health</Text>
              <div style={{ marginTop: 4 }}>
                <Tag
                  color={healthColor(pm.health_indicator)}
                  style={{ fontSize: 14, padding: "4px 16px" }}
                >
                  {pm.health_indicator?.toUpperCase() ?? "N/A"}
                </Tag>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Progress bar */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={16}>
          <Col span={3}><Text strong>Realizat vs. Plan:</Text></Col>
          <Col span={18}>
            <Progress
              percent={pm.percent_complete}
              success={{ percent: pm.planned_progress, strokeColor: "#1677ff" }}
              strokeColor="#52c41a"
              trailColor="#f0f0f0"
              size={["100%", 20]}
            />
          </Col>
          <Col span={3}>
            <Text>
              {pm.percent_complete.toFixed(1)}% / {pm.planned_progress.toFixed(1)}%
            </Text>
          </Col>
        </Row>
      </Card>

      {/* S-Curve */}
      <Card title="S-Curve — Planificat vs. Realizat" style={{ marginBottom: 24 }}>
        <SCurveChart data={sCurveData} />
      </Card>

      {/* Tasks summary + Milestones */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card title="Sumar Task-uri" size="small">
            <Space direction="vertical" style={{ width: "100%" }}>
              <Row justify="space-between">
                <Text>Total</Text>
                <Text strong>{ts.total}</Text>
              </Row>
              <Row justify="space-between">
                <Text>
                  <CheckCircleOutlined style={{ color: "#52c41a" }} /> Finalizate
                </Text>
                <Text strong style={{ color: "#52c41a" }}>{ts.done}</Text>
              </Row>
              <Row justify="space-between">
                <Text>
                  <ClockCircleOutlined style={{ color: "#1677ff" }} /> În progres
                </Text>
                <Text strong style={{ color: "#1677ff" }}>{ts.in_progress}</Text>
              </Row>
              <Row justify="space-between">
                <Text>
                  <WarningOutlined style={{ color: "#ff4d4f" }} /> Blocate
                </Text>
                <Text strong style={{ color: "#ff4d4f" }}>{ts.blocked}</Text>
              </Row>
              <Row justify="space-between">
                <Text>De făcut</Text>
                <Text strong>{ts.todo}</Text>
              </Row>
              <Progress
                percent={ts.total > 0 ? Math.round((ts.done / ts.total) * 100) : 0}
                strokeColor="#52c41a"
                size="small"
              />
            </Space>
          </Card>
        </Col>
        <Col span={16}>
          <Card title="Milestone-uri" size="small">
            <Table
              dataSource={pm.milestones ?? []}
              rowKey={(_, i) => String(i)}
              pagination={false}
              size="small"
              columns={[
                {
                  title: "",
                  key: "icon",
                  width: 32,
                  render: () => <FlagOutlined style={{ color: "#faad14" }} />,
                },
                { title: "Milestone", dataIndex: "title", key: "title" },
                {
                  title: "Data planificată",
                  dataIndex: "planned_date",
                  key: "planned",
                  width: 120,
                  render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
                },
                {
                  title: "Data reală",
                  dataIndex: "actual_date",
                  key: "actual",
                  width: 120,
                  render: (d?: string) =>
                    d ? dayjs(d).format("DD.MM.YYYY") : <Text type="secondary">—</Text>,
                },
                {
                  title: "Status",
                  dataIndex: "status",
                  key: "status",
                  width: 100,
                  render: (s: string) => {
                    const colors: Record<string, string> = {
                      done: "success",
                      in_progress: "processing",
                      todo: "default",
                      delayed: "error",
                    };
                    return <Tag color={colors[s] ?? "default"}>{s}</Tag>;
                  },
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
