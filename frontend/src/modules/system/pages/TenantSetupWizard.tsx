/**
 * F160: Tenant Setup Wizard — SaaS Onboarding (P3)
 * Wizard prima conectare: configurare companie, branding, module active, utilizatori.
 *
 * Step 1: Date companie (nume, CUI, adresă, logo)
 * Step 2: Activare module (CRM, Pipeline, PM, RM, BI)
 * Step 3: Creare utilizatori inițiali + rol assignment
 * Step 4: Branding personalizat (culori, limbă, valută)
 *
 * F-codes: F160, F136, F137, F138, F139, F040
 */
import { useState, useCallback } from "react";
import {
  Card,
  Steps,
  Button,
  Form,
  Input,
  Typography,
  Row,
  Col,
  Space,
  Switch,
  Tag,
  Select,
  ColorPicker,
  message,
  Result,
  Avatar,
  Divider,
  Alert,
} from "antd";
import type { Color } from "antd/es/color-picker";
import {
  BankOutlined,
  AppstoreOutlined,
  UserAddOutlined,
  FormatPainterOutlined,
  CheckCircleOutlined,
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  ToolOutlined,
  BarChartOutlined,
  PlusOutlined,
  DeleteOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { systemService } from "../services/systemService";
import type { TenantSetupPayload } from "../../../types";

const { Title, Text, Paragraph } = Typography;

// ─── Module definitions ─────────────────────────────────────────────────────

const AVAILABLE_MODULES = [
  {
    key: "crm",
    label: "CRM — Contacts & Properties",
    description: "Gestiune contacte, proprietăți, profiluri energetice",
    icon: <TeamOutlined style={{ fontSize: 24 }} />,
    default: true,
    fcodes: "F001-F010",
  },
  {
    key: "pipeline",
    label: "Sales Pipeline",
    description: "Oportunități, oferte, contracte, forecast",
    icon: <FunnelPlotOutlined style={{ fontSize: 24 }} />,
    default: true,
    fcodes: "F020-F063",
  },
  {
    key: "pm",
    label: "Project Management",
    description: "Proiecte, WBS, Gantt, devize, situații de lucrări",
    icon: <ProjectOutlined style={{ fontSize: 24 }} />,
    default: true,
    fcodes: "F069-F095",
  },
  {
    key: "rm",
    label: "Resource Management",
    description: "HR, echipamente, materiale, alocare resurse (P2+P3)",
    icon: <ToolOutlined style={{ fontSize: 24 }} />,
    default: false,
    fcodes: "F107-F131",
    badge: "P2+P3",
  },
  {
    key: "bi",
    label: "Business Intelligence",
    description: "Dashboards, rapoarte, KPI-uri, AI assistant",
    icon: <BarChartOutlined style={{ fontSize: 24 }} />,
    default: false,
    fcodes: "F132-F135",
  },
];

const ROLE_OPTIONS = [
  { value: "admin", label: "Administrator", description: "Acces complet" },
  { value: "manager_vanzari", label: "Manager Vânzări", description: "CRM + Pipeline + Rapoarte" },
  { value: "agent_comercial", label: "Agent Comercial", description: "CRM + Pipeline propriu" },
  { value: "tehnician", label: "Tehnician", description: "PM + Execuție" },
];

const LANGUAGE_OPTIONS = [
  { value: "ro", label: "Română" },
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
];

const CURRENCY_OPTIONS = [
  { value: "RON", label: "RON — Leu Românesc" },
  { value: "EUR", label: "EUR — Euro" },
  { value: "USD", label: "USD — Dolar American" },
  { value: "GBP", label: "GBP — Liră Sterlină" },
];

interface InvitedUser {
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function TenantSetupWizard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Wizard step
  const [currentStep, setCurrentStep] = useState(0);

  // Step 1: Company
  const [companyForm] = Form.useForm();

  // Step 2: Modules
  const [enabledModules, setEnabledModules] = useState<string[]>(
    AVAILABLE_MODULES.filter((m) => m.default).map((m) => m.key)
  );

  // Step 3: Users
  const [invitedUsers, setInvitedUsers] = useState<InvitedUser[]>([]);
  const [userForm] = Form.useForm();

  // Step 4: Branding
  const [primaryColor, setPrimaryColor] = useState("#1677ff");
  const [secondaryColor, setSecondaryColor] = useState("#52c41a");
  const [language, setLanguage] = useState("ro");
  const [currency, setCurrency] = useState("RON");

  // Setup complete
  const [setupDone, setSetupDone] = useState(false);

  // Submit mutation
  const setupMut = useMutation({
    mutationFn: (payload: TenantSetupPayload) =>
      systemService.completeTenantSetup(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization"] });
      setSetupDone(true);
      message.success("Configurare completă! Platforma este gata.");
    },
    onError: () => message.error("Eroare la configurare. Încearcă din nou."),
  });

  // Module toggle
  const toggleModule = useCallback((key: string) => {
    setEnabledModules((prev) =>
      prev.includes(key) ? prev.filter((m) => m !== key) : [...prev, key]
    );
  }, []);

  // Add user
  const addUser = useCallback(() => {
    userForm.validateFields().then((vals) => {
      setInvitedUsers((prev) => [...prev, vals as InvitedUser]);
      userForm.resetFields();
    });
  }, [userForm]);

  // Remove user
  const removeUser = useCallback((idx: number) => {
    setInvitedUsers((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  // Final submit
  const handleFinish = useCallback(async () => {
    const companyVals = await companyForm.validateFields();
    const payload: TenantSetupPayload = {
      company: {
        name: companyVals.name,
        cui: companyVals.cui,
        phone: companyVals.phone,
        email: companyVals.email,
        address: companyVals.address,
      },
      branding: {
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        default_language: language,
        default_currency: currency,
      },
      modules: enabledModules,
      users: invitedUsers,
    };
    setupMut.mutate(payload);
  }, [companyForm, primaryColor, secondaryColor, language, currency, enabledModules, invitedUsers, setupMut]);

  // ─── Step 1: Company Data ─────────────────────────────────────────────────

  const renderCompanyStep = () => (
    <div>
      <Title level={5}>
        <BankOutlined /> Date Companie
      </Title>
      <Paragraph type="secondary">
        Configurează datele firmei. Acestea vor apărea pe documente (oferte, contracte, facturi).
      </Paragraph>

      <Form form={companyForm} layout="vertical" style={{ maxWidth: 600 }}>
        <Form.Item
          name="name"
          label="Denumire companie"
          rules={[{ required: true, message: "Introdu numele companiei" }]}
        >
          <Input placeholder="Ex: BAHN S.R.L." size="large" />
        </Form.Item>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="cui" label="CUI / Cod Fiscal">
              <Input placeholder="Ex: RO12345678" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="phone" label="Telefon">
              <Input placeholder="+40..." />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item name="email" label="Email companie">
          <Input placeholder="office@company.ro" />
        </Form.Item>

        <Form.Item name="address" label="Adresă sediu">
          <Input.TextArea rows={2} placeholder="Strada, Nr, Orașul, Județul" />
        </Form.Item>
      </Form>
    </div>
  );

  // ─── Step 2: Module Activation ────────────────────────────────────────────

  const renderModulesStep = () => (
    <div>
      <Title level={5}>
        <AppstoreOutlined /> Activare Module
      </Title>
      <Paragraph type="secondary">
        Selectează modulele pe care le vei folosi. Poți activa/dezactiva ulterior din Setări.
      </Paragraph>

      <Row gutter={[16, 16]}>
        {AVAILABLE_MODULES.map((mod) => {
          const isEnabled = enabledModules.includes(mod.key);
          return (
            <Col xs={24} sm={12} key={mod.key}>
              <Card
                hoverable
                onClick={() => toggleModule(mod.key)}
                style={{
                  borderColor: isEnabled ? "#1677ff" : "#d9d9d9",
                  borderWidth: isEnabled ? 2 : 1,
                  opacity: isEnabled ? 1 : 0.7,
                }}
              >
                <Row justify="space-between" align="middle">
                  <Col>
                    <Space>
                      {mod.icon}
                      <div>
                        <Text strong>{mod.label}</Text>
                        {mod.badge && (
                          <Tag color="orange" style={{ marginLeft: 8 }}>
                            {mod.badge}
                          </Tag>
                        )}
                        <br />
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {mod.description}
                        </Text>
                        <br />
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {mod.fcodes}
                        </Text>
                      </div>
                    </Space>
                  </Col>
                  <Col>
                    <Switch
                      checked={isEnabled}
                      onChange={() => toggleModule(mod.key)}
                    />
                  </Col>
                </Row>
              </Card>
            </Col>
          );
        })}
      </Row>

      <Alert
        type="info"
        showIcon
        style={{ marginTop: 16 }}
        message={`${enabledModules.length} module active din ${AVAILABLE_MODULES.length}`}
      />
    </div>
  );

  // ─── Step 3: Initial Users ────────────────────────────────────────────────

  const renderUsersStep = () => (
    <div>
      <Title level={5}>
        <UserAddOutlined /> Utilizatori Inițiali
      </Title>
      <Paragraph type="secondary">
        Invită membrii echipei. Vor primi email de activare. Contul tău (admin) e deja creat.
      </Paragraph>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Form form={userForm} layout="inline" style={{ gap: 8, flexWrap: "wrap" }}>
          <Form.Item
            name="email"
            rules={[{ required: true, type: "email", message: "Email valid" }]}
          >
            <Input placeholder="email@company.ro" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item
            name="first_name"
            rules={[{ required: true, message: "Prenume" }]}
          >
            <Input placeholder="Prenume" style={{ width: 120 }} />
          </Form.Item>
          <Form.Item
            name="last_name"
            rules={[{ required: true, message: "Nume" }]}
          >
            <Input placeholder="Nume" style={{ width: 120 }} />
          </Form.Item>
          <Form.Item
            name="role"
            rules={[{ required: true, message: "Selectează rol" }]}
          >
            <Select
              placeholder="Rol"
              style={{ width: 180 }}
              options={ROLE_OPTIONS.map((r) => ({
                value: r.value,
                label: `${r.label} — ${r.description}`,
              }))}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={addUser}
            >
              Adaugă
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {invitedUsers.length === 0 && (
        <Alert
          type="info"
          showIcon
          message="Poți sări acest pas și adăuga utilizatori ulterior din Setări → Utilizatori"
        />
      )}

      {invitedUsers.length > 0 && (
        <Card size="small" title={`${invitedUsers.length} utilizatori de invitat`}>
          {invitedUsers.map((u, idx) => (
            <Row
              key={idx}
              justify="space-between"
              align="middle"
              style={{
                padding: "8px 0",
                borderBottom: idx < invitedUsers.length - 1 ? "1px solid #f0f0f0" : undefined,
              }}
            >
              <Col>
                <Space>
                  <Avatar size="small">
                    {u.first_name[0]}
                    {u.last_name[0]}
                  </Avatar>
                  <div>
                    <Text strong>
                      {u.first_name} {u.last_name}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {u.email}
                    </Text>
                  </div>
                </Space>
              </Col>
              <Col>
                <Space>
                  <Tag color="blue">
                    {ROLE_OPTIONS.find((r) => r.value === u.role)?.label ?? u.role}
                  </Tag>
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    size="small"
                    onClick={() => removeUser(idx)}
                  />
                </Space>
              </Col>
            </Row>
          ))}
        </Card>
      )}
    </div>
  );

  // ─── Step 4: Branding ─────────────────────────────────────────────────────

  const renderBrandingStep = () => (
    <div>
      <Title level={5}>
        <FormatPainterOutlined /> Branding Personalizat
      </Title>
      <Paragraph type="secondary">
        Configurează aspectul vizual al platformei. Culorile vor apărea în interfață și pe documente generate.
      </Paragraph>

      <Row gutter={24}>
        <Col xs={24} md={12}>
          <Card size="small" title="Culori" style={{ marginBottom: 16 }}>
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              <div>
                <Text>Culoare principală</Text>
                <div style={{ marginTop: 4 }}>
                  <ColorPicker
                    value={primaryColor}
                    onChange={(_: Color, hex: string) => setPrimaryColor(hex)}
                    showText
                  />
                </div>
              </div>
              <div>
                <Text>Culoare secundară</Text>
                <div style={{ marginTop: 4 }}>
                  <ColorPicker
                    value={secondaryColor}
                    onChange={(_: Color, hex: string) => setSecondaryColor(hex)}
                    showText
                  />
                </div>
              </div>
            </Space>
          </Card>

          <Card size="small" title="Localizare">
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              <div>
                <Text>Limba implicită (F138)</Text>
                <Select
                  value={language}
                  onChange={setLanguage}
                  style={{ width: "100%", marginTop: 4 }}
                  options={LANGUAGE_OPTIONS}
                />
              </div>
              <div>
                <Text>Valuta principală (F139)</Text>
                <Select
                  value={currency}
                  onChange={setCurrency}
                  style={{ width: "100%", marginTop: 4 }}
                  options={CURRENCY_OPTIONS}
                />
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card size="small" title="Preview Branding">
            <div
              style={{
                borderRadius: 8,
                overflow: "hidden",
                border: "1px solid #f0f0f0",
              }}
            >
              {/* Mock header */}
              <div
                style={{
                  background: primaryColor,
                  padding: "12px 16px",
                  color: "#fff",
                }}
              >
                <Space>
                  <BankOutlined />
                  <Text strong style={{ color: "#fff" }}>
                    {companyForm.getFieldValue("name") || "Compania Ta"}
                  </Text>
                </Space>
              </div>
              {/* Mock sidebar */}
              <Row>
                <Col
                  span={6}
                  style={{
                    background: "#f5f5f5",
                    padding: "12px 8px",
                    minHeight: 120,
                  }}
                >
                  {enabledModules.slice(0, 4).map((mod) => (
                    <div
                      key={mod}
                      style={{
                        padding: "4px 8px",
                        fontSize: 11,
                        borderLeft: `3px solid ${primaryColor}`,
                        marginBottom: 4,
                        background: "#fff",
                        borderRadius: 2,
                      }}
                    >
                      {mod.toUpperCase()}
                    </div>
                  ))}
                </Col>
                <Col span={18} style={{ padding: 12 }}>
                  <div
                    style={{
                      background: secondaryColor,
                      borderRadius: 4,
                      padding: 8,
                      marginBottom: 8,
                      opacity: 0.3,
                      height: 20,
                    }}
                  />
                  <div
                    style={{
                      background: "#f0f0f0",
                      borderRadius: 4,
                      padding: 8,
                      height: 40,
                    }}
                  />
                  <div style={{ marginTop: 8, textAlign: "center" }}>
                    <Tag color={primaryColor}>
                      {LANGUAGE_OPTIONS.find((l) => l.value === language)?.label}
                    </Tag>
                    <Tag>{currency}</Tag>
                  </div>
                </Col>
              </Row>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );

  // ─── Completion ───────────────────────────────────────────────────────────

  if (setupDone) {
    return (
      <div style={{ maxWidth: 600, margin: "80px auto", padding: 24 }}>
        <Result
          status="success"
          icon={<RocketOutlined style={{ color: primaryColor }} />}
          title="Platforma este configurată!"
          subTitle={
            <>
              <Paragraph>
                {enabledModules.length} module active
                {invitedUsers.length > 0 && `, ${invitedUsers.length} utilizatori invitați`}.
              </Paragraph>
              <Paragraph type="secondary">
                Poți modifica oricând setările din meniul Setări.
              </Paragraph>
            </>
          }
          extra={[
            <Button
              type="primary"
              size="large"
              key="start"
              onClick={() => navigate("/")}
              style={{ background: primaryColor }}
            >
              Începe să folosești BuildWise
            </Button>,
          ]}
        />
      </div>
    );
  }

  // ─── Step content ─────────────────────────────────────────────────────────

  const steps = [
    { title: "Companie", icon: <BankOutlined />, content: renderCompanyStep },
    { title: "Module", icon: <AppstoreOutlined />, content: renderModulesStep },
    { title: "Utilizatori", icon: <UserAddOutlined />, content: renderUsersStep },
    { title: "Branding", icon: <FormatPainterOutlined />, content: renderBrandingStep },
  ];

  const canNextStep2 = enabledModules.length > 0;

  const handleNext = async () => {
    if (currentStep === 0) {
      await companyForm.validateFields();
    }
    setCurrentStep((s) => s + 1);
  };

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 24 }}>
      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <Title level={3}>
          <RocketOutlined /> BuildWise — Configurare Platformă
        </Title>
        <Paragraph type="secondary">
          Wizard onboarding — F160. Configurează platforma în 4 pași simpli.
        </Paragraph>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Steps
          current={currentStep}
          items={steps.map((s) => ({
            title: s.title,
            icon: s.icon,
          }))}
        />
      </Card>

      <Card>{steps[currentStep]!.content()}</Card>

      <Divider />

      {/* Navigation */}
      <Row justify="space-between">
        <Col>
          {currentStep > 0 && (
            <Button onClick={() => setCurrentStep((s) => s - 1)}>
              Înapoi
            </Button>
          )}
        </Col>
        <Col>
          <Space>
            {currentStep === 2 && (
              <Button onClick={() => setCurrentStep(3)}>
                Sări peste
              </Button>
            )}
            {currentStep < steps.length - 1 && (
              <Button
                type="primary"
                onClick={handleNext}
                disabled={currentStep === 1 && !canNextStep2}
              >
                Continuă
              </Button>
            )}
            {currentStep === steps.length - 1 && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleFinish}
                loading={setupMut.isPending}
                size="large"
              >
                Finalizează Configurarea
              </Button>
            )}
          </Space>
        </Col>
      </Row>
    </div>
  );
}
