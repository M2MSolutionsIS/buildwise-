/**
 * E-041 / F142: Reports Builder — Drag & drop report builder
 * Sidebar with fields, canvas zones (GROUP BY / VALUE / FILTERS), preview, export.
 * Specific P3 only.
 */
import { useState, useMemo } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Table,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Tabs,
  Divider,
  Popconfirm,
  message,
  Spin,
  Empty,
  List,
  Tooltip,
  Badge,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  FilterOutlined,
  GroupOutlined,
  NumberOutlined,
  SaveOutlined,
  BarChartOutlined,
  TableOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { biService } from "../services/biService";
import type { ReportDefinition, ReportColumn, ReportFilter } from "../../../types";

const { Title, Text } = Typography;
const { TextArea } = Input;

const MODULE_OPTIONS = [
  { label: "CRM", value: "crm" },
  { label: "Pipeline", value: "pipeline" },
  { label: "PM", value: "pm" },
  { label: "RM", value: "rm" },
];

const REPORT_TYPES = [
  { label: "Programare", value: "schedule" },
  { label: "Financiar", value: "financial" },
  { label: "KPI", value: "kpi" },
  { label: "Custom", value: "custom" },
];

const AGGREGATE_OPTIONS = [
  { label: "Niciuna", value: "" },
  { label: "Sumă", value: "sum" },
  { label: "Medie", value: "avg" },
  { label: "Numărare", value: "count" },
  { label: "Minim", value: "min" },
  { label: "Maxim", value: "max" },
];

const FIELD_CATALOG: Record<string, { label: string; fields: { field: string; label: string; type: "text" | "number" | "date" | "currency" }[] }> = {
  crm: {
    label: "CRM",
    fields: [
      { field: "contact_name", label: "Nume Contact", type: "text" },
      { field: "contact_type", label: "Tip Contact", type: "text" },
      { field: "company", label: "Companie", type: "text" },
      { field: "email", label: "Email", type: "text" },
      { field: "created_at", label: "Data Creare", type: "date" },
    ],
  },
  pipeline: {
    label: "Pipeline",
    fields: [
      { field: "opportunity_name", label: "Nume Oportunitate", type: "text" },
      { field: "stage", label: "Etapă", type: "text" },
      { field: "estimated_value", label: "Valoare Estimată", type: "currency" },
      { field: "probability", label: "Probabilitate (%)", type: "number" },
      { field: "expected_close", label: "Data Închidere", type: "date" },
      { field: "won_lost", label: "Câștigat/Pierdut", type: "text" },
    ],
  },
  pm: {
    label: "PM",
    fields: [
      { field: "project_name", label: "Nume Proiect", type: "text" },
      { field: "status", label: "Status", type: "text" },
      { field: "progress", label: "Progres (%)", type: "number" },
      { field: "budget", label: "Buget", type: "currency" },
      { field: "actual_cost", label: "Cost Real", type: "currency" },
      { field: "start_date", label: "Data Start", type: "date" },
      { field: "end_date", label: "Data Finalizare", type: "date" },
    ],
  },
  rm: {
    label: "RM",
    fields: [
      { field: "employee_name", label: "Angajat", type: "text" },
      { field: "department", label: "Departament", type: "text" },
      { field: "role", label: "Rol", type: "text" },
      { field: "allocation_hours", label: "Ore Alocate", type: "number" },
      { field: "equipment_name", label: "Echipament", type: "text" },
      { field: "material_qty", label: "Cantitate Material", type: "number" },
    ],
  },
};

function FieldSidebar({
  module,
  onAddColumn,
  onAddGroupBy,
  onAddFilter,
}: {
  module: string;
  onAddColumn: (f: { field: string; label: string; type: "text" | "number" | "date" | "currency" }) => void;
  onAddGroupBy: (field: string) => void;
  onAddFilter: (field: string) => void;
}) {
  const catalog = FIELD_CATALOG[module];
  if (!catalog) return <Empty description="Selectează un modul" />;

  return (
    <Card title={`Câmpuri — ${catalog.label}`} size="small" style={{ height: "100%" }}>
      <Text type="secondary" style={{ fontSize: 11, display: "block", marginBottom: 8 }}>
        Click pe butoane pentru a adăuga câmpuri
      </Text>
      <List
        dataSource={catalog.fields}
        size="small"
        renderItem={(f) => (
          <List.Item style={{ padding: "4px 0" }}>
            <Space size={4} style={{ width: "100%" }} wrap>
              <Text style={{ flex: 1, minWidth: 80 }}>{f.label}</Text>
              <Tooltip title="Adaugă ca valoare">
                <Button size="small" icon={<NumberOutlined />} onClick={() => onAddColumn(f)} />
              </Tooltip>
              <Tooltip title="Adaugă la GROUP BY">
                <Button size="small" icon={<GroupOutlined />} onClick={() => onAddGroupBy(f.field)} />
              </Tooltip>
              <Tooltip title="Adaugă filtru">
                <Button size="small" icon={<FilterOutlined />} onClick={() => onAddFilter(f.field)} />
              </Tooltip>
            </Space>
          </List.Item>
        )}
      />
    </Card>
  );
}

