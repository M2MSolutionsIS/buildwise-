/**
 * Budget Control / EVM — F080
 * Buget alocat vs costuri angajate vs realizate.
 * CPI, SPI, EAC, ETC, VAC indicators.
 * Varianțe per capitol WBS / categorie.
 *
 * Canvas bar chart for budget breakdown by category.
 */
import { useRef, useEffect, useCallback, useMemo } from "react";
import {
  Card,
  Statistic,
  Row,
  Col,
  Table,
  Tag,
  Typography,
  Progress,
  Alert,
  Space,
  Spin,
  Empty,
  Descriptions,
} from "antd";
import {
  DollarOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  FundOutlined,
  RiseOutlined,
  FallOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { BudgetControl, BudgetCategory } from "../../../types";

const { Title, Text } = Typography;

// ─── Budget Bar Chart ────────────────────────────────────────────────────────

function BudgetBarChart({ categories }: { categories: BudgetCategory[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || categories.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const PAD = { top: 30, right: 20, bottom: 60, left: 80 };
    const chartW = W - PAD.left - PAD.right;
    const chartH = H - PAD.top - PAD.bottom;

    ctx.clearRect(0, 0, W, H);

    const maxVal = Math.max(
      ...categories.flatMap((c) => [c.allocated, c.committed, c.actual])
    );
    if (maxVal === 0) return;

    const barGroupW = chartW / categories.length;
    const barW = Math.min(barGroupW * 0.22, 30);
    const gap = 3;

    // Grid
    ctx.strokeStyle = "#f0f0f0";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = PAD.top + (chartH / 5) * i;
      ctx.beginPath();
      ctx.moveTo(PAD.left, y);
      ctx.lineTo(PAD.left + chartW, y);
      ctx.stroke();

      const val = maxVal - (maxVal / 5) * i;
      ctx.fillStyle = "#666";
      ctx.font = "10px -apple-system, sans-serif";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      ctx.fillText(`${(val / 1000).toFixed(0)}k`, PAD.left - 8, y);
    }

    // Bars
    const colors = ["#1677ff", "#faad14", "#52c41a"]; // allocated, committed, actual
    categories.forEach((cat, idx) => {
      const cx = PAD.left + barGroupW * idx + barGroupW / 2;
      const vals = [cat.allocated, cat.committed, cat.actual];

      vals.forEach((val, bIdx) => {
        const bh = (val / maxVal) * chartH;
        const x = cx - (1.5 * barW + gap) + bIdx * (barW + gap);
        const y = PAD.top + chartH - bh;

        ctx.fillStyle = colors[bIdx] ?? "#999";
        ctx.fillRect(x, y, barW, bh);
      });

      // Category label
      ctx.fillStyle = "#333";
      ctx.font = "11px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      const label = cat.category.length > 12
        ? cat.category.slice(0, 12) + "…"
        : cat.category;
      ctx.fillText(label, cx, PAD.top + chartH + 8);
    });

    // Legend
    const legendLabels = ["Alocat", "Angajat", "Realizat"];
    let legendX = PAD.left;
    const legendY = PAD.top + chartH + 35;
    legendLabels.forEach((label, i) => {
      ctx.fillStyle = colors[i] ?? "#999";
      ctx.fillRect(legendX, legendY - 5, 12, 12);
      ctx.fillStyle = "#333";
      ctx.font = "11px -apple-system, sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(label, legendX + 16, legendY + 5);
      legendX += 90;
    });

    // Title
    ctx.fillStyle = "#333";
    ctx.font = "bold 13px -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Buget per Categorie (RON)", W / 2, 16);
  }, [categories]);

  useEffect(() => {
    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  if (categories.length === 0) {
    return <Empty description="Nu există date bugetare" />;
  }

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: 320, display: "block" }}
    />
  );
}

// ─── EVM indicator helper ────────────────────────────────────────────────────

