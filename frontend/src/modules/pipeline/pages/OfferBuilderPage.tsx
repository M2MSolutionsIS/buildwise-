import { useState, useEffect, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Typography,
  Steps,
  Button,
  Card,
  Row,
  Col,
  Input,
  Select,
  Table,
  InputNumber,
  Space,
  Alert,
  Divider,
  Form,
  Descriptions,
  Statistic,
  App,
} from "antd";
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  FilePdfOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { useCreateOffer } from "../hooks/useOffers";
import { offerService } from "../services/offerService";
import ProductPickerModal from "../components/ProductPickerModal";
import type {
  OfferLineItemCreate,
  OfferWizardDraft,
  Product,
  OfferEstimation,
} from "../../../types/pipeline";
import type { ContactListItem, Property } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const DRAFT_KEY = "buildwise_offer_wizard_draft";
const U_VALUE_GLASS = 0.3; // W/m²K — coeficient U sticlă tratată termic BAHM

const INITIAL_DRAFT: OfferWizardDraft = {
  current_step: 0,
  line_items: [],
  currency: "RON",
  validity_days: 30,
};

function loadDraft(): OfferWizardDraft {
  try {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) return JSON.parse(saved);
  } catch {
    // ignore
  }
  return { ...INITIAL_DRAFT };
}

function saveDraft(draft: OfferWizardDraft) {
  localStorage.setItem(
    DRAFT_KEY,
    JSON.stringify({ ...draft, saved_at: new Date().toISOString() })
  );
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
}

