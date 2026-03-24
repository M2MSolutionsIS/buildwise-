/**
 * E-033 — HR — Echipe & Personal
 * F-codes: F107 (CRUD angajați), F108 (Planificare HR), F109 (Concedii), F110 (Competențe), F111 (Salarizare)
 * CRUD angajați cu competențe, disponibilitate, filtre pe departament/status
 */
import { useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Typography,
  Input,
  Select,
  Button,
  Table,
  Tag,
  Space,
  Row,
  Col,
  Card,
  App,
  Popconfirm,
  Tooltip,
  Modal,
  Form,
  DatePicker,
  InputNumber,
  Drawer,
  Descriptions,
  Tabs,
  List,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rmService, type EmployeeFilters } from "../services/rmService";
import type { Employee, EmployeeCreate } from "../types";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";

const STATUS_COLORS: Record<string, string> = {
  active: "green",
  on_leave: "orange",
  terminated: "red",
  probation: "blue",
};

const CONTRACT_LABELS: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  freelance: "Freelancer",
};

export default function EmployeesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  const filters: EmployeeFilters = useMemo(
    () => ({
      page: Number(searchParams.get("page")) || 1,
      per_page: Number(searchParams.get("per_page")) || 20,
      search: searchParams.get("search") || undefined,
      department: searchParams.get("department") || undefined,
      status: searchParams.get("status") || undefined,
    }),
    [searchParams]
  );

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["rm-employees", filters],
    queryFn: () => rmService.listEmployees(filters),
  });

  const createMutation = useMutation({
    mutationFn: (payload: EmployeeCreate) => rmService.createEmployee(payload),
    onSuccess: () => {
      message.success("Angajat creat.");
      queryClient.invalidateQueries({ queryKey: ["rm-employees"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la creare."),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<EmployeeCreate> }) =>
      rmService.updateEmployee(id, payload),
    onSuccess: () => {
      message.success("Angajat actualizat.");
      queryClient.invalidateQueries({ queryKey: ["rm-employees"] });
      setModalOpen(false);
      setEditingId(null);
      form.resetFields();
    },
    onError: () => message.error("Eroare la actualizare."),
  });

  const deleteMutation = useMutation({
    mutationFn: rmService.deleteEmployee,
    onSuccess: () => {
      message.success("Angajat șters.");
      queryClient.invalidateQueries({ queryKey: ["rm-employees"] });
    },
    onError: () => message.error("Eroare la ștergere."),
  });

  const updateFilter = (key: string, value: string | undefined) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value);
    else params.delete(key);
    params.set("page", "1");
    setSearchParams(params);
  };

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditingId(emp.id);
    form.setFieldsValue({
      ...emp,
      hire_date: emp.hire_date ? dayjs(emp.hire_date) : undefined,
      skills: emp.skills?.join(", "),
      qualifications: emp.qualifications?.join(", "),
      certifications: emp.certifications?.join(", "),
    });
    setModalOpen(true);
  };

  const openDetail = async (emp: Employee) => {
    setSelectedEmployee(emp);
    setDrawerOpen(true);
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    const payload: EmployeeCreate = {
      ...values,
      hire_date: values.hire_date?.toISOString(),
      skills: values.skills ? values.skills.split(",").map((s: string) => s.trim()).filter(Boolean) : undefined,
      qualifications: values.qualifications ? values.qualifications.split(",").map((s: string) => s.trim()).filter(Boolean) : undefined,
      certifications: values.certifications ? values.certifications.split(",").map((s: string) => s.trim()).filter(Boolean) : undefined,
    };
    if (editingId) {
      updateMutation.mutate({ id: editingId, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const columns: ColumnsType<Employee> = [
    {
      title: "Nume",
      key: "name",
      render: (_, rec) => (
        <a onClick={() => openDetail(rec)}>
          {rec.first_name} {rec.last_name}
        </a>
      ),
      sorter: (a, b) => a.last_name.localeCompare(b.last_name),
    },
    {
      title: "Poziție",
      dataIndex: "position",
      key: "position",
      width: 150,
      render: (v: string) => v || "—",
    },
    {
      title: "Departament",
      dataIndex: "department",
      key: "department",
      width: 140,
      render: (v: string) => v || "—",
    },
    {
      title: "Contract",
      dataIndex: "contract_type",
      key: "contract_type",
      width: 110,
      render: (v: string) => CONTRACT_LABELS[v] || v,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (s: string) => (
        <Tag color={STATUS_COLORS[s] || "default"}>
          {s?.charAt(0).toUpperCase() + s?.slice(1)}
        </Tag>
      ),
    },
    {
      title: "Rată orară",
      dataIndex: "hourly_rate",
      key: "hourly_rate",
      width: 110,
      render: (v: number, rec) => (v ? `${v} ${rec.currency}` : "—"),
    },
    {
      title: "Email",
      dataIndex: "email",
      key: "email",
      width: 180,
      ellipsis: true,
      render: (v: string) => v || "—",
    },
    {
      title: "",
      key: "actions",
      width: 110,
      render: (_, rec) => (
        <Space size="small">
          <Tooltip title="Detalii">
            <Button type="text" size="small" icon={<EyeOutlined />} onClick={() => openDetail(rec)} />
          </Tooltip>
          <Tooltip title="Editează">
            <Button type="text" size="small" icon={<EditOutlined />} onClick={() => openEdit(rec)} />
          </Tooltip>
          <Popconfirm
            title="Sigur vrei să ștergi?"
            onConfirm={() => deleteMutation.mutate(rec.id)}
            okText="Da"
            cancelText="Nu"
          >
            <Tooltip title="Șterge">
              <Button type="text" danger size="small" icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const employees = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          <UserOutlined style={{ marginRight: 8 }} />
          HR — Echipe & Personal
        </Typography.Title>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </Tooltip>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Angajat nou
          </Button>
        </Space>
      </Row>

      {/* Filters */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input
              placeholder="Caută nume, email..."
              prefix={<SearchOutlined />}
              allowClear
              value={filters.search || ""}
              onChange={(e) => updateFilter("search", e.target.value || undefined)}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Departament"
              allowClear
              style={{ width: "100%" }}
              value={filters.department}
              onChange={(v) => updateFilter("department", v)}
              options={[
                { label: "Management", value: "management" },
                { label: "Tehnic", value: "tehnic" },
                { label: "Vânzări", value: "vanzari" },
                { label: "Producție", value: "productie" },
                { label: "Administrativ", value: "administrativ" },
              ]}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: "100%" }}
              value={filters.status}
              onChange={(v) => updateFilter("status", v)}
              options={[
                { label: "Activ", value: "active" },
                { label: "În concediu", value: "on_leave" },
                { label: "Probație", value: "probation" },
                { label: "Încheiat", value: "terminated" },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {/* Table */}
      <Table<Employee>
        rowKey="id"
        columns={columns}
        dataSource={employees}
        loading={isLoading}
        pagination={{
          current: filters.page,
          pageSize: filters.per_page,
          total,
          showSizeChanger: true,
          showTotal: (t) => `Total: ${t} angajați`,
          onChange: (page, pageSize) => {
            const params = new URLSearchParams(searchParams);
            params.set("page", String(page));
            params.set("per_page", String(pageSize));
            setSearchParams(params);
          },
        }}
        scroll={{ x: 1000 }}
        locale={{ emptyText: "Niciun angajat încă" }}
      />

      {/* Create/Edit Modal — E-033.M1 */}
      <Modal
        title={editingId ? "Editează angajat" : "Angajat nou"}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditingId(null); form.resetFields(); }}
        onOk={handleSubmit}
        okText={editingId ? "Salvează" : "Creează"}
        cancelText="Anulează"
        width={700}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="first_name" label="Prenume" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input prefix={<UserOutlined />} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="last_name" label="Nume" rules={[{ required: true, message: "Obligatoriu" }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="email" label="Email">
                <Input prefix={<MailOutlined />} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phone" label="Telefon">
                <Input prefix={<PhoneOutlined />} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="position" label="Poziție">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="department" label="Departament">
                <Select
                  allowClear
                  options={[
                    { label: "Management", value: "management" },
                    { label: "Tehnic", value: "tehnic" },
                    { label: "Vânzări", value: "vanzari" },
                    { label: "Producție", value: "productie" },
                    { label: "Administrativ", value: "administrativ" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="contract_type" label="Tip contract" initialValue="full_time">
                <Select
                  options={[
                    { label: "Full-time", value: "full_time" },
                    { label: "Part-time", value: "part_time" },
                    { label: "Contract", value: "contract" },
                    { label: "Freelancer", value: "freelance" },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="hire_date" label="Data angajării">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="hourly_rate" label="Rată orară">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON/h" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="employee_number" label="Nr. angajat">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="gross_salary" label="Salariu brut (F111)">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="net_salary" label="Salariu net">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="cost_center" label="Centru de cost">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="skills" label="Competențe (F110)" extra="Separate prin virgulă">
            <Input placeholder="Ex: Sudură, Electrician, AutoCAD" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="qualifications" label="Calificări" extra="Separate prin virgulă">
                <Input placeholder="Ex: Inginer, Maistru" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="certifications" label="Certificări" extra="Separate prin virgulă">
                <Input placeholder="Ex: ISO 9001, ISCIR" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="is_external" label="Extern" valuePropName="checked" initialValue={false}>
                <Select
                  options={[
                    { label: "Nu", value: false },
                    { label: "Da — subcontractor", value: true },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="external_company" label="Firma externă">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="external_daily_rate" label="Rată zilnică externă">
                <InputNumber style={{ width: "100%" }} min={0} addonAfter="RON/zi" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={selectedEmployee ? `${selectedEmployee.first_name} ${selectedEmployee.last_name}` : ""}
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); setSelectedEmployee(null); }}
        width={520}
      >
        {selectedEmployee && (
          <Tabs
            items={[
              {
                key: "info",
                label: "Date generale",
                children: (
                  <Descriptions column={1} bordered size="small">
                    <Descriptions.Item label="Poziție">{selectedEmployee.position || "—"}</Descriptions.Item>
                    <Descriptions.Item label="Departament">{selectedEmployee.department || "—"}</Descriptions.Item>
                    <Descriptions.Item label="Email">{selectedEmployee.email || "—"}</Descriptions.Item>
                    <Descriptions.Item label="Telefon">{selectedEmployee.phone || "—"}</Descriptions.Item>
                    <Descriptions.Item label="Nr. angajat">{selectedEmployee.employee_number || "—"}</Descriptions.Item>
                    <Descriptions.Item label="Tip contract">
                      {CONTRACT_LABELS[selectedEmployee.contract_type] || selectedEmployee.contract_type}
                    </Descriptions.Item>
                    <Descriptions.Item label="Status">
                      <Tag color={STATUS_COLORS[selectedEmployee.status] || "default"}>
                        {selectedEmployee.status}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Data angajării">
                      {selectedEmployee.hire_date ? new Date(selectedEmployee.hire_date).toLocaleDateString("ro-RO") : "—"}
                    </Descriptions.Item>
                    <Descriptions.Item label="Rată orară">
                      {selectedEmployee.hourly_rate ? `${selectedEmployee.hourly_rate} ${selectedEmployee.currency}/h` : "—"}
                    </Descriptions.Item>
                    <Descriptions.Item label="Salariu brut">
                      {selectedEmployee.gross_salary ? `${selectedEmployee.gross_salary} ${selectedEmployee.currency}` : "—"}
                    </Descriptions.Item>
                    {selectedEmployee.is_external && (
                      <>
                        <Descriptions.Item label="Firmă externă">{selectedEmployee.external_company || "—"}</Descriptions.Item>
                        <Descriptions.Item label="Rată zilnică">
                          {selectedEmployee.external_daily_rate ? `${selectedEmployee.external_daily_rate} ${selectedEmployee.currency}/zi` : "—"}
                        </Descriptions.Item>
                      </>
                    )}
                  </Descriptions>
                ),
              },
              {
                key: "skills",
                label: "Competențe (F110)",
                children: (
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Typography.Text strong>Competențe</Typography.Text>
                    {selectedEmployee.skills?.length ? (
                      <Space wrap>
                        {selectedEmployee.skills.map((s) => <Tag key={s} color="blue">{s}</Tag>)}
                      </Space>
                    ) : <Typography.Text type="secondary">Niciuna</Typography.Text>}

                    <Typography.Text strong style={{ marginTop: 16, display: "block" }}>Calificări</Typography.Text>
                    {selectedEmployee.qualifications?.length ? (
                      <Space wrap>
                        {selectedEmployee.qualifications.map((q) => <Tag key={q} color="green">{q}</Tag>)}
                      </Space>
                    ) : <Typography.Text type="secondary">Niciuna</Typography.Text>}

                    <Typography.Text strong style={{ marginTop: 16, display: "block" }}>Certificări</Typography.Text>
                    {selectedEmployee.certifications?.length ? (
                      <List
                        size="small"
                        dataSource={selectedEmployee.certifications}
                        renderItem={(c) => <List.Item>{c}</List.Item>}
                      />
                    ) : <Typography.Text type="secondary">Niciuna</Typography.Text>}
                  </Space>
                ),
              },
            ]}
          />
        )}
      </Drawer>
    </>
  );
}
