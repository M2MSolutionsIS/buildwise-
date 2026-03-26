/**
 * E-017: Budget/Deviz Editor — F071, F074, F125
 * Editable table grouped by WBS phases, estimated vs actual columns,
 * color coding for overbudget (>5%), footer totals.
 */
import { useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import {
  Typography,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  App,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Card,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  DollarOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import { useTranslation } from "../../../i18n";
import type { DevizItem } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const { Title, Text } = Typography;

const UNITS = ["buc", "mp", "ml", "kg", "t", "ore", "zi", "mc", "set", "lot"];

export default function DevizEditorPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const t = useTranslation();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DevizItem | null>(null);
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ["deviz", projectId],
    queryFn: () => pmService.listDevizItems(projectId!),
    enabled: !!projectId,
  });

  const items = data?.data || [];

  const createMut = useMutation({
    mutationFn: (payload: Omit<DevizItem, "id" | "project_id" | "created_at" | "updated_at" | "estimated_total" | "actual_total" | "over_budget_alert">) =>
      pmService.createDevizItem(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deviz", projectId] });
      message.success("Articol deviz creat");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<DevizItem> }) =>
      pmService.updateDevizItem(projectId!, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deviz", projectId] });
      message.success("Articol actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteDevizItem(projectId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deviz", projectId] });
      message.success("Articol șters");
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({
      unit_of_measure: "buc",
      currency: "RON",
      estimated_quantity: 0,
      estimated_unit_price_material: 0,
      estimated_unit_price_labor: 0,
      actual_quantity: 0,
      actual_unit_price_material: 0,
      actual_unit_price_labor: 0,
      sort_order: items.length,
    });
    setModalOpen(true);
  };

  const openEdit = (record: DevizItem) => {
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

  // Summary calculations
  const summary = useMemo(() => {
    const totalEstimated = items.reduce((s, i) => s + i.estimated_total, 0);
    const totalActual = items.reduce((s, i) => s + i.actual_total, 0);
    const delta = totalActual - totalEstimated;
    const deltaPercent = totalEstimated > 0 ? (delta / totalEstimated) * 100 : 0;
    const overBudgetCount = items.filter((i) => i.over_budget_alert).length;
    return { totalEstimated, totalActual, delta, deltaPercent, overBudgetCount };
  }, [items]);

  const getDeltaColor = (estimated: number, actual: number) => {
    if (actual === 0 || estimated === 0) return undefined;
    const pct = ((actual - estimated) / estimated) * 100;
    if (pct > 5) return "#EF4444";
    if (pct > 0) return "#F59E0B";
    return "#10B981";
  };

  const columns: ColumnsType<DevizItem> = [
    {
      title: "Cod",
      dataIndex: "code",
      key: "code",
      width: 100,
      fixed: "left" as const,
      render: (code: string) => (
        <span style={{ fontFamily: "monospace", fontWeight: 600 }}>{code || "—"}</span>
      ),
    },
    {
      title: t.common.description,
      dataIndex: "description",
      key: "description",
      width: 200,
      fixed: "left" as const,
      ellipsis: true,
    },
    {
      title: "UM",
      dataIndex: "unit_of_measure",
      key: "unit_of_measure",
      width: 60,
      align: "center",
    },
    {
      title: t.pm.estimatedQty,
      dataIndex: "estimated_quantity",
      key: "estimated_quantity",
      width: 100,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { maximumFractionDigits: 2 }),
    },
    {
      title: "Preț Mat. Est.",
      dataIndex: "estimated_unit_price_material",
      key: "estimated_unit_price_material",
      width: 110,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Preț Man. Est.",
      dataIndex: "estimated_unit_price_labor",
      key: "estimated_unit_price_labor",
      width: 110,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Total Estimat",
      dataIndex: "estimated_total",
      key: "estimated_total",
      width: 120,
      align: "right",
      render: (v: number) => (
        <Text strong>{v.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}</Text>
      ),
    },
    {
      title: t.pm.actualQty,
      dataIndex: "actual_quantity",
      key: "actual_quantity",
      width: 100,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { maximumFractionDigits: 2 }),
    },
    {
      title: "Preț Mat. Real",
      dataIndex: "actual_unit_price_material",
      key: "actual_unit_price_material",
      width: 110,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Preț Man. Real",
      dataIndex: "actual_unit_price_labor",
      key: "actual_unit_price_labor",
      width: 110,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Total Real",
      dataIndex: "actual_total",
      key: "actual_total",
      width: 120,
      align: "right",
      render: (v: number, record: DevizItem) => (
        <Text strong style={{ color: getDeltaColor(record.estimated_total, v) }}>
          {v.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
        </Text>
      ),
    },
    {
      title: t.pm.delta,
      key: "delta",
      width: 110,
      align: "right",
      render: (_: unknown, record: DevizItem) => {
        const delta = record.actual_total - record.estimated_total;
        if (record.actual_total === 0) return "—";
        const color = getDeltaColor(record.estimated_total, record.actual_total);
        return (
          <Space size={4}>
            {record.over_budget_alert && (
              <WarningOutlined style={{ color: "#EF4444", fontSize: 12 }} />
            )}
            <Text style={{ color, fontWeight: 600 }}>
              {delta > 0 ? "+" : ""}
              {delta.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
            </Text>
          </Space>
        );
      },
    },
    {
      title: t.common.actions,
      key: "actions",
      width: 90,
      render: (_: unknown, record: DevizItem) => (
        <Space size="small">
          <Button type="text" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm
            title="Ștergeți acest articol?"
            onConfirm={() => deleteMut.mutate(record.id)}
            okText={t.common.yes}
            cancelText={t.common.no}
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <DollarOutlined style={{ fontSize: 20, color: "#047857" }} />
          <Title level={4} style={{ margin: 0 }}>
            {t.pm.devizEditor}
          </Title>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          {t.common.add}
        </Button>
      </div>

      {/* Summary Cards */}
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderTop: "3px solid #2563EB" }}>
            <Statistic
              title="Total Estimat"
              value={summary.totalEstimated}
              precision={2}
              suffix="RON"
              valueStyle={{ fontSize: 18 }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderTop: "3px solid #047857" }}>
            <Statistic
              title="Total Real"
              value={summary.totalActual}
              precision={2}
              suffix="RON"
              valueStyle={{ fontSize: 18 }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card
            size="small"
            style={{
              borderTop: `3px solid ${summary.delta > 0 ? "#EF4444" : "#10B981"}`,
            }}
          >
            <Statistic
              title={t.pm.delta}
              value={summary.delta}
              precision={2}
              suffix="RON"
              valueStyle={{
                fontSize: 18,
                color: summary.delta > 0 ? "#EF4444" : "#10B981",
              }}
              prefix={summary.delta > 0 ? "+" : ""}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card
            size="small"
            style={{
              borderTop: `3px solid ${summary.overBudgetCount > 0 ? "#EF4444" : "#10B981"}`,
            }}
          >
            <Statistic
              title={t.pm.overBudget}
              value={summary.overBudgetCount}
              suffix={`/ ${items.length}`}
              valueStyle={{
                fontSize: 18,
                color: summary.overBudgetCount > 0 ? "#EF4444" : "#10B981",
              }}
              prefix={summary.overBudgetCount > 0 ? <WarningOutlined /> : undefined}
            />
          </Card>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={items}
        rowKey="id"
        loading={isLoading}
        pagination={false}
        size="small"
        scroll={{ x: 1600 }}
        rowClassName={(record) =>
          record.over_budget_alert ? "deviz-overbudget-row" : ""
        }
        summary={() => {
          if (items.length === 0) return null;
          return (
            <Table.Summary fixed>
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={6} align="right">
                  <Text strong>TOTAL</Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={6} align="right">
                  <Text strong>
                    {summary.totalEstimated.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
                  </Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={7} colSpan={3} />
                <Table.Summary.Cell index={10} align="right">
                  <Text strong style={{ color: getDeltaColor(summary.totalEstimated, summary.totalActual) }}>
                    {summary.totalActual.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
                  </Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={11} align="right">
                  <Text
                    strong
                    style={{ color: getDeltaColor(summary.totalEstimated, summary.totalActual) }}
                  >
                    {summary.delta > 0 ? "+" : ""}
                    {summary.delta.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
                    {" "}
                    ({summary.deltaPercent > 0 ? "+" : ""}
                    {summary.deltaPercent.toFixed(1)}%)
                  </Text>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={12} />
              </Table.Summary.Row>
            </Table.Summary>
          );
        }}
      />

      {/* Create/Edit Modal */}
      <Modal
        title={editing ? `${t.common.edit} — ${editing.description}` : t.common.create}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSubmit}
        confirmLoading={createMut.isPending || updateMut.isPending}
        width={700}
        okText={t.common.save}
        cancelText={t.common.cancel}
      >
        <Form form={form} layout="vertical" size="middle">
          <Row gutter={12}>
            <Col span={6}>
              <Form.Item name="code" label="Cod">
                <Input placeholder="Ex: A.1.01" />
              </Form.Item>
            </Col>
            <Col span={18}>
              <Form.Item
                name="description"
                label={t.common.description}
                rules={[{ required: true, message: "Descriere obligatorie" }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={8}>
              <Form.Item
                name="unit_of_measure"
                label="UM"
                rules={[{ required: true }]}
              >
                <Select options={UNITS.map((u) => ({ label: u, value: u }))} />
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
              <Form.Item name="sort_order" label="Ordine">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>

          <Title level={5} style={{ marginBottom: 12, color: "#2563EB" }}>
            Estimat
          </Title>
          <Row gutter={12}>
            <Col span={8}>
              <Form.Item name="estimated_quantity" label={t.pm.estimatedQty}>
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="estimated_unit_price_material" label="Preț Material">
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="estimated_unit_price_labor" label="Preț Manoperă">
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>

          <Title level={5} style={{ marginBottom: 12, color: "#047857" }}>
            Real
          </Title>
          <Row gutter={12}>
            <Col span={8}>
              <Form.Item name="actual_quantity" label={t.pm.actualQty}>
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="actual_unit_price_material" label="Preț Material">
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="actual_unit_price_labor" label="Preț Manoperă">
                <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
