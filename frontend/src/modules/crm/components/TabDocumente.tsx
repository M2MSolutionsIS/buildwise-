import { Typography, Table, Tag, Button, Space, Empty, Upload, App, Popconfirm, Spin } from "antd";
import {
  UploadOutlined,
  FileOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileExcelOutlined,
  FileWordOutlined,
  DeleteOutlined,
  InboxOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentService } from "../services/documentService";
import type { CrmDocumentListItem } from "../../../types";

const { Dragger } = Upload;

const FILE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FilePdfOutlined style={{ color: "#ff4d4f" }} />,
  jpg: <FileImageOutlined style={{ color: "#1890ff" }} />,
  jpeg: <FileImageOutlined style={{ color: "#1890ff" }} />,
  png: <FileImageOutlined style={{ color: "#1890ff" }} />,
  xlsx: <FileExcelOutlined style={{ color: "#52c41a" }} />,
  xls: <FileExcelOutlined style={{ color: "#52c41a" }} />,
  doc: <FileWordOutlined style={{ color: "#1677ff" }} />,
  docx: <FileWordOutlined style={{ color: "#1677ff" }} />,
};

const CATEGORIES: Record<string, string> = {
  contracts: "Contracte",
  offers: "Oferte",
  technical: "Date tehnice",
  photos: "Fotografii",
  other: "Altele",
};

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

interface Props {
  contactId: string;
}

export default function TabDocumente({ contactId }: Props) {
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["documents", "contact", contactId],
    queryFn: () => documentService.list("contact", contactId),
    enabled: !!contactId,
  });

  const createMutation = useMutation({
    mutationFn: documentService.create,
    onSuccess: () => {
      message.success("Document înregistrat.");
      queryClient.invalidateQueries({ queryKey: ["documents", "contact", contactId] });
    },
    onError: () => message.error("Eroare la înregistrarea documentului."),
  });

  const deleteMutation = useMutation({
    mutationFn: documentService.delete,
    onSuccess: () => {
      message.success("Document șters.");
      queryClient.invalidateQueries({ queryKey: ["documents", "contact", contactId] });
    },
    onError: () => message.error("Eroare la ștergerea documentului."),
  });

  const handleUpload = (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    const category = ["jpg", "jpeg", "png"].includes(ext)
      ? "photos"
      : ["pdf"].includes(ext)
        ? "contracts"
        : ["doc", "docx"].includes(ext)
          ? "technical"
          : ["xls", "xlsx"].includes(ext)
            ? "offers"
            : "other";

    createMutation.mutate({
      entity_type: "contact",
      entity_id: contactId,
      file_name: file.name,
      file_path: `/uploads/contacts/${contactId}/${file.name}`,
      file_size: file.size,
      mime_type: file.type,
      category,
    });
    return false;
  };

  const documents = data?.data ?? [];

  const columns: ColumnsType<CrmDocumentListItem> = [
    {
      title: "Fișier",
      dataIndex: "file_name",
      key: "file_name",
      render: (name: string) => {
        const ext = name.split(".").pop()?.toLowerCase() || "";
        return (
          <Space>
            {FILE_ICONS[ext] || <FileOutlined />}
            {name}
          </Space>
        );
      },
    },
    {
      title: "Categorie",
      dataIndex: "category",
      key: "category",
      width: 140,
      render: (cat: string) => <Tag>{CATEGORIES[cat] || cat}</Tag>,
    },
    {
      title: "Dimensiune",
      dataIndex: "file_size",
      key: "file_size",
      width: 100,
      render: (size: number) => (size ? formatFileSize(size) : "—"),
    },
    {
      title: "Versiune",
      dataIndex: "version",
      key: "version",
      width: 80,
      render: (v: number) => `v${v}`,
    },
    {
      title: "Data",
      dataIndex: "created_at",
      key: "created_at",
      width: 120,
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
      render: (_: unknown, record: CrmDocumentListItem) => (
        <Popconfirm
          title="Ștergi documentul?"
          onConfirm={() => deleteMutation.mutate(record.id)}
          okText="Da"
          cancelText="Nu"
        >
          <Button type="text" size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  if (isLoading) {
    return <Spin style={{ display: "block", margin: "40px auto" }} />;
  }

  if (documents.length === 0) {
    return (
      <div style={{ maxWidth: 500, margin: "0 auto" }}>
        <Dragger
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.zip"
          beforeUpload={(file) => handleUpload(file as File)}
          showUploadList={false}
          style={{ padding: 24 }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">
            Trage și plasează fișierele aici sau click pentru a selecta
          </p>
          <p className="ant-upload-hint">
            PDF, DOC, XLS, JPG, PNG, ZIP — max 50 MB per fișier
          </p>
        </Dragger>
        <Empty
          description={
            <Typography.Text type="secondary">
              Niciun document încărcat pentru acest contact.
            </Typography.Text>
          }
          style={{ marginTop: 24 }}
        />
      </div>
    );
  }

  return (
    <>
      <Space style={{ marginBottom: 16, width: "100%", justifyContent: "flex-end" }}>
        <Upload
          beforeUpload={(file) => handleUpload(file as File)}
          showUploadList={false}
          multiple
        >
          <Button icon={<UploadOutlined />} loading={createMutation.isPending}>
            Încarcă document
          </Button>
        </Upload>
      </Space>
      <Table<CrmDocumentListItem>
        rowKey="id"
        columns={columns}
        dataSource={documents}
        pagination={false}
        size="small"
      />
    </>
  );
}
