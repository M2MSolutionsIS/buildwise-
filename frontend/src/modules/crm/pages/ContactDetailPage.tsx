import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import {
  Typography,
  Tabs,
  Space,
  Tag,
  Button,
  Skeleton,
  Avatar,
  Alert,
  Dropdown,
  App,
  Modal,
  Form,
  Input,
  Select,
  Switch,
} from "antd";
import {
  ArrowLeftOutlined,
  PlusOutlined,
  EditOutlined,
  MoreOutlined,
  UserOutlined,
  BankOutlined,
  InfoCircleOutlined,
  HistoryOutlined,
  HomeOutlined,
  FileOutlined,
  DollarOutlined,
  WarningOutlined,
  DeleteOutlined,
  FunnelPlotOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";
import TabDateGenerale from "../components/TabDateGenerale";
import TabIstoricInteractiuni from "../components/TabIstoricInteractiuni";
import TabProprietati from "../components/TabProprietati";
import TabDocumente from "../components/TabDocumente";
import TabOferteContracte from "../components/TabOferteContracte";
import { useState } from "react";

const STAGE_COLORS: Record<string, string> = {
  prospect: "blue",
  active: "green",
  inactive: "default",
  client: "green",
  partner: "purple",
  lead: "cyan",
};

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [addPersonOpen, setAddPersonOpen] = useState(false);
  const [personForm] = Form.useForm();

  const activeTab = searchParams.get("tab") || "general";

  const { data, isLoading, error } = useQuery({
    queryKey: ["contact", id],
    queryFn: () => contactService.get(id!),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => contactService.delete(id!),
    onSuccess: () => {
      message.success("Contact șters.");
      navigate("/crm/contacts");
    },
  });

  const addPersonMutation = useMutation({
    mutationFn: (values: Record<string, unknown>) =>
      contactService.addPerson(id!, {
        first_name: values.first_name as string,
        last_name: values.last_name as string,
        role: values.role as string,
        email: values.email as string | undefined,
        phone: values.phone as string | undefined,
        is_primary: (values.is_primary as boolean) || false,
      }),
    onSuccess: () => {
      message.success("Persoană adăugată.");
      queryClient.invalidateQueries({ queryKey: ["contact", id] });
      setAddPersonOpen(false);
      personForm.resetFields();
    },
    onError: () => message.error("Eroare."),
  });

  if (isLoading) {
    return <Skeleton active paragraph={{ rows: 8 }} />;
  }

  if (error || !data?.data) {
    return (
      <Alert
        type="error"
        message="Contact negăsit"
        description="Contactul solicitat nu a fost găsit sau a fost șters."
        action={
          <Button onClick={() => navigate("/crm/contacts")}>Înapoi la listă</Button>
        }
      />
    );
  }

  const contact = data.data;
  const initials =
    contact.company_name
      ?.split(" ")
      .map((w) => w[0])
      .join("")
      .substring(0, 2)
      .toUpperCase() || "?";

  const tabItems = [
    {
      key: "general",
      label: (
        <span>
          <InfoCircleOutlined /> Date Generale
        </span>
      ),
      children: <TabDateGenerale contact={contact} />,
    },
    {
      key: "interactions",
      label: (
        <span>
          <HistoryOutlined /> Istoric Interacțiuni
        </span>
      ),
      children: <TabIstoricInteractiuni contactId={contact.id} />,
    },
    {
      key: "properties",
      label: (
        <span>
          <HomeOutlined /> Proprietăți
        </span>
      ),
      children: <TabProprietati contactId={contact.id} />,
    },
    {
      key: "documents",
      label: (
        <span>
          <FileOutlined /> Documente
        </span>
      ),
      children: <TabDocumente contactId={contact.id} />,
    },
    {
      key: "offers",
      label: (
        <span>
          <DollarOutlined /> Oferte & Contracte
        </span>
      ),
      children: <TabOferteContracte contactId={contact.id} />,
    },
  ];

  return (
    <>
      {/* Header persistent */}
      <div
        style={{
          marginBottom: 24,
          padding: 16,
          background: "#fff",
          borderRadius: 8,
          border: "1px solid #f0f0f0",
        }}
      >
        <Space style={{ width: "100%", justifyContent: "space-between" }}>
          <Space size="middle">
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate("/crm/contacts")}
            />
            <Avatar
              size={48}
              style={{ backgroundColor: "#1677ff" }}
              icon={
                contact.contact_type === "company" ? (
                  <BankOutlined />
                ) : (
                  <UserOutlined />
                )
              }
            >
              {initials}
            </Avatar>
            <div>
              <Space>
                <Typography.Title level={4} style={{ margin: 0 }}>
                  {contact.company_name}
                </Typography.Title>
                <Tag>
                  {contact.contact_type === "company" ? "Companie" : "Persoană"}
                </Tag>
                <Tag color={STAGE_COLORS[contact.stage] || "default"}>
                  {contact.stage?.charAt(0).toUpperCase() + contact.stage?.slice(1)}
                </Tag>
              </Space>
              <Typography.Text type="secondary">
                {[contact.city, contact.county, contact.cui && `CUI: ${contact.cui}`]
                  .filter(Boolean)
                  .join(" • ")}
              </Typography.Text>
            </div>
          </Space>

          <Space>
            <Button
              icon={<FunnelPlotOutlined />}
              onClick={() => navigate(`/pipeline/opportunities/new?contact_id=${contact.id}`)}
            >
              Oportunitate nouă
            </Button>
            <Button
              icon={<PlusOutlined />}
              onClick={() => navigate(`/pipeline/offers/new?contact_id=${contact.id}`)}
            >
              Ofertă nouă
            </Button>
            <Button icon={<UserOutlined />} onClick={() => setAddPersonOpen(true)}>
              Persoană
            </Button>
            <Dropdown
              menu={{
                items: [
                  {
                    key: "edit",
                    icon: <EditOutlined />,
                    label: "Editează",
                    onClick: () => {
                      setSearchParams(new URLSearchParams({ tab: "general" }));
                    },
                  },
                  { type: "divider" },
                  {
                    key: "delete",
                    icon: <DeleteOutlined />,
                    label: "Șterge contactul",
                    danger: true,
                    onClick: () => deleteMutation.mutate(),
                  },
                ],
              }}
            >
              <Button icon={<MoreOutlined />} />
            </Dropdown>
          </Space>
        </Space>

        {/* Duplicate Guard banner - shown if contact has potential duplicates */}
        {contact.cui && (
          <DuplicateGuardBanner contactId={contact.id} cui={contact.cui} />
        )}
      </div>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onChange={(key) => setSearchParams(new URLSearchParams({ tab: key }))}
        items={tabItems}
        size="large"
      />

      {/* Add Person Modal (E-003.M1) */}
      <Modal
        title="Adaugă persoană de contact"
        open={addPersonOpen}
        onCancel={() => setAddPersonOpen(false)}
        onOk={() => personForm.submit()}
        confirmLoading={addPersonMutation.isPending}
        okText="Adaugă"
        cancelText="Anulează"
      >
        <Form
          form={personForm}
          layout="vertical"
          onFinish={(v) => addPersonMutation.mutate(v)}
        >
          <Form.Item
            name="first_name"
            label="Prenume"
            rules={[{ required: true, message: "Introdu prenumele" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="last_name"
            label="Nume"
            rules={[{ required: true, message: "Introdu numele" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="role"
            label="Rol"
            rules={[{ required: true, message: "Selectează rolul" }]}
          >
            <Select
              options={[
                { label: "CEO", value: "CEO" },
                { label: "Director", value: "Director" },
                { label: "Project Manager", value: "PM" },
                { label: "Contabil", value: "Accountant" },
                { label: "Persoană de contact", value: "Contact person" },
                { label: "Altul", value: "Other" },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="email"
            label="Email"
            rules={[{ type: "email", message: "Email invalid" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Telefon">
            <Input />
          </Form.Item>
          <Form.Item name="is_primary" label="Persoană principală" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}

/**
 * Duplicate Guard banner component - checks for duplicates
 */
function DuplicateGuardBanner({ contactId: _contactId, cui }: { contactId: string; cui: string }) {
  const { data } = useQuery({
    queryKey: ["duplicate-check", cui],
    queryFn: () =>
      contactService.checkDuplicates({ company_name: "", cui }),
    enabled: !!cui,
    staleTime: 60_000,
  });

  if (!data?.data?.has_duplicates) return null;

  const matches = data.data.matches || [];
  if (matches.length === 0) return null;

  return (
    <Alert
      type="warning"
      icon={<WarningOutlined />}
      message={
        <Space>
          <Typography.Text strong>Duplicat posibil detectat</Typography.Text>
          <Typography.Text type="secondary">
            — {matches.length} contact(e) cu CUI/email similar
          </Typography.Text>
        </Space>
      }
      banner
      style={{ marginTop: 12, borderRadius: 6 }}
    />
  );
}
