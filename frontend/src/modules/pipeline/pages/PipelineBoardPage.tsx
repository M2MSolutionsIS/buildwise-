/**
 * E-009 — Pipeline Board (Kanban)
 * F050: Kanban visualization | F051: Drag & drop + stagnation alerts
 * F052: Win probability     | F053: Weighted value + loss reasons
 */
import { useState } from "react";
import {
  Card,
  Tag,
  Typography,
  Spin,
  Alert,
  Row,
  Col,
  Statistic,
  Badge,
  Tooltip,
  Button,
  Modal,
  Input,
  Select,
  Space,
  Drawer,
  Timeline,
  Divider,
  Progress,
  App,
} from "antd";
import {
  DragOutlined,
  PlusOutlined,
  TrophyOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  PhoneOutlined,
  FileTextOutlined,
  EyeOutlined,
  FilterOutlined,
  ClearOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { pipelineService } from "../services/pipelineService";
import type { OpportunityListItem, PipelineBoardStage } from "../../../types";
import { useTranslation } from "../../../i18n";

const { Text, Title } = Typography;
const { TextArea } = Input;

const STAGE_CONFIG: Record<
  string,
  { label: string; color: string; probability: number; stagnationDays: number }
> = {
  new: { label: "Nou", color: "blue", probability: 10, stagnationDays: 14 },
  qualified: { label: "Calificat", color: "cyan", probability: 25, stagnationDays: 10 },
  scoping: { label: "Predimensionare", color: "geekblue", probability: 40, stagnationDays: 10 },
  offering: { label: "Ofertare", color: "purple", probability: 60, stagnationDays: 7 },
  sent: { label: "Trimis", color: "orange", probability: 75, stagnationDays: 7 },
  negotiation: { label: "Negociere", color: "gold", probability: 85, stagnationDays: 5 },
  won: { label: "Câștigat", color: "green", probability: 100, stagnationDays: 999 },
  lost: { label: "Pierdut", color: "red", probability: 0, stagnationDays: 999 },
};

const ACTIVE_STAGES = ["new", "qualified", "scoping", "offering", "sent", "negotiation"];

const LOSS_REASONS = [
  { value: "price", label: "Preț prea mare" },
  { value: "competitor", label: "Concurență" },
  { value: "quality", label: "Calitate" },
  { value: "timing", label: "Timeline nepotrivit" },
  { value: "budget", label: "Fără buget" },
  { value: "no_response", label: "Fără răspuns" },
  { value: "other", label: "Altul" },
];

/** F051: Calculate days in current stage */
function daysInStage(opp: OpportunityListItem): number {
  if (!opp.created_at) return 0;
  return Math.floor((Date.now() - new Date(opp.created_at).getTime()) / 86400000);
}

/** F051: Check stagnation against stage threshold */
function isStagnant(opp: OpportunityListItem): boolean {
  const threshold = STAGE_CONFIG[opp.stage]?.stagnationDays ?? 14;
  return daysInStage(opp) > threshold;
}

/** F052: Scoring — simplified visual score 0-100 */
function computeScore(opp: OpportunityListItem): number {
  const prob = opp.win_probability ?? STAGE_CONFIG[opp.stage]?.probability ?? 0;
  const valueNorm = Math.min((opp.estimated_value ?? 0) / 100000, 1) * 25;
  const stageBonus = (ACTIVE_STAGES.indexOf(opp.stage) + 1) * 5;
  const stagnationPenalty = isStagnant(opp) ? -15 : 0;
  return Math.max(0, Math.min(100, Math.round(prob * 0.4 + valueNorm + stageBonus + stagnationPenalty)));
}

export default function PipelineBoardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const t = useTranslation();

  // Drag state
  const [dragItem, setDragItem] = useState<OpportunityListItem | null>(null);

  // Loss modal (E-010.M1 equivalent on board)
  const [lossModal, setLossModal] = useState<{
    open: boolean;
    opportunityId: string;
  }>({ open: false, opportunityId: "" });
  const [lossReason, setLossReason] = useState("");
  const [lossDetail, setLossDetail] = useState("");
  const [reactivation, setReactivation] = useState<string | undefined>();

  // E-009.M1 Slide-over panel
  const [slideOver, setSlideOver] = useState<OpportunityListItem | null>(null);

  // Filters (F050)
  const [filterAgent, setFilterAgent] = useState<string | undefined>();
  const [filterMinValue, setFilterMinValue] = useState<number | undefined>();
  const [showFilters, setShowFilters] = useState(false);

  const { data: boardData, isLoading, error } = useQuery({
    queryKey: ["pipeline-board", { owner_id: filterAgent, min_value: filterMinValue }],
    queryFn: () => pipelineService.getBoard({
      owner_id: filterAgent,
      min_value: filterMinValue,
    }),
  });

  // Activities for slide-over
  const { data: slideActivities } = useQuery({
    queryKey: ["activities", { opportunity_id: slideOver?.id }],
    queryFn: () => pipelineService.listActivities({ opportunity_id: slideOver!.id, per_page: 5 }),
    enabled: !!slideOver,
  });

  const transitionMutation = useMutation({
    mutationFn: ({
      id, stage, reason, detail,
    }: { id: string; stage: string; reason?: string; detail?: string }) =>
      pipelineService.transitionStage(id, stage, reason, detail),
    onSuccess: () => {
      message.success("Oportunitate mutată.");
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
    },
    onError: () => message.error("Tranziție invalidă."),
  });

  const board = boardData?.data;
  const stagesMap = new Map<string, PipelineBoardStage>();
  board?.stages?.forEach((s) => stagesMap.set(s.stage, s));

  const handleDragStart = (opp: OpportunityListItem) => setDragItem(opp);

  const handleDrop = (targetStage: string) => {
    if (!dragItem || dragItem.stage === targetStage) {
      setDragItem(null);
      return;
    }
    if (targetStage === "lost") {
      setLossModal({ open: true, opportunityId: dragItem.id });
      setDragItem(null);
      return;
    }
    transitionMutation.mutate({ id: dragItem.id, stage: targetStage });
    setDragItem(null);
  };

  const handleLossConfirm = () => {
    if (!lossReason) {
      message.warning("Selectează un motiv de pierdere.");
      return;
    }
    transitionMutation.mutate({
      id: lossModal.opportunityId,
      stage: "lost",
      reason: lossReason,
      detail: lossDetail,
    });
    setLossModal({ open: false, opportunityId: "" });
    setLossReason("");
    setLossDetail("");
    setReactivation(undefined);
  };

  const clearFilters = () => {
    setFilterAgent(undefined);
    setFilterMinValue(undefined);
  };

  const hasFilters = !!filterAgent || filterMinValue !== undefined;

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error) return <Alert type="error" message="Eroare la încărcarea pipeline-ului" />;

  // Count stagnant opportunities
  const allOpps = board?.stages?.flatMap((s) => s.opportunities) ?? [];
  const stagnantCount = allOpps.filter((o) => isStagnant(o)).length;

  return (
    <>
      {/* Header with summary + filters */}
      <Row gutter={16} style={{ marginBottom: 16 }} align="middle">
        <Col flex="auto">
          <Space>
            <Title level={3} style={{ margin: 0 }}>{t.nav.pipelineKanban}</Title>
            {stagnantCount > 0 && (
              <Tooltip title={`${stagnantCount} oportunități stagnante`}>
                <Badge count={stagnantCount} style={{ backgroundColor: "#ff4d4f" }}>
                  <Tag color="red" icon={<WarningOutlined />}>Stagnare</Tag>
                </Badge>
              </Tooltip>
            )}
          </Space>
        </Col>
        <Col>
          <Space size="large">
            <Statistic
              title="Valoare Pipeline"
              value={board?.total_pipeline_value ?? 0}
              suffix={board?.currency ?? "RON"}
              valueStyle={{ fontSize: 16 }}
            />
            <Statistic
              title="Valoare Ponderată"
              value={board?.total_weighted_value ?? 0}
              suffix={board?.currency ?? "RON"}
              valueStyle={{ fontSize: 16, color: "#1677ff" }}
            />
          </Space>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<FilterOutlined />}
              onClick={() => setShowFilters(!showFilters)}
              type={hasFilters ? "primary" : "default"}
            >
              Filtre
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate("/pipeline/opportunities/new")}
            >
              Oportunitate Nouă
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Filter bar */}
      {showFilters && (
        <Card size="small" style={{ marginBottom: 12 }}>
          <Row gutter={12} align="middle">
            <Col>
              <Text type="secondary" style={{ fontSize: 12 }}>Agent:</Text>
              <Input
                placeholder="Owner ID"
                value={filterAgent}
                onChange={(e) => setFilterAgent(e.target.value || undefined)}
                style={{ width: 200, marginLeft: 8 }}
                allowClear
              />
            </Col>
            <Col>
              <Text type="secondary" style={{ fontSize: 12 }}>Valoare min:</Text>
              <Input
                type="number"
                placeholder="0"
                value={filterMinValue}
                onChange={(e) => setFilterMinValue(e.target.value ? Number(e.target.value) : undefined)}
                style={{ width: 140, marginLeft: 8 }}
                allowClear
              />
            </Col>
            <Col>
              {hasFilters && (
                <Button icon={<ClearOutlined />} size="small" onClick={clearFilters}>
                  Resetează
                </Button>
              )}
            </Col>
          </Row>
        </Card>
      )}

      {/* Kanban columns */}
      <div
        style={{
          display: "flex",
          gap: 12,
          overflowX: "auto",
          paddingBottom: 16,
          minHeight: 500,
        }}
      >
        {ACTIVE_STAGES.map((stageKey) => {
          const config = STAGE_CONFIG[stageKey]!;
          const stageData = stagesMap.get(stageKey);
          const opps = stageData?.opportunities ?? [];
          const stageStagnant = opps.filter((o) => isStagnant(o)).length;

          return (
            <div
              key={stageKey}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(stageKey)}
              style={{
                minWidth: 260,
                maxWidth: 280,
                flex: "1 0 260px",
                background: "#fafafa",
                borderRadius: 8,
                padding: 8,
                border: dragItem ? "2px dashed #1677ff" : "2px solid transparent",
              }}
            >
              {/* Column header */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 8,
                  padding: "4px 8px",
                }}
              >
                <Space>
                  <Tag color={config.color}>{config.label}</Tag>
                  <Badge count={opps.length} style={{ backgroundColor: "#999" }} />
                  {stageStagnant > 0 && (
                    <Tooltip title={`${stageStagnant} stagnante (>${config.stagnationDays}z)`}>
                      <WarningOutlined style={{ color: "#ff4d4f", fontSize: 13 }} />
                    </Tooltip>
                  )}
                </Space>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {((stageData?.total_value ?? 0) / 1000).toFixed(0)}k {board?.currency}
                </Text>
              </div>

              {/* Column footer: weighted value */}
              <div style={{ padding: "0 8px 4px", marginBottom: 4 }}>
                <Text type="secondary" style={{ fontSize: 10 }}>
                  Ponderat: {((stageData?.weighted_value ?? 0) / 1000).toFixed(0)}k
                </Text>
              </div>

              {/* Opportunity cards */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 480, overflowY: "auto" }}>
                {opps.map((opp) => {
                  const days = daysInStage(opp);
                  const stagnant = isStagnant(opp);
                  const score = computeScore(opp);

                  return (
                    <Card
                      key={opp.id}
                      size="small"
                      hoverable
                      draggable
                      onDragStart={() => handleDragStart(opp)}
                      onClick={() => setSlideOver(opp)}
                      onDoubleClick={() => navigate(`/pipeline/opportunities/${opp.id}`)}
                      style={{
                        cursor: "grab",
                        borderLeft: stagnant ? "3px solid #ff4d4f" : "3px solid transparent",
                      }}
                      styles={{ body: { padding: "8px 12px" } }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <Text
                          strong
                          ellipsis={{ tooltip: opp.title }}
                          style={{ maxWidth: 160, fontSize: 13 }}
                        >
                          {opp.title}
                        </Text>
                        <DragOutlined style={{ color: "#bbb", fontSize: 12 }} />
                      </div>

                      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {opp.estimated_value?.toLocaleString("ro-RO") ?? "—"} {opp.currency}
                        </Text>
                        <Tooltip title={`Probabilitate: ${opp.win_probability ?? config.probability}%`}>
                          <Tag
                            color={(opp.win_probability ?? 0) >= 60 ? "green" : (opp.win_probability ?? 0) >= 30 ? "orange" : "default"}
                            style={{ fontSize: 11 }}
                          >
                            {opp.win_probability ?? config.probability}%
                          </Tag>
                        </Tooltip>
                      </div>

                      {/* F052: Score bar */}
                      <Progress
                        percent={score}
                        size="small"
                        strokeColor={score >= 60 ? "#52c41a" : score >= 30 ? "#faad14" : "#ff4d4f"}
                        showInfo={false}
                        style={{ marginTop: 4, marginBottom: 0 }}
                      />

                      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {days}z în stadiu
                        </Text>
                        {stagnant && (
                          <Tooltip title={`Stagnare: ${days} zile fără avansare (limita: ${config.stagnationDays}z)`}>
                            <Tag color="red" style={{ fontSize: 10, lineHeight: "16px" }}>
                              <WarningOutlined /> Stagnare
                            </Tag>
                          </Tooltip>
                        )}
                      </div>
                    </Card>
                  );
                })}

                {opps.length === 0 && (
                  <div style={{ padding: 24, textAlign: "center", color: "#bbb", fontSize: 13 }}>
                    Nicio oportunitate
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Won column */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => handleDrop("won")}
          style={{
            minWidth: 200,
            flex: "0 0 200px",
            background: "#f6ffed",
            borderRadius: 8,
            padding: 8,
            border: dragItem ? "2px dashed #52c41a" : "2px solid transparent",
          }}
        >
          <div style={{ textAlign: "center", padding: 8 }}>
            <TrophyOutlined style={{ color: "#52c41a", fontSize: 20 }} />
            <br />
            <Tag color="green">Câștigat</Tag>
            <Badge
              count={stagesMap.get("won")?.count ?? 0}
              style={{ backgroundColor: "#52c41a", marginLeft: 4 }}
            />
          </div>
          <Statistic
            value={stagesMap.get("won")?.total_value ?? 0}
            suffix={board?.currency}
            valueStyle={{ fontSize: 14, textAlign: "center" }}
          />
        </div>

        {/* Lost column */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => handleDrop("lost")}
          style={{
            minWidth: 200,
            flex: "0 0 200px",
            background: "#fff2f0",
            borderRadius: 8,
            padding: 8,
            border: dragItem ? "2px dashed #ff4d4f" : "2px solid transparent",
          }}
        >
          <div style={{ textAlign: "center", padding: 8 }}>
            <CloseCircleOutlined style={{ color: "#ff4d4f", fontSize: 20 }} />
            <br />
            <Tag color="red">Pierdut</Tag>
            <Badge
              count={stagesMap.get("lost")?.count ?? 0}
              style={{ backgroundColor: "#ff4d4f", marginLeft: 4 }}
            />
          </div>
        </div>
      </div>

      {/* ─── E-009.M1 — Quick Opportunity Slide-over (380px) ──────────────── */}
      <Drawer
        title={slideOver?.title ?? "Oportunitate"}
        open={!!slideOver}
        onClose={() => setSlideOver(null)}
        width={380}
        extra={
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              navigate(`/pipeline/opportunities/${slideOver!.id}`);
              setSlideOver(null);
            }}
          >
            Detalii complete
          </Button>
        }
      >
        {slideOver && (() => {
          const days = daysInStage(slideOver);
          const stagnant = isStagnant(slideOver);
          const score = computeScore(slideOver);
          const config = STAGE_CONFIG[slideOver.stage];

          return (
            <>
              {/* KPI section */}
              <Row gutter={[16, 12]}>
                <Col span={12}>
                  <Statistic
                    title="Valoare"
                    value={slideOver.estimated_value ?? 0}
                    suffix={slideOver.currency}
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Probabilitate"
                    value={slideOver.win_probability ?? config?.probability ?? 0}
                    suffix="%"
                    valueStyle={{ fontSize: 16, color: (slideOver.win_probability ?? 0) >= 60 ? "#52c41a" : "#faad14" }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic title="Zile în stadiu" value={days} valueStyle={{ fontSize: 16 }} />
                </Col>
                <Col span={12}>
                  <div>
                    <Text type="secondary" style={{ fontSize: 12 }}>Scoring</Text>
                    <Progress
                      percent={score}
                      strokeColor={score >= 60 ? "#52c41a" : score >= 30 ? "#faad14" : "#ff4d4f"}
                      size="small"
                    />
                  </div>
                </Col>
              </Row>

              {stagnant && (
                <Alert
                  type="warning"
                  message={`Stagnare — ${days} zile fără avansare`}
                  description="Planifică un follow-up pentru această oportunitate."
                  icon={<WarningOutlined />}
                  showIcon
                  style={{ marginTop: 12 }}
                />
              )}

              <Divider />

              {/* Quick actions */}
              <Space direction="vertical" style={{ width: "100%" }}>
                <Button
                  block
                  icon={<PhoneOutlined />}
                  onClick={() => {
                    navigate(`/pipeline/opportunities/${slideOver.id}`);
                    setSlideOver(null);
                  }}
                >
                  Planifică apel
                </Button>
                <Button
                  block
                  icon={<FileTextOutlined />}
                  onClick={() => {
                    navigate(`/pipeline/offers/new?opportunity_id=${slideOver.id}&contact_id=${slideOver.contact_id}`);
                    setSlideOver(null);
                  }}
                >
                  Creează ofertă
                </Button>
              </Space>

              <Divider />

              {/* Last activities */}
              <Text strong style={{ marginBottom: 8, display: "block" }}>Activități recente</Text>
              {(slideActivities?.data ?? []).length === 0 ? (
                <Text type="secondary">Nicio activitate.</Text>
              ) : (
                <Timeline
                  items={(slideActivities?.data ?? []).map((a) => ({
                    color: a.status === "completed" ? "green" : a.status === "cancelled" ? "red" : "blue",
                    children: (
                      <div>
                        <Text style={{ fontSize: 13 }}>{a.title}</Text>
                        <br />
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {a.activity_type} — {new Date(a.scheduled_date).toLocaleDateString("ro-RO")}
                        </Text>
                      </div>
                    ),
                  }))}
                />
              )}
            </>
          );
        })()}
      </Drawer>

      {/* ─── Loss Reason Modal (E-010.M1) ─────────────────────────────────── */}
      <Modal
        title="Motiv pierdere oportunitate"
        open={lossModal.open}
        onOk={handleLossConfirm}
        onCancel={() => {
          setLossModal({ open: false, opportunityId: "" });
          setLossReason("");
          setLossDetail("");
          setReactivation(undefined);
        }}
        okText="Confirmă"
        cancelText="Anulează"
        okButtonProps={{ disabled: !lossReason }}
      >
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
          {lossReason === "competitor" && (
            <div>
              <Text strong>Competitor</Text>
              <Input
                placeholder="Numele competitorului"
                style={{ marginTop: 4 }}
              />
            </div>
          )}
          <div>
            <Text strong>Detalii *</Text>
            <TextArea
              rows={3}
              placeholder="Detalii adiționale (min 10 caractere)"
              value={lossDetail}
              onChange={(e) => setLossDetail(e.target.value)}
              minLength={10}
              style={{ marginTop: 4 }}
            />
          </div>
          <div>
            <Text strong>Posibilitate reactivare?</Text>
            <Select
              placeholder="Selectează"
              value={reactivation}
              onChange={setReactivation}
              style={{ width: "100%", marginTop: 4 }}
              options={[
                { value: "yes", label: "Da" },
                { value: "no", label: "Nu" },
                { value: "maybe", label: "Poate" },
              ]}
              allowClear
            />
          </div>
        </Space>
      </Modal>
    </>
  );
}