export default function ReportsBuilderPage() {
  const queryClient = useQueryClient();
  const [builderOpen, setBuilderOpen] = useState(false);
  const [editingReport, setEditingReport] = useState<ReportDefinition | null>(null);
  const [form] = Form.useForm();
  const [columns, setColumns] = useState<ReportColumn[]>([]);
  const [groupBy, setGroupBy] = useState<string[]>([]);
  const [filters, setFilters] = useState<ReportFilter[]>([]);
  const [selectedModule, setSelectedModule] = useState("crm");
  const [moduleFilter, setModuleFilter] = useState<string | undefined>(undefined);
  const [previewMode, setPreviewMode] = useState(false);

  const { data: reportsData, isLoading } = useQuery({
    queryKey: ["reports", moduleFilter],
    queryFn: () => biService.listReports({ module: moduleFilter, per_page: 100 }),
  });

  const reports: ReportDefinition[] = reportsData?.data ?? [];

  const createMutation = useMutation({
    mutationFn: (payload: Partial<ReportDefinition>) => biService.createReport(payload),
    onSuccess: () => {
      message.success("Raport creat cu succes");
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      closeBuilder();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ReportDefinition> }) =>
      biService.updateReport(id, payload),
    onSuccess: () => {
      message.success("Raport actualizat");
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      closeBuilder();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  function openCreate() {
    setEditingReport(null);
    form.resetFields();
    setColumns([]);
    setGroupBy([]);
    setFilters([]);
    setSelectedModule("crm");
    setPreviewMode(false);
    setBuilderOpen(true);
  }

  function openEdit(report: ReportDefinition) {
    setEditingReport(report);
    form.setFieldsValue({
      name: report.name,
      description: report.description,
      report_type: report.report_type,
      module: report.module,
      is_scheduled: report.is_scheduled,
      schedule_cron: report.schedule_cron,
    });
    setColumns(report.columns_config ?? []);
    setGroupBy((report.grouping_config as { fields?: string[] })?.fields ?? []);
    setFilters(report.filters_config ?? []);
    setSelectedModule(report.module);
    setPreviewMode(false);
    setBuilderOpen(true);
  }

  function closeBuilder() {
    setBuilderOpen(false);
    setEditingReport(null);
  }

  async function handleSave() {
    const values = await form.validateFields();
    const payload: Partial<ReportDefinition> = {
      ...values,
      columns_config: columns,
      filters_config: filters,
      grouping_config: { fields: groupBy },
    };

    if (editingReport) {
      updateMutation.mutate({ id: editingReport.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  }

  function addColumn(f: { field: string; label: string; type: "text" | "number" | "date" | "currency" }) {
    if (columns.find((c) => c.field === f.field)) return;
    setColumns((prev) => [...prev, { field: f.field, label: f.label, type: f.type }]);
  }

  function removeColumn(field: string) {
    setColumns((prev) => prev.filter((c) => c.field !== field));
  }

  function updateColumnAggregate(field: string, aggregate: string) {
    setColumns((prev) =>
      prev.map((c) =>
        c.field === field
          ? { ...c, aggregate: (aggregate || undefined) as ReportColumn["aggregate"] }
          : c
      )
    );
  }

  function addGroupBy(field: string) {
    if (groupBy.includes(field)) return;
    setGroupBy((prev) => [...prev, field]);
  }

  function removeGroupBy(field: string) {
    setGroupBy((prev) => prev.filter((f) => f !== field));
  }

  function addFilter(field: string) {
    if (filters.find((f) => f.field === field)) return;
    setFilters((prev) => [...prev, { field, operator: "equals" as const, value: "" }]);
  }

  function removeFilter(field: string) {
    setFilters((prev) => prev.filter((f) => f.field !== field));
  }

  function updateFilter(field: string, key: "operator" | "value", val: unknown) {
    setFilters((prev) => prev.map((f) => (f.field === field ? { ...f, [key]: val } : f)));
  }

  // Preview: generate a mock table based on columns config
  const previewColumns = useMemo(
    () =>
      columns.map((c) => ({
        title: `${c.label}${c.aggregate ? ` (${c.aggregate})` : ""}`,
        dataIndex: c.field,
        key: c.field,
      })),
    [columns]
  );

  const tableColumns = [
    {
      title: "Nume",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: ReportDefinition) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          {record.description && <Text type="secondary" style={{ fontSize: 11 }}>{record.description}</Text>}
        </Space>
      ),
    },
    {
      title: "Tip",
      dataIndex: "report_type",
      key: "report_type",
      width: 100,
      render: (t: string) => <Tag>{t}</Tag>,
    },
    {
      title: "Modul",
      dataIndex: "module",
      key: "module",
      width: 100,
      render: (mod: string) => (
        <Tag color={mod === "pm" ? "green" : mod === "crm" ? "blue" : mod === "pipeline" ? "orange" : "purple"}>
          {mod.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Coloane",
      key: "columns",
      width: 80,
      render: (_: unknown, record: ReportDefinition) => (
        <Badge count={record.columns_config?.length ?? 0} style={{ backgroundColor: "#1677ff" }} />
      ),
    },
    {
      title: "Programat",
      dataIndex: "is_scheduled",
      key: "is_scheduled",
      width: 90,
      render: (v: boolean) => (v ? <Tag color="blue">Da</Tag> : <Tag>Nu</Tag>),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 120,
      render: (_: unknown, record: ReportDefinition) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Tooltip title="Generează raport">
            <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => message.info("Generare raport — conectare la endpoint în curs")} />
          </Tooltip>
          <Popconfirm title="Ștergi acest raport?" onConfirm={() => message.info("Ștergere raport — endpoint TBD")}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <FileTextOutlined /> Reports Builder (E-041 / F142)
          </Title>
          <Text type="secondary">Constructor de rapoarte cu drag & drop</Text>
        </Col>
        <Col>
          <Space>
            <Select
              placeholder="Filtrare modul"
              allowClear
              value={moduleFilter}
              onChange={setModuleFilter}
              options={MODULE_OPTIONS}
              style={{ width: 150 }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
              Raport Nou
            </Button>
          </Space>
        </Col>
      </Row>

      <Card>
        <Table
          dataSource={reports}
          columns={tableColumns}
          rowKey="id"
          pagination={{ pageSize: 20 }}
          size="small"
          locale={{ emptyText: <Empty description="Niciun raport definit. Creează primul raport." /> }}
        />
      </Card>

      {/* Report Builder Modal */}
      <Modal
        title={editingReport ? "Editare Raport" : "Raport Nou"}
        open={builderOpen}
        onCancel={closeBuilder}
        width={1000}
        footer={[
          <Button key="cancel" onClick={closeBuilder}>Anulează</Button>,
          <Button
            key="preview"
            icon={previewMode ? <TableOutlined /> : <BarChartOutlined />}
            onClick={() => setPreviewMode(!previewMode)}
          >
            {previewMode ? "Editor" : "Previzualizare"}
          </Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            loading={createMutation.isPending || updateMutation.isPending}
            onClick={handleSave}
          >
            Salvează
          </Button>,
        ]}
      >
        {previewMode ? (
          <div>
            <Title level={5}>Previzualizare Raport</Title>
            {columns.length === 0 ? (
              <Empty description="Adaugă coloane în editor" />
            ) : (
              <Table
                dataSource={[]}
                columns={previewColumns}
                size="small"
                pagination={false}
                locale={{ emptyText: "Datele vor fi generate la execuție" }}
              />
            )}
            {groupBy.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text type="secondary">GROUP BY: </Text>
                {groupBy.map((g) => <Tag key={g}>{g}</Tag>)}
              </div>
            )}
            {filters.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">FILTRE: </Text>
                {filters.map((f) => (
                  <Tag key={f.field}>{f.field} {f.operator} {String(f.value)}</Tag>
                ))}
              </div>
            )}
            <Divider />
            <Space>
              <Button icon={<DownloadOutlined />} onClick={() => message.info("Export PDF — conectare la endpoint")}>
                Export PDF
              </Button>
              <Button icon={<DownloadOutlined />} onClick={() => message.info("Export Excel — conectare la endpoint")}>
                Export Excel
              </Button>
            </Space>
          </div>
        ) : (
          <Tabs
            items={[
              {
                key: "general",
                label: "General",
                children: (
                  <Form form={form} layout="vertical" initialValues={{ report_type: "custom", module: "crm", is_scheduled: false }}>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item name="name" label="Nume Raport" rules={[{ required: true, message: "Obligatoriu" }]}>
                          <Input placeholder="ex: Raport Vânzări Q1" />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item name="report_type" label="Tip" rules={[{ required: true }]}>
                          <Select options={REPORT_TYPES} />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item name="module" label="Modul" rules={[{ required: true }]}>
                          <Select options={MODULE_OPTIONS} onChange={(v) => setSelectedModule(v)} />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Form.Item name="description" label="Descriere">
                      <TextArea rows={2} />
                    </Form.Item>
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item name="is_scheduled" label="Programat" valuePropName="checked">
                          <Switch />
                        </Form.Item>
                      </Col>
                      <Col span={16}>
                        <Form.Item name="schedule_cron" label="Cron (dacă programat)">
                          <Input placeholder="0 8 * * 1 (luni la 08:00)" />
                        </Form.Item>
                      </Col>
                    </Row>
                  </Form>
                ),
              },
              {
                key: "builder",
                label: "Constructor",
                children: (
                  <Row gutter={16}>
                    <Col span={8}>
                      <FieldSidebar
                        module={selectedModule}
                        onAddColumn={addColumn}
                        onAddGroupBy={addGroupBy}
                        onAddFilter={addFilter}
                      />
                    </Col>
                    <Col span={16}>
                      {/* VALUES zone */}
                      <Card
                        title={<><NumberOutlined /> Valori (Coloane)</>}
                        size="small"
                        style={{ marginBottom: 12 }}
                      >
                        {columns.length === 0 ? (
                          <Text type="secondary">Click pe ⊕ din sidebar pentru a adăuga coloane</Text>
                        ) : (
                          <Space wrap>
                            {columns.map((c) => (
                              <Tag
                                key={c.field}
                                closable
                                onClose={() => removeColumn(c.field)}
                                style={{ padding: "4px 8px" }}
                              >
                                {c.label}
                                <Select
                                  size="small"
                                  value={c.aggregate ?? ""}
                                  onChange={(v) => updateColumnAggregate(c.field, v)}
                                  options={AGGREGATE_OPTIONS}
                                  style={{ width: 80, marginLeft: 4 }}
                                  bordered={false}
                                />
                              </Tag>
                            ))}
                          </Space>
                        )}
                      </Card>

                      {/* GROUP BY zone */}
                      <Card
                        title={<><GroupOutlined /> Group By</>}
                        size="small"
                        style={{ marginBottom: 12 }}
                      >
                        {groupBy.length === 0 ? (
                          <Text type="secondary">Click pe ⊞ din sidebar</Text>
                        ) : (
                          <Space wrap>
                            {groupBy.map((g) => (
                              <Tag key={g} closable onClose={() => removeGroupBy(g)} color="blue">
                                {g}
                              </Tag>
                            ))}
                          </Space>
                        )}
                      </Card>

                      {/* FILTERS zone */}
                      <Card
                        title={<><FilterOutlined /> Filtre</>}
                        size="small"
                      >
                        {filters.length === 0 ? (
                          <Text type="secondary">Click pe filtru din sidebar</Text>
                        ) : (
                          <Space direction="vertical" style={{ width: "100%" }}>
                            {filters.map((f) => (
                              <Row key={f.field} gutter={8} align="middle">
                                <Col span={6}>
                                  <Tag>{f.field}</Tag>
                                </Col>
                                <Col span={6}>
                                  <Select
                                    size="small"
                                    value={f.operator}
                                    onChange={(v) => updateFilter(f.field, "operator", v)}
                                    style={{ width: "100%" }}
                                    options={[
                                      { label: "=", value: "equals" },
                                      { label: "conține", value: "contains" },
                                      { label: ">", value: "greater_than" },
                                      { label: "<", value: "less_than" },
                                      { label: "între", value: "between" },
                                      { label: "în", value: "in" },
                                    ]}
                                  />
                                </Col>
                                <Col span={9}>
                                  <Input
                                    size="small"
                                    value={String(f.value)}
                                    onChange={(e) => updateFilter(f.field, "value", e.target.value)}
                                    placeholder="Valoare..."
                                  />
                                </Col>
                                <Col span={3}>
                                  <Button size="small" danger icon={<CloseOutlined />} onClick={() => removeFilter(f.field)} />
                                </Col>
                              </Row>
                            ))}
                          </Space>
                        )}
                      </Card>
                    </Col>
                  </Row>
                ),
              },
            ]}
          />
        )}
      </Modal>
    </div>
  );
}
