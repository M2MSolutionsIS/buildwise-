/**
 * E-010 — Opportunity Detail
 * F-codes: F042 (Qualify & Handover), F043-F048 (Deal Scoping),
 *          F051 (Stage transition), F052 (Win probability)
 */
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
  message,
  Popconfirm,
} from "antd";
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pipelineService } from "../services/pipelineService";
import type { OpportunityStage } from "../../../types";

const { Title, Text } = Typography;

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
STAGES.forEach((s, i) => {
  STAGE_INDEX[s.key] = i;
});

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["opportunity", id],
    queryFn: () => pipelineService.getOpportunity(id!),
    enabled: !!id,
  });

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", { opportunity_id: id }],
    queryFn: () =>
      pipelineService.listActivities({ opportunity_id: id, per_page: 10 }),
    enabled: !!id,
  });

  const transitionMutation = useMutation({
    mutationFn: (stage: string) =>
      pipelineService.transitionStage(id!, stage),
    onSuccess: () => {
      message.success("Stadiu actualizat.");
      queryClient.invalidateQueries({ queryKey: ["opportunity", id] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
    },
    onError: () => message.error("Tranziție invalidă."),
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

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error || !data?.data)
    return <Alert type="error" message="Oportunitate negăsită" />;

  const opp = data.data;
  const currentIdx = STAGE_INDEX[opp.stage] ?? 0;
  const isTerminal = opp.stage === "won" || opp.stage === "lost";
  const activities = activitiesData?.data ?? [];

  const nextStage = !isTerminal ? STAGES[currentIdx + 1] : null;

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate("/pipeline/board")}
        >
          Înapoi la Pipeline
        </Button>
      </Space>

      {/* Stage progress */}
      <Card style={{ marginBottom: 16 }}>
        <Steps
          current={opp.stage === "lost" ? undefined : currentIdx}
          status={opp.stage === "lost" ? "error" : opp.stage === "won" ? "finish" : "process"}
          items={STAGES.map((s) => ({ title: s.label }))}
          size="small"
        />
        {!isTerminal && nextStage && (
          <div style={{ textAlign: "center", marginTop: 12 }}>
            <Button
              type="primary"
              icon={<RocketOutlined />}
              loading={transitionMutation.isPending}
              onClick={() => transitionMutation.mutate(nextStage.key)}
            >
              Avansează la: {nextStage.label}
            </Button>
          </div>
        )}
      </Card>

      <Row gutter={16}>
        <Col xs={24} lg={16}>
          {/* Main details */}
          <Card
            title={
              <Space>
                <Title level={4} style={{ margin: 0 }}>
                  {opp.title}
                </Title>
                <Tag
                  color={
                    opp.stage === "won"
                      ? "green"
                      : opp.stage === "lost"
                        ? "red"
                        : "blue"
                  }
                >
                  {STAGES.find((s) => s.key === opp.stage)?.label ?? opp.stage}
                </Tag>
              </Space>
            }
            extra={
              <Space>
                {!opp.is_qualified && opp.stage === "new" && (
                  <Button
                    icon={<CheckCircleOutlined />}
                    loading={qualifyMutation.isPending}
                    onClick={() => qualifyMutation.mutate()}
                  >
                    Califică
                  </Button>
                )}
                <Button
                  icon={<EditOutlined />}
                  onClick={() =>
                    navigate(`/pipeline/opportunities/${id}/edit`)
                  }
                >
                  Editează
                </Button>
                <Popconfirm
                  title="Ștergi oportunitatea?"
                  onConfirm={() => deleteMutation.mutate()}
                  okText="Da"
                  cancelText="Nu"
                >
                  <Button danger icon={<DeleteOutlined />} />
                </Popconfirm>
              </Space>
            }
            style={{ marginBottom: 16 }}
          >
            <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
              <Descriptions.Item label="Valoare estimată">
                {opp.estimated_value?.toLocaleString("ro-RO") ?? "—"}{" "}
                {opp.currency}
              </Descriptions.Item>
              <Descriptions.Item label="Probabilitate câștig">
                <Tag
                  color={
                    (opp.win_probability ?? 0) >= 60
                      ? "green"
                      : (opp.win_probability ?? 0) >= 30
                        ? "orange"
                        : "default"
                  }
                >
                  {opp.win_probability ?? 0}%
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Valoare ponderată">
                {opp.weighted_value?.toLocaleString("ro-RO") ?? "—"}{" "}
                {opp.currency}
              </Descriptions.Item>
              <Descriptions.Item label="Dată închidere estimată">
                {opp.expected_close_date
                  ? new Date(opp.expected_close_date).toLocaleDateString(
                      "ro-RO"
                    )
                  : "—"}
              </Descriptions.Item>
              <Descriptions.Item label="Calificat">
                {opp.is_qualified ? (
                  <Tag color="green">Da</Tag>
                ) : (
                  <Tag color="default">Nu</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Validat RM">
                {opp.rm_validated ? (
                  <Tag color="green">Da</Tag>
                ) : (
                  <Tag color="default">Nu</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Sursă">
                {opp.source ?? "—"}
              </Descriptions.Item>
              <Descriptions.Item label="Creat">
                {new Date(opp.created_at).toLocaleString("ro-RO")}
              </Descriptions.Item>
            </Descriptions>

            {opp.description && (
              <div style={{ marginTop: 12 }}>
                <Text type="secondary">Descriere:</Text>
                <p>{opp.description}</p>
              </div>
            )}

            {opp.stage === "lost" && opp.loss_reason && (
              <Alert
                type="error"
                style={{ marginTop: 12 }}
                message={`Motiv pierdere: ${opp.loss_reason}`}
                description={opp.loss_reason_detail}
              />
            )}
          </Card>

          {/* Activities timeline */}
          <Card title="Activități Recente" style={{ marginBottom: 16 }}>
            {activities.length === 0 ? (
              <Text type="secondary">Nicio activitate înregistrată.</Text>
            ) : (
              <Timeline
                items={activities.map((a) => ({
                  children: (
                    <div>
                      <Text strong>{a.title}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {a.activity_type} —{" "}
                        {new Date(a.scheduled_date).toLocaleDateString("ro-RO")}
                      </Text>
                      <br />
                      <Tag
                        color={
                          a.status === "completed"
                            ? "green"
                            : a.status === "cancelled"
                              ? "red"
                              : "blue"
                        }
                      >
                        {a.status}
                      </Tag>
                    </div>
                  ),
                }))}
              />
            )}
          </Card>
        </Col>

        {/* Sidebar KPIs */}
        <Col xs={24} lg={8}>
          <Card title="Indicatori" style={{ marginBottom: 16 }}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="Valoare"
                  value={opp.estimated_value ?? 0}
                  suffix={opp.currency}
                  valueStyle={{ fontSize: 16 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Probabilitate"
                  value={opp.win_probability ?? 0}
                  suffix="%"
                  valueStyle={{
                    fontSize: 16,
                    color:
                      (opp.win_probability ?? 0) >= 60 ? "#52c41a" : "#faad14",
                  }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Ponderat"
                  value={opp.weighted_value ?? 0}
                  suffix={opp.currency}
                  valueStyle={{ fontSize: 16 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Zile în stadiu"
                  value={
                    opp.stage_entered_at
                      ? Math.floor(
                          (Date.now() -
                            new Date(opp.stage_entered_at).getTime()) /
                            86400000
                        )
                      : "—"
                  }
                  valueStyle={{ fontSize: 16 }}
                />
              </Col>
            </Row>
          </Card>

          {opp.tags && opp.tags.length > 0 && (
            <Card title="Tag-uri" style={{ marginBottom: 16 }}>
              {opp.tags.map((tag) => (
                <Tag key={tag} style={{ marginBottom: 4 }}>
                  {tag}
                </Tag>
              ))}
            </Card>
          )}

          {opp.notes && (
            <Card title="Note" style={{ marginBottom: 16 }}>
              <Text>{opp.notes}</Text>
            </Card>
          )}
        </Col>
      </Row>
    </>
  );
}
