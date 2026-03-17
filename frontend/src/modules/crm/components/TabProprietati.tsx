import { useState } from "react";
import {
  Card,
  Row,
  Col,
  Tag,
  Typography,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Empty,
  Spin,
  Space,
  App,
} from "antd";
import {
  HomeOutlined,
  PlusOutlined,
  EnvironmentOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";

const ENERGY_BADGE = (energyClass?: string) => {
  if (!energyClass) return null;
  const cls = energyClass.toUpperCase();
  if (cls === "A" || cls === "A+") return <Tag color="green">{cls}</Tag>;
  if (cls === "B" || cls === "C") return <Tag color="orange">{cls}</Tag>;
  return <Tag color="red">{cls}</Tag>;
};

const PROPERTY_TYPES: Record<string, string> = {
  residential: "Rezidențial",
  commercial: "Comercial",
  industrial: "Industrial",
  public: "Public",
};

interface Props {
  contactId: string;
}

export default function TabProprietati({ contactId }: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["properties", contactId],
    queryFn: () => contactService.listProperties(contactId),
  });

  const addMutation = useMutation({
    mutationFn: (values: Record<string, unknown>) =>
      contactService.addProperty(contactId, values as never),
    onSuccess: () => {
      message.success("Proprietate adăugată.");
      queryClient.invalidateQueries({ queryKey: ["properties", contactId] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la adăugare."),
  });

  const properties = data?.data || [];

  return (
    <>
      <Space style={{ marginBottom: 16, width: "100%", justifyContent: "flex-end" }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Proprietate nouă
        </Button>
      </Space>

      {isLoading ? (
        <Spin style={{ display: "block", textAlign: "center", padding: 48 }} />
      ) : properties.length === 0 ? (
        <Empty description="Nicio proprietate asignată">
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Adaugă prima proprietate
          </Button>
        </Empty>
      ) : (
        <Row gutter={[16, 16]}>
          {properties.map((p) => (
            <Col xs={24} sm={12} lg={8} key={p.id}>
              <Card
                hoverable
                size="small"
                title={
                  <Space>
                    <HomeOutlined />
                    {p.name}
                  </Space>
                }
                extra={ENERGY_BADGE(p.energy_class)}
              >
                <Space direction="vertical" size={4} style={{ width: "100%" }}>
                  <Tag>{PROPERTY_TYPES[p.property_type] || p.property_type}</Tag>
                  {p.address && (
                    <Typography.Text type="secondary">
                      <EnvironmentOutlined /> {p.address}
                      {p.city ? `, ${p.city}` : ""}
                    </Typography.Text>
                  )}
                  {p.total_area_sqm && (
                    <Typography.Text>
                      Suprafață: {p.total_area_sqm} m²
                    </Typography.Text>
                  )}
                  {p.year_built && (
                    <Typography.Text type="secondary">
                      Construit: {p.year_built}
                    </Typography.Text>
                  )}
                  {p.energy_class && (
                    <Typography.Text>
                      <ThunderboltOutlined /> Clasă energetică: {p.energy_class}
                    </Typography.Text>
                  )}
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title="Adaugă proprietate"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={addMutation.isPending}
        okText="Adaugă"
        cancelText="Anulează"
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={(v) => addMutation.mutate(v)}>
          <Form.Item
            name="name"
            label="Denumire"
            rules={[{ required: true, message: "Introdu denumirea" }]}
          >
            <Input />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="property_type"
                label="Tip"
                rules={[{ required: true, message: "Selectează tipul" }]}
              >
                <Select
                  options={Object.entries(PROPERTY_TYPES).map(([k, v]) => ({
                    label: v,
                    value: k,
                  }))}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="total_area_sqm" label="Suprafață totală (m²)">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="address" label="Adresă">
            <Input />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="city" label="Localitate">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="county" label="Județ">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="year_built" label="An construcție">
                <InputNumber min={1800} max={2030} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="floors_count" label="Etaje">
                <InputNumber min={0} max={200} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="energy_class" label="Clasă energetică">
                <Select
                  allowClear
                  options={["A+", "A", "B", "C", "D", "E", "F", "G"].map((c) => ({
                    label: c,
                    value: c,
                  }))}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="notes" label="Notițe">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
