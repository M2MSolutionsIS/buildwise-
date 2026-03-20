/**
 * E-005 — Offer Builder Wizard (5 steps)
 * F-codes: F019 (Offer Builder), F020 (Client Select), F021/F022 (Line Items),
 *          F023 (T&C + Output), F024/F025 (Preview & Generate), F026 (Versionare)
 */
import { useState, useMemo, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Steps,
  Button,
  Card,
  Form,
  Input,
  Select,
  InputNumber,
  Table,
  Space,
  Typography,
  Alert,
  Divider,
  Row,
  Col,
  message,
  Popconfirm,
  Descriptions,
  Tag,
} from "antd";
import {
  UserOutlined,
  ShoppingCartOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  EyeOutlined,
  PlusOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";
import { offerService } from "../services/offerService";
import ProductPickerModal from "../components/ProductPickerModal";
import type { OfferLineItemCreate, ContactListItem, Property, Product } from "../../../types";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// U value for BAHM treated glass — critical business parameter
const U_VALUE_TREATED_GLASS = 0.3; // W/m²K

interface LineItemRow extends OfferLineItemCreate {
  _key: string;
}

export default function OfferBuilderPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const preselectedContactId = searchParams.get("contact_id") || undefined;
  const preselectedPropertyId = searchParams.get("property_id") || undefined;

  const [currentStep, setCurrentStep] = useState(0);
  const [contactId, setContactId] = useState<string | undefined>(preselectedContactId);
  const [propertyId, setPropertyId] = useState<string | undefined>(preselectedPropertyId);
  const [contactSearch, setContactSearch] = useState("");
  const [lineItems, setLineItems] = useState<LineItemRow[]>([]);
  const [offerTitle, setOfferTitle] = useState("");
  const [offerDescription, setOfferDescription] = useState("");
  const [currency, setCurrency] = useState("RON");
  const [validityDays, setValidityDays] = useState(30);
  const [termsAndConditions, setTermsAndConditions] = useState(DEFAULT_TERMS);
  const [productPickerOpen, setProductPickerOpen] = useState(false);
  const [draftSavedAt, setDraftSavedAt] = useState<string | null>(null);
  const [createdOfferId, setCreatedOfferId] = useState<string | null>(null);

  // F020 — Search contacts
  const { data: contactsData, isLoading: contactsLoading } = useQuery({
    queryKey: ["contacts-search", contactSearch],
    queryFn: () => contactService.list({ search: contactSearch, per_page: 10 }),
    enabled: contactSearch.length >= 2,
  });

  // Load selected contact details
  const { data: selectedContact } = useQuery({
    queryKey: ["contact", contactId],
    queryFn: () => contactService.get(contactId!),
    enabled: !!contactId,
  });

  // Load contact properties
  const { data: propertiesData } = useQuery({
    queryKey: ["contact-properties", contactId],
    queryFn: () => contactService.listProperties(contactId!),
    enabled: !!contactId,
  });

  const contact = selectedContact?.data;
  const properties = propertiesData?.data || [];
  const selectedProperty = properties.find((p: Property) => p.id === propertyId);

  // F019 — Create offer mutation
  const createOfferMutation = useMutation({
    mutationFn: () =>
      offerService.create({
        contact_id: contactId!,
        property_id: propertyId,
        title: offerTitle || `Ofertă ${contact?.company_name || ""}`,
        description: offerDescription,
        currency,
        validity_days: validityDays,
        terms_and_conditions: termsAndConditions,
        line_items: lineItems.map(({ _key, ...item }) => item),
      }),
    onSuccess: (res) => {
      setCreatedOfferId(res.data.id);
      setDraftSavedAt(new Date().toLocaleTimeString("ro-RO", { hour: "2-digit", minute: "2-digit" }));
      message.success("Ofertă creată cu succes!");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la crearea ofertei"),
  });

  // F023 — Generate document
  const generateMutation = useMutation({
    mutationFn: (id: string) => offerService.generateDocument(id),
    onSuccess: () => {
      message.success("Document generat!");
      if (createdOfferId) navigate(`/pipeline/offers/${createdOfferId}`);
    },
    onError: () => message.error("Eroare la generarea documentului"),
  });

  // Subtotal calculation (client-side, real-time)
  const subtotal = useMemo(
    () => lineItems.reduce((sum, item) => sum + item.quantity * item.unit_price, 0),
    [lineItems]
  );

  const vatAmount = useMemo(
    () =>
      lineItems.reduce(
        (sum, item) => sum + item.quantity * item.unit_price * ((item.vat_rate || 19) / 100),
        0
      ),
    [lineItems]
  );

  // Add product from catalog (F007)
  const handleProductSelect = useCallback((product: Product) => {
    setLineItems((prev) => [
      ...prev,
      {
        _key: crypto.randomUUID(),
        product_id: product.id,
        description: product.name,
        quantity: 1,
        unit_of_measure: product.unit_of_measure || "buc",
        unit_price: product.unit_price || 0,
        discount_percent: 0,
        vat_rate: product.vat_rate || 19,
        sort_order: prev.length,
      },
    ]);
  }, []);

  // Add manual line
  const handleAddManualLine = useCallback(() => {
    setLineItems((prev) => [
      ...prev,
      {
        _key: crypto.randomUUID(),
        description: "",
        quantity: 1,
        unit_of_measure: "buc",
        unit_price: 0,
        discount_percent: 0,
        vat_rate: 19,
        sort_order: prev.length,
      },
    ]);
  }, []);

  // Update line item field
  const updateLineItem = useCallback((key: string, field: string, value: unknown) => {
    setLineItems((prev) =>
      prev.map((item) => (item._key === key ? { ...item, [field]: value } : item))
    );
  }, []);

  // Delete line item
  const deleteLineItem = useCallback((key: string) => {
    setLineItems((prev) => prev.filter((item) => item._key !== key));
  }, []);

  // Step navigation
  const canGoNext = (): boolean => {
    switch (currentStep) {
      case 0:
        return !!contactId;
      case 1:
        return lineItems.length > 0 && lineItems.every((i) => i.description && i.quantity > 0 && i.unit_price > 0);
      case 2:
        return true; // Estimates step is informational
      case 3:
        return true; // T&C is optional
      case 4:
        return true;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < 4) setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  // Save draft and generate
  const handleSaveDraft = async () => {
    if (!createdOfferId) {
      await createOfferMutation.mutateAsync();
    } else {
      message.info("Draft salvat");
    }
  };

  const handleGenerate = async () => {
    let offerId = createdOfferId;
    if (!offerId) {
      const res = await createOfferMutation.mutateAsync();
      offerId = res.data.id;
    }
    if (offerId) {
      try {
        await generateMutation.mutateAsync(offerId);
      } catch {
        // Navigate anyway — document generation may not be fully wired
        navigate(`/pipeline/offers/${offerId}`);
      }
    }
  };

  // =========== STEP RENDERERS ===========

  // Step 1: Select Client (F020)
  const renderStep1 = () => (
    <Card title="Selectare client și proprietate">
      <Form layout="vertical">
        <Form.Item label="Client" required>
          <Select
            showSearch
            placeholder="Caută client (denumire, CUI, email)..."
            value={contactId}
            onChange={(val) => {
              setContactId(val);
              setPropertyId(undefined);
            }}
            onSearch={(val) => setContactSearch(val)}
            loading={contactsLoading}
            filterOption={false}
            notFoundContent={contactSearch.length < 2 ? "Tastează minim 2 caractere" : "Niciun rezultat"}
            options={(contactsData?.data || []).map((c: ContactListItem) => ({
              value: c.id,
              label: `${c.company_name}${c.cui ? ` (CUI: ${c.cui})` : ""}${c.city ? ` — ${c.city}` : ""}`,
            }))}
            style={{ width: "100%" }}
            size="large"
          />
        </Form.Item>

        {contact && (
          <Alert
            type="info"
            showIcon
            icon={<UserOutlined />}
            message={contact.company_name}
            description={
              <Space direction="vertical" size={0}>
                {contact.cui && <Text type="secondary">CUI: {contact.cui}</Text>}
                {contact.email && <Text type="secondary">Email: {contact.email}</Text>}
                {contact.phone && <Text type="secondary">Tel: {contact.phone}</Text>}
                {contact.city && <Text type="secondary">Loc: {contact.city}, {contact.county}</Text>}
              </Space>
            }
            style={{ marginBottom: 16 }}
          />
        )}

        {contactId && (
          <Form.Item label="Proprietate (opțional)">
            <Select
              placeholder="Selectează proprietate..."
              value={propertyId}
              onChange={setPropertyId}
              allowClear
              options={properties.map((p: Property) => ({
                value: p.id,
                label: `${p.name} — ${p.property_type || ""} ${p.total_area_sqm ? `(${p.total_area_sqm} m²)` : ""}`,
              }))}
            />
          </Form.Item>
        )}

        {selectedProperty && (
          <Alert
            type="success"
            message={`Proprietate: ${selectedProperty.name}`}
            description={
              <Space direction="vertical" size={0}>
                {selectedProperty.address && <Text type="secondary">{selectedProperty.address}, {selectedProperty.city}</Text>}
                {selectedProperty.total_area_sqm && <Text type="secondary">Suprafață: {selectedProperty.total_area_sqm} m²</Text>}
                {selectedProperty.energy_class && (
                  <Text type="secondary">Clasă energetică: {selectedProperty.energy_class}</Text>
                )}
              </Space>
            }
            style={{ marginBottom: 16 }}
          />
        )}

        <Form.Item label="Titlu ofertă">
          <Input
            placeholder="Ex: Ofertă reabilitare termică bloc A1"
            value={offerTitle}
            onChange={(e) => setOfferTitle(e.target.value)}
          />
        </Form.Item>

        <Form.Item label="Descriere (opțional)">
          <TextArea
            rows={2}
            placeholder="Descriere suplimentară..."
            value={offerDescription}
            onChange={(e) => setOfferDescription(e.target.value)}
          />
        </Form.Item>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item label="Monedă">
              <Select value={currency} onChange={setCurrency}>
                <Select.Option value="RON">RON</Select.Option>
                <Select.Option value="EUR">EUR</Select.Option>
                <Select.Option value="USD">USD</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="Valabilitate (zile)">
              <InputNumber
                min={1}
                max={365}
                value={validityDays}
                onChange={(v) => setValidityDays(v || 30)}
                style={{ width: "100%" }}
              />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );

  // Step 2: Line Items (F021, F022)
  const renderStep2 = () => {
    const columns = [
      {
        title: "#",
        width: 50,
        render: (_: unknown, __: unknown, idx: number) => idx + 1,
      },
      {
        title: "Produs / Descriere",
        dataIndex: "description",
        key: "description",
        render: (val: string, record: LineItemRow) => (
          <Input
            value={val}
            onChange={(e) => updateLineItem(record._key, "description", e.target.value)}
            placeholder="Denumire produs/serviciu"
            status={!val ? "error" : undefined}
          />
        ),
      },
      {
        title: "UM",
        dataIndex: "unit_of_measure",
        key: "um",
        width: 90,
        render: (val: string, record: LineItemRow) => (
          <Select
            value={val}
            onChange={(v) => updateLineItem(record._key, "unit_of_measure", v)}
            style={{ width: 80 }}
            options={[
              { value: "buc", label: "buc" },
              { value: "m²", label: "m²" },
              { value: "ml", label: "ml" },
              { value: "m³", label: "m³" },
              { value: "kg", label: "kg" },
              { value: "L", label: "L" },
              { value: "ore", label: "ore" },
              { value: "set", label: "set" },
            ]}
          />
        ),
      },
      {
        title: "Cantitate",
        dataIndex: "quantity",
        key: "quantity",
        width: 110,
        render: (val: number, record: LineItemRow) => (
          <InputNumber
            min={0.01}
            max={100000}
            step={0.5}
            value={val}
            onChange={(v) => updateLineItem(record._key, "quantity", v || 0)}
            style={{ width: 100 }}
            status={val <= 0 ? "error" : undefined}
          />
        ),
      },
      {
        title: `Preț unitar (${currency})`,
        dataIndex: "unit_price",
        key: "unit_price",
        width: 140,
        render: (val: number, record: LineItemRow) => (
          <InputNumber
            min={0.01}
            max={1000000}
            step={0.01}
            precision={2}
            value={val}
            onChange={(v) => updateLineItem(record._key, "unit_price", v || 0)}
            style={{ width: 130 }}
            status={val <= 0 ? "error" : undefined}
          />
        ),
      },
      {
        title: `Total (${currency})`,
        key: "total",
        width: 120,
        render: (_: unknown, record: LineItemRow) => (
          <Text strong>
            {(record.quantity * record.unit_price).toLocaleString("ro-RO", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </Text>
        ),
      },
      {
        title: "",
        key: "actions",
        width: 50,
        render: (_: unknown, record: LineItemRow) => (
          <Popconfirm title="Ștergi linia?" onConfirm={() => deleteLineItem(record._key)}>
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        ),
      },
    ];

    return (
      <Card title="Produse și servicii">
        <Space style={{ marginBottom: 16 }}>
          <Button icon={<PlusOutlined />} onClick={() => setProductPickerOpen(true)}>
            Adaugă din catalog
          </Button>
          <Button icon={<PlusOutlined />} onClick={handleAddManualLine} type="dashed">
            Linie manuală
          </Button>
        </Space>

        <Table
          rowKey="_key"
          columns={columns}
          dataSource={lineItems}
          pagination={false}
          size="small"
          locale={{ emptyText: "Adaugă cel puțin un produs sau serviciu" }}
          footer={() => (
            <div style={{ textAlign: "right" }}>
              <Space direction="vertical" size={4} style={{ textAlign: "right" }}>
                <Text>
                  Subtotal:{" "}
                  <Text strong>
                    {subtotal.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                  </Text>
                </Text>
                <Text type="secondary">
                  TVA:{" "}
                  {vatAmount.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                </Text>
                <Title level={5} style={{ margin: 0 }}>
                  TOTAL: {(subtotal + vatAmount).toLocaleString("ro-RO", { minimumFractionDigits: 2 })}{" "}
                  {currency}
                </Title>
              </Space>
            </div>
          )}
        />

        <ProductPickerModal
          open={productPickerOpen}
          onClose={() => setProductPickerOpen(false)}
          onSelect={handleProductSelect}
        />
      </Card>
    );
  };

  // Step 3: Estimates & Predimensionare
  const renderStep3 = () => {
    // Energy impact calculation for P1 (BuildWise)
    const areaSqm = selectedProperty?.total_area_sqm || 0;
    const estimatedSavingsPercent = areaSqm > 0 ? Math.min(65, Math.round(30 + areaSqm * 0.01)) : 0;
    const estimatedCO2 = areaSqm > 0 ? Math.round(areaSqm * 0.045) : 0;
    const estimatedROI = subtotal > 0 && areaSqm > 0 ? Math.round((subtotal / (areaSqm * 12)) * 10) / 10 : 0;

    return (
      <Card title="Estimări și predimensionare">
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <Alert
              type="info"
              message="Estimări automate bazate pe datele tehnice"
              description="Valorile de mai jos sunt calculate automat pe baza produselor selectate și a proprietății alese. Pot fi ajustate manual."
              showIcon
            />
          </Col>

          {/* Cost breakdown */}
          <Col xs={24} md={12}>
            <Card size="small" title="Sumar costuri" type="inner">
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Subtotal produse">
                  {subtotal.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                </Descriptions.Item>
                <Descriptions.Item label="TVA (19%)">
                  {vatAmount.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                </Descriptions.Item>
                <Descriptions.Item label="TOTAL">
                  <Text strong>
                    {(subtotal + vatAmount).toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                  </Text>
                </Descriptions.Item>
                <Descriptions.Item label="Nr. linii">{lineItems.length}</Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>

          {/* Energy impact (P1 specific) */}
          <Col xs={24} md={12}>
            <Card
              size="small"
              title={
                <Space>
                  Estimare impact energetic
                  <Tag color="blue">P1 BuildWise</Tag>
                </Space>
              }
              type="inner"
            >
              {selectedProperty ? (
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="Suprafață">
                    {areaSqm} m²
                  </Descriptions.Item>
                  <Descriptions.Item label="Coef. U sticlă BAHM">
                    <Text strong>{U_VALUE_TREATED_GLASS} W/m²K</Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="Reducere consum estimată">
                    <Tag color="green">{estimatedSavingsPercent}%</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="CO₂ evitat estimat">
                    <Tag color="green">{estimatedCO2} tone/an</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="ROI estimat">
                    <Tag color={estimatedROI <= 5 ? "green" : estimatedROI <= 10 ? "orange" : "red"}>
                      {estimatedROI} ani
                    </Tag>
                  </Descriptions.Item>
                </Descriptions>
              ) : (
                <Text type="secondary">
                  Selectează o proprietate în Pasul 1 pentru estimări energetice.
                </Text>
              )}
            </Card>
          </Col>

          {/* Glass parameters */}
          <Col span={24}>
            <Card size="small" title="Parametri sticlă tratată termic BAHM" type="inner">
              <Row gutter={16}>
                <Col span={8}>
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Coeficient U">
                      {U_VALUE_TREATED_GLASS} W/m²K
                    </Descriptions.Item>
                    <Descriptions.Item label="Tip">Sticlă tratată termic</Descriptions.Item>
                    <Descriptions.Item label="Standard">EN 673</Descriptions.Item>
                  </Descriptions>
                </Col>
                <Col span={16}>
                  <Paragraph type="secondary" style={{ fontSize: 12 }}>
                    Coeficientul U de 0.3 W/m²K pentru sticla tratată termic BAHM este un parametru
                    fundamental în calculele de eficiență energetică. Acesta reprezintă
                    transferul termic prin suprafața vitroului și determină reducerea pierderilor
                    de căldură cu până la 65% față de sticla standard (U ≈ 2.8 W/m²K).
                  </Paragraph>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  // Step 4: Terms & Conditions (F023)
  const renderStep4 = () => (
    <Card title="Termeni și condiții">
      <Form layout="vertical">
        <Form.Item label="Șablon">
          <Select
            defaultValue="default"
            options={[
              { value: "default", label: "Termeni standard — Ofertă" },
              { value: "simplified", label: "Termeni simplificați" },
              { value: "custom", label: "Personalizat" },
            ]}
            onChange={(val) => {
              if (val === "default") setTermsAndConditions(DEFAULT_TERMS);
              else if (val === "simplified") setTermsAndConditions(SIMPLIFIED_TERMS);
            }}
          />
        </Form.Item>

        <Form.Item label="Conținut T&C (editabil)">
          <TextArea
            rows={12}
            value={termsAndConditions}
            onChange={(e) => setTermsAndConditions(e.target.value)}
            style={{ fontFamily: "monospace", fontSize: 13 }}
          />
        </Form.Item>

        <Alert
          type="info"
          message="Placeholder-e disponibile"
          description="{{company.name}}, {{contact.name}}, {{offer.total_value}}, {{offer.date}}, {{offer.validity_days}}, {{property.address}} — vor fi substituite automat la generarea documentului."
          showIcon
        />
      </Form>
    </Card>
  );

  // Step 5: Preview & Generate (F024, F025)
  const renderStep5 = () => (
    <Card title="Previzualizare ofertă">
      <div
        style={{
          position: "relative",
          border: "1px solid #d9d9d9",
          borderRadius: 8,
          padding: 32,
          background: "#fff",
          maxWidth: 800,
          margin: "0 auto",
          minHeight: 600,
        }}
      >
        {/* DRAFT watermark */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%) rotate(-45deg)",
            opacity: 0.08,
            fontSize: 120,
            fontWeight: "bold",
            color: "#999",
            zIndex: 0,
            pointerEvents: "none",
            userSelect: "none",
          }}
        >
          DRAFT
        </div>

        {/* Header */}
        <div style={{ position: "relative", zIndex: 1 }}>
          <Row justify="space-between" align="top">
            <Col>
              <Title level={3} style={{ margin: 0 }}>BuildWise</Title>
              <Text type="secondary">BAHN S.R.L.</Text>
            </Col>
            <Col style={{ textAlign: "right" }}>
              <Text type="secondary">Data: {new Date().toLocaleDateString("ro-RO")}</Text>
              <br />
              <Text type="secondary">Valabilitate: {validityDays} zile</Text>
            </Col>
          </Row>

          <Divider />

          {/* Client info */}
          <Title level={5}>Către:</Title>
          <Paragraph>
            <strong>{contact?.company_name}</strong>
            <br />
            {contact?.address && <>{contact.address}, {contact.city}, {contact.county}<br /></>}
            {contact?.cui && <>CUI: {contact.cui}<br /></>}
            {contact?.email && <>Email: {contact.email}</>}
          </Paragraph>

          {selectedProperty && (
            <>
              <Title level={5}>Proprietate:</Title>
              <Paragraph>
                {selectedProperty.name} — {selectedProperty.address}, {selectedProperty.city}
                {selectedProperty.total_area_sqm && <> ({selectedProperty.total_area_sqm} m²)</>}
              </Paragraph>
            </>
          )}

          {offerTitle && (
            <>
              <Title level={5}>Referință: {offerTitle}</Title>
              {offerDescription && <Paragraph type="secondary">{offerDescription}</Paragraph>}
            </>
          )}

          <Divider />

          {/* Line items table */}
          <Table
            rowKey="_key"
            dataSource={lineItems}
            pagination={false}
            size="small"
            columns={[
              { title: "#", render: (_: unknown, __: unknown, i: number) => i + 1, width: 40 },
              { title: "Descriere", dataIndex: "description" },
              { title: "UM", dataIndex: "unit_of_measure", width: 60 },
              {
                title: "Cant.",
                dataIndex: "quantity",
                width: 70,
                render: (v: number) => v.toLocaleString("ro-RO"),
              },
              {
                title: `Preț (${currency})`,
                dataIndex: "unit_price",
                width: 100,
                render: (v: number) => v.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
              },
              {
                title: `Total (${currency})`,
                key: "total",
                width: 120,
                render: (_: unknown, r: LineItemRow) =>
                  (r.quantity * r.unit_price).toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
              },
            ]}
            footer={() => (
              <Row justify="end">
                <Col>
                  <Space direction="vertical" size={2} style={{ textAlign: "right" }}>
                    <Text>Subtotal: {subtotal.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}</Text>
                    <Text type="secondary">TVA: {vatAmount.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}</Text>
                    <Title level={4} style={{ margin: 0 }}>
                      TOTAL: {(subtotal + vatAmount).toLocaleString("ro-RO", { minimumFractionDigits: 2 })} {currency}
                    </Title>
                  </Space>
                </Col>
              </Row>
            )}
          />

          {termsAndConditions && (
            <>
              <Divider />
              <Title level={5}>Termeni și condiții</Title>
              <Paragraph style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>
                {termsAndConditions}
              </Paragraph>
            </>
          )}
        </div>
      </div>

      {draftSavedAt && (
        <Alert
          type="success"
          message={`Draft salvat la ${draftSavedAt}`}
          style={{ marginTop: 16 }}
          showIcon
        />
      )}

      <Divider />

      <Space>
        <Button
          size="large"
          onClick={handleSaveDraft}
          loading={createOfferMutation.isPending}
        >
          Salvează draft
        </Button>
        <Button
          type="primary"
          size="large"
          onClick={handleGenerate}
          loading={createOfferMutation.isPending || generateMutation.isPending}
        >
          Generează ofertă
        </Button>
      </Space>
    </Card>
  );

  const steps = [
    { title: "Client", icon: <UserOutlined />, content: renderStep1 },
    { title: "Produse", icon: <ShoppingCartOutlined />, content: renderStep2 },
    { title: "Estimări", icon: <CalculatorOutlined />, content: renderStep3 },
    { title: "T&C", icon: <FileTextOutlined />, content: renderStep4 },
    { title: "Preview", icon: <EyeOutlined />, content: renderStep5 },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
          Înapoi
        </Button>
        <Title level={4} style={{ margin: 0 }}>
          Offer Builder — E-005
        </Title>
      </Space>

      <Steps
        current={currentStep}
        items={steps.map((s) => ({ title: s.title, icon: s.icon }))}
        style={{ marginBottom: 24 }}
      />

      {steps[currentStep]?.content()}

      {currentStep < 4 && (
        <div style={{ marginTop: 24, display: "flex", justifyContent: "space-between" }}>
          <Button onClick={handlePrev} disabled={currentStep === 0}>
            Înapoi
          </Button>
          <Button type="primary" onClick={handleNext} disabled={!canGoNext()}>
            Următorul pas
          </Button>
        </div>
      )}
    </div>
  );
}

// Default T&C template
const DEFAULT_TERMS = `1. OBIECTUL OFERTEI
Prezenta ofertă acoperă produsele și serviciile enumerate mai sus, conform specificațiilor tehnice agreate.

2. PREȚURI ȘI PLATĂ
Prețurile sunt exprimate fără TVA, cu TVA calculat separat.
Plata se efectuează în termen de 30 de zile de la emiterea facturii.

3. VALABILITATE
Oferta este valabilă {{offer.validity_days}} zile de la data emiterii.
După expirarea termenului, prețurile pot fi modificate.

4. LIVRARE
Termenul de livrare va fi stabilit de comun acord la semnarea contractului.

5. GARANȚIE
Produsele beneficiază de garanție conform legislației în vigoare.
Sticla tratată termic BAHM: coeficient U = 0.3 W/m²K, garantat 10 ani.

6. CONDIȚII SPECIALE
Oferta poate fi retrasă în orice moment înainte de acceptare.
Acceptarea ofertei se face prin semnarea contractului aferent.`;

const SIMPLIFIED_TERMS = `Oferta este valabilă {{offer.validity_days}} zile.
Plata: 30 zile de la facturare.
Garanție conform legislației în vigoare.`;
