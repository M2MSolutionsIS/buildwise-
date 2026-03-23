/**
 * E-018 — Timesheet — Input & Review
 * F072: Logging ore efective pe task (estimate vs realizate, cost actual)
 * F073: Status task: ToDo→InProgress→Blocat→Done
 *
 * Grid-based input: rows = WBS activities, columns = days of week.
 * Input mode (team): editable, 0.5h increments, max 24h/day.
 * Review mode (PM): read-only, bulk approve/reject.
 * Locked (approved): greyed out, non-editable.
 */
import { useState, useMemo, useCallback } from "react";
import {
  Card,
  Table,
  Button,
  InputNumber,
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
  Tooltip,
  Popconfirm,
  Typography,
  Alert,
} from "antd";
import {
  PlusOutlined,
  CheckOutlined,
  CloseOutlined,
  SendOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  LeftOutlined,
  RightOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { TimesheetEntry, PMTask } from "../../../types";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";

dayjs.extend(isoWeek);

const { Title, Text } = Typography;

const STATUS_COLORS: Record<string, string> = {
  draft: "default",
  submitted: "processing",
  approved: "success",
  rejected: "error",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Ciornă",
  submitted: "Trimis",
  approved: "Aprobat",
  rejected: "Respins",
};

export default function TimesheetPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [currentWeek, setCurrentWeek] = useState(dayjs().startOf("isoWeek"));
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const weekStr = currentWeek.format("YYYY-[W]WW");
  const weekDays = useMemo(
    () => Array.from({ length: 7 }, (_, i) => currentWeek.add(i, "day")),
    [currentWeek]
  );

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: timesheetRes, isLoading } = useQuery({
    queryKey: ["timesheets", projectId, weekStr],
    queryFn: () => pmService.listTimesheets(projectId!, { week: weekStr }),
    enabled: !!projectId,
  });

  const { data: tasksRes } = useQuery({
    queryKey: ["pm-tasks", projectId],
    queryFn: () => pmService.listTasks(projectId!),
    enabled: !!projectId,
  });

  const entries = timesheetRes?.data ?? [];
  const tasks = tasksRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createTimesheet(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets", projectId] });
      message.success("Intrare pontaj adăugată");
      setIsModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const submitMut = useMutation({
    mutationFn: (id: string) => pmService.submitTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets", projectId] });
      message.success("Pontaj trimis pentru aprobare");
    },
  });

  const approveMut = useMutation({
    mutationFn: (id: string) => pmService.approveTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets", projectId] });
      message.success("Pontaj aprobat");
    },
  });

  const rejectMut = useMutation({
    mutationFn: (id: string) => pmService.rejectTimesheet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timesheets", projectId] });
      message.warning("Pontaj respins");
    },
  });

  // ─── Derived data ──────────────────────────────────────────────────────────

  const taskMap = useMemo(() => {
    const m = new Map<string, PMTask>();
    tasks.forEach((t) => m.set(t.id, t));
    return m;
  }, [tasks]);

  // Group entries by day
  const entriesByDay = useMemo(() => {
    const byDay: Record<string, TimesheetEntry[]> = {};
    weekDays.forEach((d) => {
      const key = d.format("YYYY-MM-DD");
      byDay[key] = entries.filter(
        (e) => dayjs(e.work_date).format("YYYY-MM-DD") === key
      );
    });
    return byDay;
  }, [entries, weekDays]);

  const totalHoursWeek = useMemo(
    () => entries.reduce((s, e) => s + e.hours, 0),
    [entries]
  );

  const totalCostWeek = useMemo(
    () => entries.reduce((s, e) => s + (e.cost ?? 0), 0),
    [entries]
  );

  const pendingCount = useMemo(
    () => entries.filter((e) => e.status === "submitted").length,
    [entries]
  );

  // ─── Week navigation ─────────────────────────────────────────────────────

  const prevWeek = useCallback(
    () => setCurrentWeek((w) => w.subtract(1, "week")),
    []
  );
  const nextWeek = useCallback(
    () => setCurrentWeek((w) => w.add(1, "week")),
    []
  );
  const goToday = useCallback(
    () => setCurrentWeek(dayjs().startOf("isoWeek")),
    []
  );

  // ─── Table columns ─────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Task",
      dataIndex: "task_id",
      key: "task",
      width: 200,
      render: (taskId: string | undefined) => {
        if (!taskId) return <Text type="secondary">— General —</Text>;
        const task = taskMap.get(taskId);
        return task ? task.title : taskId.slice(0, 8);
      },
    },
    {
      title: "Data",
      dataIndex: "work_date",
      key: "date",
      width: 120,
      render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
      sorter: (a: TimesheetEntry, b: TimesheetEntry) =>
        dayjs(a.work_date).unix() - dayjs(b.work_date).unix(),
    },
    {
      title: "Ore",
      dataIndex: "hours",
      key: "hours",
      width: 80,
      align: "right" as const,
      render: (h: number) => <Text strong>{h.toFixed(1)}h</Text>,
    },
    {
      title: "Rată orară",
      dataIndex: "hourly_rate",
      key: "rate",
      width: 100,
      align: "right" as const,
      render: (r?: number) => (r ? `${r.toFixed(0)} RON` : "—"),
    },
    {
      title: "Cost",
      dataIndex: "cost",
      key: "cost",
      width: 100,
      align: "right" as const,
      render: (c?: number) =>
        c ? <Text strong>{c.toFixed(0)} RON</Text> : "—",
    },
    {
      title: "Descriere",
      dataIndex: "description",
      key: "desc",
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (s: string) => (
        <Tag color={STATUS_COLORS[s]}>{STATUS_LABELS[s] ?? s}</Tag>
      ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 150,
      render: (_: unknown, rec: TimesheetEntry) => (
        <Space size="small">
          {rec.status === "draft" && (
            <Tooltip title="Trimite pentru aprobare">
              <Button
                size="small"
                icon={<SendOutlined />}
                onClick={() => submitMut.mutate(rec.id)}
              />
            </Tooltip>
          )}
          {rec.status === "submitted" && (
            <>
              <Tooltip title="Aprobă">
                <Button
                  size="small"
                  type="primary"
                  icon={<CheckOutlined />}
                  onClick={() => approveMut.mutate(rec.id)}
                />
              </Tooltip>
              <Popconfirm
                title="Respingi acest pontaj?"
                onConfirm={() => rejectMut.mutate(rec.id)}
              >
                <Button size="small" danger icon={<CloseOutlined />} />
              </Popconfirm>
            </>
          )}
          {rec.status === "approved" && (
            <Tag color="green">
              <CheckOutlined /> Aprobat
            </Tag>
          )}
        </Space>
      ),
    },
  ];

  // ─── Daily summary grid ───────────────────────────────────────────────────

  const daySummary = weekDays.map((day) => {
    const key = day.format("YYYY-MM-DD");
    const dayEntries = entriesByDay[key] ?? [];
    const hours = dayEntries.reduce((s, e) => s + e.hours, 0);
    const isToday = day.isSame(dayjs(), "day");
    return { day, key, hours, count: dayEntries.length, isToday };
  });

  // ─── Submit handler ───────────────────────────────────────────────────────

  const handleCreate = (values: Record<string, unknown>) => {
    const workDate = (values.work_date as dayjs.Dayjs).toISOString();
    createMut.mutate({
      ...values,
      work_date: workDate,
    });
  };

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
          <ClockCircleOutlined /> Pontaj — Timesheet (E-018)
        </Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          Înregistrează ore
        </Button>
      </div>

      {/* Stats row */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total ore săptămână"
              value={totalHoursWeek}
              suffix="h"
              prefix={<ClockCircleOutlined />}
              precision={1}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Cost total"
              value={totalCostWeek}
              suffix="RON"
              prefix={<DollarOutlined />}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Înregistrări"
              value={entries.length}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Pending aprobare"
              value={pendingCount}
              prefix={<TeamOutlined />}
              valueStyle={pendingCount > 0 ? { color: "#faad14" } : undefined}
            />
          </Card>
        </Col>
      </Row>

      {/* Week navigation + day summary grid */}
      <Card
        size="small"
        style={{ marginBottom: 16 }}
        title={
          <Space>
            <Button icon={<LeftOutlined />} size="small" onClick={prevWeek} />
            <Text strong>
              {currentWeek.format("DD MMM")} –{" "}
              {currentWeek.add(6, "day").format("DD MMM YYYY")}
            </Text>
            <Button icon={<RightOutlined />} size="small" onClick={nextWeek} />
            <Button size="small" onClick={goToday}>
              Azi
            </Button>
          </Space>
        }
      >
        <div style={{ display: "flex", gap: 8 }}>
          {daySummary.map((ds) => (
            <div
              key={ds.key}
              style={{
                flex: 1,
                textAlign: "center",
                padding: "8px 4px",
                borderRadius: 6,
                background: ds.isToday
                  ? "#e6f4ff"
                  : ds.hours > 0
                  ? "#f6ffed"
                  : "#fafafa",
                border: ds.isToday ? "2px solid #1677ff" : "1px solid #f0f0f0",
              }}
            >
              <div style={{ fontSize: 12, color: "#666" }}>
                {ds.day.format("ddd")}
              </div>
              <div style={{ fontWeight: 600 }}>{ds.day.format("DD")}</div>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: ds.hours > 8 ? "#ff4d4f" : ds.hours > 0 ? "#52c41a" : "#ccc",
                }}
              >
                {ds.hours > 0 ? `${ds.hours.toFixed(1)}h` : "—"}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Validation alert */}
      {daySummary.some((ds) => ds.hours > 24) && (
        <Alert
          type="error"
          message="Ore zilnice depășesc 24h!"
          description="Verifică înregistrările — o zi nu poate avea mai mult de 24 ore loggate."
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Entries table */}
      <Card title="Înregistrări pontaj">
        <Table
          columns={columns}
          dataSource={entries}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 20, showSizeChanger: true }}
          size="middle"
          rowClassName={(rec) =>
            rec.status === "approved"
              ? "row-approved"
              : rec.status === "rejected"
              ? "row-rejected"
              : ""
          }
        />
      </Card>

      {/* Add entry modal */}
      <Modal
        title="Înregistrare ore"
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="task_id" label="Task">
            <Select
              placeholder="Selectează task (opțional)"
              allowClear
              showSearch
              optionFilterProp="label"
              options={tasks.map((t) => ({
                value: t.id,
                label: t.title,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="work_date"
            label="Data"
            rules={[{ required: true, message: "Data este obligatorie" }]}
            initialValue={dayjs()}
          >
            <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="hours"
                label="Ore"
                rules={[
                  { required: true, message: "Ore sunt obligatorii" },
                  {
                    type: "number",
                    max: 24,
                    message: "Max 24h/zi",
                  },
                ]}
              >
                <InputNumber
                  min={0.5}
                  max={24}
                  step={0.5}
                  style={{ width: "100%" }}
                  placeholder="0.5"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="hourly_rate" label="Rată orară (RON)">
                <InputNumber
                  min={0}
                  step={10}
                  style={{ width: "100%" }}
                  placeholder="50"
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="Descriere activitate">
            <Input.TextArea rows={3} placeholder="Ce ai lucrat..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
