/**
 * E-007: Contracts List — F031, F035, F037
 * Lista contractelor cu navigare cross-modul.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, Table, Tag, Button, Space, Select } from "antd";
import {
  FileTextOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { pipelineService } from "../services/pipelineService";
import type { ContractListItem } from "../../../types";

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  draft: { color: "default", label: "Draft" },
  pending_approval: { color: "processing", label: "Aprobare" },
  approved: { color: "cyan", label: "Aprobat" },
  sent: { color: "blue", label: "Trimis" },
  negotiation: { color: "orange", label: "Negociere" },
  signed: { color: "green", label: "Semnat" },
  active: { color: "green", label: "Activ" },
  completed: { color: "purple", label: "Finalizat" },
  terminated: { color: "red", label: "Reziliat" },
};

function fmtCurrency(v?: number | null): string {
  if (v == null) return "—";
  return new Intl.NumberFormat("ro-RO", {
    style: "currency",
    currency: "RON",
    maximumFractionDigits: 0,
  }).format(v);
}

export default function ContractsListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const perPage = 20;

  const { data: resp, isLoading } = useQuery({
    queryKey: ["pipeline", "contracts", page, statusFilter],
    queryFn: () =>
      pipelineService.listContracts({
        page,
        per_page: perPage,
        status: statusFilter,
      }),
  });

  const contracts = resp?.data ?? [];
  const total = resp?.meta?.total ?? 0;

  const columns: ColumnsType<ContractListItem> = [
    {
      title: "Nr. Contract",
      dataIndex: "contract_number",
      width: 140,
      render: (v: string, rec) => (
        <a onClick={() => navigate(`/pipeline/contracts/${rec.id}`)}>{v}</a>
      ),
    },
    {
      title: "Titlu",
      dataIndex: "title",
      ellipsis: true,
      render: (v: string, rec) => (
        <a onClick={() => navigate(`/pipeline/contracts/${rec.id}`)}>{v}</a>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      width: 120,
      render: (v: string) => {
        const cfg = STATUS_MAP[v] ?? { color: "default", label: v };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: "Valoare",
      dataIndex: "total_value",
      width: 140,
      align: "right",
      render: (v: number) => fmtCurrency(v),
    },
    {
      title: "Data",
      dataIndex: "created_at",
      width: 110,
      render: (v: string) =>
        v ? new Date(v).toLocaleDateString("ro-RO") : "—",
    },
    {
      title: "Acțiuni",
      key: "actions",
      width: 100,
      render: (_: unknown, rec: ContractListItem) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => navigate(`/pipeline/contracts/${rec.id}`)}
          >
            Detalii
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2>Contracte (F031, F035)</h2>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="Status"
            allowClear
            value={statusFilter}
            onChange={(v) => {
              setStatusFilter(v);
              setPage(1);
            }}
            style={{ width: 160 }}
            options={Object.entries(STATUS_MAP).map(([val, cfg]) => ({
              value: val,
              label: cfg.label,
            }))}
          />
        </Space>
      </Card>

      <Card size="small">
        <Table
          loading={isLoading}
          dataSource={contracts}
          columns={columns}
          rowKey="id"
          size="small"
          pagination={{
            current: page,
            pageSize: perPage,
            total,
            onChange: setPage,
            showTotal: (t) => `${t} contracte`,
          }}
        />
      </Card>
    </div>
  );
}
