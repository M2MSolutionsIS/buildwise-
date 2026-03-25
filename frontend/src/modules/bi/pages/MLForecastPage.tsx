/**
 * F135: Previziuni Predictive — ML Forecast Placeholder (P3)
 * Placeholder until TRL7. Shows forecast UI with simulated data.
 * Real ML integration will come from Functionalitati_TRL7.md.
 */
import { useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Select,
  Tag,
  Space,
  Statistic,
  Alert,
  Divider,
  Progress,
  Table,
  Segmented,
} from "antd";
import {
  ExperimentOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined,
  BarChartOutlined,
  TableOutlined,
  CalendarOutlined,
} from "@ant-design/icons";
import type { MLForecastResult } from "../../../types";

const { Title, Text } = Typography;

// ─── Simulated forecast data ─────────────────────────────────────────────────

const FORECAST_MODULES = [
  { value: "revenue", label: "Venituri" },
  { value: "pipeline", label: "Pipeline Conversion" },
  { value: "projects", label: "Finalizare Proiecte" },
  { value: "costs", label: "Costuri Operaționale" },
  { value: "energy", label: "Eficiență Energetică" },
];

const PERIOD_OPTIONS = [
  { value: "3m", label: "3 luni" },
  { value: "6m", label: "6 luni" },
  { value: "12m", label: "12 luni" },
];

const SIMULATED_DATA: Record<string, { summary: { value: number; delta: number; unit: string; confidence: number }; forecast: MLForecastResult[] }> = {
  revenue: {
    summary: { value: 2450000, delta: 15.3, unit: "RON", confidence: 82 },
    forecast: [
      { period: "Ian 2026", predicted_value: 380, confidence_lower: 340, confidence_upper: 420, actual_value: 395 },
      { period: "Feb 2026", predicted_value: 420, confidence_lower: 370, confidence_upper: 470, actual_value: 410 },
      { period: "Mar 2026", predicted_value: 455, confidence_lower: 400, confidence_upper: 510, actual_value: 460 },
      { period: "Apr 2026", predicted_value: 490, confidence_lower: 420, confidence_upper: 560 },
      { period: "Mai 2026", predicted_value: 520, confidence_lower: 440, confidence_upper: 600 },
      { period: "Iun 2026", predicted_value: 550, confidence_lower: 460, confidence_upper: 640 },
    ],
  },
  pipeline: {
    summary: { value: 34, delta: 5.2, unit: "%", confidence: 76 },
    forecast: [
      { period: "Ian 2026", predicted_value: 28, confidence_lower: 22, confidence_upper: 34, actual_value: 30 },
      { period: "Feb 2026", predicted_value: 31, confidence_lower: 24, confidence_upper: 38, actual_value: 29 },
      { period: "Mar 2026", predicted_value: 33, confidence_lower: 26, confidence_upper: 40, actual_value: 34 },
      { period: "Apr 2026", predicted_value: 36, confidence_lower: 28, confidence_upper: 44 },
      { period: "Mai 2026", predicted_value: 38, confidence_lower: 29, confidence_upper: 47 },
      { period: "Iun 2026", predicted_value: 41, confidence_lower: 31, confidence_upper: 51 },
    ],
  },
  projects: {
    summary: { value: 87, delta: 8.1, unit: "%", confidence: 85 },
    forecast: [
      { period: "Ian 2026", predicted_value: 78, confidence_lower: 70, confidence_upper: 86, actual_value: 80 },
      { period: "Feb 2026", predicted_value: 82, confidence_lower: 73, confidence_upper: 91, actual_value: 85 },
      { period: "Mar 2026", predicted_value: 85, confidence_lower: 76, confidence_upper: 94, actual_value: 87 },
      { period: "Apr 2026", predicted_value: 88, confidence_lower: 78, confidence_upper: 98 },
      { period: "Mai 2026", predicted_value: 90, confidence_lower: 80, confidence_upper: 100 },
      { period: "Iun 2026", predicted_value: 92, confidence_lower: 82, confidence_upper: 100 },
    ],
  },
  costs: {
    summary: { value: 890000, delta: -3.4, unit: "RON", confidence: 79 },
    forecast: [
      { period: "Ian 2026", predicted_value: 145, confidence_lower: 130, confidence_upper: 160, actual_value: 148 },
      { period: "Feb 2026", predicted_value: 150, confidence_lower: 133, confidence_upper: 167, actual_value: 142 },
      { period: "Mar 2026", predicted_value: 148, confidence_lower: 130, confidence_upper: 166, actual_value: 147 },
      { period: "Apr 2026", predicted_value: 145, confidence_lower: 126, confidence_upper: 164 },
      { period: "Mai 2026", predicted_value: 142, confidence_lower: 122, confidence_upper: 162 },
      { period: "Iun 2026", predicted_value: 140, confidence_lower: 118, confidence_upper: 162 },
    ],
  },
  energy: {
    summary: { value: 0.3, delta: 12.0, unit: "W/m²K", confidence: 88 },
    forecast: [
      { period: "Ian 2026", predicted_value: 0.35, confidence_lower: 0.30, confidence_upper: 0.40, actual_value: 0.34 },
      { period: "Feb 2026", predicted_value: 0.33, confidence_lower: 0.28, confidence_upper: 0.38, actual_value: 0.32 },
      { period: "Mar 2026", predicted_value: 0.31, confidence_lower: 0.26, confidence_upper: 0.36, actual_value: 0.30 },
      { period: "Apr 2026", predicted_value: 0.29, confidence_lower: 0.24, confidence_upper: 0.34 },
      { period: "Mai 2026", predicted_value: 0.28, confidence_lower: 0.23, confidence_upper: 0.33 },
      { period: "Iun 2026", predicted_value: 0.27, confidence_lower: 0.22, confidence_upper: 0.32 },
    ],
  },
};

