import { useNavigate } from "react-router-dom";
import {
  Typography,
  Form,
  Input,
  Select,
  Button,
  Card,
  Row,
  Col,
  Switch,
  Space,
  App,
  Divider,
} from "antd";
import { ArrowLeftOutlined, SaveOutlined, PlusOutlined, MinusCircleOutlined } from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";
import type { ContactCreate } from "../../../types";

export default function ContactCreatePage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (values: ContactCreate) => contactService.create(values),
    onSuccess: (data) => {
      message.success("Contact creat cu succes!");
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
      navigate(`/crm/contacts/${data.data.id}`);
    },
    onError: () => message.error("Eroare la crearea contactului."),
  });

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate("/crm/contacts")}
        />
        <Typography.Title level={3} style={{ margin: 0 }}>
          Contact nou
        </Typography.Title>
      </Space>

      <Form
        form={form}
        layout="vertical"
        onFinish={(values) => createMutation.mutate(values)}
        initialValues={{ contact_type: "company", stage: "prospect", country: "RO" }}
      >
        <Row gutter={24}>
          <Col xs={24} lg={16}>
            <Card title="Informații de bază">
              <Row gutter={16}>
                <Col xs={24} sm={16}>
                  <Form.Item
                    name="company_name"
                    label="Denumire"
                    rules={[{ required: true, message: "Introdu denumirea" }]}
                  >
                    <Input placeholder="Numele companiei sau persoanei" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="contact_type"
                    label="Tip"
                    rules={[{ required: true }]}
                  >
                    <Select
                      options={[
                        { label: "Companie", value: "company" },
                        { label: "Persoană fizică", value: "individual" },
                      ]}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={12} sm={8}>
                  <Form.Item name="cui" label="CUI">
                    <Input placeholder="RO12345678" />
                  </Form.Item>
                </Col>
                <Col xs={12} sm={8}>
                  <Form.Item name="registration_number" label="Nr. înregistrare">
                    <Input placeholder="J40/123/2020" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item name="stage" label="Status">
                    <Select
                      options={[
                        { label: "Prospect", value: "prospect" },
                        { label: "Activ", value: "active" },
                        { label: "Client", value: "client" },
                        { label: "Partener", value: "partner" },
                      ]}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="email"
                    label="Email"
                    rules={[{ type: "email", message: "Email invalid" }]}
                  >
                    <Input placeholder="contact@companie.ro" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item name="phone" label="Telefon">
                    <Input placeholder="+40 7XX XXX XXX" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item name="website" label="Website">
                <Input placeholder="https://www.companie.ro" />
              </Form.Item>
            </Card>

            <Card title="Adresă" style={{ marginTop: 16 }}>
              <Form.Item name="address" label="Adresă">
                <Input placeholder="Strada, număr" />
              </Form.Item>
              <Row gutter={16}>
                <Col xs={12} sm={8}>
                  <Form.Item name="city" label="Localitate">
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={12} sm={8}>
                  <Form.Item name="county" label="Județ">
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={12} sm={4}>
                  <Form.Item name="postal_code" label="Cod poștal">
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={12} sm={4}>
                  <Form.Item name="country" label="Țara">
                    <Input />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            <Card title="Persoane de contact" style={{ marginTop: 16 }}>
              <Form.List name="persons">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Row gutter={12} key={key} align="middle" style={{ marginBottom: 8 }}>
                        <Col span={5}>
                          <Form.Item
                            {...restField}
                            name={[name, "first_name"]}
                            rules={[{ required: true, message: "Prenume" }]}
                            style={{ marginBottom: 0 }}
                          >
                            <Input placeholder="Prenume" />
                          </Form.Item>
                        </Col>
                        <Col span={5}>
                          <Form.Item
                            {...restField}
                            name={[name, "last_name"]}
                            rules={[{ required: true, message: "Nume" }]}
                            style={{ marginBottom: 0 }}
                          >
                            <Input placeholder="Nume" />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item
                            {...restField}
                            name={[name, "role"]}
                            style={{ marginBottom: 0 }}
                          >
                            <Select
                              placeholder="Rol"
                              options={[
                                { label: "CEO", value: "CEO" },
                                { label: "Director", value: "Director" },
                                { label: "PM", value: "PM" },
                                { label: "Contact", value: "Contact person" },
                              ]}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={5}>
                          <Form.Item
                            {...restField}
                            name={[name, "email"]}
                            style={{ marginBottom: 0 }}
                          >
                            <Input placeholder="Email" />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item
                            {...restField}
                            name={[name, "phone"]}
                            style={{ marginBottom: 0 }}
                          >
                            <Input placeholder="Telefon" />
                          </Form.Item>
                        </Col>
                        <Col span={1}>
                          <MinusCircleOutlined onClick={() => remove(name)} />
                        </Col>
                      </Row>
                    ))}
                    <Button
                      type="dashed"
                      onClick={() => add({ is_primary: fields.length === 0 })}
                      icon={<PlusOutlined />}
                      block
                    >
                      Adaugă persoană
                    </Button>
                  </>
                )}
              </Form.List>
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Card title="Opțiuni">
              <Form.Item name="source" label="Sursă">
                <Select
                  allowClear
                  placeholder="Cum a ajuns contactul"
                  options={[
                    { label: "Referință", value: "referral" },
                    { label: "Website", value: "website" },
                    { label: "Telefon", value: "phone" },
                    { label: "Email", value: "email" },
                    { label: "Eveniment", value: "event" },
                    { label: "Altul", value: "other" },
                  ]}
                />
              </Form.Item>
              <Form.Item name="vat_payer" label="Plătitor TVA" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="gdpr_consent" label="Consimțământ GDPR" valuePropName="checked">
                <Switch />
              </Form.Item>

              <Divider />

              <Form.Item name="bank_name" label="Banca">
                <Input />
              </Form.Item>
              <Form.Item name="bank_account" label="Cont bancar (IBAN)">
                <Input placeholder="RO49AAAA1B31007593840000" />
              </Form.Item>
            </Card>

            <Card title="Notițe" style={{ marginTop: 16 }}>
              <Form.Item name="notes">
                <Input.TextArea rows={4} placeholder="Notițe interne..." />
              </Form.Item>
            </Card>

            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={createMutation.isPending}
              block
              size="large"
              style={{ marginTop: 16 }}
            >
              Salvează contactul
            </Button>
          </Col>
        </Row>
      </Form>
    </>
  );
}
