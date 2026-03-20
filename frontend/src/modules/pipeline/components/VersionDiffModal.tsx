/**
 * E-006.M1 — Version Diff Modal
 * F-code: F029 (Version comparison)
 * Side-by-side comparison of offer versions with color-coded changes
 */
import { useState, useMemo } from "react";
import { Modal, Select, Table, Tag, Row, Col, Typography, Empty, Statistic, Card } from "antd";
import type { Offer } from "../../../types";

const { Text } = Typography;

interface Props {
  open: boolean;
  onClose: () => void;
  currentOffer: Offer;
  versions: Offer[];
}

interface DiffRow {
  key: string;
  description: string;
  type: "added" | "deleted" | "modified" | "unchanged";
  v1Qty?: number;
  v1Price?: number;
  v1Total?: number;
  v2Qty?: number;
  v2Price?: number;
  v2Total?: number;
}

export default function VersionDiffModal({ open, onClose, currentOffer, versions }: Props) {
  const allVersions = useMemo(() => {
    if (versions.length > 0) return versions;
    return [currentOffer];
  }, [versions, currentOffer]);

  const [v1Id, setV1Id] = useState<string | undefined>(allVersions.length > 1 ? allVersions[0]?.id : undefined);
  const [v2Id, setV2Id] = useState<string | undefined>(currentOffer.id);

  const v1 = allVersions.find((v) => v.id === v1Id);
  const v2 = allVersions.find((v) => v.id === v2Id);

  // Compute diff
  const diffRows = useMemo((): DiffRow[] => {
    if (!v1 || !v2) return [];

    const v1Items = v1.line_items || [];
    const v2Items = v2.line_items || [];

    const rows: DiffRow[] = [];
    const v2Matched = new Set<number>();

    // Match by description (best effort)
    for (const item1 of v1Items) {
      const matchIdx = v2Items.findIndex(
        (item2, idx) => !v2Matched.has(idx) && item2.description === item1.description
      );

      if (matchIdx >= 0) {
        v2Matched.add(matchIdx);
        const item2 = v2Items[matchIdx]!;
        const isModified =
          item1.quantity !== item2.quantity ||
          item1.unit_price !== item2.unit_price;

        rows.push({
          key: item1.id || item1.description,
          description: item1.description,
          type: isModified ? "modified" : "unchanged",
          v1Qty: item1.quantity,
          v1Price: item1.unit_price,
          v1Total: item1.total_price || item1.quantity * item1.unit_price,
          v2Qty: item2.quantity,
          v2Price: item2.unit_price,
          v2Total: item2.total_price || item2.quantity * item2.unit_price,
        });
      } else {
        rows.push({
          key: item1.id || `del-${item1.description}`,
          description: item1.description,
          type: "deleted",
          v1Qty: item1.quantity,
          v1Price: item1.unit_price,
          v1Total: item1.total_price || item1.quantity * item1.unit_price,
        });
      }
    }

    // Items only in v2
    v2Items.forEach((item2, idx) => {
      if (!v2Matched.has(idx)) {
        rows.push({
          key: item2.id || `add-${item2.description}`,
          description: item2.description,
          type: "added",
          v2Qty: item2.quantity,
          v2Price: item2.unit_price,
          v2Total: item2.total_price || item2.quantity * item2.unit_price,
        });
      }
    });

    return rows;
  }, [v1, v2]);

  const v1Total = v1?.total_amount || 0;
  const v2Total = v2?.total_amount || 0;
  const totalDiff = v2Total - v1Total;

  const TYPE_COLORS: Record<string, string> = {
    added: "#f6ffed",
    deleted: "#fff2f0",
    modified: "#fffbe6",
    unchanged: "transparent",
  };

  const TYPE_TAGS: Record<string, { color: string; label: string }> = {
    added: { color: "success", label: "Adăugat" },
    deleted: { color: "error", label: "Șters" },
    modified: { color: "warning", label: "Modificat" },
    unchanged: { color: "default", label: "Neschimbat" },
  };

  const columns = [
    {
      title: "Produs",
      dataIndex: "description",
      key: "description",
    },
    {
      title: "Status",
      dataIndex: "type",
      key: "type",
      width: 100,
      render: (type: string) => {
        const cfg = TYPE_TAGS[type];
        return cfg ? <Tag color={cfg.color}>{cfg.label}</Tag> : null;
      },
    },
    {
      title: `v${v1?.version || "?"} Cant.`,
      dataIndex: "v1Qty",
      key: "v1Qty",
      width: 80,
      render: (v: number) => v?.toLocaleString("ro-RO") ?? "—",
    },
    {
      title: `v${v1?.version || "?"} Preț`,
      dataIndex: "v1Price",
      key: "v1Price",
      width: 100,
      render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) ?? "—",
    },
    {
      title: `v${v1?.version || "?"} Total`,
      dataIndex: "v1Total",
      key: "v1Total",
      width: 100,
      render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) ?? "—",
    },
    {
      title: `v${v2?.version || "?"} Cant.`,
      dataIndex: "v2Qty",
      key: "v2Qty",
      width: 80,
      render: (v: number, row: DiffRow) => {
        const changed = row.type === "modified" && v !== row.v1Qty;
        return (
          <Text strong={changed} type={changed ? "warning" : undefined}>
            {v?.toLocaleString("ro-RO") ?? "—"}
          </Text>
        );
      },
    },
    {
      title: `v${v2?.version || "?"} Preț`,
      dataIndex: "v2Price",
      key: "v2Price",
      width: 100,
      render: (v: number, row: DiffRow) => {
        const changed = row.type === "modified" && v !== row.v1Price;
        return (
          <Text strong={changed} type={changed ? "warning" : undefined}>
            {v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) ?? "—"}
          </Text>
        );
      },
    },
    {
      title: `v${v2?.version || "?"} Total`,
      dataIndex: "v2Total",
      key: "v2Total",
      width: 100,
      render: (v: number) => v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 }) ?? "—",
    },
  ];

  return (
    <Modal
      title={`Compară versiuni: ${currentOffer.offer_number}`}
      open={open}
      onCancel={onClose}
      footer={null}
      width={1000}
      destroyOnClose
    >
      {/* Version selectors */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Text strong>Versiunea veche:</Text>
          <Select
            value={v1Id}
            onChange={setV1Id}
            style={{ width: "100%", marginTop: 4 }}
            options={allVersions.map((v) => ({
              value: v.id,
              label: `v${v.version} — ${new Date(v.created_at).toLocaleDateString("ro-RO")} (${v.total_amount?.toLocaleString("ro-RO")} ${v.currency})`,
            }))}
          />
        </Col>
        <Col span={12}>
          <Text strong>Versiunea nouă:</Text>
          <Select
            value={v2Id}
            onChange={setV2Id}
            style={{ width: "100%", marginTop: 4 }}
            options={allVersions.map((v) => ({
              value: v.id,
              label: `v${v.version} — ${new Date(v.created_at).toLocaleDateString("ro-RO")} (${v.total_amount?.toLocaleString("ro-RO")} ${v.currency})`,
            }))}
          />
        </Col>
      </Row>

      {/* Summary */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title={`Total v${v1?.version || "?"}`}
              value={v1Total}
              precision={2}
              suffix={v1?.currency}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title={`Total v${v2?.version || "?"}`}
              value={v2Total}
              precision={2}
              suffix={v2?.currency}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Diferență"
              value={totalDiff}
              precision={2}
              prefix={totalDiff > 0 ? "+" : ""}
              suffix={v2?.currency}
              valueStyle={{ color: totalDiff > 0 ? "#cf1322" : totalDiff < 0 ? "#3f8600" : undefined }}
            />
          </Card>
        </Col>
      </Row>

      {/* Diff table */}
      {diffRows.length > 0 ? (
        <Table
          rowKey="key"
          columns={columns}
          dataSource={diffRows}
          pagination={false}
          size="small"
          onRow={(record) => ({
            style: { background: TYPE_COLORS[record.type] },
          })}
        />
      ) : (
        <Empty description="Selectează două versiuni diferite pentru comparare" />
      )}
    </Modal>
  );
}
