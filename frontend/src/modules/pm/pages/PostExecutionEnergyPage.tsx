/**
 * E-029: Post-Execution Energy — F086, F088, F090, F105
 * P1-specific: PRE/POST energy comparison dashboard + ML dataset export.
 * Connected to /api/v1/pm/projects/:id/energy-impact
 */
import { useParams } from "react-router-dom";
import {
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Space,
  Tag,
  App,
  Progress,
  Alert,
} from "antd";
import {
  ThunderboltOutlined,
  ArrowDownOutlined,
  ArrowUpOutlined,
  DownloadOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  DatabaseOutlined,
  FireOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import api from "../../../services/api";
import type { ApiResponse, EnergyImpact } from "../../../types";
import { SkeletonKPI } from "../../../components/SkeletonLoaders";
import EmptyState from "../../../components/EmptyState";

const { Title, Text } = Typography;

export default function PostExecutionEnergyPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { message } = App.useApp();

  const { data, isLoading } = useQuery({
    queryKey: ["energy-impact", projectId],
    queryFn: async (): Promise<ApiResponse<EnergyImpact>> => {
      const { data } = await api.get(`/pm/projects/${projectId}/energy-impact`);
      return data;
    },
    enabled: !!projectId,
  });

  const impact = data?.data;

  const exportMLDataset = async () => {
    try {
      const { data } = await api.get(`/pm/projects/${projectId}/energy-impact/export`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `energy_dataset_${projectId}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      message.success("Dataset exportat cu succes");
    } catch {
      message.error("Eroare la export");
    }
  };

  if (isLoading) return <SkeletonKPI count={4} />;

  if (!impact) {
    return (
      <EmptyState
        icon={<ThunderboltOutlined style={{ color: "#F59E0B" }} />}
        title="Nicio analiză energetică post-execuție"
        description="Completează măsurătorile PRE și POST pentru a genera comparația."
      />
    );
  }

  // Calculations
  const kwhSavings = impact.estimated_kwh_savings || ((impact.pre_kwh_annual || 0) - (impact.post_kwh_annual || 0));
  const co2Reduction = impact.estimated_co2_reduction || ((impact.pre_co2_kg_annual || 0) - (impact.post_co2_kg_annual || 0));
  const kwhSavingsPct = impact.pre_kwh_annual ? ((kwhSavings / impact.pre_kwh_annual) * 100).toFixed(1) : "0";
  const uImprovement = (impact.pre_u_value_avg || 0) - (impact.post_u_value_avg || 0);

  const comparisonRows = [
    {
      key: "kwh",
      metric: "Consum electric (kWh/an)",
      pre: impact.pre_kwh_annual,
      post: impact.post_kwh_annual,
      saving: kwhSavings,
      unit: "kWh",
    },
    {
      key: "gas",
      metric: "Consum gaz (mc/an)",
      pre: impact.pre_gas_mc_annual,
      post: impact.post_gas_mc_annual,
      saving: (impact.pre_gas_mc_annual || 0) - (impact.post_gas_mc_annual || 0),
      unit: "mc",
    },
    {
      key: "co2",
      metric: "Emisii CO₂ (kg/an)",
      pre: impact.pre_co2_kg_annual,
      post: impact.post_co2_kg_annual,
      saving: co2Reduction,
      unit: "kg",
    },
    {
      key: "uvalue",
      metric: "U-value mediu (W/m²K)",
      pre: impact.pre_u_value_avg,
      post: impact.post_u_value_avg,
      saving: uImprovement,
      unit: "W/m²K",
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <ThunderboltOutlined style={{ fontSize: 20, color: "#F59E0B" }} />
          <Title level={4} style={{ margin: 0 }}>Analiză Energetică Post-Execuție</Title>
          <Tag color="orange">P1 — Eficiență Energetică</Tag>
        </Space>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={exportMLDataset}>
            Export CSV
          </Button>
          <Button type="primary" icon={<DatabaseOutlined />} onClick={exportMLDataset}>
            Export Dataset ML
          </Button>
        </Space>
      </div>

      {/* Summary KPIs */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Statistic
              title={<Text type="secondary">Economie kWh/an</Text>}
              value={kwhSavings}
              precision={0}
              valueStyle={{ color: kwhSavings > 0 ? "#52c41a" : "#f5222d" }}
              prefix={kwhSavings > 0 ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
              suffix={<span style={{ fontSize: 14 }}>({kwhSavingsPct}%)</span>}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Statistic
              title={<Text type="secondary">Reducere CO₂</Text>}
              value={co2Reduction}
              precision={0}
              suffix="kg/an"
              valueStyle={{ color: co2Reduction > 0 ? "#52c41a" : "#f5222d" }}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Statistic
              title={<Text type="secondary">Îmbunătățire U-value</Text>}
              value={uImprovement}
              precision={2}
              suffix="W/m²K"
              valueStyle={{ color: uImprovement > 0 ? "#52c41a" : "#f5222d" }}
              prefix={<FireOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
            <Statistic
              title={<Text type="secondary">Suprafață tratată</Text>}
              value={impact.treated_area_sqm || 0}
              suffix={<span>/ {impact.total_area_sqm || 0} m²</span>}
              prefix={<CheckCircleOutlined />}
            />
            <Progress
              percent={impact.total_area_sqm ? Math.round(((impact.treated_area_sqm || 0) / impact.total_area_sqm) * 100) : 0}
              size="small"
              style={{ marginTop: 4 }}
            />
          </Card>
        </Col>
      </Row>

      {/* PRE vs POST Comparison Table */}
      <Card
        title="Comparație PRE / POST Execuție"
        size="small"
        style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)", marginBottom: 24 }}
      >
        <Table
          dataSource={comparisonRows}
          rowKey="key"
          size="small"
          pagination={false}
          columns={[
            { title: "Indicator", dataIndex: "metric", key: "metric" },
            {
              title: "PRE",
              dataIndex: "pre",
              key: "pre",
              align: "right",
              render: (v: number | undefined) => (
                <Text style={{ color: "#EF4444" }}>{v?.toLocaleString("ro-RO") || "—"}</Text>
              ),
            },
            {
              title: "POST",
              dataIndex: "post",
              key: "post",
              align: "right",
              render: (v: number | undefined) => (
                <Text style={{ color: "#3B82F6" }}>{v?.toLocaleString("ro-RO") || "—"}</Text>
              ),
            },
            {
              title: "Economie",
              dataIndex: "saving",
              key: "saving",
              align: "right",
              render: (v: number, row: { unit: string }) => (
                <Tag color={v > 0 ? "green" : v < 0 ? "red" : "default"}>
                  {v > 0 ? "↓" : v < 0 ? "↑" : "="} {Math.abs(v).toLocaleString("ro-RO")} {row.unit}
                </Tag>
              ),
            },
          ]}
        />
      </Card>

      {/* Actual vs Estimated */}
      {(impact.actual_kwh_savings != null || impact.actual_co2_reduction != null) && (
        <Card
          title="Estimat vs. Actual"
          size="small"
          style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)", marginBottom: 24 }}
        >
          <Row gutter={24}>
            <Col xs={12}>
              <Statistic
                title="Economie kWh estimată"
                value={impact.estimated_kwh_savings || 0}
                suffix="kWh"
              />
              <Statistic
                title="Economie kWh actuală"
                value={impact.actual_kwh_savings || 0}
                suffix="kWh"
                valueStyle={{ color: "#52c41a" }}
              />
            </Col>
            <Col xs={12}>
              <Statistic
                title="Reducere CO₂ estimată"
                value={impact.estimated_co2_reduction || 0}
                suffix="kg"
              />
              <Statistic
                title="Reducere CO₂ actuală"
                value={impact.actual_co2_reduction || 0}
                suffix="kg"
                valueStyle={{ color: "#52c41a" }}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* ML Dataset Info */}
      <Alert
        message="Dataset ML"
        description="Exportul ML include: suprafață totală/tratată, U-values PRE/POST, consum kWh/gaz PRE/POST, emisii CO₂, materiale folosite, cost total, durată execuție. Formatul este CSV compatibil cu modelele de regresie TRL5→TRL7."
        type="info"
        showIcon
        icon={<DatabaseOutlined />}
        style={{ marginBottom: 16 }}
      />
    </div>
  );
}
