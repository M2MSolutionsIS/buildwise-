/**
 * E-020: Project Reporting 3-in-1 — F080, F091, F092, F095, F142
 * Earned Value (EVM) + P&L + Cash Flow + TrueCast + Export PDF
 */
import { useMemo, useRef, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Button,
  Tabs,
  Tooltip,
  Alert,
  Space,
  Empty,
  Spin,
  message,
} from "antd";
import {
  FileExcelOutlined,
  FilePdfOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  DashboardOutlined,
  DollarOutlined,
  BankOutlined,
  LineChartOutlined,
} from "@ant-design/icons";
import type { ProjectFinanceEntry, ProjectCashFlowEntry } from "../../../types";
import { pmService } from "../services/pmService";

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

function fmtCurrency(v?: number | null, currency = "RON"): string {
  if (v == null) return "—";
  return new Intl.NumberFormat("ro-RO", { style: "currency", currency, maximumFractionDigits: 0 }).format(v);
}

function fmtPct(v?: number | null): string {
  if (v == null) return "—";
  return `${(v * 100).toFixed(1)}%`;
}

function evmColor(val?: number | null): string {
  if (val == null) return "#888";
  if (val >= 1) return "#52c41a";
  if (val >= 0.9) return "#faad14";
  return "#ff4d4f";
}

/* ─── S-Curve Canvas ──────────────────────────────────────────────────────── */

function SCurveChart({
  pv,
  ev,
  ac,
  budget,
}: {
  pv: number;
  ev: number;
  ac: number;
  budget: number;
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

    const pad = { top: 30, right: 20, bottom: 40, left: 60 };
    const cW = W - pad.left - pad.right;
    const cH = H - pad.top - pad.bottom;
    const maxVal = Math.max(budget, ac, pv, ev, 1);

    // Grid
    ctx.strokeStyle = "#f0f0f0";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = pad.top + (cH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(W - pad.right, y);
      ctx.stroke();
      ctx.fillStyle = "#999";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText(fmtCurrency(maxVal - (maxVal / 4) * i), pad.left - 8, y + 4);
    }

    // Labels
    const labels = ["Start", "Curent", "BAC"];
    labels.forEach((l, i) => {
      const x = pad.left + (cW / (labels.length - 1)) * i;
      ctx.fillStyle = "#666";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(l, x, H - 10);
    });

    // Draw bars
    const barWidth = cW * 0.15;
    const centerX = pad.left + cW / 2;

    const drawBar = (x: number, val: number, color: string, label: string) => {
      const h = (val / maxVal) * cH;
      const y = pad.top + cH - h;
      ctx.fillStyle = color;
      ctx.fillRect(x - barWidth / 2, y, barWidth, h);
      ctx.fillStyle = "#333";
      ctx.font = "bold 11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(label, x, y - 6);
    };

    drawBar(centerX - barWidth * 1.5, pv, "#1677ff", "PV");
    drawBar(centerX, ev, "#52c41a", "EV");
    drawBar(centerX + barWidth * 1.5, ac, "#ff4d4f", "AC");

    // BAC line
    const bacY = pad.top + cH - (budget / maxVal) * cH;
    ctx.strokeStyle = "#faad14";
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 3]);
    ctx.beginPath();
    ctx.moveTo(pad.left, bacY);
    ctx.lineTo(W - pad.right, bacY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#faad14";
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "right";
    ctx.fillText(`BAC: ${fmtCurrency(budget)}`, W - pad.right, bacY - 6);

    // Title
    ctx.fillStyle = "#333";
    ctx.font = "bold 13px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Earned Value — PV / EV / AC", W / 2, 18);
  }, [pv, ev, ac, budget]);

  return <canvas ref={canvasRef} width={600} height={320} style={{ width: "100%", height: 320 }} />;
}

/* ─── Main Component ──────────────────────────────────────────────────────── */

