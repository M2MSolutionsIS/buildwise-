/**
 * F133: Executive Dashboard — Cross-module CRM+Pipeline+PM+RM
 * Template + custom. KPI summary. Specific P2+P3.
 */
import { useMemo } from "react";
import {
  Card,
  Statistic,
  Row,
  Col,
  Typography,
  Tag,
  Spin,
  Progress,
  Space,
  Alert,
  Divider,
} from "antd";
import {
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  ToolOutlined,
  DashboardOutlined,
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  DollarOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { biService } from "../services/biService";
import type { ExecutiveSummary } from "../../../types";

const { Title, Text } = Typography;

function fmt(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
  return v.toLocaleString("ro-RO");
}

export default function ExecutiveDashboardPage() {
  const { data: summaryData, isLoading } = useQuery({
    queryKey: ["executive-summary"],
    queryFn: () => biService.getExecutiveSummary(),
  });

  const { data: kpiData } = useQuery({
    queryKey: ["kpi-dashboard"],
    queryFn: () => biService.getKPIDashboard(),
  });

  const summary: ExecutiveSummary | undefined = summaryData?.data;
  const kpis = kpiData?.data ?? [];

  const kpiSummary = useMemo(() => {
    const green = kpis.filter((k) => k.threshold_color === "green").length;
    const yellow = kpis.filter((k) => k.threshold_color === "yellow").length;
    const red = kpis.filter((k) => k.threshold_color === "red").length;
    return { green, yellow, red, total: kpis.length };
  }, [kpis]);

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
            <DashboardOutlined /> Executive Dashboard (F133)
          </Title>
          <Text type="secondary">
            Vedere strategică unificată — CRM + Pipeline + PM + RM
          </Text>
        </Col>
        <Col>
          <Space>
            <Tag color="green">{kpiSummary.green} KPI OK</Tag>
            <Tag color="orange">{kpiSummary.yellow} Atenție</Tag>
            <Tag color="red">{kpiSummary.red} Critic</Tag>
          </Space>
        </Col>
      </Row>

      {!summary && (
        <Alert
          type="info"
          showIcon
          message="Nu există date suficiente pentru dashboard"
          description="Dashboard-ul se va popula automat pe măsură ce adaugi contacte, oportunități și proiecte."
        />
      )}

      {summary && (
        <>
          {/* CRM Module */}
          <Divider orientation="left">
            <Space>
              <TeamOutlined style={{ color: "#1677ff" }} />
              <Text strong>CRM</Text>
            </Space>
          </Divider>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Total Contacte" value={summary.crm.total_contacts} prefix={<TeamOutlined />} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Contacte Active" value={summary.crm.active_contacts} valueStyle={{ color: "#52c41a" }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Lead-uri" value={summary.crm.leads} valueStyle={{ color: "#1677ff" }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Clienți" value={summary.crm.clients} prefix={<CheckCircleOutlined />} valueStyle={{ color: "#52c41a" }} />
              </Card>
            </Col>
          </Row>

          {/* Pipeline Module */}
          <Divider orientation="left">
            <Space>
              <FunnelPlotOutlined style={{ color: "#fa8c16" }} />
              <Text strong>Sales Pipeline</Text>
            </Space>
          </Divider>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Oportunități Deschise" value={summary.pipeline.open_opportunities} suffix={`/ ${summary.pipeline.total_opportunities}`} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Valoare Pipeline" value={fmt(summary.pipeline.total_pipeline_value)} prefix={<DollarOutlined />} suffix={summary.pipeline.currency} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Valoare Ponderată" value={fmt(summary.pipeline.weighted_value)} suffix={summary.pipeline.currency} valueStyle={{ color: "#1677ff" }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic
                  title="Win Rate"
                  value={summary.pipeline.win_rate}
                  precision={1}
                  suffix="%"
                  prefix={summary.pipeline.win_rate >= 30 ? <RiseOutlined /> : <FallOutlined />}
                  valueStyle={{ color: summary.pipeline.win_rate >= 30 ? "#52c41a" : "#ff4d4f" }}
                />
              </Card>
            </Col>
          </Row>

          {/* PM Module */}
          <Divider orientation="left">
            <Space>
              <ProjectOutlined style={{ color: "#52c41a" }} />
              <Text strong>Project Management</Text>
            </Space>
          </Divider>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Proiecte Active" value={summary.pm.active_projects} suffix={`/ ${summary.pm.total_projects}`} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Finalizate" value={summary.pm.completed_projects} prefix={<CheckCircleOutlined />} valueStyle={{ color: "#52c41a" }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Progres Mediu" value={summary.pm.avg_progress} suffix="%" />
                <Progress percent={summary.pm.avg_progress} size="small" showInfo={false} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Total Proiecte" value={summary.pm.total_projects} prefix={<ProjectOutlined />} />
              </Card>
            </Col>
          </Row>

          {/* RM Module */}
          <Divider orientation="left">
            <Space>
              <ToolOutlined style={{ color: "#722ed1" }} />
              <Text strong>Resource Management</Text>
            </Space>
          </Divider>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Angajați Activi" value={summary.rm.active_employees} suffix={`/ ${summary.rm.total_employees}`} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Echipamente" value={summary.rm.total_equipment} prefix={<ToolOutlined />} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic title="Alocări Active" value={summary.rm.active_allocations} valueStyle={{ color: "#1677ff" }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small">
                <Statistic
                  title="KPI-uri"
                  value={kpiSummary.total}
                  prefix={kpiSummary.red > 0 ? <WarningOutlined /> : <CheckCircleOutlined />}
                  valueStyle={{ color: kpiSummary.red > 0 ? "#ff4d4f" : "#52c41a" }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* KPI Cards */}
      {kpis.length > 0 && (
        <>
          <Divider orientation="left">
            <Space>
              <DashboardOutlined />
              <Text strong>KPI-uri Cheie (F152)</Text>
            </Space>
          </Divider>
          <Row gutter={[16, 16]}>
            {kpis.slice(0, 8).map((kpi) => {
              const colorMap: Record<string, string> = { green: "#52c41a", yellow: "#faad14", red: "#ff4d4f" };
              const color = colorMap[kpi.threshold_color ?? ""] ?? "#d9d9d9";
              return (
                <Col xs={12} sm={6} key={kpi.kpi_id}>
                  <Card
                    size="small"
                    style={{ borderLeft: `4px solid ${color}` }}
                  >
                    <Statistic
                      title={kpi.name}
                      value={kpi.current_value ?? 0}
                      suffix={kpi.unit}
                      valueStyle={{ color }}
                    />
                    <Tag color={kpi.module === "pm" ? "green" : kpi.module === "crm" ? "blue" : "orange"}>
                      {kpi.module.toUpperCase()}
                    </Tag>
                  </Card>
                </Col>
              );
            })}
          </Row>
        </>
      )}
    </div>
  );
}
