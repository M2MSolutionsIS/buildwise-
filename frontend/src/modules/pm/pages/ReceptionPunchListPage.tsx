/**
 * E-021 — Recepție & Punch List
 * F081: Checklist recepție — iteme generate din WBS, status OK/Parțial/Defect.
 * F082: Punch List — defecte cu severitate, responsabil, deadline, fotografii.
 * F086: Flux închidere proiect — validare 0 defecte critice deschise.
 *
 * 3 tabs: Checklist, Punch List, Finalizare.
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
  Select,
  DatePicker,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Popconfirm,
  Tabs,
  Progress,
  Alert,
  Badge,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  SafetyOutlined,
  FileDoneOutlined,
  EnvironmentOutlined,
  FlagOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { PunchItem, PunchItemSeverity, PunchItemStatus, PMTask } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

const SEVERITY_CONFIG: Record<PunchItemSeverity, { label: string; color: string }> = {
  low: { label: "Minoră", color: "blue" },
  medium: { label: "Medie", color: "orange" },
  high: { label: "Ridicată", color: "volcano" },
  critical: { label: "Critică", color: "red" },
};

const STATUS_CONFIG: Record<PunchItemStatus, { label: string; color: string }> = {
  open: { label: "Deschis", color: "error" },
  in_progress: { label: "În lucru", color: "processing" },
  resolved: { label: "Rezolvat", color: "warning" },
  verified: { label: "Verificat", color: "success" },
};

export default function ReceptionPunchListPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<PunchItem | null>(null);
  const [receptionModalOpen, setReceptionModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [receptionForm] = Form.useForm();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: punchRes, isLoading } = useQuery({
    queryKey: ["punch-items", projectId],
    queryFn: () => pmService.listPunchItems(projectId!),
    enabled: !!projectId,
  });

  const { data: tasksRes } = useQuery({
    queryKey: ["pm-tasks", projectId],
    queryFn: () => pmService.listTasks(projectId!),
    enabled: !!projectId,
  });

  const items = punchRes?.data ?? [];
  const tasks = tasksRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createPunchItem(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["punch-items", projectId] });
      message.success("Defect adăugat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updatePunchItem(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["punch-items", projectId] });
      message.success("Defect actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const receptionMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createReception(projectId!, payload),
    onSuccess: () => {
      message.success("PV Recepție creat cu succes!");
      setReceptionModalOpen(false);
      receptionForm.resetFields();
    },
    onError: () => message.error("Eroare la creare PV"),
  });

  // ─── Derived data ──────────────────────────────────────────────────────────

  const openItems = useMemo(
    () => items.filter((i) => i.status === "open" || i.status === "in_progress"),
    [items]
  );
  const criticalOpen = useMemo(
    () => openItems.filter((i) => i.severity === "critical"),
    [openItems]
  );
  const resolvedCount = useMemo(
    () => items.filter((i) => i.status === "resolved" || i.status === "verified").length,
    [items]
  );

  // Checklist from tasks (WBS activities as checklist items)
  const checklist = useMemo(() => {
    return tasks.map((task) => {
      const relatedPunch = items.filter(
        (p) => p.title.includes(task.title) || p.location === task.title
      );
      let checkStatus: "ok" | "partial" | "defect" = "ok";
      if (relatedPunch.some((p) => p.status === "open" && p.severity === "critical"))
        checkStatus = "defect";
      else if (relatedPunch.some((p) => p.status === "open"))
        checkStatus = "partial";
      else if (task.status !== "done")
        checkStatus = "partial";

      return {
        key: task.id,
        title: task.title,
        taskStatus: task.status,
        percent: task.percent_complete,
        checkStatus,
        defectsCount: relatedPunch.length,
      };
    });
  }, [tasks, items]);

  const canFinalize = criticalOpen.length === 0 && openItems.length === 0;

  // ─── Modal helpers ──────────────────────────────────────────────────────────

  const openCreate = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({ severity: "medium" });
    setIsModalOpen(true);
  };

  const openEdit = (item: PunchItem) => {
    setEditingItem(item);
    form.setFieldsValue({
      ...item,
      due_date: item.due_date ? dayjs(item.due_date) : undefined,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
    form.resetFields();
  };

  const handleSubmit = (values: Record<string, unknown>) => {
    const payload = {
      ...values,
      due_date: values.due_date
        ? (values.due_date as dayjs.Dayjs).toISOString()
        : undefined,
    };
    if (editingItem) {
      updateMut.mutate({ id: editingItem.id, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  const quickStatusChange = (item: PunchItem, newStatus: PunchItemStatus) => {
    updateMut.mutate({
      id: item.id,
      payload: {
        status: newStatus,
        ...(newStatus === "resolved" ? { resolved_at: new Date().toISOString() } : {}),
      },
    });
  };

  // ─── Tab: Checklist (F081) ────────────────────────────────────────────────

  const checklistTab = (
    <div>
      <Alert
        type="info"
        showIcon
        message="Checklist generat automat din activitățile WBS ale proiectului"
        style={{ marginBottom: 16 }}
      />
      <Table
        dataSource={checklist}
        rowKey="key"
        pagination={false}
        size="middle"
        columns={[
          {
            title: "Activitate WBS",
            dataIndex: "title",
            key: "title",
            render: (v: string) => <Text strong>{v}</Text>,
          },
          {
            title: "Progres task",
            dataIndex: "percent",
            key: "pct",
            width: 120,
            render: (v: number) => <Progress percent={v} size="small" />,
          },
          {
            title: "Status recepție",
            dataIndex: "checkStatus",
            key: "check",
            width: 130,
            render: (s: string) => {
              if (s === "ok")
                return <Tag color="success" icon={<CheckCircleOutlined />}>OK</Tag>;
              if (s === "partial")
                return <Tag color="warning" icon={<ExclamationCircleOutlined />}>Parțial</Tag>;
              return <Tag color="error" icon={<CloseCircleOutlined />}>Defect</Tag>;
            },
          },
          {
            title: "Defecte",
            dataIndex: "defectsCount",
            key: "defects",
            width: 80,
            align: "center" as const,
            render: (v: number) =>
              v > 0 ? <Badge count={v} /> : <Text type="secondary">0</Text>,
          },
        ]}
      />
    </div>
  );

  // ─── Tab: Punch List (F082) ───────────────────────────────────────────────

  const punchListColumns = [
    {
      title: "Defect",
      dataIndex: "title",
      key: "title",
      width: 200,
      render: (v: string, rec: PunchItem) => (
        <Space>
          {rec.severity === "critical" && (
            <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />
          )}
          <Text strong>{v}</Text>
        </Space>
      ),
    },
    {
      title: "Severitate",
      dataIndex: "severity",
      key: "severity",
      width: 110,
      render: (v: PunchItemSeverity) => (
        <Tag color={SEVERITY_CONFIG[v].color}>{SEVERITY_CONFIG[v].label}</Tag>
      ),
      filters: (Object.keys(SEVERITY_CONFIG) as PunchItemSeverity[]).map((k) => ({
        text: SEVERITY_CONFIG[k].label,
        value: k,
      })),
      onFilter: (value: unknown, rec: PunchItem) => rec.severity === value,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (v: PunchItemStatus) => (
        <Tag color={STATUS_CONFIG[v].color}>{STATUS_CONFIG[v].label}</Tag>
      ),
      filters: (Object.keys(STATUS_CONFIG) as PunchItemStatus[]).map((k) => ({
        text: STATUS_CONFIG[k].label,
        value: k,
      })),
      onFilter: (value: unknown, rec: PunchItem) => rec.status === value,
    },
    {
      title: "Locație",
      dataIndex: "location",
      key: "loc",
      width: 120,
      render: (v?: string) =>
        v ? (
          <Tag icon={<EnvironmentOutlined />}>{v}</Tag>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
    {
      title: "Deadline",
      dataIndex: "due_date",
      key: "due",
      width: 110,
      render: (d?: string) => {
        if (!d) return "—";
        const isOverdue = dayjs(d).isBefore(dayjs(), "day");
        return (
          <Text type={isOverdue ? "danger" : undefined}>
            {dayjs(d).format("DD.MM.YYYY")}
          </Text>
        );
      },
      sorter: (a: PunchItem, b: PunchItem) =>
        dayjs(a.due_date ?? "2099-01-01").unix() -
        dayjs(b.due_date ?? "2099-01-01").unix(),
    },
    {
      title: "Rezolvat",
      dataIndex: "resolved_at",
      key: "resolved",
      width: 110,
      render: (d?: string) =>
        d ? (
          <Text type="success">{dayjs(d).format("DD.MM.YYYY")}</Text>
        ) : (
          "—"
        ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 180,
      render: (_: unknown, rec: PunchItem) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(rec)}
          />
          {rec.status === "open" && (
            <Tooltip title="Marchează în lucru">
              <Button
                size="small"
                onClick={() => quickStatusChange(rec, "in_progress")}
              >
                Start
              </Button>
            </Tooltip>
          )}
          {rec.status === "in_progress" && (
            <Tooltip title="Marchează rezolvat">
              <Button
                size="small"
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={() => quickStatusChange(rec, "resolved")}
              />
            </Tooltip>
          )}
          {rec.status === "resolved" && (
            <Tooltip title="Verifică">
              <Button
                size="small"
                style={{ borderColor: "#52c41a", color: "#52c41a" }}
                icon={<SafetyOutlined />}
                onClick={() => quickStatusChange(rec, "verified")}
              />
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  const punchListTab = (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Adaugă defect
        </Button>
      </div>
      <Table
        columns={punchListColumns}
        dataSource={items}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 15 }}
        size="middle"
        expandable={{
          expandedRowRender: (rec) => (
            <div style={{ padding: "8px 16px" }}>
              {rec.description && (
                <div style={{ marginBottom: 8 }}>
                  <Text type="secondary">Descriere: </Text>
                  <Text>{rec.description}</Text>
                </div>
              )}
              {rec.photos && rec.photos.length > 0 && (
                <div>
                  <Text type="secondary">Fotografii: </Text>
                  <Text>{rec.photos.length} atașate</Text>
                </div>
              )}
            </div>
          ),
        }}
      />
    </div>
  );

  // ─── Tab: Finalizare (F086/F103) ──────────────────────────────────────────

  const finalizareTab = (
    <div>
      {!canFinalize && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message="Nu se poate finaliza recepția"
          description={
            <div>
              {criticalOpen.length > 0 && (
                <div>
                  <Text type="danger" strong>
                    {criticalOpen.length} defecte critice deschise
                  </Text>
                  — trebuie rezolvate înainte de finalizare.
                </div>
              )}
              {openItems.length > 0 && (
                <div>
                  <Text type="warning" strong>
                    {openItems.length} defecte totale deschise
                  </Text>
                  — toate trebuie rezolvate sau verificate.
                </div>
              )}
            </div>
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {canFinalize && (
        <Alert
          type="success"
          showIcon
          icon={<CheckCircleOutlined />}
          message="Recepția poate fi finalizată"
          description="Toate defectele sunt rezolvate. Puteți genera PV de recepție."
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={24}>
        <Col span={12}>
          <Card title="Sumar recepție">
            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <Row justify="space-between">
                <Text>Total defecte înregistrate</Text>
                <Text strong>{items.length}</Text>
              </Row>
              <Row justify="space-between">
                <Text>Deschise</Text>
                <Text strong type="danger">
                  {items.filter((i) => i.status === "open").length}
                </Text>
              </Row>
              <Row justify="space-between">
                <Text>În lucru</Text>
                <Text strong style={{ color: "#1677ff" }}>
                  {items.filter((i) => i.status === "in_progress").length}
                </Text>
              </Row>
              <Row justify="space-between">
                <Text>Rezolvate</Text>
                <Text strong style={{ color: "#faad14" }}>
                  {items.filter((i) => i.status === "resolved").length}
                </Text>
              </Row>
              <Row justify="space-between">
                <Text>Verificate</Text>
                <Text strong type="success">
                  {items.filter((i) => i.status === "verified").length}
                </Text>
              </Row>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Acțiuni finalizare">
            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <Button
                type="primary"
                icon={<FileDoneOutlined />}
                size="large"
                block
                disabled={!canFinalize}
                onClick={() => setReceptionModalOpen(true)}
              >
                Generează PV Recepție
              </Button>
              <Text type="secondary" style={{ fontSize: 12 }}>
                PV-ul va fi generat ca document oficial al proiectului.
                Statutul proiectului va fi schimbat în "Închis".
                Clientul va fi notificat automat.
              </Text>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );

  return (
    <div style={{ padding: 24 }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <SafetyOutlined /> Recepție & Punch List (E-021)
      </Title>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total defecte"
              value={items.length}
              prefix={<FlagOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Deschise"
              value={openItems.length}
              valueStyle={openItems.length > 0 ? { color: "#ff4d4f" } : undefined}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Critice deschise"
              value={criticalOpen.length}
              valueStyle={criticalOpen.length > 0 ? { color: "#ff4d4f" } : undefined}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Rezolvate / Verificate"
              value={resolvedCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Activități WBS"
              value={checklist.length}
            />
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Card>
        <Tabs
          defaultActiveKey="checklist"
          items={[
            {
              key: "checklist",
              label: (
                <span>
                  <CheckCircleOutlined /> Checklist Recepție
                </span>
              ),
              children: checklistTab,
            },
            {
              key: "punch",
              label: (
                <span>
                  <Badge count={openItems.length} offset={[10, 0]}>
                    <ExclamationCircleOutlined /> Punch List
                  </Badge>
                </span>
              ),
              children: punchListTab,
            },
            {
              key: "finalize",
              label: (
                <span>
                  <FileDoneOutlined /> Finalizare
                </span>
              ),
              children: finalizareTab,
            },
          ]}
        />
      </Card>

      {/* Add/Edit Defect Modal (E-021.M1) */}
      <Modal
        title={editingItem ? "Editare defect" : "Adaugă defect"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={550}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="title"
            label="Titlu defect"
            rules={[{ required: true, message: "Titlul este obligatoriu" }]}
          >
            <Input placeholder="Ex: Fisură tencuială etaj 2" />
          </Form.Item>
          <Form.Item name="description" label="Descriere detaliată">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="severity"
                label="Severitate"
                rules={[{ required: true }]}
              >
                <Select
                  options={(
                    Object.keys(SEVERITY_CONFIG) as PunchItemSeverity[]
                  ).map((k) => ({
                    value: k,
                    label: SEVERITY_CONFIG[k].label,
                  }))}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="due_date" label="Deadline">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="location" label="Locație">
            <Input placeholder="Ex: Etaj 2, Apartament 5B" />
          </Form.Item>
          {editingItem && (
            <Form.Item name="status" label="Status">
              <Select
                options={(
                  Object.keys(STATUS_CONFIG) as PunchItemStatus[]
                ).map((k) => ({
                  value: k,
                  label: STATUS_CONFIG[k].label,
                }))}
              />
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* PV Recepție Modal */}
      <Modal
        title="Generare PV Recepție"
        open={receptionModalOpen}
        onCancel={() => {
          setReceptionModalOpen(false);
          receptionForm.resetFields();
        }}
        onOk={() => receptionForm.submit()}
        confirmLoading={receptionMut.isPending}
        okText="Generează PV"
        cancelText="Anulează"
      >
        <Form
          form={receptionForm}
          layout="vertical"
          onFinish={(values) =>
            receptionMut.mutate({
              ...values,
              title: `PV Recepție — ${dayjs().format("DD.MM.YYYY")}`,
              post_type: "DOCUMENT",
              is_official: true,
            })
          }
        >
          <Form.Item
            name="content"
            label="Observații PV"
          >
            <Input.TextArea
              rows={4}
              placeholder="Observații pentru procesul verbal de recepție..."
            />
          </Form.Item>
          <Alert
            type="warning"
            message="Aceasta va schimba statusul proiectului în 'Închis' și va notifica clientul."
            showIcon
          />
        </Form>
      </Modal>
    </div>
  );
}