export default function ProjectReportPage() {
  const { projectId } = useParams<{ projectId: string }>();

  // F095: Aggregated report
  const { data: reportResp, isLoading: loadingReport } = useQuery({
    queryKey: ["pm", "project-report", projectId],
    queryFn: () => pmService.getProjectReport(projectId!),
    enabled: !!projectId,
  });

  // F091: P&L entries
  const { data: financeResp, isLoading: loadingFinance } = useQuery({
    queryKey: ["pm", "finance", projectId],
    queryFn: () => pmService.listFinanceEntries(projectId!),
    enabled: !!projectId,
  });

  // F092: Cash flow entries
  const { data: cashFlowResp, isLoading: loadingCF } = useQuery({
    queryKey: ["pm", "cash-flow", projectId],
    queryFn: () => pmService.listCashFlow(projectId!),
    enabled: !!projectId,
  });

  // F080: Budget control (for EVM)
  const { data: budgetResp, isLoading: loadingBudget } = useQuery({
    queryKey: ["pm", "budget-control", projectId],
    queryFn: () => pmService.getBudgetControl(projectId!),
    enabled: !!projectId,
  });

  const report = reportResp?.data;
  const budget = budgetResp?.data;
  const financeEntries = financeResp?.data ?? [];
  const cashFlowEntries = cashFlowResp?.data ?? [];

  const isLoading = loadingReport || loadingFinance || loadingCF || loadingBudget;

  /* ─── EVM Calculations ─────────────────────────────────────────────────── */

  const evm = useMemo(() => {
    if (!budget) return null;
    const BAC = budget.budget_allocated ?? 0;
    const EV = budget.ev ?? 0;
    const PV = budget.pv ?? 0;
    const AC = budget.ac ?? 0;
    const CPI = budget.cpi ?? (AC > 0 ? EV / AC : 0);
    const SPI = budget.spi ?? (PV > 0 ? EV / PV : 0);
    const EAC = CPI > 0 ? AC + (BAC - EV) / CPI : BAC;
    const ETC = EAC - AC;
    const VAC = BAC - EAC;
    return { BAC, EV, PV, AC, CPI, SPI, EAC, ETC, VAC };
  }, [budget]);

  /* ─── P&L Aggregation ──────────────────────────────────────────────────── */

  const pnl = useMemo(() => {
    const revenue: Record<string, { forecast: number; actual: number }> = {};
    const costs: Record<string, { forecast: number; actual: number }> = {};

    financeEntries.forEach((e: ProjectFinanceEntry) => {
      const bucket = e.entry_type === "revenue" ? revenue : costs;
      if (!bucket[e.category]) bucket[e.category] = { forecast: 0, actual: 0 };
      bucket[e.category]!.forecast += e.forecast_amount;
      bucket[e.category]!.actual += e.actual_amount;
    });

    const totalRevForecast = Object.values(revenue).reduce((s, v) => s + v.forecast, 0);
    const totalRevActual = Object.values(revenue).reduce((s, v) => s + v.actual, 0);
    const totalCostForecast = Object.values(costs).reduce((s, v) => s + v.forecast, 0);
    const totalCostActual = Object.values(costs).reduce((s, v) => s + v.actual, 0);

    return {
      revenue,
      costs,
      totalRevForecast,
      totalRevActual,
      totalCostForecast,
      totalCostActual,
      profitForecast: totalRevForecast - totalCostForecast,
      profitActual: totalRevActual - totalCostActual,
    };
  }, [financeEntries]);

  /* ─── Cash Flow by Month ───────────────────────────────────────────────── */

  const cashFlowTable = useMemo(() => {
    const months: Record<
      string,
      { inflow: number; outflow: number; net: number; cumulative: number }
    > = {};

    cashFlowEntries
      .sort(
        (a: ProjectCashFlowEntry, b: ProjectCashFlowEntry) =>
          new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime()
      )
      .forEach((e: ProjectCashFlowEntry) => {
        const d = new Date(e.transaction_date);
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
        if (!months[key]) months[key] = { inflow: 0, outflow: 0, net: 0, cumulative: 0 };
        if (e.entry_type === "inflow") {
          months[key].inflow += e.amount;
        } else {
          months[key].outflow += e.amount;
        }
      });

    let cum = 0;
    return Object.entries(months)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, v]) => {
        v.net = v.inflow - v.outflow;
        cum += v.net;
        return { month, ...v, cumulative: cum };
      });
  }, [cashFlowEntries]);

  /* ─── TrueCast ─────────────────────────────────────────────────────────── */

  const trueCast = useMemo(() => {
    if (!evm || !report) return null;
    const pctDone = report.percent_complete / 100;
    if (pctDone < 0.1) return null; // insufficient data

    const daysTotal =
      report.planned_start && report.planned_end
        ? (new Date(report.planned_end).getTime() - new Date(report.planned_start).getTime()) /
          86400000
        : null;

    const estimatedEndDate =
      daysTotal && report.planned_start && evm.SPI > 0
        ? new Date(
            new Date(report.planned_start).getTime() + (daysTotal / evm.SPI) * 86400000
          ).toLocaleDateString("ro-RO")
        : "—";

    return {
      estimatedEndDate,
      finalCost: evm.EAC,
      vac: evm.VAC,
      profitProjection: pnl.profitForecast + evm.VAC,
    };
  }, [evm, report, pnl]);

  /* ─── Export Handlers ──────────────────────────────────────────────────── */

  const handleExport = useCallback(
    async (format: "pdf" | "excel") => {
      if (!projectId) return;
      try {
        const blob = await pmService.exportProjectReport(projectId, format);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `raport-proiect-${projectId}.${format === "pdf" ? "pdf" : "xlsx"}`;
        a.click();
        URL.revokeObjectURL(url);
        message.success(`Export ${format.toUpperCase()} descărcat`);
      } catch {
        message.error("Eroare la export. Încercați din nou.");
      }
    },
    [projectId]
  );

  /* ─── Render ───────────────────────────────────────────────────────────── */

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!report) {
    return <Empty description="Raportul nu a putut fi încărcat" />;
  }

  const cpiAlert = evm && evm.CPI < 0.9;

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <h2 style={{ margin: 0 }}>
            Raport Proiect 3-in-1 — {report.project_name}
          </h2>
          <span style={{ color: "#888" }}>
            E-020 | F095 + F091 + F092 | Status: {report.status} | Progres:{" "}
            {report.percent_complete.toFixed(0)}%
          </span>
        </Col>
        <Col>
          <Space>
            <Button icon={<FilePdfOutlined />} onClick={() => handleExport("pdf")}>
              Export PDF
            </Button>
            <Button icon={<FileExcelOutlined />} onClick={() => handleExport("excel")}>
              Export Excel
            </Button>
          </Space>
        </Col>
      </Row>

      {/* CPI Alert Banner */}
      {cpiAlert && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message={`CPI = ${evm!.CPI.toFixed(2)} — Proiectul depășește bugetul cu ${((1 - evm!.CPI) * 100).toFixed(0)}%. Recomandare: revizuiți costurile.`}
          style={{ marginBottom: 16 }}
        />
      )}

      <Tabs
        defaultActiveKey="ev"
        items={[
          {
            key: "ev",
            label: (
              <span>
                <DashboardOutlined /> Earned Value
              </span>
            ),
            children: (
              <>
                {/* EVM KPI Cards */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col xs={12} sm={6}>
                    <Card size="small">
                      <Statistic
                        title={
                          <Tooltip title="Schedule Performance Index = EV / PV">
                            SPI
                          </Tooltip>
                        }
                        value={evm ? evm.SPI.toFixed(2) : "—"}
                        valueStyle={{ color: evmColor(evm?.SPI) }}
                        prefix={evm && evm.SPI >= 1 ? <CheckCircleOutlined /> : <WarningOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} sm={6}>
                    <Card size="small">
                      <Statistic
                        title={
                          <Tooltip title="Cost Performance Index = EV / AC">
                            CPI
                          </Tooltip>
                        }
                        value={evm ? evm.CPI.toFixed(2) : "—"}
                        valueStyle={{ color: evmColor(evm?.CPI) }}
                        prefix={evm && evm.CPI >= 1 ? <CheckCircleOutlined /> : <WarningOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} sm={6}>
                    <Card size="small">
                      <Statistic
                        title={<Tooltip title="Earned Value">EV</Tooltip>}
                        value={fmtCurrency(evm?.EV)}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} sm={6}>
                    <Card size="small">
                      <Statistic
                        title={
                          <Tooltip title="Estimate At Completion = AC + (BAC - EV) / CPI">
                            EAC
                          </Tooltip>
                        }
                        value={fmtCurrency(evm?.EAC)}
                        valueStyle={{
                          color: evm && evm.EAC > evm.BAC ? "#ff4d4f" : "#52c41a",
                        }}
                      />
                    </Card>
                  </Col>
                </Row>

                {/* S-Curve Chart */}
                <Card size="small" title="Grafic EVM">
                  {evm ? (
                    <SCurveChart
                      pv={evm.PV}
                      ev={evm.EV}
                      ac={evm.AC}
                      budget={evm.BAC}
                    />
                  ) : (
                    <Empty description="Date EVM insuficiente" />
                  )}
                </Card>
              </>
            ),
          },
          {
            key: "pnl",
            label: (
              <span>
                <DollarOutlined /> P&L
              </span>
            ),
            children: (
              <Card size="small" title="Profit & Loss (F091)">
                <h4>Venituri</h4>
                <Table
                  size="small"
                  pagination={false}
                  dataSource={Object.entries(pnl.revenue).map(([cat, v]) => ({
                    key: cat,
                    category: cat,
                    ...v,
                    variance: v.actual - v.forecast,
                  }))}
                  columns={[
                    { title: "Categorie", dataIndex: "category" },
                    {
                      title: "Buget",
                      dataIndex: "forecast",
                      render: (v: number) => fmtCurrency(v),
                      align: "right" as const,
                    },
                    {
                      title: "Realizat",
                      dataIndex: "actual",
                      render: (v: number) => fmtCurrency(v),
                      align: "right" as const,
                    },
                    {
                      title: "Varianță",
                      dataIndex: "variance",
                      render: (v: number) => (
                        <span style={{ color: v >= 0 ? "#52c41a" : "#ff4d4f" }}>
                          {fmtCurrency(v)}
                        </span>
                      ),
                      align: "right" as const,
                    },
                  ]}
                  summary={() => (
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0}>
                        <strong>Total Venituri</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={1} align="right">
                        <strong>{fmtCurrency(pnl.totalRevForecast)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={2} align="right">
                        <strong>{fmtCurrency(pnl.totalRevActual)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={3} align="right">
                        <strong
                          style={{
                            color:
                              pnl.totalRevActual - pnl.totalRevForecast >= 0
                                ? "#52c41a"
                                : "#ff4d4f",
                          }}
                        >
                          {fmtCurrency(pnl.totalRevActual - pnl.totalRevForecast)}
                        </strong>
                      </Table.Summary.Cell>
                    </Table.Summary.Row>
                  )}
                />

                <h4 style={{ marginTop: 24 }}>Costuri</h4>
                <Table
                  size="small"
                  pagination={false}
                  dataSource={Object.entries(pnl.costs).map(([cat, v]) => ({
                    key: cat,
                    category: cat,
                    ...v,
                    variance: v.actual - v.forecast,
                  }))}
                  columns={[
                    { title: "Categorie", dataIndex: "category" },
                    {
                      title: "Buget",
                      dataIndex: "forecast",
                      render: (v: number) => fmtCurrency(v),
                      align: "right" as const,
                    },
                    {
                      title: "Realizat",
                      dataIndex: "actual",
                      render: (v: number) => fmtCurrency(v),
                      align: "right" as const,
                    },
                    {
                      title: "Varianță",
                      dataIndex: "variance",
                      render: (v: number) => (
                        <span style={{ color: v <= 0 ? "#52c41a" : "#ff4d4f" }}>
                          {fmtCurrency(v)}
                        </span>
                      ),
                      align: "right" as const,
                    },
                  ]}
                  summary={() => (
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0}>
                        <strong>Total Costuri</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={1} align="right">
                        <strong>{fmtCurrency(pnl.totalCostForecast)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={2} align="right">
                        <strong>{fmtCurrency(pnl.totalCostActual)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={3} align="right">
                        <strong
                          style={{
                            color:
                              pnl.totalCostActual - pnl.totalCostForecast <= 0
                                ? "#52c41a"
                                : "#ff4d4f",
                          }}
                        >
                          {fmtCurrency(pnl.totalCostActual - pnl.totalCostForecast)}
                        </strong>
                      </Table.Summary.Cell>
                    </Table.Summary.Row>
                  )}
                />

                {/* Profit Summary */}
                <Row gutter={16} style={{ marginTop: 24 }}>
                  <Col span={8}>
                    <Card size="small">
                      <Statistic
                        title="Profit Bugetat"
                        value={pnl.profitForecast}
                        precision={0}
                        suffix="RON"
                        valueStyle={{
                          color: pnl.profitForecast >= 0 ? "#52c41a" : "#ff4d4f",
                        }}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card size="small">
                      <Statistic
                        title="Profit Realizat"
                        value={pnl.profitActual}
                        precision={0}
                        suffix="RON"
                        valueStyle={{
                          color: pnl.profitActual >= 0 ? "#52c41a" : "#ff4d4f",
                        }}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card size="small">
                      <Statistic
                        title="Marjă Profit"
                        value={
                          pnl.totalRevActual > 0
                            ? ((pnl.profitActual / pnl.totalRevActual) * 100).toFixed(1)
                            : "—"
                        }
                        suffix="%"
                      />
                    </Card>
                  </Col>
                </Row>
              </Card>
            ),
          },
          {
            key: "cf",
            label: (
              <span>
                <BankOutlined /> Cash Flow
              </span>
            ),
            children: (
              <Card size="small" title="Cash Flow Lunar (F092)">
                {cashFlowTable.length > 0 ? (
                  <Table
                    size="small"
                    pagination={false}
                    dataSource={cashFlowTable.map((row) => ({
                      ...row,
                      key: row.month,
                    }))}
                    columns={[
                      { title: "Lună", dataIndex: "month", width: 120 },
                      {
                        title: "Încasări",
                        dataIndex: "inflow",
                        render: (v: number) => (
                          <span style={{ color: "#52c41a" }}>{fmtCurrency(v)}</span>
                        ),
                        align: "right" as const,
                      },
                      {
                        title: "Plăți",
                        dataIndex: "outflow",
                        render: (v: number) => (
                          <span style={{ color: "#ff4d4f" }}>{fmtCurrency(v)}</span>
                        ),
                        align: "right" as const,
                      },
                      {
                        title: "Net",
                        dataIndex: "net",
                        render: (v: number) => (
                          <span style={{ color: v >= 0 ? "#52c41a" : "#ff4d4f", fontWeight: 600 }}>
                            {fmtCurrency(v)}
                          </span>
                        ),
                        align: "right" as const,
                      },
                      {
                        title: "Cumulat",
                        dataIndex: "cumulative",
                        render: (v: number) => (
                          <Tag color={v >= 0 ? "green" : "red"}>{fmtCurrency(v)}</Tag>
                        ),
                        align: "right" as const,
                      },
                    ]}
                  />
                ) : (
                  <Empty description="Nicio înregistrare Cash Flow" />
                )}
              </Card>
            ),
          },
          {
            key: "truecast",
            label: (
              <span>
                <LineChartOutlined /> TrueCast
              </span>
            ),
            children: (
              <Card size="small" title="Proiecție la Finalizare (TrueCast)">
                {trueCast ? (
                  <Row gutter={16}>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="Data Estimată Finalizare"
                        value={trueCast.estimatedEndDate}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="Cost Final Proiectat (EAC)"
                        value={fmtCurrency(trueCast.finalCost)}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="VAC (Variance at Completion)"
                        value={fmtCurrency(trueCast.vac)}
                        valueStyle={{
                          color: trueCast.vac >= 0 ? "#52c41a" : "#ff4d4f",
                        }}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="Profit Proiectat"
                        value={fmtCurrency(trueCast.profitProjection)}
                        valueStyle={{
                          color: trueCast.profitProjection >= 0 ? "#52c41a" : "#ff4d4f",
                        }}
                      />
                    </Col>
                  </Row>
                ) : (
                  <Alert
                    type="info"
                    message="Date insuficiente"
                    description="Proiectul este prea nou pentru a genera proiecții fiabile. Este necesar un progres de minim 10%."
                  />
                )}
              </Card>
            ),
          },
        ]}
      />

      {/* Summary footer */}
      <Card size="small" style={{ marginTop: 16 }}>
        <Row gutter={16}>
          <Col span={4}>
            <Statistic title="Task-uri Total" value={report.total_tasks} />
          </Col>
          <Col span={4}>
            <Statistic title="Finalizate" value={report.completed_tasks} valueStyle={{ color: "#52c41a" }} />
          </Col>
          <Col span={4}>
            <Statistic
              title="Riscuri Deschise"
              value={report.open_risks}
              valueStyle={{ color: report.open_risks > 0 ? "#faad14" : "#52c41a" }}
            />
          </Col>
          <Col span={4}>
            <Statistic
              title="Defecte Deschise"
              value={report.open_punch_items}
              valueStyle={{ color: report.open_punch_items > 0 ? "#ff4d4f" : "#52c41a" }}
            />
          </Col>
          <Col span={4}>
            <Statistic title="SPI" value={fmtPct(report.spi)} />
          </Col>
          <Col span={4}>
            <Statistic title="CPI" value={fmtPct(report.cpi)} />
          </Col>
        </Row>
      </Card>
    </div>
  );
}
