/**
 * E-004: Products & Services Catalog — F017
 * CRUD catalog with category filtering, search, status toggle.
 */
import { useState } from "react";
import {
  Typography,
  Button,
  Table,
  Space,
  Tag,
  Input,
  Select,
  Modal,
  Form,
  InputNumber,
  App,
  Row,
  Col,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ShoppingOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productService, type ProductCreate } from "../../pipeline/services/productService";
import { useTranslation } from "../../../i18n";
import { confirmDelete } from "../../../components/ConfirmDelete";
import EmptyState from "../../../components/EmptyState";
import type { Product } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const { Title } = Typography;

const PRODUCT_TYPES = ["product", "service", "material", "equipment"];
const UNITS = ["buc", "mp", "ml", "kg", "t", "ore", "zi", "lună", "set", "lot"];

export default function ProductsServicesPage() {
  const t = useTranslation();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ["products", search, typeFilter, statusFilter],
    queryFn: () =>
      productService.list({
        search: search || undefined,
        product_type: typeFilter,
        is_active: statusFilter,
      }),
  });

  const createMut = useMutation({
    mutationFn: (payload: ProductCreate) => productService.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      message.success("Produs creat cu succes");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ProductCreate> }) =>
      productService.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      message.success("Produs actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => productService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      message.success("Produs șters");
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ product_type: "product", unit_of_measure: "buc", currency: "RON", vat_rate: 19, is_active: true });
    setModalOpen(true);
  };

  const openEdit = (record: Product) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditing(null);
    form.resetFields();
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    if (editing) {
      updateMut.mutate({ id: editing.id, payload: values });
    } else {
      createMut.mutate(values);
    }
  };

  const columns: ColumnsType<Product> = [
    {
      title: t.crm.productCode,
      dataIndex: "code",
      key: "code",
      width: 120,
      sorter: (a, b) => a.code.localeCompare(b.code),
      render: (code: string) => (
        <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{code}</span>
      ),
    },
    {
      title: t.common.name,
      dataIndex: "name",
      key: "name",
      ellipsis: true,
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: t.crm.productType,
      dataIndex: "product_type",
      key: "product_type",
      width: 120,
      render: (type: string) => {
        const colors: Record<string, string> = {
          product: "blue",
          service: "purple",
          material: "green",
          equipment: "orange",
        };
        return <Tag color={colors[type] || "default"}>{type}</Tag>;
      },
    },
    {
      title: t.crm.unitOfMeasure,
      dataIndex: "unit_of_measure",
      key: "unit_of_measure",
      width: 100,
    },
    {
      title: t.crm.unitPrice,
      dataIndex: "unit_price",
      key: "unit_price",
      width: 130,
      align: "right",
      sorter: (a, b) => a.unit_price - b.unit_price,
      render: (price: number, record: Product) =>
        `${price.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} ${record.currency}`,
    },
    {
      title: t.crm.vatRate,
      dataIndex: "vat_rate",
      key: "vat_rate",
      width: 80,
      align: "right",
      render: (rate: number) => `${rate}%`,
    },
    {
      title: t.common.status,
      dataIndex: "is_active",
      key: "is_active",
      width: 100,
      render: (active: boolean) => (
        <Tag color={active ? "green" : "default"}>
          {active ? t.common.active : t.common.inactive}
        </Tag>
      ),
    },
    {
      title: t.common.actions,
      key: "actions",
      width: 100,
      render: (_: unknown, record: Product) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(record)}
          />
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() =>
              confirmDelete({
                title: `Șterge ${record.name}?`,
                content: "Produsul va fi șters permanent.",
                onOk: () => deleteMut.mutate(record.id),
              })
            }
          />
        </Space>
      ),
    },
  ];

  const products = data?.data || [];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <ShoppingOutlined style={{ fontSize: 20, color: "#1E40AF" }} />
          <Title level={4} style={{ margin: 0 }}>
            {t.crm.products}
          </Title>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          {t.common.add}
        </Button>
      </div>

      {/* Filters */}
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Input
            placeholder={t.common.search}
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
        </Col>
        <Col xs={12} sm={5}>
          <Select
            placeholder={t.crm.productType}
            value={typeFilter}
            onChange={setTypeFilter}
            allowClear
            style={{ width: "100%" }}
            options={PRODUCT_TYPES.map((pt) => ({ label: pt, value: pt }))}
          />
        </Col>
        <Col xs={12} sm={5}>
          <Select
            placeholder={t.common.status}
            value={statusFilter}
            onChange={setStatusFilter}
            allowClear
            style={{ width: "100%" }}
            options={[
              { label: t.common.active, value: true },
              { label: t.common.inactive, value: false },
            ]}
          />
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={products}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `${total} produse` }}
        size="small"
        scroll={{ x: 900 }}
        locale={{
          emptyText: (
            <EmptyState
              icon={<ShoppingOutlined style={{ color: "#1E40AF" }} />}
              title="Niciun produs sau serviciu"
              description="Adaugă primul produs pentru a-l folosi în oferte."
              actionLabel={t.common.add}
              onAction={openCreate}
            />
          ),
        }}
      />

      {/* Create/Edit Modal */}
      <Modal
        title={editing ? `${t.common.edit} — ${editing.name}` : t.common.create}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSubmit}
        confirmLoading={createMut.isPending || updateMut.isPending}
        width={600}
        okText={t.common.save}
        cancelText={t.common.cancel}
      >
        <Form form={form} layout="vertical" size="middle">
          <Row gutter={12}>
            <Col span={8}>
              <Form.Item
                name="code"
                label={t.crm.productCode}
                rules={[{ required: true, message: "Cod obligatoriu" }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item
                name="name"
                label={t.common.name}
                rules={[{ required: true, message: "Nume obligatoriu" }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label={t.common.description}>
            <Input.TextArea rows={2} />
          </Form.Item>

          <Row gutter={12}>
            <Col span={8}>
              <Form.Item
                name="product_type"
                label={t.crm.productType}
                rules={[{ required: true }]}
              >
                <Select options={PRODUCT_TYPES.map((pt) => ({ label: pt, value: pt }))} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="category" label={t.crm.category}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="unit_of_measure"
                label={t.crm.unitOfMeasure}
                rules={[{ required: true }]}
              >
                <Select options={UNITS.map((u) => ({ label: u, value: u }))} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={8}>
              <Form.Item
                name="unit_price"
                label={t.crm.unitPrice}
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="currency" label="Valuta">
                <Select
                  options={[
                    { label: "RON", value: "RON" },
                    { label: "EUR", value: "EUR" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="vat_rate" label={t.crm.vatRate}>
                <InputNumber min={0} max={100} step={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
