/**
 * F131: Configurator RM — Categorii resurse, unități de măsură, praguri alerte
 * Specific P2+P3. Parte din F136 Configurator Global ERP.
 *
 * 3 tab-uri:
 * - Categorii Resurse (employee / equipment / material)
 * - Unități de Măsură (timp, cantitate, greutate, volum, suprafață, lungime)
 * - Praguri Alerte (min/max cu warning/critical per metric)
 */
import { useState, useCallback } from "react";
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
  Typography,
  Row,
  Col,
  message,
  Tabs,
  Popconfirm,
  Alert,
  Badge,
  Statistic,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  ToolOutlined,
  TeamOutlined,
  ExperimentOutlined,
  AlertOutlined,
  DashboardOutlined,
  ColumnWidthOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { systemService } from "../services/systemService";
import type {
  RMResourceCategory,
  RMUnitOfMeasure,
  RMAlertThreshold,
} from "../../../types";

const { Title, Text } = Typography;

// ─── Constants ──────────────────────────────────────────────────────────────

const RESOURCE_TYPES = [
  { value: "employee", label: "Angajat", icon: <TeamOutlined />, color: "#1677ff" },
  { value: "equipment", label: "Echipament", icon: <ToolOutlined />, color: "#fa8c16" },
  { value: "material", label: "Material", icon: <ExperimentOutlined />, color: "#52c41a" },
];

const UNIT_CATEGORIES = [
  { value: "time", label: "Timp" },
  { value: "quantity", label: "Cantitate" },
  { value: "weight", label: "Greutate" },
  { value: "volume", label: "Volum" },
  { value: "area", label: "Suprafață" },
  { value: "length", label: "Lungime" },
];

const THRESHOLD_METRICS = [
  { value: "utilization_percent", label: "Utilizare %" },
  { value: "hours_overtime", label: "Ore suplimentare" },
  { value: "stock_level", label: "Nivel stoc" },
  { value: "allocation_percent", label: "Alocare %" },
  { value: "cost_variance", label: "Varianță cost %" },
  { value: "maintenance_due_days", label: "Zile până la mentenanță" },
  { value: "budget_consumed", label: "Buget consumat %" },
];

const APPLIES_TO_OPTIONS = [
  { value: "all", label: "Toate resursele" },
  { value: "employee", label: "Doar angajați" },
  { value: "equipment", label: "Doar echipamente" },
  { value: "material", label: "Doar materiale" },
];

// ─── Component ──────────────────────────────────────────────────────────────

