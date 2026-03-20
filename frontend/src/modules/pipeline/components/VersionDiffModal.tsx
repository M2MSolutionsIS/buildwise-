import { useState } from "react";
import { Modal, Select, Table, Tag, Typography, Space, Empty, Spin } from "antd";
import { useQuery } from "@tanstack/react-query";
import { offerService } from "../services/offerService";
import type { OfferDiff } from "../../../types/pipeline";
import type { ColumnsType } from "antd/es/table";

interface VersionDiffModalProps {
  open: boolean;
  onClose: () => void;
  offerId: string;
  currentVersion: number;
}

const CHANGE_COLORS: Record<string, string> = {
  added: "green",
  removed: "red",
  modified: "orange",
};

const CHANGE_LABELS: Record<string, string> = {
  added: "Adăugat",
  removed: "Șters",
  modified: "Modificat",
};

export default function VersionDiffModal({
  open,
  onClose,
  offerId,
  currentVersion,
}: VersionDiffModalProps) {
  const [v1, setV1] = useState(Math.max(1, currentVersion - 1));
  const [v2, setV2] = useState(currentVersion);

  const versionOptions = Array.from({ length: currentVersion }, (_, i) => ({
    label: `v${i + 1}`,
    value: i + 1,
  }));

  const { data, isLoading } = useQuery({
    queryKey: ["offer-diff", offerId, v1, v2],
    queryFn: () => offerService.getVersionDiff(offerId, v1, v2),
    enabled: open && v1 !== v2,
  });

  const diffs = data?.data || [];

  const columns: ColumnsType<OfferDiff> = [
    {
      title: "Câmp",
      dataIndex: "field",
      key: "field",
      width: 200,
      render: (field: string) => (
        <Typography.Text strong>{field}</Typography.Text>
      ),
    },
    {
      title: `Valoare v${v1}`,
      dataIndex: "old_value",
      key: "old_value",
      render: (value: string | number | null, record: OfferDiff) => (
        <Typography.Text
          delete={record.change_type === "removed" || record.change_type === "modified"}
          type={record.change_type === "removed" ? "danger" : undefined}
        >
          {value ?? "—"}
        </Typography.Text>
      ),
    },
    {
      title: `Valoare v${v2}`,
      dataIndex: "new_value",
      key: "new_value",
      render: (value: string | number | null, record: OfferDiff) => (
        <Typography.Text
          type={record.change_type === "added" ? "success" : undefined}
          style={
            record.change_type === "modified"
              ? { backgroundColor: "#fff7e6", padding: "2px 4px", borderRadius: 2 }
              : undefined
          }
        >
          {value ?? "—"}
        </Typography.Text>
      ),
    },
    {
      title: "Tip",
      dataIndex: "change_type",
      key: "change_type",
      width: 110,
      render: (type: string) => (
        <Tag color={CHANGE_COLORS[type]}>{CHANGE_LABELS[type]}</Tag>
      ),
    },
  ];

  return (
    <Modal
      title="Comparare versiuni ofertă"
      open={open}
      onCancel={onClose}
      footer={null}
      width={900}
      destroyOnClose
    >
      <Space style={{ marginBottom: 16 }}>
        <Typography.Text>Compară:</Typography.Text>
        <Select
          value={v1}
          onChange={setV1}
          options={versionOptions}
          style={{ width: 80 }}
        />
        <Typography.Text>cu</Typography.Text>
        <Select
          value={v2}
          onChange={setV2}
          options={versionOptions}
          style={{ width: 80 }}
        />
      </Space>

      {v1 === v2 ? (
        <Empty description="Selectați versiuni diferite pentru comparare" />
      ) : isLoading ? (
        <div style={{ textAlign: "center", padding: 48 }}>
          <Spin size="large" />
        </div>
      ) : (
        <Table<OfferDiff>
          rowKey={(record, index) => `${record.field}-${index}`}
          columns={columns}
          dataSource={diffs}
          pagination={false}
          size="small"
          locale={{
            emptyText: <Empty description="Nicio diferență între versiuni" />,
          }}
        />
      )}
    </Modal>
  );
}
