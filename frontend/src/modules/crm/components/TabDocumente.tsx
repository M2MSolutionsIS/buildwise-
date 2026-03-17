import { Typography, Table, Tag, Button, Space, Empty, Upload } from "antd";
import {
  UploadOutlined,
  FileOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileExcelOutlined,
  FileWordOutlined,
  DownloadOutlined,
  InboxOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";

const { Dragger } = Upload;

interface Document {
  id: string;
  name: string;
  category: string;
  size: number;
  uploaded_by: string;
  uploaded_at: string;
  mime_type: string;
}

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

export default function TabDocumente({ contactId: _contactId }: Props) {
  // Documents API not yet implemented in backend - placeholder UI
  const documents: Document[] = [];

  const columns: ColumnsType<Document> = [
    {
      title: "Fișier",
      dataIndex: "name",
      key: "name",
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
      dataIndex: "size",
      key: "size",
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: "Încărcat de",
      dataIndex: "uploaded_by",
      key: "uploaded_by",
      width: 140,
    },
    {
      title: "Data",
      dataIndex: "uploaded_at",
      key: "uploaded_at",
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
      render: () => (
        <Button type="text" size="small" icon={<DownloadOutlined />} />
      ),
    },
  ];

  if (documents.length === 0) {
    return (
      <div style={{ maxWidth: 500, margin: "0 auto" }}>
        <Dragger
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.zip"
          beforeUpload={() => false}
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
              Niciun document încărcat. Documentele vor fi disponibile după
              implementarea API-ului de upload.
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
        <Upload beforeUpload={() => false} multiple>
          <Button icon={<UploadOutlined />}>Încarcă document</Button>
        </Upload>
      </Space>
      <Table<Document>
        rowKey="id"
        columns={columns}
        dataSource={documents}
        pagination={false}
        size="small"
      />
    </>
  );
}
