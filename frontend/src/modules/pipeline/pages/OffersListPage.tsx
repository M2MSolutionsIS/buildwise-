import { useState, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Typography,
  Table,
  Tag,
  Button,
  Space,
  Row,
  Col,
  Card,
  Input,
  Select,
  Popconfirm,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useOffers, useDeleteOffer } from "../hooks/useOffers";
import type { OfferListItem, OfferStatus } from "../../../types/pipeline";
import type { ColumnsType } from "antd/es/table";
import type { OfferFilters } from "../services/offerService";

const STATUS_COLORS: Record<OfferStatus, string> = {
  draft: "default",
  pending_approval: "processing",
  approved: "blue",
  sent: "cyan",
  negotiation: "orange",
  accepted: "green",
  rejected: "red",
  expired: "red",
};

const STATUS_LABELS: Record<OfferStatus, string> = {
  draft: "Draft",
  pending_approval: "Aprobare",
  approved: "Aprobată",
  sent: "Trimisă",
  negotiation: "Negociere",
  accepted: "Acceptată",
  rejected: "Refuzată",
  expired: "Expirată",
};

export default function OffersListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const filters: OfferFilters = useMemo(
    () => ({
      page: Number(searchParams.get("page")) || 1,
      per_page: Number(searchParams.get("per_page")) || 20,
      search: searchParams.get("search") || undefined,
      status: searchParams.get("status") || undefined,
    }),
    [searchParams]
  );

  const { data, isLoading, refetch } = useOffers(filters);
  const deleteMutation = useDeleteOffer();

  const updateFilter = (key: string, value: string | undefined) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.set("page", "1");
    setSearchParams(params);
  };

  const columns: ColumnsType<OfferListItem> = [
    {
      title: "Nr. ofertă",
      dataIndex: "offer_number",
      key: "offer_number",
      width: 140,
      render: (text: string, record: OfferListItem) => (
        <a onClick={() => navigate(`/pipeline/offers/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: "Titlu",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
      render: (text: string, record: OfferListItem) => (
        <Space>
          <a onClick={() => navigate(`/pipeline/offers/${record.id}`)}>{text}</a>
          {record.version > 1 && <Tag>v{record.version}</Tag>}
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 110,
      render: (status: OfferStatus) => (
        <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
      ),
    },
    {
      title: "Total",
      dataIndex: "total_amount",
      key: "total_amount",
      width: 140,
      align: "right",
      sorter: (a, b) => a.total_amount - b.total_amount,
      render: (value: number, record: OfferListItem) =>
        new Intl.NumberFormat("ro-RO", {
          style: "currency",
          currency: record.currency,
        }).format(value),
    },
    {
      title: "Creat",
      dataIndex: "created_at",
      key: "created_at",
      width: 110,
      sorter: (a, b) => a.created_at.localeCompare(b.created_at),
      defaultSortOrder: "descend",
      render: (date: string) =>
        new Date(date).toLocaleDateString("ro-RO", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }),
    },
    {
      title: "",
      key: "actions",
      width: 50,
      render: (_: unknown, record: OfferListItem) =>
        record.status === "draft" ? (
          <Popconfirm
            title="Sigur vrei să ștergi?"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="Da"
            cancelText="Nu"
          >
            <Tooltip title="Șterge">
              <Button type="text" danger size="small" icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        ) : null,
    },
  ];

  const offers = data?.data || [];
  const total = data?.meta?.total || 0;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Oferte
        </Typography.Title>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </Tooltip>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate("/pipeline/offers/new")}
          >
            Ofertă nouă
          </Button>
        </Space>
      </Row>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input
              placeholder="Caută nr. ofertă, titlu..."
              prefix={<SearchOutlined />}
              allowClear
              value={filters.search || ""}
              onChange={(e) => updateFilter("search", e.target.value || undefined)}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: "100%" }}
              value={filters.status}
              onChange={(v) => updateFilter("status", v)}
              options={Object.entries(STATUS_LABELS).map(([value, label]) => ({
                value,
                label,
              }))}
            />
          </Col>
        </Row>
      </Card>

      <Table<OfferListItem>
        rowKey="id"
        columns={columns}
        dataSource={offers}
        loading={isLoading}
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        pagination={{
          current: filters.page,
          pageSize: filters.per_page,
          total,
          showSizeChanger: true,
          pageSizeOptions: ["10", "20", "50"],
          showTotal: (t) => `Total: ${t} oferte`,
          onChange: (page, pageSize) => {
            const params = new URLSearchParams(searchParams);
            params.set("page", String(page));
            params.set("per_page", String(pageSize));
            setSearchParams(params);
          },
        }}
        onRow={(record) => ({
          onClick: () => navigate(`/pipeline/offers/${record.id}`),
          style: { cursor: "pointer" },
        })}
        scroll={{ x: 800 }}
        locale={{
          emptyText: (
            <Space direction="vertical" style={{ padding: 32 }}>
              <Typography.Text type="secondary">Nicio ofertă încă</Typography.Text>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate("/pipeline/offers/new")}
              >
                Creează prima ofertă
              </Button>
            </Space>
          ),
        }}
      />
    </>
  );
}
