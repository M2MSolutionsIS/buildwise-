/**
 * C-005: PDF Preview Modal — Iframe PDF + download/print.
 * Previews PDF documents (offers, contracts, reports).
 * Common (P1+P2+P3).
 */
import { Modal, Button, Space, Typography, Alert } from "antd";
import {
  DownloadOutlined,
  PrinterOutlined,
  ExpandOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { useState } from "react";

const { Text } = Typography;

interface PDFPreviewModalProps {
  /** Whether the modal is visible */
  open: boolean;
  /** Close callback */
  onClose: () => void;
  /** PDF URL to preview */
  url?: string;
  /** Document title */
  title?: string;
  /** Document filename for download */
  filename?: string;
}

export default function PDFPreviewModal({
  open,
  onClose,
  url,
  title = "Previzualizare Document",
  filename = "document.pdf",
}: PDFPreviewModalProps) {
  const [fullscreen, setFullscreen] = useState(false);

  const handleDownload = () => {
    if (!url) return;
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
  };

  const handlePrint = () => {
    if (!url) return;
    const printWindow = window.open(url, "_blank");
    if (printWindow) {
      printWindow.addEventListener("load", () => {
        printWindow.print();
      });
    }
  };

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title={
        <Space>
          <FileTextOutlined />
          <Text>{title}</Text>
        </Space>
      }
      width={fullscreen ? "95vw" : 900}
      style={fullscreen ? { top: 20 } : undefined}
      footer={
        <Space>
          <Button icon={<ExpandOutlined />} onClick={() => setFullscreen(!fullscreen)}>
            {fullscreen ? "Normal" : "Ecran Complet"}
          </Button>
          <Button icon={<PrinterOutlined />} onClick={handlePrint} disabled={!url}>
            Printează
          </Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleDownload} disabled={!url}>
            Descarcă
          </Button>
        </Space>
      }
    >
      {url ? (
        <iframe
          src={url}
          style={{
            width: "100%",
            height: fullscreen ? "80vh" : "65vh",
            border: "1px solid #f0f0f0",
            borderRadius: 4,
          }}
          title={title}
        />
      ) : (
        <Alert
          type="info"
          showIcon
          message="Niciun document disponibil"
          description="URL-ul documentului PDF nu a fost furnizat. Generează mai întâi documentul."
        />
      )}
    </Modal>
  );
}
