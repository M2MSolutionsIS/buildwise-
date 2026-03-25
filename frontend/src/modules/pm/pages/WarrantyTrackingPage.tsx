/**
 * Warranty Tracking — F086
 * Garanții per proiect: start/end, alerte înainte de expirare,
 * log intervenții.
 */
import { useState, useMemo } from "react";
import {
  Card,
  Table,
  Button,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Progress,
  Alert,
  Divider,
  Timeline,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  SafetyOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  MinusCircleOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { PMWarranty, WarrantyIntervention } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

function warrantyStatus(w: PMWarranty): {
  label: string;
  color: string;
  daysLeft: number;
} {
  if (!w.is_active) return { label: "Inactivă", color: "default", daysLeft: 0 };
  const end = dayjs(w.end_date);
  const now = dayjs();
  const daysLeft = end.diff(now, "day");

  if (daysLeft < 0) return { label: "Expirată", color: "error", daysLeft };
  if (daysLeft <= w.alert_before_days)
    return { label: "Expiră curând", color: "warning", daysLeft };
  return { label: "Activă", color: "success", daysLeft };
}

export default function WarrantyTrackingPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const { data: warrantyRes, isLoading } = useQuery({
    queryKey: ["warranties", projectId],
    queryFn: () => pmService.listWarranties(projectId!),
    enabled: !!projectId,
  });

  const warranties = warrantyRes?.data ?? [];

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createWarranty(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warranties", projectId] });
      message.success("Garanție adăugată");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateWarranty(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warranties", projectId] });
      message.success("Garanție actualizată");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const activeCount = useMemo(
    () => warranties.filter((w) => w.is_active).length,
    [warranties]
  );
  const expiringCount = useMemo(
    () =>
      warranties.filter((w) => {
        const s = warrantyStatus(w);
        return s.color === "warning";
      }).length,
    [warranties]
  );
  const expiredCount = useMemo(
    () =>
      warranties.filter((w) => {
        const s = warrantyStatus(w);
        return s.color === "error";
      }).length,
    [warranties]
  );

  // ─── Modal ──────────────────────────────────────────────────────────────────

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ alert_before_days: 30 });
    setIsModalOpen(true);
  };

  const openEdit = (w: PMWarranty) => {
    setEditingId(w.id);
    form.setFieldsValue({
      ...w,
      start_date: dayjs(w.start_date),
      end_date: dayjs(w.end_date),
      interventions: w.interventions ?? [],
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
      start_date: (values.start_date as dayjs.Dayjs).toISOString(),
      end_date: (values.end_date as dayjs.Dayjs).toISOString(),
      interventions: (values.interventions as WarrantyIntervention[] | undefined)?.filter(
        (i) => i.description
      ),
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
      title: "Descriere garanție",
      dataIndex: "description",
      key: "desc",
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: "Început",
      dataIndex: "start_date",
      key: "start",
      width: 110,
      render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
    },
    {
      title: "Sfârșit",
      dataIndex: "end_date",
      key: "end",
      width: 110,
      render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
    },
    {
      title: "Durată / Progres",
      key: "progress",
      width: 160,
      render: (_: unknown, rec: PMWarranty) => {
        const start = dayjs(rec.start_date);
        const end = dayjs(rec.end_date);
        const now = dayjs();
        const totalDays = end.diff(start, "day");
        const elapsed = now.diff(start, "day");
        const pct = totalDays > 0 ? Math.min(Math.round((elapsed / totalDays) * 100), 100) : 100;

        return (
          <Progress
            percent={pct}
            size="small"
            strokeColor={pct >= 100 ? "#ff4d4f" : pct >= 80 ? "#faad14" : "#52c41a"}
            format={() => `${Math.max(totalDays - elapsed, 0)}z rămase`}
          />
        );
      },
    },
    {
      title: "Alertă",
      dataIndex: "alert_before_days",
      key: "alert",
      width: 80,
      align: "center" as const,
      render: (v: number) => <Text type="secondary">{v}z</Text>,
    },
    {
      title: "Status",
      key: "status",
      width: 120,
      render: (_: unknown, rec: PMWarranty) => {
        const s = warrantyStatus(rec);
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: "Intervenții",
      key: "interventions",
      width: 100,
      align: "center" as const,
      render: (_: unknown, rec: PMWarranty) => {
        const count = rec.interventions?.length ?? 0;
        return count > 0 ? (
          <Tag color="blue">{count}</Tag>
        ) : (
          <Text type="secondary">0</Text>
        );
      },
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 80,
      render: (_: unknown, rec: PMWarranty) => (
        <Button
          size="small"
          icon={<EditOutlined />}
          onClick={() => openEdit(rec)}
        />
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
          <SafetyOutlined /> Tracking Garanții (F086)
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Adaugă garanție
        </Button>
      </div>

      {/* Expiring alert */}
      {expiringCount > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message={`${expiringCount} garanții expiră curând!`}
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total garanții"
              value={warranties.length}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Active"
              value={activeCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Expiră curând"
              value={expiringCount}
              prefix={<ClockCircleOutlined />}
              valueStyle={expiringCount > 0 ? { color: "#faad14" } : undefined}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Expirate"
              value={expiredCount}
              prefix={<WarningOutlined />}
              valueStyle={expiredCount > 0 ? { color: "#ff4d4f" } : undefined}
            />
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={warranties}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
          size="middle"
          expandable={{
            expandedRowRender: (rec) => {
              const interventions = rec.interventions ?? [];
              if (interventions.length === 0)
                return <Text type="secondary">Nicio intervenție înregistrată</Text>;
              return (
                <Timeline
                  items={interventions.map((iv, idx) => ({
                    key: idx,
                    color: "blue",
                    children: (
                      <div>
                        <Text strong>{dayjs(iv.date).format("DD.MM.YYYY")}</Text>
                        {" — "}
                        <Text>{iv.description}</Text>
                        {iv.performed_by && (
                          <Text type="secondary"> (de {iv.performed_by})</Text>
                        )}
                        {iv.cost != null && (
                          <Tag color="orange" style={{ marginLeft: 8 }}>
                            {iv.cost} RON
                          </Tag>
                        )}
                      </div>
                    ),
                  }))}
                />
              );
            },
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare garanție" : "Adaugă garanție"}
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
            name="description"
            label="Descriere garanție"
            rules={[{ required: true }]}
          >
            <Input.TextArea rows={2} placeholder="Ex: Garanție tâmplărie PVC — 5 ani" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="start_date"
                label="Data început"
                rules={[{ required: true }]}
              >
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="end_date"
                label="Data sfârșit"
                rules={[{ required: true }]}
              >
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="alert_before_days"
                label="Alertă (zile înainte)"
              >
                <InputNumber
                  min={1}
                  max={365}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>

          {editingId && (
            <>
              <Divider orientation="left">Intervenții în garanție</Divider>
              <Form.List name="interventions">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...rest }) => (
                      <Row key={key} gutter={8} style={{ marginBottom: 8 }}>
                        <Col span={6}>
                          <Form.Item {...rest} name={[name, "date"]} noStyle>
                            <Input placeholder="Data (DD.MM.YYYY)" />
                          </Form.Item>
                        </Col>
                        <Col span={10}>
                          <Form.Item {...rest} name={[name, "description"]} noStyle>
                            <Input placeholder="Descriere intervenție" />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item {...rest} name={[name, "performed_by"]} noStyle>
                            <Input placeholder="Efectuat de" />
                          </Form.Item>
                        </Col>
                        <Col span={3}>
                          <Form.Item {...rest} name={[name, "cost"]} noStyle>
                            <InputNumber placeholder="Cost" min={0} style={{ width: "100%" }} />
                          </Form.Item>
                        </Col>
                        <Col span={1}>
                          <Button
                            icon={<MinusCircleOutlined />}
                            onClick={() => remove(name)}
                            danger
                            size="small"
                          />
                        </Col>
                      </Row>
                    ))}
                    <Button
                      type="dashed"
                      onClick={() =>
                        add({
                          date: dayjs().format("YYYY-MM-DD"),
                          description: "",
                        })
                      }
                      icon={<PlusOutlined />}
                      block
                    >
                      Adaugă intervenție
                    </Button>
                  </>
                )}
              </Form.List>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
}
