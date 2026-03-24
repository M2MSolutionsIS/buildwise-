/**
 * E-040 — Financial Planning — RM
 * F-codes: F115 (Planificare financiară), F116 (Analiză costuri și economii)
 * Dashboard financiar: bugete per centru cost, bugetat vs realizat, alerte depășire
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
  Alert,
  Space,
  Button,
  Select,
  InputNumber,
  Modal,
  Form,
  Input,
  Tooltip,
  Progress,
  Divider,
  App,
} from "antd";
import {
  DollarOutlined,
  FundOutlined,
  WarningOutlined,
  PlusOutlined,
  ReloadOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  EditOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rmService } from "../services/rmService";
import type { BudgetEntry, BudgetEntryCreate, CostAnalysis } from "../types";
import type { ColumnsType } from "antd/es/table";

const { Title, Text } = Typography;

const CURRENT_YEAR = new Date().getFullYear();
const MONTHS = [
  "Ian", "Feb", "Mar", "Apr", "Mai", "Iun",
  "Iul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export default function FinancialPlanningPage() {
  const { message: msg } = App.useApp();
  const queryClient = useQueryClient();
  const [selectedYear, setSelectedYear] = useState(CURRENT_YEAR);
  const [costCenterFilter, setCostCenterFilter] = useState<string | undefined>(undefined);
  const [modalOpen, setModalOpen] = useState(false);
  const [editEntry, setEditEntry] = useState<BudgetEntry | null>(null);
  const [form] = Form.useForm();

  /* ── Queries ──────────────────────────────────────────────────────── */
  const { data: budgetsData, isLoading: loadingBudgets } = useQuery({
    queryKey: ["rm-budgets", selectedYear, costCenterFilter],
    queryFn: () =>
      rmService.listBudgets({
        per_page: 500,
        period_year: selectedYear,
        cost_center: costCenterFilter,
      }),
  });

  const { data: costAnalysisData, isLoading: loadingCost } = useQuery({
    queryKey: ["rm-cost-analysis", selectedYear, costCenterFilter],
    queryFn: () =>
      rmService.getCostAnalysis({
        period_year: selectedYear,
        cost_center: costCenterFilter,
      }),
  });

  const isLoading = loadingBudgets || loadingCost;
  const budgets = budgetsData?.data ?? [];
  const costAnalysis = costAnalysisData?.data ?? [];

  /* ── Mutations ────────────────────────────────────────────────────── */
  const createMut = useMutation({
    mutationFn: (data: BudgetEntryCreate) => rmService.createBudget(data),
    onSuccess: () => {
      msg.success("Buget creat cu succes");
      queryClient.invalidateQueries({ queryKey: ["rm-budgets"] });
      queryClient.invalidateQueries({ queryKey: ["rm-cost-analysis"] });
      closeModal();
    },
    onError: () => msg.error("Eroare la crearea bugetului"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<BudgetEntryCreate> }) =>
      rmService.updateBudget(id, data),
    onSuccess: () => {
      msg.success("Buget actualizat");
      queryClient.invalidateQueries({ queryKey: ["rm-budgets"] });
      queryClient.invalidateQueries({ queryKey: ["rm-cost-analysis"] });
      closeModal();
    },
    onError: () => msg.error("Eroare la actualizare"),
  });

  /* ── KPI Calculations ─────────────────────────────────────────────── */
  const kpis = useMemo(() => {
    const totalBudgeted = budgets.reduce((s, b) => s + b.budgeted_amount, 0);
    const totalActual = budgets.reduce((s, b) => s + b.actual_amount, 0);
    const totalVariance = totalBudgeted - totalActual;
    const overagePct = totalBudgeted > 0 ? ((totalActual - totalBudgeted) / totalBudgeted) * 100 : 0;

    // Simple linear forecast: project from current data
    const currentMonth = new Date().getMonth() + 1;
    const monthsElapsed = Math.max(1, currentMonth);
    const forecast = totalBudgeted > 0 ? (totalActual / monthsElapsed) * 12 : 0;

    return { totalBudgeted, totalActual, totalVariance, overagePct, forecast };
  }, [budgets]);

  const overBudgetEntries = useMemo(
    () => budgets.filter((b) => b.actual_amount > b.budgeted_amount && b.budgeted_amount > 0),
    [budgets],
  );

  /* ── Unique cost centers for filter ────────────────────────────────── */
  const costCenters = useMemo(() => {
    const set = new Set<string>();
    for (const b of budgets) set.add(b.cost_center);
    return Array.from(set).sort();
  }, [budgets]);

  /* ── Modal helpers ────────────────────────────────────────────────── */
  const openCreate = () => {
    setEditEntry(null);
    form.resetFields();
    form.setFieldsValue({ period_year: selectedYear, currency: "RON" });
    setModalOpen(true);
  };

  const openEdit = (entry: BudgetEntry) => {
    setEditEntry(entry);
    form.setFieldsValue({
      cost_center: entry.cost_center,
      category: entry.category,
      description: entry.description,
      period_month: entry.period_month,
      period_year: entry.period_year,
      budgeted_amount: entry.budgeted_amount,
      actual_amount: entry.actual_amount,
      currency: entry.currency,
    });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditEntry(null);
    form.resetFields();
  };

  const handleSave = async () => {
    const vals = await form.validateFields();
    if (editEntry) {
      updateMut.mutate({ id: editEntry.id, data: vals });
    } else {
      createMut.mutate(vals);
    }
  };

  /* ── Cost Analysis table columns ───────────────────────────────────── */
  const costColumns: ColumnsType<CostAnalysis> = [
    {
      title: "Centru cost",
      dataIndex: "cost_center",
      key: "cc",
      width: 180,
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: "Bugetat (RON)",
      dataIndex: "total_budgeted",
      key: "budgeted",
      width: 140,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Realizat (RON)",
      dataIndex: "total_actual",
      key: "actual",
      width: 140,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Varianță",
      dataIndex: "total_variance",
      key: "variance",
      width: 140,
      align: "right",
      render: (v: number) => (
        <Text type={v >= 0 ? "success" : "danger"} strong>
          {v >= 0 ? "+" : ""}
          {v.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
        </Text>
      ),
      sorter: (a, b) => a.total_variance - b.total_variance,
    },
    {
      title: "Depășire %",
      key: "pct",
      width: 130,
      render: (_: unknown, r: CostAnalysis) => {
        if (r.total_budgeted === 0) return <Text type="secondary">—</Text>;
        const pct = ((r.total_actual - r.total_budgeted) / r.total_budgeted) * 100;
        return (
          <Progress
            percent={Math.min(Math.abs(pct), 100)}
            size="small"
            status={pct > 10 ? "exception" : pct > 5 ? "active" : "success"}
            format={() => `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`}
            strokeColor={pct > 10 ? "#ff4d4f" : pct > 5 ? "#faad14" : "#52c41a"}
          />
        );
      },
    },
    {
      title: "Nr. intrări",
      key: "count",
      width: 80,
      align: "center",
      render: (_: unknown, r: CostAnalysis) => (
        <Tag>{r.entries?.length ?? 0}</Tag>
      ),
    },
  ];

  /* ── Budget entries detail table ───────────────────────────────────── */
  const budgetColumns: ColumnsType<BudgetEntry> = [
    {
      title: "Centru cost",
      dataIndex: "cost_center",
      key: "cc",
      width: 140,
      filters: costCenters.map((c) => ({ text: c, value: c })),
      onFilter: (val, rec) => rec.cost_center === val,
    },
    {
      title: "Categorie",
      dataIndex: "category",
      key: "cat",
      width: 130,
    },
    {
      title: "Descriere",
      dataIndex: "description",
      key: "desc",
      ellipsis: true,
      render: (v: string) => v || "—",
    },
    {
      title: "Lună",
      dataIndex: "period_month",
      key: "month",
      width: 80,
      render: (m: number) => MONTHS[m - 1] || m,
      sorter: (a, b) => a.period_month - b.period_month,
    },
    {
      title: "Bugetat",
      dataIndex: "budgeted_amount",
      key: "budgeted",
      width: 120,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
      sorter: (a, b) => a.budgeted_amount - b.budgeted_amount,
    },
    {
      title: "Realizat",
      dataIndex: "actual_amount",
      key: "actual",
      width: 120,
      align: "right",
      render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
    },
    {
      title: "Varianță",
      dataIndex: "variance",
      key: "var",
      width: 120,
      align: "right",
      render: (v: number) => (
        <Text type={v >= 0 ? "success" : "danger"}>
          {v >= 0 ? "+" : ""}
          {v.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}
        </Text>
      ),
      sorter: (a, b) => a.variance - b.variance,
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 80,
      align: "center",
      render: (_: unknown, rec: BudgetEntry) => (
        <Tooltip title="Editează">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(rec)} />
        </Tooltip>
      ),
    },
  ];

  /* ── Render ─────────────────────────────────────────────────────── */
  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          Financial Planning
        </Title>
        <Space>
          <Tag color="purple">E-040</Tag>
          <Tag>F115, F116</Tag>
          <Select
            value={selectedYear}
            onChange={setSelectedYear}
            style={{ width: 100 }}
            options={[
              { value: CURRENT_YEAR - 1, label: `${CURRENT_YEAR - 1}` },
              { value: CURRENT_YEAR, label: `${CURRENT_YEAR}` },
              { value: CURRENT_YEAR + 1, label: `${CURRENT_YEAR + 1}` },
            ]}
          />
          <Select
            value={costCenterFilter}
            onChange={setCostCenterFilter}
            allowClear
            placeholder="Centru cost"
            style={{ width: 160 }}
            options={costCenters.map((c) => ({ value: c, label: c }))}
          />
          <Button icon={<ReloadOutlined />} onClick={() => {
            queryClient.invalidateQueries({ queryKey: ["rm-budgets"] });
            queryClient.invalidateQueries({ queryKey: ["rm-cost-analysis"] });
          }} />
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Buget nou
          </Button>
        </Space>
      </Row>

      {isLoading ? (
        <Spin style={{ display: "block", margin: "40px auto" }} />
      ) : (
        <>
          {/* ── KPI Cards ───────────────────────────────────────────── */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Total bugetat"
                  value={kpis.totalBudgeted}
                  precision={2}
                  prefix={<DollarOutlined />}
                  suffix="RON"
                  valueStyle={{ color: "#1677ff" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Total realizat"
                  value={kpis.totalActual}
                  precision={2}
                  prefix={<FundOutlined />}
                  suffix="RON"
                  valueStyle={{
                    color: kpis.totalActual > kpis.totalBudgeted ? "#ff4d4f" : "#52c41a",
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Depășire"
                  value={Math.abs(kpis.overagePct)}
                  precision={1}
                  prefix={kpis.overagePct > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  suffix="%"
                  valueStyle={{
                    color:
                      kpis.overagePct > 10
                        ? "#ff4d4f"
                        : kpis.overagePct > 5
                          ? "#faad14"
                          : "#52c41a",
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Forecast anual"
                  value={kpis.forecast}
                  precision={2}
                  suffix="RON"
                  prefix={<FundOutlined />}
                  valueStyle={{ color: "#722ed1" }}
                />
              </Card>
            </Col>
          </Row>

          {/* ── Alert for over-budget items ──────────────────────────── */}
          {overBudgetEntries.length > 0 && (
            <Alert
              type="error"
              showIcon
              icon={<WarningOutlined />}
              message={`${overBudgetEntries.length} categorii depășesc bugetul alocat`}
              description={
                <Space direction="vertical" size={2}>
                  {overBudgetEntries.slice(0, 5).map((e) => (
                    <Text key={e.id} type="danger">
                      {e.cost_center} / {e.category} ({MONTHS[e.period_month - 1]}): depășire{" "}
                      {(e.actual_amount - e.budgeted_amount).toLocaleString("ro-RO", {
                        minimumFractionDigits: 2,
                      })}{" "}
                      RON
                    </Text>
                  ))}
                  {overBudgetEntries.length > 5 && (
                    <Text type="secondary">...și alte {overBudgetEntries.length - 5} categorii</Text>
                  )}
                </Space>
              }
              style={{ marginBottom: 24 }}
            />
          )}

          {/* ── Cost Analysis per Centru Cost (F116) ─────────────────── */}
          <Card
            title="Analiză costuri per centru de cost (F116)"
            style={{ marginBottom: 24 }}
            extra={<Tag color="blue">{costAnalysis.length} centre</Tag>}
          >
            <Table<CostAnalysis>
              rowKey="cost_center"
              columns={costColumns}
              dataSource={costAnalysis}
              pagination={false}
              size="small"
              locale={{ emptyText: "Nu există date de analiză pentru anul selectat" }}
              expandable={{
                expandedRowRender: (record) => (
                  <Table<BudgetEntry>
                    rowKey="id"
                    columns={[
                      { title: "Categorie", dataIndex: "category", key: "cat", width: 140 },
                      { title: "Lună", dataIndex: "period_month", key: "m", width: 80, render: (m: number) => MONTHS[m - 1] },
                      { title: "Bugetat", dataIndex: "budgeted_amount", key: "b", width: 120, align: "right", render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) },
                      { title: "Realizat", dataIndex: "actual_amount", key: "a", width: 120, align: "right", render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) },
                      {
                        title: "Varianță", dataIndex: "variance", key: "v", width: 120, align: "right",
                        render: (v: number) => <Text type={v >= 0 ? "success" : "danger"}>{v >= 0 ? "+" : ""}{v.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}</Text>,
                      },
                    ]}
                    dataSource={record.entries ?? []}
                    pagination={false}
                    size="small"
                  />
                ),
              }}
            />
          </Card>

          <Divider />

          {/* ── Budget Entries Detail (F115) ──────────────────────────── */}
          <Card
            title="Detaliu bugete (F115)"
            extra={<Tag>{budgets.length} intrări</Tag>}
          >
            <Table<BudgetEntry>
              rowKey="id"
              columns={budgetColumns}
              dataSource={budgets}
              pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (t) => `Total: ${t}` }}
              size="small"
              locale={{ emptyText: "Nu există bugete pentru anul selectat" }}
            />
          </Card>
        </>
      )}

      {/* ── Create/Edit Budget Modal ─────────────────────────────────── */}
      <Modal
        title={editEntry ? "Editare buget" : "Buget nou"}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSave}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText={editEntry ? "Salvează" : "Creează"}
        cancelText="Anulare"
        width={520}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="cost_center"
                label="Centru cost"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <Input placeholder="ex: Personal, Echipamente" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="category"
                label="Categorie"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <Input placeholder="ex: Salarii, Mentenanță" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={2} placeholder="Detalii opționale..." />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="period_month"
                label="Lună"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <Select
                  placeholder="Lună"
                  options={MONTHS.map((m, i) => ({ value: i + 1, label: m }))}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="period_year"
                label="An"
                rules={[{ required: true, message: "Obligatoriu" }]}
              >
                <InputNumber min={2020} max={2030} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="currency" label="Monedă">
                <Select
                  options={[
                    { value: "RON", label: "RON" },
                    { value: "EUR", label: "EUR" },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="budgeted_amount" label="Sumă bugetată">
                <InputNumber
                  min={0}
                  style={{ width: "100%" }}
                  precision={2}
                  placeholder="0.00"
                  formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="actual_amount" label="Sumă realizată">
                <InputNumber
                  min={0}
                  style={{ width: "100%" }}
                  precision={2}
                  placeholder="0.00"
                  formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </>
  );
}
