/**
 * E-010 — Opportunity Detail
 * F042: Qualify & Handover | F043-F048: Deal Scoping
 * F051: Stage transition   | F052: Win probability / Scoring
 * F053: Weighted value      | F054-F056: Activities
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
  Steps,
  Row,
  Col,
  Statistic,
  Spin,
  Alert,
  Timeline,
  Tabs,
  Progress,
  Modal,
  Input,
  Select,
  Form,
  DatePicker,
  Popconfirm,
  Empty,
  Tooltip,
  Badge,
  App,
} from "antd";
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  RocketOutlined,
  PlusOutlined,
  WarningOutlined,
  TrophyOutlined,
  CloseCircleOutlined,
  PhoneOutlined,
  MailOutlined,
  TeamOutlined,
  FileTextOutlined,
  CalendarOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pipelineService } from "../services/pipelineService";
import type { OpportunityStage, ActivityListItem } from "../../../types";

const { Title, Text } = Typography;
const { TextArea } = Input;

const STAGES: { key: OpportunityStage; label: string }[] = [
  { key: "new", label: "Nou" },
  { key: "qualified", label: "Calificat" },
  { key: "scoping", label: "Predimensionare" },
  { key: "offering", label: "Ofertare" },
  { key: "sent", label: "Trimis" },
  { key: "negotiation", label: "Negociere" },
  { key: "won", label: "Câștigat" },
];

const STAGE_INDEX: Record<string, number> = {};
STAGES.forEach((s, i) => { STAGE_INDEX[s.key] = i; });

const STAGE_STAGNATION: Record<string, number> = {
  new: 14, qualified: 10, scoping: 10, offering: 7, sent: 7, negotiation: 5,
};

const ACTIVITY_TYPES = [
  { value: "call", label: "Apel", icon: <PhoneOutlined /> },
  { value: "email", label: "Email", icon: <MailOutlined /> },
  { value: "meeting", label: "Întâlnire", icon: <TeamOutlined /> },
  { value: "visit", label: "Vizită", icon: <CalendarOutlined /> },
  { value: "note", label: "Notă", icon: <FileTextOutlined /> },
];

const LOSS_REASONS = [
  { value: "price", label: "Preț prea mare" },
  { value: "competitor", label: "Concurență" },
  { value: "quality", label: "Calitate" },
  { value: "timing", label: "Timeline nepotrivit" },
  { value: "budget", label: "Fără buget" },
  { value: "no_response", label: "Fără răspuns" },
  { value: "other", label: "Altul" },
];

/** F052: Compute opportunity score (0-100) */
function computeScore(opp: {
  win_probability?: number | null;
  estimated_value?: number | null;
  stage: string;
  stage_entered_at?: string | null;
}): { total: number; breakdown: { label: string; weight: number; value: number }[] } {
  const prob = opp.win_probability ?? 0;
  const valueNorm = Math.min((opp.estimated_value ?? 0) / 100000, 1) * 100;
  const stageIdx = STAGE_INDEX[opp.stage] ?? 0;
  const stageScore = (stageIdx / 6) * 100;
  const daysInStage = opp.stage_entered_at
    ? Math.floor((Date.now() - new Date(opp.stage_entered_at).getTime()) / 86400000)
    : 0;
  const threshold = STAGE_STAGNATION[opp.stage] ?? 14;
  const timeScore = Math.max(0, 100 - (daysInStage / threshold) * 100);

  const breakdown = [
    { label: "Frecvență interacțiuni", weight: 30, value: prob },
    { label: "Valoare normalizată", weight: 25, value: valueNorm },
    { label: "Progres stadiu", weight: 20, value: stageScore },
    { label: "Timp în stadiu", weight: 15, value: timeScore },
    { label: "Completitudine date", weight: 10, value: opp.estimated_value && opp.win_probability ? 100 : 40 },
  ];

  const total = Math.round(
    breakdown.reduce((sum, b) => sum + (b.value * b.weight) / 100, 0)
  );

  return { total: Math.max(0, Math.min(100, total)), breakdown };
}

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  // Activity filters
  const [activityFilter, setActivityFilter] = useState<string>("all");

  // Add activity modal
  const [addActivityOpen, setAddActivityOpen] = useState(false);
  const [activityForm] = Form.useForm();

  // Won/Lost modal (E-010.M1)
  const [wonLostModal, setWonLostModal] = useState<{ open: boolean; type: "won" | "lost" }>({
    open: false, type: "won",
  });
  const [lossReason, setLossReason] = useState("");
  const [lossDetail, setLossDetail] = useState("");
  const [wonReason, setWonReason] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["opportunity", id],
    queryFn: () => pipelineService.getOpportunity(id!),
    enabled: !!id,
  });

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", { opportunity_id: id }],
    queryFn: () => pipelineService.listActivities({ opportunity_id: id, per_page: 50 }),
    enabled: !!id,
  });

  const transitionMutation = useMutation({
    mutationFn: (stage: string) => pipelineService.transitionStage(id!, stage),
    onSuccess: () => {
      message.success("Stadiu actualizat.");
      queryClient.invalidateQueries({ queryKey: ["opportunity", id] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
    },
    onError: () => message.error("Tranziție invalidă."),
  });

  const wonLostMutation = useMutation({
    mutationFn: ({ stage, reason, detail }: { stage: string; reason?: string; detail?: string }) =>
      pipelineService.transitionStage(id!, stage, reason, detail),
    onSuccess: () => {
      message.success("Oportunitate finalizată.");
      queryClient.invalidateQueries({ queryKey: ["opportunity", id] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
      setWonLostModal({ open: false, type: "won" });
      setLossReason("");
      setLossDetail("");
      setWonReason("");
    },
    onError: () => message.error("Eroare la tranziție."),
  });

  const deleteMutation = useMutation({
    mutationFn: () => pipelineService.deleteOpportunity(id!),
    onSuccess: () => {
      message.success("Oportunitate ștearsă.");
      navigate("/pipeline/board");
    },
  });

  const qualifyMutation = useMutation({
    mutationFn: () => pipelineService.qualifyOpportunity(id!),
    onSuccess: () => {
      message.success("Oportunitate calificată.");
      queryClient.invalidateQueries({ queryKey: ["opportunity", id] });
    },
  });

  const createActivityMutation = useMutation({
    mutationFn: (values: Record<string, unknown>) => pipelineService.createActivity(values),
    onSuccess: () => {
      message.success("Activitate creată.");
      setAddActivityOpen(false);
      activityForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["activities", { opportunity_id: id }] });
    },
    onError: () => message.error("Eroare la crearea activității."),
  });

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error || !data?.data) return <Alert type="error" message="Oportunitate negăsită" />;

  const opp = data.data;
  const currentIdx = STAGE_INDEX[opp.stage] ?? 0;
  const isTerminal = opp.stage === "won" || opp.stage === "lost";
  const allActivities: ActivityListItem[] = activitiesData?.data ?? [];
  const nextStage = !isTerminal ? STAGES[currentIdx + 1] : null;

  // F051: Stagnation detection
  const daysInStage = opp.stage_entered_at
    ? Math.floor((Date.now() - new Date(opp.stage_entered_at).getTime()) / 86400000)
    : 0;
  const stagnationThreshold = STAGE_STAGNATION[opp.stage] ?? 14;
  const isStagnant = !isTerminal && daysInStage > stagnationThreshold;

  // F052: Scoring
  const scoring = computeScore(opp);

  // Activity filtering
  const filteredActivities = allActivities.filter((a) => {
    if (activityFilter === "all") return true;
    if (activityFilter === "planned") return a.status === "planned";
    if (activityFilter === "completed") return a.status === "completed";
    if (activityFilter === "overdue") {
      return a.status === "planned" && new Date(a.scheduled_date) < new Date();
    }
    return true;
  });

  const overdueCount = allActivities.filter(
    (a) => a.status === "planned" && new Date(a.scheduled_date) < new Date()
  ).length;

  const handleWonLostConfirm = () => {
    if (wonLostModal.type === "lost" && !lossReason) {
      message.warning("Selectează un motiv de pierdere.");
      return;
    }
    wonLostMutation.mutate({
      stage: wonLostModal.type,
      reason: wonLostModal.type === "lost" ? lossReason : wonReason,
      detail: wonLostModal.type === "lost" ? lossDetail : wonReason,
    });
  };

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/pipeline/board")}>
          Înapoi la Pipeline
        </Button>
        {opp?.contact_id && (
          <Button
            icon={<TeamOutlined />}
            onClick={() => navigate(`/crm/contacts/${opp.contact_id}`)}
          >
            Contact
          </Button>
        )}
      </Space>

      {/* F051: Stagnation alert */}
      {isStagnant && (
        <Alert
          type="warning"
          message={`Stagnare — ${daysInStage} zile fără avansare (limita: ${stagnationThreshold}z)`}
          description="Planifică un follow-up sau avansează oportunitatea."
          icon={<WarningOutlined />}
          showIcon
          action={
            <Button size="small" onClick={() => setAddActivityOpen(true)}>
              Planifică follow-up
            </Button>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Stage progress */}
      <Card style={{ marginBottom: 16 }}>
        <Steps
          current={opp.stage === "lost" ? undefined : currentIdx}
          status={opp.stage === "lost" ? "error" : opp.stage === "won" ? "finish" : "process"}
          items={STAGES.map((s) => ({ title: s.label }))}
          size="small"
        />
        {!isTerminal && (
          <div style={{ textAlign: "center", marginTop: 12 }}>
            <Space>
              {nextStage && (
                <Button
                  type="primary"
                  icon={<RocketOutlined />}
                  loading={transitionMutation.isPending}
                  onClick={() => transitionMutation.mutate(nextStage.key)}
                >
                  Avansează la: {nextStage.label}
                </Button>
              )}
              <Button
                icon={<TrophyOutlined />}
                style={{ color: "#52c41a", borderColor: "#52c41a" }}
                onClick={() => setWonLostModal({ open: true, type: "won" })}
              >
                Câștigat
              </Button>
              <Button
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => setWonLostModal({ open: true, type: "lost" })}
              >
                Pierdut
              </Button>
            </Space>
          </div>
        )}
      </Card>

      <Row gutter={16}>
        <Col xs={24} lg={16}>
          {/* Main details with title bar */}
          <Card
            title={
              <Space>
                <Title level={4} style={{ margin: 0 }}>{opp.title}</Title>
                <Tag color={opp.stage === "won" ? "green" : opp.stage === "lost" ? "red" : "blue"}>
                  {STAGES.find((s) => s.key === opp.stage)?.label ?? opp.stage}
                </Tag>
              </Space>
            }
            extra={
              <Space>
                {!opp.is_qualified && opp.stage === "new" && (
                  <Button icon={<CheckCircleOutlined />} loading={qualifyMutation.isPending} onClick={() => qualifyMutation.mutate()}>
                    Califică
                  </Button>
                )}
                <Button icon={<EditOutlined />} onClick={() => navigate(`/pipeline/opportunities/${id}/edit`)}>
                  Editează
                </Button>
                <Popconfirm title="Ștergi oportunitatea?" onConfirm={() => deleteMutation.mutate()} okText="Da" cancelText="Nu">
                  <Button danger icon={<DeleteOutlined />} />
                </Popconfirm>
              </Space>
            }
            style={{ marginBottom: 16 }}
          >
            <Tabs
              defaultActiveKey="scoring"
              items={[
                {
                  key: "scoring",
                  label: "Scoring",
                  children: (
                    <>
                      {/* F052: Score visualization */}
                      <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
                        <Col span={8}>
                          <div style={{ textAlign: "center" }}>
                            <Progress
                              type="circle"
                              percent={scoring.total}
                              size={120}
                              strokeColor={scoring.total >= 60 ? "#52c41a" : scoring.total >= 30 ? "#faad14" : "#ff4d4f"}
                              format={(p) => <span style={{ fontSize: 24 }}>{p}</span>}
                            />
                            <div style={{ marginTop: 8 }}>
                              <Text strong>Scor Total</Text>
                            </div>
                          </div>
                        </Col>
                        <Col span={16}>
                          {scoring.breakdown.map((b) => (
                            <div key={b.label} style={{ marginBottom: 8 }}>
                              <Row justify="space-between">
                                <Text style={{ fontSize: 13 }}>{b.label} ({b.weight}%)</Text>
                                <Text type="secondary" style={{ fontSize: 12 }}>{Math.round(b.value)}/100</Text>
                              </Row>
                              <Progress
                                percent={Math.round(b.value)}
                                size="small"
                                showInfo={false}
                                strokeColor={b.value >= 60 ? "#52c41a" : b.value >= 30 ? "#faad14" : "#ff4d4f"}
                              />
                            </div>
                          ))}
                        </Col>
                      </Row>
                    </>
                  ),
                },
                {
                  key: "activities",
                  label: (
                    <Space>
                      Activități
                      {overdueCount > 0 && <Badge count={overdueCount} style={{ backgroundColor: "#ff4d4f" }} />}
                    </Space>
                  ),
                  children: (
                    <>
                      <Row justify="space-between" style={{ marginBottom: 12 }}>
                        <Select
                          value={activityFilter}
                          onChange={setActivityFilter}
                          style={{ width: 180 }}
                          options={[
                            { value: "all", label: "Toate" },
                            { value: "planned", label: "Planificate" },
                            { value: "completed", label: "Finalizate" },
                            { value: "overdue", label: `Restante (${overdueCount})` },
                          ]}
                        />
                        <Button icon={<PlusOutlined />} onClick={() => setAddActivityOpen(true)}>
                          Activitate
                        </Button>
                      </Row>

                      {filteredActivities.length === 0 ? (
                        <Empty description="Nicio activitate." />
                      ) : (
                        <Timeline
                          items={filteredActivities.map((a) => {
                            const isOverdue = a.status === "planned" && new Date(a.scheduled_date) < new Date();
                            return {
                              color: a.status === "completed" ? "green" : isOverdue ? "red" : "blue",
                              children: (
                                <div>
                                  <Space>
                                    <Text strong style={{ fontSize: 13 }}>{a.title}</Text>
                                    <Tag color={a.status === "completed" ? "green" : isOverdue ? "red" : "blue"}>
                                      {a.status === "completed" ? "Finalizat" : isOverdue ? "Restant" : "Planificat"}
                                    </Tag>
                                  </Space>
                                  <br />
                                  <Text type="secondary" style={{ fontSize: 12 }}>
                                    {ACTIVITY_TYPES.find((t) => t.value === a.activity_type)?.label ?? a.activity_type}
                                    {" — "}
                                    {new Date(a.scheduled_date).toLocaleDateString("ro-RO")}
                                  </Text>
                                  {isOverdue && (
                                    <Tooltip title="Activitate restantă">
                                      <WarningOutlined style={{ color: "#ff4d4f", marginLeft: 6 }} />
                                    </Tooltip>
                                  )}
                                </div>
                              ),
                            };
                          })}
                        />
                      )}
                    </>
                  ),
                },
                {
                  key: "details",
                  label: "Detalii",
                  children: (
                    <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
                      <Descriptions.Item label="Valoare estimată">
                        {opp.estimated_value?.toLocaleString("ro-RO") ?? "—"} {opp.currency}
                      </Descriptions.Item>
                      <Descriptions.Item label="Probabilitate câștig">
                        <Tag color={(opp.win_probability ?? 0) >= 60 ? "green" : (opp.win_probability ?? 0) >= 30 ? "orange" : "default"}>
                          {opp.win_probability ?? 0}%
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="Valoare ponderată">
                        {opp.weighted_value?.toLocaleString("ro-RO") ?? "—"} {opp.currency}
                      </Descriptions.Item>
                      <Descriptions.Item label="Dată închidere estimată">
                        {opp.expected_close_date ? new Date(opp.expected_close_date).toLocaleDateString("ro-RO") : "—"}
                      </Descriptions.Item>
                      <Descriptions.Item label="Calificat">
                        {opp.is_qualified ? <Tag color="green">Da</Tag> : <Tag color="default">Nu</Tag>}
                      </Descriptions.Item>
                      <Descriptions.Item label="Validat RM">
                        {opp.rm_validated ? <Tag color="green">Da</Tag> : <Tag color="default">Nu</Tag>}
                      </Descriptions.Item>
                      <Descriptions.Item label="Sursă">{opp.source ?? "—"}</Descriptions.Item>
                      <Descriptions.Item label="Creat">{new Date(opp.created_at).toLocaleString("ro-RO")}</Descriptions.Item>
                    </Descriptions>
                  ),
                },
                {
                  key: "notes",
                  label: "Notițe",
                  children: (
                    <div>
                      {opp.description ? (
                        <div>
                          <Text type="secondary" style={{ fontSize: 12 }}>Descriere:</Text>
                          <p>{opp.description}</p>
                        </div>
                      ) : null}
                      {opp.notes ? <p>{opp.notes}</p> : <Text type="secondary">Nicio notiță.</Text>}
                    </div>
                  ),
                },
              ]}
            />

            {opp.stage === "lost" && opp.loss_reason && (
              <Alert
                type="error"
                style={{ marginTop: 12 }}
                message={`Motiv pierdere: ${opp.loss_reason}`}
                description={opp.loss_reason_detail}
              />
            )}

            {opp.stage === "won" && opp.won_reason && (
              <Alert
                type="success"
                style={{ marginTop: 12 }}
                message={`Motiv câștig: ${opp.won_reason}`}
              />
            )}
          </Card>
        </Col>

        {/* Sidebar KPIs */}
        <Col xs={24} lg={8}>
          <Card title="Indicatori" style={{ marginBottom: 16 }}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="Valoare" value={opp.estimated_value ?? 0} suffix={opp.currency} valueStyle={{ fontSize: 16 }} />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Probabilitate"
                  value={opp.win_probability ?? 0}
                  suffix="%"
                  valueStyle={{ fontSize: 16, color: (opp.win_probability ?? 0) >= 60 ? "#52c41a" : "#faad14" }}
                />
              </Col>
              <Col span={12}>
                <Statistic title="Ponderat" value={opp.weighted_value ?? 0} suffix={opp.currency} valueStyle={{ fontSize: 16 }} />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Zile în stadiu"
                  value={daysInStage}
                  valueStyle={{ fontSize: 16, color: isStagnant ? "#ff4d4f" : undefined }}
                />
              </Col>
              <Col span={24}>
                <Text type="secondary" style={{ fontSize: 12 }}>Scoring</Text>
                <Progress
                  percent={scoring.total}
                  strokeColor={scoring.total >= 60 ? "#52c41a" : scoring.total >= 30 ? "#faad14" : "#ff4d4f"}
                />
              </Col>
            </Row>
          </Card>

          {/* Quick actions */}
          <Card title="Acțiuni rapide" size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Button
                block
                icon={<FileTextOutlined />}
                onClick={() => navigate(`/pipeline/offers/new?opportunity_id=${id}&contact_id=${opp.contact_id}`)}
              >
                Ofertă nouă
              </Button>
              <Button block icon={<PlusOutlined />} onClick={() => setAddActivityOpen(true)}>
                Adaugă activitate
              </Button>
              <Button block icon={<PhoneOutlined />} onClick={() => {
                activityForm.setFieldsValue({ activity_type: "call" });
                setAddActivityOpen(true);
              }}>
                Planifică apel
              </Button>
            </Space>
          </Card>

          {opp.tags && opp.tags.length > 0 && (
            <Card title="Tag-uri" style={{ marginBottom: 16 }}>
              {opp.tags.map((tag) => (
                <Tag key={tag} style={{ marginBottom: 4 }}>{tag}</Tag>
              ))}
            </Card>
          )}
        </Col>
      </Row>

      {/* ─── E-010.M1 — Won/Lost Reason Modal ────────────────────────────── */}
      <Modal
        title={wonLostModal.type === "won" ? "Confirmare câștig oportunitate" : "Motiv pierdere oportunitate"}
        open={wonLostModal.open}
        onOk={handleWonLostConfirm}
        onCancel={() => {
          setWonLostModal({ open: false, type: "won" });
          setLossReason("");
          setLossDetail("");
          setWonReason("");
        }}
        okText="Salvează"
        cancelText="Anulează"
        confirmLoading={wonLostMutation.isPending}
        okButtonProps={{ disabled: wonLostModal.type === "lost" && !lossReason }}
      >
        {wonLostModal.type === "won" ? (
          <Space direction="vertical" style={{ width: "100%" }}>
            <div>
              <Text strong>Motiv câștig (opțional)</Text>
              <TextArea
                rows={3}
                placeholder="De ce am câștigat acest deal?"
                value={wonReason}
                onChange={(e) => setWonReason(e.target.value)}
                style={{ marginTop: 4 }}
              />
            </div>
          </Space>
        ) : (
          <Space direction="vertical" style={{ width: "100%" }} size="middle">
            <div>
              <Text strong>Motiv principal *</Text>
              <Select
                placeholder="Selectează motivul"
                value={lossReason || undefined}
                onChange={setLossReason}
                style={{ width: "100%", marginTop: 4 }}
                options={LOSS_REASONS}
              />
            </div>
            <div>
              <Text strong>Detalii</Text>
              <TextArea
                rows={3}
                placeholder="Detalii adiționale"
                value={lossDetail}
                onChange={(e) => setLossDetail(e.target.value)}
                style={{ marginTop: 4 }}
              />
            </div>
          </Space>
        )}
      </Modal>

      {/* ─── Add Activity Modal (E-011.M1) ────────────────────────────────── */}
      <Modal
        title="Adaugă activitate"
        open={addActivityOpen}
        onOk={() => activityForm.submit()}
        onCancel={() => {
          setAddActivityOpen(false);
          activityForm.resetFields();
        }}
        okText="Salvează"
        cancelText="Anulează"
        confirmLoading={createActivityMutation.isPending}
      >
        <Form
          form={activityForm}
          layout="vertical"
          onFinish={(values) => {
            createActivityMutation.mutate({
              ...values,
              opportunity_id: id,
              contact_id: opp.contact_id,
              scheduled_date: values.scheduled_date?.toISOString(),
            });
          }}
        >
          <Form.Item name="activity_type" label="Tip" rules={[{ required: true, message: "Selectează tipul" }]}>
            <Select options={ACTIVITY_TYPES.map((t) => ({ value: t.value, label: t.label }))} />
          </Form.Item>
          <Form.Item name="title" label="Titlu" rules={[{ required: true, message: "Introdu titlul" }]}>
            <Input />
          </Form.Item>
          <Form.Item name="scheduled_date" label="Data planificată" rules={[{ required: true, message: "Selectează data" }]}>
            <DatePicker showTime style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="description" label="Descriere">
            <TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
