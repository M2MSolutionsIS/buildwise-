/**
 * E-028: Technical Data Energy — F010, F012, F016, F018
 * P1-specific: Energy parameters, HVAC, surface calculator, measurement history per property.
 * Connected to /api/v1/crm/properties/:id/energy-profile
 */
import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Form,
  InputNumber,
  Select,
  Space,
  Tag,
  App,
  Tabs,
  Divider,
  Descriptions,
  Progress,
} from "antd";
import {
  ThunderboltOutlined,
  FireOutlined,
  HomeOutlined,
  CalculatorOutlined,
  HistoryOutlined,
  SaveOutlined,
  ExperimentOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../services/api";
import type { ApiResponse } from "../../../types";
import { SkeletonKPI } from "../../../components/SkeletonLoaders";

const { Title, Text } = Typography;

interface EnergyProfile {
  id: string;
  property_id: string;
  energy_class?: string;
  annual_kwh?: number;
  annual_gas_mc?: number;
  annual_co2_kg?: number;
  u_value_walls?: number;
  u_value_windows?: number;
  u_value_roof?: number;
  u_value_floor?: number;
  u_value_avg?: number;
  heating_system?: string;
  cooling_system?: string;
  ventilation_type?: string;
  renewable_sources?: string[];
  total_area_sqm?: number;
  heated_area_sqm?: number;
  glazed_area_sqm?: number;
  measurements?: EnergyMeasurement[];
  created_at: string;
  updated_at?: string;
}

interface EnergyMeasurement {
  id: string;
  date: string;
  type: string;
  value: number;
  unit: string;
  notes?: string;
}

const ENERGY_CLASSES = ["A+", "A", "B", "C", "D", "E", "F", "G"];
const HEATING_SYSTEMS = ["centrala_gaz", "centrala_electrica", "pompa_caldura", "calorifere", "pardoseala", "soba"];
const COOLING_SYSTEMS = ["aer_conditionat", "chiller", "ventilatie_naturala", "fara"];
const VENTILATION_TYPES = ["naturala", "mecanica", "recuperare_caldura", "mixta"];

export default function TechnicalDataEnergyPage() {
  const { propertyId } = useParams<{ propertyId: string }>();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState("overview");

  const { data, isLoading } = useQuery({
    queryKey: ["energy-profile", propertyId],
    queryFn: async (): Promise<ApiResponse<EnergyProfile>> => {
      const { data } = await api.get(`/crm/properties/${propertyId}/energy-profile`);
      return data;
    },
    enabled: !!propertyId,
  });

  const profile = data?.data;

  const updateMut = useMutation({
    mutationFn: async (payload: Partial<EnergyProfile>) => {
      const { data } = await api.put(`/crm/properties/${propertyId}/energy-profile`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["energy-profile", propertyId] });
      message.success("Profil energetic actualizat");
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const getEnergyClassColor = (cls?: string) => {
    const colors: Record<string, string> = {
      "A+": "#52c41a", A: "#73d13d", B: "#95de64", C: "#fadb14",
      D: "#faad14", E: "#fa8c16", F: "#f5222d", G: "#a8071a",
    };
    return colors[cls || ""] || "#999";
  };

  // Surface calculator
  const [calcWalls, setCalcWalls] = useState(0);
  const [calcWindows, setCalcWindows] = useState(0);
  const [calcRoof, setCalcRoof] = useState(0);
  const [calcFloor, setCalcFloor] = useState(0);

  const totalSurface = calcWalls + calcWindows + calcRoof + calcFloor;
  const glazingRatio = totalSurface > 0 ? ((calcWindows / totalSurface) * 100).toFixed(1) : "0";

  if (isLoading) return <SkeletonKPI count={4} />;

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <ThunderboltOutlined style={{ fontSize: 20, color: "#F59E0B" }} />
        <Title level={4} style={{ margin: 0 }}>Date Tehnice Energetice</Title>
        <Tag color="orange">P1 — Eficiență Energetică</Tag>
      </Space>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "overview",
            label: "Prezentare generală",
            children: (
              <>
                {/* KPI Cards */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col xs={12} md={6}>
                    <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                      <Statistic
                        title={<Text type="secondary">Clasă energetică</Text>}
                        value={profile?.energy_class || "N/A"}
                        valueStyle={{ color: getEnergyClassColor(profile?.energy_class), fontWeight: 700, fontSize: 28 }}
                        prefix={<ThunderboltOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} md={6}>
                    <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                      <Statistic
                        title={<Text type="secondary">Consum anual kWh</Text>}
                        value={profile?.annual_kwh || 0}
                        precision={0}
                        suffix="kWh/an"
                        prefix={<FireOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} md={6}>
                    <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                      <Statistic
                        title={<Text type="secondary">Emisii CO₂</Text>}
                        value={profile?.annual_co2_kg || 0}
                        precision={0}
                        suffix="kg/an"
                        prefix={<ExperimentOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} md={6}>
                    <Card size="small" style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}>
                      <Statistic
                        title={<Text type="secondary">U mediu</Text>}
                        value={profile?.u_value_avg || 0}
                        precision={2}
                        suffix="W/m²K"
                        prefix={<HomeOutlined />}
                      />
                    </Card>
                  </Col>
                </Row>

                {/* U-Values detail */}
                <Card
                  title="Coeficienți transfer termic (U-value)"
                  size="small"
                  style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)", marginBottom: 16 }}
                >
                  <Row gutter={24}>
                    {[
                      { label: "Pereți", value: profile?.u_value_walls, target: 0.56 },
                      { label: "Ferestre", value: profile?.u_value_windows, target: 1.3 },
                      { label: "Acoperiș", value: profile?.u_value_roof, target: 0.35 },
                      { label: "Planșeu", value: profile?.u_value_floor, target: 0.40 },
                    ].map((item) => (
                      <Col xs={12} md={6} key={item.label}>
                        <div style={{ textAlign: "center", padding: "8px 0" }}>
                          <Text type="secondary" style={{ fontSize: 12 }}>{item.label}</Text>
                          <div style={{ fontSize: 24, fontWeight: 700, color: (item.value || 0) <= item.target ? "#52c41a" : "#f5222d" }}>
                            {item.value?.toFixed(2) || "—"}
                          </div>
                          <Text type="secondary" style={{ fontSize: 11 }}>Target: ≤{item.target} W/m²K</Text>
                        </div>
                      </Col>
                    ))}
                  </Row>
                </Card>

                {/* HVAC */}
                <Card
                  title="Sisteme HVAC"
                  size="small"
                  style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
                >
                  <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
                    <Descriptions.Item label="Încălzire">
                      <Tag color="red">{profile?.heating_system || "N/A"}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Răcire">
                      <Tag color="blue">{profile?.cooling_system || "N/A"}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Ventilație">
                      <Tag color="green">{profile?.ventilation_type || "N/A"}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Surse regenerabile">
                      {profile?.renewable_sources?.length
                        ? profile.renewable_sources.map((s) => <Tag key={s} color="cyan">{s}</Tag>)
                        : "—"
                      }
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </>
            ),
          },
          {
            key: "calculator",
            label: "Calculator suprafețe",
            children: (
              <Card
                title={<Space><CalculatorOutlined /> Calculator suprafețe anvelopă</Space>}
                size="small"
                style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
              >
                <Row gutter={16}>
                  <Col xs={12} md={6}>
                    <Text type="secondary">Pereți (m²)</Text>
                    <InputNumber min={0} value={calcWalls} onChange={(v) => setCalcWalls(v || 0)} style={{ width: "100%", marginTop: 4 }} />
                  </Col>
                  <Col xs={12} md={6}>
                    <Text type="secondary">Ferestre (m²)</Text>
                    <InputNumber min={0} value={calcWindows} onChange={(v) => setCalcWindows(v || 0)} style={{ width: "100%", marginTop: 4 }} />
                  </Col>
                  <Col xs={12} md={6}>
                    <Text type="secondary">Acoperiș (m²)</Text>
                    <InputNumber min={0} value={calcRoof} onChange={(v) => setCalcRoof(v || 0)} style={{ width: "100%", marginTop: 4 }} />
                  </Col>
                  <Col xs={12} md={6}>
                    <Text type="secondary">Planșeu (m²)</Text>
                    <InputNumber min={0} value={calcFloor} onChange={(v) => setCalcFloor(v || 0)} style={{ width: "100%", marginTop: 4 }} />
                  </Col>
                </Row>
                <Divider />
                <Row gutter={16}>
                  <Col xs={12}>
                    <Statistic title="Suprafață totală anvelopă" value={totalSurface} suffix="m²" />
                  </Col>
                  <Col xs={12}>
                    <Statistic title="Raport suprafață vitrată" value={Number(glazingRatio)} suffix="%" />
                    <Progress percent={Number(glazingRatio)} status={Number(glazingRatio) > 40 ? "exception" : "normal"} size="small" />
                  </Col>
                </Row>
              </Card>
            ),
          },
          {
            key: "edit",
            label: "Editare profil",
            children: (
              <Card
                title="Editare profil energetic"
                size="small"
                style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
              >
                <Form
                  form={form}
                  layout="vertical"
                  initialValues={profile || {}}
                  onFinish={(values) => updateMut.mutate(values)}
                >
                  <Row gutter={16}>
                    <Col xs={12} md={6}>
                      <Form.Item name="energy_class" label="Clasă energetică">
                        <Select options={ENERGY_CLASSES.map((c) => ({ label: c, value: c }))} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="annual_kwh" label="Consum anual (kWh)">
                        <InputNumber min={0} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="annual_gas_mc" label="Consum gaz (mc/an)">
                        <InputNumber min={0} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="annual_co2_kg" label="Emisii CO₂ (kg/an)">
                        <InputNumber min={0} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Divider orientation="left">Coeficienți U (W/m²K)</Divider>
                  <Row gutter={16}>
                    <Col xs={12} md={6}>
                      <Form.Item name="u_value_walls" label="Pereți">
                        <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="u_value_windows" label="Ferestre">
                        <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="u_value_roof" label="Acoperiș">
                        <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Item name="u_value_floor" label="Planșeu">
                        <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Divider orientation="left">Sisteme HVAC</Divider>
                  <Row gutter={16}>
                    <Col xs={12} md={8}>
                      <Form.Item name="heating_system" label="Încălzire">
                        <Select options={HEATING_SYSTEMS.map((s) => ({ label: s.replace(/_/g, " "), value: s }))} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={8}>
                      <Form.Item name="cooling_system" label="Răcire">
                        <Select options={COOLING_SYSTEMS.map((s) => ({ label: s.replace(/_/g, " "), value: s }))} />
                      </Form.Item>
                    </Col>
                    <Col xs={12} md={8}>
                      <Form.Item name="ventilation_type" label="Ventilație">
                        <Select options={VENTILATION_TYPES.map((s) => ({ label: s.replace(/_/g, " "), value: s }))} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={updateMut.isPending}>
                    Salvează
                  </Button>
                </Form>
              </Card>
            ),
          },
          {
            key: "history",
            label: "Istoric măsurători",
            children: (
              <Card
                title={<Space><HistoryOutlined /> Istoric măsurători energetice</Space>}
                size="small"
                style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
              >
                <Table
                  dataSource={profile?.measurements || []}
                  rowKey="id"
                  size="small"
                  pagination={{ pageSize: 10 }}
                  locale={{ emptyText: "Nicio măsurătoare înregistrată" }}
                  columns={[
                    {
                      title: "Data",
                      dataIndex: "date",
                      key: "date",
                      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
                    },
                    { title: "Tip", dataIndex: "type", key: "type", render: (t: string) => <Tag>{t}</Tag> },
                    { title: "Valoare", dataIndex: "value", key: "value", align: "right" as const },
                    { title: "Unitate", dataIndex: "unit", key: "unit" },
                    { title: "Note", dataIndex: "notes", key: "notes", ellipsis: true },
                  ]}
                />
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}
