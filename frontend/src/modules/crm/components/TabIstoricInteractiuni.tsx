import { useState } from "react";
import {
  Timeline,
  Tag,
  Typography,
  Select,
  Space,
  Button,
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Empty,
  Spin,
  App,
} from "antd";
import {
  MailOutlined,
  PhoneOutlined,
  CalendarOutlined,
  FileOutlined,
  DollarOutlined,
  FileTextOutlined,
  MessageOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contactService } from "../../../services/contactService";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/ro";

dayjs.extend(relativeTime);
dayjs.locale("ro");

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  email: { icon: <MailOutlined />, color: "blue", label: "Email" },
  call: { icon: <PhoneOutlined />, color: "green", label: "Apel" },
  meeting: { icon: <CalendarOutlined />, color: "purple", label: "Întâlnire" },
  document: { icon: <FileOutlined />, color: "orange", label: "Document" },
  offer: { icon: <DollarOutlined />, color: "gold", label: "Ofertă" },
  contract: { icon: <FileTextOutlined />, color: "cyan", label: "Contract" },
  note: { icon: <MessageOutlined />, color: "default", label: "Notă" },
};

interface Props {
  contactId: string;
}

export default function TabIstoricInteractiuni({ contactId }: Props) {
  const [typeFilter, setTypeFilter] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["interactions", contactId, typeFilter],
    queryFn: () =>
      contactService.listInteractions(contactId, {
        interaction_type: typeFilter,
        per_page: 50,
      }),
  });

  const addMutation = useMutation({
    mutationFn: (values: Record<string, unknown>) =>
      contactService.addInteraction(contactId, {
        interaction_type: values.interaction_type as string,
        subject: values.subject as string,
        description: values.description as string | undefined,
        interaction_date: (values.interaction_date as dayjs.Dayjs)?.toISOString() || new Date().toISOString(),
        duration_minutes: values.duration_minutes as number | undefined,
      }),
    onSuccess: () => {
      message.success("Interacțiune adăugată.");
      queryClient.invalidateQueries({ queryKey: ["interactions", contactId] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare."),
  });

  const interactions = data?.data || [];

  return (
    <>
      <Space style={{ marginBottom: 16, width: "100%", justifyContent: "space-between" }}>
        <Select
          placeholder="Filtrează tipul"
          allowClear
          style={{ width: 200 }}
          value={typeFilter}
          onChange={setTypeFilter}
          options={Object.entries(TYPE_CONFIG).map(([key, v]) => ({
            label: v.label,
            value: key,
          }))}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Adaugă interacțiune
        </Button>
      </Space>

      {isLoading ? (
        <Spin style={{ display: "block", textAlign: "center", padding: 48 }} />
      ) : interactions.length === 0 ? (
        <Empty description="Nicio interacțiune încă" />
      ) : (
        <Timeline
          items={interactions.map((i) => {
            const cfg = TYPE_CONFIG[i.interaction_type] ?? TYPE_CONFIG.note!;
            return {
              dot: cfg.icon,
              color: cfg.color,
              children: (
                <div>
                  <Space>
                    <Tag color={cfg.color}>{cfg.label}</Tag>
                    <Typography.Text strong>{i.subject}</Typography.Text>
                  </Space>
                  {i.description && (
                    <Typography.Paragraph
                      type="secondary"
                      style={{ margin: "4px 0 0" }}
                      ellipsis={{ rows: 2, expandable: true }}
                    >
                      {i.description}
                    </Typography.Paragraph>
                  )}
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {dayjs(i.interaction_date).fromNow()} •{" "}
                    {dayjs(i.interaction_date).format("D MMM YYYY HH:mm")}
                    {i.duration_minutes ? ` • ${i.duration_minutes} min` : ""}
                  </Typography.Text>
                </div>
              ),
            };
          })}
        />
      )}

      <Modal
        title="Adaugă interacțiune"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={addMutation.isPending}
        okText="Adaugă"
        cancelText="Anulează"
      >
        <Form form={form} layout="vertical" onFinish={(v) => addMutation.mutate(v)}>
          <Form.Item
            name="interaction_type"
            label="Tip"
            rules={[{ required: true, message: "Selectează tipul" }]}
          >
            <Select
              options={Object.entries(TYPE_CONFIG).map(([key, v]) => ({
                label: v.label,
                value: key,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="subject"
            label="Subiect"
            rules={[{ required: true, message: "Introdu subiectul" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Descriere">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="interaction_date" label="Data">
            <DatePicker
              showTime
              style={{ width: "100%" }}
              format="DD.MM.YYYY HH:mm"
            />
          </Form.Item>
          <Form.Item name="duration_minutes" label="Durată (minute)">
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
