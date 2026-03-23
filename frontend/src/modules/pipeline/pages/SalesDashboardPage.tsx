/**
 * E-012 — Pipeline Analytics Dashboard
 * F-codes: F056 (Log apeluri + urmărire), F058 (Sales Dashboard — KPIs, funnel, forecast)
 *
 * Tabs: KPIs | Conversion Funnel | Performance per Agent | Forecast Revenue | Product Mix
 * Filters: Period (date range) + Agent
 * Export: CSV
 */
import { useState, useMemo } from "react";
import {
  Card,
  Col,
  Row,
  Statistic,
  Typography,
  Spin,
  Alert,
  Table,
  Tag,
  Tabs,
  Select,
  DatePicker,
  Button,
  Space,
  Tooltip,
  Progress,
  Empty,
} from "antd";
import {
  FunnelPlotOutlined,
  DollarOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  FieldTimeOutlined,
  DownloadOutlined,
  TeamOutlined,
  BarChartOutlined,
  PieChartOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from "recharts";
import dayjs from "dayjs";
import { pipelineService } from "../services/pipelineService";
import type {
  FunnelStage,
  AgentPerformance,
  ForecastMonth,
  ProductMixItem,
} from "../../../types";

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const STAGE_LABELS: Record<string, string> = {
  new: "Nou",
  qualified: "Calificat",
  scoping: "Predimensionare",
  offering: "Ofertare",
  sent: "Trimis",
  negotiation: "Negociere",
  won: "Câștigat",
  lost: "Pierdut",
};

const STAGE_COLORS: Record<string, string> = {
  new: "#1677ff",
  qualified: "#2f54eb",
  scoping: "#722ed1",
  offering: "#eb2f96",
  sent: "#fa8c16",
  negotiation: "#faad14",
  won: "#52c41a",
  lost: "#ff4d4f",
};

const PIE_COLORS = ["#1677ff", "#52c41a", "#722ed1", "#fa8c16", "#eb2f96", "#13c2c2", "#faad14", "#2f54eb"];

const formatRON = (v: number) =>
  v.toLocaleString("ro-RO", { minimumFractionDigits: 0, maximumFractionDigits: 0 });

export default function SalesDashboardPage() {
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([null, null]);
  const [agentFilter, setAgentFilter] = useState<string | undefined>(undefined);

  const queryParams = useMemo(() => {
    const params: Record<string, string> = {};
    if (dateRange[0]) params.period_start = dateRange[0].toISOString();
    if (dateRange[1]) params.period_end = dateRange[1].toISOString();
    if (agentFilter) params.agent_id = agentFilter;
    return params;
  }, [dateRange, agentFilter]);

  const {
    data: analyticsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["pipeline-analytics", queryParams],
    queryFn: () => pipelineService.getPipelineAnalytics(queryParams),
  });

  const analytics = analyticsData?.data;

  // Get unique agents for filter dropdown
  const agentOptions = useMemo(() => {
    if (!analytics?.agent_performance) return [];
    return analytics.agent_performance
      .filter((a) => a.agent_id)
      .map((a) => ({ value: a.agent_id!, label: a.agent_name }));
  }, [analytics]);

  const handleExportCSV = async () => {
    try {
      const blob = await pipelineService.exportAnalyticsCSV("all");
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `pipeline_analytics_${dayjs().format("YYYY-MM-DD")}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      // silent fail
    }
  };

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error) return <Alert type="error" message="Eroare la încărcarea analytics-ului" />;
  if (!analytics) return <Alert type="warning" message="Date indisponibile" />;

  const { kpis, funnel, agent_performance, forecast, product_mix } = analytics;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={3} style={{ margin: 0 }}>Pipeline Analytics</Title>
        </Col>
        <Col>
          <Space wrap>
            <RangePicker
              value={dateRange}
              onChange={(vals) => setDateRange(vals ?? [null, null])}
              format="DD.MM.YYYY"
              placeholder={["De la", "Până la"]}
              allowClear
            />
            <Select
              placeholder="Toți agenții"
              allowClear
              style={{ width: 200 }}
              value={agentFilter}
              onChange={setAgentFilter}
              options={agentOptions}
            />
            <Tooltip title="Export CSV">
              <Button icon={<DownloadOutlined />} onClick={handleExportCSV}>
                Export CSV
              </Button>
            </Tooltip>
          </Space>
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="kpis"
        type="card"
        items={[
          {
            key: "kpis",
            label: (
              <span><BarChartOutlined /> KPIs</span>
            ),
            children: <KPIsTab kpis={kpis} currency={analytics.currency} />,
          },
          {
            key: "funnel",
            label: (
              <span><FunnelPlotOutlined /> Funnel Conversie</span>
            ),
            children: <FunnelTab funnel={funnel} />,
          },
          {
            key: "agents",
            label: (
              <span><TeamOutlined /> Performanță Agenți</span>
            ),
            children: <AgentPerformanceTab agents={agent_performance} currency={analytics.currency} />,
          },
          {
            key: "forecast",
            label: (
              <span><RiseOutlined /> Forecast Venituri</span>
            ),
            children: <ForecastTab forecast={forecast} currency={analytics.currency} />,
          },
          {
            key: "product_mix",
            label: (
              <span><PieChartOutlined /> Mix Produse</span>
            ),
            children: <ProductMixTab items={product_mix} currency={analytics.currency} />,
          },
        ]}
      />
    </>
  );
}

/* ─── KPIs Tab ──────────────────────────────────────────────────────────────── */

function KPIsTab({ kpis, currency }: { kpis: NonNullable<ReturnType<typeof Object>>; currency: string }) {
  const k = kpis as Record<string, number>;
  return (
    <>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Total Oportunități"
              value={k.total_opportunities}
              prefix={<FunnelPlotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Deschise"
              value={k.open_opportunities}
              valueStyle={{ color: "#1677ff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Câștigate"
              value={k.won_opportunities}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Pierdute"
              value={k.lost_opportunities}
              prefix={<FallOutlined />}
              valueStyle={{ color: "#ff4d4f" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Win Rate"
              value={k.win_rate}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: (k.win_rate ?? 0) >= 30 ? "#52c41a" : "#faad14" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card hoverable>
            <Statistic
              title="Ciclu Mediu"
              value={k.avg_cycle_days}
              suffix="zile"
              prefix={<FieldTimeOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Valoare Pipeline"
              value={k.pipeline_value}
              prefix={<DollarOutlined />}
              suffix={currency}
              valueStyle={{ color: "#1677ff" }}
              formatter={(v) => formatRON(Number(v))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Pipeline Ponderat"
              value={k.weighted_value}
              suffix={currency}
              valueStyle={{ color: "#722ed1" }}
              formatter={(v) => formatRON(Number(v))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Valoare Câștigată"
              value={k.won_value}
              suffix={currency}
              valueStyle={{ color: "#52c41a" }}
              formatter={(v) => formatRON(Number(v))}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Valoare Medie Deal"
              value={k.avg_deal_value}
              suffix={currency}
              formatter={(v) => formatRON(Number(v))}
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}

/* ─── Conversion Funnel Tab ─────────────────────────────────────────────────── */

function FunnelTab({ funnel }: { funnel: FunnelStage[] }) {
  if (!funnel.length) return <Empty description="Date insuficiente pentru funnel" />;

  const maxCount = Math.max(...funnel.map((f) => f.count), 1);

  const chartData = funnel.map((f) => ({
    ...f,
    name: STAGE_LABELS[f.stage] ?? f.stage,
    fill: STAGE_COLORS[f.stage] ?? "#1677ff",
  }));

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={14}>
        <Card title="Funnel Conversie — Vizualizare">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={120} />
              <RechartsTooltip
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                formatter={((value: any, name: any) => [
                  name === "count" ? value : `${formatRON(Number(value))} RON`,
                  name === "count" ? "Oportunități" : "Valoare",
                ]) as any}
              />
              <Bar dataKey="count" name="Oportunități" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24} lg={10}>
        <Card title="Drop-off per Stadiu">
          {funnel.map((step, idx) => (
            <div key={step.stage} style={{ marginBottom: 16 }}>
              <Row justify="space-between">
                <Text strong>{STAGE_LABELS[step.stage] ?? step.stage}</Text>
                <Space>
                  <Tag color="blue">{step.count} opp.</Tag>
                  <Tag color="green">{formatRON(step.value)} RON</Tag>
                </Space>
              </Row>
              <Row align="middle" style={{ gap: 8, marginTop: 4 }}>
                <Progress
                  percent={Math.round((step.count / maxCount) * 100)}
                  showInfo={false}
                  strokeColor={STAGE_COLORS[step.stage] ?? "#1677ff"}
                  style={{ flex: 1 }}
                />
                {idx > 0 && (
                  <Tooltip title={`Drop-off: ${step.drop_off_rate}%`}>
                    <Tag color={step.drop_off_rate > 50 ? "red" : step.drop_off_rate > 30 ? "orange" : "green"}>
                      {step.conversion_rate > 0 ? `${step.conversion_rate}%` : "—"}
                    </Tag>
                  </Tooltip>
                )}
              </Row>
            </div>
          ))}
        </Card>
      </Col>
    </Row>
  );
}

/* ─── Agent Performance Tab ─────────────────────────────────────────────────── */

function AgentPerformanceTab({ agents, currency }: { agents: AgentPerformance[]; currency: string }) {
  if (!agents.length) return <Empty description="Niciun agent cu oportunități" />;

  const columns = [
    {
      title: "Agent",
      dataIndex: "agent_name",
      key: "agent_name",
      fixed: "left" as const,
      width: 160,
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: "Total",
      dataIndex: "total_deals",
      key: "total_deals",
      align: "center" as const,
      width: 70,
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.total_deals - b.total_deals,
    },
    {
      title: "Câștig.",
      dataIndex: "won_deals",
      key: "won_deals",
      align: "center" as const,
      width: 70,
      render: (v: number) => <Tag color="green">{v}</Tag>,
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.won_deals - b.won_deals,
    },
    {
      title: "Pierd.",
      dataIndex: "lost_deals",
      key: "lost_deals",
      align: "center" as const,
      width: 70,
      render: (v: number) => <Tag color="red">{v}</Tag>,
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.lost_deals - b.lost_deals,
    },
    {
      title: "Deschise",
      dataIndex: "open_deals",
      key: "open_deals",
      align: "center" as const,
      width: 80,
    },
    {
      title: `Valoare (${currency})`,
      dataIndex: "total_value",
      key: "total_value",
      align: "right" as const,
      width: 130,
      render: (v: number) => formatRON(v),
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.total_value - b.total_value,
    },
    {
      title: `Câștigat (${currency})`,
      dataIndex: "won_value",
      key: "won_value",
      align: "right" as const,
      width: 130,
      render: (v: number) => <Text style={{ color: "#52c41a" }}>{formatRON(v)}</Text>,
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.won_value - b.won_value,
    },
    {
      title: "Win Rate",
      dataIndex: "win_rate",
      key: "win_rate",
      align: "center" as const,
      width: 90,
      render: (v: number) => (
        <Tag color={v >= 40 ? "green" : v >= 20 ? "orange" : "red"}>{v}%</Tag>
      ),
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.win_rate - b.win_rate,
    },
    {
      title: "Val. Medie",
      dataIndex: "avg_deal_value",
      key: "avg_deal_value",
      align: "right" as const,
      width: 110,
      render: (v: number) => formatRON(v),
    },
    {
      title: "Ciclu (zile)",
      dataIndex: "avg_cycle_days",
      key: "avg_cycle_days",
      align: "center" as const,
      width: 100,
      render: (v: number) => v > 0 ? `${v}` : "—",
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.avg_cycle_days - b.avg_cycle_days,
    },
    {
      title: "Activități",
      dataIndex: "activities_count",
      key: "activities_count",
      align: "center" as const,
      width: 90,
      sorter: (a: AgentPerformance, b: AgentPerformance) => a.activities_count - b.activities_count,
    },
  ];

  // Chart data for visual comparison
  const chartData = agents.slice(0, 10).map((a) => ({
    name: a.agent_name.split(" ")[0],
    won: a.won_value,
    open: a.total_value - a.won_value,
    winRate: a.win_rate,
  }));

  return (
    <>
      <Card title="Comparație Vizuală — Top Agenți" style={{ marginBottom: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ left: 10, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
            <RechartsTooltip
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={((value: any, name: any) => [
                name === "winRate" ? `${value}%` : `${formatRON(Number(value))} ${currency}`,
                name === "won" ? "Câștigat" : name === "open" ? "Pipeline" : "Win Rate",
              ]) as any}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="won" name="Câștigat" fill="#52c41a" stackId="a" />
            <Bar yAxisId="left" dataKey="open" name="Pipeline" fill="#1677ff" stackId="a" />
            <Bar yAxisId="right" dataKey="winRate" name="Win Rate %" fill="#faad14" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card title="Tabel Detaliat Performanță">
        <Table
          dataSource={agents}
          columns={columns}
          rowKey="agent_id"
          pagination={false}
          scroll={{ x: 1200 }}
          size="middle"
          summary={() => {
            const totals = agents.reduce(
              (acc, a) => ({
                total: acc.total + a.total_deals,
                won: acc.won + a.won_deals,
                lost: acc.lost + a.lost_deals,
                open: acc.open + a.open_deals,
                value: acc.value + a.total_value,
                wonValue: acc.wonValue + a.won_value,
                acts: acc.acts + a.activities_count,
              }),
              { total: 0, won: 0, lost: 0, open: 0, value: 0, wonValue: 0, acts: 0 },
            );
            const totalWR = (totals.won + totals.lost) > 0
              ? (totals.won / (totals.won + totals.lost) * 100)
              : 0;
            return (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0}><Text strong>TOTAL</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={1} align="center"><Text strong>{totals.total}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={2} align="center"><Text strong>{totals.won}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={3} align="center"><Text strong>{totals.lost}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={4} align="center"><Text strong>{totals.open}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={5} align="right"><Text strong>{formatRON(totals.value)}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={6} align="right"><Text strong style={{ color: "#52c41a" }}>{formatRON(totals.wonValue)}</Text></Table.Summary.Cell>
                <Table.Summary.Cell index={7} align="center"><Tag color="blue">{totalWR.toFixed(1)}%</Tag></Table.Summary.Cell>
                <Table.Summary.Cell index={8} />
                <Table.Summary.Cell index={9} />
                <Table.Summary.Cell index={10} align="center"><Text strong>{totals.acts}</Text></Table.Summary.Cell>
              </Table.Summary.Row>
            );
          }}
        />
      </Card>
    </>
  );
}

/* ─── Forecast Tab ──────────────────────────────────────────────────────────── */

function ForecastTab({ forecast, currency }: { forecast: ForecastMonth[]; currency: string }) {
  if (!forecast.length) return <Empty description="Date insuficiente pentru forecast" />;

  const chartData = forecast.map((f) => ({
    ...f,
    name: dayjs(f.month + "-01").format("MMM YYYY"),
    total: f.confirmed_value + f.weighted_value,
  }));

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={16}>
        <Card title="Forecast Venituri — Confirmat vs. Ponderat (6 luni)">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ left: 10, right: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <RechartsTooltip
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                formatter={((value: any, name: any) => [
                  `${formatRON(Number(value))} ${currency}`,
                  name === "confirmed_value" ? "Confirmat" : "Ponderat",
                ]) as any}
              />
              <Legend />
              <Bar dataKey="confirmed_value" name="Confirmat (Câștigat)" fill="#52c41a" radius={[4, 4, 0, 0]} />
              <Bar dataKey="weighted_value" name="Ponderat (Pipeline)" fill="#1677ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        <Card title="Detalii Lunare">
          <Table
            dataSource={chartData}
            rowKey="month"
            pagination={false}
            size="small"
            columns={[
              {
                title: "Luna",
                dataIndex: "name",
                key: "name",
              },
              {
                title: "Confirmat",
                dataIndex: "confirmed_value",
                key: "confirmed_value",
                align: "right" as const,
                render: (v: number) => (
                  <Text style={{ color: "#52c41a" }}>{formatRON(v)}</Text>
                ),
              },
              {
                title: "Ponderat",
                dataIndex: "weighted_value",
                key: "weighted_value",
                align: "right" as const,
                render: (v: number) => (
                  <Text style={{ color: "#1677ff" }}>{formatRON(v)}</Text>
                ),
              },
              {
                title: "Deals",
                dataIndex: "deal_count",
                key: "deal_count",
                align: "center" as const,
              },
            ]}
            summary={() => {
              const totConf = forecast.reduce((s, f) => s + f.confirmed_value, 0);
              const totWeighted = forecast.reduce((s, f) => s + f.weighted_value, 0);
              const totDeals = forecast.reduce((s, f) => s + f.deal_count, 0);
              return (
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0}><Text strong>TOTAL</Text></Table.Summary.Cell>
                  <Table.Summary.Cell index={1} align="right">
                    <Text strong style={{ color: "#52c41a" }}>{formatRON(totConf)}</Text>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={2} align="right">
                    <Text strong style={{ color: "#1677ff" }}>{formatRON(totWeighted)}</Text>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={3} align="center">
                    <Text strong>{totDeals}</Text>
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              );
            }}
          />
        </Card>
      </Col>
    </Row>
  );
}

/* ─── Product Mix Tab ───────────────────────────────────────────────────────── */

function ProductMixTab({ items, currency }: { items: ProductMixItem[]; currency: string }) {
  if (!items.length) return <Empty description="Date insuficiente pentru mix produse" />;

  const pieData = items.map((p, i) => ({
    name: p.category,
    value: p.total_value,
    fill: PIE_COLORS[i % PIE_COLORS.length],
  }));

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <Card title="Distribuție Valoare per Categorie">
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={120}
                dataKey="value"
                label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
              >
                {pieData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.fill} />
                ))}
              </Pie>
              <RechartsTooltip
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                formatter={((value: any) => [`${formatRON(Number(value))} ${currency}`, "Valoare"]) as any}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Tabel Mix Produse">
          <Table
            dataSource={items}
            rowKey="category"
            pagination={false}
            size="middle"
            columns={[
              {
                title: "Categorie",
                dataIndex: "category",
                key: "category",
                render: (v: string, _: ProductMixItem, idx: number) => (
                  <Space>
                    <div style={{
                      width: 12,
                      height: 12,
                      borderRadius: 2,
                      backgroundColor: PIE_COLORS[idx % PIE_COLORS.length],
                    }} />
                    <Text>{v}</Text>
                  </Space>
                ),
              },
              {
                title: "Deals",
                dataIndex: "deal_count",
                key: "deal_count",
                align: "center" as const,
              },
              {
                title: `Valoare (${currency})`,
                dataIndex: "total_value",
                key: "total_value",
                align: "right" as const,
                render: (v: number) => formatRON(v),
                sorter: (a: ProductMixItem, b: ProductMixItem) => a.total_value - b.total_value,
              },
              {
                title: "%",
                dataIndex: "percentage",
                key: "percentage",
                align: "center" as const,
                render: (v: number) => (
                  <Progress
                    percent={v}
                    size="small"
                    format={(p) => `${p}%`}
                    strokeColor="#1677ff"
                  />
                ),
              },
            ]}
          />
        </Card>
      </Col>
    </Row>
  );
}