export default function RMConfiguratorPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("categories");

  // ─── Categories ───────────────────────────────────────────────────────────

  const { data: catsData, isLoading: catsLoading } = useQuery({
    queryKey: ["rm-categories"],
    queryFn: () => systemService.listRMCategories(),
  });
  const categories = catsData?.data ?? [];

  const [catModalOpen, setCatModalOpen] = useState(false);
  const [editingCat, setEditingCat] = useState<RMResourceCategory | null>(null);
  const [catForm] = Form.useForm();

  const createCatMut = useMutation({
    mutationFn: (p: Partial<RMResourceCategory>) => systemService.createRMCategory(p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-categories"] }); message.success("Categorie creată"); setCatModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const updateCatMut = useMutation({
    mutationFn: ({ id, p }: { id: string; p: Partial<RMResourceCategory> }) => systemService.updateRMCategory(id, p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-categories"] }); message.success("Categorie actualizată"); setCatModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const deleteCatMut = useMutation({
    mutationFn: (id: string) => systemService.deleteRMCategory(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-categories"] }); message.success("Șters"); },
  });

  const openCatCreate = useCallback(() => {
    setEditingCat(null);
    catForm.resetFields();
    catForm.setFieldsValue({ is_active: true, sort_order: categories.length + 1 });
    setCatModalOpen(true);
  }, [catForm, categories.length]);

  const openCatEdit = useCallback((cat: RMResourceCategory) => {
    setEditingCat(cat);
    catForm.setFieldsValue(cat);
    setCatModalOpen(true);
  }, [catForm]);

  const saveCat = useCallback(async () => {
    const vals = await catForm.validateFields();
    if (editingCat) updateCatMut.mutate({ id: editingCat.id, p: vals });
    else createCatMut.mutate(vals);
  }, [catForm, editingCat, updateCatMut, createCatMut]);

  // ─── Units ────────────────────────────────────────────────────────────────

  const { data: unitsData, isLoading: unitsLoading } = useQuery({
    queryKey: ["rm-units"],
    queryFn: () => systemService.listRMUnits(),
  });
  const units = unitsData?.data ?? [];

  const [unitModalOpen, setUnitModalOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState<RMUnitOfMeasure | null>(null);
  const [unitForm] = Form.useForm();

  const createUnitMut = useMutation({
    mutationFn: (p: Partial<RMUnitOfMeasure>) => systemService.createRMUnit(p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-units"] }); message.success("Unitate creată"); setUnitModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const updateUnitMut = useMutation({
    mutationFn: ({ id, p }: { id: string; p: Partial<RMUnitOfMeasure> }) => systemService.updateRMUnit(id, p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-units"] }); message.success("Unitate actualizată"); setUnitModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const deleteUnitMut = useMutation({
    mutationFn: (id: string) => systemService.deleteRMUnit(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-units"] }); message.success("Șters"); },
  });

  const openUnitCreate = useCallback(() => {
    setEditingUnit(null);
    unitForm.resetFields();
    unitForm.setFieldsValue({ is_active: true, sort_order: units.length + 1 });
    setUnitModalOpen(true);
  }, [unitForm, units.length]);

  const openUnitEdit = useCallback((u: RMUnitOfMeasure) => {
    setEditingUnit(u);
    unitForm.setFieldsValue(u);
    setUnitModalOpen(true);
  }, [unitForm]);

  const saveUnit = useCallback(async () => {
    const vals = await unitForm.validateFields();
    if (editingUnit) updateUnitMut.mutate({ id: editingUnit.id, p: vals });
    else createUnitMut.mutate(vals);
  }, [unitForm, editingUnit, updateUnitMut, createUnitMut]);

  // ─── Thresholds ───────────────────────────────────────────────────────────

  const { data: thresholdsData, isLoading: thresholdsLoading } = useQuery({
    queryKey: ["rm-thresholds"],
    queryFn: () => systemService.listRMThresholds(),
  });
  const thresholds = thresholdsData?.data ?? [];

  const [thresholdModalOpen, setThresholdModalOpen] = useState(false);
  const [editingThreshold, setEditingThreshold] = useState<RMAlertThreshold | null>(null);
  const [thresholdForm] = Form.useForm();

  const createThresholdMut = useMutation({
    mutationFn: (p: Partial<RMAlertThreshold>) => systemService.createRMThreshold(p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-thresholds"] }); message.success("Prag creat"); setThresholdModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const updateThresholdMut = useMutation({
    mutationFn: ({ id, p }: { id: string; p: Partial<RMAlertThreshold> }) => systemService.updateRMThreshold(id, p),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-thresholds"] }); message.success("Prag actualizat"); setThresholdModalOpen(false); },
    onError: () => message.error("Eroare"),
  });
  const deleteThresholdMut = useMutation({
    mutationFn: (id: string) => systemService.deleteRMThreshold(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rm-thresholds"] }); message.success("Șters"); },
  });

  const openThresholdCreate = useCallback(() => {
    setEditingThreshold(null);
    thresholdForm.resetFields();
    thresholdForm.setFieldsValue({ is_active: true, notification_enabled: true, threshold_type: "max", applies_to: "all" });
    setThresholdModalOpen(true);
  }, [thresholdForm]);

  const openThresholdEdit = useCallback((t: RMAlertThreshold) => {
    setEditingThreshold(t);
    thresholdForm.setFieldsValue(t);
    setThresholdModalOpen(true);
  }, [thresholdForm]);

  const saveThreshold = useCallback(async () => {
    const vals = await thresholdForm.validateFields();
    if (editingThreshold) updateThresholdMut.mutate({ id: editingThreshold.id, p: vals });
    else createThresholdMut.mutate(vals);
  }, [thresholdForm, editingThreshold, updateThresholdMut, createThresholdMut]);

  // ─── Tab: Categories ──────────────────────────────────────────────────────

  const categoriesTab = (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Text strong>Categorii resurse</Text>
            <Badge count={categories.length} style={{ backgroundColor: "#1677ff" }} />
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCatCreate} size="small">
            Adaugă categorie
          </Button>
        </Col>
      </Row>
      <Table
        dataSource={categories}
        rowKey="id"
        loading={catsLoading}
        size="small"
        pagination={false}
        columns={[
          { title: "#", dataIndex: "sort_order", key: "sort", width: 50 },
          {
            title: "Categorie", dataIndex: "name", key: "name",
            render: (v: string, r: RMResourceCategory) => (
              <Space>
                {RESOURCE_TYPES.find((t) => t.value === r.resource_type)?.icon}
                <Text strong>{v}</Text>
              </Space>
            ),
          },
          { title: "Cod", dataIndex: "code", key: "code", width: 100, render: (v: string) => <Tag>{v}</Tag> },
          {
            title: "Tip resursă", dataIndex: "resource_type", key: "type", width: 120,
            render: (v: string) => {
              const cfg = RESOURCE_TYPES.find((t) => t.value === v);
              return <Tag color={cfg?.color}>{cfg?.label ?? v}</Tag>;
            },
          },
          { title: "UM Default", dataIndex: "default_unit", key: "unit", width: 80 },
          {
            title: "Activ", dataIndex: "is_active", key: "active", width: 60,
            render: (v: boolean) => v ? <Tag color="green">Da</Tag> : <Tag>Nu</Tag>,
          },
          {
            title: "Acțiuni", key: "actions", width: 100,
            render: (_: unknown, r: RMResourceCategory) => (
              <Space>
                <Button type="text" icon={<EditOutlined />} size="small" onClick={() => openCatEdit(r)} />
                <Popconfirm title="Ștergi?" onConfirm={() => deleteCatMut.mutate(r.id)}>
                  <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
    </>
  );

  // ─── Tab: Units ───────────────────────────────────────────────────────────

  const unitsTab = (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Text strong>Unități de măsură</Text>
            <Badge count={units.length} style={{ backgroundColor: "#52c41a" }} />
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={openUnitCreate} size="small">
            Adaugă unitate
          </Button>
        </Col>
      </Row>
      <Table
        dataSource={units}
        rowKey="id"
        loading={unitsLoading}
        size="small"
        pagination={false}
        columns={[
          { title: "#", dataIndex: "sort_order", key: "sort", width: 50 },
          { title: "Nume", dataIndex: "name", key: "name", render: (v: string) => <Text strong>{v}</Text> },
          { title: "Cod", dataIndex: "code", key: "code", width: 80, render: (v: string) => <Tag>{v}</Tag> },
          {
            title: "Categorie", dataIndex: "category", key: "cat", width: 120,
            render: (v: string) => <Tag color="blue">{UNIT_CATEGORIES.find((c) => c.value === v)?.label ?? v}</Tag>,
          },
          {
            title: "Activ", dataIndex: "is_active", key: "active", width: 60,
            render: (v: boolean) => v ? <Tag color="green">Da</Tag> : <Tag>Nu</Tag>,
          },
          {
            title: "Acțiuni", key: "actions", width: 100,
            render: (_: unknown, r: RMUnitOfMeasure) => (
              <Space>
                <Button type="text" icon={<EditOutlined />} size="small" onClick={() => openUnitEdit(r)} />
                <Popconfirm title="Ștergi?" onConfirm={() => deleteUnitMut.mutate(r.id)}>
                  <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
    </>
  );

  // ─── Tab: Thresholds ──────────────────────────────────────────────────────

  const thresholdsTab = (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Text strong>Praguri alerte</Text>
            <Badge count={thresholds.length} style={{ backgroundColor: "#ff4d4f" }} />
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={openThresholdCreate} size="small">
            Adaugă prag
          </Button>
        </Col>
      </Row>
      {thresholds.length === 0 && !thresholdsLoading && (
        <Alert
          type="info"
          showIcon
          message="Niciun prag configurat"
          description="Adaugă praguri de alertă pentru utilizare resurse, nivel stoc, cost etc."
          style={{ marginBottom: 16 }}
        />
      )}
      <Table
        dataSource={thresholds}
        rowKey="id"
        loading={thresholdsLoading}
        size="small"
        pagination={false}
        columns={[
          {
            title: "Metric", dataIndex: "metric", key: "metric", width: 180,
            render: (v: string) => <Text strong>{THRESHOLD_METRICS.find((m) => m.value === v)?.label ?? v}</Text>,
          },
          {
            title: "Tip", dataIndex: "threshold_type", key: "type", width: 80,
            render: (v: string) => <Tag>{v.toUpperCase()}</Tag>,
          },
          {
            title: "Warning", dataIndex: "warning_value", key: "warn", width: 90,
            align: "center" as const,
            render: (v: number) => <Statistic value={v} valueStyle={{ fontSize: 14, color: "#faad14" }} />,
          },
          {
            title: "Critical", dataIndex: "critical_value", key: "crit", width: 90,
            align: "center" as const,
            render: (v: number) => <Statistic value={v} valueStyle={{ fontSize: 14, color: "#ff4d4f" }} />,
          },
          {
            title: "Se aplică la", dataIndex: "applies_to", key: "applies", width: 130,
            render: (v: string) => <Tag>{APPLIES_TO_OPTIONS.find((a) => a.value === v)?.label ?? v}</Tag>,
          },
          {
            title: "Notificare", dataIndex: "notification_enabled", key: "notif", width: 80,
            render: (v: boolean) => v ? <Tag color="green">Da</Tag> : <Tag>Nu</Tag>,
          },
          {
            title: "Activ", dataIndex: "is_active", key: "active", width: 60,
            render: (v: boolean) => v ? <Tag color="green">Da</Tag> : <Tag>Nu</Tag>,
          },
          {
            title: "Acțiuni", key: "actions", width: 100,
            render: (_: unknown, r: RMAlertThreshold) => (
              <Space>
                <Button type="text" icon={<EditOutlined />} size="small" onClick={() => openThresholdEdit(r)} />
                <Popconfirm title="Ștergi?" onConfirm={() => deleteThresholdMut.mutate(r.id)}>
                  <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />
    </>
  );

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/settings")}>
              Setări
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              <ToolOutlined /> Configurator RM (F131)
            </Title>
            <Tag color="orange">P2+P3</Tag>
          </Space>
        </Col>
      </Row>

      {/* Summary stats */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card size="small">
            <Statistic title="Categorii resurse" value={categories.length} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic title="Unități de măsură" value={units.length} prefix={<ColumnWidthOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Praguri alerte"
              value={thresholds.length}
              prefix={<AlertOutlined />}
              valueStyle={{ color: thresholds.filter((t) => t.is_active).length > 0 ? "#ff4d4f" : undefined }}
            />
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: "categories",
              label: (
                <Space>
                  <DashboardOutlined />
                  Categorii Resurse
                  <Badge count={categories.length} size="small" />
                </Space>
              ),
              children: categoriesTab,
            },
            {
              key: "units",
              label: (
                <Space>
                  <ColumnWidthOutlined />
                  Unități Măsură
                  <Badge count={units.length} size="small" />
                </Space>
              ),
              children: unitsTab,
            },
            {
              key: "thresholds",
              label: (
                <Space>
                  <AlertOutlined />
                  Praguri Alerte
                  <Badge count={thresholds.length} size="small" />
                </Space>
              ),
              children: thresholdsTab,
            },
          ]}
        />
      </Card>

      {/* Category Modal */}
      <Modal
        title={editingCat ? "Editează Categorie" : "Categorie Nouă"}
        open={catModalOpen}
        onCancel={() => setCatModalOpen(false)}
        onOk={saveCat}
        confirmLoading={createCatMut.isPending || updateCatMut.isPending}
        okText="Salvează"
      >
        <Form form={catForm} layout="vertical">
          <Form.Item name="name" label="Nume" rules={[{ required: true }]}>
            <Input placeholder="Ex: Muncitori calificați" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="code" label="Cod" rules={[{ required: true }]}>
                <Input placeholder="Ex: muncitori_cal" disabled={!!editingCat} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="resource_type" label="Tip resursă" rules={[{ required: true }]}>
                <Select options={RESOURCE_TYPES.map((t) => ({ value: t.value, label: t.label }))} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="default_unit" label="UM default">
                <Input placeholder="Ex: ore, buc, kg" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="sort_order" label="Ordine">
                <InputNumber min={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="is_active" label="Activ" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Unit Modal */}
      <Modal
        title={editingUnit ? "Editează Unitate" : "Unitate Nouă"}
        open={unitModalOpen}
        onCancel={() => setUnitModalOpen(false)}
        onOk={saveUnit}
        confirmLoading={createUnitMut.isPending || updateUnitMut.isPending}
        okText="Salvează"
      >
        <Form form={unitForm} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="Nume" rules={[{ required: true }]}>
                <Input placeholder="Ex: Ore lucrate" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="code" label="Cod" rules={[{ required: true }]}>
                <Input placeholder="Ex: ore" disabled={!!editingUnit} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="Categorie" rules={[{ required: true }]}>
                <Select options={UNIT_CATEGORIES} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="sort_order" label="Ordine">
                <InputNumber min={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="is_active" label="Activ" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Threshold Modal */}
      <Modal
        title={editingThreshold ? "Editează Prag" : "Prag Alertă Nou"}
        open={thresholdModalOpen}
        onCancel={() => setThresholdModalOpen(false)}
        onOk={saveThreshold}
        confirmLoading={createThresholdMut.isPending || updateThresholdMut.isPending}
        okText="Salvează"
        width={560}
      >
        <Form form={thresholdForm} layout="vertical">
          <Form.Item name="metric" label="Metric" rules={[{ required: true }]}>
            <Select options={THRESHOLD_METRICS} placeholder="Selectează metric" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="threshold_type" label="Tip prag" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: "min", label: "Minim" },
                    { value: "max", label: "Maxim" },
                    { value: "range", label: "Interval" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="warning_value" label="Warning" rules={[{ required: true }]}>
                <InputNumber style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="critical_value" label="Critical" rules={[{ required: true }]}>
                <InputNumber style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="applies_to" label="Se aplică la" rules={[{ required: true }]}>
                <Select options={APPLIES_TO_OPTIONS} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="notification_enabled" label="Notificare" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="is_active" label="Activ" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
