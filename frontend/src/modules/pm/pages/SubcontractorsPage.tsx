/**
 * Subcontractori — F075
 * Evidență subcontractori: contracte, activități, valori, facturi, % realizare.
 *
 * Table with CRUD + progress tracking + financial summary.
 */
import { useState, useMemo } from "react";
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Statistic,
  Row,
  Col,
  message,
  Progress,
  Typography,
  Popconfirm,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  DollarOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { PMSubcontractor } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

export default function SubcontractorsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: subRes, isLoading } = useQuery({
    queryKey: ["subcontractors", projectId],
    queryFn: () => pmService.listSubcontractors(projectId!),
    enabled: !!projectId,
  });

  const subs = subRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createSubcontractor(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subcontractors", projectId] });
      message.success("Subcontractor adăugat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateSubcontractor(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subcontractors", projectId] });
      message.success("Subcontractor actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteSubcontractor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subcontractors", projectId] });
      message.success("Subcontractor șters");
    },
  });

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const totalContractValue = useMemo(
    () => subs.reduce((s, sub) => s + (sub.contract_value ?? 0), 0),
    [subs]
  );
  const totalInvoiced = useMemo(
    () => subs.reduce((s, sub) => s + sub.invoiced_amount, 0),
    [subs]
  );
  const totalPaid = useMemo(
    () => subs.reduce((s, sub) => s + sub.paid_amount, 0),
    [subs]
  );
  const avgCompletion = useMemo(
    () =>
      subs.length > 0
        ? subs.reduce((s, sub) => s + sub.percent_complete, 0) / subs.length
        : 0,
    [subs]
  );

  // ─── Modal ──────────────────────────────────────────────────────────────────

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const openEdit = (sub: PMSubcontractor) => {
    setEditingId(sub.id);
    form.setFieldsValue({
      ...sub,
      start_date: sub.start_date ? dayjs(sub.start_date) : undefined,
      end_date: sub.end_date ? dayjs(sub.end_date) : undefined,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    form.resetFields();
  };

  const handleSubmit = (values: Record<string, unknown>) => {
    const payload = {
      ...values,
      start_date: values.start_date
        ? (values.start_date as dayjs.Dayjs).toISOString()
        : undefined,
      end_date: values.end_date
        ? (values.end_date as dayjs.Dayjs).toISOString()
        : undefined,
    };
    if (editingId) {
      updateMut.mutate({ id: editingId, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  // ─── Columns ────────────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Firmă",
      dataIndex: "company_name",
      key: "company",
      width: 180,
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: "Nr. contract",
      dataIndex: "contract_number",
      key: "contract",
      width: 120,
      render: (v?: string) => v ?? "—",
    },
    {
      title: "Valoare contract",
      dataIndex: "contract_value",
      key: "value",
      width: 140,
      align: "right" as const,
      render: (v?: number, rec?: PMSubcontractor) =>
        v ? `${v.toLocaleString("ro-RO")} ${rec?.currency ?? "RON"}` : "—",
    },
    {
      title: "Realizare",
      dataIndex: "percent_complete",
      key: "progress",
      width: 150,
      render: (v: number) => (
        <Progress
          percent={v}
          size="small"
          strokeColor={v >= 100 ? "#52c41a" : v >= 50 ? "#1677ff" : "#faad14"}
        />
      ),
    },
    {
      title: "Facturat",
      dataIndex: "invoiced_amount",
      key: "invoiced",
      width: 120,
      align: "right" as const,
      render: (v: number, rec: PMSubcontractor) => {
        const pct =
          rec.contract_value && rec.contract_value > 0
            ? (v / rec.contract_value) * 100
            : 0;
        return (
          <Tooltip title={`${pct.toFixed(0)}% din contract`}>
            {v.toLocaleString("ro-RO")} RON
          </Tooltip>
        );
      },
    },
    {
      title: "Plătit",
      dataIndex: "paid_amount",
      key: "paid",
      width: 120,
      align: "right" as const,
      render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
    },
    {
      title: "Perioadă",
      key: "period",
      width: 180,
      render: (_: unknown, rec: PMSubcontractor) => {
        const start = rec.start_date ? dayjs(rec.start_date).format("DD.MM.YY") : "—";
        const end = rec.end_date ? dayjs(rec.end_date).format("DD.MM.YY") : "—";
        return `${start} → ${end}`;
      },
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 100,
      render: (_: unknown, rec: PMSubcontractor) => (
        <Space size="small">
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(rec)} />
          <Popconfirm
            title="Ștergi acest subcontractor?"
            onConfirm={() => deleteMut.mutate(rec.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          <TeamOutlined /> Subcontractori (F075)
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Adaugă subcontractor
        </Button>
      </div>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Nr. subcontractori"
              value={subs.length}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Valoare totală contracte"
              value={totalContractValue}
              suffix="RON"
              prefix={<FileTextOutlined />}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total facturat / plătit"
              value={totalInvoiced}
              suffix={`/ ${totalPaid.toLocaleString("ro-RO")} RON`}
              prefix={<DollarOutlined />}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Realizare medie"
              value={avgCompletion}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              precision={0}
            />
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={subs}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 15 }}
          size="middle"
          expandable={{
            expandedRowRender: (rec) =>
              rec.scope_description ? (
                <div style={{ padding: "8px 16px" }}>
                  <Text type="secondary">Scope: </Text>
                  <Text>{rec.scope_description}</Text>
                  {rec.notes && (
                    <>
                      <br />
                      <Text type="secondary">Note: </Text>
                      <Text>{rec.notes}</Text>
                    </>
                  )}
                </div>
              ) : null,
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare subcontractor" : "Adaugă subcontractor"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="company_name"
            label="Firmă"
            rules={[{ required: true, message: "Numele firmei este obligatoriu" }]}
          >
            <Input placeholder="S.C. Exemplu S.R.L." />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="contract_number" label="Nr. contract">
                <Input placeholder="CT-2026-001" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="contract_value" label="Valoare contract (RON)">
                <InputNumber min={0} step={1000} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="start_date" label="Data început">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="end_date" label="Data sfârșit">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="scope_description" label="Descriere scope">
            <Input.TextArea rows={3} placeholder="Lucrări de tâmplărie PVC..." />
          </Form.Item>
          {editingId && (
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="percent_complete" label="% realizare">
                  <InputNumber min={0} max={100} style={{ width: "100%" }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="invoiced_amount" label="Facturat (RON)">
                  <InputNumber min={0} style={{ width: "100%" }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="paid_amount" label="Plătit (RON)">
                  <InputNumber min={0} style={{ width: "100%" }} />
                </Form.Item>
              </Col>
            </Row>
          )}
          <Form.Item name="notes" label="Note">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
