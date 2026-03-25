/**
 * F061: Configurator Pipeline — Stadii, reguli avansare, alertă stagnare
 * Specific P3 (SaaS). Parte din F136 Configurator Global ERP.
 *
 * Funcționalități:
 * - CRUD stadii pipeline cu drag reorder
 * - Culori, probabilitate câștig, zile stagnare
 * - Reguli avansare automată (field, operator, value → target stage)
 * - Câmpuri obligatorii per stadiu
 * - Marcaje is_closed_won / is_closed_lost
 */
import { useState, useMemo, useCallback } from "react";
import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  ColorPicker,
  Typography,
  Row,
  Col,
  message,
  Alert,
  Popconfirm,
  Badge,
  Tooltip,
  Divider,
} from "antd";
import type { Color } from "antd/es/color-picker";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  FunnelPlotOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { systemService } from "../services/systemService";
import type { PipelineStageConfig } from "../../../types";

const { Title, Text } = Typography;

// ─── Auto-advance rule operators ────────────────────────────────────────────

const OPERATORS = [
  { value: "equals", label: "Este egal cu" },
  { value: "greater_than", label: "Mai mare decât" },
  { value: "not_empty", label: "Nu este gol" },
  { value: "contains", label: "Conține" },
];

const ADVANCE_FIELDS = [
  { value: "total_value", label: "Valoare totală" },
  { value: "has_offer", label: "Are ofertă" },
  { value: "has_contract", label: "Are contract" },
  { value: "contact_verified", label: "Contact verificat" },
  { value: "days_in_stage", label: "Zile în stadiu" },
  { value: "activities_count", label: "Nr. activități" },
];

const REQUIRED_FIELD_OPTIONS = [
  { value: "contact_id", label: "Contact asociat" },
  { value: "estimated_value", label: "Valoare estimată" },
  { value: "expected_close_date", label: "Dată închidere" },
  { value: "offer_id", label: "Ofertă atașată" },
  { value: "technical_evaluation", label: "Evaluare tehnică" },
  { value: "decision_maker", label: "Decident" },
];

// ─── Default pipeline stages (as reference) ─────────────────────────────────

const DEFAULT_STAGES = [
  { code: "identificare", name: "Identificare Nevoie", color: "#8c8c8c", win_probability: 10 },
  { code: "evaluare", name: "Evaluare Tehnică", color: "#1677ff", win_probability: 25 },
  { code: "oferta", name: "Ofertă", color: "#faad14", win_probability: 50 },
  { code: "negociere", name: "Negociere", color: "#fa8c16", win_probability: 70 },
  { code: "contract", name: "Contract", color: "#52c41a", win_probability: 90 },
  { code: "executie", name: "Execuție", color: "#13c2c2", win_probability: 95 },
  { code: "post_vanzare", name: "Post-vânzare", color: "#722ed1", win_probability: 100 },
];

// ─── Component ──────────────────────────────────────────────────────────────

