/**
 * E-010 — Create / Edit Opportunity
 * F-codes: F042 (Qualify & Handover)
 */
import { useNavigate } from "react-router-dom";
import {
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  Button,
  Space,
  message,
  Typography,
} from "antd";
import { ArrowLeftOutlined } from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { pipelineService } from "../services/pipelineService";
import type { OpportunityCreate } from "../../../types";

const { Title } = Typography;
const { TextArea } = Input;

export default function OpportunityCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  const createMutation = useMutation({
    mutationFn: (values: OpportunityCreate) =>
      pipelineService.createOpportunity(values),
    onSuccess: (res) => {
      message.success("Oportunitate creată.");
      queryClient.invalidateQueries({ queryKey: ["pipeline-board"] });
      navigate(`/pipeline/opportunities/${res.data.id}`);
    },
    onError: () => message.error("Eroare la creare."),
  });

  const handleFinish = (values: Record<string, unknown>) => {
    const payload: OpportunityCreate = {
      contact_id: values.contact_id as string,
      title: values.title as string,
      description: values.description as string | undefined,
      estimated_value: values.estimated_value as number | undefined,
      currency: (values.currency as string) ?? "RON",
      expected_close_date: values.expected_close_date
        ? (values.expected_close_date as { toISOString: () => string }).toISOString()
        : undefined,
      source: values.source as string | undefined,
      tags: values.tags as string[] | undefined,
      notes: values.notes as string | undefined,
    };
    createMutation.mutate(payload);
  };

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate("/pipeline/board")}
        >
          Înapoi la Pipeline
        </Button>
      </Space>

      <Card>
        <Title level={4}>Oportunitate Nouă</Title>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          initialValues={{ currency: "RON", stage: "new" }}
          style={{ maxWidth: 700 }}
        >
          <Form.Item
            name="title"
            label="Titlu"
            rules={[{ required: true, message: "Titlul e obligatoriu" }]}
          >
            <Input placeholder="ex: Reabilitare termică Bloc A3" />
          </Form.Item>

          <Form.Item
            name="contact_id"
            label="Contact (ID)"
            rules={[{ required: true, message: "Selectează un contact" }]}
          >
            <Input placeholder="UUID contact" />
          </Form.Item>

          <Form.Item name="description" label="Descriere">
            <TextArea rows={3} />
          </Form.Item>

          <Space size="large">
            <Form.Item name="estimated_value" label="Valoare estimată">
              <InputNumber
                min={0}
                style={{ width: 200 }}
                formatter={(v) =>
                  `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
                }
              />
            </Form.Item>
            <Form.Item name="currency" label="Monedă">
              <Select style={{ width: 100 }}>
                <Select.Option value="RON">RON</Select.Option>
                <Select.Option value="EUR">EUR</Select.Option>
                <Select.Option value="USD">USD</Select.Option>
              </Select>
            </Form.Item>
          </Space>

          <Form.Item name="expected_close_date" label="Dată închidere estimată">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item name="source" label="Sursă">
            <Select allowClear placeholder="Selectează sursa">
              <Select.Option value="referral">Referral</Select.Option>
              <Select.Option value="website">Website</Select.Option>
              <Select.Option value="cold_call">Cold Call</Select.Option>
              <Select.Option value="event">Eveniment</Select.Option>
              <Select.Option value="partner">Partener</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="tags" label="Tag-uri">
            <Select mode="tags" placeholder="Adaugă tag-uri" />
          </Form.Item>

          <Form.Item name="notes" label="Note">
            <TextArea rows={2} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createMutation.isPending}
              >
                Creează Oportunitate
              </Button>
              <Button onClick={() => navigate("/pipeline/board")}>
                Anulează
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </>
  );
}