// ─── SVG Line Chart ──────────────────────────────────────────────────────────

function ForecastChart({ data, unit }: { data: MLForecastResult[]; unit: string }) {
  const w = 500;
  const h = 200;
  const pad = 40;

  const allValues = data.flatMap((d) => [d.confidence_lower, d.confidence_upper, d.predicted_value, d.actual_value ?? d.predicted_value]);
  const minV = Math.min(...allValues) * 0.9;
  const maxV = Math.max(...allValues) * 1.1;
  const range = maxV - minV || 1;

  const xStep = (w - pad * 2) / (data.length - 1);
  const toY = (v: number) => h - pad - ((v - minV) / range) * (h - pad * 2);
  const toX = (i: number) => pad + i * xStep;

  // Confidence band polygon
  const bandPoints = data.map((d, i) => `${toX(i)},${toY(d.confidence_upper)}`)
    .concat(data.map((_, i) => `${toX(data.length - 1 - i)},${toY(data[data.length - 1 - i]!.confidence_lower)}`))
    .join(" ");

  // Predicted line
  const predLine = data.map((d, i) => `${toX(i)},${toY(d.predicted_value)}`).join(" ");

  // Actual line (where available)
  const actualData = data.filter((d) => d.actual_value != null);
  const actualLine = actualData.map((d) => {
    const idx = data.indexOf(d);
    return `${toX(idx)},${toY(d.actual_value!)}`;
  }).join(" ");

  // First forecasted index (where actual is missing)
  const firstForecastIdx = data.findIndex((d) => d.actual_value == null);

  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h + 20}`} style={{ display: "block" }}>
      {/* Confidence band */}
      <polygon fill="#1677ff" opacity={0.1} points={bandPoints} />

      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((p) => {
        const y = h - pad - p * (h - pad * 2);
        const val = (minV + p * range).toFixed(unit === "%" || unit === "W/m²K" ? 1 : 0);
        return (
          <g key={p}>
            <line x1={pad} y1={y} x2={w - pad} y2={y} stroke="#f0f0f0" />
            <text x={pad - 5} y={y + 4} fontSize={9} textAnchor="end" fill="#999">{val}</text>
          </g>
        );
      })}

      {/* Divider line between actual and forecast */}
      {firstForecastIdx > 0 && (
        <line
          x1={toX(firstForecastIdx - 0.5)}
          y1={pad}
          x2={toX(firstForecastIdx - 0.5)}
          y2={h - pad}
          stroke="#d9d9d9"
          strokeDasharray="4,4"
        />
      )}

      {/* Predicted line */}
      <polyline fill="none" stroke="#1677ff" strokeWidth={2} points={predLine} strokeDasharray={firstForecastIdx > 0 ? undefined : "6,3"} />

      {/* Actual line */}
      {actualLine && <polyline fill="none" stroke="#52c41a" strokeWidth={2} points={actualLine} />}

      {/* Data points */}
      {data.map((d, i) => (
        <g key={i}>
          <circle cx={toX(i)} cy={toY(d.predicted_value)} r={3} fill="#1677ff" />
          {d.actual_value != null && (
            <circle cx={toX(i)} cy={toY(d.actual_value)} r={3} fill="#52c41a" />
          )}
          <text x={toX(i)} y={h - 10} fontSize={9} textAnchor="middle" fill="#666">{d.period.replace(" 2026", "")}</text>
        </g>
      ))}

      {/* Legend */}
      <g transform={`translate(${pad}, ${h + 5})`}>
        <line x1={0} y1={0} x2={16} y2={0} stroke="#52c41a" strokeWidth={2} />
        <text x={20} y={4} fontSize={9} fill="#666">Actual</text>
        <line x1={80} y1={0} x2={96} y2={0} stroke="#1677ff" strokeWidth={2} />
        <text x={100} y={4} fontSize={9} fill="#666">Predicție</text>
        <rect x={170} y={-5} width={16} height={10} fill="#1677ff" opacity={0.1} stroke="#1677ff" strokeWidth={0.5} />
        <text x={190} y={4} fontSize={9} fill="#666">Interval Confidence</text>
      </g>
    </svg>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function MLForecastPage() {
  const [selectedModule, setSelectedModule] = useState("revenue");
  const [period, setPeriod] = useState("6m");
  const [viewMode, setViewMode] = useState<string>("chart");

  const moduleData = SIMULATED_DATA[selectedModule]!;
  const { summary, forecast } = moduleData;

  const tableColumns = [
    { title: "Perioadă", dataIndex: "period", key: "period" },
    { title: "Predicție", dataIndex: "predicted_value", key: "predicted_value", render: (v: number) => <Text strong>{v}</Text> },
    { title: "Interval Min", dataIndex: "confidence_lower", key: "confidence_lower", render: (v: number) => <Text type="secondary">{v}</Text> },
    { title: "Interval Max", dataIndex: "confidence_upper", key: "confidence_upper", render: (v: number) => <Text type="secondary">{v}</Text> },
    {
      title: "Actual",
      dataIndex: "actual_value",
      key: "actual_value",
      render: (v: number | undefined) => v != null ? <Tag color="green">{v}</Tag> : <Tag>—</Tag>,
    },
    {
      title: "Eroare",
      key: "error",
      render: (_: unknown, record: MLForecastResult) => {
        if (record.actual_value == null) return <Tag>N/A</Tag>;
        const err = ((Math.abs(record.actual_value - record.predicted_value) / record.predicted_value) * 100).toFixed(1);
        return <Tag color={Number(err) < 5 ? "green" : Number(err) < 10 ? "orange" : "red"}>{err}%</Tag>;
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <ExperimentOutlined /> Previziuni Predictive (F135)
          </Title>
          <Text type="secondary">Machine Learning pe date istorice — Placeholder TRL7</Text>
        </Col>
        <Col>
          <Space>
            <Select
              value={selectedModule}
              onChange={setSelectedModule}
              options={FORECAST_MODULES}
              style={{ width: 200 }}
            />
            <Select
              value={period}
              onChange={setPeriod}
              options={PERIOD_OPTIONS}
              style={{ width: 110 }}
              prefix={<CalendarOutlined />}
            />
          </Space>
        </Col>
      </Row>

      <Alert
        type="info"
        showIcon
        icon={<InfoCircleOutlined />}
        message="Date Simulate"
        description="Această pagină demonstrează interfața de previziuni ML. Implementarea reală a modelelor AI/ML va fi disponibilă la TRL7 (vezi Functionalitati_TRL7.md)."
        style={{ marginBottom: 24 }}
      />

      {/* Summary Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title={FORECAST_MODULES.find((m) => m.value === selectedModule)?.label}
              value={summary.value}
              suffix={summary.unit}
              valueStyle={{ color: summary.delta > 0 ? "#52c41a" : "#ff4d4f" }}
              prefix={summary.delta > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="Trend"
              value={Math.abs(summary.delta)}
              suffix="%"
              valueStyle={{ color: summary.delta > 0 ? "#52c41a" : "#ff4d4f" }}
              prefix={summary.delta > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Text type="secondary">Confidence Score</Text>
            <div style={{ marginTop: 8 }}>
              <Progress
                percent={summary.confidence}
                size="small"
                strokeColor={summary.confidence > 80 ? "#52c41a" : summary.confidence > 60 ? "#faad14" : "#ff4d4f"}
              />
            </div>
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small">
            <Text type="secondary">Perioadă Analizată</Text>
            <div style={{ marginTop: 8 }}>
              <Tag icon={<CalendarOutlined />} color="blue">{forecast.length} perioade</Tag>
            </div>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {forecast[0]?.period} — {forecast[forecast.length - 1]?.period}
            </Text>
          </Card>
        </Col>
      </Row>

      {/* View Toggle */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Segmented
            value={viewMode}
            onChange={(v) => setViewMode(v as string)}
            options={[
              { value: "chart", icon: <BarChartOutlined />, label: "Grafic" },
              { value: "table", icon: <TableOutlined />, label: "Tabel" },
            ]}
          />
        </Col>
        <Col>
          <Space size={4}>
            <Tag color="green">Actual</Tag>
            <Tag color="blue">Predicție</Tag>
            <Tag>Interval Confidence</Tag>
          </Space>
        </Col>
      </Row>

      {/* Chart or Table */}
      <Card>
        {viewMode === "chart" ? (
          <ForecastChart data={forecast} unit={summary.unit} />
        ) : (
          <Table
            dataSource={forecast}
            columns={tableColumns}
            rowKey="period"
            pagination={false}
            size="small"
          />
        )}
      </Card>

      {/* Model Details */}
      <Divider />
      <Card title="Detalii Model ML" size="small">
        <Row gutter={16}>
          <Col span={6}>
            <Text type="secondary">Algoritm</Text>
            <div><Tag color="purple">ARIMA + Random Forest</Tag></div>
          </Col>
          <Col span={6}>
            <Text type="secondary">Date Antrenare</Text>
            <div><Text>12 luni istoric (simulat)</Text></div>
          </Col>
          <Col span={6}>
            <Text type="secondary">Eroare Medie</Text>
            <div><Tag color="green">4.2% MAPE</Tag></div>
          </Col>
          <Col span={6}>
            <Text type="secondary">Ultima Antrenare</Text>
            <div><Text>Placeholder — TRL7</Text></div>
          </Col>
        </Row>
      </Card>
    </div>
  );
}
