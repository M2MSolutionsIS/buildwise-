/**
 * Livrări Materiale — parte din F074 (urmărire livrări)
 * Tracking deliveries received on site, linked to Daily Reports (F077).
 *
 * Shows all material deliveries aggregated from daily reports + standalone entries.
 */
import { useMemo } from "react";
import {
  Card,
  Table,
  Tag,
  Space,
  Statistic,
  Row,
  Col,
  Typography,
  Empty,
} from "antd";
import {
  TruckOutlined,
  InboxOutlined,
  CalendarOutlined,
  ShopOutlined,
} from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import type { MaterialDelivery } from "../../../types";
import dayjs from "dayjs";

const { Title, Text } = Typography;

interface DeliveryRow extends MaterialDelivery {
  id: string;
  report_date: string;
  report_id: string;
}

export default function DeliveriesPage() {
  const { projectId } = useParams<{ projectId: string }>();

  // ─── Queries ────────────────────────────────────────────────────────────────

  const { data: reportsRes, isLoading } = useQuery({
    queryKey: ["daily-reports", projectId],
    queryFn: () => pmService.listDailyReports(projectId!),
    enabled: !!projectId,
  });

  const reports = reportsRes?.data ?? [];

  // Extract all deliveries from daily reports
  const deliveries: DeliveryRow[] = useMemo(() => {
    const rows: DeliveryRow[] = [];
    reports.forEach((report) => {
      if (report.materials_received && Array.isArray(report.materials_received)) {
        report.materials_received.forEach((delivery, idx) => {
          rows.push({
            ...delivery,
            id: `${report.id}-${idx}`,
            report_date: report.report_date,
            report_id: report.id,
          });
        });
      }
    });
    return rows.sort(
      (a, b) => dayjs(b.report_date).unix() - dayjs(a.report_date).unix()
    );
  }, [reports]);

  // ─── Stats ──────────────────────────────────────────────────────────────────

  const totalDeliveries = deliveries.length;
  const uniqueMaterials = useMemo(
    () => new Set(deliveries.map((d) => d.material_name)).size,
    [deliveries]
  );
  const uniqueSuppliers = useMemo(
    () => new Set(deliveries.filter((d) => d.supplier).map((d) => d.supplier)).size,
    [deliveries]
  );
  const totalQuantity = useMemo(
    () => deliveries.reduce((s, d) => s + d.quantity, 0),
    [deliveries]
  );

  // ─── By supplier aggregation ──────────────────────────────────────────────

  const bySupplier = useMemo(() => {
    const map = new Map<string, { count: number; materials: Set<string> }>();
    deliveries.forEach((d) => {
      const sup = d.supplier ?? "Necunoscut";
      if (!map.has(sup)) map.set(sup, { count: 0, materials: new Set() });
      const entry = map.get(sup)!;
      entry.count++;
      entry.materials.add(d.material_name);
    });
    return Array.from(map.entries()).map(([supplier, data]) => ({
      supplier,
      count: data.count,
      materialsCount: data.materials.size,
    }));
  }, [deliveries]);

  // ─── Columns ────────────────────────────────────────────────────────────────

  const columns = [
    {
      title: "Data livrare",
      dataIndex: "report_date",
      key: "date",
      width: 120,
      render: (d: string) => dayjs(d).format("DD.MM.YYYY"),
      sorter: (a: DeliveryRow, b: DeliveryRow) =>
        dayjs(a.report_date).unix() - dayjs(b.report_date).unix(),
      defaultSortOrder: "descend" as const,
    },
    {
      title: "Material",
      dataIndex: "material_name",
      key: "material",
      width: 200,
      render: (name: string) => <Text strong>{name}</Text>,
      filters: [...new Set(deliveries.map((d) => d.material_name))].map((n) => ({
        text: n,
        value: n,
      })),
      onFilter: (value: unknown, record: DeliveryRow) =>
        record.material_name === value,
    },
    {
      title: "Cantitate",
      dataIndex: "quantity",
      key: "qty",
      width: 100,
      align: "right" as const,
      render: (v: number) => <Text strong>{v.toFixed(2)}</Text>,
    },
    {
      title: "U.M.",
      dataIndex: "unit_of_measure",
      key: "um",
      width: 80,
    },
    {
      title: "Furnizor",
      dataIndex: "supplier",
      key: "supplier",
      width: 160,
      render: (s?: string) =>
        s ? (
          <Tag icon={<ShopOutlined />} color="blue">
            {s}
          </Tag>
        ) : (
          <Text type="secondary">—</Text>
        ),
      filters: bySupplier.map((s) => ({ text: s.supplier, value: s.supplier })),
      onFilter: (value: unknown, record: DeliveryRow) =>
        (record.supplier ?? "Necunoscut") === value,
    },
    {
      title: "Aviz / Notă",
      dataIndex: "delivery_note",
      key: "note",
      ellipsis: true,
      render: (v?: string) => v ?? "—",
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <TruckOutlined /> Livrări Materiale (F074)
      </Title>

      {/* Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total livrări"
              value={totalDeliveries}
              prefix={<TruckOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Materiale distincte"
              value={uniqueMaterials}
              prefix={<InboxOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Furnizori"
              value={uniqueSuppliers}
              prefix={<ShopOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Cantitate totală"
              value={totalQuantity}
              precision={0}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Supplier summary */}
      {bySupplier.length > 0 && (
        <Card
          size="small"
          title="Rezumat per furnizor"
          style={{ marginBottom: 16 }}
        >
          <Space wrap>
            {bySupplier.map((s) => (
              <Tag key={s.supplier} color="blue">
                {s.supplier}: {s.count} livrări, {s.materialsCount} materiale
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* Deliveries table */}
      <Card title="Toate livrările">
        <Table
          columns={columns}
          dataSource={deliveries}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 20, showSizeChanger: true }}
          size="middle"
          locale={{
            emptyText: (
              <Empty
                description="Nicio livrare înregistrată. Adaugă livrări din Raportul Zilnic de Șantier."
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ),
          }}
        />
      </Card>
    </div>
  );
}
