/**
 * E-001 — Dashboard Principal (parțial)
 * F-codes: F133 (Executive Dashboard), F058 (Sales KPIs)
 */
import { Card, Col, Row, Statistic, Typography, Spin, Space, Button } from "antd";
import {
  TeamOutlined,
  FunnelPlotOutlined,
  DollarOutlined,
  TrophyOutlined,
  RiseOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { pipelineService } from "../../pipeline/services/pipelineService";

const { Title } = Typography;

export default function DashboardPage() {
  const navigate = useNavigate();
  const { data: kpiData, isLoading } = useQuery({
    queryKey: ["sales-kpi"],
    queryFn: () => pipelineService.getSalesKPI(),
  });

  const kpi = kpiData?.data;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          Dashboard Principal
        </Title>
        <Space>
          <Button onClick={() => navigate("/pipeline/board")}>
            Pipeline Kanban
          </Button>
          <Button onClick={() => navigate("/pipeline/dashboard")}>
            Sales Dashboard
          </Button>
        </Space>
      </Row>

      {isLoading ? (
        <Spin style={{ display: "block", margin: "40px auto" }} />
      ) : (
        <>
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/crm/contacts")}>
                <Statistic
                  title="Contacte Active"
                  value={kpi?.active_contacts ?? 0}
                  prefix={<TeamOutlined />}
                  suffix={`/ ${kpi?.total_contacts ?? 0}`}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/pipeline/board")}>
                <Statistic
                  title="Oportunități Deschise"
                  value={kpi?.open_opportunities ?? 0}
                  prefix={<FunnelPlotOutlined />}
                  suffix={`/ ${kpi?.total_opportunities ?? 0}`}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/pipeline/dashboard")}>
                <Statistic
                  title="Valoare Pipeline"
                  value={kpi?.pipeline_value ?? 0}
                  prefix={<DollarOutlined />}
                  suffix={kpi?.currency ?? "RON"}
                  valueStyle={{ color: "#1677ff" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Pipeline Ponderat"
                  value={kpi?.weighted_pipeline_value ?? 0}
                  prefix={<DollarOutlined />}
                  suffix={kpi?.currency ?? "RON"}
                  valueStyle={{ color: "#722ed1" }}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Câștigate"
                  value={kpi?.won_opportunities ?? 0}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Rată Conversie"
                  value={kpi?.conversion_rate ?? 0}
                  prefix={<RiseOutlined />}
                  suffix="%"
                  valueStyle={{
                    color:
                      (kpi?.conversion_rate ?? 0) >= 30 ? "#52c41a" : "#faad14",
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Oferte"
                  value={kpi?.total_offers ?? 0}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Contracte Active"
                  value={kpi?.active_contracts ?? 0}
                  suffix={`/ ${kpi?.total_contracts ?? 0}`}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}
    </>
  );
}