function evmColor(val: number, threshold = 1): string {
  if (val >= threshold) return "#52c41a";
  if (val >= threshold * 0.9) return "#faad14";
  return "#ff4d4f";
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function BudgetControlPage() {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: budgetRes, isLoading } = useQuery({
    queryKey: ["budget-control", projectId],
    queryFn: () => pmService.getBudgetControl(projectId!),
    enabled: !!projectId,
  });

  const bc = budgetRes?.data;

  const budgetUsedPct = useMemo(
    () =>
      bc && bc.budget_allocated > 0
        ? (bc.budget_actual / bc.budget_allocated) * 100
        : 0,
    [bc]
  );

  if (isLoading) {
    return (
      <div style={{ padding: 24, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!bc) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="Date bugetare indisponibile" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <FundOutlined /> Control Buget — Earned Value Management (F080)
      </Title>

      {/* Alerts */}
      {bc.alerts && bc.alerts.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message="Alerte bugetare"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {bc.alerts.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Budget overview */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Buget alocat"
              value={bc.budget_allocated}
              suffix={bc.currency}
              prefix={<DollarOutlined />}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Costuri angajate"
              value={bc.budget_committed}
              suffix={bc.currency}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Costuri realizate"
              value={bc.budget_actual}
              suffix={bc.currency}
              precision={0}
              valueStyle={
                bc.budget_actual > bc.budget_allocated
                  ? { color: "#ff4d4f" }
                  : undefined
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>Utilizare buget</Text>
              <Progress
                percent={Math.min(budgetUsedPct, 100)}
                strokeColor={
                  budgetUsedPct > 100
                    ? "#ff4d4f"
                    : budgetUsedPct > 90
                    ? "#faad14"
                    : "#52c41a"
                }
                format={() => `${budgetUsedPct.toFixed(0)}%`}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* EVM Indicators */}
      <Card
        title="Indicatori EVM (Earned Value Management)"
        style={{ marginBottom: 24 }}
      >
        <Row gutter={[16, 16]}>
          <Col span={4}>
            <Statistic
              title="CPI"
              value={bc.cpi}
              precision={2}
              valueStyle={{ color: evmColor(bc.cpi) }}
              prefix={bc.cpi >= 1 ? <RiseOutlined /> : <FallOutlined />}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Cost Performance Index
            </Text>
          </Col>
          <Col span={4}>
            <Statistic
              title="SPI"
              value={bc.spi}
              precision={2}
              valueStyle={{ color: evmColor(bc.spi) }}
              prefix={bc.spi >= 1 ? <RiseOutlined /> : <FallOutlined />}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Schedule Performance Index
            </Text>
          </Col>
          <Col span={4}>
            <Statistic
              title="EV"
              value={bc.ev}
              suffix={bc.currency}
              precision={0}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Earned Value
            </Text>
          </Col>
          <Col span={4}>
            <Statistic
              title="PV"
              value={bc.pv}
              suffix={bc.currency}
              precision={0}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Planned Value
            </Text>
          </Col>
          <Col span={4}>
            <Statistic
              title="AC"
              value={bc.ac}
              suffix={bc.currency}
              precision={0}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Actual Cost
            </Text>
          </Col>
          <Col span={4}>
            <Statistic
              title="EAC"
              value={bc.eac}
              suffix={bc.currency}
              precision={0}
              valueStyle={
                bc.eac > bc.budget_allocated ? { color: "#ff4d4f" } : undefined
              }
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              Estimate at Completion
            </Text>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={6}>
            <Descriptions size="small" column={1} bordered>
              <Descriptions.Item label="SV (Schedule Variance)">
                <Text style={{ color: bc.sv >= 0 ? "#52c41a" : "#ff4d4f" }}>
                  {bc.sv >= 0 ? "+" : ""}{bc.sv.toLocaleString("ro-RO")} {bc.currency}
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label="CV (Cost Variance)">
                <Text style={{ color: bc.cv >= 0 ? "#52c41a" : "#ff4d4f" }}>
                  {bc.cv >= 0 ? "+" : ""}{bc.cv.toLocaleString("ro-RO")} {bc.currency}
                </Text>
              </Descriptions.Item>
            </Descriptions>
          </Col>
          <Col span={6}>
            <Descriptions size="small" column={1} bordered>
              <Descriptions.Item label="ETC (Estimate to Complete)">
                {bc.etc.toLocaleString("ro-RO")} {bc.currency}
              </Descriptions.Item>
              <Descriptions.Item label="VAC (Variance at Completion)">
                <Text style={{ color: bc.vac >= 0 ? "#52c41a" : "#ff4d4f" }}>
                  {bc.vac >= 0 ? "+" : ""}{bc.vac.toLocaleString("ro-RO")} {bc.currency}
                </Text>
              </Descriptions.Item>
            </Descriptions>
          </Col>
          <Col span={12}>
            <Card size="small" title="Interpretare">
              <Space direction="vertical" size={4}>
                <Text>
                  <Tag color={evmColor(bc.cpi)}>CPI = {bc.cpi.toFixed(2)}</Tag>
                  {bc.cpi >= 1
                    ? "Proiectul este sub buget (eficient)"
                    : "Proiectul depășește bugetul (ineficient)"}
                </Text>
                <Text>
                  <Tag color={evmColor(bc.spi)}>SPI = {bc.spi.toFixed(2)}</Tag>
                  {bc.spi >= 1
                    ? "Proiectul este în avans sau la timp"
                    : "Proiectul este în întârziere"}
                </Text>
                <Text>
                  {bc.eac <= bc.budget_allocated ? (
                    <Tag color="success" icon={<CheckCircleOutlined />}>
                      Proiectul va fi sub buget
                    </Tag>
                  ) : (
                    <Tag color="error" icon={<WarningOutlined />}>
                      Depășire estimată: {(bc.eac - bc.budget_allocated).toLocaleString("ro-RO")} {bc.currency}
                    </Tag>
                  )}
                </Text>
              </Space>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Budget by category chart */}
      <Card
        title="Buget per Categorie"
        style={{ marginBottom: 24 }}
      >
        <BudgetBarChart categories={bc.by_category} />
      </Card>

      {/* Category detail table */}
      <Card title="Detaliu Varianțe per Categorie">
        <Table
          dataSource={bc.by_category}
          rowKey="category"
          pagination={false}
          size="middle"
          columns={[
            {
              title: "Categorie",
              dataIndex: "category",
              key: "cat",
              render: (v: string) => <Text strong>{v}</Text>,
            },
            {
              title: "Alocat",
              dataIndex: "allocated",
              key: "alloc",
              align: "right" as const,
              render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
            },
            {
              title: "Angajat",
              dataIndex: "committed",
              key: "commit",
              align: "right" as const,
              render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
            },
            {
              title: "Realizat",
              dataIndex: "actual",
              key: "actual",
              align: "right" as const,
              render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
            },
            {
              title: "Varianță",
              dataIndex: "variance",
              key: "var",
              align: "right" as const,
              render: (v: number) => (
                <Text style={{ color: v >= 0 ? "#52c41a" : "#ff4d4f" }}>
                  {v >= 0 ? "+" : ""}{v.toLocaleString("ro-RO")} RON
                </Text>
              ),
            },
            {
              title: "Varianță %",
              dataIndex: "variance_pct",
              key: "var_pct",
              width: 120,
              render: (v: number) => (
                <Tag color={v >= 0 ? "success" : v > -10 ? "warning" : "error"}>
                  {v >= 0 ? "+" : ""}{v.toFixed(1)}%
                </Tag>
              ),
            },
            {
              title: "Utilizare",
              key: "usage",
              width: 140,
              render: (_: unknown, rec: BudgetCategory) => {
                const pct =
                  rec.allocated > 0
                    ? (rec.actual / rec.allocated) * 100
                    : 0;
                return (
                  <Progress
                    percent={Math.min(pct, 150)}
                    size="small"
                    strokeColor={
                      pct > 100 ? "#ff4d4f" : pct > 90 ? "#faad14" : "#52c41a"
                    }
                    format={() => `${pct.toFixed(0)}%`}
                  />
                );
              },
            },
          ]}
          summary={() => {
            const totAlloc = bc.by_category.reduce((s, c) => s + c.allocated, 0);
            const totCommit = bc.by_category.reduce((s, c) => s + c.committed, 0);
            const totActual = bc.by_category.reduce((s, c) => s + c.actual, 0);
            const totVar = bc.by_category.reduce((s, c) => s + c.variance, 0);
            return (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0}>
                  <Text strong>TOTAL</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={1} align="right">
                  <Text strong>{totAlloc.toLocaleString("ro-RO")} RON</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={2} align="right">
                  <Text strong>{totCommit.toLocaleString("ro-RO")} RON</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={3} align="right">
                  <Text strong>{totActual.toLocaleString("ro-RO")} RON</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={4} align="right">
                  <Text
                    strong
                    style={{ color: totVar >= 0 ? "#52c41a" : "#ff4d4f" }}
                  >
                    {totVar >= 0 ? "+" : ""}{totVar.toLocaleString("ro-RO")} RON
                  </Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={5} />
                <Table.Summary.Cell index={6} />
              </Table.Summary.Row>
            );
          }}
        />
      </Card>
    </div>
  );
}
