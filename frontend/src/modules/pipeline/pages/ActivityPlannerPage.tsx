/**
 * E-011 — Activity Planner
 * F054: Planificator activități zilnice — Calendar per agent
 * F055: Vizite tehnice la obiectiv — Documentare vizite
 * F056: Log apeluri + urmărire emailuri
 */
import { useState, useMemo } from "react";
import {
  Calendar,
  Card,
  Tag,
  Typography,
  Badge,
  Row,
  Col,
  Button,
  Space,
  Select,
  Spin,
  Alert,
  Table,
  Tooltip,
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Switch,
  Tabs,
  Statistic,
  Popconfirm,
  App,
} from "antd";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import {
  PlusOutlined,
  PhoneOutlined,
  MailOutlined,
  TeamOutlined,
  EnvironmentOutlined,
  FileTextOutlined,
  CalendarOutlined,
  UnorderedListOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useSearchParams } from "react-router-dom";
import { pipelineService, type ActivityFilters } from "../services/pipelineService";
import type { Activity, ActivityListItem } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const { Title, Text } = Typography;
const { TextArea } = Input;

const ACTIVITY_TYPES = [
  { value: "call", label: "Apel", icon: <PhoneOutlined />, color: "#1677ff" },
  { value: "email", label: "Email", icon: <MailOutlined />, color: "#8c8c8c" },
  { value: "visit", label: "Vizită", icon: <EnvironmentOutlined />, color: "#52c41a" },
  { value: "meeting", label: "Meeting", icon: <TeamOutlined />, color: "#722ed1" },
  { value: "note", label: "Notă", icon: <FileTextOutlined />, color: "#faad14" },
];

const TYPE_COLORS: Record<string, string> = {
  call: "blue",
  email: "default",
  visit: "green",
  meeting: "purple",
  note: "gold",
};

const STATUS_COLORS: Record<string, string> = {
  planned: "processing",
  completed: "success",
  cancelled: "default",
};

function isOverdue(a: ActivityListItem): boolean {
  return a.status === "planned" && new Date(a.scheduled_date) < new Date();
}