export default function PipelineConfiguratorPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingStage, setEditingStage] = useState<PipelineStageConfig | null>(null);
  const [rulesModalOpen, setRulesModalOpen] = useState(false);
  const [rulesStage, setRulesStage] = useState<PipelineStageConfig | null>(null);
  const [form] = Form.useForm();

  // Data
  const { data: stagesData, isLoading } = useQuery({
    queryKey: ["pipeline-stages"],
    queryFn: () => systemService.listPipelineStages(),
  });
  const stages = useMemo(
    () => (stagesData?.data ?? []).sort((a, b) => a.sort_order - b.sort_order),
    [stagesData]
  );

  // Mutations
  const createMut = useMutation({
    mutationFn: (payload: Partial<PipelineStageConfig>) =>
      systemService.createPipelineStage(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-stages"] });
      message.success("Stadiu creat");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<PipelineStageConfig> }) =>
      systemService.updatePipelineStage(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-stages"] });
      message.success("Stadiu actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => systemService.deletePipelineStage(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-stages"] });
      message.success("Stadiu șters");
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  // Modal handlers
  const openCreate = useCallback(() => {
    setEditingStage(null);
    form.resetFields();
    form.setFieldsValue({
      sort_order: stages.length + 1,
      is_active: true,
      is_closed_won: false,
      is_closed_lost: false,
      color: "#1677ff",
      win_probability: 50,
      stagnation_days: 14,
    });
    setModalOpen(true);
  }, [form, stages.length]);

  const openEdit = useCallback(
    (stage: PipelineStageConfig) => {
      setEditingStage(stage);
      form.setFieldsValue({
        ...stage,
      });
      setModalOpen(true);
    },
    [form]
  );

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setEditingStage(null);
    form.resetFields();
  }, [form]);

  const handleSave = useCallback(async () => {
    const vals = await form.validateFields();
    if (editingStage) {
      updateMut.mutate({ id: editingStage.id, payload: vals });
    } else {
      createMut.mutate(vals);
    }
  }, [form, editingStage, updateMut, createMut]);

  const openRules = useCallback((stage: PipelineStageConfig) => {
    setRulesStage(stage);
    setRulesModalOpen(true);
  }, []);

  const handleSaveRules = useCallback(
    (rules: PipelineStageConfig["auto_advance_rules"]) => {
      if (rulesStage) {
        updateMut.mutate({
          id: rulesStage.id,
          payload: { auto_advance_rules: rules },
        });
      }
      setRulesModalOpen(false);
    },
    [rulesStage, updateMut]
  );

  // Stats
  const activeCount = stages.filter((s) => s.is_active).length;
  const wonStage = stages.find((s) => s.is_closed_won);
  const lostStage = stages.find((s) => s.is_closed_lost);

  // ─── Table columns ────────────────────────────────────────────────────────

  const columns = [
    {
      title: "#",
      dataIndex: "sort_order",
      key: "sort_order",
      width: 50,
      render: (v: number) => <Text type="secondary">{v}</Text>,
    },
    {
      title: "Stadiu",
      key: "name",
      width: 200,
      render: (_: unknown, r: PipelineStageConfig) => (
        <Space>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: r.color ?? "#d9d9d9",
            }}
          />
          <Text strong>{r.name}</Text>
          {r.is_closed_won && (
            <Tag color="green" icon={<CheckCircleOutlined />}>
              Won
            </Tag>
          )}
          {r.is_closed_lost && (
            <Tag color="red" icon={<CloseCircleOutlined />}>
              Lost
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: "Cod",
      dataIndex: "code",
      key: "code",
      width: 120,
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: "Probabilitate %",
      dataIndex: "win_probability",
      key: "win_probability",
      width: 120,
      align: "center" as const,
      render: (v: number | undefined) =>
        v != null ? (
          <Tag color={v >= 70 ? "green" : v >= 40 ? "orange" : "default"}>
            {v}%
          </Tag>
        ) : (
          "—"
        ),
    },
    {
      title: "Stagnare (zile)",
      dataIndex: "stagnation_days",
      key: "stagnation_days",
      width: 120,
      align: "center" as const,
      render: (v: number | undefined) =>
        v != null ? (
          <Space>
            <ClockCircleOutlined style={{ color: "#faad14" }} />
            <Text>{v}z</Text>
          </Space>
        ) : (
          "—"
        ),
    },
    {
      title: "Reguli avansare",
      key: "rules",
      width: 130,
      render: (_: unknown, r: PipelineStageConfig) => {
        const count = r.auto_advance_rules?.length ?? 0;
        return (
          <Badge count={count} size="small" style={{ backgroundColor: count > 0 ? "#1677ff" : "#d9d9d9" }}>
            <Button
              size="small"
              icon={<ThunderboltOutlined />}
              onClick={() => openRules(r)}
            >
              Reguli
            </Button>
          </Badge>
        );
      },
    },
    {
      title: "Activ",
      dataIndex: "is_active",
      key: "is_active",
      width: 70,
      render: (v: boolean) =>
        v ? (
          <Tag color="green">Da</Tag>
        ) : (
          <Tag color="default">Nu</Tag>
        ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 120,
      render: (_: unknown, r: PipelineStageConfig) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            size="small"
            onClick={() => openEdit(r)}
          />
          <Popconfirm
            title="Sigur ștergi acest stadiu?"
            onConfirm={() => deleteMut.mutate(r.id)}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              size="small"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate("/settings")}
            >
              Setări
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              <FunnelPlotOutlined /> Configurator Pipeline (F061)
            </Title>
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Adaugă Stadiu
          </Button>
        </Col>
      </Row>

      {/* Info alerts */}
      {!wonStage && stages.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message='Nu există stadiu marcat "Closed Won". Orice pipeline trebuie să aibă un stadiu de câștig.'
          style={{ marginBottom: 16 }}
        />
      )}
      {!lostStage && stages.length > 0 && (
        <Alert
          type="info"
          showIcon
          message='Niciun stadiu marcat "Closed Lost". Recomandăm adăugarea unui stadiu de pierdere.'
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Tag color="blue">{activeCount} stadii active</Tag>
        </Col>
        <Col>
          <Tag color="green">{wonStage ? `Won: ${wonStage.name}` : "Fără Won"}</Tag>
        </Col>
        <Col>
          <Tag color="red">{lostStage ? `Lost: ${lostStage.name}` : "Fără Lost"}</Tag>
        </Col>
      </Row>

      {/* Visual pipeline */}
      {stages.length > 0 && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", gap: 4, overflowX: "auto", padding: "8px 0" }}>
            {stages
              .filter((s) => s.is_active)
              .map((s, idx) => (
                <div
                  key={s.id}
                  style={{
                    flex: 1,
                    minWidth: 100,
                    textAlign: "center",
                    padding: "8px 12px",
                    background: s.color ?? "#f0f0f0",
                    color: "#fff",
                    borderRadius: 4,
                    fontSize: 12,
                    fontWeight: 600,
                    position: "relative",
                  }}
                >
                  {s.name}
                  <br />
                  <span style={{ fontSize: 10, opacity: 0.8 }}>
                    {s.win_probability ?? 0}%
                  </span>
                  {idx < stages.filter((st) => st.is_active).length - 1 && (
                    <span
                      style={{
                        position: "absolute",
                        right: -8,
                        top: "50%",
                        transform: "translateY(-50%)",
                        fontSize: 14,
                        zIndex: 1,
                      }}
                    >
                      →
                    </span>
                  )}
                </div>
              ))}
          </div>
        </Card>
      )}

      {/* Empty state with defaults */}
      {stages.length === 0 && !isLoading && (
        <Card style={{ marginBottom: 16 }}>
          <Alert
            type="info"
            showIcon
            message="Nu există stadii configurate"
            description="Poți crea stadii manual sau folosi template-ul implicit BuildWise."
            action={
              <Button
                size="small"
                type="primary"
                onClick={() => {
                  DEFAULT_STAGES.forEach((s, idx) => {
                    createMut.mutate({
                      ...s,
                      sort_order: idx + 1,
                      is_active: true,
                      is_closed_won: s.code === "post_vanzare",
                      is_closed_lost: false,
                      stagnation_days: 14,
                    });
                  });
                }}
              >
                Încarcă stadii implicite
              </Button>
            }
          />
        </Card>
      )}

      {/* Stages table */}
      <Card>
        <Table
          dataSource={stages}
          rowKey="id"
          columns={columns}
          loading={isLoading}
          pagination={false}
          size="small"
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingStage ? "Editează Stadiu" : "Stadiu Nou"}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSave}
        confirmLoading={createMut.isPending || updateMut.isPending}
        width={640}
        okText="Salvează"
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                name="name"
                label="Nume stadiu"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <Input placeholder="Ex: Evaluare Tehnică" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="code"
                label="Cod"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <Input placeholder="Ex: evaluare" disabled={!!editingStage} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="sort_order" label="Ordine">
                <InputNumber min={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="color" label="Culoare">
                <ColorPicker
                  onChange={(_: Color, hex: string) => form.setFieldValue("color", hex)}
                  showText
                />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="win_probability" label="Probabilitate %">
                <InputNumber min={0} max={100} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="stagnation_days" label="Stagnare (zile)">
                <Tooltip title="După câte zile se declanșează alerta de stagnare">
                  <InputNumber min={1} style={{ width: "100%" }} />
                </Tooltip>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="required_fields" label="Câmpuri obligatorii la acest stadiu">
            <Select
              mode="multiple"
              placeholder="Selectează câmpuri"
              options={REQUIRED_FIELD_OPTIONS}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="is_active" label="Activ" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_closed_won" label="Closed Won" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_closed_lost" label="Closed Lost" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Rules Modal */}
      <AutoAdvanceRulesModal
        open={rulesModalOpen}
        stage={rulesStage}
        stages={stages}
        onClose={() => setRulesModalOpen(false)}
        onSave={handleSaveRules}
      />
    </div>
  );
}

