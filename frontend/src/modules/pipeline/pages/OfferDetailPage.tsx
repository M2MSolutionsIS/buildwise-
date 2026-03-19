/**
 * E-006 — Offer Detail / Lifecycle
 * F-codes: F027 (Status tracking), F028 (Approval flow), F029 (Analytics/Versions), F049 (Quick quote)
 */
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Typography,
  Table,
  Steps,
  Timeline,
  Tabs,
  Row,
  Col,
  Statistic,
  Dropdown,
  Modal,
  Input,
  message,
  Spin,
  Alert,
  Divider,
  Popconfirm,
} from "antd";
import {
  ArrowLeftOutlined,
  SendOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
  FilePdfOutlined,
  HistoryOutlined,
  EditOutlined,
  MoreOutlined,
  ExclamationCircleOutlined,
  DiffOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { offerService } from "../services/offerService";
import { contactService } from "../../../services/contactService";
import VersionDiffModal from "../components/VersionDiffModal";
import type { Offer, OfferLineItem, OfferStatus } from "../../../types";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const STATUS_CONFIG: Record<OfferStatus, { color: string; label: string; step: number }> = {
  DRAFT: { color: "default", label: "Draft", step: 0 },
  PENDING_APPROVAL: { color: "processing", label: "Așteptare aprobare", step: 1 },
  APPROVED: { color: "cyan", label: "Aprobată", step: 2 },
  SENT: { color: "blue", label: "Trimisă", step: 3 },
  NEGOTIATION: { color: "orange", label: "Negociere", step: 4 },
  ACCEPTED: { color: "green", label: "Acceptată", step: 5 },
  REJECTED: { color: "red", label: "Refuzată", step: 5 },
  EXPIRED: { color: "default", label: "Expirată", step: 5 },
};

export default function OfferDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [versionDiffOpen, setVersionDiffOpen] = useState(false);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");

  // Fetch offer
  const { data: offerData, isLoading } = useQuery({
    queryKey: ["offer", id],
    queryFn: () => offerService.get(id!),
    enabled: !!id,
  });

  const offer = offerData?.data;

  // Fetch contact
  const { data: contactData } = useQuery({
    queryKey: ["contact", offer?.contact_id],
    queryFn: () => contactService.get(offer!.contact_id),
    enabled: !!offer?.contact_id,
  });

  const contact = contactData?.data;

  // Fetch versions (F026)
  const { data: versionsData } = useQuery({
    queryKey: ["offer-versions", id],
    queryFn: () => offerService.listVersions(id!),
    enabled: !!id,
  });

  const versions = versionsData?.data || [];

  // Mutations
  const invalidateOffer = () => {
    queryClient.invalidateQueries({ queryKey: ["offer", id] });
    queryClient.invalidateQueries({ queryKey: ["offers"] });
  };

  // F028 — Submit for approval
  const submitMutation = useMutation({
    mutationFn: () => offerService.submit(id!),
    onSuccess: () => { message.success("Oferta trimisă pentru aprobare"); invalidateOffer(); },
    onError: () => message.error("Eroare la trimiterea pentru aprobare"),
  });

  // F028 — Approve
  const approveMutation = useMutation({
    mutationFn: (decision: { approved: boolean; comment?: string }) =>
      offerService.approve(id!, decision),
    onSuccess: (_, vars) => {
      message.success(vars.approved ? "Ofertă aprobată" : "Ofertă respinsă");
      invalidateOffer();
      setRejectModalOpen(false);
    },
    onError: () => message.error("Eroare la procesarea deciziei"),
  });

  // F027 — Send to client
  const sendMutation = useMutation({
    mutationFn: () => offerService.send(id!),
    onSuccess: () => { message.success("Oferta trimisă clientului"); invalidateOffer(); },
    onError: () => message.error("Eroare la trimiterea ofertei"),
  });

  // F027 — Update status
  const statusMutation = useMutation({
    mutationFn: (params: { status: string; reason?: string }) =>
      offerService.updateStatus(id!, params.status, params.reason),
    onSuccess: () => { message.success("Status actualizat"); invalidateOffer(); },
    onError: () => message.error("Eroare la actualizarea statusului"),
  });

  // F026 — Create new version
  const versionMutation = useMutation({
    mutationFn: () => offerService.createVersion(id!),
    onSuccess: (res) => {
      message.success(`Versiune v${res.data.version} creată`);
      navigate(`/pipeline/offers/${res.data.id}`);
    },
    onError: () => message.error("Eroare la crearea versiunii"),
  });

  // F023 — Generate document
  const generateMutation = useMutation({
    mutationFn: () => offerService.generateDocument(id!),
    onSuccess: () => message.success("Document generat"),
    onError: () => message.error("Eroare la generarea documentului"),
  });

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (!offer) return <Alert type="error" message="Oferta nu a fost găsită" showIcon />;

  const statusCfg = STATUS_CONFIG[offer.status] || STATUS_CONFIG.DRAFT;
  const isDraft = offer.status === "DRAFT";
  const isSent = offer.status === "SENT";
  const isAccepted = offer.status === "ACCEPTED";
  const isNegotiation = offer.status === "NEGOTIATION";
  const isEditable = isDraft;

  // Status pipeline steps (F027)
  const pipelineSteps = [
    { title: "Draft" },
    { title: "Aprobare" },
    { title: "Aprobată" },
    { title: "Trimisă" },
    { title: "Negociere" },
    { title: offer.status === "REJECTED" ? "Refuzată" : offer.status === "EXPIRED" ? "Expirată" : "Acceptată" },
  ];

  // Action dropdown items
  const actionItems = [
    isDraft && {
      key: "edit",
      icon: <EditOutlined />,
      label: "Editează în Builder",
      onClick: () => navigate(`/pipeline/offers/new?edit=${id}`),
    },
    isDraft && {
      key: "submit",
      icon: <SendOutlined />,
      label: "Trimite pentru aprobare",
      onClick: () => submitMutation.mutate(),
    },
    (offer.status === "APPROVED" || isDraft) && {
      key: "send",
      icon: <SendOutlined />,
      label: "Trimite la client",
      onClick: () => sendMutation.mutate(),
    },
    (isSent || isNegotiation) && {
      key: "negotiation",
      icon: <ExclamationCircleOutlined />,
      label: "Marchează Negociere",
      onClick: () => statusMutation.mutate({ status: "NEGOTIATION" }),
    },
    (isSent || isNegotiation) && {
      key: "accept",
      icon: <CheckCircleOutlined />,
      label: "Marchează Acceptată",
      onClick: () => statusMutation.mutate({ status: "ACCEPTED" }),
    },
    (isSent || isNegotiation) && {
      key: "reject",
      icon: <CloseCircleOutlined />,
      label: "Marchează Refuzată",
      danger: true,
      onClick: () => setRejectModalOpen(true),
    },
    {
      key: "version",
      icon: <CopyOutlined />,
      label: "Creează versiune nouă",
      onClick: () => versionMutation.mutate(),
    },
    {
      key: "pdf",
      icon: <FilePdfOutlined />,
      label: "Generează PDF",
      onClick: () => generateMutation.mutate(),
    },
  ].filter(Boolean);

  // Line items columns
  const lineItemColumns = [
    { title: "#", render: (_: unknown, __: unknown, i: number) => i + 1, width: 40 },
    { title: "Descriere", dataIndex: "description", key: "description" },
    { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 60 },
    {
      title: "Cantitate",
      dataIndex: "quantity",
      key: "qty",
      width: 90,
      render: (v: number) => v?.toLocaleString("ro-RO"),
    },
    {
      title: `Preț unitar (${offer.currency})`,
      dataIndex: "unit_price",
      key: "price",
      width: 130,
      render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Disc. %",
      dataIndex: "discount_percent",
      key: "discount",
      width: 70,
      render: (v: number) => (v > 0 ? `${v}%` : "—"),
    },
    {
      title: `Total (${offer.currency})`,
      dataIndex: "total_price",
      key: "total",
      width: 130,
      render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
  ];

  return (
    <div>
      {/* Header */}
      <Space style={{ marginBottom: 16 }} align="start">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/pipeline/offers")}>
          Înapoi la oferte
        </Button>
      </Space>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <Space align="center">
            <Title level={3} style={{ margin: 0 }}>
              {offer.offer_number}
            </Title>
            <Tag color={statusCfg.color} style={{ fontSize: 14, padding: "2px 12px" }}>
              {statusCfg.label}
            </Tag>
            {offer.version > 1 && <Tag>v{offer.version}</Tag>}
          </Space>
          <br />
          <Text type="secondary">{offer.title}</Text>
          {contact && (
            <>
              {" — "}
              <a onClick={() => navigate(`/crm/contacts/${contact.id}`)}>{contact.company_name}</a>
            </>
          )}
        </Col>
        <Col>
          <Space>
            {isAccepted && (
              <Button type="primary" icon={<CheckCircleOutlined />}>
                Convertește → Contract
              </Button>
            )}
            <Dropdown menu={{ items: actionItems as never[] }} trigger={["click"]}>
              <Button icon={<MoreOutlined />}>Acțiuni</Button>
            </Dropdown>
          </Space>
        </Col>
      </Row>

      {/* Status pipeline (F027) */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Steps
          current={statusCfg.step}
          status={offer.status === "REJECTED" ? "error" : undefined}
          items={pipelineSteps}
          size="small"
        />
      </Card>

      {/* Follow-up alert */}
      {isNegotiation && offer.next_follow_up && (
        <Alert
          type="warning"
          message={`Follow-up programat: ${new Date(offer.next_follow_up).toLocaleDateString("ro-RO")}`}
          description="Oferta este în negociere. Contactează clientul pentru a avansa."
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Main content tabs */}
      <Tabs
        defaultActiveKey="details"
        items={[
          {
            key: "details",
            label: "Detalii ofertă",
            children: (
              <Row gutter={[16, 16]}>
                {/* Stats cards */}
                <Col xs={8}>
                  <Card size="small">
                    <Statistic
                      title="Subtotal"
                      value={offer.subtotal}
                      precision={2}
                      suffix={offer.currency}
                    />
                  </Card>
                </Col>
                <Col xs={8}>
                  <Card size="small">
                    <Statistic
                      title="TVA"
                      value={offer.vat_amount}
                      precision={2}
                      suffix={offer.currency}
                    />
                  </Card>
                </Col>
                <Col xs={8}>
                  <Card size="small">
                    <Statistic
                      title="TOTAL"
                      value={offer.total_amount}
                      precision={2}
                      suffix={offer.currency}
                      valueStyle={{ color: "#1677ff", fontWeight: "bold" }}
                    />
                  </Card>
                </Col>

                {/* Offer info */}
                <Col span={24}>
                  <Card size="small" title="Informații ofertă">
                    <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
                      <Descriptions.Item label="Nr. ofertă">{offer.offer_number}</Descriptions.Item>
                      <Descriptions.Item label="Versiune">v{offer.version}</Descriptions.Item>
                      <Descriptions.Item label="Status">
                        <Tag color={statusCfg.color}>{statusCfg.label}</Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="Monedă">{offer.currency}</Descriptions.Item>
                      <Descriptions.Item label="Valabilitate">{offer.validity_days} zile</Descriptions.Item>
                      <Descriptions.Item label="Expiră la">
                        {offer.valid_until
                          ? new Date(offer.valid_until).toLocaleDateString("ro-RO")
                          : "—"}
                      </Descriptions.Item>
                      <Descriptions.Item label="Creat la">
                        {new Date(offer.created_at).toLocaleDateString("ro-RO")}
                      </Descriptions.Item>
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
                      {offer.rejected_at && (
                        <Descriptions.Item label="Respinsă la">
                          {new Date(offer.rejected_at).toLocaleDateString("ro-RO")}
                        </Descriptions.Item>
                      )}
                    </Descriptions>
                    {offer.description && (
                      <>
                        <Divider style={{ margin: "8px 0" }} />
                        <Paragraph type="secondary">{offer.description}</Paragraph>
                      </>
                    )}
                    {offer.rejection_reason && (
                      <Alert
                        type="error"
                        message="Motiv respingere"
                        description={offer.rejection_reason}
                        style={{ marginTop: 8 }}
                      />
                    )}
                  </Card>
                </Col>

                {/* Line items */}
                <Col span={24}>
                  <Card size="small" title="Produse și servicii">
                    <Table<OfferLineItem>
                      rowKey="id"
                      columns={lineItemColumns}
                      dataSource={offer.line_items || []}
                      pagination={false}
                      size="small"
                      footer={() => (
                        <Row justify="end">
                          <Col>
                            <Space direction="vertical" size={2} style={{ textAlign: "right" }}>
                              <Text>
                                Subtotal: {offer.subtotal?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                {offer.currency}
                              </Text>
                              {offer.discount_amount > 0 && (
                                <Text type="secondary">
                                  Discount: -{offer.discount_amount?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                  {offer.currency}
                                </Text>
                              )}
                              <Text type="secondary">
                                TVA: {offer.vat_amount?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                {offer.currency}
                              </Text>
                              <Title level={5} style={{ margin: 0 }}>
                                TOTAL: {offer.total_amount?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                {offer.currency}
                              </Title>
                            </Space>
                          </Col>
                        </Row>
                      )}
                    />
                  </Card>
                </Col>

                {/* T&C */}
                {offer.terms_and_conditions && (
                  <Col span={24}>
                    <Card size="small" title="Termeni și condiții">
                      <Paragraph style={{ whiteSpace: "pre-wrap", fontSize: 13 }}>
                        {offer.terms_and_conditions}
                      </Paragraph>
                    </Card>
                  </Col>
                )}
              </Row>
            ),
          },
          {
            key: "versions",
            label: (
              <Space>
                <HistoryOutlined />
                Versiuni ({versions.length || offer.version})
              </Space>
            ),
            children: (
              <Card size="small">
                {versions.length > 1 && (
                  <Button
                    icon={<DiffOutlined />}
                    onClick={() => setVersionDiffOpen(true)}
                    style={{ marginBottom: 16 }}
                  >
                    Compară versiuni
                  </Button>
                )}

                <Timeline
                  items={
                    versions.length > 0
                      ? versions.map((v: Offer) => ({
                          color: v.id === id ? "blue" : "gray",
                          children: (
                            <Space direction="vertical" size={0}>
                              <Space>
                                <Text strong>v{v.version}</Text>
                                <Tag color={STATUS_CONFIG[v.status]?.color || "default"}>
                                  {STATUS_CONFIG[v.status]?.label || v.status}
                                </Tag>
                                {v.id === id && <Tag color="blue">Curentă</Tag>}
                              </Space>
                              <Text type="secondary">
                                {new Date(v.created_at).toLocaleDateString("ro-RO")} —{" "}
                                {v.total_amount?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                {v.currency}
                              </Text>
                              {v.id !== id && (
                                <a onClick={() => navigate(`/pipeline/offers/${v.id}`)}>
                                  Vezi această versiune
                                </a>
                              )}
                            </Space>
                          ),
                        }))
                      : [
                          {
                            color: "blue",
                            children: (
                              <Space direction="vertical" size={0}>
                                <Text strong>v{offer.version}</Text>
                                <Tag color={statusCfg.color}>{statusCfg.label}</Tag>
                                <Text type="secondary">
                                  {new Date(offer.created_at).toLocaleDateString("ro-RO")} —{" "}
                                  {offer.total_amount?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                                  {offer.currency}
                                </Text>
                              </Space>
                            ),
                          },
                        ]
                  }
                />

                <Divider />
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => versionMutation.mutate()}
                  loading={versionMutation.isPending}
                >
                  Creează versiune nouă (v{offer.version + 1})
                </Button>
              </Card>
            ),
          },
          {
            key: "timeline",
            label: "Activitate",
            children: (
              <Card size="small">
                <Timeline
                  items={[
                    {
                      color: "green",
                      children: (
                        <Space direction="vertical" size={0}>
                          <Text strong>Ofertă creată</Text>
                          <Text type="secondary">
                            {new Date(offer.created_at).toLocaleString("ro-RO")}
                          </Text>
                        </Space>
                      ),
                    },
                    ...(offer.sent_at
                      ? [
                          {
                            color: "blue" as const,
                            children: (
                              <Space direction="vertical" size={0}>
                                <Text strong>Trimisă la client</Text>
                                <Text type="secondary">
                                  {new Date(offer.sent_at).toLocaleString("ro-RO")}
                                </Text>
                              </Space>
                            ),
                          },
                        ]
                      : []),
                    ...(offer.accepted_at
                      ? [
                          {
                            color: "green" as const,
                            children: (
                              <Space direction="vertical" size={0}>
                                <Text strong>Acceptată de client</Text>
                                <Text type="secondary">
                                  {new Date(offer.accepted_at).toLocaleString("ro-RO")}
                                </Text>
                              </Space>
                            ),
                          },
                        ]
                      : []),
                    ...(offer.rejected_at
                      ? [
                          {
                            color: "red" as const,
                            children: (
                              <Space direction="vertical" size={0}>
                                <Text strong>Refuzată</Text>
                                {offer.rejection_reason && (
                                  <Text type="secondary">Motiv: {offer.rejection_reason}</Text>
                                )}
                                <Text type="secondary">
                                  {new Date(offer.rejected_at).toLocaleString("ro-RO")}
                                </Text>
                              </Space>
                            ),
                          },
                        ]
                      : []),
                  ]}
                />
              </Card>
            ),
          },
        ]}
      />

      {/* Reject modal */}
      <Modal
        title="Respinge oferta"
        open={rejectModalOpen}
        onCancel={() => setRejectModalOpen(false)}
        onOk={() =>
          statusMutation.mutate({ status: "REJECTED", reason: rejectionReason })
        }
        okText="Respinge"
        okButtonProps={{ danger: true }}
      >
        <TextArea
          rows={3}
          placeholder="Motivul respingerii (opțional)..."
          value={rejectionReason}
          onChange={(e) => setRejectionReason(e.target.value)}
        />
      </Modal>

      {/* Version diff modal (F029) */}
      <VersionDiffModal
        open={versionDiffOpen}
        onClose={() => setVersionDiffOpen(false)}
        currentOffer={offer}
        versions={versions}
      />
    </div>
  );
}
