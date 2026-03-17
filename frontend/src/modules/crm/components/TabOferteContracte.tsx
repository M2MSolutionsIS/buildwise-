import { Typography, Table, Tag, Space, Empty, Card, Statistic, Row, Col } from "antd";
import {
  DollarOutlined,
  FileTextOutlined,
  TrophyOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";

interface Offer {
  id: string;
  offer_number: string;
  date: string;
  amount: number;
  currency: string;
  status: string;
  validity_days: number;
}

interface Contract {
  id: string;
  contract_number: string;
  linked_offer?: string;
  date_signed: string;
  amount: number;
  currency: string;
  project?: string;
  status: string;
  end_date?: string;
}

const OFFER_STATUS_COLORS: Record<string, string> = {
  draft: "default",
  sent: "processing",
  viewed: "processing",
  accepted: "success",
  expired: "warning",
  rejected: "error",
};

const CONTRACT_STATUS_COLORS: Record<string, string> = {
  active: "success",
  suspended: "warning",
  completed: "default",
  terminated: "error",
};

interface Props {
  contactId: string;
}

export default function TabOferteContracte({ contactId: _contactId }: Props) {
  // Offers & Contracts API - will be populated when Pipeline module is implemented
  const offers: Offer[] = [];
  const contracts: Contract[] = [];

  const offerColumns: ColumnsType<Offer> = [
    { title: "Nr. ofertă", dataIndex: "offer_number", key: "offer_number" },
    {
      title: "Data",
      dataIndex: "date",
      key: "date",
      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
    },
    {
      title: "Valoare",
      dataIndex: "amount",
      key: "amount",
      render: (v: number, r: Offer) => `${v?.toLocaleString("ro-RO")} ${r.currency || "RON"}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (s: string) => (
        <Tag color={OFFER_STATUS_COLORS[s] || "default"}>
          {s?.charAt(0).toUpperCase() + s?.slice(1)}
        </Tag>
      ),
    },
  ];

  const contractColumns: ColumnsType<Contract> = [
    { title: "Nr. contract", dataIndex: "contract_number", key: "contract_number" },
    {
      title: "Data semnare",
      dataIndex: "date_signed",
      key: "date_signed",
      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
    },
    {
      title: "Valoare",
      dataIndex: "amount",
      key: "amount",
      render: (v: number, r: Contract) => `${v?.toLocaleString("ro-RO")} ${r.currency || "RON"}`,
    },
    {
      title: "Proiect",
      dataIndex: "project",
      key: "project",
      render: (p: string) => p || "—",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (s: string) => (
        <Tag color={CONTRACT_STATUS_COLORS[s] || "default"}>
          {s?.charAt(0).toUpperCase() + s?.slice(1)}
        </Tag>
      ),
    },
  ];

  const hasData = offers.length > 0 || contracts.length > 0;

  return (
    <>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Valoare oferte"
              value={offers.reduce((sum, o) => sum + (o.amount || 0), 0)}
              prefix={<DollarOutlined />}
              suffix="RON"
            />
          </Card>
        </Col>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Valoare contracte"
              value={contracts.reduce((sum, c) => sum + (c.amount || 0), 0)}
              prefix={<FileTextOutlined />}
              suffix="RON"
            />
          </Card>
        </Col>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Rată conversie"
              value={offers.length > 0 ? Math.round((contracts.length / offers.length) * 100) : 0}
              prefix={<TrophyOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      {!hasData ? (
        <Empty description={
          <Typography.Text type="secondary">
            Nicio ofertă sau contract. Ofertele vor apărea aici după crearea lor din modulul Pipeline.
          </Typography.Text>
        } />
      ) : (
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div>
            <Typography.Title level={5}>Oferte</Typography.Title>
            <Table<Offer>
              rowKey="id"
              columns={offerColumns}
              dataSource={offers}
              pagination={false}
              size="small"
            />
          </div>
          <div>
            <Typography.Title level={5}>Contracte</Typography.Title>
            <Table<Contract>
              rowKey="id"
              columns={contractColumns}
              dataSource={contracts}
              pagination={false}
              size="small"
            />
          </div>
        </Space>
      )}
    </>
  );
}
