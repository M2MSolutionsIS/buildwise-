import { useState } from "react";
import {
  Card,
  Descriptions,
  Tag,
  Typography,
  Input,
  Select,
  Row,
  Col,
  Statistic,
  Space,
  App,
  Button,
} from "antd";
import {
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  MailOutlined,
  PhoneOutlined,
  GlobalOutlined,
  TagOutlined,
} from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";
import type { Contact } from "../../../types";

interface Props {
  contact: Contact;
}

export default function TabDateGenerale({ contact }: Props) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Partial<Contact>>({});
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Contact>) => contactService.update(contact.id, data),
    onSuccess: () => {
      message.success("Contact actualizat.");
      queryClient.invalidateQueries({ queryKey: ["contact", contact.id] });
      setEditing(false);
    },
    onError: () => message.error("Eroare la actualizare."),
  });

  const startEdit = () => {
    setForm({
      company_name: contact.company_name,
      cui: contact.cui,
      contact_type: contact.contact_type,
      stage: contact.stage,
      email: contact.email,
      phone: contact.phone,
      website: contact.website,
      address: contact.address,
      city: contact.city,
      county: contact.county,
      notes: contact.notes,
      source: contact.source,
    });
    setEditing(true);
  };

  const handleSave = () => updateMutation.mutate(form);

  return (
    <Row gutter={[24, 24]}>
      <Col xs={24} lg={16}>
        <Card
          title="Informații companie"
          extra={
            editing ? (
              <Space>
                <Button
                  icon={<SaveOutlined />}
                  type="primary"
                  size="small"
                  loading={updateMutation.isPending}
                  onClick={handleSave}
                >
                  Salvează
                </Button>
                <Button
                  icon={<CloseOutlined />}
                  size="small"
                  onClick={() => setEditing(false)}
                >
                  Anulează
                </Button>
              </Space>
            ) : (
              <Button icon={<EditOutlined />} size="small" onClick={startEdit}>
                Editează
              </Button>
            )
          }
        >
          <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
            <Descriptions.Item label="Denumire">
              {editing ? (
                <Input
                  value={form.company_name}
                  onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                />
              ) : (
                contact.company_name
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Tip">
              {editing ? (
                <Select
                  value={form.contact_type}
                  onChange={(v) => setForm({ ...form, contact_type: v })}
                  options={[
                    { label: "Companie", value: "company" },
                    { label: "Persoană fizică", value: "individual" },
                  ]}
                  style={{ width: "100%" }}
                />
              ) : (
                <Tag>{contact.contact_type === "company" ? "Companie" : "Persoană"}</Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="CUI">
              {editing ? (
                <Input
                  value={form.cui}
                  onChange={(e) => setForm({ ...form, cui: e.target.value })}
                />
              ) : (
                contact.cui || "—"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              {editing ? (
                <Select
                  value={form.stage}
                  onChange={(v) => setForm({ ...form, stage: v })}
                  options={[
                    { label: "Prospect", value: "prospect" },
                    { label: "Activ", value: "active" },
                    { label: "Client", value: "client" },
                    { label: "Inactiv", value: "inactive" },
                    { label: "Partener", value: "partner" },
                  ]}
                  style={{ width: "100%" }}
                />
              ) : (
                <Tag color={contact.stage === "active" ? "green" : "blue"}>
                  {contact.stage}
                </Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label={<><MailOutlined /> Email</>}>
              {editing ? (
                <Input
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              ) : (
                contact.email || "—"
              )}
            </Descriptions.Item>
            <Descriptions.Item label={<><PhoneOutlined /> Telefon</>}>
              {editing ? (
                <Input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              ) : (
                contact.phone || "—"
              )}
            </Descriptions.Item>
            <Descriptions.Item label={<><GlobalOutlined /> Website</>}>
              {editing ? (
                <Input
                  value={form.website}
                  onChange={(e) => setForm({ ...form, website: e.target.value })}
                />
              ) : contact.website ? (
                <a href={contact.website} target="_blank" rel="noopener noreferrer">
                  {contact.website}
                </a>
              ) : (
                "—"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Sursă">
              {editing ? (
                <Input
                  value={form.source}
                  onChange={(e) => setForm({ ...form, source: e.target.value })}
                />
              ) : (
                contact.source || "—"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Adresă" span={2}>
              {editing ? (
                <Input
                  value={form.address}
                  onChange={(e) => setForm({ ...form, address: e.target.value })}
                />
              ) : (
                [contact.address, contact.city, contact.county]
                  .filter(Boolean)
                  .join(", ") || "—"
              )}
            </Descriptions.Item>
          </Descriptions>

          {contact.persons?.length > 0 && (
            <>
              <Typography.Title level={5} style={{ marginTop: 24 }}>
                Persoane de contact
              </Typography.Title>
              <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
                {contact.persons.map((p) => (
                  <Descriptions.Item
                    key={p.id}
                    label={
                      <Space>
                        {p.first_name} {p.last_name}
                        {p.is_primary && <Tag color="blue">Principal</Tag>}
                      </Space>
                    }
                  >
                    <Space direction="vertical" size={0}>
                      <Typography.Text type="secondary">{p.role}</Typography.Text>
                      {p.email && <Typography.Text>{p.email}</Typography.Text>}
                      {p.phone && <Typography.Text>{p.phone}</Typography.Text>}
                    </Space>
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </>
          )}

          <Typography.Title level={5} style={{ marginTop: 24 }}>
            <TagOutlined /> Etichete
          </Typography.Title>
          <Space wrap>
            {contact.tags?.map((tag) => (
              <Tag key={tag} closable={editing}>
                {tag}
              </Tag>
            ))}
            {(!contact.tags || contact.tags.length === 0) && (
              <Typography.Text type="secondary">Nicio etichetă</Typography.Text>
            )}
          </Space>

          {(contact.notes || editing) && (
            <>
              <Typography.Title level={5} style={{ marginTop: 24 }}>
                Notițe interne
              </Typography.Title>
              {editing ? (
                <Input.TextArea
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  rows={4}
                />
              ) : (
                <Typography.Paragraph>{contact.notes}</Typography.Paragraph>
              )}
            </>
          )}
        </Card>
      </Col>

      <Col xs={24} lg={8}>
        <Card title="Sumar">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Statistic title="Persoane" value={contact.persons?.length || 0} />
            </Col>
            <Col span={12}>
              <Statistic
                title="GDPR"
                value={contact.gdpr_consent ? "Da" : "Nu"}
                valueStyle={{
                  color: contact.gdpr_consent ? "#52c41a" : "#ff4d4f",
                }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="TVA"
                value={contact.vat_payer ? "Plătitor" : "Neplătitor"}
              />
            </Col>
            <Col span={12}>
              <Statistic title="Țara" value={contact.country || "RO"} />
            </Col>
          </Row>
        </Card>

        <Card title="Date financiare" style={{ marginTop: 16 }}>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="Cont bancar">
              {contact.bank_account || "—"}
            </Descriptions.Item>
            <Descriptions.Item label="Banca">
              {contact.bank_name || "—"}
            </Descriptions.Item>
            <Descriptions.Item label="Nr. înregistrare">
              {contact.registration_number || "—"}
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Card title="Metadate" style={{ marginTop: 16 }}>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="Creat la">
              {new Date(contact.created_at).toLocaleString("ro-RO")}
            </Descriptions.Item>
            <Descriptions.Item label="Actualizat la">
              {new Date(contact.updated_at).toLocaleString("ro-RO")}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>
    </Row>
  );
}
