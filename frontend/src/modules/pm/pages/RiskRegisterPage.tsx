/**
 * Registru Riscuri — F084 (RIEM Methodology)
 * Identificare, evaluare P×I, plan mitigare, export.
 *
 * 5×5 risk matrix visualization + CRUD table.
 * Risk Score = Probability × Impact (numeric mapping).
 */
import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Popconfirm,
  Tooltip,
  Alert,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  WarningOutlined,
  SafetyOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { PMRisk, RiskProbability, RiskImpact, RiskStatus } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

const PROB_LABELS: Record<RiskProbability, string> = {
  very_low: "Foarte scăzută",
  low: "Scăzută",
  medium: "Medie",
  high: "Ridicată",
  very_high: "Foarte ridicată",
};

const IMPACT_LABELS: Record<RiskImpact, string> = {
  negligible: "Neglijabil",
  minor: "Minor",
  moderate: "Moderat",
  major: "Major",
  critical: "Critic",
};

const STATUS_LABELS: Record<RiskStatus, string> = {
  identified: "Identificat",
  assessed: "Evaluat",
  mitigating: "Mitigare",
  resolved: "Rezolvat",
  accepted: "Acceptat",
};

const STATUS_COLORS: Record<RiskStatus, string> = {
  identified: "default",
  assessed: "processing",
  mitigating: "warning",
  resolved: "success",
  accepted: "cyan",
};

const PROB_NUMERIC: Record<RiskProbability, number> = {
  very_low: 1,
  low: 2,
  medium: 3,
  high: 4,
  very_high: 5,
};

const IMPACT_NUMERIC: Record<RiskImpact, number> = {
  negligible: 1,
  minor: 2,
  moderate: 3,
  major: 4,
  critical: 5,
};

const RISK_CATEGORIES = [
  "Tehnic", "Financiar", "Calendar", "Resurse", "Extern",
  "Juridic", "Mediu", "Calitate", "Comunicare", "Alt",
];

function riskScoreColor(score: number): string {
  if (score >= 15) return "#ff4d4f"; // critical
  if (score >= 10) return "#fa8c16"; // high
  if (score >= 5) return "#faad14";  // medium
  return "#52c41a";                   // low
}

function riskScoreLevel(score: number): string {
  if (score >= 15) return "Critic";
  if (score >= 10) return "Ridicat";
  if (score >= 5) return "Mediu";
  return "Scăzut";
}

// ─── 5×5 Risk Matrix ─────────────────────────────────────────────────────────

