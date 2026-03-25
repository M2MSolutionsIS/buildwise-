/**
 * Măsurători Consum Energetic PRE/POST — F088, F090
 * F088: kWh pre/post, economii estimate vs reale, CO₂ savings.
 * F090: Baza de date proiecte finalizate cu impact energetic.
 *
 * Form-based with PRE/POST comparison cards and savings calculations.
 * U-value reference: 0.3 W/m²K (BAHM treated glass).
 */
import { useState, useRef, useEffect, useCallback } from "react";
import {
  Card,
  Form,
  InputNumber,
  Button,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Divider,
  Tag,
  Space,
  Spin,
  Alert,
} from "antd";
import {
  ThunderboltOutlined,
  SaveOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  AreaChartOutlined,
  ArrowDownOutlined,
  ArrowUpOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
// types used implicitly via API responses

const { Title, Text } = Typography;

const U_VALUE_BAHM = 0.3; // W/m²K — BAHM treated glass reference

// ─── Comparison Bar Chart ────────────────────────────────────────────────────

function ComparisonChart({
  preKwh,
  postKwh,
  preCo2,
  postCo2,
}: {
  preKwh: number;
  postKwh: number;
  preCo2: number;
  postCo2: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const PAD = { top: 30, right: 20, bottom: 50, left: 20 };
    const chartH = H - PAD.top - PAD.bottom;

    ctx.clearRect(0, 0, W, H);

    const groups = [
      { label: "Consum kWh/an", pre: preKwh, post: postKwh, unit: "kWh" },
      { label: "Emisii CO₂ kg/an", pre: preCo2, post: postCo2, unit: "kg" },
    ];

    const groupW = (W - PAD.left - PAD.right) / groups.length;
    const barW = 40;
    const gap = 16;

    groups.forEach((g, gIdx) => {
      const cx = PAD.left + groupW * gIdx + groupW / 2;
      const maxVal = Math.max(g.pre, g.post, 1);

      // PRE bar
      const preH = (g.pre / maxVal) * chartH * 0.8;
      const preX = cx - barW - gap / 2;
      const preY = PAD.top + chartH - preH;
      ctx.fillStyle = "#ff7875";
      ctx.fillRect(preX, preY, barW, preH);

      // POST bar
      const postH = (g.post / maxVal) * chartH * 0.8;
      const postX = cx + gap / 2;
      const postY = PAD.top + chartH - postH;
      ctx.fillStyle = "#95de64";
      ctx.fillRect(postX, postY, barW, postH);

      // Labels
      ctx.fillStyle = "#333";
      ctx.font = "bold 11px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      ctx.fillText(g.pre > 0 ? g.pre.toLocaleString("ro-RO") : "—", preX + barW / 2, preY - 4);
      ctx.fillText(g.post > 0 ? g.post.toLocaleString("ro-RO") : "—", postX + barW / 2, postY - 4);

      // Group label
      ctx.fillStyle = "#666";
      ctx.font = "12px -apple-system, sans-serif";
      ctx.textBaseline = "top";
      ctx.fillText(g.label, cx, PAD.top + chartH + 8);

      // Savings arrow
      if (g.pre > 0 && g.post > 0) {
        const savings = ((g.pre - g.post) / g.pre) * 100;
        ctx.fillStyle = savings > 0 ? "#52c41a" : "#ff4d4f";
        ctx.font = "bold 13px -apple-system, sans-serif";
        ctx.fillText(
          `${savings > 0 ? "↓" : "↑"} ${Math.abs(savings).toFixed(1)}%`,
          cx,
          PAD.top + chartH + 26
        );
      }
    });

    // Legend
    const legendY = 12;
    ctx.font = "11px -apple-system, sans-serif";
    ctx.textAlign = "left";
    ctx.fillStyle = "#ff7875";
    ctx.fillRect(W / 2 - 80, legendY - 5, 12, 12);
    ctx.fillStyle = "#333";
    ctx.fillText("PRE", W / 2 - 64, legendY + 5);
    ctx.fillStyle = "#95de64";
    ctx.fillRect(W / 2, legendY - 5, 12, 12);
    ctx.fillStyle = "#333";
    ctx.fillText("POST", W / 2 + 16, legendY + 5);
  }, [preKwh, postKwh, preCo2, postCo2]);

  useEffect(() => {
    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: 280, display: "block" }}
    />
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function EnergyImpactPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [formLoaded, setFormLoaded] = useState(false);

  const { data: energyRes, isLoading } = useQuery({
    queryKey: ["energy-impact", projectId],
    queryFn: () => pmService.getEnergyImpact(projectId!),
    enabled: !!projectId,
  });

  const energy = energyRes?.data;

  // Load form when data arrives
  if (energy && !formLoaded) {
    form.setFieldsValue(energy);
    setFormLoaded(true);
  }

  const upsertMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.upsertEnergyImpact(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["energy-impact", projectId] });
      message.success("Măsurători energetice salvate");
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const handleSave = (values: Record<string, unknown>) => {
    // Auto-calculate savings
    const preKwh = (values.pre_kwh_annual as number) ?? 0;
    const postKwh = (values.post_kwh_annual as number) ?? 0;
    const preCo2 = (values.pre_co2_kg_annual as number) ?? 0;
    const postCo2 = (values.post_co2_kg_annual as number) ?? 0;

    upsertMut.mutate({
      ...values,
      actual_kwh_savings: preKwh > 0 && postKwh > 0 ? preKwh - postKwh : values.actual_kwh_savings,
      actual_co2_reduction: preCo2 > 0 && postCo2 > 0 ? preCo2 - postCo2 : values.actual_co2_reduction,
    });
  };

  // ─── Derived values ─────────────────────────────────────────────────────────

  const preKwh = energy?.pre_kwh_annual ?? 0;
  const postKwh = energy?.post_kwh_annual ?? 0;
  const preCo2 = energy?.pre_co2_kg_annual ?? 0;
  const postCo2 = energy?.post_co2_kg_annual ?? 0;

  const kwhSavingsPct = preKwh > 0 ? ((preKwh - postKwh) / preKwh) * 100 : 0;
  const co2SavingsPct = preCo2 > 0 ? ((preCo2 - postCo2) / preCo2) * 100 : 0;
  if (isLoading) {
    return (
      <div style={{ padding: 24, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <ThunderboltOutlined /> Măsurători Impact Energetic (F088, F090)
      </Title>

      {/* Reference note */}
      <Alert
        type="info"
        showIcon
        message={`Coeficient U de referință sticlă tratată termic BAHM: ${U_VALUE_BAHM} W/m²K`}
        style={{ marginBottom: 16 }}
      />

      {/* KPI cards */}
      {(preKwh > 0 || postKwh > 0) && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="Economie kWh"
                value={kwhSavingsPct}
                precision={1}
                suffix="%"
                prefix={kwhSavingsPct > 0 ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
                valueStyle={{ color: kwhSavingsPct > 0 ? "#52c41a" : "#ff4d4f" }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="Reducere CO₂"
                value={co2SavingsPct}
                precision={1}
                suffix="%"
                prefix={co2SavingsPct > 0 ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
                valueStyle={{ color: co2SavingsPct > 0 ? "#52c41a" : "#ff4d4f" }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="U-value PRE"
                value={energy?.pre_u_value_avg ?? 0}
                precision={2}
                suffix="W/m²K"
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="U-value POST"
                value={energy?.post_u_value_avg ?? 0}
                precision={2}
                suffix="W/m²K"
                valueStyle={
                  (energy?.post_u_value_avg ?? 99) <= U_VALUE_BAHM
                    ? { color: "#52c41a" }
                    : undefined
                }
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="Suprafață tratată"
                value={energy?.treated_area_sqm ?? 0}
                suffix="mp"
                prefix={<AreaChartOutlined />}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card size="small">
              <Statistic
                title="Verificat"
                value={energy?.is_verified ? "Da" : "Nu"}
                prefix={
                  energy?.is_verified ? (
                    <CheckCircleOutlined style={{ color: "#52c41a" }} />
                  ) : (
                    <ExclamationCircleOutlined style={{ color: "#faad14" }} />
                  )
                }
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Comparison chart */}
      {(preKwh > 0 || postKwh > 0) && (
        <Card
          title="Comparație PRE vs POST"
          style={{ marginBottom: 24 }}
        >
          <ComparisonChart
            preKwh={preKwh}
            postKwh={postKwh}
            preCo2={preCo2}
            postCo2={postCo2}
          />
        </Card>
      )}

      {/* Form */}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={energy ?? {}}
      >
        <Row gutter={24}>
          {/* PRE column */}
          <Col span={12}>
            <Card
              title={
                <Space>
                  <Tag color="red">PRE</Tag>
                  <Text strong>Măsurători înainte de intervenție</Text>
                </Space>
              }
              size="small"
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="pre_kwh_annual" label="Consum kWh/an">
                    <InputNumber min={0} step={100} style={{ width: "100%" }} placeholder="Ex: 15000" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="pre_gas_mc_annual" label="Consum gaz mc/an">
                    <InputNumber min={0} step={10} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="pre_co2_kg_annual" label="Emisii CO₂ kg/an">
                    <InputNumber min={0} step={100} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="pre_u_value_avg" label="U-value mediu (W/m²K)">
                    <InputNumber min={0} max={10} step={0.1} style={{ width: "100%" }} placeholder="Ex: 2.8" />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* POST column */}
          <Col span={12}>
            <Card
              title={
                <Space>
                  <Tag color="green">POST</Tag>
                  <Text strong>Măsurători după intervenție</Text>
                </Space>
              }
              size="small"
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="post_kwh_annual" label="Consum kWh/an">
                    <InputNumber min={0} step={100} style={{ width: "100%" }} placeholder="Ex: 8000" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="post_gas_mc_annual" label="Consum gaz mc/an">
                    <InputNumber min={0} step={10} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="post_co2_kg_annual" label="Emisii CO₂ kg/an">
                    <InputNumber min={0} step={100} style={{ width: "100%" }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="post_u_value_avg" label="U-value mediu (W/m²K)">
                    <InputNumber min={0} max={10} step={0.1} style={{ width: "100%" }} placeholder={`Target: ${U_VALUE_BAHM}`} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        <Divider orientation="left">Economii estimate</Divider>
        <Row gutter={16}>
          <Col span={6}>
            <Form.Item name="estimated_kwh_savings" label="Economie kWh estimată/an">
              <InputNumber min={0} step={100} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="estimated_co2_reduction" label="Reducere CO₂ estimată kg/an">
              <InputNumber min={0} step={100} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="actual_kwh_savings" label="Economie kWh reală/an">
              <InputNumber min={0} step={100} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="actual_co2_reduction" label="Reducere CO₂ reală kg/an">
              <InputNumber min={0} step={100} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">Date proiect</Divider>
        <Row gutter={16}>
          <Col span={6}>
            <Form.Item name="total_area_sqm" label="Suprafață totală (mp)">
              <InputNumber min={0} step={10} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="treated_area_sqm" label="Suprafață tratată (mp)">
              <InputNumber min={0} step={10} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="total_project_cost" label="Cost total proiect (RON)">
              <InputNumber min={0} step={1000} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name="duration_days" label="Durată (zile)">
              <InputNumber min={0} style={{ width: "100%" }} />
            </Form.Item>
          </Col>
        </Row>

        <div style={{ textAlign: "right", marginTop: 16 }}>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
            loading={upsertMut.isPending}
            size="large"
          >
            Salvează măsurătorile
          </Button>
        </div>
      </Form>
    </div>
  );
}
