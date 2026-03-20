/**
 * E-009 — Pipeline Board (Kanban)
 * F-codes: F050 (Kanban visualization), F051 (Drag & drop + stagnation),
 *          F052 (Win probability), F053 (Weighted value + loss reasons)
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
  message,
} from "antd";
import {
  DragOutlined,
  PlusOutlined,
  TrophyOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { pipelineService } from "../services/pipelineService";
import type { OpportunityListItem, PipelineBoardStage } from "../../../types";

const { Text, Title } = Typography;
const { TextArea } = Input;

const STAGE_CONFIG: Record<
  string,
  { label: string; color: string; probability: number }
> = {
  new: { label: "Nou", color: "blue", probability: 10 },
  qualified: { label: "Calificat", color: "cyan", probability: 25 },
  scoping: { label: "Predimensionare", color: "geekblue", probability: 40 },
  offering: { label: "Ofertare", color: "purple", probability: 60 },
  sent: { label: "Trimis", color: "orange", probability: 75 },
  negotiation: { label: "Negociere", color: "gold", probability: 85 },
  won: { label: "Câștigat", color: "green", probability: 100 },
  lost: { label: "Pierdut", color: "red", probability: 0 },
};

const ACTIVE_STAGES = [
  "new",
  "qualified",
  "scoping",
  "offering",
  "sent",
  "negotiation",
];

export default function PipelineBoardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [dragItem, setDragItem] = useState<OpportunityListItem | null>(null);
  const [lossModal, setLossModal] = useState<{
    open: boolean;
    opportunityId: string;
    stage: string;
  }>({ open: false, opportunityId: "", stage: "" });
  const [lossReason, setLossReason] = useState("");
  const [lossDetail, setLossDetail] = useState("");

  const { data: boardData, isLoading, error } = useQuery({
    queryKey: ["pipeline-board"],
    queryFn: () => pipelineService.getBoard(),
  });

  const transitionMutation = useMutation({
    mutationFn: ({
      id,
      stage,
      reason,
      detail,
    }: {
      id: string;
      stage: string;
      reason?: string;
      detail?: string;
    }) => pipelineService.transitionStage(id, stage, reason, detail),
    onSuccess: () => {
      message.success("Oportunitate mutată.");
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
    },
    onError: () => message.error("Tranziție invalidă."),
  });

  const board = boardData?.data;
  const stagesMap = new Map<string, PipelineBoardStage>();
  board?.stages?.forEach((s) => stagesMap.set(s.stage, s));

  const handleDragStart = (opp: OpportunityListItem) => {
    setDragItem(opp);
  };

  const handleDrop = (targetStage: string) => {
    if (!dragItem || dragItem.stage === targetStage) {
      setDragItem(null);
      return;
    }
    if (targetStage === "lost") {
      setLossModal({
        open: true,
        opportunityId: dragItem.id,
        stage: targetStage,
      });
      setDragItem(null);
      return;
    }
    transitionMutation.mutate({ id: dragItem.id, stage: targetStage });
    setDragItem(null);
  };

  const handleLossConfirm = () => {
    transitionMutation.mutate({
      id: lossModal.opportunityId,
      stage: "lost",
      reason: lossReason,
      detail: lossDetail,
    });
    setLossModal({ open: false, opportunityId: "", stage: "" });
    setLossReason("");
    setLossDetail("");
  };

  if (isLoading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (error) return <Alert type="error" message="Eroare la încărcarea pipeline-ului" />;

  return (
    <>
      {/* Pipeline summary */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <Title level={3} style={{ margin: 0 }}>
            Pipeline Kanban
          </Title>
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
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate("/pipeline/opportunities/new")}
          >
            Oportunitate Nouă
          </Button>
        </Col>
      </Row>

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
                  <Badge
                    count={opps.length}
                    style={{ backgroundColor: "#999" }}
                  />
                </Space>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {((stageData?.total_value ?? 0) / 1000).toFixed(0)}k{" "}
                  {board?.currency}
                </Text>
              </div>

              {/* Opportunity cards */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {opps.map((opp) => (
                  <Card
                    key={opp.id}
                    size="small"
                    hoverable
                    draggable
                    onDragStart={() => handleDragStart(opp)}
                    onClick={() =>
                      navigate(`/pipeline/opportunities/${opp.id}`)
                    }
                    style={{ cursor: "grab" }}
                    styles={{ body: { padding: "8px 12px" } }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                      }}
                    >
                      <Text
                        strong
                        ellipsis={{ tooltip: opp.title }}
                        style={{ maxWidth: 170, fontSize: 13 }}
                      >
                        {opp.title}
                      </Text>
                      <DragOutlined style={{ color: "#bbb", fontSize: 12 }} />
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginTop: 4,
                      }}
                    >
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {opp.estimated_value?.toLocaleString("ro-RO") ?? "—"}{" "}
                        {opp.currency}
                      </Text>
                      <Tooltip title={`Probabilitate: ${opp.win_probability ?? config.probability}%`}>
                        <Tag
                          color={
                            (opp.win_probability ?? 0) >= 60
                              ? "green"
                              : (opp.win_probability ?? 0) >= 30
                                ? "orange"
                                : "default"
                          }
                          style={{ fontSize: 11 }}
                        >
                          {opp.win_probability ?? config.probability}%
                        </Tag>
                      </Tooltip>
                    </div>
                    {opp.expected_close_date && (
                      <Text
                        type="secondary"
                        style={{ fontSize: 11, display: "block", marginTop: 2 }}
                      >
                        Close:{" "}
                        {new Date(opp.expected_close_date).toLocaleDateString(
                          "ro-RO"
                        )}
                      </Text>
                    )}
                  </Card>
                ))}

                {opps.length === 0 && (
                  <div
                    style={{
                      padding: 24,
                      textAlign: "center",
                      color: "#bbb",
                      fontSize: 13,
                    }}
                  >
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

      {/* Loss reason modal */}
      <Modal
        title="Motiv pierdere oportunitate"
        open={lossModal.open}
        onOk={handleLossConfirm}
        onCancel={() => setLossModal({ open: false, opportunityId: "", stage: "" })}
        okText="Confirmă"
        cancelText="Anulează"
      >
        <Select
          placeholder="Selectează motivul"
          value={lossReason || undefined}
          onChange={setLossReason}
          style={{ width: "100%", marginBottom: 12 }}
          options={[
            { value: "price", label: "Preț prea mare" },
            { value: "competitor", label: "Concurență" },
            { value: "timing", label: "Timing nepotrivit" },
            { value: "budget", label: "Fără buget" },
            { value: "no_response", label: "Fără răspuns" },
            { value: "other", label: "Altul" },
          ]}
        />
        <TextArea
          rows={3}
          placeholder="Detalii adiționale (opțional)"
          value={lossDetail}
          onChange={(e) => setLossDetail(e.target.value)}
        />
      </Modal>
    </>
  );
}
