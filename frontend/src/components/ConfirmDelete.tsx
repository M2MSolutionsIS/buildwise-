/**
 * C-001: Confirmare Ștergere — Pattern reutilizat pentru confirmare ștergere.
 * Modal "Ești sigur?" cu opțiuni Anulează / Șterge.
 * Common (P1+P2+P3).
 */
import { Modal } from "antd";
import { ExclamationCircleOutlined } from "@ant-design/icons";

interface ConfirmDeleteOptions {
  title?: string;
  content?: string;
  onOk: () => void | Promise<void>;
  onCancel?: () => void;
  okText?: string;
  cancelText?: string;
}

/**
 * Usage:
 *   confirmDelete({
 *     title: "Șterge contactul?",
 *     content: "Acțiunea este ireversibilă.",
 *     onOk: () => deleteMutation.mutate(id),
 *   });
 */
export function confirmDelete({
  title = "Confirmare ștergere",
  content = "Ești sigur că vrei să ștergi? Acțiunea nu poate fi anulată.",
  onOk,
  onCancel,
  okText = "Șterge",
  cancelText = "Anulează",
}: ConfirmDeleteOptions) {
  Modal.confirm({
    title,
    icon: <ExclamationCircleOutlined />,
    content,
    okText,
    okType: "danger",
    cancelText,
    onOk,
    onCancel,
  });
}

export default confirmDelete;