export default function ActivityPlannerPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  // View mode
  const [viewMode, setViewMode] = useState<"calendar" | "list">("calendar");

  // Filters
  const [filterType, setFilterType] = useState<string | undefined>();
  const [filterStatus, setFilterStatus] = useState<string | undefined>();

  // Calendar panel date
  const [calendarDate, setCalendarDate] = useState<Dayjs>(dayjs());

  // Activity modal (E-011.M1)
  const [activityModalOpen, setActivityModalOpen] = useState(false);
  const [editingActivity, setEditingActivity] = useState<Activity | null>(null);
  const [activityForm] = Form.useForm();

  // Visit detail modal (F055)
  const [visitModalOpen, setVisitModalOpen] = useState(false);
  const [visitForm] = Form.useForm();
  const [visitActivityId, setVisitActivityId] = useState<string | null>(null);

  // Call log modal (F056)
  const [callLogOpen, setCallLogOpen] = useState(false);
  const [callForm] = Form.useForm();

  // Fetch activities for current month range
  const monthStart = calendarDate.startOf("month").subtract(7, "day").toISOString();
  const monthEnd = calendarDate.endOf("month").add(7, "day").toISOString();

  const filters: ActivityFilters = {
    date_from: monthStart,
    date_to: monthEnd,
    activity_type: filterType,
    status: filterStatus,
    per_page: 200,
    opportunity_id: searchParams.get("opportunity_id") || undefined,
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ["activities", filters],
    queryFn: () => pipelineService.listActivities(filters),
  });

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => pipelineService.createActivity(payload),
    onSuccess: () => {
      message.success("Activitate creată.");
      setActivityModalOpen(false);
      activityForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["activities"] });
    },
    onError: () => message.error("Eroare la crearea activității."),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pipelineService.updateActivity(id, payload),
    onSuccess: () => {
      message.success("Activitate actualizată.");
      setEditingActivity(null);
      setActivityModalOpen(false);
      setVisitModalOpen(false);
      setCallLogOpen(false);
      activityForm.resetFields();
      visitForm.resetFields();
      callForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["activities"] });
    },
    onError: () => message.error("Eroare la actualizare."),
  });

  const deleteMutation = useMutation({
    mutationFn: pipelineService.deleteActivity,
    onSuccess: () => {
      message.success("Activitate ștearsă.");
      queryClient.invalidateQueries({ queryKey: ["activities"] });
    },
  });

  const activities: ActivityListItem[] = data?.data ?? [];
  const overdueCount = activities.filter(isOverdue).length;
  const plannedCount = activities.filter((a) => a.status === "planned").length;
  const completedCount = activities.filter((a) => a.status === "completed").length;

  // Group activities by date for calendar
  const byDate = useMemo(() => {
    const map = new Map<string, ActivityListItem[]>();
    activities.forEach((a) => {
      const key = dayjs(a.scheduled_date).format("YYYY-MM-DD");
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(a);
    });
    return map;
  }, [activities]);

  // Calendar cell renderer
  const dateCellRender = (date: Dayjs) => {
    const key = date.format("YYYY-MM-DD");
    const dayActivities = byDate.get(key) ?? [];
    if (dayActivities.length === 0) return null;

    return (
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {dayActivities.slice(0, 3).map((a) => (
          <li key={a.id} style={{ marginBottom: 2 }}>
            <Badge
              status={isOverdue(a) ? "error" : (STATUS_COLORS[a.status] as "processing" | "success" | "default") ?? "default"}
              text={
                <Tooltip title={`${a.title} — ${ACTIVITY_TYPES.find((t) => t.value === a.activity_type)?.label ?? a.activity_type}`}>
                  <Text
                    style={{
                      fontSize: 11,
                      cursor: "pointer",
                      color: isOverdue(a) ? "#ff4d4f" : undefined,
                    }}
                    ellipsis
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditActivity(a.id);
                    }}
                  >
                    {a.title}
                  </Text>
                </Tooltip>
              }
            />
          </li>
        ))}
        {dayActivities.length > 3 && (
          <li>
            <Text type="secondary" style={{ fontSize: 10 }}>
              +{dayActivities.length - 3} more
            </Text>
          </li>
        )}
      </ul>
    );
  };

  const handleEditActivity = async (activityId: string) => {
    try {
      const res = await pipelineService.getActivity(activityId);
      const act = res.data;
      setEditingActivity(act);

      if (act.activity_type === "visit") {
        visitForm.setFieldsValue({
          title: act.title,
          description: act.description,
          visit_persons: act.visit_data?.persons,
          visit_observations: act.visit_data?.observations,
          visit_measurements: act.measurements ? JSON.stringify(act.measurements) : "",
        });
        setVisitActivityId(act.id);
        setVisitModalOpen(true);
      } else if (act.activity_type === "call") {
        callForm.setFieldsValue({
          title: act.title,
          description: act.description,
          call_duration_seconds: act.call_duration_seconds,
          call_outcome: act.call_outcome,
          status: act.status,
        });
        setCallLogOpen(true);
      } else {
        activityForm.setFieldsValue({
          activity_type: act.activity_type,
          title: act.title,
          description: act.description,
          scheduled_date: dayjs(act.scheduled_date),
          duration_minutes: act.duration_minutes,
          contact_id: act.contact_id,
          opportunity_id: act.opportunity_id,
        });
        setActivityModalOpen(true);
      }
    } catch {
      message.error("Eroare la încărcarea activității.");
    }
  };

  const handleCreateActivity = (values: Record<string, unknown>) => {
    const payload = {
      ...values,
      scheduled_date: (values.scheduled_date as Dayjs)?.toISOString(),
    };

    if (editingActivity) {
      updateMutation.mutate({ id: editingActivity.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const openNewActivity = (type?: string, date?: Dayjs) => {
    setEditingActivity(null);
    activityForm.resetFields();
    if (type) activityForm.setFieldsValue({ activity_type: type });
    if (date) activityForm.setFieldsValue({ scheduled_date: date });
    setActivityModalOpen(true);
  };

  // List view columns
  const columns: ColumnsType<ActivityListItem> = [
    {
      title: "Tip",
      dataIndex: "activity_type",
      key: "type",
      width: 100,
      render: (type: string) => {
        const t = ACTIVITY_TYPES.find((at) => at.value === type);
        return <Tag color={TYPE_COLORS[type]}>{t?.icon} {t?.label ?? type}</Tag>;
      },
    },
    {
      title: "Titlu",
      dataIndex: "title",
      key: "title",
      render: (title: string, record: ActivityListItem) => (
        <a onClick={() => handleEditActivity(record.id)}>{title}</a>
      ),
    },
    {
      title: "Data",
      dataIndex: "scheduled_date",
      key: "date",
      width: 160,
      sorter: (a, b) => new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime(),
      render: (date: string) => dayjs(date).format("DD.MM.YYYY HH:mm"),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 120,
      render: (status: string, record: ActivityListItem) => {
        if (isOverdue(record)) {
          return <Tag color="red" icon={<WarningOutlined />}>Restant</Tag>;
        }
        return (
          <Tag color={status === "completed" ? "green" : status === "cancelled" ? "default" : "blue"}>
            {status === "completed" ? "Finalizat" : status === "cancelled" ? "Anulat" : "Planificat"}
          </Tag>
        );
      },
    },
    {
      title: "Oportunitate",
      dataIndex: "opportunity_id",
      key: "opp",
      width: 100,
      render: (oppId: string) =>
        oppId ? (
          <a onClick={() => navigate(`/pipeline/opportunities/${oppId}`)}>
            Deschide
          </a>
        ) : (
          "—"
        ),
    },
    {
      title: "",
      key: "actions",
      width: 80,
      render: (_: unknown, record: ActivityListItem) => (
        <Space>
          {record.status === "planned" && (
            <Tooltip title="Marchează finalizat">
              <Button
                type="text"
                size="small"
                icon={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
                onClick={() =>
                  updateMutation.mutate({
                    id: record.id,
                    payload: { status: "completed", completed_at: new Date().toISOString() },
                  })
                }
              />
            </Tooltip>
          )}
          <Popconfirm title="Ștergi?" onConfirm={() => deleteMutation.mutate(record.id)} okText="Da" cancelText="Nu">
            <Button type="text" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (error) return <Alert type="error" message="Eroare la încărcarea activităților" />;

  return (
    <>
      {/* Header */}
      <Row gutter={16} style={{ marginBottom: 16 }} align="middle">
        <Col flex="auto">
          <Space>
            <Title level={3} style={{ margin: 0 }}>Planificator Activități</Title>
            {overdueCount > 0 && (
              <Tag color="red" icon={<WarningOutlined />}>{overdueCount} restante</Tag>
            )}
          </Space>
        </Col>
        <Col>
          <Space size="large">
            <Statistic title="Planificate" value={plannedCount} valueStyle={{ fontSize: 16 }} prefix={<ClockCircleOutlined />} />
            <Statistic title="Finalizate" value={completedCount} valueStyle={{ fontSize: 16, color: "#52c41a" }} prefix={<CheckCircleOutlined />} />
            <Statistic title="Restante" value={overdueCount} valueStyle={{ fontSize: 16, color: overdueCount > 0 ? "#ff4d4f" : undefined }} prefix={<WarningOutlined />} />
          </Space>
        </Col>
      </Row>

      {/* Controls */}
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle" justify="space-between">
          <Col>
            <Space>
              <Tabs
                activeKey={viewMode}
                onChange={(k) => setViewMode(k as "calendar" | "list")}
                size="small"
                items={[
                  { key: "calendar", label: <><CalendarOutlined /> Calendar</> },
                  { key: "list", label: <><UnorderedListOutlined /> Listă</> },
                ]}
              />
              <Select
                placeholder="Tip activitate"
                value={filterType}
                onChange={setFilterType}
                allowClear
                style={{ width: 160 }}
                options={ACTIVITY_TYPES.map((t) => ({ value: t.value, label: t.label }))}
              />
              <Select
                placeholder="Status"
                value={filterStatus}
                onChange={setFilterStatus}
                allowClear
                style={{ width: 140 }}
                options={[
                  { value: "planned", label: "Planificate" },
                  { value: "completed", label: "Finalizate" },
                  { value: "cancelled", label: "Anulate" },
                ]}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<PhoneOutlined />} onClick={() => openNewActivity("call")}>
                Log Apel
              </Button>
              <Button icon={<EnvironmentOutlined />} onClick={() => openNewActivity("visit")}>
                Vizită
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={() => openNewActivity()}>
                Activitate
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Content */}
      {isLoading ? (
        <Spin size="large" style={{ display: "block", margin: "60px auto" }} />
      ) : viewMode === "calendar" ? (
        <Card>
          <Calendar
            value={calendarDate}
            onChange={setCalendarDate}
            cellRender={(date, info) => {
              if (info.type === "date") return dateCellRender(date);
              return null;
            }}
            onSelect={(date, info) => {
              if (info.source === "date") {
                openNewActivity(undefined, date);
              }
            }}
          />
        </Card>
      ) : (
        <Card>
          <Table<ActivityListItem>
            rowKey="id"
            columns={columns}
            dataSource={activities}
            pagination={{ pageSize: 20, showSizeChanger: true }}
            size="small"
            rowClassName={(record) => (isOverdue(record) ? "ant-table-row-overdue" : "")}
          />
        </Card>
      )}

      {/* Empty state CTA */}
      {!isLoading && activities.length === 0 && (
        <div style={{ textAlign: "center", padding: 48 }}>
          <CalendarOutlined style={{ fontSize: 48, color: "#bbb" }} />
          <Title level={4} style={{ marginTop: 16 }}>Planifică prima activitate</Title>
          <Text type="secondary">Apeluri, întâlniri, vizite tehnice — organizează-ți ziua de muncă</Text>
          <br /><br />
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => openNewActivity()}>
            Prima Activitate
          </Button>
        </div>
      )}

      {/* ─── E-011.M1 — New/Edit Activity Modal ──────────────────────────── */}
      <Modal
        title={editingActivity ? "Editează activitate" : "Activitate nouă"}
        open={activityModalOpen}
        onOk={() => activityForm.submit()}
        onCancel={() => {
          setActivityModalOpen(false);
          setEditingActivity(null);
          activityForm.resetFields();
        }}
        okText="Salvează"
        cancelText="Anulează"
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={520}
      >
        <Form
          form={activityForm}
          layout="vertical"
          onFinish={handleCreateActivity}
          initialValues={{ activity_type: "call", scheduled_date: dayjs() }}
        >
          <Form.Item name="activity_type" label="Tip activitate" rules={[{ required: true }]}>
            <Select>
              {ACTIVITY_TYPES.map((t) => (
                <Select.Option key={t.value} value={t.value}>
                  <Space>{t.icon} {t.label}</Space>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="title" label="Titlu" rules={[{ required: true, message: "Introdu titlul" }]}>
            <Input placeholder="Ex: Apel follow-up client X" />
          </Form.Item>

          <Row gutter={12}>
            <Col span={14}>
              <Form.Item name="scheduled_date" label="Data" rules={[{ required: true, message: "Selectează data" }]}>
                <DatePicker showTime format="DD.MM.YYYY HH:mm" style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={10}>
              <Form.Item name="duration_minutes" label="Durată (min)">
                <InputNumber min={5} max={480} step={15} style={{ width: "100%" }} placeholder="30" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="opportunity_id" label="Oportunitate (opțional)">
            <Input placeholder="ID oportunitate" />
          </Form.Item>

          <Form.Item name="contact_id" label="Contact (opțional)">
            <Input placeholder="ID contact" />
          </Form.Item>

          <Form.Item name="description" label="Notițe">
            <TextArea rows={3} placeholder="Detalii suplimentare..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* ─── F055 — Visit Documentation Modal ────────────────────────────── */}
      <Modal
        title={
          <Space>
            <EnvironmentOutlined style={{ color: "#52c41a" }} />
            Documentare vizită tehnică
          </Space>
        }
        open={visitModalOpen}
        onOk={() => {
          visitForm.validateFields().then((values) => {
            const payload: Record<string, unknown> = {
              title: values.title,
              description: values.description,
              status: values.completed ? "completed" : "planned",
              completed_at: values.completed ? new Date().toISOString() : undefined,
              visit_data: {
                persons: values.visit_persons,
                observations: values.visit_observations,
                photos: values.visit_photos,
              },
              measurements: values.visit_measurements
                ? JSON.parse(values.visit_measurements)
                : undefined,
            };
            if (visitActivityId) {
              updateMutation.mutate({ id: visitActivityId, payload });
            }
          }).catch(() => {});
        }}
        onCancel={() => {
          setVisitModalOpen(false);
          setVisitActivityId(null);
          setEditingActivity(null);
          visitForm.resetFields();
        }}
        okText="Salvează"
        cancelText="Anulează"
        confirmLoading={updateMutation.isPending}
        width={600}
      >
        <Form form={visitForm} layout="vertical">
          <Form.Item name="title" label="Titlu vizită">
            <Input />
          </Form.Item>

          <Form.Item name="visit_persons" label="Persoane prezente">
            <TextArea rows={2} placeholder="Nume persoane prezente la vizită, separate prin virgulă" />
          </Form.Item>

          <Form.Item name="visit_observations" label="Observații">
            <TextArea rows={4} placeholder="Observații din teren: starea clădirii, access, particularități..." />
          </Form.Item>

          <Form.Item name="visit_measurements" label="Măsurători (JSON)">
            <TextArea
              rows={3}
              placeholder='{"suprafata_mp": 120, "etaje": 3, "tip_geam": "dublu", "u_value": 1.2}'
            />
          </Form.Item>

          <Form.Item name="visit_photos" label="Fotografii (URL-uri separate prin virgulă)">
            <TextArea rows={2} placeholder="https://... , https://..." />
          </Form.Item>

          <Form.Item name="description" label="Note adiționale">
            <TextArea rows={2} />
          </Form.Item>

          <Form.Item name="completed" label="Marchează ca finalizată" valuePropName="checked">
            <Switch checkedChildren="Da" unCheckedChildren="Nu" />
          </Form.Item>
        </Form>
      </Modal>

      {/* ─── F056 — Call Log Modal ────────────────────────────────────────── */}
      <Modal
        title={
          <Space>
            <PhoneOutlined style={{ color: "#1677ff" }} />
            Log apel
          </Space>
        }
        open={callLogOpen}
        onOk={() => {
          callForm.validateFields().then((values) => {
            if (editingActivity) {
              updateMutation.mutate({
                id: editingActivity.id,
                payload: {
                  title: values.title,
                  description: values.description,
                  call_duration_seconds: values.call_duration_seconds,
                  call_outcome: values.call_outcome,
                  status: values.status,
                  completed_at: values.status === "completed" ? new Date().toISOString() : undefined,
                },
              });
            }
          }).catch(() => {});
        }}
        onCancel={() => {
          setCallLogOpen(false);
          setEditingActivity(null);
          callForm.resetFields();
        }}
        okText="Salvează"
        cancelText="Anulează"
        confirmLoading={updateMutation.isPending}
        width={480}
      >
        <Form form={callForm} layout="vertical">
          <Form.Item name="title" label="Subiect apel" rules={[{ required: true }]}>
            <Input placeholder="Ex: Follow-up ofertă" />
          </Form.Item>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="call_duration_seconds" label="Durată (secunde)">
                <InputNumber min={0} step={30} style={{ width: "100%" }} placeholder="180" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="call_outcome" label="Rezultat">
                <Select
                  placeholder="Selectează"
                  options={[
                    { value: "answered", label: "Răspuns" },
                    { value: "no_answer", label: "Fără răspuns" },
                    { value: "busy", label: "Ocupat" },
                    { value: "voicemail", label: "Mesaj vocal" },
                    { value: "callback", label: "Apel înapoi" },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="status" label="Status">
            <Select
              options={[
                { value: "planned", label: "Planificat" },
                { value: "completed", label: "Finalizat" },
                { value: "cancelled", label: "Anulat" },
              ]}
            />
          </Form.Item>

          <Form.Item name="description" label="Note apel">
            <TextArea rows={3} placeholder="Ce s-a discutat, acțiuni de follow-up..." />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
