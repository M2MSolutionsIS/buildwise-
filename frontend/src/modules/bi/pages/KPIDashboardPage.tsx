/**
 * F152: KPI Dashboard — Grid cards, gauge, trend, drill-down, ranking
 * Specific P0 — Common (all prototypes).
 */
import { useState, useMemo } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Tag,
  Spin,
  Select,
  Progress,
  Space,
  Empty,
  Tooltip,
  Badge,
  Segmented,
} from "antd";
import {
  DashboardOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
  AppstoreOutlined,
  BarsOutlined,
  FilterOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { biService } from "../services/biService";
import type { KPIDashboardItem } from "../../../types";

const { Title, Text } = Typography;

const MODULE_OPTIONS = [
  { label: "Toate", value: "all" },
  { label: "CRM", value: "crm" },
  { label: "Pipeline", value: "pipeline" },
  { label: "PM", value: "pm" },
  { label: "RM", value: "rm" },
];

const COLOR_MAP: Record<string, string> = {
  green: "#52c41a",
  yellow: "#faad14",
  red: "#ff4d4f",
};

function TrendIndicator({ trend }: { trend: number[] }) {
  if (!trend || trend.length < 2) return <MinusOutlined style={{ color: "#d9d9d9" }} />;
  const last = trend[trend.length - 1]!;
  const prev = trend[trend.length - 2]!;
  const diff = last - prev;
  const pct = prev !== 0 ? ((diff / prev) * 100).toFixed(1) : "0";

  if (diff > 0) {
    return (
      <Tooltip title={`+${pct}% față de perioada anterioară`}>
        <Text style={{ color: "#52c41a", fontSize: 12 }}>
          <ArrowUpOutlined /> +{pct}%
        </Text>
      </Tooltip>
    );
  }
  if (diff < 0) {
    return (
      <Tooltip title={`${pct}% față de perioada anterioară`}>
        <Text style={{ color: "#ff4d4f", fontSize: 12 }}>
          <ArrowDownOutlined /> {pct}%
        </Text>
      </Tooltip>
    );
  }
  return (
    <Tooltip title="Nicio schimbare">
      <Text style={{ color: "#d9d9d9", fontSize: 12 }}>
        <MinusOutlined /> 0%
      </Text>
    </Tooltip>
  );
}

function MiniSparkline({ trend, color }: { trend: number[]; color: string }) {
  if (!trend || trend.length < 2) return null;
  const max = Math.max(...trend);
  const min = Math.min(...trend);
  const range = max - min || 1;
  const h = 32;
  const w = 80;
  const points = trend
    .map((v, i) => {
      const x = (i / (trend.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polyline fill="none" stroke={color} strokeWidth={1.5} points={points} />
    </svg>
  );
}

function KPICard({ kpi }: { kpi: KPIDashboardItem }) {
  const color = COLOR_MAP[kpi.threshold_color ?? ""] ?? "#d9d9d9";
  const moduleTag = kpi.module === "pm" ? "green" : kpi.module === "crm" ? "blue" : kpi.module === "pipeline" ? "orange" : "purple";

  return (
    <Card
      size="small"
      style={{ borderLeft: `4px solid ${color}`, height: "100%" }}
      styles={{ body: { padding: "12px 16px" } }}
    >
      <Space direction="vertical" size={4} style={{ width: "100%" }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Text type="secondary" style={{ fontSize: 12 }}>{kpi.name}</Text>
          </Col>
          <Col>
            <Tag color={moduleTag} style={{ margin: 0, fontSize: 10 }}>
              {kpi.module.toUpperCase()}
            </Tag>
          </Col>
        </Row>

        <Row justify="space-between" align="bottom">
          <Col>
            <Text strong style={{ fontSize: 24, color }}>
              {kpi.current_value ?? "—"}
            </Text>
            {kpi.unit && (
              <Text type="secondary" style={{ marginLeft: 4, fontSize: 12 }}>
                {kpi.unit}
              </Text>
            )}
          </Col>
          <Col>
            <MiniSparkline trend={kpi.trend} color={color} />
          </Col>
        </Row>

        <Row justify="space-between" align="middle">
          <Col>
            <TrendIndicator trend={kpi.trend} />
          </Col>
          <Col>
            {kpi.display_type === "gauge" && kpi.current_value != null && (
              <Progress
                type="circle"
                percent={Math.min(kpi.current_value, 100)}
                size={28}
                strokeColor={color}
                format={() => ""}
              />
            )}
          </Col>
        </Row>
      </Space>
    </Card>
  );
}

function KPIRanking({ kpis }: { kpis: KPIDashboardItem[] }) {
  const sorted = [...kpis]
    .filter((k) => k.current_value != null)
    .sort((a, b) => (b.current_value ?? 0) - (a.current_value ?? 0));

  if (sorted.length === 0) return <Empty description="Niciun KPI cu valoare" />;

  return (
    <Card title="Ranking KPI" size="small">
      {sorted.slice(0, 10).map((kpi, idx) => {
        const color = COLOR_MAP[kpi.threshold_color ?? ""] ?? "#d9d9d9";
        return (
          <Row key={kpi.kpi_id} justify="space-between" style={{ padding: "6px 0", borderBottom: "1px solid #f0f0f0" }}>
            <Col>
              <Badge count={idx + 1} style={{ backgroundColor: idx < 3 ? "#1677ff" : "#d9d9d9" }} />
              <Text style={{ marginLeft: 8 }}>{kpi.name}</Text>
            </Col>
            <Col>
              <Text strong style={{ color }}>
                {kpi.current_value} {kpi.unit}
              </Text>
            </Col>
          </Row>
        );
      })}
    </Card>
  );
}

export default function KPIDashboardPage() {
  const [moduleFilter, setModuleFilter] = useState("all");
  const [viewMode, setViewMode] = useState<string>("grid");

  const { data: kpiData, isLoading } = useQuery({
    queryKey: ["kpi-dashboard"],
    queryFn: () => biService.getKPIDashboard(),
  });

  const kpis: KPIDashboardItem[] = kpiData?.data ?? [];

  const filtered = useMemo(
    () => (moduleFilter === "all" ? kpis : kpis.filter((k) => k.module === moduleFilter)),
    [kpis, moduleFilter]
  );

  const stats = useMemo(() => {
    const green = filtered.filter((k) => k.threshold_color === "green").length;
    const yellow = filtered.filter((k) => k.threshold_color === "yellow").length;
    const red = filtered.filter((k) => k.threshold_color === "red").length;
    return { green, yellow, red, total: filtered.length };
  }, [filtered]);

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <DashboardOutlined /> KPI Dashboard (F152)
          </Title>
          <Text type="secondary">Monitorizare KPI-uri în timp real</Text>
        </Col>
        <Col>
          <Space>
            <Tag color="green">{stats.green} OK</Tag>
            <Tag color="orange">{stats.yellow} Atenție</Tag>
            <Tag color="red">{stats.red} Critic</Tag>
          </Space>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <FilterOutlined />
            <Select
              value={moduleFilter}
              onChange={setModuleFilter}
              options={MODULE_OPTIONS}
              style={{ width: 140 }}
            />
          </Space>
        </Col>
        <Col>
          <Segmented
            value={viewMode}
            onChange={(v) => setViewMode(v as string)}
            options={[
              { value: "grid", icon: <AppstoreOutlined /> },
              { value: "ranking", icon: <BarsOutlined /> },
            ]}
          />
        </Col>
      </Row>

      {/* Summary bar */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={6}>
          <Card size="small" style={{ textAlign: "center" }}>
            <Text type="secondary">Total</Text>
            <div>
              <Text strong style={{ fontSize: 20 }}>{stats.total}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={6}>
          <Card size="small" style={{ textAlign: "center", borderTop: "3px solid #52c41a" }}>
            <Text type="secondary">OK</Text>
            <div>
              <Text strong style={{ fontSize: 20, color: "#52c41a" }}>{stats.green}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={6}>
          <Card size="small" style={{ textAlign: "center", borderTop: "3px solid #faad14" }}>
            <Text type="secondary">Atenție</Text>
            <div>
              <Text strong style={{ fontSize: 20, color: "#faad14" }}>{stats.yellow}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={6}>
          <Card size="small" style={{ textAlign: "center", borderTop: "3px solid #ff4d4f" }}>
            <Text type="secondary">Critic</Text>
            <div>
              <Text strong style={{ fontSize: 20, color: "#ff4d4f" }}>{stats.red}</Text>
            </div>
          </Card>
        </Col>
      </Row>

      {filtered.length === 0 ? (
        <Empty description="Niciun KPI definit. Creează KPI-uri din KPI Builder (F148)." />
      ) : viewMode === "grid" ? (
        <Row gutter={[16, 16]}>
          {filtered.map((kpi) => (
            <Col xs={24} sm={12} md={8} lg={6} key={kpi.kpi_id}>
              <KPICard kpi={kpi} />
            </Col>
          ))}
        </Row>
      ) : (
        <KPIRanking kpis={filtered} />
      )}
    </div>
  );
}
