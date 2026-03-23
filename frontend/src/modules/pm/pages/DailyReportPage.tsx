/**
 * Raport Zilnic de Șantier (RZS) — F077
 * Activități, personal, echipamente, materiale primite, meteo, observații.
 *
 * List view + create/edit modal with dynamic sub-tables for
 * personnel, equipment, and material deliveries.
 */
import { useState } from "react";
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
  DatePicker,
  Select,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Descriptions,
  Popconfirm,
  Tooltip,
  Divider,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CloudOutlined,
  TeamOutlined,
  ToolOutlined,
  TruckOutlined,
  EyeOutlined,
  MinusCircleOutlined,
  CalendarOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type {
  DailyReport,
  PersonnelEntry,
  EquipmentEntry,
  MaterialDelivery,
} from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

const WEATHER_OPTIONS = [
  { value: "sunny", label: "Însorit ☀️" },
  { value: "cloudy", label: "Înnorat ☁️" },
  { value: "rain", label: "Ploaie 🌧️" },
  { value: "snow", label: "Ninsoare ❄️" },
  { value: "wind", label: "Vânt puternic 💨" },
  { value: "storm", label: "Furtună ⛈️" },
  { value: "fog", label: "Ceață 🌫️" },
];

export default function DailyReportPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [viewReport, setViewReport] = useState<DailyReport | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: reportsRes, isLoading } = useQuery({
    queryKey: ["daily-reports", projectId],
    queryFn: () => pmService.listDailyReports(projectId!),
    enabled: !!projectId,
  });

  const reports = reportsRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createDailyReport(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-reports", projectId] });
      message.success("Raport zilnic creat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateDailyReport(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-reports", projectId] });
      message.success("Raport actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteDailyReport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-reports", projectId] });
      message.success("Raport șters");
    },
  });

  // ─── Modal helpers ──────────────────────────────────────────────────────────

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({
      report_date: dayjs(),
      personnel_present: [{ name: "", role: "", hours: 8 }],
    });
    setIsModalOpen(true);
  };

  const openEdit = (report: DailyReport) => {
    setEditingId(report.id);
    form.setFieldsValue({
      ...report,
      report_date: dayjs(report.report_date),
      personnel_present: report.personnel_present?.length
        ? report.personnel_present
        : [{ name: "", role: "", hours: 8 }],
      equipment_used: report.equipment_used?.length
        ? report.equipment_used
        : [],
      materials_received: report.materials_received?.length
        ? report.materials_received
        : [],
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
      report_date: (values.report_date as dayjs.Dayjs).toISOString(),
      // Clean empty sub-entries
      personnel_present: (values.personnel_present as PersonnelEntry[] | undefined)?.filter(
        (p) => p.name
      ),
      equipment_used: (values.equipment_used as EquipmentEntry[] | undefined)?.filter(
        (e) => e.name
      ),
      materials_received: (values.materials_received as MaterialDelivery[] | undefined)?.filter(
        (m) => m.material_name
      ),
    };
    if (editingId) {
      updateMut.mutate({ id: editingId, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  // ─── List columns ──────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Data",
      dataIndex: "report_date",
      key: "date",
      width: 120,
      render: (d: string) => (
        <Text strong>{dayjs(d).format("DD.MM.YYYY")}</Text>
      ),
      sorter: (a: DailyReport, b: DailyReport) =>
        dayjs(a.report_date).unix() - dayjs(b.report_date).unix(),
      defaultSortOrder: "descend" as const,
    },
    {
      title: "Meteo",
      key: "weather",
      width: 140,
      render: (_: unknown, rec: DailyReport) => {
        const w = WEATHER_OPTIONS.find((o) => o.value === rec.weather);
        const temp =
          rec.temperature_min != null && rec.temperature_max != null
            ? `${rec.temperature_min}°–${rec.temperature_max}°C`
            : "";
        return (
          <Space>
            <Tag icon={<CloudOutlined />}>{w?.label ?? rec.weather ?? "—"}</Tag>
            {temp && <Text type="secondary">{temp}</Text>}
          </Space>
        );
      },
    },
    {
      title: "Personal",
      key: "personnel",
      width: 100,
      align: "center" as const,
      render: (_: unknown, rec: DailyReport) => {
        const count = Array.isArray(rec.personnel_present)
          ? rec.personnel_present.length
          : 0;
        return (
          <Tag icon={<TeamOutlined />} color={count > 0 ? "blue" : "default"}>
            {count}
          </Tag>
        );
      },
    },
    {
      title: "Echipamente",
      key: "equipment",
      width: 110,
      align: "center" as const,
      render: (_: unknown, rec: DailyReport) => {
        const count = Array.isArray(rec.equipment_used)
          ? rec.equipment_used.length
          : 0;
        return (
          <Tag icon={<ToolOutlined />} color={count > 0 ? "green" : "default"}>
            {count}
          </Tag>
        );
      },
    },
    {
      title: "Livrări",
      key: "deliveries",
      width: 100,
      align: "center" as const,
      render: (_: unknown, rec: DailyReport) => {
        const count = Array.isArray(rec.materials_received)
          ? rec.materials_received.length
          : 0;
        return (
          <Tag icon={<TruckOutlined />} color={count > 0 ? "orange" : "default"}>
            {count}
          </Tag>
        );
      },
    },
    {
      title: "Activități",
      dataIndex: "activities_summary",
      key: "activities",
      ellipsis: true,
      render: (v?: string) => v ?? <Text type="secondary">—</Text>,
    },
    {
      title: "Probleme",
      dataIndex: "issues",
      key: "issues",
      width: 120,
      render: (v?: string) =>
        v ? (
          <Tag color="red">{v.slice(0, 30)}...</Tag>
        ) : (
          <Tag color="green">Fără</Tag>
        ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 120,
      render: (_: unknown, rec: DailyReport) => (
        <Space size="small">
          <Tooltip title="Vizualizare">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => setViewReport(rec)}
            />
          </Tooltip>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(rec)}
          />
          <Popconfirm
            title="Ștergi acest raport?"
            onConfirm={() => deleteMut.mutate(rec.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const totalPersonnel = reports.reduce(
    (s, r) =>
      s + (Array.isArray(r.personnel_present) ? r.personnel_present.length : 0),
    0
  );
  const issueCount = reports.filter((r) => r.issues).length;

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
          <FileTextOutlined /> Raport Zilnic Șantier (F077)
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Raport nou
        </Button>
      </div>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total rapoarte"
              value={reports.length}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Personal total (intrări)"
              value={totalPersonnel}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Zile cu probleme"
              value={issueCount}
              valueStyle={issueCount > 0 ? { color: "#ff4d4f" } : undefined}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Ultimul raport"
              value={
                reports.length > 0
                  ? dayjs(reports[0]?.report_date).format("DD.MM.YYYY")
                  : "—"
              }
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          size="middle"
        />
      </Card>

      {/* View detail modal */}
      <Modal
        title={
          viewReport
            ? `Raport zilnic — ${dayjs(viewReport.report_date).format("DD.MM.YYYY")}`
            : ""
        }
        open={!!viewReport}
        onCancel={() => setViewReport(null)}
        footer={
          <Button onClick={() => setViewReport(null)}>Închide</Button>
        }
        width={700}
      >
        {viewReport && (
          <>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Data">
                {dayjs(viewReport.report_date).format("DD.MM.YYYY")}
              </Descriptions.Item>
              <Descriptions.Item label="Meteo">
                {WEATHER_OPTIONS.find((o) => o.value === viewReport.weather)?.label ??
                  viewReport.weather ??
                  "—"}
                {viewReport.temperature_min != null &&
                  ` | ${viewReport.temperature_min}°–${viewReport.temperature_max}°C`}
              </Descriptions.Item>
            </Descriptions>

            <Divider orientation="left">Activități</Divider>
            <Text>{viewReport.activities_summary ?? "—"}</Text>

            {Array.isArray(viewReport.personnel_present) &&
              viewReport.personnel_present.length > 0 && (
                <>
                  <Divider orientation="left">Personal prezent</Divider>
                  <Table
                    size="small"
                    pagination={false}
                    dataSource={viewReport.personnel_present}
                    rowKey={(_, i) => String(i)}
                    columns={[
                      { title: "Nume", dataIndex: "name", key: "name" },
                      { title: "Rol", dataIndex: "role", key: "role" },
                      {
                        title: "Ore",
                        dataIndex: "hours",
                        key: "hours",
                        width: 80,
                      },
                    ]}
                  />
                </>
              )}

            {Array.isArray(viewReport.equipment_used) &&
              viewReport.equipment_used.length > 0 && (
                <>
                  <Divider orientation="left">Echipamente</Divider>
                  <Table
                    size="small"
                    pagination={false}
                    dataSource={viewReport.equipment_used}
                    rowKey={(_, i) => String(i)}
                    columns={[
                      { title: "Echipament", dataIndex: "name", key: "name" },
                      { title: "Ore", dataIndex: "hours", key: "hours", width: 80 },
                      { title: "Note", dataIndex: "notes", key: "notes" },
                    ]}
                  />
                </>
              )}

            {Array.isArray(viewReport.materials_received) &&
              viewReport.materials_received.length > 0 && (
                <>
                  <Divider orientation="left">Materiale primite</Divider>
                  <Table
                    size="small"
                    pagination={false}
                    dataSource={viewReport.materials_received}
                    rowKey={(_, i) => String(i)}
                    columns={[
                      { title: "Material", dataIndex: "material_name", key: "mat" },
                      { title: "Cantitate", dataIndex: "quantity", key: "qty", width: 100 },
                      { title: "U.M.", dataIndex: "unit_of_measure", key: "um", width: 80 },
                      { title: "Furnizor", dataIndex: "supplier", key: "sup" },
                      { title: "Aviz", dataIndex: "delivery_note", key: "note" },
                    ]}
                  />
                </>
              )}

            {viewReport.observations && (
              <>
                <Divider orientation="left">Observații</Divider>
                <Text>{viewReport.observations}</Text>
              </>
            )}

            {viewReport.issues && (
              <>
                <Divider orientation="left">Probleme</Divider>
                <Text type="danger">{viewReport.issues}</Text>
              </>
            )}
          </>
        )}
      </Modal>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare raport zilnic" : "Raport zilnic nou"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={750}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="report_date"
                label="Data"
                rules={[{ required: true }]}
              >
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="weather" label="Meteo">
                <Select
                  options={WEATHER_OPTIONS}
                  placeholder="Selectează"
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="temperature_min" label="Temp. min (°C)">
                <InputNumber style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="temperature_max" label="Temp. max (°C)">
                <InputNumber style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="activities_summary" label="Sumar activități">
            <Input.TextArea rows={3} placeholder="Descrierea activităților zilei..." />
          </Form.Item>

          {/* Personnel dynamic list */}
          <Divider orientation="left">Personal prezent</Divider>
          <Form.List name="personnel_present">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Row key={key} gutter={8} style={{ marginBottom: 8 }}>
                    <Col span={9}>
                      <Form.Item {...rest} name={[name, "name"]} noStyle>
                        <Input placeholder="Nume" />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item {...rest} name={[name, "role"]} noStyle>
                        <Input placeholder="Rol / Funcția" />
                      </Form.Item>
                    </Col>
                    <Col span={5}>
                      <Form.Item {...rest} name={[name, "hours"]} noStyle>
                        <InputNumber
                          placeholder="Ore"
                          min={0}
                          max={24}
                          step={0.5}
                          style={{ width: "100%" }}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={2}>
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
                  onClick={() => add({ name: "", role: "", hours: 8 })}
                  icon={<PlusOutlined />}
                  block
                >
                  Adaugă personal
                </Button>
              </>
            )}
          </Form.List>

          {/* Equipment dynamic list */}
          <Divider orientation="left">Echipamente utilizate</Divider>
          <Form.List name="equipment_used">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Row key={key} gutter={8} style={{ marginBottom: 8 }}>
                    <Col span={10}>
                      <Form.Item {...rest} name={[name, "name"]} noStyle>
                        <Input placeholder="Echipament" />
                      </Form.Item>
                    </Col>
                    <Col span={5}>
                      <Form.Item {...rest} name={[name, "hours"]} noStyle>
                        <InputNumber
                          placeholder="Ore"
                          min={0}
                          max={24}
                          style={{ width: "100%" }}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={7}>
                      <Form.Item {...rest} name={[name, "notes"]} noStyle>
                        <Input placeholder="Note" />
                      </Form.Item>
                    </Col>
                    <Col span={2}>
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
                  onClick={() => add({ name: "", hours: 0 })}
                  icon={<PlusOutlined />}
                  block
                >
                  Adaugă echipament
                </Button>
              </>
            )}
          </Form.List>

          {/* Material deliveries dynamic list */}
          <Divider orientation="left">Materiale primite (livrări)</Divider>
          <Form.List name="materials_received">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Row key={key} gutter={8} style={{ marginBottom: 8 }}>
                    <Col span={7}>
                      <Form.Item {...rest} name={[name, "material_name"]} noStyle>
                        <Input placeholder="Material" />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item {...rest} name={[name, "quantity"]} noStyle>
                        <InputNumber
                          placeholder="Cantitate"
                          min={0}
                          style={{ width: "100%" }}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item {...rest} name={[name, "unit_of_measure"]} noStyle>
                        <Input placeholder="U.M." />
                      </Form.Item>
                    </Col>
                    <Col span={5}>
                      <Form.Item {...rest} name={[name, "supplier"]} noStyle>
                        <Input placeholder="Furnizor" />
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item {...rest} name={[name, "delivery_note"]} noStyle>
                        <Input placeholder="Aviz" />
                      </Form.Item>
                    </Col>
                    <Col span={2}>
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
                    add({ material_name: "", quantity: 0, unit_of_measure: "buc" })
                  }
                  icon={<PlusOutlined />}
                  block
                >
                  Adaugă livrare material
                </Button>
              </>
            )}
          </Form.List>

          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={12}>
              <Form.Item name="observations" label="Observații">
                <Input.TextArea rows={2} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="issues" label="Probleme / Blocaje">
                <Input.TextArea rows={2} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
