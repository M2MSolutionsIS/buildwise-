/**
 * E-037: Import Engine — Devize (F123)
 * Wizard 4 pași: Selectare Sursă → Upload + Preview → Mapping WBS → Confirmare.
 * Specific P2 (BAHM) — import multi-format: Intersoft XML, eDevize, CSV, Excel.
 */
import { useState, useMemo, useCallback } from "react";
import {
  Card,
  Steps,
  Button,
  Upload,
  Table,
  Tag,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Space,
  Spin,
  Select,
  message,
  Badge,
  Tooltip,
  Result,
  Progress,
} from "antd";
import {
  InboxOutlined,
  FileExcelOutlined,
  FileTextOutlined,
  ApiOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
  ImportOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type {
  ImportSourceType,
  ImportPreviewItem,
  ImportError,
  ImportUploadResponse,
} from "../../../types";

const { Title, Text } = Typography;
const { Dragger } = Upload;

// ─── Source config ──────────────────────────────────────────────────────────

const IMPORT_SOURCES: {
  key: ImportSourceType;
  label: string;
  description: string;
  icon: React.ReactNode;
  extensions: string;
  recommended?: boolean;
}[] = [
  {
    key: "intersoft",
    label: "Intersoft XML",
    description: "Import din software Intersoft — format XML standard devize construcții",
    icon: <ApiOutlined style={{ fontSize: 32, color: "#1677ff" }} />,
    extensions: ".xml",
    recommended: true,
  },
  {
    key: "edevize",
    label: "eDevize Export",
    description: "Export din platforma eDevize — CSV sau XLSX",
    icon: <FileExcelOutlined style={{ fontSize: 32, color: "#52c41a" }} />,
    extensions: ".csv,.xlsx",
  },
  {
    key: "csv",
    label: "CSV Manual",
    description: "Fișier CSV cu coloane: cod, denumire, UM, cantitate, preț unitar",
    icon: <FileTextOutlined style={{ fontSize: 32, color: "#fa8c16" }} />,
    extensions: ".csv",
  },
  {
    key: "excel",
    label: "Excel Generic",
    description: "Fișier Excel (.xlsx) cu structură tabulară liberă",
    icon: <FileExcelOutlined style={{ fontSize: 32, color: "#13c2c2" }} />,
    extensions: ".xlsx,.xls",
  },
];

const DUPLICATE_OPTIONS = [
  { value: "overwrite", label: "Suprascrie existente" },
  { value: "sum", label: "Adună cantitățile" },
  { value: "exclude", label: "Exclude duplicatele" },
] as const;

// ─── Component ──────────────────────────────────────────────────────────────

export default function ImportEnginePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // Wizard state
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedSource, setSelectedSource] = useState<ImportSourceType | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [previewItems, setPreviewItems] = useState<ImportPreviewItem[]>([]);
  const [parseErrors, setParseErrors] = useState<ImportError[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [validRows, setValidRows] = useState(0);
  const [duplicateAction, setDuplicateAction] = useState<"overwrite" | "sum" | "exclude">("overwrite");
  const [importComplete, setImportComplete] = useState(false);
  const [importedCount, setImportedCount] = useState(0);

  // Existing import jobs
  const { data: jobsData } = useQuery({
    queryKey: ["import-jobs", projectId],
    queryFn: () => pmService.listImportJobs(projectId!),
    enabled: !!projectId,
  });
  const jobs = jobsData?.data ?? [];

  // Upload mutation
  const uploadMut = useMutation({
    mutationFn: (file: File) =>
      pmService.uploadImportFile(projectId!, file, selectedSource!),
    onSuccess: (res) => {
      const d: ImportUploadResponse = res.data;
      setSessionId(d.session_id);
      setPreviewItems(d.items);
      setParseErrors(d.errors);
      setTotalRows(d.total_rows);
      setValidRows(d.valid_rows);
      message.success(`${d.valid_rows}/${d.total_rows} rânduri parsate cu succes`);
      setCurrentStep(2);
    },
    onError: () => message.error("Eroare la upload. Verifică formatul fișierului."),
  });

  // Auto-match WBS mutation
  const autoMatchMut = useMutation({
    mutationFn: () => pmService.autoMatchWBS(sessionId!),
    onSuccess: (res) => {
      setPreviewItems(res.data);
      const matched = res.data.filter((i) => i.wbs_node_id).length;
      message.success(`${matched}/${res.data.length} articole asociate automat la WBS`);
    },
    onError: () => message.error("Eroare la auto-match WBS"),
  });

  // Confirm import mutation
  const confirmMut = useMutation({
    mutationFn: () =>
      pmService.updateImportMapping(sessionId!, {
        items: previewItems.map((it) => ({
          import_row_index: it.row_index,
          wbs_node_id: it.wbs_node_id ?? null,
        })),
        duplicate_action: duplicateAction,
      }).then(() => pmService.confirmImport(sessionId!)),
    onSuccess: (res) => {
      setImportComplete(true);
      setImportedCount(res.data.records_imported);
      message.success("Import finalizat cu succes!");
      setCurrentStep(3);
    },
    onError: () => message.error("Eroare la import"),
  });

  // Helpers
  const errorCount = useMemo(
    () => previewItems.filter((i) => !i.is_valid).length,
    [previewItems]
  );
  const matchedCount = useMemo(
    () => previewItems.filter((i) => i.wbs_node_id).length,
    [previewItems]
  );
  const duplicateCount = useMemo(
    () => previewItems.filter((i) => i.is_duplicate).length,
    [previewItems]
  );

  const handleFileUpload = useCallback(
    (file: File) => {
      uploadMut.mutate(file);
      return false; // prevent default upload
    },
    [uploadMut]
  );

  const updateItemWBS = useCallback(
    (rowIndex: number, wbsNodeId: string | null, wbsNodeName: string | null) => {
      setPreviewItems((prev) =>
        prev.map((it) =>
          it.row_index === rowIndex
            ? { ...it, wbs_node_id: wbsNodeId ?? undefined, wbs_node_name: wbsNodeName ?? undefined, match_score: wbsNodeId ? 1 : undefined }
            : it
        )
      );
    },
    []
  );

  const canProceedStep1 = selectedSource !== null;
  const canProceedStep2 = sessionId !== null && validRows > 0;

  // ─── Step 0: Source Selection ─────────────────────────────────────────────

  const renderSourceSelection = () => (
    <div>
      <Title level={5} style={{ marginBottom: 16 }}>
        Selectează sursa de import
      </Title>
      <Row gutter={[16, 16]}>
        {IMPORT_SOURCES.map((src) => (
          <Col xs={24} sm={12} lg={6} key={src.key}>
            <Card
              hoverable
              onClick={() => setSelectedSource(src.key)}
              style={{
                borderColor: selectedSource === src.key ? "#1677ff" : undefined,
                borderWidth: selectedSource === src.key ? 2 : 1,
                textAlign: "center",
                height: "100%",
              }}
            >
              {src.recommended && (
                <Tag color="blue" style={{ position: "absolute", top: 8, right: 8 }}>
                  Recomandat
                </Tag>
              )}
              <div style={{ marginBottom: 12 }}>{src.icon}</div>
              <Title level={5} style={{ margin: 0 }}>
                {src.label}
              </Title>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {src.description}
              </Text>
              <div style={{ marginTop: 8 }}>
                <Tag>{src.extensions}</Tag>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Existing import history */}
      {jobs.length > 0 && (
        <Card size="small" title="Importuri anterioare" style={{ marginTop: 24 }}>
          <Table
            dataSource={jobs}
            rowKey="id"
            size="small"
            pagination={false}
            columns={[
              { title: "Fișier", dataIndex: "file_name", key: "file_name" },
              {
                title: "Sursă",
                dataIndex: "source_type",
                key: "source_type",
                render: (v: string) =>
                  IMPORT_SOURCES.find((s) => s.key === v)?.label ?? v,
              },
              {
                title: "Status",
                dataIndex: "status",
                key: "status",
                render: (v: string) => {
                  const colors: Record<string, string> = {
                    completed: "green",
                    error: "red",
                    importing: "blue",
                    pending: "default",
                    mapping: "orange",
                  };
                  return <Tag color={colors[v] ?? "default"}>{v}</Tag>;
                },
              },
              {
                title: "Înregistrări",
                key: "records",
                render: (_: unknown, r: { records_imported: number; records_total: number }) =>
                  `${r.records_imported}/${r.records_total}`,
              },
              {
                title: "Data",
                dataIndex: "created_at",
                key: "created_at",
                render: (v: string) =>
                  v ? new Date(v).toLocaleDateString("ro-RO") : "—",
              },
            ]}
          />
        </Card>
      )}
    </div>
  );

  // ─── Step 1: Upload + Preview ─────────────────────────────────────────────

  const renderUploadPreview = () => {
    const sourceConfig = IMPORT_SOURCES.find((s) => s.key === selectedSource);
    return (
      <div>
        {!sessionId && (
          <Dragger
            accept={sourceConfig?.extensions}
            beforeUpload={handleFileUpload}
            showUploadList={false}
            disabled={uploadMut.isPending}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              Click sau drag & drop fișier {sourceConfig?.label}
            </p>
            <p className="ant-upload-hint">
              Extensii acceptate: {sourceConfig?.extensions}
            </p>
          </Dragger>
        )}

        {uploadMut.isPending && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>Se parsează fișierul...</Text>
            </div>
          </div>
        )}

        {sessionId && (
          <>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Statistic title="Total rânduri" value={totalRows} />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Valide"
                  value={validRows}
                  valueStyle={{ color: "#52c41a" }}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Erori"
                  value={errorCount}
                  valueStyle={{ color: errorCount > 0 ? "#ff4d4f" : "#52c41a" }}
                  prefix={errorCount > 0 ? <CloseCircleOutlined /> : <CheckCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Duplicate"
                  value={duplicateCount}
                  valueStyle={{ color: duplicateCount > 0 ? "#fa8c16" : undefined }}
                  prefix={duplicateCount > 0 ? <WarningOutlined /> : undefined}
                />
              </Col>
            </Row>

            {parseErrors.length > 0 && (
              <Alert
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
                message={`${parseErrors.length} erori de parsare`}
                description={
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    {parseErrors.slice(0, 5).map((e, i) => (
                      <li key={i}>
                        {e.row != null ? `Rând ${e.row}` : ""}
                        {e.col ? `, coloana "${e.col}"` : ""}: {e.message}
                      </li>
                    ))}
                    {parseErrors.length > 5 && (
                      <li>...și încă {parseErrors.length - 5} erori</li>
                    )}
                  </ul>
                }
              />
            )}

            <Table
              dataSource={previewItems}
              rowKey="row_index"
              size="small"
              scroll={{ x: 800 }}
              pagination={{ pageSize: 20, showSizeChanger: true }}
              columns={[
                {
                  title: "#",
                  dataIndex: "row_index",
                  key: "row_index",
                  width: 50,
                },
                {
                  title: "Status",
                  key: "status",
                  width: 80,
                  render: (_: unknown, r: ImportPreviewItem) =>
                    r.is_valid ? (
                      <Tag color="green" icon={<CheckCircleOutlined />}>OK</Tag>
                    ) : (
                      <Tooltip title={r.errors?.map((e) => e.message).join("; ")}>
                        <Tag color="red" icon={<CloseCircleOutlined />}>Eroare</Tag>
                      </Tooltip>
                    ),
                },
                { title: "Cod", dataIndex: "code", key: "code", width: 100 },
                {
                  title: "Denumire",
                  dataIndex: "description",
                  key: "description",
                  ellipsis: true,
                },
                { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 60 },
                {
                  title: "Cantitate",
                  dataIndex: "quantity",
                  key: "qty",
                  width: 90,
                  align: "right" as const,
                  render: (v: number) => v?.toLocaleString("ro-RO"),
                },
                {
                  title: "Preț unitar",
                  dataIndex: "unit_price",
                  key: "price",
                  width: 100,
                  align: "right" as const,
                  render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
                },
                {
                  title: "Total",
                  dataIndex: "total",
                  key: "total",
                  width: 110,
                  align: "right" as const,
                  render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
                },
                {
                  title: "Duplicat",
                  key: "dup",
                  width: 80,
                  render: (_: unknown, r: ImportPreviewItem) =>
                    r.is_duplicate ? (
                      <Tag color="orange">Duplicat</Tag>
                    ) : null,
                },
              ]}
              rowClassName={(r: ImportPreviewItem) =>
                !r.is_valid ? "ant-table-row-error" : r.is_duplicate ? "ant-table-row-warning" : ""
              }
            />
          </>
        )}
      </div>
    );
  };

  // ─── Step 2: WBS Mapping ──────────────────────────────────────────────────

  const renderWBSMapping = () => {
    const validItems = previewItems.filter((i) => i.is_valid);
    return (
      <div>
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Text strong>Asociere articole → noduri WBS</Text>
              <Badge
                count={`${matchedCount}/${validItems.length} asociate`}
                style={{ backgroundColor: matchedCount === validItems.length ? "#52c41a" : "#1677ff" }}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<LinkOutlined />}
                onClick={() => autoMatchMut.mutate()}
                loading={autoMatchMut.isPending}
              >
                Auto-Match WBS
              </Button>
              {duplicateCount > 0 && (
                <Select
                  value={duplicateAction}
                  onChange={(v) => setDuplicateAction(v)}
                  style={{ width: 200 }}
                  options={DUPLICATE_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
                />
              )}
            </Space>
          </Col>
        </Row>

        {duplicateCount > 0 && (
          <Alert
            type="warning"
            showIcon
            icon={<WarningOutlined />}
            style={{ marginBottom: 16 }}
            message={`${duplicateCount} articole duplicate detectate — acțiune: ${DUPLICATE_OPTIONS.find((o) => o.value === duplicateAction)?.label}`}
          />
        )}

        <Table
          dataSource={validItems}
          rowKey="row_index"
          size="small"
          scroll={{ x: 900 }}
          pagination={{ pageSize: 25, showSizeChanger: true }}
          columns={[
            { title: "Cod", dataIndex: "code", key: "code", width: 90 },
            {
              title: "Articol import",
              dataIndex: "description",
              key: "description",
              ellipsis: true,
              width: 250,
            },
            { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 50 },
            {
              title: "Cantitate",
              dataIndex: "quantity",
              key: "qty",
              width: 80,
              align: "right" as const,
              render: (v: number) => v?.toLocaleString("ro-RO"),
            },
            {
              title: "Preț unitar",
              dataIndex: "unit_price",
              key: "price",
              width: 90,
              align: "right" as const,
              render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
            },
            {
              title: "Nod WBS",
              key: "wbs",
              width: 200,
              render: (_: unknown, r: ImportPreviewItem) => (
                <Select
                  value={r.wbs_node_id ?? undefined}
                  onChange={(val) => updateItemWBS(r.row_index, val, val)}
                  placeholder="Selectează nod WBS"
                  allowClear
                  style={{ width: "100%" }}
                  showSearch
                  optionFilterProp="label"
                  options={[
                    { value: "fundatii", label: "1. Fundații" },
                    { value: "structura", label: "2. Structură" },
                    { value: "inchideri", label: "3. Închideri" },
                    { value: "instalatii", label: "4. Instalații" },
                    { value: "finisaje", label: "5. Finisaje" },
                  ]}
                />
              ),
            },
            {
              title: "Match",
              key: "match",
              width: 70,
              render: (_: unknown, r: ImportPreviewItem) => {
                if (!r.wbs_node_id) return <Tag>—</Tag>;
                if (r.match_score && r.match_score >= 0.7)
                  return <Tag color="green">Auto</Tag>;
                return <Tag color="blue">Manual</Tag>;
              },
            },
            {
              title: "Duplicat",
              key: "dup",
              width: 70,
              render: (_: unknown, r: ImportPreviewItem) =>
                r.is_duplicate ? <Tag color="orange">DA</Tag> : null,
            },
          ]}
        />
      </div>
    );
  };

  // ─── Step 3: Confirmation ─────────────────────────────────────────────────

  const renderConfirmation = () => {
    if (importComplete) {
      return (
        <Result
          status="success"
          title="Import finalizat cu succes!"
          subTitle={`${importedCount} articole importate în devizul proiectului`}
          extra={[
            <Button
              type="primary"
              key="back"
              onClick={() => navigate(`/pm/projects/${projectId}/budget`)}
            >
              Vezi Deviz
            </Button>,
            <Button key="new" onClick={() => {
              setCurrentStep(0);
              setSelectedSource(null);
              setSessionId(null);
              setPreviewItems([]);
              setParseErrors([]);
              setImportComplete(false);
            }}>
              Import Nou
            </Button>,
          ]}
        />
      );
    }

    const validItems = previewItems.filter((i) => i.is_valid);
    const totalValue = validItems.reduce((s, i) => s + i.total, 0);

    return (
      <div>
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
          message="Revizuire finală — Confirmă importul"
          description="Verifică totalurile și confirmă importul articolelor în deviz."
        />

        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Articole de importat"
                value={validItems.length}
                suffix={`/ ${totalRows}`}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Asociate WBS"
                value={matchedCount}
                suffix={`/ ${validItems.length}`}
                valueStyle={{ color: matchedCount === validItems.length ? "#52c41a" : "#fa8c16" }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Duplicate"
                value={duplicateCount}
                valueStyle={{ color: duplicateCount > 0 ? "#fa8c16" : undefined }}
              />
              {duplicateCount > 0 && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Acțiune: {DUPLICATE_OPTIONS.find((o) => o.value === duplicateAction)?.label}
                </Text>
              )}
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Valoare totală"
                value={totalValue}
                precision={2}
                suffix="RON"
                valueStyle={{ color: "#1677ff" }}
              />
            </Card>
          </Col>
        </Row>

        <Table
          dataSource={validItems}
          rowKey="row_index"
          size="small"
          pagination={{ pageSize: 15 }}
          scroll={{ x: 700 }}
          columns={[
            { title: "Cod", dataIndex: "code", key: "code", width: 90 },
            {
              title: "Denumire",
              dataIndex: "description",
              key: "desc",
              ellipsis: true,
            },
            { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 50 },
            {
              title: "Cantitate",
              dataIndex: "quantity",
              key: "qty",
              width: 80,
              align: "right" as const,
              render: (v: number) => v?.toLocaleString("ro-RO"),
            },
            {
              title: "Total",
              dataIndex: "total",
              key: "total",
              width: 110,
              align: "right" as const,
              render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }),
            },
            {
              title: "Nod WBS",
              dataIndex: "wbs_node_name",
              key: "wbs",
              width: 150,
              render: (v: string) => v ?? <Text type="secondary">Neasociat</Text>,
            },
          ]}
          summary={() => (
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={4}>
                <Text strong>TOTAL</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={1} align="right">
                <Text strong>{totalValue.toLocaleString("ro-RO", { minimumFractionDigits: 2 })}</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={2} />
            </Table.Summary.Row>
          )}
        />

        {confirmMut.isPending && (
          <div style={{ textAlign: "center", padding: 24 }}>
            <Progress percent={50} status="active" />
            <Text>Se importează articolele...</Text>
          </div>
        )}
      </div>
    );
  };

  // ─── Step content map ─────────────────────────────────────────────────────

  const stepContent = [
    renderSourceSelection,
    renderUploadPreview,
    renderWBSMapping,
    renderConfirmation,
  ];

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ padding: 24 }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(`/pm/projects/${projectId}/budget`)}
            >
              Înapoi la Deviz
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              Import Engine — Devize (E-037 / F123)
            </Title>
          </Space>
        </Col>
      </Row>

      <Card style={{ marginBottom: 24 }}>
        <Steps
          current={currentStep}
          items={[
            { title: "Selectare Sursă", description: "Format import" },
            { title: "Upload + Preview", description: "Parsare fișier" },
            { title: "Mapping WBS", description: "Asociere noduri" },
            { title: "Confirmare", description: "Import final" },
          ]}
        />
      </Card>

      <Card>{stepContent[currentStep]!()}</Card>

      {/* Navigation buttons */}
      {!importComplete && (
        <Row justify="space-between" style={{ marginTop: 16 }}>
          <Col>
            {currentStep > 0 && currentStep < 3 && (
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => setCurrentStep((s) => s - 1)}
              >
                Înapoi
              </Button>
            )}
          </Col>
          <Col>
            {currentStep === 0 && (
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                disabled={!canProceedStep1}
                onClick={() => setCurrentStep(1)}
              >
                Continuă
              </Button>
            )}
            {currentStep === 1 && sessionId && (
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                disabled={!canProceedStep2}
                onClick={() => setCurrentStep(2)}
              >
                Continuă la Mapping
              </Button>
            )}
            {currentStep === 2 && (
              <Button
                type="primary"
                icon={<ImportOutlined />}
                onClick={() => confirmMut.mutate()}
                loading={confirmMut.isPending}
              >
                Confirmă Import ({previewItems.filter((i) => i.is_valid).length} articole)
              </Button>
            )}
          </Col>
        </Row>
      )}
    </div>
  );
}
