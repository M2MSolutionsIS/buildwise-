/**
 * E-016 + E-038 — Gantt Chart Dual-Layer
 * F-codes: F070 (Gantt forecast + dual-layer), F073 (Task status),
 *          F083 (Resource allocation per proiect sync RM),
 *          F117 (Alocare resurse pe proiecte/faze),
 *          F118 (Urmărire consum resurse real-time)
 *
 * Layer 1 (comun): Gantt standard — baseline (gray) vs actual (colored)
 * Layer 2 (P2 — E-038): Resource overlay — echipă=albastru, echipament=portocaliu
 *   - Toggle "Arată Resurse" / "Ascunde Resurse"
 *   - Conflict detection: bare roșii pulsante + popup rezolvare
 *   - Opțiuni rezolvare: Re-alocare, Amânare, Subcontractare
 *
 * Features:
 * - Dual bars: baseline (gray) vs actual (colored)
 * - Dependencies: FS, SS, FF, SF with arrow lines
 * - Critical path highlighted in red
 * - Zoom levels: day / week / month
 * - Milestone markers (diamond)
 * - Resource allocation dual-layer overlay
 * - Conflict detection + resolution popup
 * - Task status colors
 */
import { useState, useMemo, useCallback, useRef, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Spin,
  Alert,
  Button,
  Space,
  Segmented,
  Tag,
  Tooltip,
  Progress,
  Table,
  Badge,
  Empty,
  Switch,
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Statistic,
} from "antd";
import {
  ExclamationCircleOutlined,
  PlusOutlined,
  TeamOutlined,
  AimOutlined,
  WarningOutlined,
  SwapOutlined,
  ClockCircleOutlined,
  UserSwitchOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import dayjs from "dayjs";
import { pmService } from "../services/pmService";
import type { PMTask, TaskDependency, GanttResourceRow, ResourceConflict } from "../../../types";

const { Title, Text } = Typography;

// ─── Constants ──────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  todo: "#d9d9d9",
  in_progress: "#1677ff",
  blocked: "#ff4d4f",
  done: "#52c41a",
};

const STATUS_LABELS: Record<string, string> = {
  todo: "De Făcut",
  in_progress: "În Progres",
  blocked: "Blocat",
  done: "Finalizat",
};

const DEP_TYPE_LABELS: Record<string, string> = {
  finish_to_start: "FS",
  start_to_start: "SS",
  finish_to_finish: "FF",
  start_to_finish: "SF",
};

type ZoomLevel = "day" | "week" | "month";

const ZOOM_CONFIGS: Record<ZoomLevel, { unitDays: number; format: string; headerFormat: string }> = {
  day: { unitDays: 1, format: "DD", headerFormat: "MMM YYYY" },
  week: { unitDays: 7, format: "[S]W", headerFormat: "MMM YYYY" },
  month: { unitDays: 30, format: "MMM", headerFormat: "YYYY" },
};

const COL_WIDTH: Record<ZoomLevel, number> = { day: 30, week: 40, month: 60 };
const ROW_HEIGHT = 40;
const RESOURCE_ROW_HEIGHT = 20;

const RESOURCE_COLORS: Record<string, string> = {
  employee: "#1677ff",
  equipment: "#fa8c16",
};

const RESOURCE_LABELS: Record<string, string> = {
  employee: "Echipă",
  equipment: "Echipament",
};

const RESOLUTION_OPTIONS: { key: string; label: string; icon: React.ReactNode }[] = [
  { key: "reallocate", label: "Re-alocare resursă", icon: <UserSwitchOutlined /> },
  { key: "postpone", label: "Amânare activitate", icon: <ClockCircleOutlined /> },
  { key: "subcontract", label: "Subcontractare", icon: <SwapOutlined /> },
];

// ─── Main Component ─────────────────────────────────────────────────────────

