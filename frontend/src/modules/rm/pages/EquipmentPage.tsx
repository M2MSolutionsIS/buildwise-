/**
 * E-034 — Echipamente & Utilaje
 * F-codes: F107 (tracking echipamente — parte din resurse)
 * CRUD echipamente: inventar, status, mentenanță, cost
 */
import { useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Typography,
  Input,
  Select,
  Button,
  Table,
  Tag,
  Space,
  Row,
  Col,
  Card,
  App,
  Popconfirm,
  Tooltip,
  Modal,
  Form,
  DatePicker,
  InputNumber,
} from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined,
  ToolOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rmService, type EquipmentFilters } from "../services/rmService";
import type { Equipment, EquipmentCreate, EquipmentUpdate } from "../types";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";

const STATUS_COLORS: Record<string, string> = {
  available: "green",
  in_use: "blue",
  maintenance: "orange",
  out_of_service: "red",
};

const STATUS_LABELS: Record<string, string> = {
  available: "Disponibil",
  in_use: "În utilizare",
  maintenance: "Mentenanță",
  out_of_service: "Indisponibil",
};

export default function EquipmentPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const filters: EquipmentFilters = useMemo(
    () => ({
      page: Number(searchParams.get("page")) || 1,
      per_page: Number(searchParams.get("per_page")) || 20,
      status: searchParams.get("status") || undefined,
      category: searchParams.get("category") || undefined,
    }),
    [searchParams]
  );

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["rm-equipment", filters],
    queryFn: () => rmService.listEquipment(filters),
  });

  const createMutation = useMutation({
    mutationFn: (payload: EquipmentCreate) => rmService.createEquipment(payload),
    onSuccess: () => {
      message.success("Echipament creat.");
      queryClient.invalidateQueries({ queryKey: ["rm-equipment"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la creare."),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<EquipmentCreate> }) =>
      rmService.updateEquipment(id, payload),
    onSuccess: () => {
      message.success("Echipament actualizat.");
      queryClient.invalidateQueries({ queryKey: ["rm-equipment"] });
      setModalOpen(false);
      setEditingId(null);
      form.resetFields();
    },
    onError: () => message.error("Eroare la actualizare."),
  });

  const deleteMutation = useMutation({
    mutationFn: rmService.deleteEquipment,
    onSuccess: () => {
      message.success("Echipament șters.");
      queryClient.invalidateQueries({ queryKey: ["rm-equipment"] });
    },
    onError: () => message.error("Eroare la ștergere."),
  });

  const updateFilter = (key: string, value: string | undefined) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value);
    else params.delete(key);
    params.set("page", "1");
    setSearchParams(params);
  };

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (eq: Equipment) => {
    setEditingId(eq.id);
    form.setFieldsValue({
      ...eq,
      purchase_date: eq.purchase_date ? dayjs(eq.purchase_date) : undefined,
      next_maintenance_date: eq.next_maintenance_date ? dayjs(eq.next_maintenance_date) : undefined,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    const payload: EquipmentCreate = {
      ...values,
      purchase_date: values.purchase_date?.toISOString(),
    };
    const extra = values.next_maintenance_date
      ? { next_maintenance_date: values.next_maintenance_date.toISOString() }
      : {};
    if (editingId) {
      updateMutation.mutate({ id: editingId, payload: { ...payload, ...extra, status: values.status } as EquipmentUpdate });
    } else {
      createMutation.mutate(payload);
    }
  };

  const columns: ColumnsType<Equipment> = [
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
      title: "Categorie",
      dataIndex: "category",
      key: "category",
      width: 130,
      render: (v: string) => v || "—",
    },
    {
      title: "Producător / Model",
      key: "mfg",
      width: 180,
      render: (_, rec) =>
        [rec.manufacturer, rec.model].filter(Boolean).join(" — ") || "—",
    },
    {
      title: "Locație",
      dataIndex: "location",
      key: "location",
      width: 120,
      render: (v: string) => v || "—",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 120,
      render: (s: string) => (
        <Tag color={STATUS_COLORS[s] || "default"}>
          {STATUS_LABELS[s] || s}
        </Tag>
      ),
    },
    {
      title: "Rată zilnică",
      dataIndex: "daily_rate",
      key: "daily_rate",
      width: 110,
      render: (v: number, rec) => (v ? `${v} ${rec.currency}` : "—"),
    },
    {
      title: "Mentenanță",
      dataIndex: "next_maintenance_date",
      key: "maintenance",
      width: 120,
      render: (d: string) => {
        if (!d) return "—";
        const date = new Date(d);
        const isPast = date < new Date();
        return (
          <Tag color={isPast ? "red" : "default"}>
            {date.toLocaleDateString("ro-RO", { day: "2-digit", month: "short", year: "numeric" })}
          </Tag>
        );
      },
    },
    {
      title: "",
      key: "actions",
      width: 90,
      render: (_, rec) => (
        <Space size="small">
          <Tooltip title="Editează">
            <Button type="text" size="small" icon={<EditOutlined />} onClick={() => openEdit(rec)} />
          </Tooltip>
          <Popconfirm
            title="Sigur vrei să ștergi?"
            onConfirm={() => deleteMutation.mutate(rec.id)}
            okText="Da"
            cancelText="Nu"
          >
            <Tooltip title="Șterge">
              <Button type="text" danger size="small" icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const equipment = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          <ToolOutlined style={{ marginRight: 8 }} />
          Echipamente & Utilaje
        </Typography.Title>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </Tooltip>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Echipament nou
          </Button>
        </Space>
      </Row>

      {/* Filters */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: "100%" }}
              value={filters.status}
              onChange={(v) => updateFilter("status", v)}
              options={[
                { label: "Disponibil", value: "available" },
                { label: "În utilizare", value: "in_use" },
                { label: "Mentenanță", value: "maintenance" },
                { label: "Indisponibil", value: "out_of_service" },
              ]}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Categorie"
              allowClear
              style={{ width: "100%" }}
              value={filters.category}
              onChange={(v) => updateFilter("category", v)}
              options={[
                { label: "Utilaje grele", value: "utilaje_grele" },
                { label: "Scule electrice", value: "scule_electrice" },
                { label: "Vehicule", value: "vehicule" },
                { label: "Echipamente măsurare", value: "masurare" },
                { label: "Altele", value: "altele" },
              ]}
            />
          </Col>
        </Row>
      </Card>

      <Table<Equipment>
        rowKey="id"
        columns={columns}
        dataSource={equipment}
        loading={isLoading}
        pagination={{
          current: filters.page,
          pageSize: filters.per_page,
          total,
          showSizeChanger: true,
          showTotal: (t) => `Total: ${t} echipamente`,
          onChange: (page, pageSize) => {
            const params = new URLSearchParams(searchParams);
            params.set("page", String(page));
            params.set("per_page", String(pageSize));
            setSearchParams(params);
          },
        }}
        scroll={{ x: 1100 }}
        locale={{ emptyText: "Niciun echipament încă" }}
      />

      {/* Create/Edit Modal — E-034.M1 */}
      <Modal
        title={editingId ? "Editează echipament" : "Echipament nou"}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditingId(null); form.resetFields(); }}
        onOk={handleSubmit}
        okText={editingId ? "Salvează" : "Creează"}
        cancelText="Anulează"
        width={650}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item name="name" label="Denumire" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="code" label="Cod inventar">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="category" label="Categorie">
                <Select
                  allowClear
                  options={[
                    { label: "Utilaje grele", value: "utilaje_grele" },
                    { label: "Scule electrice", value: "scule_electrice" },
                    { label: "Vehicule", value: "vehicule" },
                    { label: "Echipamente măsurare", value: "masurare" },
                    { label: "Altele", value: "altele" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="manufacturer" label="Producător">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="model" label="Model">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="serial_number" label="Serie">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="location" label="Locație">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="daily_rate" label="Rată zilnică">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="purchase_date" label="Data achiziție">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="purchase_cost" label="Cost achiziție">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="next_maintenance_date" label="Următoarea mentenanță">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>
          {editingId && (
            <Form.Item name="status" label="Status">
              <Select
                options={[
                  { label: "Disponibil", value: "available" },
                  { label: "În utilizare", value: "in_use" },
                  { label: "Mentenanță", value: "maintenance" },
                  { label: "Indisponibil", value: "out_of_service" },
                ]}
              />
            </Form.Item>
          )}
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
