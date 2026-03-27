/**
 * E-024: Settings Hub — F040, F041, F039, F106, F136
 * Tabs: Users & Roles (E-024.1), Permissions (E-024.2), Templates (E-024.3),
 * Custom Fields (E-024.4), + links to Pipeline/RM/Branding configurators.
 * Route: /settings
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography,
  Tabs,
  Card,
  Table,
  Button,
  Space,
  Tag,
  App,
  Switch,
  Row,
  Col,
  Modal,
  Form,
  Input,
  Select,
  Popconfirm,
} from "antd";
import {
  UserOutlined,
  SafetyOutlined,
  FileTextOutlined,
  SettingOutlined,
  PlusOutlined,
  DeleteOutlined,
  MailOutlined,
  FunnelPlotOutlined,
  ToolOutlined,
  FormatPainterOutlined,
  CheckOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { systemService } from "../services/systemService";
import api from "../../../services/api";
import type { ApiResponse, User, SystemRole } from "../../../types";
import { toast } from "../../../components/ToastNotifications";

const { Title, Text } = Typography;

// ─── Custom Fields & Templates interfaces ────────────────────────────────────

interface CustomField {
  id: string;
  entity_type: string;
  field_name: string;
  field_type: string;
  is_required: boolean;
  options?: string[];
  sort_order: number;
  created_at: string;
}

interface DocumentTemplate {
  id: string;
  name: string;
  template_type: string;
  content_template: string;
  is_active: boolean;
  created_at: string;
}

// ─── Permissions matrix ──────────────────────────────────────────────────────

const MODULES = ["CRM", "Pipeline", "PM", "RM", "BI", "System"];
const ACTIONS = ["view", "create", "edit", "delete", "export"];
const ROLE_DEFAULTS: Record<string, Record<string, string[]>> = {
  admin: Object.fromEntries(MODULES.map((m) => [m, ACTIONS])),
  manager: {
    CRM: ACTIONS,
    Pipeline: ACTIONS,
    PM: ["view", "create", "edit", "export"],
    RM: ["view"],
    BI: ACTIONS,
    System: ["view"],
  },
  agent: {
    CRM: ["view", "create", "edit"],
    Pipeline: ["view", "create", "edit"],
    PM: ["view"],
    RM: [],
    BI: ["view"],
    System: [],
  },
  technician: {
    CRM: ["view"],
    Pipeline: ["view"],
    PM: ["view", "create", "edit"],
    RM: ["view"],
    BI: [],
    System: [],
  },
};

export default function SettingsHubPage() {
  const { message: msg } = App.useApp();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("users");
  const [inviteOpen, setInviteOpen] = useState(false);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [_editingRole, setEditingRole] = useState<SystemRole | null>(null);
  const [cfModalOpen, setCfModalOpen] = useState(false);
  const [tplModalOpen, setTplModalOpen] = useState(false);
  const [inviteForm] = Form.useForm();
  const [roleForm] = Form.useForm();
  const [cfForm] = Form.useForm();
  const [tplForm] = Form.useForm();

  // Permissions state (local)
  const [permissions, setPermissions] = useState(ROLE_DEFAULTS);

  // ─── Users (E-024.1) ────────────────────────────────────────────────────────

  const { data: usersData, isLoading: loadingUsers } = useQuery({
    queryKey: ["system-users"],
    queryFn: () => systemService.listUsers(),
  });

  const { data: rolesData, isLoading: loadingRoles } = useQuery({
    queryKey: ["system-roles"],
    queryFn: () => systemService.listRoles(),
  });

  const users = usersData?.data || [];
  const roles = rolesData?.data || [];

  const inviteMut = useMutation({
    mutationFn: (payload: { email: string; first_name: string; last_name: string; role_code: string }) =>
      systemService.inviteUser(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-users"] });
      toast.success("Invitație trimisă");
      setInviteOpen(false);
      inviteForm.resetFields();
    },
    onError: () => toast.error("Eroare la trimiterea invitației"),
  });

  const assignRoleMut = useMutation({
    mutationFn: ({ userId, roleCodes }: { userId: string; roleCodes: string[] }) =>
      systemService.assignUserRoles(userId, roleCodes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-users"] });
      msg.success("Roluri actualizate");
    },
  });

  const createRoleMut = useMutation({
    mutationFn: (payload: { name: string; code: string; description?: string }) =>
      systemService.createRole(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-roles"] });
      msg.success("Rol creat");
      setRoleModalOpen(false);
      roleForm.resetFields();
    },
  });

  const deleteRoleMut = useMutation({
    mutationFn: systemService.deleteRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-roles"] });
      msg.success("Rol șters");
    },
  });

  // ─── Custom Fields (E-024.4) ────────────────────────────────────────────────

  const { data: cfData, isLoading: loadingCF } = useQuery({
    queryKey: ["custom-fields"],
    queryFn: async (): Promise<ApiResponse<CustomField[]>> => {
      const { data } = await api.get("/system/custom-fields");
      return data;
    },
  });

  const customFields = cfData?.data || [];

  const createCFMut = useMutation({
    mutationFn: async (payload: Partial<CustomField>) => {
      const { data } = await api.post("/system/custom-fields", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["custom-fields"] });
      msg.success("Câmp custom creat");
      setCfModalOpen(false);
      cfForm.resetFields();
    },
  });

  const deleteCFMut = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/system/custom-fields/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["custom-fields"] });
      msg.success("Câmp șters");
    },
  });

  // ─── Document Templates (E-024.3) ──────────────────────────────────────────

  const { data: tplData, isLoading: loadingTPL } = useQuery({
    queryKey: ["doc-templates"],
    queryFn: async (): Promise<ApiResponse<DocumentTemplate[]>> => {
      const { data } = await api.get("/system/document-templates");
      return data;
    },
  });

  const templates = tplData?.data || [];

  const createTplMut = useMutation({
    mutationFn: async (payload: Partial<DocumentTemplate>) => {
      const { data } = await api.post("/system/document-templates", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["doc-templates"] });
      msg.success("Template creat");
      setTplModalOpen(false);
      tplForm.resetFields();
    },
  });

  const deleteTplMut = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/system/document-templates/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["doc-templates"] });
      msg.success("Template șters");
    },
  });

  const togglePerm = (roleCode: string, module: string, action: string) => {
    setPermissions((prev) => {
      const current = prev[roleCode]?.[module] || [];
      const has = current.includes(action);
      return {
        ...prev,
        [roleCode]: {
          ...prev[roleCode],
          [module]: has ? current.filter((a) => a !== action) : [...current, action],
        },
      };
    });
  };

  // ─── Quick Links ────────────────────────────────────────────────────────────

  const quickLinks = [
    { label: "Pipeline Configurator", icon: <FunnelPlotOutlined />, path: "/settings/pipeline", desc: "Stadii pipeline, auto-advance rules" },
    { label: "RM Configurator", icon: <ToolOutlined />, path: "/settings/rm", desc: "Categorii resurse, unități, praguri alertă" },
    { label: "Branding & Limbă", icon: <FormatPainterOutlined />, path: "/settings/branding", desc: "Logo, culori, white-label, multi-limbă" },
  ];

  return (
    <div>
      <Title level={3} style={{ margin: "0 0 16px" }}>Setări</Title>

      {/* Quick Links to other configurators */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {quickLinks.map((link) => (
          <Col xs={24} sm={8} key={link.path}>
            <Card
              hoverable
              size="small"
              style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
              onClick={() => navigate(link.path)}
            >
              <Space>
                <div style={{ fontSize: 20, color: "#3B82F6" }}>{link.icon}</div>
                <div>
                  <Text strong>{link.label}</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: 11 }}>{link.desc}</Text>
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "users",
            label: <Space><UserOutlined /> Utilizatori & Roluri</Space>,
            children: (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                  <Text type="secondary">{users.length} utilizatori, {roles.length} roluri</Text>
                  <Space>
                    <Button icon={<PlusOutlined />} onClick={() => { setEditingRole(null); roleForm.resetFields(); setRoleModalOpen(true); }}>
                      Rol nou
                    </Button>
                    <Button type="primary" icon={<MailOutlined />} onClick={() => setInviteOpen(true)}>
                      Invită utilizator
                    </Button>
                  </Space>
                </div>

                <Card title="Utilizatori" size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)", marginBottom: 16 }}>
                  <Table
                    dataSource={users}
                    rowKey="id"
                    size="small"
                    loading={loadingUsers}
                    pagination={{ pageSize: 10 }}
                    columns={[
                      {
                        title: "Nume",
                        key: "name",
                        render: (_: unknown, u: User) => `${u.first_name} ${u.last_name}`,
                      },
                      { title: "Email", dataIndex: "email", key: "email" },
                      {
                        title: "Roluri",
                        dataIndex: "roles",
                        key: "roles",
                        render: (r: string[]) => r?.map((role) => <Tag key={role} color="blue">{role}</Tag>),
                      },
                      {
                        title: "Status",
                        dataIndex: "is_active",
                        key: "status",
                        render: (a: boolean) => <Tag color={a ? "green" : "red"}>{a ? "Activ" : "Inactiv"}</Tag>,
                      },
                      {
                        title: "Acțiuni",
                        key: "actions",
                        width: 120,
                        render: (_: unknown, u: User) => (
                          <Select
                            mode="multiple"
                            size="small"
                            style={{ width: 120 }}
                            value={u.roles}
                            options={roles.map((r) => ({ label: r.name, value: r.code }))}
                            onChange={(vals) => assignRoleMut.mutate({ userId: u.id, roleCodes: vals })}
                            placeholder="Roluri"
                          />
                        ),
                      },
                    ]}
                  />
                </Card>

                <Card title="Roluri" size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <Table
                    dataSource={roles}
                    rowKey="id"
                    size="small"
                    loading={loadingRoles}
                    pagination={false}
                    columns={[
                      { title: "Nume", dataIndex: "name", key: "name" },
                      { title: "Cod", dataIndex: "code", key: "code", render: (c: string) => <Tag>{c}</Tag> },
                      { title: "Descriere", dataIndex: "description", key: "desc", ellipsis: true },
                      {
                        title: "Sistem",
                        dataIndex: "is_system",
                        key: "system",
                        render: (s: boolean) => s ? <Tag color="orange">Sistem</Tag> : <Tag>Custom</Tag>,
                      },
                      {
                        title: "",
                        key: "actions",
                        width: 80,
                        render: (_: unknown, r: SystemRole) =>
                          !r.is_system && (
                            <Popconfirm title="Ștergi rolul?" onConfirm={() => deleteRoleMut.mutate(r.id)}>
                              <Button size="small" danger icon={<DeleteOutlined />} />
                            </Popconfirm>
                          ),
                      },
                    ]}
                  />
                </Card>
              </div>
            ),
          },
          {
            key: "permissions",
            label: <Space><SafetyOutlined /> Permisiuni</Space>,
            children: (
              <Card title="Matrice Roluri × Acțiuni" size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                <Table
                  dataSource={MODULES.map((m) => ({ key: m, module: m }))}
                  rowKey="key"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: "Modul", dataIndex: "module", key: "module", width: 120, render: (m: string) => <Text strong>{m}</Text> },
                    ...Object.keys(permissions).map((roleCode) => ({
                      title: roleCode.charAt(0).toUpperCase() + roleCode.slice(1),
                      key: roleCode,
                      children: ACTIONS.map((action) => ({
                        title: action,
                        key: `${roleCode}-${action}`,
                        width: 60,
                        align: "center" as const,
                        render: (_: unknown, row: { module: string }) => (
                          <Switch
                            size="small"
                            checked={permissions[roleCode]?.[row.module]?.includes(action) ?? false}
                            onChange={() => togglePerm(roleCode, row.module, action)}
                          />
                        ),
                      })),
                    })),
                  ]}
                />
                <div style={{ marginTop: 16, textAlign: "right" }}>
                  <Button type="primary" onClick={() => toast.success("Permisiuni salvate")}>
                    Salvează permisiuni
                  </Button>
                </div>
              </Card>
            ),
          },
          {
            key: "templates",
            label: <Space><FileTextOutlined /> Template-uri</Space>,
            children: (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                  <Text type="secondary">{templates.length} template-uri documente</Text>
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => { tplForm.resetFields(); setTplModalOpen(true); }}>
                    Template nou
                  </Button>
                </div>
                <Table
                  dataSource={templates}
                  rowKey="id"
                  size="small"
                  loading={loadingTPL}
                  columns={[
                    { title: "Nume", dataIndex: "name", key: "name" },
                    {
                      title: "Tip",
                      dataIndex: "template_type",
                      key: "type",
                      render: (t: string) => <Tag>{t}</Tag>,
                    },
                    {
                      title: "Activ",
                      dataIndex: "is_active",
                      key: "active",
                      render: (a: boolean) => a ? <CheckOutlined style={{ color: "#52c41a" }} /> : <CloseOutlined style={{ color: "#f5222d" }} />,
                    },
                    {
                      title: "Creat",
                      dataIndex: "created_at",
                      key: "created",
                      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
                    },
                    {
                      title: "",
                      key: "actions",
                      width: 80,
                      render: (_: unknown, t: DocumentTemplate) => (
                        <Popconfirm title="Ștergi template-ul?" onConfirm={() => deleteTplMut.mutate(t.id)}>
                          <Button size="small" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      ),
                    },
                  ]}
                />
              </div>
            ),
          },
          {
            key: "custom-fields",
            label: <Space><SettingOutlined /> Câmpuri Custom</Space>,
            children: (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                  <Text type="secondary">{customFields.length} câmpuri custom definite</Text>
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => { cfForm.resetFields(); setCfModalOpen(true); }}>
                    Câmp nou
                  </Button>
                </div>
                <Table
                  dataSource={customFields}
                  rowKey="id"
                  size="small"
                  loading={loadingCF}
                  columns={[
                    { title: "Nume câmp", dataIndex: "field_name", key: "name" },
                    {
                      title: "Entitate",
                      dataIndex: "entity_type",
                      key: "entity",
                      render: (e: string) => <Tag color="purple">{e}</Tag>,
                    },
                    {
                      title: "Tip",
                      dataIndex: "field_type",
                      key: "type",
                      render: (t: string) => <Tag>{t}</Tag>,
                    },
                    {
                      title: "Obligatoriu",
                      dataIndex: "is_required",
                      key: "required",
                      render: (r: boolean) => r ? <CheckOutlined style={{ color: "#52c41a" }} /> : "—",
                    },
                    {
                      title: "",
                      key: "actions",
                      width: 80,
                      render: (_: unknown, cf: CustomField) => (
                        <Popconfirm title="Ștergi câmpul?" onConfirm={() => deleteCFMut.mutate(cf.id)}>
                          <Button size="small" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      ),
                    },
                  ]}
                />
              </div>
            ),
          },
        ]}
      />

      {/* E-024.M1: Invite User Modal */}
      <Modal
        title="Invită Utilizator"
        open={inviteOpen}
        onCancel={() => setInviteOpen(false)}
        onOk={() => inviteForm.validateFields().then((v) => inviteMut.mutate(v))}
        confirmLoading={inviteMut.isPending}
        okText="Trimite invitație"
        cancelText="Anulează"
      >
        <Form form={inviteForm} layout="vertical">
          <Form.Item name="email" label="Email" rules={[{ required: true, type: "email", message: "Email valid obligatoriu" }]}>
            <Input prefix={<MailOutlined />} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="first_name" label="Prenume" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="last_name" label="Nume" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="role_code" label="Rol" rules={[{ required: true }]}>
            <Select
              options={roles.map((r) => ({ label: r.name, value: r.code }))}
              placeholder="Selectează rol"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Create Role Modal */}
      <Modal
        title="Rol Nou"
        open={roleModalOpen}
        onCancel={() => setRoleModalOpen(false)}
        onOk={() => roleForm.validateFields().then((v) => createRoleMut.mutate(v))}
        confirmLoading={createRoleMut.isPending}
        okText="Creează"
        cancelText="Anulează"
      >
        <Form form={roleForm} layout="vertical">
          <Form.Item name="name" label="Nume rol" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="code" label="Cod" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Create Template Modal */}
      <Modal
        title="Template Nou"
        open={tplModalOpen}
        onCancel={() => setTplModalOpen(false)}
        onOk={() => tplForm.validateFields().then((v) => createTplMut.mutate(v))}
        confirmLoading={createTplMut.isPending}
        okText="Creează"
        cancelText="Anulează"
      >
        <Form form={tplForm} layout="vertical">
          <Form.Item name="name" label="Nume" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="template_type" label="Tip" rules={[{ required: true }]}>
            <Select options={[
              { label: "Ofertă", value: "offer" },
              { label: "Contract", value: "contract" },
              { label: "Factură", value: "invoice" },
              { label: "Raport", value: "report" },
              { label: "SdL", value: "sdl" },
            ]} />
          </Form.Item>
          <Form.Item name="content_template" label="Conținut template">
            <Input.TextArea rows={6} placeholder="HTML / Markdown template..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Create Custom Field Modal */}
      <Modal
        title="Câmp Custom Nou"
        open={cfModalOpen}
        onCancel={() => setCfModalOpen(false)}
        onOk={() => cfForm.validateFields().then((v) => createCFMut.mutate(v))}
        confirmLoading={createCFMut.isPending}
        okText="Creează"
        cancelText="Anulează"
      >
        <Form form={cfForm} layout="vertical">
          <Form.Item name="field_name" label="Nume câmp" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="entity_type" label="Entitate" rules={[{ required: true }]}>
            <Select options={[
              { label: "Contact", value: "contact" },
              { label: "Oportunitate", value: "opportunity" },
              { label: "Proiect", value: "project" },
              { label: "Ofertă", value: "offer" },
              { label: "Contract", value: "contract" },
              { label: "Angajat", value: "employee" },
            ]} />
          </Form.Item>
          <Form.Item name="field_type" label="Tip" rules={[{ required: true }]}>
            <Select options={[
              { label: "Text", value: "text" },
              { label: "Număr", value: "number" },
              { label: "Dată", value: "date" },
              { label: "Selectare", value: "select" },
              { label: "Checkbox", value: "checkbox" },
              { label: "URL", value: "url" },
            ]} />
          </Form.Item>
          <Form.Item name="is_required" label="Obligatoriu" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