export default function GanttChartPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [zoom, setZoom] = useState<ZoomLevel>("week");
  const [showResources, setShowResources] = useState(false);
  const [showCriticalOnly, setShowCriticalOnly] = useState(false);
  const [addTaskOpen, setAddTaskOpen] = useState(false);
  const [conflictModalOpen, setConflictModalOpen] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<ResourceConflict | null>(null);
  const [form] = Form.useForm();

  const ganttRef = useRef<HTMLDivElement>(null);

  // Fetch tasks
  const { data: tasksData, isLoading } = useQuery({
    queryKey: ["pm-tasks", projectId],
    queryFn: () => pmService.listTasks(projectId!),
    enabled: !!projectId,
  });

  // Fetch project
  const { data: projectData } = useQuery({
    queryKey: ["pm-project", projectId],
    queryFn: () => pmService.getProject(projectId!),
    enabled: !!projectId,
  });

  // E-038: Fetch gantt resource rows (dual-layer)
  const { data: ganttResourceData } = useQuery({
    queryKey: ["pm-gantt-resources", projectId],
    queryFn: () => pmService.listGanttResources(projectId!),
    enabled: !!projectId && showResources,
  });

  // E-038: Fetch resource conflicts
  const { data: conflictsData } = useQuery({
    queryKey: ["pm-gantt-conflicts", projectId],
    queryFn: () => pmService.listResourceConflicts(projectId!),
    enabled: !!projectId && showResources,
  });

  // E-038: Resolve conflict mutation
  const resolveConflictMut = useMutation({
    mutationFn: (payload: { resource_id: string; resolution: string; details?: Record<string, unknown> }) =>
      pmService.resolveConflict(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pm-gantt-resources", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pm-gantt-conflicts", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pm-allocations", projectId] });
      setConflictModalOpen(false);
      setSelectedConflict(null);
    },
  });

  // Fetch dependencies per task
  const tasks: PMTask[] = tasksData?.data ?? [];
  const project = projectData?.data;
  const ganttResources: GanttResourceRow[] = ganttResourceData?.data ?? [];
  const conflicts: ResourceConflict[] = conflictsData?.data ?? [];

  // E-038: Group resource rows by task_id
  const resourcesByTask = useMemo(() => {
    const map: Record<string, GanttResourceRow[]> = {};
    for (const r of ganttResources) {
      if (!map[r.task_id]) map[r.task_id] = [];
      map[r.task_id]!.push(r);
    }
    return map;
  }, [ganttResources]);

  // E-038: Count conflicts
  const conflictCount = conflicts.length;

  // Create task mutation
  const createTaskMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createTask(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pm-tasks", projectId] });
      setAddTaskOpen(false);
      form.resetFields();
    },
  });

  // Filter tasks
  const displayTasks = useMemo(() => {
    let filtered = [...tasks];
    if (showCriticalOnly) {
      filtered = filtered.filter((t) => t.is_critical_path);
    }
    return filtered.sort((a, b) => a.sort_order - b.sort_order);
  }, [tasks, showCriticalOnly]);

  // Compute timeline bounds
  const { timelineStart, totalUnits } = useMemo(() => {
    if (displayTasks.length === 0) {
      const now = dayjs();
      return {
        timelineStart: now.startOf("month"),
        totalUnits: 90,
      };
    }

    const dates = displayTasks.flatMap((t) => {
      const d: dayjs.Dayjs[] = [];
      if (t.planned_start) d.push(dayjs(t.planned_start));
      if (t.planned_end) d.push(dayjs(t.planned_end));
      if (t.actual_start) d.push(dayjs(t.actual_start));
      if (t.actual_end) d.push(dayjs(t.actual_end));
      return d;
    });

    if (dates.length === 0) {
      const now = dayjs();
      return {
        timelineStart: now.startOf("month"),
        totalUnits: 90,
      };
    }

    const minDate = dates.reduce((a, b) => (a.isBefore(b) ? a : b)).subtract(7, "day").startOf("week");
    const maxDate = dates.reduce((a, b) => (a.isAfter(b) ? a : b)).add(14, "day").endOf("week");
    const unitDays = ZOOM_CONFIGS[zoom].unitDays;
    const units = Math.ceil(maxDate.diff(minDate, "day") / unitDays) + 2;

    return { timelineStart: minDate, totalUnits: units };
  }, [displayTasks, zoom]);

  // Compute task dependencies map (task_id -> dependencies)
  const [depsMap, setDepsMap] = useState<Record<string, TaskDependency[]>>({});

  useEffect(() => {
    const fetchDeps = async () => {
      const map: Record<string, TaskDependency[]> = {};
      for (const task of displayTasks) {
        try {
          const res = await pmService.getTask(task.id);
          if (res.data?.dependencies) {
            map[task.id] = res.data.dependencies;
          }
        } catch {
          // ignore
        }
      }
      setDepsMap(map);
    };
    if (displayTasks.length > 0) fetchDeps();
  }, [displayTasks.length]);

  // Helper: get bar position for a task
  const getBarPosition = useCallback(
    (start?: string, end?: string) => {
      if (!start) return { left: 0, width: 0 };
      const startD = dayjs(start);
      const endD = end ? dayjs(end) : startD.add(1, "day");
      const unitDays = ZOOM_CONFIGS[zoom].unitDays;
      const colW = COL_WIDTH[zoom];
      const left = (startD.diff(timelineStart, "day") / unitDays) * colW;
      const width = Math.max((endD.diff(startD, "day") / unitDays) * colW, colW / 2);
      return { left, width };
    },
    [zoom, timelineStart]
  );

  // Timeline header columns
  const timelineHeaders = useMemo(() => {
    const headers: { label: string; key: string }[] = [];
    const unitDays = ZOOM_CONFIGS[zoom].unitDays;
    const fmt = ZOOM_CONFIGS[zoom].format;
    let current = timelineStart;
    for (let i = 0; i < totalUnits; i++) {
      headers.push({
        label: current.format(fmt),
        key: current.toISOString(),
      });
      current = current.add(unitDays, "day");
    }
    return headers;
  }, [zoom, timelineStart, totalUnits]);

  // Today marker position
  const todayPos = useMemo(() => {
    const now = dayjs();
    const unitDays = ZOOM_CONFIGS[zoom].unitDays;
    return (now.diff(timelineStart, "day") / unitDays) * COL_WIDTH[zoom];
  }, [zoom, timelineStart]);

  // E-038: Compute row height per task (includes resource sub-rows when toggled)
  const getTaskRowHeight = useCallback(
    (task: PMTask) => {
      if (!showResources) return ROW_HEIGHT;
      const taskResources = resourcesByTask[task.id] ?? [];
      const resourceRows = Math.max(taskResources.length, 0);
      return ROW_HEIGHT + (resourceRows > 0 ? resourceRows * RESOURCE_ROW_HEIGHT + 4 : 0);
    },
    [showResources, resourcesByTask]
  );

  // E-038: Compute cumulative Y offset per task
  const taskYOffsets = useMemo(() => {
    const offsets: number[] = [];
    let cumY = 0;
    for (const task of displayTasks) {
      offsets.push(cumY);
      cumY += getTaskRowHeight(task);
    }
    return offsets;
  }, [displayTasks, getTaskRowHeight]);

  const totalChartHeight = useMemo(() => {
    return displayTasks.reduce((sum, task) => sum + getTaskRowHeight(task), 0);
  }, [displayTasks, getTaskRowHeight]);

  // E-038: Handle conflict click
  const handleConflictClick = (resourceRow: GanttResourceRow) => {
    if (!resourceRow.has_conflict || !resourceRow.conflict_details) return;
    const conflict = conflicts.find(
      (c) =>
        c.resource_id === resourceRow.resource_id &&
        (c.task_a_id === resourceRow.task_id || c.task_b_id === resourceRow.task_id)
    );
    if (conflict) {
      setSelectedConflict(conflict);
      setConflictModalOpen(true);
    }
  };

  const handleAddTask = async () => {
    const values = await form.validateFields();
    createTaskMut.mutate({
      title: values.title,
      planned_start: values.dates?.[0]?.toISOString(),
      planned_end: values.dates?.[1]?.toISOString(),
      planned_duration_days: values.duration_days,
      estimated_hours: values.estimated_hours,
      assigned_to: values.assigned_to || undefined,
      is_milestone: values.is_milestone || false,
    });
  };

  if (!projectId) {
    return <Alert type="error" message="ID proiect lipsă" />;
  }

  if (isLoading) {
    return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  }

  const colW = COL_WIDTH[zoom];
  const chartWidth = totalUnits * colW;

  return (
    <>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Button onClick={() => navigate(-1)}>Înapoi</Button>
            <Title level={3} style={{ margin: 0 }}>
              Gantt Chart {project ? `— ${project.name}` : ""}
            </Title>
          </Space>
        </Col>
        <Col>
          <Space wrap>
            <Segmented
              value={zoom}
              onChange={(v) => setZoom(v as ZoomLevel)}
              options={[
                { label: "Zi", value: "day" },
                { label: "Săptămână", value: "week" },
                { label: "Lună", value: "month" },
              ]}
            />
            <Tooltip title="Arată doar calea critică">
              <Switch
                checkedChildren={<AimOutlined />}
                unCheckedChildren="CP"
                checked={showCriticalOnly}
                onChange={setShowCriticalOnly}
              />
            </Tooltip>
            <Tooltip title={showResources ? "Ascunde Resurse" : "Arată Resurse"}>
              <Badge count={showResources ? conflictCount : 0} size="small" offset={[-4, 0]}>
                <Button
                  type={showResources ? "primary" : "default"}
                  icon={<TeamOutlined />}
                  onClick={() => setShowResources(!showResources)}
                >
                  {showResources ? "Ascunde Resurse" : "Arată Resurse"}
                </Button>
              </Badge>
            </Tooltip>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setAddTaskOpen(true)}
            >
              Task Nou
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Legend */}
      <Row style={{ marginBottom: 12 }}>
        <Space size="large" wrap>
          <Space size={4}>
            <div style={{ width: 16, height: 8, background: "#bfbfbf", borderRadius: 2 }} />
            <Text type="secondary">Planificat (baseline)</Text>
          </Space>
          <Space size={4}>
            <div style={{ width: 16, height: 8, background: "#1677ff", borderRadius: 2 }} />
            <Text type="secondary">Realizat</Text>
          </Space>
          <Space size={4}>
            <div style={{ width: 16, height: 8, background: "#ff4d4f", borderRadius: 2, border: "2px solid #ff4d4f" }} />
            <Text type="secondary">Cale critică</Text>
          </Space>
          <Space size={4}>
            <div style={{ width: 10, height: 10, background: "#faad14", transform: "rotate(45deg)" }} />
            <Text type="secondary">Milestone</Text>
          </Space>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <Tag key={k} color={STATUS_COLORS[k]}>{v}</Tag>
          ))}
          {showResources && (
            <>
              <Space size={4}>
                <div style={{ width: 16, height: 8, background: RESOURCE_COLORS.employee, borderRadius: 2 }} />
                <Text type="secondary">Echipă (Layer 2)</Text>
              </Space>
              <Space size={4}>
                <div style={{ width: 16, height: 8, background: RESOURCE_COLORS.equipment, borderRadius: 2 }} />
                <Text type="secondary">Echipament (Layer 2)</Text>
              </Space>
              <Space size={4}>
                <div style={{ width: 16, height: 8, background: "#ff4d4f", borderRadius: 2, border: "2px solid #ff4d4f" }} />
                <Text type="secondary">Conflict resurse</Text>
              </Space>
            </>
          )}
        </Space>
      </Row>

      {/* E-038: Conflict Alert Banner */}
      {showResources && conflictCount > 0 && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message={`${conflictCount} conflict${conflictCount > 1 ? "e" : ""} de resurse detectat${conflictCount > 1 ? "e" : ""}`}
          description="Click pe barele roșii din Layer 2 pentru opțiuni de rezolvare."
          style={{ marginBottom: 12 }}
        />
      )}

      {displayTasks.length === 0 ? (
        <Card>
          <Empty description="Definește structura WBS pentru a vedea Gantt-ul">
            <Button type="primary" onClick={() => setAddTaskOpen(true)}>
              Adaugă primul task
            </Button>
          </Empty>
        </Card>
      ) : (
        <Card bodyStyle={{ padding: 0, overflow: "hidden" }}>
          <div style={{ display: "flex", overflow: "auto" }} ref={ganttRef}>
            {/* Left panel — task list */}
            <div style={{ minWidth: 320, maxWidth: 320, borderRight: "2px solid #f0f0f0", flexShrink: 0 }}>
              {/* Header */}
              <div style={{
                height: 48,
                display: "flex",
                alignItems: "center",
                padding: "0 12px",
                background: "#fafafa",
                borderBottom: "1px solid #f0f0f0",
                fontWeight: 600,
              }}>
                <span style={{ flex: 1 }}>Task</span>
                <span style={{ width: 50, textAlign: "center" }}>Status</span>
                <span style={{ width: 40, textAlign: "center" }}>%</span>
              </div>
              {/* Task rows */}
              {displayTasks.map((task) => {
                const taskRes = resourcesByTask[task.id] ?? [];
                const hasConflicts = taskRes.some((r) => r.has_conflict);
                return (
                  <div key={task.id} style={{ borderBottom: "1px solid #f5f5f5" }}>
                    {/* Main task row */}
                    <div
                      style={{
                        height: ROW_HEIGHT,
                        display: "flex",
                        alignItems: "center",
                        padding: "0 12px",
                        background: task.is_critical_path ? "#fff1f0" : undefined,
                        cursor: "pointer",
                      }}
                      onClick={() => navigate(`/pm/projects/${projectId}/tasks/${task.id}`)}
                    >
                      <Space style={{ flex: 1, overflow: "hidden" }} size={4}>
                        {task.is_milestone && (
                          <div style={{
                            width: 8, height: 8, background: "#faad14",
                            transform: "rotate(45deg)", flexShrink: 0,
                          }} />
                        )}
                        {task.is_critical_path && (
                          <ExclamationCircleOutlined style={{ color: "#ff4d4f", flexShrink: 0 }} />
                        )}
                        <Text ellipsis style={{ fontSize: 13 }}>{task.title}</Text>
                      </Space>
                      {hasConflicts && <WarningOutlined style={{ color: "#ff4d4f", marginRight: 4 }} />}
                      <Badge
                        color={STATUS_COLORS[task.status]}
                        style={{ width: 50, textAlign: "center" }}
                      />
                      <span style={{ width: 40, textAlign: "center", fontSize: 12 }}>
                        {task.percent_complete}%
                      </span>
                    </div>
                    {/* E-038: Resource sub-rows (Layer 2 labels) */}
                    {showResources && taskRes.length > 0 && (
                      <div style={{ paddingLeft: 24, background: "#fafafa" }}>
                        {taskRes.map((res) => (
                          <div
                            key={res.allocation_id}
                            style={{
                              height: RESOURCE_ROW_HEIGHT,
                              display: "flex",
                              alignItems: "center",
                              fontSize: 11,
                              color: res.has_conflict ? "#ff4d4f" : "#8c8c8c",
                            }}
                          >
                            <div
                              style={{
                                width: 8, height: 8, borderRadius: 2, marginRight: 6,
                                background: res.has_conflict ? "#ff4d4f" : RESOURCE_COLORS[res.resource_type] || "#8c8c8c",
                              }}
                            />
                            <Text ellipsis style={{ fontSize: 11, maxWidth: 200 }}>
                              {res.resource_name}
                            </Text>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Right panel — Gantt bars */}
            <div style={{ flex: 1, overflow: "auto" }}>
              {/* Timeline header */}
              <div style={{
                display: "flex",
                height: 48,
                background: "#fafafa",
                borderBottom: "1px solid #f0f0f0",
                position: "sticky",
                top: 0,
                zIndex: 2,
              }}>
                {timelineHeaders.map((h) => (
                  <div
                    key={h.key}
                    style={{
                      width: colW,
                      minWidth: colW,
                      textAlign: "center",
                      fontSize: 11,
                      lineHeight: "48px",
                      borderRight: "1px solid #f5f5f5",
                      color: "#8c8c8c",
                    }}
                  >
                    {h.label}
                  </div>
                ))}
              </div>

              {/* Gantt body */}
              <div style={{ position: "relative", width: chartWidth, minHeight: totalChartHeight }}>
                {/* Grid lines */}
                {timelineHeaders.map((h, i) => (
                  <div
                    key={h.key}
                    style={{
                      position: "absolute",
                      left: i * colW,
                      top: 0,
                      bottom: 0,
                      width: 1,
                      background: "#f5f5f5",
                    }}
                  />
                ))}

                {/* Today marker */}
                {todayPos > 0 && todayPos < chartWidth && (
                  <div
                    style={{
                      position: "absolute",
                      left: todayPos,
                      top: 0,
                      bottom: 0,
                      width: 2,
                      background: "#ff4d4f",
                      zIndex: 3,
                      opacity: 0.6,
                    }}
                  />
                )}

                {/* Task bars + E-038 Resource bars (Layer 2) */}
                {displayTasks.map((task, rowIdx) => {
                  const topY = taskYOffsets[rowIdx] ?? 0;
                  const planned = getBarPosition(task.planned_start, task.planned_end);
                  const actual = getBarPosition(
                    task.actual_start || task.planned_start,
                    task.actual_end || undefined
                  );

                  // For milestones
                  if (task.is_milestone) {
                    const mPos = getBarPosition(task.planned_start, task.planned_start);
                    return (
                      <div key={task.id}>
                        <Tooltip title={`${task.title} — Milestone`}>
                          <div
                            style={{
                              position: "absolute",
                              left: mPos.left - 6,
                              top: topY + ROW_HEIGHT / 2 - 6,
                              width: 12,
                              height: 12,
                              background: task.status === "done" ? "#52c41a" : "#faad14",
                              transform: "rotate(45deg)",
                              border: task.is_critical_path ? "2px solid #ff4d4f" : "1px solid #d48806",
                              zIndex: 2,
                            }}
                          />
                        </Tooltip>
                      </div>
                    );
                  }

                  // E-038: Task resource rows for dual-layer
                  const taskRes = resourcesByTask[task.id] ?? [];

                  return (
                    <div key={task.id}>
                      {/* Layer 1: Baseline bar (gray) */}
                      {planned.width > 0 && (
                        <Tooltip
                          title={
                            <div>
                              <div><strong>{task.title}</strong></div>
                              <div>Plan: {task.planned_start ? dayjs(task.planned_start).format("DD.MM.YYYY") : "—"} → {task.planned_end ? dayjs(task.planned_end).format("DD.MM.YYYY") : "—"}</div>
                              <div>Status: {STATUS_LABELS[task.status]}</div>
                              <div>Progres: {task.percent_complete}%</div>
                              {task.assigned_to && <div>Alocat: {task.assigned_to.slice(0, 8)}...</div>}
                            </div>
                          }
                        >
                          <div
                            style={{
                              position: "absolute",
                              left: planned.left,
                              top: topY + 6,
                              width: planned.width,
                              height: 12,
                              background: "#e8e8e8",
                              borderRadius: 3,
                              border: task.is_critical_path ? "2px solid #ff4d4f" : "1px solid #d9d9d9",
                              zIndex: 1,
                            }}
                          />
                        </Tooltip>
                      )}

                      {/* Layer 1: Actual bar (colored by status) */}
                      {actual.width > 0 && task.percent_complete > 0 && (
                        <div
                          style={{
                            position: "absolute",
                            left: actual.left,
                            top: topY + 22,
                            width: Math.max(actual.width * (task.percent_complete / 100), 4),
                            height: 12,
                            background: STATUS_COLORS[task.status] || "#1677ff",
                            borderRadius: 3,
                            border: task.is_critical_path ? "2px solid #ff4d4f" : undefined,
                            zIndex: 1,
                            opacity: 0.9,
                          }}
                        />
                      )}

                      {/* Layer 1: Progress indicator on baseline */}
                      {planned.width > 0 && task.percent_complete > 0 && (
                        <div
                          style={{
                            position: "absolute",
                            left: planned.left,
                            top: topY + 6,
                            width: planned.width * (task.percent_complete / 100),
                            height: 12,
                            background: STATUS_COLORS[task.status] || "#1677ff",
                            borderRadius: "3px 0 0 3px",
                            opacity: 0.4,
                            zIndex: 1,
                          }}
                        />
                      )}

                      {/* E-038 Layer 2: Resource allocation bars */}
                      {showResources && taskRes.map((res, resIdx) => {
                        const rPos = getBarPosition(res.start_date, res.end_date);
                        const resTopY = topY + ROW_HEIGHT + resIdx * RESOURCE_ROW_HEIGHT + 2;
                        const barColor = res.has_conflict ? "#ff4d4f" : (RESOURCE_COLORS[res.resource_type] || "#8c8c8c");

                        return (
                          <Tooltip
                            key={res.allocation_id}
                            title={
                              <div>
                                <div><strong>{res.resource_name}</strong></div>
                                <div>{RESOURCE_LABELS[res.resource_type] || res.resource_type}</div>
                                <div>{res.allocated_hours}h ({res.allocation_percent}%)</div>
                                <div>{dayjs(res.start_date).format("DD.MM")} — {dayjs(res.end_date).format("DD.MM.YYYY")}</div>
                                {res.has_conflict && (
                                  <div style={{ color: "#ff4d4f", fontWeight: 600 }}>
                                    ⚠ Conflict — click pentru rezolvare
                                  </div>
                                )}
                              </div>
                            }
                          >
                            <div
                              onClick={(e) => {
                                e.stopPropagation();
                                if (res.has_conflict) handleConflictClick(res);
                              }}
                              style={{
                                position: "absolute",
                                left: rPos.left,
                                top: resTopY,
                                width: Math.max(rPos.width, 8),
                                height: RESOURCE_ROW_HEIGHT - 4,
                                background: barColor,
                                borderRadius: 3,
                                opacity: res.has_conflict ? 0.85 : 0.6,
                                zIndex: 2,
                                cursor: res.has_conflict ? "pointer" : "default",
                                animation: res.has_conflict ? "pulse 1.5s infinite" : undefined,
                                border: res.has_conflict ? "2px solid #ff4d4f" : undefined,
                                display: "flex",
                                alignItems: "center",
                                paddingLeft: 4,
                                overflow: "hidden",
                              }}
                            >
                              {rPos.width > 60 && (
                                <span style={{ fontSize: 9, color: "#fff", whiteSpace: "nowrap" }}>
                                  {res.resource_name}
                                </span>
                              )}
                              {res.has_conflict && (
                                <WarningOutlined style={{ color: "#fff", fontSize: 10, marginLeft: 2 }} />
                              )}
                            </div>
                          </Tooltip>
                        );
                      })}
                    </div>
                  );
                })}

                {/* Dependency arrows */}
                <svg
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: chartWidth,
                    height: totalChartHeight,
                    pointerEvents: "none",
                    zIndex: 4,
                  }}
                >
                  <defs>
                    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
                      <polygon points="0 0, 8 3, 0 6" fill="#8c8c8c" />
                    </marker>
                    <marker id="arrowhead-critical" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
                      <polygon points="0 0, 8 3, 0 6" fill="#ff4d4f" />
                    </marker>
                  </defs>
                  {Object.entries(depsMap).flatMap(([taskId, deps]) => {
                    const taskIdx = displayTasks.findIndex((t) => t.id === taskId);
                    if (taskIdx < 0) return [];

                    return deps.map((dep) => {
                      const depIdx = displayTasks.findIndex((t) => t.id === dep.depends_on_id);
                      if (depIdx < 0) return null;

                      const fromTask = displayTasks[depIdx]!;
                      const toTask = displayTasks[taskIdx]!;
                      if (!fromTask || !toTask) return null;
                      const isCritical = fromTask.is_critical_path && toTask.is_critical_path;

                      const fromPos = getBarPosition(fromTask.planned_start, fromTask.planned_end);
                      const toPos = getBarPosition(toTask.planned_start, toTask.planned_end);
                      const fromY = (taskYOffsets[depIdx] ?? 0) + ROW_HEIGHT / 2;
                      const toY = (taskYOffsets[taskIdx] ?? 0) + ROW_HEIGHT / 2;

                      let x1: number, y1: number, x2: number, y2: number;

                      switch (dep.dependency_type) {
                        case "finish_to_start":
                          x1 = fromPos.left + fromPos.width; y1 = fromY;
                          x2 = toPos.left; y2 = toY;
                          break;
                        case "start_to_start":
                          x1 = fromPos.left; y1 = fromY;
                          x2 = toPos.left; y2 = toY;
                          break;
                        case "finish_to_finish":
                          x1 = fromPos.left + fromPos.width; y1 = fromY;
                          x2 = toPos.left + toPos.width; y2 = toY;
                          break;
                        case "start_to_finish":
                          x1 = fromPos.left; y1 = fromY;
                          x2 = toPos.left + toPos.width; y2 = toY;
                          break;
                        default:
                          x1 = fromPos.left + fromPos.width; y1 = fromY;
                          x2 = toPos.left; y2 = toY;
                      }

                      const midX = (x1 + x2) / 2;
                      const path = `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;

                      return (
                        <g key={`${dep.id}`}>
                          <path
                            d={path}
                            fill="none"
                            stroke={isCritical ? "#ff4d4f" : "#8c8c8c"}
                            strokeWidth={isCritical ? 2 : 1}
                            strokeDasharray={dep.dependency_type !== "finish_to_start" ? "4 2" : undefined}
                            markerEnd={isCritical ? "url(#arrowhead-critical)" : "url(#arrowhead)"}
                          />
                          <text
                            x={midX}
                            y={(y1 + y2) / 2 - 4}
                            fontSize={9}
                            fill={isCritical ? "#ff4d4f" : "#bfbfbf"}
                            textAnchor="middle"
                          >
                            {DEP_TYPE_LABELS[dep.dependency_type] || "FS"}
                          </text>
                        </g>
                      );
                    });
                  })}
                </svg>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* E-038: Resource Allocation Summary — Layer 2 Details */}
      {showResources && ganttResources.length > 0 && (
        <Card
          title={
            <Space>
              <TeamOutlined />
              <span>Alocare Resurse — Layer 2 (E-038)</span>
              {conflictCount > 0 && (
                <Badge count={conflictCount} style={{ backgroundColor: "#ff4d4f" }} />
              )}
            </Space>
          }
          style={{ marginTop: 16 }}
        >
          <Table
            dataSource={ganttResources}
            rowKey="allocation_id"
            pagination={false}
            size="small"
            columns={[
              {
                title: "Resursă",
                dataIndex: "resource_name",
                key: "resource_name",
                width: 180,
                render: (v: string, r: GanttResourceRow) => (
                  <Space>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: RESOURCE_COLORS[r.resource_type] || "#8c8c8c" }} />
                    <Text strong>{v}</Text>
                  </Space>
                ),
              },
              {
                title: "Tip",
                dataIndex: "resource_type",
                key: "resource_type",
                width: 100,
                render: (v: string) => (
                  <Tag color={v === "employee" ? "blue" : "orange"}>
                    {RESOURCE_LABELS[v] || v}
                  </Tag>
                ),
              },
              {
                title: "Perioadă",
                key: "period",
                width: 180,
                render: (_: unknown, r: GanttResourceRow) =>
                  `${dayjs(r.start_date).format("DD.MM")} — ${dayjs(r.end_date).format("DD.MM.YYYY")}`,
              },
              {
                title: "Ore",
                dataIndex: "allocated_hours",
                key: "allocated_hours",
                width: 80,
                align: "center" as const,
                render: (v: number) => `${v}h`,
              },
              {
                title: "Alocare %",
                dataIndex: "allocation_percent",
                key: "allocation_percent",
                width: 120,
                align: "center" as const,
                render: (v: number) => <Progress percent={v} size="small" />,
              },
              {
                title: "Status",
                dataIndex: "has_conflict",
                key: "has_conflict",
                width: 120,
                align: "center" as const,
                render: (v: boolean, r: GanttResourceRow) =>
                  v ? (
                    <Button
                      size="small"
                      danger
                      icon={<WarningOutlined />}
                      onClick={() => handleConflictClick(r)}
                    >
                      Conflict
                    </Button>
                  ) : (
                    <Tag color="green">OK</Tag>
                  ),
              },
            ]}
          />
        </Card>
      )}

      {/* Stats Summary */}
      {displayTasks.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} sm={6}>
            <Card size="small">
              <Statistic title="Total Tasks" value={tasks.length} />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card size="small">
              <Statistic
                title="Cale Critică"
                value={tasks.filter((t) => t.is_critical_path).length}
                valueStyle={{ color: "#ff4d4f" }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card size="small">
              <Statistic
                title="Blocate"
                value={tasks.filter((t) => t.status === "blocked").length}
                valueStyle={{ color: "#ff4d4f" }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card size="small">
              <Statistic
                title="Finalizate"
                value={tasks.filter((t) => t.status === "done").length}
                suffix={`/ ${tasks.length}`}
                valueStyle={{ color: "#52c41a" }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* E-038: Conflict Resolution Modal */}
      <Modal
        title={
          <Space>
            <WarningOutlined style={{ color: "#ff4d4f" }} />
            <span>Conflict de Resurse — Rezolvare</span>
          </Space>
        }
        open={conflictModalOpen}
        onCancel={() => { setConflictModalOpen(false); setSelectedConflict(null); }}
        footer={null}
        width={560}
      >
        {selectedConflict && (
          <div>
            <Alert
              type="error"
              showIcon
              message={`${selectedConflict.resource_name} (${RESOURCE_LABELS[selectedConflict.resource_type] || selectedConflict.resource_type})`}
              description={
                <div>
                  <div>Alocat simultan pe 2 activități în aceeași perioadă:</div>
                  <div style={{ marginTop: 8 }}>
                    <Tag color="blue">A: {selectedConflict.task_a_title}</Tag>
                    <Tag color="orange">B: {selectedConflict.task_b_title}</Tag>
                  </div>
                  <div style={{ marginTop: 4 }}>
                    Overlap: {dayjs(selectedConflict.overlap_start).format("DD.MM.YYYY")} — {dayjs(selectedConflict.overlap_end).format("DD.MM.YYYY")}
                  </div>
                </div>
              }
              style={{ marginBottom: 16 }}
            />
            <Title level={5}>Opțiuni rezolvare:</Title>
            <Space direction="vertical" style={{ width: "100%" }}>
              {RESOLUTION_OPTIONS.filter((opt) =>
                selectedConflict.resolution_options.includes(opt.key as "reallocate" | "postpone" | "subcontract")
              ).map((opt) => (
                <Button
                  key={opt.key}
                  block
                  size="large"
                  icon={opt.icon}
                  loading={resolveConflictMut.isPending}
                  onClick={() =>
                    resolveConflictMut.mutate({
                      resource_id: selectedConflict.resource_id,
                      resolution: opt.key,
                    })
                  }
                >
                  {opt.label}
                </Button>
              ))}
              {selectedConflict.resolution_options.length === 0 &&
                RESOLUTION_OPTIONS.map((opt) => (
                  <Button
                    key={opt.key}
                    block
                    size="large"
                    icon={opt.icon}
                    loading={resolveConflictMut.isPending}
                    onClick={() =>
                      resolveConflictMut.mutate({
                        resource_id: selectedConflict.resource_id,
                        resolution: opt.key,
                      })
                    }
                  >
                    {opt.label}
                  </Button>
                ))
              }
            </Space>
          </div>
        )}
      </Modal>

      {/* Add Task Modal */}
      <Modal
        title="Adaugă Task Nou"
        open={addTaskOpen}
        onOk={handleAddTask}
        onCancel={() => setAddTaskOpen(false)}
        confirmLoading={createTaskMut.isPending}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="Titlu" rules={[{ required: true, message: "Titlu obligatoriu" }]}>
            <Input placeholder="Denumire task" />
          </Form.Item>
          <Form.Item name="dates" label="Perioadă planificată">
            <DatePicker.RangePicker format="DD.MM.YYYY" style={{ width: "100%" }} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="duration_days" label="Durată (zile)">
                <InputNumber min={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="estimated_hours" label="Ore estimate">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="is_milestone" label="Milestone" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
    </>
  );
}
