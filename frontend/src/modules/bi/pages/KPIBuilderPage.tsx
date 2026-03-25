/**
 * F148: KPI Builder — CRUD KPI definitions with formula, thresholds, assignment.
 * Specific P0 — Common (all prototypes).
 */
import { useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Table,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  Divider,
  Popconfirm,
  message,
  Spin,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ToolOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { biService } from "../services/biService";
import type { KPIDefinition } from "../../../types";

const { Title, Text } = Typography;
const { TextArea } = Input;

const MODULE_OPTIONS = [
  { label: "CRM", value: "crm" },
  { label: "Pipeline", value: "pipeline" },
  { label: "PM", value: "pm" },
  { label: "RM", value: "rm" },
  { label: "BI", value: "bi" },
];

const DISPLAY_TYPE_OPTIONS = [
  { label: "Card", value: "card" },
  { label: "Gauge", value: "gauge" },
  { label: "Chart", value: "chart" },
];

interface ThresholdRow {
  key: string;
  color: "green" | "yellow" | "red";
  label: string;
  min: number;
  max: number;
}

const DEFAULT_THRESHOLDS: ThresholdRow[] = [
  { key: "green", color: "green", label: "OK", min: 80, max: 100 },
  { key: "yellow", color: "yellow", label: "Atenție", min: 50, max: 79 },
  { key: "red", color: "red", label: "Critic", min: 0, max: 49 },
];

export default function KPIBuilderPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingKPI, setEditingKPI] = useState<KPIDefinition | null>(null);
  const [form] = Form.useForm();
  const [thresholds, setThresholds] = useState<ThresholdRow[]>(DEFAULT_THRESHOLDS);
  const [moduleFilter, setModuleFilter] = useState<string | undefined>(undefined);

  const { data: kpiData, isLoading } = useQuery({
    queryKey: ["kpis", moduleFilter],
    queryFn: () => biService.listKPIs({ module: moduleFilter, per_page: 100 }),
  });

  const kpis: KPIDefinition[] = kpiData?.data ?? [];

  const createMutation = useMutation({
    mutationFn: (payload: Partial<KPIDefinition>) => biService.createKPI(payload),
    onSuccess: () => {
      message.success("KPI creat cu succes");
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
      queryClient.invalidateQueries({ queryKey: ["kpi-dashboard"] });
      closeModal();
    },
    onError: () => message.error("Eroare la crearea KPI"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<KPIDefinition> }) =>
      biService.updateKPI(id, payload),
    onSuccess: () => {
      message.success("KPI actualizat cu succes");
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
      queryClient.invalidateQueries({ queryKey: ["kpi-dashboard"] });
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => biService.deleteKPI(id),
    onSuccess: () => {
      message.success("KPI șters");
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
      queryClient.invalidateQueries({ queryKey: ["kpi-dashboard"] });
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  function openCreate() {
    setEditingKPI(null);
    form.resetFields();
    setThresholds(DEFAULT_THRESHOLDS);
    setModalOpen(true);
  }

  function openEdit(kpi: KPIDefinition) {
    setEditingKPI(kpi);
    form.setFieldsValue({
      name: kpi.name,
      code: kpi.code,
      module: kpi.module,
      description: kpi.description,
      unit: kpi.unit,
      display_type: kpi.display_type,
      formula_text: kpi.formula_text,
      is_active: kpi.is_active,
      sort_order: kpi.sort_order,
    });
    if (kpi.thresholds && kpi.thresholds.length > 0) {
      setThresholds(
        kpi.thresholds.map((t) => ({
          key: t.color,
          color: t.color,
          label: t.label,
          min: t.min,
          max: t.max,
        }))
      );
    } else {
      setThresholds(DEFAULT_THRESHOLDS);
    }
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingKPI(null);
    form.resetFields();
  }

  async function handleSave() {
    const values = await form.validateFields();
    const payload: Partial<KPIDefinition> = {
      ...values,
      thresholds: thresholds.map(({ color, label, min, max }) => ({ color, label, min, max })),
    };

    if (editingKPI) {
      updateMutation.mutate({ id: editingKPI.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  }

  function updateThreshold(key: string, field: keyof ThresholdRow, value: unknown) {
    setThresholds((prev) =>
      prev.map((t) => (t.key === key ? { ...t, [field]: value } : t))
    );
  }

  const columns = [
    {
      title: "Nume",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: KPIDefinition) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: 11 }}>{record.code}</Text>
        </Space>
      ),
    },
    {
      title: "Modul",
      dataIndex: "module",
      key: "module",
      width: 100,
      render: (mod: string) => (
        <Tag color={mod === "pm" ? "green" : mod === "crm" ? "blue" : mod === "pipeline" ? "orange" : "purple"}>
          {mod.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Unitate",
      dataIndex: "unit",
      key: "unit",
      width: 80,
    },
    {
      title: "Afișare",
      dataIndex: "display_type",
      key: "display_type",
      width: 80,
      render: (dt: string) => <Tag>{dt}</Tag>,
    },
    {
      title: "Praguri",
      key: "thresholds",
      width: 180,
      render: (_: unknown, record: KPIDefinition) => {
        if (!record.thresholds || record.thresholds.length === 0) return <Text type="secondary">—</Text>;
        return (
          <Space size={4}>
            {record.thresholds.map((t) => (
              <Tag key={t.color} color={t.color === "green" ? "success" : t.color === "yellow" ? "warning" : "error"}>
                {t.min}–{t.max}
              </Tag>
            ))}
          </Space>
        );
      },
    },
    {
      title: "Activ",
      dataIndex: "is_active",
      key: "is_active",
      width: 70,
      render: (v: boolean) => (v ? <Tag color="green">Da</Tag> : <Tag>Nu</Tag>),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 100,
      render: (_: unknown, record: KPIDefinition) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm title="Ștergi acest KPI?" onConfirm={() => deleteMutation.mutate(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <ToolOutlined /> KPI Builder (F148)
          </Title>
          <Text type="secondary">Definire și configurare KPI-uri</Text>
        </Col>
        <Col>
          <Space>
            <Select
              placeholder="Filtrare modul"
              allowClear
              value={moduleFilter}
              onChange={setModuleFilter}
              options={MODULE_OPTIONS}
              style={{ width: 150 }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
              KPI Nou
            </Button>
          </Space>
        </Col>
      </Row>

      <Card>
        <Table
          dataSource={kpis}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 20 }}
          size="small"
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingKPI ? "Editare KPI" : "KPI Nou"}
        open={modalOpen}
        onCancel={closeModal}
        width={720}
        footer={[
          <Button key="cancel" onClick={closeModal}>Anulează</Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            loading={createMutation.isPending || updateMutation.isPending}
            onClick={handleSave}
          >
            Salvează
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical" initialValues={{ is_active: true, display_type: "card", sort_order: 0, module: "pm" }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="Nume KPI" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input placeholder="ex: Win Rate Pipeline" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="code" label="Cod" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input placeholder="ex: KPI_WIN_RATE" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="module" label="Modul" rules={[{ required: true }]}>
                <Select options={MODULE_OPTIONS} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit" label="Unitate">
                <Input placeholder="%, RON, ore, etc." />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="display_type" label="Tip afișare">
                <Select options={DISPLAY_TYPE_OPTIONS} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label="Descriere">
            <TextArea rows={2} placeholder="Descriere KPI..." />
          </Form.Item>

          <Form.Item name="formula_text" label="Formulă (text)">
            <TextArea rows={2} placeholder="ex: (opportunities_won / total_opportunities) * 100" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="sort_order" label="Ordine">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_active" label="Activ" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>

        <Divider>Praguri de Alertă</Divider>
        <Table
          dataSource={thresholds}
          rowKey="key"
          pagination={false}
          size="small"
          columns={[
            {
              title: "Culoare",
              dataIndex: "color",
              width: 90,
              render: (c: string) => (
                <Tag color={c === "green" ? "success" : c === "yellow" ? "warning" : "error"}>
                  {c.toUpperCase()}
                </Tag>
              ),
            },
            {
              title: "Etichetă",
              dataIndex: "label",
              render: (val: string, row: ThresholdRow) => (
                <Input
                  size="small"
                  value={val}
                  onChange={(e) => updateThreshold(row.key, "label", e.target.value)}
                />
              ),
            },
            {
              title: "Min",
              dataIndex: "min",
              width: 100,
              render: (val: number, row: ThresholdRow) => (
                <InputNumber
                  size="small"
                  value={val}
                  onChange={(v) => updateThreshold(row.key, "min", v ?? 0)}
                  style={{ width: "100%" }}
                />
              ),
            },
            {
              title: "Max",
              dataIndex: "max",
              width: 100,
              render: (val: number, row: ThresholdRow) => (
                <InputNumber
                  size="small"
                  value={val}
                  onChange={(v) => updateThreshold(row.key, "max", v ?? 0)}
                  style={{ width: "100%" }}
                />
              ),
            },
          ]}
        />
      </Modal>
    </div>
  );
}
