/**
 * F137: Personalizare Cromatică + F138: Suport Multi-limbă — Settings Page (E-024)
 *
 * Sections:
 * 1. Logo — upload custom logo (white-label)
 * 2. Colors — primary/secondary with ColorPicker + live preview
 * 3. Fonts — font family selector per tenant
 * 4. Language — default language, bilingual docs toggle, secondary language
 * 5. White-label — app name override, hide BuildWise branding
 *
 * P3 only — M2M ERP Lite SaaS.
 */
import { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Space,
  Input,
  Select,
  Switch,
  ColorPicker,
  Upload,
  Divider,
  Tag,
  message,
  Alert,
  Avatar,
} from "antd";
import type { Color } from "antd/es/color-picker";
import {
  FormatPainterOutlined,
  UploadOutlined,
  SaveOutlined,
  DeleteOutlined,
  GlobalOutlined,
  FontSizeOutlined,
  BgColorsOutlined,
  PictureOutlined,
  EyeOutlined,
  BankOutlined,
  UndoOutlined,
  CrownOutlined,
} from "@ant-design/icons";
import { useBrandingStore } from "../../../stores/brandingStore";
import { useLanguage } from "../../../i18n";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { systemService } from "../services/systemService";

const { Title, Text, Paragraph } = Typography;

const LANGUAGE_OPTIONS = [
  { value: "ro", label: "Română" },
  { value: "en", label: "English" },
];

const FONT_OPTIONS = [
  { value: "Inter, -apple-system, BlinkMacSystemFont, sans-serif", label: "Inter (default)" },
  { value: "'Roboto', sans-serif", label: "Roboto" },
  { value: "'Open Sans', sans-serif", label: "Open Sans" },
  { value: "'Poppins', sans-serif", label: "Poppins" },
  { value: "'Nunito', sans-serif", label: "Nunito" },
  { value: "'Lato', sans-serif", label: "Lato" },
  { value: "'Source Sans Pro', sans-serif", label: "Source Sans Pro" },
  { value: "'Montserrat', sans-serif", label: "Montserrat" },
];

const CURRENCY_OPTIONS = [
  { value: "RON", label: "RON — Leu Românesc" },
  { value: "EUR", label: "EUR — Euro" },
  { value: "USD", label: "USD — Dolar American" },
  { value: "GBP", label: "GBP — Liră Sterlină" },
];

