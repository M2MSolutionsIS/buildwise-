/**
 * Offers List Page — part of Pipeline module
 * F-codes: F019 (Offer Builder entry), F029 (Offers Analytics overview)
 */
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Input,
  Select,
  Row,
  Col,
  Statistic,
  Typography,
  Popconfirm,
  message,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  ThunderboltOutlined,
  DeleteOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { offerService } from "../services/offerService";
import type { OfferListItem, OfferStatus } from "../../../types";
import type { ColumnsType } from "antd/es/table";

const { Title } = Typography;

const STATUS_COLORS: Record<string, string> = {
  DRAFT: "default",
  PENDING_APPROVAL: "processing",
  APPROVED: "cyan",
  SENT: "blue",
  NEGOTIATION: "orange",
  ACCEPTED: "success",
  REJECTED: "error",
  EXPIRED: "default",
};

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  PENDING_APPROVAL: "Așteptare aprobare",
  APPROVED: "Aprobată",
  SENT: "Trimisă",
  NEGOTIATION: "Negociere",
  ACCEPTED: "Acceptată",
  REJECTED: "Refuzată",
  EXPIRED: "Expirată",
};

export default function OffersListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const page = parseInt(searchParams.get("page") || "1", 10);
  const search = searchParams.get("search") || "";
  const statusFilter = searchParams.get("status") || "";

  const { data, isLoading } = useQuery({
    queryKey: ["offers", { page, search, status: statusFilter }],
    queryFn: () =>
      offerService.list({
        page,
        per_page: 20,
        search: search || undefined,
        status: statusFilter || undefined,
      }),
  });

  const { data: analyticsData } = useQuery({
    queryKey: ["offers-analytics"],
    queryFn: () => offerService.getAnalytics(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => offerService.delete(id),
    onSuccess: () => {
      message.success("Ofertă ștearsă");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  const offers = data?.data || [];
  const total = data?.meta?.total || 0;
  const analytics = analyticsData?.data;

  const updateParams = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.set("page", "1");
    setSearchParams(next);
  };

  const columns: ColumnsType<OfferListItem> = [
    {
      title: "Nr. ofertă",
      dataIndex: "offer_number",
      key: "offer_number",
      render: (val: string, record) => (
        <a onClick={() => navigate(`/pipeline/offers/${record.id}`)}>{val}</a>
      ),
    },
    { title: "Titlu", dataIndex: "title", key: "title", ellipsis: true },
    {
      title: "Versiune",
      dataIndex: "version",
      key: "version",
      width: 80,
      render: (v: number) => `v${v}`,
    },
    {
      title: "Total",
      dataIndex: "total_amount",
      key: "total",
      width: 140,
      render: (v: number, r) =>
        `${v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} ${r.currency}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 140,
      render: (s: OfferStatus) => (
        <Tag color={STATUS_COLORS[s] || "default"}>
          {STATUS_LABELS[s] || s}
        </Tag>
      ),
    },
    {
      title: "Data",
      dataIndex: "created_at",
      key: "created_at",
      width: 110,
      render: (d: string) => new Date(d).toLocaleDateString("ro-RO"),
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/pipeline/offers/${record.id}`)}
          />
          {record.status === "DRAFT" && (
            <Popconfirm title="Ștergi oferta?" onConfirm={() => deleteMutation.mutate(record.id)}>
              <Button type="text" size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            Oferte
          </Title>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ThunderboltOutlined />}
              onClick={() => navigate("/pipeline/offers/new?quick=true")}
            >
              Ofertă rapidă
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate("/pipeline/offers/new")}
            >
              Ofertă nouă
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Analytics cards (F029) */}
      {analytics && (
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={12} md={6}>
            <Card size="small">
              <Statistic title="Total oferte" value={analytics.total_offers} />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small">
              <Statistic
                title="Valoare totală"
                value={analytics.total_value}
                precision={0}
                suffix="RON"
              />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small">
              <Statistic title="Valoare medie" value={analytics.average_value} precision={0} suffix="RON" />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small">
              <Statistic
                title="Rată conversie"
                value={analytics.conversion_rate}
                precision={1}
                suffix="%"
                valueStyle={{ color: analytics.conversion_rate >= 30 ? "#3f8600" : "#cf1322" }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <Input
            placeholder="Caută după nr. ofertă, titlu..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => updateParams("search", e.target.value)}
            allowClear
          />
        </Col>
        <Col>
          <Select
            placeholder="Status"
            value={statusFilter || undefined}
            onChange={(val) => updateParams("status", val || "")}
            allowClear
            style={{ width: 180 }}
            options={Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }))}
          />
        </Col>
      </Row>

      <Table<OfferListItem>
        rowKey="id"
        columns={columns}
        dataSource={offers}
        loading={isLoading}
        pagination={{
          current: page,
          pageSize: 20,
          total,
          onChange: (p) => updateParams("page", String(p)),
          showSizeChanger: false,
          showTotal: (t) => `${t} oferte`,
        }}
        onRow={(record) => ({
          onClick: () => navigate(`/pipeline/offers/${record.id}`),
          style: { cursor: "pointer" },
        })}
      />
    </div>
  );
}
