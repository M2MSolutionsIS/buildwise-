/**
 * E-039 — Situații de Lucrări (SdL) + SdL Generator
 * F-codes: F079 (Situații de Lucrări — evidență + generare),
 *          F078 (Monitorizare avansare proiect)
 *
 * Features:
 * - Lista SdL existente cu approval workflow
 * - E-039: SdL Generator wizard — generare automată din deviz:
 *   Step 1: Selectare perioadă + articole din deviz
 *   Step 2: Input cantități realizate în perioadă
 *   Step 3: Preview cu calcul automat (cumulat, valoric, % din contract)
 *   Step 4: Generare + PDF
 * - Banner "Prima SdL" / "SdL finală — recepție"
 * - Link Emite factură → Billing (F035)
 */
import { useState, useMemo, useCallback } from "react";
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
  Select,
  Statistic,
  Row,
  Col,
  message,
  Typography,
  Popconfirm,
  Tooltip,
  Progress,
  Steps,
  Alert,
  Divider,
  Spin,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  CheckOutlined,
  FileTextOutlined,
  DollarOutlined,
  FileDoneOutlined,
  CalendarOutlined,
  ThunderboltOutlined,
  FilePdfOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { WorkSituation, DevizItem, SdLGeneratorItem } from "../../../types";

const { Title, Text } = Typography;

const MONTHS = [
  "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
  "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie",
];

