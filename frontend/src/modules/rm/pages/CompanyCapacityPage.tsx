/**
 * E-036 — Company Capacity Dashboard
 * F-codes: F121 (Rapoarte utilizare resurse), F122 (Analize comparative + Predicții)
 * Dashboard strategic: câte proiecte poate lua firma simultan
 * Heatmap echipe × luni, simulare what-if, trend utilizare
 */
import { useState, useMemo } from "react";
import {
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Spin,
  Tag,
  Table,
  Progress,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Button,
  Alert,
  Space,
  Tooltip,
  Divider,
  Empty,
} from "antd";
import {
  ProjectOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { rmService } from "../services/rmService";
import type { ResourceUtilization } from "../types";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";

const { Title, Text } = Typography;

/* ── Color helper based on utilization % ──────────────────────────────── */
function utilizationColor(pct: number): string {
  if (pct > 100) return "#ff4d4f";
  if (pct >= 90) return "#fa8c16";
  if (pct >= 75) return "#fadb14";
  if (pct >= 50) return "#52c41a";
  return "#d9f7be";
}

function utilizationStatus(pct: number): string {
  if (pct > 100) return "Supraîncărcat";
  if (pct >= 90) return "Critic";
  if (pct >= 75) return "Ridicat";
  if (pct >= 50) return "Optim";
  return "Disponibil";
}

/* ── Generate month labels for heatmap ───────────────────────────────── */
function generateMonthLabels(count: number): { key: string; label: string }[] {
  const months: { key: string; label: string }[] = [];
  const now = dayjs();
  for (let i = -2; i < count; i++) {
    const m = now.add(i, "month");
    months.push({
      key: m.format("YYYY-MM"),
      label: m.format("MMM YYYY"),
    });
  }
  return months;
}

/* ── Simulation types ────────────────────────────────────────────────── */
interface SimTeam {
  name: string;
  allocation: number;
}

interface SimForm {
  project_name: string;
  duration_weeks: number;
  start_date: dayjs.Dayjs | null;
  teams: SimTeam[];
}

export default function CompanyCapacityPage() {
  const [simActive, setSimActive] = useState(false);
  const [simResult, setSimResult] = useState<{
    canAccept: boolean;
    message: string;
    bottlenecks: string[];
  } | null>(null);
  const [form] = Form.useForm<SimForm>();

  /* ── Queries ──────────────────────────────────────────────────────── */
  const { data: capacityData, isLoading: loadingCap } = useQuery({
    queryKey: ["rm-capacity"],
    queryFn: () => rmService.getCapacity(),
  });

  const { data: utilizationData, isLoading: loadingUtil } = useQuery({
    queryKey: ["rm-utilization-capacity"],
    queryFn: () => rmService.getUtilization(),
  });

  const { data: allocationsData, isLoading: loadingAlloc } = useQuery({
    queryKey: ["rm-allocations-all"],
    queryFn: () => rmService.listAllocations({ per_page: 200 }),
  });

  const { data: employeesData, isLoading: loadingEmp } = useQuery({
    queryKey: ["rm-employees-all-cap"],
    queryFn: () => rmService.listEmployees({ per_page: 200, status: "active" }),
  });

  const isLoading = loadingCap || loadingUtil || loadingAlloc || loadingEmp;
  const cap = capacityData?.data;
  const utilization = utilizationData?.data ?? [];
  const allocations = allocationsData?.data ?? [];
  const employees = employeesData?.data ?? [];

  /* ── Build heatmap data: group employees by department, show utilization per month ── */
  const months = useMemo(() => generateMonthLabels(8), []);

  const heatmapData = useMemo(() => {
    const deptMap = new Map<string, { name: string; employees: string[] }>();
    for (const emp of employees) {
      const dept = emp.department || "Fără departament";
      if (!deptMap.has(dept)) deptMap.set(dept, { name: dept, employees: [] });
      deptMap.get(dept)!.employees.push(emp.id);
    }

    return Array.from(deptMap.values()).map((dept) => {
      const row: Record<string, number> = {};
      const teamSize = dept.employees.length;

      for (const m of months) {
        const monthStart = dayjs(m.key + "-01");
        const monthEnd = monthStart.endOf("month");

        let totalAllocationPct = 0;
        for (const alloc of allocations) {
          if (!dept.employees.includes(alloc.employee_id ?? "")) continue;
          const aStart = dayjs(alloc.start_date);
          const aEnd = dayjs(alloc.end_date);
          if (aStart.isBefore(monthEnd) && aEnd.isAfter(monthStart)) {
            totalAllocationPct += alloc.allocation_percent || 100;
          }
        }
        row[m.key] = teamSize > 0 ? Math.round(totalAllocationPct / teamSize) : 0;
      }

      return { team: dept.name, teamSize, ...row };
    });
  }, [employees, allocations, months]);

  /* ── Heatmap table columns ─────────────────────────────────────────── */
  const heatmapColumns: ColumnsType<Record<string, unknown>> = [
    {
      title: "Echipă / Departament",
      dataIndex: "team",
      key: "team",
      width: 180,
      fixed: "left",
      render: (name: string, row: Record<string, unknown>) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {row.teamSize as number} angajați
          </Text>
        </Space>
      ),
    },
    ...months.map((m) => ({
      title: m.label,
      dataIndex: m.key,
      key: m.key,
      width: 100,
      align: "center" as const,
      render: (pct: number) => (
        <Tooltip title={`${utilizationStatus(pct ?? 0)} — ${pct ?? 0}%`}>
          <div
            style={{
              background: utilizationColor(pct ?? 0),
              borderRadius: 4,
              padding: "6px 4px",
              textAlign: "center",
              fontWeight: 600,
              fontSize: 12,
              color: (pct ?? 0) > 90 ? "#fff" : "#000",
              minHeight: 32,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {pct ?? 0}%
          </div>
        </Tooltip>
      ),
    })),
  ];

  /* ── Utilization trend (average per department) ──────────────────── */
  const avgUtilization = useMemo(() => {
    if (utilization.length === 0) return 0;
    return Math.round(
      utilization.reduce((s, u) => s + u.utilization_percent, 0) / utilization.length,
    );
  }, [utilization]);

  /* ── Utilization table ─────────────────────────────────────────────── */
  const utilColumns: ColumnsType<ResourceUtilization> = [
    {
      title: "Angajat",
      dataIndex: "employee_name",
      key: "name",
    },
    {
      title: "Ore alocate",
      dataIndex: "total_allocated_hours",
      key: "alloc",
      width: 100,
      render: (v: number) => v.toFixed(0),
    },
    {
      title: "Ore efective",
      dataIndex: "total_actual_hours",
      key: "actual",
      width: 100,
      render: (v: number) => v.toFixed(0),
    },
    {
      title: "Utilizare",
      dataIndex: "utilization_percent",
      key: "util",
      width: 150,
      render: (pct: number) => (
        <Progress
          percent={Math.min(pct, 100)}
          size="small"
          status={pct > 100 ? "exception" : pct >= 80 ? "success" : "normal"}
          format={() => `${pct.toFixed(0)}%`}
        />
      ),
      sorter: (a, b) => a.utilization_percent - b.utilization_percent,
      defaultSortOrder: "descend",
    },
    {
      title: "Proiecte",
      dataIndex: "project_count",
      key: "proj",
      width: 80,
    },
  ];

  /* ── What-If Simulation ─────────────────────────────────────────── */
  const handleSimulate = () => {
    const vals = form.getFieldsValue();
    if (!vals.project_name || !vals.duration_weeks || !vals.start_date) return;

    const startDate = vals.start_date;
    const durationWeeks = vals.duration_weeks;
    const teamsNeeded = vals.teams?.filter((t) => t?.name) ?? [];

    // Client-side simulation: check each month overlap
    const bottlenecks: string[] = [];
    let canAccept = true;

    for (const team of teamsNeeded) {
      for (const m of months) {
        const monthStart = dayjs(m.key + "-01");
        const monthEnd = monthStart.endOf("month");
        const simEnd = startDate.add(durationWeeks, "week");

        if (startDate.isBefore(monthEnd) && simEnd.isAfter(monthStart)) {
          const row = heatmapData.find((r) => r.team === team.name);
          const currentPct = (row as Record<string, unknown>)?.[m.key] as number ?? 0;
          const newPct = currentPct + (team.allocation || 0);

          if (newPct > 100) {
            bottlenecks.push(`${team.name} în ${m.label}: ${newPct}% (depășire +${newPct - 100}%)`);
            canAccept = false;
          }
        }
      }
    }

    setSimResult({
      canAccept,
      message: canAccept
        ? "Proiectul poate fi acceptat fără conflicte."
        : `Detectate ${bottlenecks.length} bottleneck-uri. Recomandare: amânați sau redistribuiți resursele.`,
      bottlenecks,
    });
    setSimActive(true);
  };

  const resetSimulation = () => {
    setSimActive(false);
    setSimResult(null);
    form.resetFields();
  };

  /* ── Render ─────────────────────────────────────────────────────── */
  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          Company Capacity Dashboard
        </Title>
        <Space>
          <Tag color="purple">E-036</Tag>
          <Tag>F121, F122</Tag>
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()} />
        </Space>
      </Row>

      {isLoading ? (
        <Spin style={{ display: "block", margin: "40px auto" }} />
      ) : (
        <>
          {/* ── KPI Cards ─────────────────────────────────────────────── */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Proiecte active"
                  value={cap?.active_projects_count ?? 0}
                  prefix={<ProjectOutlined />}
                  valueStyle={{ color: "#1677ff" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Angajați disponibili"
                  value={cap?.available_employees ?? 0}
                  suffix={`/ ${cap?.total_employees ?? 0}`}
                  prefix={<TeamOutlined />}
                  valueStyle={{
                    color:
                      (cap?.available_employees ?? 0) > 0 ? "#52c41a" : "#ff4d4f",
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Încărcare globală"
                  value={cap?.utilization_rate?.toFixed(1) ?? 0}
                  suffix="%"
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{
                    color:
                      (cap?.utilization_rate ?? 0) > 90
                        ? "#ff4d4f"
                        : (cap?.utilization_rate ?? 0) > 75
                          ? "#fa8c16"
                          : "#52c41a",
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Conflicte alocări"
                  value={cap?.allocations_with_conflicts ?? 0}
                  prefix={
                    (cap?.allocations_with_conflicts ?? 0) > 0 ? (
                      <WarningOutlined />
                    ) : (
                      <CheckCircleOutlined />
                    )
                  }
                  valueStyle={{
                    color:
                      (cap?.allocations_with_conflicts ?? 0) > 0
                        ? "#ff4d4f"
                        : "#52c41a",
                  }}
                />
              </Card>
            </Col>
          </Row>

          {/* ── Equipment KPIs ────────────────────────────────────────── */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Echipamente disponibile"
                  value={cap?.available_equipment ?? 0}
                  suffix={`/ ${cap?.total_equipment ?? 0}`}
                  valueStyle={{ fontSize: 18 }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Utilizare medie personal"
                  value={avgUtilization}
                  suffix="%"
                  prefix={<BarChartOutlined />}
                  valueStyle={{
                    fontSize: 18,
                    color: avgUtilization >= 80 ? "#52c41a" : avgUtilization >= 50 ? "#faad14" : "#ff4d4f",
                  }}
                />
              </Card>
            </Col>
          </Row>

          {/* ── Heatmap: Echipe × Luni ────────────────────────────────── */}
          <Card
            title="Heatmap: Echipe × Luni — Utilizare (%)"
            style={{ marginBottom: 24 }}
            extra={
              <Space>
                <Tag color="green">0-50%</Tag>
                <Tag color="lime">50-75%</Tag>
                <Tag color="gold">75-90%</Tag>
                <Tag color="orange">90-100%</Tag>
                <Tag color="red">&gt;100%</Tag>
              </Space>
            }
          >
            {heatmapData.length > 0 ? (
              <Table
                rowKey="team"
                columns={heatmapColumns}
                dataSource={heatmapData}
                pagination={false}
                size="small"
                scroll={{ x: 180 + months.length * 100 }}
              />
            ) : (
              <Empty description="Nu există angajați cu departament definit. Adăugați departamente angajaților pentru a vizualiza heatmap-ul." />
            )}
          </Card>

          {/* ── What-If Simulation (F122) ─────────────────────────────── */}
          <Card
            title={
              <Space>
                <ExperimentOutlined />
                <span>Simulare &quot;Ce-ar fi dacă?&quot;</span>
              </Space>
            }
            style={{ marginBottom: 24 }}
            extra={
              simActive ? (
                <Button size="small" onClick={resetSimulation}>
                  Resetează
                </Button>
              ) : null
            }
          >
            <Form form={form} layout="vertical" onFinish={handleSimulate}>
              <Row gutter={16}>
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="project_name"
                    label="Nume proiect"
                    rules={[{ required: true, message: "Introduceți numele" }]}
                  >
                    <Input placeholder="Proiect nou..." />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="duration_weeks"
                    label="Durată (săptămâni)"
                    rules={[{ required: true, message: "Introduceți durata" }]}
                  >
                    <InputNumber min={1} max={104} style={{ width: "100%" }} placeholder="12" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="start_date"
                    label="Data start"
                    rules={[{ required: true, message: "Selectați data" }]}
                  >
                    <DatePicker style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
              </Row>

              <Divider orientation="left" plain>
                Echipe necesare
              </Divider>

              <Form.List name="teams" initialValue={[{ name: "", allocation: 100 }]}>
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field) => (
                      <Row gutter={16} key={field.key}>
                        <Col xs={12} sm={10}>
                          <Form.Item
                            {...field}
                            name={[field.name, "name"]}
                            label={field.key === 0 ? "Departament / Echipă" : undefined}
                          >
                            <Input placeholder="ex: Instalații" />
                          </Form.Item>
                        </Col>
                        <Col xs={8} sm={6}>
                          <Form.Item
                            {...field}
                            name={[field.name, "allocation"]}
                            label={field.key === 0 ? "Alocare %" : undefined}
                          >
                            <InputNumber min={10} max={100} style={{ width: "100%" }} />
                          </Form.Item>
                        </Col>
                        <Col xs={4} sm={4}>
                          <Form.Item label={field.key === 0 ? " " : undefined}>
                            {fields.length > 1 && (
                              <Button danger size="small" onClick={() => remove(field.name)}>
                                ×
                              </Button>
                            )}
                          </Form.Item>
                        </Col>
                      </Row>
                    ))}
                    <Button type="dashed" onClick={() => add({ name: "", allocation: 100 })} block>
                      + Adaugă echipă
                    </Button>
                  </>
                )}
              </Form.List>

              <div style={{ marginTop: 16, textAlign: "right" }}>
                <Button type="primary" htmlType="submit" icon={<ExperimentOutlined />}>
                  Simulează
                </Button>
              </div>
            </Form>

            {/* Simulation result */}
            {simResult && (
              <div style={{ marginTop: 24 }}>
                <Alert
                  type={simResult.canAccept ? "success" : "warning"}
                  showIcon
                  icon={simResult.canAccept ? <CheckCircleOutlined /> : <WarningOutlined />}
                  message={simResult.canAccept ? "Proiectul poate fi acceptat" : "Bottleneck-uri detectate"}
                  description={
                    <>
                      <p>{simResult.message}</p>
                      {simResult.bottlenecks.length > 0 && (
                        <ul style={{ margin: 0, paddingLeft: 20 }}>
                          {simResult.bottlenecks.map((b, i) => (
                            <li key={i}>
                              <Text type="danger">{b}</Text>
                            </li>
                          ))}
                        </ul>
                      )}
                    </>
                  }
                />
              </div>
            )}
          </Card>

          {/* ── Utilizare resurse tabel (F121) ────────────────────────── */}
          <Card
            title="Raport utilizare resurse (F121)"
            extra={<Tag color="blue">{utilization.length} angajați</Tag>}
          >
            <Table<ResourceUtilization>
              rowKey="employee_id"
              columns={utilColumns}
              dataSource={utilization}
              pagination={{ pageSize: 15, showSizeChanger: true }}
              size="small"
              locale={{ emptyText: "Nicio alocare activă" }}
            />
          </Card>
        </>
      )}
    </>
  );
}