export default function BrandingSettingsPage() {
  const branding = useBrandingStore();
  const { locale, setLocale, bilingualDocs, setBilingualDocs, secondaryLocale, setSecondaryLocale } = useLanguage();
  const queryClient = useQueryClient();

  // Local state mirrors branding store for editing
  const [appName, setAppName] = useState(branding.appName);
  const [logoUrl, setLogoUrl] = useState(branding.logoUrl);
  const [primaryColor, setPrimaryColor] = useState(branding.primaryColor);
  const [secondaryColor, setSecondaryColor] = useState(branding.secondaryColor);
  const [fontFamily, setFontFamily] = useState(branding.fontFamily);
  const [borderRadius, setBorderRadius] = useState(branding.borderRadius);
  const [whiteLabelEnabled, setWhiteLabelEnabled] = useState(branding.whiteLabelEnabled);
  const [currency, setCurrency] = useState(() => localStorage.getItem("buildwise_currency") ?? "RON");

  // Sync local state when store changes (e.g. after reset)
  useEffect(() => {
    setAppName(branding.appName);
    setLogoUrl(branding.logoUrl);
    setPrimaryColor(branding.primaryColor);
    setSecondaryColor(branding.secondaryColor);
    setFontFamily(branding.fontFamily);
    setBorderRadius(branding.borderRadius);
    setWhiteLabelEnabled(branding.whiteLabelEnabled);
  }, [branding.appName, branding.logoUrl, branding.primaryColor, branding.secondaryColor, branding.fontFamily, branding.borderRadius, branding.whiteLabelEnabled]);

  const saveMutation = useMutation({
    mutationFn: () =>
      systemService.updateOrganization({
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        custom_branding: {
          app_name: appName,
          logo_url: logoUrl,
          font_family: fontFamily,
          border_radius: borderRadius,
          white_label_enabled: whiteLabelEnabled,
        },
        default_language: locale,
        default_currency: currency,
      }),
    onSuccess: () => {
      branding.applyBranding({
        appName,
        logoUrl,
        primaryColor,
        secondaryColor,
        fontFamily,
        borderRadius,
        whiteLabelEnabled,
      });
      localStorage.setItem("buildwise_currency", currency);
      queryClient.invalidateQueries({ queryKey: ["organization"] });
      message.success("Setările de branding au fost salvate.");
    },
    onError: () => message.error("Eroare la salvare."),
  });

  function handleReset() {
    branding.resetBranding();
    setLocale("ro");
    setBilingualDocs(false);
    setCurrency("RON");
    message.info("Branding resetat la valorile implicite.");
  }

  return (
    <div style={{ padding: 24, maxWidth: 1100 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <FormatPainterOutlined /> Branding și Personalizare (F137 + F138)
          </Title>
          <Text type="secondary">
            Configurează aspectul vizual, limba și white-label. P3 — M2M ERP Lite.
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<UndoOutlined />} onClick={handleReset}>
              Resetează
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              loading={saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              Salvează
            </Button>
          </Space>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* ─── Left Column: Settings ───────────────────────────────────── */}
        <Col xs={24} lg={14}>
          {/* Logo */}
          <Card
            title={<><PictureOutlined /> Logo</>}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Paragraph type="secondary">
              Logo-ul apare în sidebar, pe documente generate și în emailuri.
            </Paragraph>
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              {logoUrl && (
                <div style={{ textAlign: "center", padding: 16, background: "#fafafa", borderRadius: 8 }}>
                  <img
                    src={logoUrl}
                    alt="Logo"
                    style={{ maxHeight: 60, maxWidth: 200, objectFit: "contain" }}
                  />
                </div>
              )}
              <Space>
                <Upload
                  accept="image/*"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                      if (e.target?.result) setLogoUrl(e.target.result as string);
                    };
                    reader.readAsDataURL(file);
                    return false;
                  }}
                >
                  <Button icon={<UploadOutlined />}>Încarcă Logo</Button>
                </Upload>
                <Input
                  placeholder="sau URL extern..."
                  value={logoUrl}
                  onChange={(e) => setLogoUrl(e.target.value)}
                  style={{ width: 300 }}
                />
                {logoUrl && (
                  <Button danger icon={<DeleteOutlined />} onClick={() => setLogoUrl("")}>
                    Elimină
                  </Button>
                )}
              </Space>
            </Space>
          </Card>

          {/* Colors */}
          <Card
            title={<><BgColorsOutlined /> Culori</>}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Paragraph type="secondary">
              Culorile sunt aplicate global în interfață și pe documentele generate.
            </Paragraph>
            <Row gutter={24}>
              <Col span={12}>
                <Text>Culoare Principală</Text>
                <div style={{ marginTop: 8 }}>
                  <ColorPicker
                    value={primaryColor}
                    onChange={(_: Color, hex: string) => setPrimaryColor(hex)}
                    showText
                    size="large"
                  />
                </div>
              </Col>
              <Col span={12}>
                <Text>Culoare Secundară</Text>
                <div style={{ marginTop: 8 }}>
                  <ColorPicker
                    value={secondaryColor}
                    onChange={(_: Color, hex: string) => setSecondaryColor(hex)}
                    showText
                    size="large"
                  />
                </div>
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text>Border Radius</Text>
              <Select
                value={borderRadius}
                onChange={setBorderRadius}
                style={{ width: 150, marginLeft: 12 }}
                options={[
                  { value: 0, label: "0px — Pătrat" },
                  { value: 4, label: "4px — Ușor" },
                  { value: 6, label: "6px — Default" },
                  { value: 8, label: "8px — Rotunjit" },
                  { value: 12, label: "12px — Foarte rotunjit" },
                ]}
              />
            </div>
          </Card>

          {/* Fonts */}
          <Card
            title={<><FontSizeOutlined /> Fonturi</>}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Paragraph type="secondary">
              Fontul se aplică pe întreaga platformă.
            </Paragraph>
            <Select
              value={fontFamily}
              onChange={setFontFamily}
              options={FONT_OPTIONS}
              style={{ width: "100%" }}
            />
            <div style={{ marginTop: 12, padding: 12, background: "#fafafa", borderRadius: 8 }}>
              <Text style={{ fontFamily }}>
                Acesta este un exemplu de text cu fontul selectat. Aa Bb Cc 0123456789.
              </Text>
            </div>
          </Card>

          {/* Language (F138) */}
          <Card
            title={<><GlobalOutlined /> Limbă (F138)</>}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Paragraph type="secondary">
              Limba implicită a platformei și suport bilingv pentru oferte/contracte.
            </Paragraph>
            <Row gutter={16}>
              <Col span={12}>
                <Text>Limba Implicită</Text>
                <Select
                  value={locale}
                  onChange={(v) => setLocale(v as "ro" | "en")}
                  options={LANGUAGE_OPTIONS}
                  style={{ width: "100%", marginTop: 4 }}
                />
              </Col>
              <Col span={12}>
                <Text>Valuta</Text>
                <Select
                  value={currency}
                  onChange={setCurrency}
                  options={CURRENCY_OPTIONS}
                  style={{ width: "100%", marginTop: 4 }}
                />
              </Col>
            </Row>

            <Divider dashed style={{ margin: "16px 0" }} />

            <Row gutter={16} align="middle">
              <Col span={16}>
                <Text strong>Documente Bilingve (RO+EN)</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Generează oferte și contracte în ambele limbi simultan.
                </Text>
              </Col>
              <Col span={8} style={{ textAlign: "right" }}>
                <Switch checked={bilingualDocs} onChange={setBilingualDocs} />
              </Col>
            </Row>

            {bilingualDocs && (
              <div style={{ marginTop: 12 }}>
                <Text>Limba Secundară (documente)</Text>
                <Select
                  value={secondaryLocale}
                  onChange={(v) => setSecondaryLocale(v as "ro" | "en")}
                  options={LANGUAGE_OPTIONS.filter((l) => l.value !== locale)}
                  style={{ width: "100%", marginTop: 4 }}
                />
                <Alert
                  type="info"
                  showIcon
                  style={{ marginTop: 8 }}
                  message="Ofertele și contractele vor conține textul în ambele limbi, cu limba primară în stânga și limba secundară în dreapta."
                />
              </div>
            )}
          </Card>

          {/* White-Label (F137) */}
          <Card
            title={<><CrownOutlined /> White-Label (F137)</>}
            size="small"
          >
            <Paragraph type="secondary">
              Aplicația arată ca produsul clientului, fără branding BuildWise.
            </Paragraph>

            <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
              <Col span={16}>
                <Text strong>Activează White-Label</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Ascunde logo-ul și numele BuildWise din interfață.
                </Text>
              </Col>
              <Col span={8} style={{ textAlign: "right" }}>
                <Switch checked={whiteLabelEnabled} onChange={setWhiteLabelEnabled} />
              </Col>
            </Row>

            {whiteLabelEnabled && (
              <div>
                <Text>Numele Aplicației</Text>
                <Input
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="ex: EnergyPro, MyERP..."
                  style={{ marginTop: 4 }}
                />
                <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: 4 }}>
                  Înlocuiește &quot;BuildWise&quot; în sidebar, header și documente generate.
                </Text>
              </div>
            )}
          </Card>
        </Col>

        {/* ─── Right Column: Live Preview ─────────────────────────────── */}
        <Col xs={24} lg={10}>
          <Card
            title={<><EyeOutlined /> Previzualizare Live</>}
            size="small"
            style={{ position: "sticky", top: 80 }}
          >
            {/* Mini App Preview */}
            <div style={{ borderRadius: borderRadius + 2, overflow: "hidden", border: "1px solid #e8e8e8" }}>
              {/* Header */}
              <div style={{ background: primaryColor, padding: "10px 16px", color: "#fff", fontFamily }}>
                <Space>
                  {logoUrl ? (
                    <img src={logoUrl} alt="Logo" style={{ height: 22, objectFit: "contain" }} />
                  ) : (
                    <Avatar size="small" style={{ background: "rgba(255,255,255,0.2)" }}>
                      <BankOutlined />
                    </Avatar>
                  )}
                  <Text strong style={{ color: "#fff", fontFamily }}>
                    {whiteLabelEnabled ? appName : "BuildWise"}
                  </Text>
                </Space>
              </div>

              {/* Body */}
              <Row>
                {/* Sidebar */}
                <Col span={7} style={{ background: "#fafafa", padding: "10px 6px", minHeight: 180, fontFamily }}>
                  {["CRM", "Pipeline", "PM", "RM", "BI"].map((mod, i) => (
                    <div
                      key={mod}
                      style={{
                        padding: "4px 8px",
                        fontSize: 10,
                        borderLeft: i === 0 ? `3px solid ${primaryColor}` : "3px solid transparent",
                        marginBottom: 3,
                        background: i === 0 ? "#fff" : "transparent",
                        borderRadius,
                        fontWeight: i === 0 ? 600 : 400,
                        color: i === 0 ? primaryColor : "#666",
                        fontFamily,
                      }}
                    >
                      {mod}
                    </div>
                  ))}
                </Col>

                {/* Content */}
                <Col span={17} style={{ padding: 10, fontFamily }}>
                  <div
                    style={{
                      background: secondaryColor,
                      borderRadius,
                      padding: 8,
                      marginBottom: 8,
                      opacity: 0.2,
                      height: 16,
                    }}
                  />
                  <div
                    style={{
                      background: "#f0f0f0",
                      borderRadius,
                      padding: 6,
                      height: 12,
                      marginBottom: 6,
                    }}
                  />
                  <div
                    style={{
                      background: "#f0f0f0",
                      borderRadius,
                      padding: 6,
                      height: 12,
                      marginBottom: 6,
                      width: "60%",
                    }}
                  />

                  {/* Mock button */}
                  <div
                    style={{
                      background: primaryColor,
                      color: "#fff",
                      borderRadius,
                      padding: "3px 10px",
                      fontSize: 10,
                      display: "inline-block",
                      marginTop: 8,
                      fontFamily,
                    }}
                  >
                    {locale === "en" ? "Save" : "Salvează"}
                  </div>

                  {/* Tags */}
                  <div style={{ marginTop: 10 }}>
                    <Tag color={primaryColor}>
                      {LANGUAGE_OPTIONS.find((l) => l.value === locale)?.label}
                    </Tag>
                    <Tag>{currency}</Tag>
                    {bilingualDocs && <Tag color="blue">Bilingv</Tag>}
                  </div>
                </Col>
              </Row>

              {/* Footer */}
              <div
                style={{
                  background: "#fafafa",
                  padding: "6px 16px",
                  fontSize: 10,
                  color: "#999",
                  borderTop: "1px solid #e8e8e8",
                  fontFamily,
                }}
              >
                {whiteLabelEnabled
                  ? `© ${new Date().getFullYear()} ${appName}`
                  : `© ${new Date().getFullYear()} BuildWise by BAHN S.R.L.`}
              </div>
            </div>

            {/* Document Preview (Bilingual F138) */}
            {bilingualDocs && (
              <>
                <Divider dashed style={{ margin: "16px 0 12px" }}>
                  Previzualizare Document Bilingv
                </Divider>
                <div style={{ border: "1px solid #e8e8e8", borderRadius, padding: 12, fontSize: 11, fontFamily }}>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong style={{ fontSize: 12 }}>OFERTĂ / OFFER</Text>
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary">
                          {locale === "ro" ? "Nr. ofertă:" : "Offer no.:"} OF-2026-001
                        </Text>
                      </div>
                      <div style={{ marginTop: 8, borderTop: `2px solid ${primaryColor}`, paddingTop: 4 }}>
                        <Text style={{ fontSize: 10 }}>
                          Descriere produs / Product description
                        </Text>
                      </div>
                    </Col>
                    <Col span={12} style={{ borderLeft: "1px dashed #d9d9d9", paddingLeft: 12 }}>
                      <Text strong style={{ fontSize: 12 }}>
                        {secondaryLocale === "en" ? "OFFER" : "OFERTĂ"}
                      </Text>
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary">
                          {secondaryLocale === "en" ? "Offer no.:" : "Nr. ofertă:"} OF-2026-001
                        </Text>
                      </div>
                      <div style={{ marginTop: 8, borderTop: `2px solid ${secondaryColor}`, paddingTop: 4 }}>
                        <Text style={{ fontSize: 10 }}>
                          {secondaryLocale === "en" ? "Product description" : "Descriere produs"}
                        </Text>
                      </div>
                    </Col>
                  </Row>
                  <Divider dashed style={{ margin: "8px 0" }} />
                  <Row justify="space-between">
                    <Text style={{ fontSize: 9, color: "#999" }}>
                      {locale === "ro" ? "Semnătura Client" : "Client Signature"} / {secondaryLocale === "en" ? "Client Signature" : "Semnătura Client"}
                    </Text>
                    <Text style={{ fontSize: 9, color: "#999" }}>
                      {locale === "ro" ? "Semnătura Prestator" : "Provider Signature"} / {secondaryLocale === "en" ? "Provider Signature" : "Semnătura Prestator"}
                    </Text>
                  </Row>
                </div>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
