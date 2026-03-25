/**
 * C-003: Empty State Pattern — Icon + mesaj + CTA.
 * Reusable empty state for lists, tables, sections.
 * Common (P1+P2+P3).
 */
import { Empty, Button, Typography } from "antd";
import { PlusOutlined, InboxOutlined } from "@ant-design/icons";

const { Text } = Typography;

interface EmptyStateProps {
  /** Icon to display (defaults to InboxOutlined) */
  icon?: React.ReactNode;
  /** Primary message */
  title?: string;
  /** Secondary description */
  description?: string;
  /** CTA button label */
  actionLabel?: string;
  /** CTA button click handler */
  onAction?: () => void;
  /** CTA button icon */
  actionIcon?: React.ReactNode;
  /** Compact mode (less padding) */
  compact?: boolean;
}

export default function EmptyState({
  icon,
  title = "Nicio înregistrare",
  description,
  actionLabel,
  onAction,
  actionIcon = <PlusOutlined />,
  compact = false,
}: EmptyStateProps) {
  return (
    <div style={{ textAlign: "center", padding: compact ? "24px 16px" : "48px 24px" }}>
      <div style={{ fontSize: 48, color: "#d9d9d9", marginBottom: 16 }}>
        {icon ?? <InboxOutlined />}
      </div>
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        imageStyle={{ display: "none" }}
        description={
          <div>
            <Text strong style={{ display: "block", marginBottom: 4 }}>{title}</Text>
            {description && (
              <Text type="secondary" style={{ fontSize: 13 }}>{description}</Text>
            )}
          </div>
        }
      >
        {actionLabel && onAction && (
          <Button type="primary" icon={actionIcon} onClick={onAction}>
            {actionLabel}
          </Button>
        )}
      </Empty>
    </div>
  );
}