function RiskMatrix({ risks }: { risks: PMRisk[] }) {
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
    const PAD = { top: 30, right: 20, bottom: 40, left: 70 };
    const gridW = W - PAD.left - PAD.right;
    const gridH = H - PAD.top - PAD.bottom;
    const cellW = gridW / 5;
    const cellH = gridH / 5;

    ctx.clearRect(0, 0, W, H);

    // Color matrix (P × I)
    const colors = [
      ["#d4edda", "#d4edda", "#fff3cd", "#fff3cd", "#f8d7da"],
      ["#d4edda", "#fff3cd", "#fff3cd", "#f8d7da", "#f8d7da"],
      ["#fff3cd", "#fff3cd", "#f8d7da", "#f8d7da", "#f5c6cb"],
      ["#fff3cd", "#f8d7da", "#f8d7da", "#f5c6cb", "#f5c6cb"],
      ["#f8d7da", "#f8d7da", "#f5c6cb", "#f5c6cb", "#f5c6cb"],
    ];

    // Draw cells (y=0 is top = very_high probability)
    for (let row = 0; row < 5; row++) {
      for (let col = 0; col < 5; col++) {
        const x = PAD.left + col * cellW;
        const y = PAD.top + row * cellH;
        ctx.fillStyle = colors[row]?.[col] ?? "#fff";
        ctx.fillRect(x, y, cellW, cellH);
        ctx.strokeStyle = "#e0e0e0";
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, cellW, cellH);

        // Score label
        const score = (5 - row) * (col + 1);
        ctx.fillStyle = "#999";
        ctx.font = "10px -apple-system, sans-serif";
        ctx.textAlign = "right";
        ctx.textBaseline = "bottom";
        ctx.fillText(String(score), x + cellW - 4, y + cellH - 4);
      }
    }

    // Plot risks as dots
    const activeRisks = risks.filter(
      (r) => r.status !== "resolved" && r.status !== "accepted"
    );
    // Count risks per cell
    const cellCounts = new Map<string, PMRisk[]>();
    activeRisks.forEach((risk) => {
      const col = IMPACT_NUMERIC[risk.impact] - 1;
      const row = 5 - PROB_NUMERIC[risk.probability];
      const key = `${row}-${col}`;
      if (!cellCounts.has(key)) cellCounts.set(key, []);
      cellCounts.get(key)!.push(risk);
    });

    cellCounts.forEach((cellRisks, key) => {
      const [rowStr, colStr] = key.split("-");
      const row = parseInt(rowStr ?? "0");
      const col = parseInt(colStr ?? "0");
      const cx = PAD.left + col * cellW + cellW / 2;
      const cy = PAD.top + row * cellH + cellH / 2;

      const count = cellRisks.length;
      const radius = Math.min(12 + count * 3, cellW / 2 - 4);

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 77, 79, 0.7)";
      ctx.fill();
      ctx.strokeStyle = "#ff4d4f";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#fff";
      ctx.font = `bold ${count > 9 ? 11 : 13}px -apple-system, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(count), cx, cy);
    });

    // Axis labels
    const probLabels = ["F. Scăzută", "Scăzută", "Medie", "Ridicată", "F. Ridicată"];
    const impactLabels = ["Neglijabil", "Minor", "Moderat", "Major", "Critic"];

    ctx.fillStyle = "#333";
    ctx.font = "11px -apple-system, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    probLabels.forEach((label, i) => {
      const y = PAD.top + (4 - i) * cellH + cellH / 2;
      ctx.fillText(label, PAD.left - 6, y);
    });

    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    impactLabels.forEach((label, i) => {
      const x = PAD.left + i * cellW + cellW / 2;
      ctx.fillText(label, x, PAD.top + gridH + 6);
    });

    // Axis titles
    ctx.fillStyle = "#666";
    ctx.font = "bold 12px -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("IMPACT →", PAD.left + gridW / 2, PAD.top + gridH + 26);

    ctx.save();
    ctx.translate(14, PAD.top + gridH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("PROBABILITATE →", 0, 0);
    ctx.restore();

    // Title
    ctx.fillStyle = "#333";
    ctx.font = "bold 13px -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Matricea Riscurilor 5×5 (RIEM)", W / 2, 16);
  }, [risks]);

  useEffect(() => {
    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: 360, display: "block" }}
    />
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function RiskRegisterPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const { data: riskRes, isLoading } = useQuery({
    queryKey: ["risks", projectId],
    queryFn: () => pmService.listRisks(projectId!),
    enabled: !!projectId,
  });

  const risks = riskRes?.data ?? [];

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createRisk(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risks", projectId] });
      message.success("Risc adăugat");
      closeModal();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateRisk(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risks", projectId] });
      message.success("Risc actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteRisk(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risks", projectId] });
      message.success("Risc șters");
    },
  });

  // ─── Helpers ────────────────────────────────────────────────────────────────

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    form.resetFields();
  };

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({
      probability: "medium",
      impact: "moderate",
      status: "identified",
      identified_date: dayjs(),
    });
    setIsModalOpen(true);
  };

  const openEdit = (risk: PMRisk) => {
    setEditingId(risk.id);
    form.setFieldsValue({
      ...risk,
      identified_date: risk.identified_date ? dayjs(risk.identified_date) : undefined,
      review_date: risk.review_date ? dayjs(risk.review_date) : undefined,
    });
    setIsModalOpen(true);
  };

  const handleSubmit = (values: Record<string, unknown>) => {
    const prob = values.probability as RiskProbability;
    const imp = values.impact as RiskImpact;
    const payload = {
      ...values,
      risk_score: PROB_NUMERIC[prob] * IMPACT_NUMERIC[imp],
      identified_date: values.identified_date
        ? (values.identified_date as dayjs.Dayjs).toISOString()
        : undefined,
      review_date: values.review_date
        ? (values.review_date as dayjs.Dayjs).toISOString()
        : undefined,
    };
    if (editingId) {
      updateMut.mutate({ id: editingId, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const activeRisks = useMemo(
    () => risks.filter((r) => r.status !== "resolved" && r.status !== "accepted"),
    [risks]
  );
  const criticalRisks = useMemo(
    () => activeRisks.filter((r) => (r.risk_score ?? 0) >= 15),
    [activeRisks]
  );
  const avgScore = useMemo(
    () =>
      activeRisks.length > 0
        ? activeRisks.reduce((s, r) => s + (r.risk_score ?? 0), 0) / activeRisks.length
        : 0,
    [activeRisks]
  );

  // ─── Columns ────────────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Risc",
      dataIndex: "title",
      key: "title",
      width: 200,
      render: (v: string, rec: PMRisk) => (
        <Space>
          {(rec.risk_score ?? 0) >= 15 && (
            <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />
          )}
          <Text strong>{v}</Text>
        </Space>
      ),
    },
    {
      title: "Categorie",
      dataIndex: "category",
      key: "cat",
      width: 100,
      render: (v?: string) => v ? <Tag>{v}</Tag> : "—",
      filters: RISK_CATEGORIES.map((c) => ({ text: c, value: c })),
      onFilter: (value: unknown, rec: PMRisk) => rec.category === value,
    },
    {
      title: "Probabilitate",
      dataIndex: "probability",
      key: "prob",
      width: 130,
      render: (v: RiskProbability) => (
        <Tag color={PROB_NUMERIC[v] >= 4 ? "red" : PROB_NUMERIC[v] >= 3 ? "orange" : "green"}>
          {PROB_LABELS[v]} ({PROB_NUMERIC[v]})
        </Tag>
      ),
    },
    {
      title: "Impact",
      dataIndex: "impact",
      key: "impact",
      width: 110,
      render: (v: RiskImpact) => (
        <Tag color={IMPACT_NUMERIC[v] >= 4 ? "red" : IMPACT_NUMERIC[v] >= 3 ? "orange" : "green"}>
          {IMPACT_LABELS[v]} ({IMPACT_NUMERIC[v]})
        </Tag>
      ),
    },
    {
      title: "Scor P×I",
      dataIndex: "risk_score",
      key: "score",
      width: 100,
      align: "center" as const,
      sorter: (a: PMRisk, b: PMRisk) => (a.risk_score ?? 0) - (b.risk_score ?? 0),
      defaultSortOrder: "descend" as const,
      render: (v?: number) => {
        const score = v ?? 0;
        return (
          <Tag
            color={riskScoreColor(score)}
            style={{ fontWeight: 700, fontSize: 14 }}
          >
            {score}
          </Tag>
        );
      },
    },
    {
      title: "Nivel",
      key: "level",
      width: 90,
      render: (_: unknown, rec: PMRisk) => {
        const score = rec.risk_score ?? 0;
        return (
          <Text style={{ color: riskScoreColor(score), fontWeight: 600 }}>
            {riskScoreLevel(score)}
          </Text>
        );
      },
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (v: RiskStatus) => (
        <Tag color={STATUS_COLORS[v]}>{STATUS_LABELS[v]}</Tag>
      ),
      filters: (Object.keys(STATUS_LABELS) as RiskStatus[]).map((k) => ({
        text: STATUS_LABELS[k],
        value: k,
      })),
      onFilter: (value: unknown, rec: PMRisk) => rec.status === value,
    },
    {
      title: "Review",
      dataIndex: "review_date",
      key: "review",
      width: 100,
      render: (d?: string) =>
        d ? (
          <Text
            type={dayjs(d).isBefore(dayjs()) ? "danger" : undefined}
          >
            {dayjs(d).format("DD.MM.YY")}
          </Text>
        ) : (
          "—"
        ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 100,
      render: (_: unknown, rec: PMRisk) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(rec)}
          />
          <Popconfirm
            title="Ștergi acest risc?"
            onConfirm={() => deleteMut.mutate(rec.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

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
          <SafetyOutlined /> Registru Riscuri — RIEM (F084)
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Adaugă risc
        </Button>
      </div>

      {/* Critical alert */}
      {criticalRisks.length > 0 && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message={`${criticalRisks.length} riscuri critice active (scor ≥ 15)!`}
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {criticalRisks.map((r) => (
                <li key={r.id}>
                  <Text strong>{r.title}</Text> — Scor: {r.risk_score}, {PROB_LABELS[r.probability]} × {IMPACT_LABELS[r.impact]}
                </li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total riscuri"
              value={risks.length}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Active"
              value={activeRisks.length}
              prefix={<ThunderboltOutlined />}
              valueStyle={activeRisks.length > 0 ? { color: "#faad14" } : undefined}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Critice"
              value={criticalRisks.length}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={criticalRisks.length > 0 ? { color: "#ff4d4f" } : undefined}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Scor mediu"
              value={avgScore}
              precision={1}
              valueStyle={{ color: riskScoreColor(avgScore) }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Rezolvate"
              value={risks.filter((r) => r.status === "resolved").length}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
      </Row>

      {/* Risk Matrix */}
      <Card title="Matricea Riscurilor 5×5" style={{ marginBottom: 24 }}>
        <RiskMatrix risks={risks} />
      </Card>

      {/* Risk table */}
      <Card title="Lista Riscurilor">
        <Table
          columns={columns}
          dataSource={risks}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 15 }}
          size="middle"
          expandable={{
            expandedRowRender: (rec) => (
              <div style={{ padding: "8px 16px" }}>
                {rec.description && (
                  <div style={{ marginBottom: 8 }}>
                    <Text type="secondary">Descriere: </Text>
                    <Text>{rec.description}</Text>
                  </div>
                )}
                {rec.mitigation_plan && (
                  <div style={{ marginBottom: 8 }}>
                    <Text type="secondary">Plan mitigare: </Text>
                    <Text>{rec.mitigation_plan}</Text>
                  </div>
                )}
                {rec.contingency_plan && (
                  <div>
                    <Text type="secondary">Plan contingență: </Text>
                    <Text>{rec.contingency_plan}</Text>
                  </div>
                )}
              </div>
            ),
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare risc" : "Adaugă risc"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={650}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="title"
            label="Titlu risc"
            rules={[{ required: true, message: "Titlul este obligatoriu" }]}
          >
            <Input placeholder="Ex: Întârziere livrare materiale" />
          </Form.Item>
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="category"
                label="Categorie"
              >
                <Select
                  placeholder="Selectează"
                  options={RISK_CATEGORIES.map((c) => ({ value: c, label: c }))}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="probability"
                label="Probabilitate"
                rules={[{ required: true }]}
              >
                <Select
                  options={(Object.keys(PROB_LABELS) as RiskProbability[]).map(
                    (k) => ({
                      value: k,
                      label: `${PROB_LABELS[k]} (${PROB_NUMERIC[k]})`,
                    })
                  )}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="impact"
                label="Impact"
                rules={[{ required: true }]}
              >
                <Select
                  options={(Object.keys(IMPACT_LABELS) as RiskImpact[]).map(
                    (k) => ({
                      value: k,
                      label: `${IMPACT_LABELS[k]} (${IMPACT_NUMERIC[k]})`,
                    })
                  )}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="status" label="Status">
                <Select
                  options={(Object.keys(STATUS_LABELS) as RiskStatus[]).map(
                    (k) => ({ value: k, label: STATUS_LABELS[k] })
                  )}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="identified_date" label="Data identificare">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="review_date" label="Data review">
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mitigation_plan" label="Plan mitigare">
            <Input.TextArea rows={2} placeholder="Acțiuni pentru reducerea probabilității/impactului..." />
          </Form.Item>
          <Form.Item name="contingency_plan" label="Plan contingență">
            <Input.TextArea rows={2} placeholder="Ce facem dacă riscul se materializează..." />
          </Form.Item>
          <Form.Item name="notes" label="Note">
            <Input.TextArea rows={1} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
