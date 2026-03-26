import { useState, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Typography,
  Input,
  Select,
  Button,
  Table,
  Tag,
  Space,
  Row,
  Col,
  Card,
  App,
  Badge,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  ExportOutlined,
  DeleteOutlined,
  UserOutlined,
  BankOutlined,
  WarningOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService, type ContactFilters } from "../../../services/contactService";
import type { ContactListItem } from "../../../types";
import type { ColumnsType } from "antd/es/table";
import ImportExportContacts from "../components/ImportExportContacts";
import { useTranslation } from "../../../i18n";
import { confirmDelete } from "../../../components/ConfirmDelete";
import EmptyState from "../../../components/EmptyState";

const STAGE_COLORS: Record<string, string> = {
  prospect: "blue",
  active: "green",
  inactive: "default",
  client: "green",
  partner: "purple",
  lead: "cyan",
};

const TYPE_ICONS: Record<string, React.ReactNode> = {
  company: <BankOutlined />,
  individual: <UserOutlined />,
};

export default function ContactsListPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const t = useTranslation();

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const filters: ContactFilters = useMemo(
    () => ({
      page: Number(searchParams.get("page")) || 1,
      per_page: Number(searchParams.get("per_page")) || 20,
      search: searchParams.get("search") || undefined,
      stage: searchParams.get("stage") || undefined,
      contact_type: searchParams.get("contact_type") || undefined,
      city: searchParams.get("city") || undefined,
      county: searchParams.get("county") || undefined,
      source: searchParams.get("source") || undefined,
    }),
    [searchParams]
  );

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["contacts", filters],
    queryFn: () => contactService.list(filters),
  });

  const deleteMutation = useMutation({
    mutationFn: contactService.delete,
    onSuccess: () => {
      message.success("Contact șters.");
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
      setSelectedRowKeys([]);
    },
    onError: () => message.error("Eroare la ștergere."),
  });

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

  const columns: ColumnsType<ContactListItem> = [
    {
      title: "Nume companie",
      dataIndex: "company_name",
      key: "company_name",
      sorter: (a, b) => a.company_name.localeCompare(b.company_name),
      render: (text: string, record: ContactListItem) => (
        <Space>
          <a onClick={() => navigate(`/crm/contacts/${record.id}`)}>{text}</a>
        </Space>
      ),
    },
    {
      title: "CUI",
      dataIndex: "cui",
      key: "cui",
      width: 130,
      render: (cui: string) => cui || "—",
    },
    {
      title: "Tip",
      dataIndex: "contact_type",
      key: "contact_type",
      width: 120,
      render: (type: string) => (
        <Tag icon={TYPE_ICONS[type]}>
          {type === "company" ? "Companie" : "Persoană"}
        </Tag>
      ),
    },
    {
      title: "Localitate",
      dataIndex: "city",
      key: "city",
      width: 140,
      render: (city: string, record: ContactListItem) =>
        [city, record.county].filter(Boolean).join(", ") || "—",
    },
    {
      title: "Status",
      dataIndex: "stage",
      key: "stage",
      width: 110,
      render: (stage: string) => (
        <Tag color={STAGE_COLORS[stage] || "default"}>
          {stage?.charAt(0).toUpperCase() + stage?.slice(1)}
        </Tag>
      ),
    },
    {
      title: "Email",
      dataIndex: "email",
      key: "email",
      width: 200,
      ellipsis: true,
      render: (email: string) => email || "—",
    },
    {
      title: "Telefon",
      dataIndex: "phone",
      key: "phone",
      width: 140,
      render: (phone: string) => phone || "—",
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
      width: 60,
      render: (_: unknown, record: ContactListItem) => (
        <Tooltip title="Șterge">
          <Button
            type="text"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              confirmDelete({
                title: `Șterge ${record.company_name}?`,
                content: "Contactul și toate datele asociate vor fi șterse permanent.",
                onOk: () => deleteMutation.mutate(record.id),
              });
            }}
          />
        </Tooltip>
      ),
    },
  ];

  const contacts = data?.data || [];
  const total = data?.meta?.total || 0;

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          {t.nav.contacts}
        </Typography.Title>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </Tooltip>
          <ImportExportContacts />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate("/crm/contacts/new")}
          >
            Contact nou
          </Button>
        </Space>
      </Row>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Input
              placeholder="Caută nume, CUI, email..."
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
              value={filters.stage}
              onChange={(v) => updateFilter("stage", v)}
              options={[
                { label: "Prospect", value: "prospect" },
                { label: "Activ", value: "active" },
                { label: "Client", value: "client" },
                { label: "Inactiv", value: "inactive" },
                { label: "Partener", value: "partner" },
              ]}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Tip"
              allowClear
              style={{ width: "100%" }}
              value={filters.contact_type}
              onChange={(v) => updateFilter("contact_type", v)}
              options={[
                { label: "Companie", value: "company" },
                { label: "Persoană", value: "individual" },
              ]}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Input
              placeholder="Localitate"
              allowClear
              value={filters.city || ""}
              onChange={(e) => updateFilter("city", e.target.value || undefined)}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Input
              placeholder="Județ"
              allowClear
              value={filters.county || ""}
              onChange={(e) => updateFilter("county", e.target.value || undefined)}
            />
          </Col>
          <Col xs={12} sm={6} md={4} lg={3}>
            <Select
              placeholder="Sursă"
              allowClear
              style={{ width: "100%" }}
              value={filters.source}
              onChange={(v) => updateFilter("source", v)}
              options={[
                { label: "Referral", value: "referral" },
                { label: "Website", value: "website" },
                { label: "Cold Call", value: "cold_call" },
                { label: "Eveniment", value: "event" },
                { label: "Partener", value: "partner" },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {selectedRowKeys.length > 0 && (
        <Card
          size="small"
          style={{
            marginBottom: 12,
            background: "#e6f4ff",
            border: "1px solid #91caff",
          }}
        >
          <Space>
            <Badge count={selectedRowKeys.length} style={{ backgroundColor: "#1677ff" }}>
              <WarningOutlined />
            </Badge>
            <Typography.Text strong>{selectedRowKeys.length} selectate</Typography.Text>
            <Button size="small" icon={<ExportOutlined />}>
              Export selecție
            </Button>
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() =>
                confirmDelete({
                  title: `Șterge ${selectedRowKeys.length} contacte?`,
                  content: "Toate contactele selectate vor fi șterse permanent.",
                  onOk: () => {
                    selectedRowKeys.forEach((key) => deleteMutation.mutate(String(key)));
                  },
                })
              }
            >
              Șterge
            </Button>
            <Button size="small" type="link" onClick={() => setSelectedRowKeys([])}>
              Deselectează
            </Button>
          </Space>
        </Card>
      )}

      <Table<ContactListItem>
        rowKey="id"
        columns={columns}
        dataSource={contacts}
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
          pageSizeOptions: ["10", "20", "50", "100"],
          showTotal: (t) => `Total: ${t} contacte`,
          onChange: (page, pageSize) => {
            const params = new URLSearchParams(searchParams);
            params.set("page", String(page));
            params.set("per_page", String(pageSize));
            setSearchParams(params);
          },
        }}
        onRow={(record) => ({
          onClick: () => navigate(`/crm/contacts/${record.id}`),
          style: { cursor: "pointer" },
        })}
        scroll={{ x: 1000 }}
        locale={{
          emptyText: filters.search ? (
            <EmptyState
              title="Niciun contact nu corespunde filtrelor"
              description="Încearcă alte criterii de căutare."
              actionLabel="Resetează filtrele"
              onAction={() => setSearchParams(new URLSearchParams())}
              compact
            />
          ) : (
            <EmptyState
              title="Niciun contact încă"
              description="Adaugă primul contact pentru a începe."
              actionLabel="Adaugă contact"
              onAction={() => navigate("/crm/contacts/new")}
            />
          ),
        }}
      />
    </>
  );
}
