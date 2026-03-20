/**
 * E-012 — Sales Dashboard / KPI
 * F-codes: F058 (Sales Dashboard — KPIs, funnel, forecast)
 */
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
  Progress,
} from "antd";
import {
  TeamOutlined,
  FunnelPlotOutlined,
  DollarOutlined,
  TrophyOutlined,
  FileTextOutlined,
  RiseOutlined,
  FallOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { pipelineService } from "../services/pipelineService";

const { Title, Text } = Typography;

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

export default function SalesDashboardPage() {
  const {
    data: kpiData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["sales-kpi"],
    queryFn: () => pipelineService.getSalesKPI(),
  });

  const { data: weightedData } = useQuery({
    queryKey: ["weighted-pipeline"],
    queryFn: () => pipelineService.getWeightedPipeline(),
  });

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error) return <Alert type="error" message="Eroare la încărcarea dashboard-ului" />;

  const kpi = kpiData?.data;
  const weighted = weightedData?.data;

  if (!kpi) return <Alert type="warning" message="Date indisponibile" />;

  const winRate =
    kpi.won_opportunities + kpi.lost_opportunities > 0
      ? (
          (kpi.won_opportunities /
            (kpi.won_opportunities + kpi.lost_opportunities)) *
          100
        ).toFixed(1)
      : "0";

  return (
    <>
      <Title level={3}>Sales Dashboard</Title>

      {/* Top KPI cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Contacte Active"
              value={kpi.active_contacts}
              prefix={<TeamOutlined />}
              suffix={`/ ${kpi.total_contacts}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Oportunități Deschise"
              value={kpi.open_opportunities}
              prefix={<FunnelPlotOutlined />}
              suffix={`/ ${kpi.total_opportunities}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Valoare Pipeline"
              value={kpi.pipeline_value}
              prefix={<DollarOutlined />}
              suffix={kpi.currency}
              valueStyle={{ color: "#1677ff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Pipeline Ponderat"
              value={kpi.weighted_pipeline_value}
              prefix={<DollarOutlined />}
              suffix={kpi.currency}
              valueStyle={{ color: "#722ed1" }}
            />
          </Card>
        </Col>
      </Row>

      {/* Win/loss + offers row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Câștigate"
              value={kpi.won_opportunities}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Pierdute"
              value={kpi.lost_opportunities}
              prefix={<FallOutlined />}
              valueStyle={{ color: "#ff4d4f" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Rată Conversie"
              value={Number(winRate)}
              prefix={<RiseOutlined />}
              suffix="%"
              valueStyle={{
                color: Number(winRate) >= 30 ? "#52c41a" : "#faad14",
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Valoare Medie Deal"
              value={kpi.avg_deal_value}
              suffix={kpi.currency}
              valueStyle={{ fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Funnel */}
        <Col xs={24} lg={12}>
          <Card title="Funnel Vânzări">
            {kpi.funnel && kpi.funnel.length > 0 ? (
              <div>
                {kpi.funnel.map((step, idx) => {
                  const maxCount = Math.max(
                    ...kpi.funnel.map((f) => f.count),
                    1
                  );
                  return (
                    <div
                      key={step.stage}
                      style={{ marginBottom: 12, display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <Text style={{ width: 120, textAlign: "right" }}>
                        {STAGE_LABELS[step.stage] ?? step.stage}
                      </Text>
                      <Progress
                        percent={Math.round((step.count / maxCount) * 100)}
                        format={() => step.count}
                        strokeColor={
                          idx < 3
                            ? "#1677ff"
                            : idx < 5
                              ? "#722ed1"
                              : "#52c41a"
                        }
                        style={{ flex: 1 }}
                      />
                    </div>
                  );
                })}
              </div>
            ) : (
              <Text type="secondary">Date insuficiente pentru funnel.</Text>
            )}
          </Card>
        </Col>

        {/* Weighted pipeline per stage */}
        <Col xs={24} lg={12}>
          <Card title="Valoare Ponderată per Stadiu">
            {weighted?.stages ? (
              <Table
                dataSource={weighted.stages}
                rowKey="stage"
                pagination={false}
                size="small"
                columns={[
                  {
                    title: "Stadiu",
                    dataIndex: "stage",
                    render: (v: string) => (
                      <Tag>{STAGE_LABELS[v] ?? v}</Tag>
                    ),
                  },
                  {
                    title: "#",
                    dataIndex: "count",
                    align: "center" as const,
                  },
                  {
                    title: "Valoare",
                    dataIndex: "total_value",
                    align: "right" as const,
                    render: (v: number) => v.toLocaleString("ro-RO"),
                  },
                  {
                    title: "Prob.",
                    dataIndex: "win_probability",
                    align: "center" as const,
                    render: (v: number) => `${v}%`,
                  },
                  {
                    title: "Ponderat",
                    dataIndex: "weighted_value",
                    align: "right" as const,
                    render: (v: number) => (
                      <Text strong>{v.toLocaleString("ro-RO")}</Text>
                    ),
                  },
                ]}
                summary={() => (
                  <Table.Summary.Row>
                    <Table.Summary.Cell index={0}>
                      <Text strong>TOTAL</Text>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={1} />
                    <Table.Summary.Cell index={2} align="right">
                      <Text strong>
                        {weighted.total_pipeline_value.toLocaleString("ro-RO")}
                      </Text>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={3} />
                    <Table.Summary.Cell index={4} align="right">
                      <Text strong style={{ color: "#1677ff" }}>
                        {weighted.total_weighted_value.toLocaleString("ro-RO")}
                      </Text>
                    </Table.Summary.Cell>
                  </Table.Summary.Row>
                )}
              />
            ) : (
              <Text type="secondary">Date indisponibile.</Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Offers + Contracts summary */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Oferte Totale"
              value={kpi.total_offers}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Oferte Trimise"
              value={kpi.offers_sent}
              valueStyle={{ color: "#1677ff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Contracte Active"
              value={kpi.active_contracts}
              suffix={`/ ${kpi.total_contracts}`}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Venit Total"
              value={kpi.total_revenue}
              suffix={kpi.currency}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}