// ─── Auto-Advance Rules Sub-Modal ───────────────────────────────────────────

function AutoAdvanceRulesModal({
  open,
  stage,
  stages,
  onClose,
  onSave,
}: {
  open: boolean;
  stage: PipelineStageConfig | null;
  stages: PipelineStageConfig[];
  onClose: () => void;
  onSave: (rules: PipelineStageConfig["auto_advance_rules"]) => void;
}) {
  const [rules, setRules] = useState<
    { field: string; operator: string; value: string; target_stage_code: string }[]
  >([]);

  // Sync from stage when opening
  const stageRules = stage?.auto_advance_rules;
  useState(() => {
    if (stageRules) {
      setRules(stageRules.map((r) => ({ ...r })));
    } else {
      setRules([]);
    }
  });

  const addRule = () => {
    setRules((prev) => [
      ...prev,
      { field: "total_value", operator: "greater_than", value: "", target_stage_code: "" },
    ]);
  };

  const removeRule = (idx: number) => {
    setRules((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateRule = (idx: number, field: string, value: string) => {
    setRules((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, [field]: value } : r))
    );
  };

  const targetOptions = stages
    .filter((s) => s.id !== stage?.id && s.is_active)
    .map((s) => ({ value: s.code, label: s.name }));

  return (
    <Modal
      title={`Reguli avansare automată — ${stage?.name ?? ""}`}
      open={open}
      onCancel={onClose}
      onOk={() =>
        onSave(
          rules.map((r) => ({
            field: r.field,
            operator: r.operator as "equals" | "greater_than" | "not_empty" | "contains",
            value: r.value,
            target_stage_code: r.target_stage_code,
          }))
        )
      }
      width={800}
      okText="Salvează reguli"
    >
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="Regulile se verifică automat când o oportunitate este actualizată. Dacă toate condițiile sunt îndeplinite, oportunitatea avansează automat."
      />

      {rules.map((rule, idx) => (
        <Card key={idx} size="small" style={{ marginBottom: 8 }}>
          <Row gutter={8} align="middle">
            <Col span={5}>
              <Select
                value={rule.field}
                onChange={(v) => updateRule(idx, "field", v)}
                options={ADVANCE_FIELDS}
                style={{ width: "100%" }}
                size="small"
                placeholder="Câmp"
              />
            </Col>
            <Col span={5}>
              <Select
                value={rule.operator}
                onChange={(v) => updateRule(idx, "operator", v)}
                options={OPERATORS}
                style={{ width: "100%" }}
                size="small"
                placeholder="Operator"
              />
            </Col>
            <Col span={4}>
              <Input
                value={rule.value}
                onChange={(e) => updateRule(idx, "value", e.target.value)}
                size="small"
                placeholder="Valoare"
              />
            </Col>
            <Col span={1} style={{ textAlign: "center" }}>
              <Text type="secondary">→</Text>
            </Col>
            <Col span={7}>
              <Select
                value={rule.target_stage_code || undefined}
                onChange={(v) => updateRule(idx, "target_stage_code", v)}
                options={targetOptions}
                style={{ width: "100%" }}
                size="small"
                placeholder="Stadiu țintă"
              />
            </Col>
            <Col span={2}>
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                size="small"
                onClick={() => removeRule(idx)}
              />
            </Col>
          </Row>
        </Card>
      ))}

      <Button
        type="dashed"
        icon={<PlusOutlined />}
        onClick={addRule}
        block
        style={{ marginTop: 8 }}
      >
        Adaugă regulă
      </Button>

      {rules.length === 0 && (
        <Divider>
          <Text type="secondary">Fără reguli — avansarea se face manual</Text>
        </Divider>
      )}
    </Modal>
  );
}
