import { useState } from "react";
import { Modal, Input, Table, Tag, Space, Empty } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { productService } from "../services/productService";
import type { Product } from "../../../types";
import type { ColumnsType } from "antd/es/table";

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (product: Product) => void;
}

export default function ProductPickerModal({ open, onClose, onSelect }: Props) {
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["products", search],
    queryFn: () => productService.list({ search: search || undefined, is_active: true, per_page: 20 }),
    enabled: open,
  });

  const products = data?.data || [];

  const columns: ColumnsType<Product> = [
    { title: "Cod", dataIndex: "code", key: "code", width: 100 },
    { title: "Denumire", dataIndex: "name", key: "name" },
    {
      title: "Categorie",
      dataIndex: "category",
      key: "category",
      render: (c: string) => c ? <Tag>{c}</Tag> : "—",
    },
    { title: "UM", dataIndex: "unit_of_measure", key: "um", width: 60 },
    {
      title: "Preț",
      dataIndex: "unit_price",
      key: "price",
      width: 120,
      render: (v: number, r: Product) =>
        `${v?.toLocaleString("ro-RO", { minimumFractionDigits: 2 })} ${r.currency || "RON"}`,
    },
    {
      title: "Status",
      dataIndex: "is_active",
      key: "status",
      width: 80,
      render: (active: boolean) => (
        <Tag color={active ? "success" : "default"}>{active ? "Activ" : "Inactiv"}</Tag>
      ),
    },
  ];

  return (
    <Modal
      title="Selectează produs din catalog"
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Input
        placeholder="Caută după cod, denumire sau categorie..."
        prefix={<SearchOutlined />}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        allowClear
        style={{ marginBottom: 16 }}
      />

      <Table<Product>
        rowKey="id"
        columns={columns}
        dataSource={products}
        loading={isLoading}
        pagination={false}
        size="small"
        locale={{ emptyText: <Empty description="Niciun produs găsit" /> }}
        onRow={(record) => ({
          onClick: () => {
            onSelect(record);
            onClose();
          },
          style: { cursor: "pointer" },
        })}
        scroll={{ y: 400 }}
      />
    </Modal>
  );
}