export default function WorkSituationsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  // E-039: SdL Generator wizard state
  const [wizardOpen, setWizardOpen] = useState(false);
  const [wizardStep, setWizardStep] = useState(0);
  const [wizardPeriod, setWizardPeriod] = useState<{ month: number; year: number }>({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
  });
  const [wizardItems, setWizardItems] = useState<
    { deviz_item_id: string; current_period_qty: number; selected: boolean }[]
  >([]);
  const [wizardPreview, setWizardPreview] = useState<SdLGeneratorItem[] | null>(null);
  const [wizardTotals, setWizardTotals] = useState<{
    total_contracted: number;
    total_current_period: number;
    total_cumulated: number;
    total_remaining: number;
    is_first_sdl: boolean;
    is_final_sdl: boolean;
    sdl_number: string;
  } | null>(null);

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: sdlRes, isLoading } = useQuery({
    queryKey: ["work-situations", projectId],
    queryFn: () => pmService.listWorkSituations(projectId!),
    enabled: !!projectId,
  });

  // E-039: Fetch deviz items for generator
  const { data: devizRes, isLoading: devizLoading } = useQuery({
    queryKey: ["deviz-items", projectId],
    queryFn: () => pmService.listDevizItems(projectId!),
    enabled: !!projectId && wizardOpen,
  });

  const sdls = sdlRes?.data ?? [];
  const devizItems: DevizItem[] = devizRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createWorkSituation(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație de lucrări creată");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      pmService.updateWorkSituation(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație actualizată");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const approveMut = useMutation({
    mutationFn: (id: string) => pmService.approveWorkSituation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație aprobată");
    },
  });

  // E-039: Generate SdL preview mutation
  const previewMut = useMutation({
    mutationFn: () =>
      pmService.generateSdLPreview(projectId!, {
        period_month: wizardPeriod.month,
        period_year: wizardPeriod.year,
        items: wizardItems
          .filter((i) => i.selected && i.current_period_qty > 0)
          .map((i) => ({
            deviz_item_id: i.deviz_item_id,
            current_period_qty: i.current_period_qty,
          })),
      }),
    onSuccess: (res) => {
      const data = res.data;
      if (data) {
        setWizardPreview(data.items);
        setWizardTotals({
          total_contracted: data.total_contracted,
          total_current_period: data.total_current_period,
          total_cumulated: data.total_cumulated,
          total_remaining: data.total_remaining,
          is_first_sdl: data.is_first_sdl,
          is_final_sdl: data.is_final_sdl,
          sdl_number: data.sdl_number,
        });
      }
      setWizardStep(2);
    },
    onError: () => message.error("Eroare la generare preview"),
  });

  // E-039: Create SdL from preview
  const createFromPreviewMut = useMutation({
    mutationFn: () =>
      pmService.createSdLFromPreview(projectId!, {
        period_month: wizardPeriod.month,
        period_year: wizardPeriod.year,
        sdl_number: wizardTotals?.sdl_number,
        items: wizardItems
          .filter((i) => i.selected && i.current_period_qty > 0)
          .map((i) => ({
            deviz_item_id: i.deviz_item_id,
            current_period_qty: i.current_period_qty,
          })),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["work-situations", projectId] });
      message.success("Situație de lucrări generată cu succes!");
      closeWizard();
    },
    onError: () => message.error("Eroare la creare SdL"),
  });

  // E-039: PDF generation
  const pdfMut = useMutation({
    mutationFn: (sdlId: string) => pmService.generateSdLPdf(sdlId),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      message.success("PDF generat");
    },
    onError: () => message.error("Eroare la generare PDF"),
  });

  // ─── Helpers ────────────────────────────────────────────────────────────────

  const closeWizard = () => {
    setWizardOpen(false);
    setWizardStep(0);
    setWizardItems([]);
    setWizardPreview(null);
    setWizardTotals(null);
  };

  const openWizard = useCallback(() => {
    setWizardOpen(true);
    setWizardStep(0);
    setWizardPeriod({
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear(),
    });
    setWizardItems([]);
    setWizardPreview(null);
    setWizardTotals(null);
  }, []);

  // E-039: Initialize wizard items from deviz when deviz loads
  const initWizardItems = useCallback(() => {
    if (devizItems.length > 0 && wizardItems.length === 0) {
      setWizardItems(
        devizItems.map((d) => ({
          deviz_item_id: d.id,
          current_period_qty: 0,
          selected: true,
        }))
      );
    }
  }, [devizItems, wizardItems.length]);

  // Auto-init when deviz loads
  useMemo(() => {
    if (wizardOpen && devizItems.length > 0 && wizardItems.length === 0) {
      initWizardItems();
    }
  }, [wizardOpen, devizItems, wizardItems.length, initWizardItems]);

  const updateWizardItemQty = (devizItemId: string, qty: number) => {
    setWizardItems((prev) =>
      prev.map((i) => (i.deviz_item_id === devizItemId ? { ...i, current_period_qty: qty } : i))
    );
  };

  const selectedItemCount = wizardItems.filter((i) => i.selected && i.current_period_qty > 0).length;

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    form.resetFields();
  };

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    const now = new Date();
    form.setFieldsValue({
      period_month: now.getMonth() + 1,
      period_year: now.getFullYear(),
      currency: "RON",
    });
    setIsModalOpen(true);
  };

  const openEdit = (sdl: WorkSituation) => {
    setEditingId(sdl.id);
    form.setFieldsValue(sdl);
    setIsModalOpen(true);
  };

  const handleSubmit = (values: Record<string, unknown>) => {
    const payload = {
      ...values,
      remaining:
        (values.contracted_total as number) -
        (values.executed_cumulated as number),
    };
    if (editingId) {
      updateMut.mutate({ id: editingId, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const totalContracted = useMemo(
    () => sdls.reduce((s, d) => s + d.contracted_total, 0),
    [sdls]
  );
  const totalExecutedCumulated = useMemo(
    () => sdls.reduce((s, d) => s + d.executed_cumulated, 0),
    [sdls]
  );
  const totalRemaining = useMemo(
    () => sdls.reduce((s, d) => s + d.remaining, 0),
    [sdls]
  );
  const approvedCount = useMemo(
    () => sdls.filter((d) => d.is_approved).length,
    [sdls]
  );
  const invoicedCount = useMemo(
    () => sdls.filter((d) => d.is_invoiced).length,
    [sdls]
  );

  // ─── Columns ────────────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Nr. SdL",
      dataIndex: "sdl_number",
      key: "sdl",
      width: 100,
      render: (v: string) => <Text strong>{v}</Text>,
    },
    {
      title: "Perioadă",
      key: "period",
      width: 140,
      render: (_: unknown, rec: WorkSituation) =>
        `${MONTHS[rec.period_month - 1]} ${rec.period_year}`,
      sorter: (a: WorkSituation, b: WorkSituation) =>
        a.period_year * 12 + a.period_month - (b.period_year * 12 + b.period_month),
      defaultSortOrder: "descend" as const,
    },
    {
      title: "Contractat",
      dataIndex: "contracted_total",
      key: "contracted",
      width: 130,
      align: "right" as const,
      render: (v: number, rec: WorkSituation) =>
        `${v.toLocaleString("ro-RO")} ${rec.currency}`,
    },
    {
      title: "Executat curent",
      dataIndex: "executed_current",
      key: "current",
      width: 130,
      align: "right" as const,
      render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
    },
    {
      title: "Executat cumulat",
      dataIndex: "executed_cumulated",
      key: "cumulated",
      width: 140,
      align: "right" as const,
      render: (v: number) => <Text strong>{v.toLocaleString("ro-RO")} RON</Text>,
    },
    {
      title: "Rest",
      dataIndex: "remaining",
      key: "remaining",
      width: 120,
      align: "right" as const,
      render: (v: number) => (
        <Text type={v < 0 ? "danger" : "success"}>
          {v.toLocaleString("ro-RO")} RON
        </Text>
      ),
    },
    {
      title: "Progres",
      key: "progress",
      width: 100,
      render: (_: unknown, rec: WorkSituation) => {
        const pct =
          rec.contracted_total > 0
            ? (rec.executed_cumulated / rec.contracted_total) * 100
            : 0;
        return <Progress percent={Math.round(pct)} size="small" />;
      },
    },
    {
      title: "Status",
      key: "status",
      width: 140,
      render: (_: unknown, rec: WorkSituation) => (
        <Space>
          {rec.is_approved ? (
            <Tag color="success" icon={<CheckOutlined />}>Aprobat</Tag>
          ) : (
            <Tag color="warning">Neaprobat</Tag>
          )}
          {rec.is_invoiced && (
            <Tag color="blue" icon={<DollarOutlined />}>Facturat</Tag>
          )}
        </Space>
      ),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 130,
      render: (_: unknown, rec: WorkSituation) => (
        <Space size="small">
          {!rec.is_approved && (
            <>
              <Tooltip title="Editează">
                <Button
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => openEdit(rec)}
                />
              </Tooltip>
              <Popconfirm
                title="Aprobi această situație de lucrări?"
                onConfirm={() => approveMut.mutate(rec.id)}
              >
                <Tooltip title="Aprobă">
                  <Button
                    size="small"
                    type="primary"
                    icon={<CheckOutlined />}
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
          <Tooltip title="Generează PDF">
            <Button
              size="small"
              icon={<FilePdfOutlined />}
              loading={pdfMut.isPending}
              onClick={() => pdfMut.mutate(rec.id)}
            />
          </Tooltip>
          {rec.is_approved && !rec.is_invoiced && (
            <Tooltip title="Link: Emite factură (F035)">
              <Button size="small" icon={<DollarOutlined />} type="dashed">
                Facturează
              </Button>
            </Tooltip>
          )}
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
          <FileDoneOutlined /> Situații de Lucrări — SdL (F079)
        </Title>
        <Space>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={openWizard}
          >
            Generează SdL din Deviz (E-039)
          </Button>
          <Button icon={<PlusOutlined />} onClick={openCreate}>
            SdL manuală
          </Button>
        </Space>
      </div>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total SdL"
              value={sdls.length}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Total contractat"
              value={totalContracted}
              suffix="RON"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Executat cumulat"
              value={totalExecutedCumulated}
              suffix="RON"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card size="small">
            <Statistic
              title="Rest de executat"
              value={totalRemaining}
              suffix="RON"
              precision={0}
              valueStyle={totalRemaining < 0 ? { color: "#ff4d4f" } : undefined}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card size="small">
            <Statistic
              title="Aprobate / Facturate"
              value={approvedCount}
              suffix={`/ ${invoicedCount}`}
              prefix={<CheckOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={sdls}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 12 }}
          size="middle"
          expandable={{
            expandedRowRender: (rec) =>
              rec.line_items && rec.line_items.length > 0 ? (
                <Table
                  size="small"
                  pagination={false}
                  dataSource={rec.line_items}
                  rowKey={(_, i) => String(i)}
                  columns={[
                    { title: "Descriere", dataIndex: "description", key: "desc" },
                    { title: "U.M.", dataIndex: "unit_of_measure", key: "um", width: 80 },
                    {
                      title: "Cant. contractată",
                      dataIndex: "contracted_qty",
                      key: "cqty",
                      width: 130,
                      align: "right" as const,
                    },
                    {
                      title: "Preț",
                      dataIndex: "contracted_price",
                      key: "price",
                      width: 100,
                      align: "right" as const,
                      render: (v: number) => `${v?.toFixed(2) ?? "—"} RON`,
                    },
                    {
                      title: "Exec. curent",
                      dataIndex: "executed_current_qty",
                      key: "ecur",
                      width: 110,
                      align: "right" as const,
                    },
                    {
                      title: "Exec. cumulat",
                      dataIndex: "executed_cumulated_qty",
                      key: "ecum",
                      width: 110,
                      align: "right" as const,
                    },
                    {
                      title: "Rest",
                      dataIndex: "remaining_qty",
                      key: "rest",
                      width: 80,
                      align: "right" as const,
                    },
                    {
                      title: "Valoare",
                      dataIndex: "total_value",
                      key: "val",
                      width: 110,
                      align: "right" as const,
                      render: (v: number) => `${v?.toLocaleString("ro-RO") ?? "—"} RON`,
                    },
                  ]}
                />
              ) : (
                <Text type="secondary">Nu sunt articole detaliate</Text>
              ),
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? "Editare Situație de Lucrări" : "Situație de Lucrări nouă"}
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="sdl_number"
                label="Nr. SdL"
                rules={[{ required: true }]}
              >
                <Input placeholder="SdL-001" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="period_month"
                label="Luna"
                rules={[{ required: true }]}
              >
                <Select
                  options={MONTHS.map((m, i) => ({ value: i + 1, label: m }))}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="period_year"
                label="An"
                rules={[{ required: true }]}
              >
                <InputNumber
                  min={2020}
                  max={2035}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="contracted_total"
                label="Valoare contractată (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={1000} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="executed_current"
                label="Executat curent (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={100} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="executed_cumulated"
                label="Executat cumulat (RON)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={100} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* E-039: SdL Generator Wizard */}
      <Modal
        title={
          <Space>
            <ThunderboltOutlined style={{ color: "#1677ff" }} />
            <span>Generator Situații de Lucrări — din Deviz (E-039)</span>
          </Space>
        }
        open={wizardOpen}
        onCancel={closeWizard}
        footer={null}
        width={960}
        destroyOnClose
      >
        <Steps
          current={wizardStep}
          size="small"
          style={{ marginBottom: 24 }}
          items={[
            { title: "Perioadă & Articole" },
            { title: "Cantități realizate" },
            { title: "Preview & Generare" },
          ]}
        />

        {/* Step 0: Select period + articles from deviz */}
        {wizardStep === 0 && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Text strong>Luna:</Text>
                <Select
                  value={wizardPeriod.month}
                  onChange={(v) => setWizardPeriod((p) => ({ ...p, month: v }))}
                  options={MONTHS.map((m, i) => ({ value: i + 1, label: m }))}
                  style={{ width: "100%", marginTop: 4 }}
                />
              </Col>
              <Col span={8}>
                <Text strong>An:</Text>
                <InputNumber
                  value={wizardPeriod.year}
                  onChange={(v) => setWizardPeriod((p) => ({ ...p, year: v ?? p.year }))}
                  min={2020}
                  max={2035}
                  style={{ width: "100%", marginTop: 4 }}
                />
              </Col>
            </Row>

            <Divider>Articole din Deviz</Divider>

            {devizLoading ? (
              <Spin style={{ display: "block", margin: "40px auto" }} />
            ) : devizItems.length === 0 ? (
              <Alert
                type="warning"
                message="Nu există articole în deviz"
                description="Adăugați articole în devizul proiectului pentru a genera SdL automat."
              />
            ) : (
              <Table
                dataSource={devizItems}
                rowKey="id"
                pagination={false}
                size="small"
                scroll={{ y: 300 }}
                rowSelection={{
                  selectedRowKeys: wizardItems.filter((i) => i.selected).map((i) => i.deviz_item_id),
                  onChange: (selectedKeys) => {
                    setWizardItems((prev) =>
                      prev.map((i) => ({
                        ...i,
                        selected: (selectedKeys as string[]).includes(i.deviz_item_id),
                      }))
                    );
                  },
                }}
                columns={[
                  {
                    title: "Cod",
                    dataIndex: "code",
                    key: "code",
                    width: 80,
                    render: (v: string) => <Text code>{v || "—"}</Text>,
                  },
                  {
                    title: "Descriere",
                    dataIndex: "description",
                    key: "desc",
                    ellipsis: true,
                  },
                  {
                    title: "U.M.",
                    dataIndex: "unit_of_measure",
                    key: "um",
                    width: 60,
                  },
                  {
                    title: "Cant. estimată",
                    dataIndex: "estimated_quantity",
                    key: "est_qty",
                    width: 110,
                    align: "right" as const,
                  },
                  {
                    title: "Preț unitar",
                    key: "price",
                    width: 100,
                    align: "right" as const,
                    render: (_: unknown, r: DevizItem) =>
                      `${(r.estimated_unit_price_material + r.estimated_unit_price_labor).toFixed(2)}`,
                  },
                  {
                    title: "Total estimat",
                    dataIndex: "estimated_total",
                    key: "est_total",
                    width: 120,
                    align: "right" as const,
                    render: (v: number) => `${v.toLocaleString("ro-RO")} RON`,
                  },
                ]}
              />
            )}

            <div style={{ textAlign: "right", marginTop: 16 }}>
              <Button onClick={closeWizard} style={{ marginRight: 8 }}>
                Anulează
              </Button>
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                disabled={wizardItems.filter((i) => i.selected).length === 0}
                onClick={() => setWizardStep(1)}
              >
                Pasul următor
              </Button>
            </div>
          </div>
        )}

        {/* Step 1: Input quantities for selected articles */}
        {wizardStep === 1 && (
          <div>
            <Alert
              type="info"
              message={`Perioadă: ${MONTHS[wizardPeriod.month - 1]} ${wizardPeriod.year}`}
              description="Introduceți cantitățile realizate în această perioadă pentru fiecare articol selectat."
              style={{ marginBottom: 16 }}
            />

            <Table
              dataSource={devizItems.filter((d) =>
                wizardItems.find((i) => i.deviz_item_id === d.id && i.selected)
              )}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ y: 400 }}
              columns={[
                {
                  title: "Cod",
                  dataIndex: "code",
                  key: "code",
                  width: 80,
                  render: (v: string) => <Text code>{v || "—"}</Text>,
                },
                {
                  title: "Descriere",
                  dataIndex: "description",
                  key: "desc",
                  ellipsis: true,
                },
                {
                  title: "U.M.",
                  dataIndex: "unit_of_measure",
                  key: "um",
                  width: 60,
                },
                {
                  title: "Cant. contract",
                  dataIndex: "estimated_quantity",
                  key: "contract_qty",
                  width: 110,
                  align: "right" as const,
                },
                {
                  title: "Cant. realizată perioadă",
                  key: "current_qty",
                  width: 180,
                  render: (_: unknown, r: DevizItem) => {
                    const item = wizardItems.find((i) => i.deviz_item_id === r.id);
                    return (
                      <InputNumber
                        size="small"
                        min={0}
                        max={r.estimated_quantity}
                        step={0.1}
                        value={item?.current_period_qty ?? 0}
                        onChange={(v) => updateWizardItemQty(r.id, v ?? 0)}
                        style={{ width: "100%" }}
                      />
                    );
                  },
                },
              ]}
            />

            <div style={{ textAlign: "right", marginTop: 16 }}>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => setWizardStep(0)}
                style={{ marginRight: 8 }}
              >
                Înapoi
              </Button>
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                disabled={selectedItemCount === 0}
                loading={previewMut.isPending}
                onClick={() => previewMut.mutate()}
              >
                Generează Preview ({selectedItemCount} articole)
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Preview + Generate */}
        {wizardStep === 2 && (
          <div>
            {/* E-039: Banners */}
            {wizardTotals?.is_first_sdl && (
              <Alert
                type="info"
                showIcon
                icon={<CalendarOutlined />}
                message="Prima situație de lucrări a proiectului"
                style={{ marginBottom: 12 }}
              />
            )}
            {wizardTotals?.is_final_sdl && (
              <Alert
                type="success"
                showIcon
                icon={<CheckCircleOutlined />}
                message="SdL finală — recepție"
                description="Cumulatul a ajuns la 100% pe toate articolele."
                style={{ marginBottom: 12 }}
                action={
                  <Button
                    size="small"
                    type="primary"
                    onClick={() => navigate(`/pm/projects/${projectId}/reception`)}
                  >
                    Declanșează recepție
                  </Button>
                }
              />
            )}

            {/* Totals */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Nr. SdL"
                    value={wizardTotals?.sdl_number || "—"}
                    valueStyle={{ fontSize: 16 }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Total perioadă curentă"
                    value={wizardTotals?.total_current_period ?? 0}
                    suffix="RON"
                    precision={0}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Total cumulat"
                    value={wizardTotals?.total_cumulated ?? 0}
                    suffix="RON"
                    precision={0}
                    valueStyle={{ color: "#1677ff" }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="Rest de executat"
                    value={wizardTotals?.total_remaining ?? 0}
                    suffix="RON"
                    precision={0}
                    valueStyle={(wizardTotals?.total_remaining ?? 0) < 0 ? { color: "#ff4d4f" } : undefined}
                  />
                </Card>
              </Col>
            </Row>

            {/* Preview table */}
            <Table
              dataSource={wizardPreview ?? []}
              rowKey="deviz_item_id"
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
              columns={[
                {
                  title: "Cod",
                  dataIndex: "code",
                  key: "code",
                  width: 70,
                  render: (v: string) => <Text code>{v || "—"}</Text>,
                },
                {
                  title: "Descriere",
                  dataIndex: "description",
                  key: "desc",
                  ellipsis: true,
                },
                {
                  title: "U.M.",
                  dataIndex: "unit_of_measure",
                  key: "um",
                  width: 50,
                },
                {
                  title: "Contract",
                  dataIndex: "contracted_qty",
                  key: "cqty",
                  width: 80,
                  align: "right" as const,
                },
                {
                  title: "Cumulat ant.",
                  dataIndex: "previous_cumulated_qty",
                  key: "prev",
                  width: 90,
                  align: "right" as const,
                },
                {
                  title: "Perioadă",
                  dataIndex: "current_period_qty",
                  key: "period",
                  width: 80,
                  align: "right" as const,
                  render: (v: number) => <Text strong>{v}</Text>,
                },
                {
                  title: "Cumulat nou",
                  dataIndex: "new_cumulated_qty",
                  key: "newcum",
                  width: 90,
                  align: "right" as const,
                  render: (v: number) => <Text strong style={{ color: "#1677ff" }}>{v}</Text>,
                },
                {
                  title: "Rest",
                  dataIndex: "remaining_qty",
                  key: "rest",
                  width: 70,
                  align: "right" as const,
                  render: (v: number) => (
                    <Text type={v <= 0 ? "success" : undefined}>{v}</Text>
                  ),
                },
                {
                  title: "%",
                  dataIndex: "percent_complete",
                  key: "pct",
                  width: 70,
                  align: "center" as const,
                  render: (v: number) => <Progress percent={Math.round(v)} size="small" />,
                },
                {
                  title: "Val. perioadă",
                  dataIndex: "current_period_value",
                  key: "val",
                  width: 110,
                  align: "right" as const,
                  render: (v: number) => `${v?.toLocaleString("ro-RO") ?? "—"} RON`,
                },
              ]}
            />

            <Divider />

            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => setWizardStep(1)}
              >
                Înapoi
              </Button>
              <Space>
                <Button onClick={closeWizard}>Anulează</Button>
                <Button
                  type="primary"
                  size="large"
                  icon={<FileDoneOutlined />}
                  loading={createFromPreviewMut.isPending}
                  onClick={() => createFromPreviewMut.mutate()}
                >
                  Creează SdL
                </Button>
              </Space>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