export default function OfferBuilderPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { message } = App.useApp();
  const createOffer = useCreateOffer();

  const [draft, setDraft] = useState<OfferWizardDraft>(loadDraft);
  const [productPickerOpen, setProductPickerOpen] = useState(false);
  const [contactSearch, setContactSearch] = useState("");
  const [debouncedContactSearch, setDebouncedContactSearch] = useState("");

  // Pre-populate from URL params (coming from Contact Detail or Pipeline)
  useEffect(() => {
    const contactId = searchParams.get("contact_id");
    const contactName = searchParams.get("contact_name");
    const opportunityId = searchParams.get("opportunity_id");
    if (contactId && !draft.contact_id) {
      setDraft((d) => ({
        ...d,
        contact_id: contactId,
        contact_name: contactName || undefined,
        opportunity_id: opportunityId || undefined,
      }));
    }
  }, [searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-save draft on changes
  useEffect(() => {
    saveDraft(draft);
  }, [draft]);

  const updateDraft = useCallback(
    (updates: Partial<OfferWizardDraft>) => {
      setDraft((d) => ({ ...d, ...updates }));
    },
    []
  );

  // Contact search with debounce
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedContactSearch(contactSearch), 300);
    return () => clearTimeout(timer);
  }, [contactSearch]);

  const { data: contactsData } = useQuery({
    queryKey: ["contacts-search", debouncedContactSearch],
    queryFn: () => offerService.searchContacts(debouncedContactSearch),
    enabled: debouncedContactSearch.length >= 2,
  });

  const { data: propertiesData } = useQuery({
    queryKey: ["contact-properties", draft.contact_id],
    queryFn: () => offerService.getContactProperties(draft.contact_id!),
    enabled: !!draft.contact_id,
  });

  const contacts: ContactListItem[] = contactsData?.data || [];
  const properties: Property[] = propertiesData?.data || [];

  // ── Step navigation ──
  const currentStep = draft.current_step;

  const canGoNext = (): boolean => {
    switch (currentStep) {
      case 0:
        return !!draft.contact_id;
      case 1:
        return draft.line_items.length > 0;
      case 2:
        return true;
      case 3:
        return true;
      case 4:
        return !!draft.title && draft.line_items.length > 0;
      default:
        return false;
    }
  };

  const goNext = () => {
    if (currentStep < 4) {
      updateDraft({ current_step: currentStep + 1 });
    }
  };

  const goBack = () => {
    if (currentStep > 0) {
      updateDraft({ current_step: currentStep - 1 });
    }
  };

  // ── Line items management ──
  const addLineItem = (item: OfferLineItemCreate) => {
    updateDraft({
      line_items: [...draft.line_items, { ...item, sort_order: draft.line_items.length }],
    });
  };

  const updateLineItem = (index: number, updates: Partial<OfferLineItemCreate>) => {
    const items = [...draft.line_items];
    items[index] = { ...items[index], ...updates } as OfferLineItemCreate;
    updateDraft({ line_items: items });
  };

  const removeLineItem = (index: number) => {
    updateDraft({ line_items: draft.line_items.filter((_, i) => i !== index) });
  };

  const handleProductSelect = (product: Product) => {
    addLineItem({
      product_id: product.id,
      description: product.name,
      quantity: 1,
      unit_of_measure: product.unit_of_measure,
      unit_price: product.unit_price,
      discount_percent: 0,
      vat_rate: 0.19,
    });
  };

  const addManualLine = () => {
    addLineItem({
      description: "",
      quantity: 1,
      unit_of_measure: "buc",
      unit_price: 0,
      discount_percent: 0,
      vat_rate: 0.19,
    });
  };

  // ── Financial calculations ──
  const subtotal = draft.line_items.reduce((sum, item) => {
    const lineTotal = item.quantity * item.unit_price * (1 - (item.discount_percent || 0) / 100);
    return sum + lineTotal;
  }, 0);

  const vatAmount = subtotal * 0.19;
  const totalAmount = subtotal + vatAmount;

  // ── Surface & energy calculations (P1) ──
  const selectedProperty = properties.find((p) => p.id === draft.property_id);
  const estimation: OfferEstimation | null = selectedProperty
    ? {
        surface_calculation: {
          total_surface_sqm: selectedProperty.total_area_sqm || 0,
          glass_surface_sqm: (selectedProperty.total_area_sqm || 0) * 0.25,
          u_value: U_VALUE_GLASS,
          energy_loss_before: (selectedProperty.total_area_sqm || 0) * 0.25 * 1.1 * 24 * 180 / 1000,
          energy_loss_after: (selectedProperty.total_area_sqm || 0) * 0.25 * U_VALUE_GLASS * 24 * 180 / 1000,
        },
        energy_savings_percent:
          selectedProperty.total_area_sqm
            ? Math.round(((1.1 - U_VALUE_GLASS) / 1.1) * 100)
            : undefined,
        co2_reduction_kg:
          selectedProperty.total_area_sqm
            ? Math.round(
                ((selectedProperty.total_area_sqm * 0.25 * (1.1 - U_VALUE_GLASS) * 24 * 180) / 1000) * 0.233
              )
            : undefined,
        roi_months: totalAmount > 0 ? Math.round((totalAmount / (subtotal * 0.15)) * 12) : undefined,
        cost_breakdown: {
          materials: subtotal * 0.6,
          labor: subtotal * 0.3,
          overhead: subtotal * 0.1,
          total: subtotal,
        },
      }
    : null;

  // ── Submit offer ──
  const handleCreateOffer = async () => {
    if (!draft.contact_id || !draft.title) {
      message.warning("Completați câmpurile obligatorii.");
      return;
    }

    try {
      const result = await createOffer.mutateAsync({
        contact_id: draft.contact_id,
        opportunity_id: draft.opportunity_id,
        property_id: draft.property_id,
        title: draft.title,
        description: draft.description,
        currency: draft.currency,
        validity_days: draft.validity_days,
        terms_and_conditions: draft.terms_and_conditions,
        line_items: draft.line_items,
      });

      clearDraft();
      navigate(`/pipeline/offers/${result.data.id}`);
    } catch {
      // error handled by mutation
    }
  };

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("ro-RO", { style: "currency", currency: draft.currency }).format(value);

  // ── Line items table columns ──
  const lineItemColumns: ColumnsType<OfferLineItemCreate & { _index: number }> = [
    {
      title: "#",
      key: "index",
      width: 50,
      render: (_: unknown, __: unknown, idx: number) => idx + 1,
    },
    {
      title: "Descriere produs",
      dataIndex: "description",
      key: "description",
      render: (val: string, _: unknown, idx: number) => (
        <Input
          value={val}
          placeholder="Descriere..."
          onChange={(e) => updateLineItem(idx, { description: e.target.value })}
        />
      ),
    },
    {
      title: "UM",
      dataIndex: "unit_of_measure",
      key: "unit_of_measure",
      width: 80,
      render: (val: string, _: unknown, idx: number) => (
        <Input
          value={val}
          onChange={(e) => updateLineItem(idx, { unit_of_measure: e.target.value })}
        />
      ),
    },
    {
      title: "Cantitate",
      dataIndex: "quantity",
      key: "quantity",
      width: 100,
      render: (val: number, _: unknown, idx: number) => (
        <InputNumber
          value={val}
          min={0.01}
          style={{ width: "100%" }}
          onChange={(v) => updateLineItem(idx, { quantity: v || 0 })}
        />
      ),
    },
    {
      title: "Preț unitar",
      dataIndex: "unit_price",
      key: "unit_price",
      width: 130,
      render: (val: number, _: unknown, idx: number) => (
        <InputNumber
          value={val}
          min={0}
          style={{ width: "100%" }}
          addonAfter={draft.currency}
          onChange={(v) => updateLineItem(idx, { unit_price: v || 0 })}
        />
      ),
    },
    {
      title: "Discount %",
      dataIndex: "discount_percent",
      key: "discount_percent",
      width: 100,
      render: (val: number, _: unknown, idx: number) => (
        <InputNumber
          value={val}
          min={0}
          max={100}
          style={{ width: "100%" }}
          addonAfter="%"
          onChange={(v) => updateLineItem(idx, { discount_percent: v || 0 })}
        />
      ),
    },
    {
      title: "Total",
      key: "total",
      width: 130,
      align: "right",
      render: (_: unknown, record: OfferLineItemCreate) => {
        const total =
          record.quantity * record.unit_price * (1 - (record.discount_percent || 0) / 100);
        return <Typography.Text strong>{formatCurrency(total)}</Typography.Text>;
      },
    },
    {
      title: "",
      key: "actions",
      width: 50,
      render: (_: unknown, __: unknown, idx: number) => (
        <Button
          type="text"
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeLineItem(idx)}
        />
      ),
    },
  ];

  // ── Step content renderers ──
  const renderStep0 = () => (
    <Card title="Selectare Client">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Typography.Text strong>Client *</Typography.Text>
          {draft.contact_id ? (
            <div style={{ marginTop: 8 }}>
              <Alert
                message={`Client selectat: ${draft.contact_name || draft.contact_id}`}
                type="success"
                showIcon
                action={
                  <Button
                    size="small"
                    onClick={() =>
                      updateDraft({
                        contact_id: undefined,
                        contact_name: undefined,
                        property_id: undefined,
                      })
                    }
                  >
                    Schimbă
                  </Button>
                }
              />
            </div>
          ) : (
            <Select
              showSearch
              placeholder="Caută client (denumire, CUI, email)..."
              filterOption={false}
              onSearch={setContactSearch}
              onChange={(value, option: any) => {
                updateDraft({
                  contact_id: value,
                  contact_name: option?.label,
                });
              }}
              style={{ width: "100%", marginTop: 8 }}
              suffixIcon={<SearchOutlined />}
              options={contacts.map((c) => ({
                value: c.id,
                label: c.company_name,
                description: [c.cui, c.email].filter(Boolean).join(" · "),
              }))}
              optionRender={(option) => (
                <Space direction="vertical" size={0}>
                  <Typography.Text>{option.label}</Typography.Text>
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {(option.data as any).description}
                  </Typography.Text>
                </Space>
              )}
              notFoundContent={
                contactSearch.length < 2
                  ? "Introduceți min. 2 caractere"
                  : "Niciun client găsit"
              }
            />
          )}
        </Col>

        {draft.contact_id && properties.length > 0 && (
          <Col span={24}>
            <Typography.Text strong>Proprietate (opțional)</Typography.Text>
            <Select
              placeholder="Selectează proprietate..."
              allowClear
              value={draft.property_id}
              onChange={(value) => {
                const prop = properties.find((p) => p.id === value);
                updateDraft({
                  property_id: value,
                  property_name: prop?.name,
                });
              }}
              style={{ width: "100%", marginTop: 8 }}
              options={properties.map((p) => ({
                value: p.id,
                label: `${p.name} — ${p.property_type} ${p.total_area_sqm ? `(${p.total_area_sqm} m²)` : ""}`,
              }))}
            />
          </Col>
        )}

        <Col span={12}>
          <Typography.Text strong>Titlu ofertă *</Typography.Text>
          <Input
            value={draft.title || ""}
            placeholder="ex: Ofertă renovare termică apartament"
            onChange={(e) => updateDraft({ title: e.target.value })}
            style={{ marginTop: 8 }}
          />
        </Col>
        <Col span={6}>
          <Typography.Text strong>Monedă</Typography.Text>
          <Select
            value={draft.currency}
            onChange={(v) => updateDraft({ currency: v })}
            style={{ width: "100%", marginTop: 8 }}
            options={[
              { value: "RON", label: "RON" },
              { value: "EUR", label: "EUR" },
              { value: "USD", label: "USD" },
            ]}
          />
        </Col>
        <Col span={6}>
          <Typography.Text strong>Valabilitate (zile)</Typography.Text>
          <InputNumber
            value={draft.validity_days}
            min={1}
            max={365}
            style={{ width: "100%", marginTop: 8 }}
            onChange={(v) => updateDraft({ validity_days: v || 30 })}
          />
        </Col>
      </Row>
    </Card>
  );

  const renderStep1 = () => (
    <Card
      title="Line Items — Produse și servicii"
      extra={
        <Space>
          <Button icon={<PlusOutlined />} onClick={() => setProductPickerOpen(true)}>
            Adaugă din catalog
          </Button>
          <Button onClick={addManualLine}>Linie manuală</Button>
        </Space>
      }
    >
      <Table
        rowKey={(_, idx) => String(idx)}
        columns={lineItemColumns}
        dataSource={draft.line_items.map((item, i) => ({ ...item, _index: i }))}
        pagination={false}
        size="small"
        scroll={{ x: 900 }}
        locale={{ emptyText: "Adăugați produse din catalog sau linii manuale" }}
        footer={() => (
          <Row justify="end">
            <Col>
              <Descriptions column={1} size="small" style={{ width: 300 }}>
                <Descriptions.Item label="Subtotal">
                  <Typography.Text strong>{formatCurrency(subtotal)}</Typography.Text>
                </Descriptions.Item>
                <Descriptions.Item label="TVA (19%)">
                  {formatCurrency(vatAmount)}
                </Descriptions.Item>
                <Descriptions.Item label="Total">
                  <Typography.Title level={4} style={{ margin: 0 }}>
                    {formatCurrency(totalAmount)}
                  </Typography.Title>
                </Descriptions.Item>
              </Descriptions>
            </Col>
          </Row>
        )}
      />

      <ProductPickerModal
        open={productPickerOpen}
        onClose={() => setProductPickerOpen(false)}
        onSelect={handleProductSelect}
      />
    </Card>
  );

  const renderStep2 = () => (
    <Card title="Estimări & Predimensionare">
      {selectedProperty ? (
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <Alert
              message={`Proprietate: ${selectedProperty.name} — ${selectedProperty.total_area_sqm || "?"} m²`}
              type="info"
              showIcon
            />
          </Col>

          <Col span={24}>
            <Typography.Title level={5}>
              Calculator suprafețe sticlă (U = {U_VALUE_GLASS} W/m²K)
            </Typography.Title>
            <Divider />
          </Col>

          {estimation?.surface_calculation && (
            <>
              <Col xs={12} md={6}>
                <Statistic
                  title="Suprafață totală"
                  value={estimation.surface_calculation.total_surface_sqm}
                  suffix="m²"
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Suprafață sticlă (est. 25%)"
                  value={estimation.surface_calculation.glass_surface_sqm}
                  suffix="m²"
                  precision={1}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Coeficient U sticlă"
                  value={estimation.surface_calculation.u_value}
                  suffix="W/m²K"
                  precision={1}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Pierdere energie ÎNAINTE"
                  value={estimation.surface_calculation.energy_loss_before}
                  suffix="kWh/an"
                  precision={0}
                  valueStyle={{ color: "#ff4d4f" }}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Pierdere energie DUPĂ"
                  value={estimation.surface_calculation.energy_loss_after}
                  suffix="kWh/an"
                  precision={0}
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Economie energie"
                  value={estimation.energy_savings_percent}
                  suffix="%"
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="Reducere CO₂"
                  value={estimation.co2_reduction_kg}
                  suffix="kg/an"
                  valueStyle={{ color: "#52c41a" }}
                />
              </Col>
              <Col xs={12} md={6}>
                <Statistic
                  title="ROI estimat"
                  value={estimation.roi_months}
                  suffix="luni"
                />
              </Col>
            </>
          )}

          <Col span={24}>
            <Divider />
            <Typography.Title level={5}>Defalcare costuri</Typography.Title>
          </Col>
          {estimation?.cost_breakdown && (
            <>
              <Col xs={8} md={6}>
                <Statistic title="Materiale (60%)" value={estimation.cost_breakdown.materials} prefix={draft.currency} precision={0} />
              </Col>
              <Col xs={8} md={6}>
                <Statistic title="Manoperă (30%)" value={estimation.cost_breakdown.labor} prefix={draft.currency} precision={0} />
              </Col>
              <Col xs={8} md={6}>
                <Statistic title="Overhead (10%)" value={estimation.cost_breakdown.overhead} prefix={draft.currency} precision={0} />
              </Col>
            </>
          )}
        </Row>
      ) : (
        <Alert
          message="Selectați o proprietate în Step 1 pentru estimări energetice"
          description={
            <>
              Fără proprietate selectată, estimările sunt disponibile doar ca defalcare costuri simplificată.
              <Divider />
              <Row gutter={16}>
                <Col xs={8}>
                  <Statistic title="Materiale (60%)" value={subtotal * 0.6} prefix={draft.currency} precision={0} />
                </Col>
                <Col xs={8}>
                  <Statistic title="Manoperă (30%)" value={subtotal * 0.3} prefix={draft.currency} precision={0} />
                </Col>
                <Col xs={8}>
                  <Statistic title="Overhead (10%)" value={subtotal * 0.1} prefix={draft.currency} precision={0} />
                </Col>
              </Row>
            </>
          }
          type="warning"
          showIcon
        />
      )}
    </Card>
  );

  const renderStep3 = () => (
    <Card title="Termeni și Condiții">
      <Form layout="vertical">
        <Form.Item label="Template T&C">
          <Select
            placeholder="Selectează template..."
            allowClear
            style={{ width: "100%" }}
            onChange={(value) => {
              if (value === "standard") {
                updateDraft({
                  terms_and_conditions:
                    "1. Valabilitate ofertă: {{validity_days}} zile de la data emiterii.\n" +
                    "2. Plata: 50% avans, 50% la livrare.\n" +
                    "3. Termen execuție: conform grafic agreat.\n" +
                    "4. Garanție: 24 luni de la recepție.\n" +
                    "5. Coeficient U sticlă tratată termic: 0.3 W/m²K (conform standard BAHM).\n" +
                    "6. Prețurile nu includ TVA.",
                });
              } else if (value === "minimal") {
                updateDraft({
                  terms_and_conditions:
                    "1. Valabilitate: {{validity_days}} zile.\n2. Plata: conform facturii.\n3. Garanție: conform legislație.",
                });
              }
            }}
            options={[
              { value: "standard", label: "Template Standard" },
              { value: "minimal", label: "Template Minimal" },
            ]}
          />
        </Form.Item>
        <Form.Item label="Conținut T&C">
          <Input.TextArea
            rows={10}
            value={draft.terms_and_conditions || ""}
            onChange={(e) => updateDraft({ terms_and_conditions: e.target.value })}
            placeholder="Introduceți termeni și condiții..."
          />
        </Form.Item>
      </Form>
    </Card>
  );

  const renderStep4 = () => (
    <Card title="Preview ofertă">
      <div
        style={{
          position: "relative",
          border: "1px solid #d9d9d9",
          padding: 32,
          background: "#fff",
          minHeight: 400,
        }}
      >
        {/* DRAFT watermark */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%) rotate(-30deg)",
            fontSize: 80,
            fontWeight: 700,
            color: "rgba(0,0,0,0.06)",
            pointerEvents: "none",
            userSelect: "none",
            zIndex: 1,
          }}
        >
          DRAFT
        </div>

        <div style={{ position: "relative", zIndex: 2 }}>
          <Row justify="space-between" align="top">
            <Col>
              <Typography.Title level={3}>OFERTĂ</Typography.Title>
              <Typography.Text type="secondary">
                Client: {draft.contact_name || "—"}
              </Typography.Text>
              <br />
              {draft.property_name && (
                <Typography.Text type="secondary">
                  Proprietate: {draft.property_name}
                </Typography.Text>
              )}
            </Col>
            <Col style={{ textAlign: "right" }}>
              <Typography.Text type="secondary">Data: {new Date().toLocaleDateString("ro-RO")}</Typography.Text>
              <br />
              <Typography.Text type="secondary">
                Valabilitate: {draft.validity_days} zile
              </Typography.Text>
            </Col>
          </Row>

          <Typography.Title level={4} style={{ marginTop: 16 }}>
            {draft.title}
          </Typography.Title>

          <Divider />

          <Table
            rowKey={(_, idx) => String(idx)}
            columns={[
              { title: "#", key: "idx", width: 40, render: (_, __, i) => i + 1 },
              { title: "Descriere", dataIndex: "description", key: "desc" },
              { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 60 },
              { title: "Cantitate", dataIndex: "quantity", key: "qty", width: 80, align: "right" as const },
              {
                title: "Preț unitar",
                dataIndex: "unit_price",
                key: "price",
                width: 110,
                align: "right" as const,
                render: (v: number) => formatCurrency(v),
              },
              {
                title: "Total",
                key: "total",
                width: 120,
                align: "right" as const,
                render: (_: unknown, r: OfferLineItemCreate) =>
                  formatCurrency(r.quantity * r.unit_price * (1 - (r.discount_percent || 0) / 100)),
              },
            ]}
            dataSource={draft.line_items}
            pagination={false}
            size="small"
          />

          <Row justify="end" style={{ marginTop: 16 }}>
            <Col>
              <Descriptions column={1} size="small" style={{ width: 280 }}>
                <Descriptions.Item label="Subtotal">
                  {formatCurrency(subtotal)}
                </Descriptions.Item>
                <Descriptions.Item label="TVA (19%)">
                  {formatCurrency(vatAmount)}
                </Descriptions.Item>
                <Descriptions.Item label={<Typography.Text strong>TOTAL</Typography.Text>}>
                  <Typography.Text strong style={{ fontSize: 16 }}>
                    {formatCurrency(totalAmount)}
                  </Typography.Text>
                </Descriptions.Item>
              </Descriptions>
            </Col>
          </Row>

          {draft.terms_and_conditions && (
            <>
              <Divider />
              <Typography.Title level={5}>Termeni și Condiții</Typography.Title>
              <Typography.Paragraph style={{ whiteSpace: "pre-line" }}>
                {draft.terms_and_conditions.replace(
                  /\{\{validity_days\}\}/g,
                  String(draft.validity_days)
                )}
              </Typography.Paragraph>
            </>
          )}
        </div>
      </div>
    </Card>
  );

  const stepContent = [renderStep0, renderStep1, renderStep2, renderStep3, renderStep4];

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/pipeline/offers")}>
            Înapoi la oferte
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Ofertă nouă
          </Typography.Title>
        </Space>
        {draft.saved_at && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            Draft salvat la{" "}
            {new Date(draft.saved_at).toLocaleTimeString("ro-RO", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </Typography.Text>
        )}
      </Row>

      <Steps
        current={currentStep}
        style={{ marginBottom: 24 }}
        items={[
          { title: "Client" },
          { title: "Produse" },
          { title: "Estimări" },
          { title: "T&C" },
          { title: "Preview" },
        ]}
      />

      {stepContent[currentStep]?.()}

      <Row justify="space-between" style={{ marginTop: 24 }}>
        <Col>
          {currentStep > 0 && (
            <Button icon={<ArrowLeftOutlined />} onClick={goBack}>
              Înapoi
            </Button>
          )}
        </Col>
        <Col>
          <Space>
            <Button
              icon={<SaveOutlined />}
              onClick={() => {
                saveDraft(draft);
                message.success("Draft salvat.");
              }}
            >
              Salvează draft
            </Button>
            {currentStep < 4 ? (
              <Button type="primary" disabled={!canGoNext()} onClick={goNext}>
                Următorul <ArrowRightOutlined />
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<FilePdfOutlined />}
                loading={createOffer.isPending}
                disabled={!draft.title || draft.line_items.length === 0}
                onClick={handleCreateOffer}
              >
                Creează ofertă
              </Button>
            )}
          </Space>
        </Col>
      </Row>
    </>
  );
}
