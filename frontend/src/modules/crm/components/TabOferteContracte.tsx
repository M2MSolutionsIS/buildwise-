/**
 * Tab Oferte & Contracte — Contact Detail (E-003.5)
 * Connected to real API /api/v1/pipeline/offers
 * F-codes: F019, F027, F029
 */
import { useNavigate } from "react-router-dom";
import { Typography, Table, Tag, Space, Empty, Card, Statistic, Row, Col, Button } from "antd";
import {
  DollarOutlined,
  FileTextOutlined,
  TrophyOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { offerService } from "../../pipeline/services/offerService";
import type { OfferListItem, OfferStatus } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const OFFER_STATUS_COLORS: Record<string, string> = {
  DRAFT: "default",
  PENDING_APPROVAL: "processing",
  APPROVED: "cyan",
  SENT: "blue",
  NEGOTIATION: "orange",
  ACCEPTED: "success",
  REJECTED: "error",
  EXPIRED: "default",
};

const OFFER_STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  PENDING_APPROVAL: "Așteptare aprobare",
  APPROVED: "Aprobată",
  SENT: "Trimisă",
  NEGOTIATION: "Negociere",
  ACCEPTED: "Acceptată",
  REJECTED: "Refuzată",
  EXPIRED: "Expirată",
};

interface Props {
  contactId: string;
}

export default function TabOferteContracte({ contactId }: Props) {
  const navigate = useNavigate();

  // Fetch offers for this contact
  const { data: offersData, isLoading } = useQuery({
    queryKey: ["offers", { contact_id: contactId }],
    queryFn: () => offerService.list({ contact_id: contactId, per_page: 50 }),
    enabled: !!contactId,
  });

  const offers = offersData?.data || [];

  // Compute stats
  const totalOffersValue = offers.reduce((sum, o) => sum + (o.total_amount || 0), 0);
  const acceptedOffers = offers.filter((o) => o.status === "ACCEPTED");
  const conversionRate = offers.length > 0 ? Math.round((acceptedOffers.length / offers.length) * 100) : 0;
  const acceptedValue = acceptedOffers.reduce((sum, o) => sum + (o.total_amount || 0), 0);

  const offerColumns: ColumnsType<OfferListItem> = [
    {
      title: "Nr. ofertă",
      dataIndex: "offer_number",
      key: "offer_number",
      render: (val: string, record) => (
        <a onClick={() => navigate(`/pipeline/offers/${record.id}`)}>{val}</a>
      ),
    },
    {
      title: "Titlu",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
    },
    {
      title: "Versiune",
      dataIndex: "version",
      key: "version",
      width: 70,
      render: (v: number) => `v${v}`,
    },
    {
      title: "Data",
      dataIndex: "created_at",
      key: "date",
      width: 100,
      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
    },
    {
      title: "Valoare",
      dataIndex: "total_amount",
      key: "amount",
      width: 130,
      render: (v: number, r) =>
        `${v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} ${r.currency || "RON"}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 140,
      render: (s: OfferStatus) => (
        <Tag color={OFFER_STATUS_COLORS[s] || "default"}>
          {OFFER_STATUS_LABELS[s] || s}
        </Tag>
      ),
    },
  ];

  return (
    <>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Valoare oferte"
              value={totalOffersValue}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="RON"
            />
          </Card>
        </Col>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Valoare acceptate"
              value={acceptedValue}
              precision={2}
              prefix={<FileTextOutlined />}
              suffix="RON"
            />
          </Card>
        </Col>
        <Col xs={8}>
          <Card size="small">
            <Statistic
              title="Rată conversie"
              value={conversionRate}
              prefix={<TrophyOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate(`/pipeline/offers/new?contact_id=${contactId}`)}
        >
          Ofertă nouă
        </Button>
      </Space>

      {offers.length === 0 && !isLoading ? (
        <Empty
          description={
            <Typography.Text type="secondary">
              Nicio ofertă pentru acest contact. Creează prima ofertă folosind butonul de mai sus.
            </Typography.Text>
          }
        />
      ) : (
        <Table<OfferListItem>
          rowKey="id"
          columns={offerColumns}
          dataSource={offers}
          loading={isLoading}
          pagination={false}
          size="small"
          onRow={(record) => ({
            onClick: () => navigate(`/pipeline/offers/${record.id}`),
            style: { cursor: "pointer" },
          })}
        />
      )}
    </>
  );
}
