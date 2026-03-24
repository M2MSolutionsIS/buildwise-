/**
 * E-035 — Materiale & Stocuri
 * F-codes: F112 (Planificare achiziții), F113 (Facturi, NIR), F114 (Stocuri cu alerte)
 * Stocuri cu alerte minim, procurement, depozite
 */
import { useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Typography,
  Select,
  Button,
  Table,
  Tag,
  Space,
  Row,
  Col,
  Card,
  App,
  Tooltip,
  Modal,
  Form,
  Input,
  InputNumber,
  Alert,
  Tabs,
  Descriptions,
  Badge,
} from "antd";
import {
  PlusOutlined,
  ReloadOutlined,
  InboxOutlined,
  WarningOutlined,
  EditOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rmService, type MaterialFilters, type ProcurementFilters } from "../services/rmService";
import type { MaterialStock, MaterialStockCreate, ProcurementOrder, ProcurementOrderCreate, ProcurementLineItemCreate } from "../types";
import type { ColumnsType } from "antd/es/table";

export default function MaterialsStockPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [materialForm] = Form.useForm();
  const [procForm] = Form.useForm();

  const [materialModalOpen, setMaterialModalOpen] = useState(false);
  const [editingMaterialId, setEditingMaterialId] = useState<string | null>(null);
  const [procModalOpen, setProcModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("stock");

  // ─── Stock filters ────────────────────────────────────────────────────────
  const matFilters: MaterialFilters = useMemo(
    () => ({
      page: Number(searchParams.get("page")) || 1,
      per_page: Number(searchParams.get("per_page")) || 20,
      below_minimum: searchParams.get("below_minimum") === "true" || undefined,
      warehouse: searchParams.get("warehouse") || undefined,
    }),
    [searchParams]
  );

  const procFilters: ProcurementFilters = useMemo(
    () => ({
      page: Number(searchParams.get("proc_page")) || 1,
      per_page: 20,
      status: searchParams.get("proc_status") || undefined,
    }),
    [searchParams]
  );

  const { data: matData, isLoading: loadingMat, refetch: refetchMat } = useQuery({
    queryKey: ["rm-materials", matFilters],
    queryFn: () => rmService.listMaterials(matFilters),
  });

  const { data: procData, isLoading: loadingProc, refetch: refetchProc } = useQuery({
    queryKey: ["rm-procurement", procFilters],
    queryFn: () => rmService.listProcurement(procFilters),
  });

  // ─── Mutations ────────────────────────────────────────────────────────────
  const createMaterialMut = useMutation({
    mutationFn: (p: MaterialStockCreate) => rmService.createMaterial(p),
    onSuccess: () => {
      message.success("Material adăugat.");
      queryClient.invalidateQueries({ queryKey: ["rm-materials"] });
      setMaterialModalOpen(false);
      materialForm.resetFields();
    },
    onError: () => message.error("Eroare la creare material."),
  });

  const updateMaterialMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<MaterialStockCreate> }) =>
      rmService.updateMaterial(id, payload),
    onSuccess: () => {
      message.success("Material actualizat.");
      queryClient.invalidateQueries({ queryKey: ["rm-materials"] });
      setMaterialModalOpen(false);
      setEditingMaterialId(null);
      materialForm.resetFields();
    },
    onError: () => message.error("Eroare la actualizare."),
  });

  const createProcMut = useMutation({
    mutationFn: (p: ProcurementOrderCreate) => rmService.createProcurement(p),
    onSuccess: () => {
      message.success("Comandă creată.");
      queryClient.invalidateQueries({ queryKey: ["rm-procurement"] });
      setProcModalOpen(false);
      procForm.resetFields();
    },
    onError: () => message.error("Eroare la creare comandă."),
  });

  // ─── Helpers ──────────────────────────────────────────────────────────────
  const updateFilter = (key: string, value: string | undefined) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value);
    else params.delete(key);
    params.set("page", "1");
    setSearchParams(params);
  };

  const openCreateMaterial = () => {
    setEditingMaterialId(null);
    materialForm.resetFields();
    setMaterialModalOpen(true);
  };

  const openEditMaterial = (mat: MaterialStock) => {
    setEditingMaterialId(mat.id);
    materialForm.setFieldsValue(mat);
    setMaterialModalOpen(true);
  };

  const handleMaterialSubmit = async () => {
    const values = await materialForm.validateFields();
    if (editingMaterialId) {
      updateMaterialMut.mutate({ id: editingMaterialId, payload: values });
    } else {
      createMaterialMut.mutate(values);
    }
  };

  const handleProcSubmit = async () => {
    const values = await procForm.validateFields();
    const lineItems: ProcurementLineItemCreate[] = values.line_description
      ? [{ description: values.line_description, quantity: values.line_quantity || 1, unit_price: values.line_unit_price || 0 }]
      : [];
    const payload: ProcurementOrderCreate = {
      currency: values.currency || "RON",
      expected_delivery: values.expected_delivery,
      line_items: lineItems,
    };
    createProcMut.mutate(payload);
  };

  // ─── Stock Table Columns ──────────────────────────────────────────────────
  const materials = matData?.data ?? [];
  const matTotal = matData?.meta?.total ?? 0;
  const belowMinCount = materials.filter((m) => m.is_below_minimum).length;

  const matColumns: ColumnsType<MaterialStock> = [
    {
      title: "Denumire",
      dataIndex: "name",
      key: "name",
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: "Cod",
      dataIndex: "code",
      key: "code",
      width: 100,
      render: (v: string) => v || "—",
    },
    {
      title: "Depozit",
      dataIndex: "warehouse",
      key: "warehouse",
      width: 120,
      render: (v: string) => v || "—",
    },
    {
      title: "Stoc actual",
      key: "current",
      width: 120,
      render: (_, rec) => (
        <span style={{ color: rec.is_below_minimum ? "#ff4d4f" : undefined, fontWeight: rec.is_below_minimum ? 600 : 400 }}>
          {rec.current_quantity} {rec.unit_of_measure}
        </span>
      ),
      sorter: (a, b) => a.current_quantity - b.current_quantity,
    },
    {
      title: "Minim",
      key: "minimum",
      width: 100,
      render: (_, rec) => `${rec.minimum_quantity} ${rec.unit_of_measure}`,
    },
    {
      title: "Rezervat",
      dataIndex: "reserved_quantity",
      key: "reserved",
      width: 90,
      render: (v: number) => v || 0,
    },
    {
      title: "Cost unitar",
      key: "unit_cost",
      width: 110,
      render: (_, rec) => (rec.unit_cost ? `${rec.unit_cost} ${rec.currency}` : "—"),
    },
    {
      title: "Valoare totală",
      key: "total_value",
      width: 120,
      render: (_, rec) => (rec.total_value ? `${rec.total_value.toFixed(2)} ${rec.currency}` : "—"),
    },
    {
      title: "Status",
      key: "alert",
      width: 100,
      render: (_, rec) =>
        rec.is_below_minimum ? (
          <Tag color="red" icon={<WarningOutlined />}>Sub minim</Tag>
        ) : (
          <Tag color="green">OK</Tag>
        ),
    },
    {
      title: "",
      key: "actions",
      width: 60,
      render: (_, rec) => (
        <Tooltip title="Editează">
          <Button type="text" size="small" icon={<EditOutlined />} onClick={() => openEditMaterial(rec)} />
        </Tooltip>
      ),
    },
  ];

  // ─── Procurement Table Columns ────────────────────────────────────────────
  const procOrders = procData?.data ?? [];
  const procTotal = procData?.meta?.total ?? 0;

  const PROC_STATUS_COLORS: Record<string, string> = {
    draft: "default",
    submitted: "blue",
    approved: "cyan",
    ordered: "processing",
    partial_received: "orange",
    received: "green",
    cancelled: "red",
  };

  const procColumns: ColumnsType<ProcurementOrder> = [
    {
      title: "Nr. comandă",
      dataIndex: "order_number",
      key: "order_number",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 130,
      render: (s: string) => (
        <Tag color={PROC_STATUS_COLORS[s] || "default"}>
          {s?.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase())}
        </Tag>
      ),
    },
    {
      title: "Total",
      dataIndex: "total_amount",
      key: "total",
      width: 120,
      render: (v: number, rec) => `${v?.toFixed(2) || 0} ${rec.currency}`,
    },
    {
      title: "Articole",
      key: "items",
      width: 90,
      render: (_, rec) => rec.line_items?.length || 0,
    },
    {
      title: "Livrare așteptată",
      dataIndex: "expected_delivery",
      key: "expected",
      width: 130,
      render: (d: string) =>
        d ? new Date(d).toLocaleDateString("ro-RO", { day: "2-digit", month: "short", year: "numeric" }) : "—",
    },
    {
      title: "Creat",
      dataIndex: "created_at",
      key: "created",
      width: 110,
      render: (d: string) =>
        d ? new Date(d).toLocaleDateString("ro-RO", { day: "2-digit", month: "short", year: "numeric" }) : "—",
    },
  ];

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          <InboxOutlined style={{ marginRight: 8 }} />
          Materiale & Stocuri
        </Typography.Title>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => { refetchMat(); refetchProc(); }} />
          </Tooltip>
        </Space>
      </Row>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "stock",
            label: (
              <span>
                <InboxOutlined /> Stocuri (F114)
                {belowMinCount > 0 && <Badge count={belowMinCount} offset={[8, -2]} size="small" />}
              </span>
            ),
            children: (
              <>
                {/* Filters */}
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Row gutter={[12, 12]} align="middle">
                    <Col xs={12} sm={6} md={4}>
                      <Select
                        placeholder="Depozit"
                        allowClear
                        style={{ width: "100%" }}
                        value={matFilters.warehouse}
                        onChange={(v) => updateFilter("warehouse", v)}
                        options={[
                          { label: "Depozit central", value: "central" },
                          { label: "Șantier A", value: "santier_a" },
                          { label: "Șantier B", value: "santier_b" },
                        ]}
                      />
                    </Col>
                    <Col xs={12} sm={6} md={4}>
                      <Select
                        placeholder="Alertă"
                        allowClear
                        style={{ width: "100%" }}
                        value={matFilters.below_minimum ? "true" : undefined}
                        onChange={(v) => updateFilter("below_minimum", v)}
                        options={[
                          { label: "Sub minim", value: "true" },
                        ]}
                      />
                    </Col>
                    <Col flex="auto" style={{ textAlign: "right" }}>
                      <Button type="primary" icon={<PlusOutlined />} onClick={openCreateMaterial}>
                        Material nou
                      </Button>
                    </Col>
                  </Row>
                </Card>

                {matFilters.below_minimum && materials.length > 0 && (
                  <Alert
                    type="warning"
                    showIcon
                    message={`${materials.length} materiale sub stocul minim`}
                    style={{ marginBottom: 12 }}
                  />
                )}

                <Table<MaterialStock>
                  rowKey="id"
                  columns={matColumns}
                  dataSource={materials}
                  loading={loadingMat}
                  pagination={{
                    current: matFilters.page,
                    pageSize: matFilters.per_page,
                    total: matTotal,
                    showSizeChanger: true,
                    showTotal: (t) => `Total: ${t} materiale`,
                    onChange: (page, pageSize) => {
                      const params = new URLSearchParams(searchParams);
                      params.set("page", String(page));
                      params.set("per_page", String(pageSize));
                      setSearchParams(params);
                    },
                  }}
                  scroll={{ x: 1100 }}
                  locale={{ emptyText: "Niciun material în stoc" }}
                />
              </>
            ),
          },
          {
            key: "procurement",
            label: (
              <span>
                <ShoppingCartOutlined /> Achiziții (F112, F113)
              </span>
            ),
            children: (
              <>
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Row gutter={[12, 12]} align="middle">
                    <Col xs={12} sm={6} md={4}>
                      <Select
                        placeholder="Status"
                        allowClear
                        style={{ width: "100%" }}
                        value={procFilters.status}
                        onChange={(v) => updateFilter("proc_status", v)}
                        options={[
                          { label: "Draft", value: "draft" },
                          { label: "Trimisă", value: "submitted" },
                          { label: "Aprobată", value: "approved" },
                          { label: "Comandată", value: "ordered" },
                          { label: "Recepționată", value: "received" },
                          { label: "Anulată", value: "cancelled" },
                        ]}
                      />
                    </Col>
                    <Col flex="auto" style={{ textAlign: "right" }}>
                      <Button type="primary" icon={<PlusOutlined />} onClick={() => { procForm.resetFields(); setProcModalOpen(true); }}>
                        Comandă nouă
                      </Button>
                    </Col>
                  </Row>
                </Card>

                <Table<ProcurementOrder>
                  rowKey="id"
                  columns={procColumns}
                  dataSource={procOrders}
                  loading={loadingProc}
                  pagination={{
                    current: procFilters.page,
                    pageSize: 20,
                    total: procTotal,
                    showTotal: (t) => `Total: ${t} comenzi`,
                  }}
                  scroll={{ x: 800 }}
                  locale={{ emptyText: "Nicio comandă de achiziție" }}
                  expandable={{
                    expandedRowRender: (rec) => (
                      <Descriptions column={2} size="small" bordered>
                        {rec.line_items?.map((li, idx) => (
                          <Descriptions.Item key={idx} label={`Articol ${idx + 1}`} span={2}>
                            {li.description} — {li.quantity} x {li.unit_price} = {li.total_price} {rec.currency}
                          </Descriptions.Item>
                        ))}
                      </Descriptions>
                    ),
                    rowExpandable: (rec) => (rec.line_items?.length ?? 0) > 0,
                  }}
                />
              </>
            ),
          },
        ]}
      />

      {/* Material Create/Edit Modal */}
      <Modal
        title={editingMaterialId ? "Editează material" : "Material nou"}
        open={materialModalOpen}
        onCancel={() => { setMaterialModalOpen(false); setEditingMaterialId(null); materialForm.resetFields(); }}
        onOk={handleMaterialSubmit}
        okText={editingMaterialId ? "Salvează" : "Adaugă"}
        cancelText="Anulează"
        confirmLoading={createMaterialMut.isPending || updateMaterialMut.isPending}
      >
        <Form form={materialForm} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item name="name" label="Denumire" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="code" label="Cod">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="unit_of_measure" label="UM" initialValue="buc">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="current_quantity" label="Cantitate">
                <InputNumber style={{ width: "100%" }} min={0} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="minimum_quantity" label="Minim alertă">
                <InputNumber style={{ width: "100%" }} min={0} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="unit_cost" label="Cost unitar">
                <InputNumber style={{ width: "100%" }} min={0} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="warehouse" label="Depozit">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="location" label="Locație">
                <Input />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Procurement Quick Order — E-035.M1 */}
      <Modal
        title="Comandă rapidă achiziție"
        open={procModalOpen}
        onCancel={() => { setProcModalOpen(false); procForm.resetFields(); }}
        onOk={handleProcSubmit}
        okText="Creează comandă"
        cancelText="Anulează"
        confirmLoading={createProcMut.isPending}
      >
        <Form form={procForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="line_description" label="Descriere articol" rules={[{ required: true, message: "Obligatoriu" }]}>
            <Input placeholder="Ex: Ciment CEM II/A-LL 42.5R" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="line_quantity" label="Cantitate" initialValue={1}>
                <InputNumber style={{ width: "100%" }} min={0.01} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="line_unit_price" label="Preț unitar">
                <InputNumber style={{ width: "100%" }} min={0} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="currency" label="Monedă" initialValue="RON">
                <Select options={[{ label: "RON", value: "RON" }, { label: "EUR", value: "EUR" }]} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="expected_delivery" label="Livrare așteptată">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
