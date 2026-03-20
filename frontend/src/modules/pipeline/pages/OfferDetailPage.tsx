import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Typography,
  Card,
  Row,
  Col,
  Tag,
  Button,
  Space,
  Table,
  Descriptions,
  Steps,
  Timeline,
  Spin,
  Popconfirm,
  App,
  Divider,
  Result,
  Tooltip,
} from "antd";
import {
  ArrowLeftOutlined,
  SendOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
  SwapOutlined,
  FilePdfOutlined,
  EditOutlined,
  ClockCircleOutlined,
  MailOutlined,
  PhoneOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import {
  useOffer,
  useOfferTimeline,
  useSubmitOffer,
  useSendOffer,
  useCreateOfferVersion,
  useConvertToContract,
} from "../hooks/useOffers";
import { offerService } from "../services/offerService";
import VersionDiffModal from "../components/VersionDiffModal";
import type { OfferStatus, OfferLineItem } from "../../../types/pipeline";
import type { ColumnsType } from "antd/es/table";

const STATUS_CONFIG: Record<
  OfferStatus,
  { color: string; label: string; step: number }
> = {
  draft: { color: "default", label: "Draft", step: 0 },
  pending_approval: { color: "processing", label: "Aprobare", step: 1 },
  approved: { color: "blue", label: "Aprobată", step: 2 },
  sent: { color: "cyan", label: "Trimisă", step: 3 },
  negotiation: { color: "orange", label: "Negociere", step: 4 },
  accepted: { color: "green", label: "Acceptată", step: 5 },
  rejected: { color: "red", label: "Refuzată", step: 5 },
  expired: { color: "red", label: "Expirată", step: 5 },
};

const TIMELINE_ICONS: Record<string, React.ReactNode> = {
  email: <MailOutlined />,
  call: <PhoneOutlined />,
  status_change: <SwapOutlined />,
  version: <CopyOutlined />,
  document: <FileTextOutlined />,
};

export default function OfferDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { message } = App.useApp();

  const [diffModalOpen, setDiffModalOpen] = useState(false);

  const { data, isLoading } = useOffer(id);
  const { data: timelineData } = useOfferTimeline(id);
  const submitOffer = useSubmitOffer();
  const sendOffer = useSendOffer();
  const createVersion = useCreateOfferVersion();
  const convertToContract = useConvertToContract();

  const offer = data?.data;
  const timeline = timelineData?.data || [];

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!offer) {
    return (
      <Result
        status="404"
        title="Ofertă negăsită"
        subTitle="Oferta nu a fost găsită sau a fost ștearsă."
        extra={
          <Button type="primary" onClick={() => navigate("/pipeline/offers")}>
            Înapoi la oferte
          </Button>
        }
      />
    );
  }

  const statusConfig = STATUS_CONFIG[offer.status];
  const isEditable = offer.status === "draft";
  const canSubmit = offer.status === "draft" && offer.line_items.length > 0;
  const canSend = offer.status === "approved";
  const canConvert = offer.status === "accepted";
  const canCreateVersion = ["sent", "negotiation"].includes(offer.status);

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("ro-RO", {
      style: "currency",
      currency: offer.currency,
    }).format(value);

  const handleGenerateDocument = async () => {
    try {
      await offerService.generateDocument(offer.id);
      message.success("Document generat.");
    } catch {
      message.error("Eroare la generare document.");
    }
  };

  const handleConvert = async () => {
    try {
      const result = await convertToContract.mutateAsync(offer.id);
      navigate(`/pipeline/contracts/${result.data.contract_id}`);
    } catch {
      // handled by mutation
    }
  };

  const handleCreateVersion = async () => {
    try {
      const result = await createVersion.mutateAsync(offer.id);
      navigate(`/pipeline/offers/${result.data.id}`);
    } catch {
      // handled by mutation
    }
  };

  const lineItemColumns: ColumnsType<OfferLineItem> = [
    {
      title: "#",
      key: "idx",
      width: 40,
      render: (_: unknown, __: unknown, idx: number) => idx + 1,
    },
    {
      title: "Descriere",
      dataIndex: "description",
      key: "description",
    },
    {
      title: "UM",
      dataIndex: "unit_of_measure",
      key: "um",
      width: 70,
    },
    {
      title: "Cantitate",
      dataIndex: "quantity",
      key: "quantity",
      width: 90,
      align: "right",
    },
    {
      title: "Preț unitar",
      dataIndex: "unit_price",
      key: "unit_price",
      width: 120,
      align: "right",
      render: (v: number) => formatCurrency(v),
    },
    {
      title: "Discount",
      dataIndex: "discount_percent",
      key: "discount",
      width: 90,
      align: "right",
      render: (v: number) => (v ? `${v}%` : "—"),
    },
    {
      title: "Total",
      dataIndex: "total_price",
      key: "total",
      width: 130,
      align: "right",
      render: (v: number) => (
        <Typography.Text strong>{formatCurrency(v)}</Typography.Text>
      ),
    },
  ];

  // Status pipeline step items
  const statusSteps = [
    { title: "Draft" },
    { title: "Aprobare" },
    { title: "Aprobată" },
    { title: "Trimisă" },
    { title: "Negociere" },
    {
      title:
        offer.status === "rejected"
          ? "Refuzată"
          : offer.status === "expired"
            ? "Expirată"
            : "Acceptată",
    },
  ];

  return (
    <>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate("/pipeline/offers")}
          >
            Oferte
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            {offer.offer_number}
          </Typography.Title>
          <Tag color={statusConfig.color}>{statusConfig.label}</Tag>
          {offer.version > 1 && <Tag>v{offer.version}</Tag>}
        </Space>

        <Space>
          {isEditable && (
            <Button
              icon={<EditOutlined />}
              onClick={() =>
                navigate(
                  `/pipeline/offers/new?contact_id=${offer.contact_id}&opportunity_id=${offer.opportunity_id || ""}`
                )
              }
            >
              Editează
            </Button>
          )}
          {canSubmit && (
            <Popconfirm
              title="Trimiteți oferta pentru aprobare?"
              onConfirm={() => submitOffer.mutate(offer.id)}
              okText="Da"
              cancelText="Nu"
            >
              <Button type="primary" loading={submitOffer.isPending}>
                Trimite pentru aprobare
              </Button>
            </Popconfirm>
          )}
          {canSend && (
            <Button
              type="primary"
              icon={<SendOutlined />}
              loading={sendOffer.isPending}
              onClick={() => sendOffer.mutate(offer.id)}
            >
              Trimite clientului
            </Button>
          )}
          {canCreateVersion && (
            <Button
              icon={<CopyOutlined />}
              loading={createVersion.isPending}
              onClick={handleCreateVersion}
            >
              Versiune nouă
            </Button>
          )}
          {canConvert && (
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              style={{ background: "#52c41a" }}
              loading={convertToContract.isPending}
              onClick={handleConvert}
            >
              Convertește în Contract
            </Button>
          )}
          <Button icon={<FilePdfOutlined />} onClick={handleGenerateDocument}>
            Export PDF
          </Button>
          {offer.version > 1 && (
            <Button icon={<SwapOutlined />} onClick={() => setDiffModalOpen(true)}>
              Compară versiuni
            </Button>
          )}
        </Space>
      </Row>

      {/* Status Pipeline */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Steps
          current={statusConfig.step}
          status={
            offer.status === "rejected" || offer.status === "expired"
              ? "error"
              : undefined
          }
          items={statusSteps}
          size="small"
        />
      </Card>

      <Row gutter={[16, 16]}>
        {/* Main content */}
        <Col xs={24} lg={16}>
          {/* Offer details */}
          <Card title="Detalii ofertă" style={{ marginBottom: 16 }}>
            <Descriptions column={{ xs: 1, sm: 2 }} size="small">
              <Descriptions.Item label="Titlu">{offer.title}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={statusConfig.color}>{statusConfig.label}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Versiune">v{offer.version}</Descriptions.Item>
              <Descriptions.Item label="Monedă">{offer.currency}</Descriptions.Item>
              <Descriptions.Item label="Valabilitate">
                {offer.validity_days} zile
              </Descriptions.Item>
              {offer.valid_until && (
                <Descriptions.Item label="Valabilă până la">
                  {new Date(offer.valid_until).toLocaleDateString("ro-RO")}
                </Descriptions.Item>
              )}
              {offer.sent_at && (
                <Descriptions.Item label="Trimisă la">
                  {new Date(offer.sent_at).toLocaleDateString("ro-RO")}
                </Descriptions.Item>
              )}
              {offer.accepted_at && (
                <Descriptions.Item label="Acceptată la">
                  {new Date(offer.accepted_at).toLocaleDateString("ro-RO")}
                </Descriptions.Item>
              )}
              {offer.next_follow_up && (
                <Descriptions.Item label="Următor follow-up">
                  <Tag icon={<ClockCircleOutlined />} color="warning">
                    {new Date(offer.next_follow_up).toLocaleDateString("ro-RO")}
                  </Tag>
                </Descriptions.Item>
              )}
              {offer.description && (
                <Descriptions.Item label="Descriere" span={2}>
                  {offer.description}
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>

          {/* Line items */}
          <Card
            title="Produse și servicii"
            style={{ marginBottom: 16 }}
            extra={
              !isEditable && (
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  Read-only — oferta a fost trimisă
                </Typography.Text>
              )
            }
          >
            <Table<OfferLineItem>
              rowKey="id"
              columns={lineItemColumns}
              dataSource={offer.line_items}
              pagination={false}
              size="small"
            />

            <Divider />

            <Row justify="end">
              <Col>
                <Descriptions column={1} size="small" style={{ width: 300 }}>
                  <Descriptions.Item label="Subtotal">
                    {formatCurrency(offer.subtotal)}
                  </Descriptions.Item>
                  {offer.discount_percent > 0 && (
                    <Descriptions.Item label={`Discount (${offer.discount_percent}%)`}>
                      <Typography.Text type="danger">
                        -{formatCurrency(offer.discount_amount)}
                      </Typography.Text>
                    </Descriptions.Item>
                  )}
                  <Descriptions.Item label="TVA">
                    {formatCurrency(offer.vat_amount)}
                  </Descriptions.Item>
                  <Descriptions.Item
                    label={<Typography.Text strong>TOTAL</Typography.Text>}
                  >
                    <Typography.Title level={4} style={{ margin: 0 }}>
                      {formatCurrency(offer.total_amount)}
                    </Typography.Title>
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          {/* Terms & Conditions */}
          {offer.terms_and_conditions && (
            <Card title="Termeni și Condiții" style={{ marginBottom: 16 }}>
              <Typography.Paragraph style={{ whiteSpace: "pre-line" }}>
                {offer.terms_and_conditions}
              </Typography.Paragraph>
            </Card>
          )}
        </Col>

        {/* Sidebar — Timeline & Actions */}
        <Col xs={24} lg={8}>
          {/* Follow-up alert */}
          {offer.status === "negotiation" && offer.next_follow_up && (
            <Card
              size="small"
              style={{
                marginBottom: 16,
                background: "#fff7e6",
                border: "1px solid #ffd591",
              }}
            >
              <Space>
                <ClockCircleOutlined style={{ color: "#fa8c16" }} />
                <div>
                  <Typography.Text strong>Follow-up programat</Typography.Text>
                  <br />
                  <Typography.Text type="secondary">
                    {new Date(offer.next_follow_up).toLocaleDateString("ro-RO")}
                    {" · "}Follow-up #{offer.follow_up_count + 1}
                  </Typography.Text>
                </div>
              </Space>
            </Card>
          )}

          {/* Quick actions */}
          <Card title="Acțiuni" size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: "100%" }}>
              {offer.status === "negotiation" && (
                <>
                  <Tooltip title="Marchează oferta ca acceptată">
                    <Button
                      block
                      icon={<CheckCircleOutlined />}
                      style={{ color: "#52c41a", borderColor: "#52c41a" }}
                      onClick={async () => {
                        try {
                          await offerService.updateStatus(offer.id, "accepted");
                          message.success("Ofertă acceptată!");
                          window.location.reload();
                        } catch {
                          message.error("Eroare la actualizare status.");
                        }
                      }}
                    >
                      Marchează Acceptată
                    </Button>
                  </Tooltip>
                  <Button
                    block
                    danger
                    icon={<CloseCircleOutlined />}
                    onClick={async () => {
                      try {
                        await offerService.updateStatus(offer.id, "rejected");
                        message.success("Ofertă refuzată.");
                        window.location.reload();
                      } catch {
                        message.error("Eroare la actualizare status.");
                      }
                    }}
                  >
                    Marchează Refuzată
                  </Button>
                </>
              )}
            </Space>
          </Card>

          {/* Timeline */}
          <Card title="Istoric activități" size="small">
            {timeline.length > 0 ? (
              <Timeline
                items={timeline.map((event) => ({
                  dot: TIMELINE_ICONS[event.event_type],
                  children: (
                    <div>
                      <Typography.Text>{event.description}</Typography.Text>
                      <br />
                      <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                        {event.user_name && `${event.user_name} · `}
                        {new Date(event.created_at).toLocaleString("ro-RO", {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </Typography.Text>
                    </div>
                  ),
                }))}
              />
            ) : (
              <Typography.Text type="secondary">
                Nicio activitate înregistrată.
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Version Diff Modal */}
      {diffModalOpen && (
        <VersionDiffModal
          open={diffModalOpen}
          onClose={() => setDiffModalOpen(false)}
          offerId={offer.id}
          currentVersion={offer.version}
        />
      )}
    </>
  );
}
