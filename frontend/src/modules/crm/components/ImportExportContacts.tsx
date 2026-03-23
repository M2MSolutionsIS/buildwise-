/**
 * F003 — Import/Export Contacts (CSV)
 * Connects to POST /api/v1/crm/contacts/import and POST /api/v1/crm/contacts/export
 */
import { useState } from "react";
import { Button, Space, Upload, App, Modal, Table, Tag, Typography } from "antd";
import { DownloadOutlined, ImportOutlined } from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../services/api";

const { Text } = Typography;

interface ImportResult {
  imported: number;
  skipped: number;
  errors: string[];
}

export default function ImportExportContacts() {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [showResult, setShowResult] = useState(false);

  const importMutation = useMutation({
    mutationFn: async (csvContent: string) => {
      const { data } = await api.post("/crm/contacts/import", {
        csv_data: csvContent,
        update_existing: false,
      });
      return data.data as ImportResult;
    },
    onSuccess: (result) => {
      setImportResult(result);
      setShowResult(true);
      message.success(`${result.imported} contacte importate.`);
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
    },
    onError: () => message.error("Eroare la importul contactelor."),
  });

  const exportMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post("/crm/contacts/export", {
        format: "csv",
        fields: [
          "company_name",
          "cui",
          "contact_type",
          "stage",
          "email",
          "phone",
          "city",
          "county",
          "address",
          "source",
        ],
      });
      return data.data as { csv_data: string; count: number };
    },
    onSuccess: (result) => {
      const blob = new Blob([result.csv_data], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `contacte_export_${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      message.success(`${result.count} contacte exportate.`);
    },
    onError: () => message.error("Eroare la exportul contactelor."),
  });

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      if (content) {
        importMutation.mutate(content);
      }
    };
    reader.readAsText(file);
    return false;
  };

  return (
    <>
      <Space>
        <Upload
          accept=".csv"
          beforeUpload={(file) => handleFileUpload(file as File)}
          showUploadList={false}
        >
          <Button
            icon={<ImportOutlined />}
            loading={importMutation.isPending}
          >
            Import CSV
          </Button>
        </Upload>
        <Button
          icon={<DownloadOutlined />}
          onClick={() => exportMutation.mutate()}
          loading={exportMutation.isPending}
        >
          Export CSV
        </Button>
      </Space>

      <Modal
        title="Rezultat Import"
        open={showResult}
        onCancel={() => setShowResult(false)}
        footer={[
          <Button key="close" onClick={() => setShowResult(false)}>
            Închide
          </Button>,
        ]}
      >
        {importResult && (
          <div>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Space>
                <Tag color="green">Importate: {importResult.imported}</Tag>
                <Tag color="orange">Ignorate: {importResult.skipped}</Tag>
                {importResult.errors.length > 0 && (
                  <Tag color="red">Erori: {importResult.errors.length}</Tag>
                )}
              </Space>
              {importResult.errors.length > 0 && (
                <Table
                  size="small"
                  pagination={false}
                  dataSource={importResult.errors.map((err, i) => ({
                    key: i,
                    error: err,
                  }))}
                  columns={[
                    {
                      title: "Eroare",
                      dataIndex: "error",
                      key: "error",
                      render: (err: string) => (
                        <Text type="danger">{err}</Text>
                      ),
                    },
                  ]}
                />
              )}
            </Space>
          </div>
        )}
      </Modal>
    </>
  );
}
