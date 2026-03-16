import { Card, Col, Row, Statistic, Typography } from "antd";
import {
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";

export default function DashboardPage() {
  return (
    <>
      <Typography.Title level={3}>Dashboard Principal</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic title="Contacte" value={0} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Oportunități"
              value={0}
              prefix={<FunnelPlotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Proiecte Active"
              value={0}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Energie (kWh)"
              value={0}
              prefix={<ThunderboltOutlined />}
              suffix="economisiți"
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}
