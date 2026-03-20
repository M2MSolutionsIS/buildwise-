import { useState, useCallback } from "react";
import { Modal, Input, Table, Button, Tag, Empty } from "antd";
import { SearchOutlined, PlusOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { offerService } from "../services/offerService";
import type { Product } from "../../../types/pipeline";
import type { ColumnsType } from "antd/es/table";

interface ProductPickerModalProps {
  open: boolean;
  onClose: () => void;
  onSelect: (product: Product) => void;
}

export default function ProductPickerModal({
  open,
  onClose,
  onSelect,
}: ProductPickerModalProps) {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
    const timer = setTimeout(() => setDebouncedSearch(value), 300);
    return () => clearTimeout(timer);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["products", debouncedSearch],
    queryFn: () => offerService.searchProducts(debouncedSearch || undefined),
    enabled: open,
  });

  const products = data?.data || [];

  const columns: ColumnsType<Product> = [
    {
      title: "Cod",
      dataIndex: "code",
      key: "code",
      width: 100,
      render: (code: string) => <Tag>{code}</Tag>,
    },
    {
      title: "Denumire",
      dataIndex: "name",
      key: "name",
      ellipsis: true,
    },
    {
      title: "UM",
      dataIndex: "unit_of_measure",
      key: "unit_of_measure",
      width: 70,
    },
    {
      title: "Preț unitar",
      dataIndex: "unit_price",
      key: "unit_price",
      width: 120,
      align: "right",
      render: (price: number) =>
        new Intl.NumberFormat("ro-RO", {
          style: "currency",
          currency: "RON",
        }).format(price),
    },
    {
      title: "",
      key: "action",
      width: 80,
      render: (_: unknown, record: Product) => (
        <Button
          type="primary"
          size="small"
          icon={<PlusOutlined />}
          onClick={() => {
            onSelect(record);
            onClose();
          }}
        >
          Adaugă
        </Button>
      ),
    },
  ];

  return (
    <Modal
      title="Selectare produs din catalog"
      open={open}
      onCancel={onClose}
      footer={null}
      width={720}
      destroyOnClose
    >
      <Input
        placeholder="Caută produs (denumire, cod)..."
        prefix={<SearchOutlined />}
        allowClear
        value={search}
        onChange={(e) => handleSearch(e.target.value)}
        style={{ marginBottom: 16 }}
        autoFocus
      />

      <Table<Product>
        rowKey="id"
        columns={columns}
        dataSource={products}
        loading={isLoading}
        pagination={false}
        scroll={{ y: 400 }}
        size="small"
        locale={{
          emptyText: (
            <Empty
              description={
                debouncedSearch
                  ? "Niciun produs găsit"
                  : "Introduceți un termen de căutare"
              }
            />
          ),
        }}
      />
    </Modal>
  );
}
