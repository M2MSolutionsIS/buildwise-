/**
 * Situații de Lucrări (SdL) — F079
 * Cantități lunare: contractat vs executat vs cumulat.
 * Generare din deviz, link "Emite factură" → Billing (F035).
 * Approval workflow + invoice tracking.
 */
import { useState, useMemo } from "react";
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
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Popconfirm,
  Tooltip,
  Progress,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  CheckOutlined,
  FileTextOutlined,
  DollarOutlined,
  FileDoneOutlined,
  WarningOutlined,
  CalendarOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { WorkSituation } from "../../../types";

const { Title, Text } = Typography;

const MONTHS = [
  "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
  "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie",
];

export default function WorkSituationsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: sdlRes, isLoading } = useQuery({
    queryKey: ["work-situations", projectId],
    queryFn: () => pmService.listWorkSituations(projectId!),
    enabled: !!projectId,
  });

  const sdls = sdlRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createWorkSituation(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație de lucrări creată");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateWorkSituation(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație actualizată");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const approveMut = useMutation({
    mutationFn: (id: string) => pmService.approveWorkSituation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație aprobată");
    },
  });

  // ─── Helpers ────────────────────────────────────────────────────────────────

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    form.resetFields();
  };

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    const now = new Date();
    form.setFieldsValue({
      period_month: now.getMonth() + 1,
      period_year: now.getFullYear(),
      currency: "RON",
    });
    setIsModalOpen(true);
  };

  const openEdit = (sdl: WorkSituation) => {
    setEditingId(sdl.id);
    form.setFieldsValue(sdl);
    setIsModalOpen(true);
  };

  const handleSubmit = (values: Record<string, unknown>) => {
    const payload = {
      ...values,
      remaining:
        (values.contracted_total as number) -
        (values.executed_cumulated as number),
    };
    if (editingId) {
      updateMut.mutate({ id: editingId, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const totalContracted = useMemo(
    () => sdls.reduce((s, d) => s + d.contracted_total, 0),
    [sdls]
  );
  const totalExecutedCumulated = useMemo(
    () => sdls.reduce((s, d) => s + d.executed_cumulated, 0),
    [sdls]
  );
  const totalRemaining = useMemo(
    () => sdls.reduce((s, d) => s + d.remaining, 0),
    [sdls]
  );
  const approvedCount = useMemo(
    () => sdls.filter((d) => d.is_approved).length,
    [sdls]
  );
  const invoicedCount = useMemo(
    () => sdls.filter((d) => d.is_invoiced).length,
    [sdls]
  );

  // ─── Columns ────────────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Nr. SdL",
      dataIndex: "sdl_number",
      key: "sdl",
      width: 100,
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: "Perioadă",
      key: "period",
      width: 140,
      render: (_: unknown, rec: WorkSituation) =>
        `${MONTHS[rec.period_month - 1]} ${rec.period_year}`,
      sorter: (a: WorkSituation, b: WorkSituation) =>
        a.period_year * 12 + a.period_month - (b.period_year * 12 + b.period_month),
      defaultSortOrder: "descend" as const,
    },
    {
      title: "Contractat",
      dataIndex: "contracted_total",
      key: "contracted",
      width: 130,
      align: "right" as const,
      render: (v: number, rec: WorkSituation) =>
        `${v.toLocaleString("ro-RO")} ${rec.currency}`,
    },
    {
      title: "Executat curent",
      dataIndex: "executed_current",
      key: "current",
      width: 130,
      align: "right" as const,
      render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
    },
    {
      title: "Executat cumulat",
      dataIndex: "executed_cumulated",
      key: "cumulated",
      width: 140,
      align: "right" as const,
      render: (v: number) => <Text strong>{v.toLocaleString("ro-RO")} RON</Text>,
    },
    {
      title: "Rest",
      dataIndex: "remaining",
      key: "remaining",
      width: 120,
      align: "right" as const,
      render: (v: number) => (
        <Text type={v < 0 ? "danger" : "success"}>
          {v.toLocaleString("ro-RO")} RON
        </Text>
      ),
    },
    {
      title: "Progres",
      key: "progress",
      width: 100,
      render: (_: unknown, rec: WorkSituation) => {
        const pct =
          rec.contracted_total > 0
            ? (rec.executed_cumulated / rec.contracted_total) * 100
            : 0;
        return <Progress percent={Math.round(pct)} size="small" />;
      },
    },
    {
      title: "Status",
      key: "status",
      width: 140,
      render: (_: unknown, rec: WorkSituation) => (
        <Space>
          {rec.is_approved ? (
            <Tag color="success" icon={<CheckOutlined />}>Aprobat</Tag>
          ) : (
            <Tag color="warning">Neaprobat</Tag>
          )}
          {rec.is_invoiced && (
            <Tag color="blue" icon={<DollarOutlined />}>Facturat</Tag>
          )}
        </Space>
      ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 130,
      render: (_: unknown, rec: WorkSituation) => (
        <Space size="small">
          {!rec.is_approved && (
            <>
              <Tooltip title="Editează">
                <Button
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => openEdit(rec)}
                />
              </Tooltip>
              <Popconfirm
                title="Aprobi această situație de lucrări?"
                onConfirm={() => approveMut.mutate(rec.id)}
              >
                <Tooltip title="Aprobă">
                  <Button
                    size="small"
                    type="primary"
                    icon={<CheckOutlined />}
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
          {rec.is_approved && !rec.is_invoiced && (
            <Tooltip title="Link: Emite factură (F035)">
              <Button size="small" icon={<DollarOutlined />} type="dashed">
                Facturează
              </Button>
            </Tooltip>
          )}
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
          <FileDoneOutlined /> Situații de Lucrări — SdL (F079)
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          SdL nouă
        </Button>
      </div>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total SdL"
              value={sdls.length}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total contractat"
              value={totalContracted}
              suffix="RON"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Executat cumulat"
              value={totalExecutedCumulated}
              suffix="RON"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Rest de executat"
              value={totalRemaining}
              suffix="RON"
              precision={0}
              valueStyle={totalRemaining < 0 ? { color: "#ff4d4f" } : undefined}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Aprobate / Facturate"
              value={approvedCount}
              suffix={`/ ${invoicedCount}`}
              prefix={<CheckOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={sdls}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 12 }}
          size="middle"
          expandable={{
            expandedRowRender: (rec) =>
              rec.line_items && rec.line_items.length > 0 ? (
                <Table
                  size="small"
                  pagination={false}
                  dataSource={rec.line_items}
                  rowKey={(_, i) => String(i)}
                  columns={[
                    { title: "Descriere", dataIndex: "description", key: "desc" },
                    { title: "U.M.", dataIndex: "unit_of_measure", key: "um", width: 80 },
                    {
                      title: "Cant. contractată",
                      dataIndex: "contracted_qty",
                      key: "cqty",
                      width: 130,
                      align: "right" as const,
                    },
                    {
                      title: "Preț",
                      dataIndex: "contracted_price",
                      key: "price",
                      width: 100,
                      align: "right" as const,
                      render: (v: number) => `${v?.toFixed(2) ?? "—"} RON`,
                    },
                    {
                      title: "Exec. curent",
                      dataIndex: "executed_current_qty",
                      key: "ecur",
                      width: 110,
                      align: "right" as const,
                    },
                    {
                      title: "Exec. cumulat",
                      dataIndex: "executed_cumulated_qty",
                      key: "ecum",
                      width: 110,
                      align: "right" as const,
                    },
                    {
                      title: "Rest",
                      dataIndex: "remaining_qty",
                      key: "rest",
                      width: 80,
                      align: "right" as const,
                    },
                    {
                      title: "Valoare",
                      dataIndex: "total_value",
                      key: "val",
                      width: 110,
                      align: "right" as const,
                      render: (v: number) => `${v?.toLocaleString("ro-RO") ?? "—"} RON`,
                    },
                  ]}
                />
              ) : (
                <Text type="secondary">Nu sunt articole detaliate</Text>
              ),
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare Situație de Lucrări" : "Situație de Lucrări nouă"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="sdl_number"
                label="Nr. SdL"
                rules={[{ required: true }]}
              >
                <Input placeholder="SdL-001" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="period_month"
                label="Luna"
                rules={[{ required: true }]}
              >
                <Select
                  options={MONTHS.map((m, i) => ({ value: i + 1, label: m }))}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="period_year"
                label="An"
                rules={[{ required: true }]}
              >
                <InputNumber
                  min={2020}
                  max={2035}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="contracted_total"
                label="Valoare contractată (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={1000} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="executed_current"
                label="Executat curent (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={100} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="executed_cumulated"
                label="Executat cumulat (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={100} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
