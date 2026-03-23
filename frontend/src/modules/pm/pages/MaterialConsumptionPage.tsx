/**
 * E-019 — Fișe Consum Materiale — Materials Consumption Tracking
 * F074: Consum real per WBS, urmărire livrări, alertă depășire (>10%).
 *
 * Table: material, planned qty, consumed qty, remaining, difference %, status indicator.
 * Modal: Înregistrare Consum (E-019.M1).
 * Alert banner for overage >10%.
 */
import { useState, useMemo } from "react";
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
  DatePicker,
  Select,
  Statistic,
  Row,
  Col,
  message,
  Alert,
  Progress,
  Typography,
  Tooltip,
  Popconfirm,
} from "antd";
import {
  PlusOutlined,
  WarningOutlined,
  DeleteOutlined,
  ExperimentOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  InboxOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { MaterialConsumption } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

const OVERAGE_THRESHOLD = 10; // %

interface AggregatedMaterial {
  material_name: string;
  unit_of_measure: string;
  planned_quantity: number;
  consumed_quantity: number;
  remaining: number;
  difference_pct: number;
  total_cost: number;
  entries: MaterialConsumption[];
  isOverage: boolean;
}

export default function MaterialConsumptionPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: consumptionRes, isLoading } = useQuery({
    queryKey: ["consumptions", projectId],
    queryFn: () => pmService.listConsumptions(projectId!),
    enabled: !!projectId,
  });

  const entries = consumptionRes?.data ?? [];

  // ─── Mutations ──────────────────────────────────────────────────────────────

  const createMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      pmService.createConsumption(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["consumptions", projectId] });
      message.success("Consum înregistrat");
      setIsModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la salvare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteConsumption(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["consumptions", projectId] });
      message.success("Înregistrare ștearsă");
    },
  });

  // ─── Aggregate by material name ─────────────────────────────────────────────

  const aggregated: AggregatedMaterial[] = useMemo(() => {
    const map = new Map<string, MaterialConsumption[]>();
    entries.forEach((e) => {
      const key = e.material_name;
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(e);
    });

    return Array.from(map.entries()).map(([name, items]) => {
      const planned = Math.max(...items.map((i) => i.planned_quantity), 0);
      const consumed = items.reduce((s, i) => s + i.consumed_quantity, 0);
      const remaining = planned - consumed;
      const diffPct = planned > 0 ? ((consumed - planned) / planned) * 100 : 0;
      const cost = items.reduce((s, i) => s + (i.total_cost ?? 0), 0);

      return {
        material_name: name,
        unit_of_measure: items[0]?.unit_of_measure ?? "",
        planned_quantity: planned,
        consumed_quantity: consumed,
        remaining,
        difference_pct: diffPct,
        total_cost: cost,
        entries: items,
        isOverage: diffPct > OVERAGE_THRESHOLD,
      };
    });
  }, [entries]);

  const overageItems = aggregated.filter((a) => a.isOverage);

  const totalPlanned = aggregated.reduce((s, a) => s + a.planned_quantity, 0);
  const totalConsumed = aggregated.reduce((s, a) => s + a.consumed_quantity, 0);
  const totalCost = aggregated.reduce((s, a) => s + a.total_cost, 0);

  // ─── Table columns ─────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Material",
      dataIndex: "material_name",
      key: "material",
      width: 220,
      render: (name: string, rec: AggregatedMaterial) => (
        <Space>
          {rec.isOverage && (
            <Tooltip title="Depășire consum >10%">
              <WarningOutlined style={{ color: "#ff4d4f" }} />
            </Tooltip>
          )}
          <Text strong={rec.isOverage} type={rec.isOverage ? "danger" : undefined}>
            {name}
          </Text>
        </Space>
      ),
    },
    {
      title: "U.M.",
      dataIndex: "unit_of_measure",
      key: "um",
      width: 80,
    },
    {
      title: "Cantitate planificată",
      dataIndex: "planned_quantity",
      key: "planned",
      width: 140,
      align: "right" as const,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: "Consumat",
      dataIndex: "consumed_quantity",
      key: "consumed",
      width: 120,
      align: "right" as const,
      render: (v: number, rec: AggregatedMaterial) => (
        <Text type={rec.isOverage ? "danger" : undefined} strong>
          {v.toFixed(2)}
        </Text>
      ),
    },
    {
      title: "Rest",
      dataIndex: "remaining",
      key: "remaining",
      width: 100,
      align: "right" as const,
      render: (v: number) => (
        <Text type={v < 0 ? "danger" : "success"}>{v.toFixed(2)}</Text>
      ),
    },
    {
      title: "Diferență %",
      dataIndex: "difference_pct",
      key: "diff",
      width: 140,
      render: (v: number, rec: AggregatedMaterial) => {
        const color =
          v > OVERAGE_THRESHOLD ? "#ff4d4f" : v > 0 ? "#faad14" : "#52c41a";
        return (
          <Space>
            <Progress
              percent={Math.min(
                Math.abs(
                  rec.planned_quantity > 0
                    ? (rec.consumed_quantity / rec.planned_quantity) * 100
                    : 0
                ),
                150
              )}
              size="small"
              strokeColor={color}
              style={{ width: 80 }}
              showInfo={false}
            />
            <Text style={{ color }}>{v > 0 ? "+" : ""}{v.toFixed(1)}%</Text>
          </Space>
        );
      },
    },
    {
      title: "Cost total",
      dataIndex: "total_cost",
      key: "cost",
      width: 120,
      align: "right" as const,
      render: (v: number) => `${v.toFixed(0)} RON`,
    },
    {
      title: "Status",
      key: "status",
      width: 100,
      render: (_: unknown, rec: AggregatedMaterial) => {
        if (rec.isOverage)
          return (
            <Tag color="error" icon={<AlertOutlined />}>
              Depășire
            </Tag>
          );
        if (rec.difference_pct > 0)
          return (
            <Tag color="warning" icon={<WarningOutlined />}>
              Atenție
            </Tag>
          );
        return (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            OK
          </Tag>
        );
      },
    },
  ];

  // Individual entries table (expandable)
  const expandedRowRender = (record: AggregatedMaterial) => {
    const subColumns = [
      {
        title: "Data consum",
        dataIndex: "consumption_date",
        key: "date",
        width: 120,
        render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
      },
      {
        title: "Cantitate",
        dataIndex: "consumed_quantity",
        key: "qty",
        width: 100,
        align: "right" as const,
        render: (v: number) => v.toFixed(2),
      },
      {
        title: "Preț unitar",
        dataIndex: "unit_price",
        key: "price",
        width: 100,
        align: "right" as const,
        render: (v?: number) => (v ? `${v.toFixed(2)} RON` : "—"),
      },
      {
        title: "Cost",
        dataIndex: "total_cost",
        key: "cost",
        width: 100,
        align: "right" as const,
        render: (v?: number) => (v ? `${v.toFixed(0)} RON` : "—"),
      },
      {
        title: "",
        key: "actions",
        width: 60,
        render: (_: unknown, entry: MaterialConsumption) => (
          <Popconfirm
            title="Ștergi această înregistrare?"
            onConfirm={() => deleteMut.mutate(entry.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        ),
      },
    ];
    return (
      <Table
        columns={subColumns}
        dataSource={record.entries}
        rowKey="id"
        pagination={false}
        size="small"
      />
    );
  };

  // ─── Create handler ───────────────────────────────────────────────────────

  const handleCreate = (values: Record<string, unknown>) => {
    const consumptionDate = (values.consumption_date as dayjs.Dayjs).toISOString();
    const qty = values.consumed_quantity as number;
    const price = values.unit_price as number | undefined;
    createMut.mutate({
      ...values,
      consumption_date: consumptionDate,
      total_cost: price ? qty * price : undefined,
    });
  };

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
          <ExperimentOutlined /> Fișe Consum Materiale (E-019)
        </Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          Înregistrare consum
        </Button>
      </div>

      {/* Overage alert */}
      {overageItems.length > 0 && (
        <Alert
          type="error"
          showIcon
          icon={<AlertOutlined />}
          message={`${overageItems.length} materiale depășesc pragul de ${OVERAGE_THRESHOLD}% consum!`}
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {overageItems.map((item) => (
                <li key={item.material_name}>
                  <Text strong>{item.material_name}</Text> — consumat{" "}
                  {item.consumed_quantity.toFixed(2)} din {item.planned_quantity.toFixed(2)}{" "}
                  ({item.difference_pct > 0 ? "+" : ""}
                  {item.difference_pct.toFixed(1)}%)
                </li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Materiale urmărite"
              value={aggregated.length}
              prefix={<InboxOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total planificat"
              value={totalPlanned}
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total consumat"
              value={totalConsumed}
              precision={0}
              valueStyle={
                totalConsumed > totalPlanned ? { color: "#ff4d4f" } : undefined
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Cost total materiale"
              value={totalCost}
              suffix="RON"
              precision={0}
            />
          </Card>
        </Col>
      </Row>

      {/* Aggregated materials table */}
      <Card title="Consum materiale per articol">
        <Table
          columns={columns}
          dataSource={aggregated}
          rowKey="material_name"
          loading={isLoading}
          expandable={{ expandedRowRender }}
          pagination={{ pageSize: 20 }}
          size="middle"
        />
      </Card>

      {/* Modal: Înregistrare Consum (E-019.M1) */}
      <Modal
        title="Înregistrare consum material"
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending}
        okText="Salvează"
        cancelText="Anulează"
        width={520}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="material_name"
            label="Material"
            rules={[{ required: true, message: "Numele materialului" }]}
          >
            <Input placeholder="Ex: Sticlă termoizolantă 6mm" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="unit_of_measure"
                label="Unitate de măsură"
                rules={[{ required: true }]}
              >
                <Select
                  placeholder="U.M."
                  options={[
                    { value: "mp", label: "mp (metru pătrat)" },
                    { value: "ml", label: "ml (metru liniar)" },
                    { value: "buc", label: "buc (bucată)" },
                    { value: "kg", label: "kg (kilogram)" },
                    { value: "l", label: "l (litru)" },
                    { value: "mc", label: "mc (metru cub)" },
                    { value: "set", label: "set" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="consumption_date"
                label="Data consum"
                rules={[{ required: true }]}
                initialValue={dayjs()}
              >
                <DatePicker style={{ width: "100%" }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="planned_quantity"
                label="Cantitate planificată"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={0.5} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="consumed_quantity"
                label="Cantitate consumată"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} step={0.5} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit_price" label="Preț unitar (RON)">
                <InputNumber min={0} step={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
