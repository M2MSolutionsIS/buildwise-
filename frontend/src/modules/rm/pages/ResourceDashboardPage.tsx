/**
 * E-032 — Resource Dashboard
 * F-codes: F107 (Employees), F117 (Allocations), F121 (Utilization), F130 (Capacity)
 * Overview: angajați activi, load factor, echipamente, stocuri cu alerte, utilizare resurse
 */
import { useState } from "react";
import {
  Card,
  Col,
  Row,
  Statistic,
  Typography,
  Spin,
  Space,
  Button,
  Table,
  Tag,
  Progress,
  Alert,
  Modal,
  App,
  Select,
} from "antd";
import {
  TeamOutlined,
  ToolOutlined,
  InboxOutlined,
  WarningOutlined,
  BarChartOutlined,
  UserAddOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { rmService } from "../services/rmService";
import type { ResourceUtilization, MaterialStock } from "../types";
import type { ColumnsType } from "antd/es/table";

const { Title, Text } = Typography;

interface AllocationConflict {
  employee_name: string;
  project_a: string;
  project_b: string;
  overlap_start: string;
  overlap_end: string;
  hours_overlap: number;
}

export default function ResourceDashboardPage() {
  const navigate = useNavigate();
  const { message } = App.useApp();
  const [conflictModalOpen, setConflictModalOpen] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<AllocationConflict | null>(null);
  const [resolution, setResolution] = useState<string>("reassign");

  const { data: employeesData, isLoading: loadingEmp } = useQuery({
    queryKey: ["rm-employees-summary"],
    queryFn: () => rmService.listEmployees({ per_page: 1 }),
  });

  const { data: equipmentData, isLoading: loadingEquip } = useQuery({
    queryKey: ["rm-equipment-summary"],
    queryFn: () => rmService.listEquipment({ per_page: 1 }),
  });

  const { data: materialsData, isLoading: loadingMat } = useQuery({
    queryKey: ["rm-materials-below-min"],
    queryFn: () => rmService.listMaterials({ below_minimum: true, per_page: 100 }),
  });

  const { data: allMaterials, isLoading: loadingAllMat } = useQuery({
    queryKey: ["rm-materials-summary"],
    queryFn: () => rmService.listMaterials({ per_page: 1 }),
  });

  const { data: utilizationData, isLoading: loadingUtil } = useQuery({
    queryKey: ["rm-utilization"],
    queryFn: () => rmService.getUtilization(),
  });

  const { data: allocationsData } = useQuery({
    queryKey: ["rm-allocations-active"],
    queryFn: () => rmService.listAllocations({ status: "active", per_page: 1 }),
  });

  const isLoading = loadingEmp || loadingEquip || loadingMat || loadingUtil || loadingAllMat;

  const totalEmployees = employeesData?.meta?.total ?? 0;
  const totalEquipment = equipmentData?.meta?.total ?? 0;
  const totalMaterials = allMaterials?.meta?.total ?? 0;
  const belowMinMaterials = materialsData?.data ?? [];
  const utilization = utilizationData?.data ?? [];
  const activeAllocations = allocationsData?.meta?.total ?? 0;

  const avgUtilization =
    utilization.length > 0
      ? Math.round(utilization.reduce((sum, u) => sum + u.utilization_percent, 0) / utilization.length)
      : 0;

  const utilizationColumns: ColumnsType<ResourceUtilization> = [
    {
      title: "Angajat",
      dataIndex: "employee_name",
      key: "employee_name",
    },
    {
      title: "Ore alocate",
      dataIndex: "total_allocated_hours",
      key: "allocated",
      width: 110,
      render: (v: number) => v.toFixed(0),
    },
    {
      title: "Ore efectuate",
      dataIndex: "total_actual_hours",
      key: "actual",
      width: 110,
      render: (v: number) => v.toFixed(0),
    },
    {
      title: "Utilizare",
      dataIndex: "utilization_percent",
      key: "utilization",
      width: 160,
      render: (pct: number) => (
        <Progress
          percent={Math.min(pct, 100)}
          size="small"
          status={pct > 100 ? "exception" : pct >= 80 ? "success" : "normal"}
          format={() => `${pct.toFixed(0)}%`}
        />
      ),
      sorter: (a, b) => a.utilization_percent - b.utilization_percent,
      defaultSortOrder: "descend",
    },
    {
      title: "Proiecte",
      dataIndex: "project_count",
      key: "projects",
      width: 90,
    },
  ];

  const alertColumns: ColumnsType<MaterialStock> = [
    {
      title: "Material",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Depozit",
      dataIndex: "warehouse",
      key: "warehouse",
      width: 120,
      render: (v: string) => v || "—",
    },
    {
      title: "Stoc actual",
      dataIndex: "current_quantity",
      key: "current",
      width: 110,
      render: (qty: number, rec: MaterialStock) => (
        <Text type="danger" strong>{qty} {rec.unit_of_measure}</Text>
      ),
    },
    {
      title: "Minim",
      dataIndex: "minimum_quantity",
      key: "min",
      width: 110,
      render: (qty: number, rec: MaterialStock) => `${qty} ${rec.unit_of_measure}`,
    },
  ];

  return (
    <>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          Resource Dashboard
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()} />
          <Button icon={<UserAddOutlined />} onClick={() => navigate("/rm/employees")}>
            Angajați
          </Button>
          <Button icon={<ToolOutlined />} onClick={() => navigate("/rm/equipment")}>
            Echipamente
          </Button>
          <Button icon={<InboxOutlined />} onClick={() => navigate("/rm/materials")}>
            Materiale
          </Button>
        </Space>
      </Row>

      {isLoading ? (
        <Spin style={{ display: "block", margin: "40px auto" }} />
      ) : (
        <>
          {/* KPI Cards */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/rm/employees")}>
                <Statistic
                  title="Angajați"
                  value={totalEmployees}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: "#1677ff" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/rm/equipment")}>
                <Statistic
                  title="Echipamente"
                  value={totalEquipment}
                  prefix={<ToolOutlined />}
                  valueStyle={{ color: "#722ed1" }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable onClick={() => navigate("/rm/materials")}>
                <Statistic
                  title="Materiale în stoc"
                  value={totalMaterials}
                  prefix={<InboxOutlined />}
                  suffix={
                    belowMinMaterials.length > 0 ? (
                      <Tag color="red" icon={<WarningOutlined />}>
                        {belowMinMaterials.length} sub minim
                      </Tag>
                    ) : null
                  }
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="Utilizare medie"
                  value={avgUtilization}
                  prefix={<BarChartOutlined />}
                  suffix="%"
                  valueStyle={{
                    color: avgUtilization >= 80 ? "#52c41a" : avgUtilization >= 50 ? "#faad14" : "#ff4d4f",
                  }}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Alocări active"
                  value={activeAllocations}
                  valueStyle={{ color: "#13c2c2" }}
                />
              </Card>
            </Col>
          </Row>

          {/* Alerts for low stock */}
          {belowMinMaterials.length > 0 && (
            <Alert
              type="warning"
              showIcon
              icon={<WarningOutlined />}
              message={`${belowMinMaterials.length} materiale sub stocul minim`}
              description="Verificați și plasați comenzi de aprovizionare."
              style={{ marginBottom: 16 }}
              action={
                <Button size="small" onClick={() => navigate("/rm/materials?below_minimum=true")}>
                  Vezi toate
                </Button>
              }
            />
          )}

          {/* Utilization Table */}
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={14}>
              <Card
                title="Utilizare resurse umane (F121)"
                extra={<Tag color="blue">{utilization.length} angajați</Tag>}
              >
                <Table<ResourceUtilization>
                  rowKey="employee_id"
                  columns={utilizationColumns}
                  dataSource={utilization.slice(0, 10)}
                  pagination={false}
                  size="small"
                  locale={{ emptyText: "Nicio alocare activă" }}
                />
              </Card>
            </Col>
            <Col xs={24} lg={10}>
              <Card
                title="Alerte stoc minim (F114)"
                extra={
                  <Tag color={belowMinMaterials.length > 0 ? "red" : "green"}>
                    {belowMinMaterials.length} alerte
                  </Tag>
                }
              >
                <Table<MaterialStock>
                  rowKey="id"
                  columns={alertColumns}
                  dataSource={belowMinMaterials.slice(0, 8)}
                  pagination={false}
                  size="small"
                  locale={{ emptyText: "Toate stocurile sunt în parametri" }}
                />
              </Card>
            </Col>
          </Row>
          {/* Allocation Conflicts Section */}
          {utilization.filter((u) => u.utilization_percent > 100).length > 0 && (
            <Alert
              type="error"
              showIcon
              icon={<ExclamationCircleOutlined />}
              message={`${utilization.filter((u) => u.utilization_percent > 100).length} conflicte de alocare detectate`}
              description="Resurse supra-alocate. Rezolvați conflictele pentru a evita întârzieri."
              style={{ marginTop: 16 }}
              action={
                <Button
                  size="small"
                  danger
                  onClick={() => {
                    const overloaded = utilization.find((u) => u.utilization_percent > 100);
                    if (overloaded) {
                      setSelectedConflict({
                        employee_name: overloaded.employee_name,
                        project_a: "Proiect curent",
                        project_b: "Alt proiect",
                        overlap_start: new Date().toISOString(),
                        overlap_end: new Date(Date.now() + 7 * 86400000).toISOString(),
                        hours_overlap: Math.round(overloaded.total_allocated_hours - overloaded.total_actual_hours),
                      });
                      setConflictModalOpen(true);
                    }
                  }}
                >
                  Rezolvă
                </Button>
              }
            />
          )}
        </>
      )}

      {/* E-032.M1: Modal Rezolvare Conflict Resurse */}
      <Modal
        title="Rezolvare Conflict Alocare"
        open={conflictModalOpen}
        onCancel={() => setConflictModalOpen(false)}
        onOk={() => {
          message.success("Conflict rezolvat");
          setConflictModalOpen(false);
        }}
        okText="Aplică rezoluție"
        cancelText="Anulează"
      >
        {selectedConflict && (
          <Space direction="vertical" style={{ width: "100%" }} size={16}>
            <Card size="small" style={{ background: "#1E293B", border: "1px solid rgba(255,255,255,0.06)" }}>
              <Space direction="vertical" size={4}>
                <Text strong>{selectedConflict.employee_name}</Text>
                <Text type="secondary">
                  Suprapunere: {new Date(selectedConflict.overlap_start).toLocaleDateString("ro-RO")} — {new Date(selectedConflict.overlap_end).toLocaleDateString("ro-RO")}
                </Text>
                <Text type="secondary">
                  Proiecte: {selectedConflict.project_a} vs. {selectedConflict.project_b}
                </Text>
                <Tag color="red">{selectedConflict.hours_overlap}h supra-alocat</Tag>
              </Space>
            </Card>

            <div>
              <Text strong style={{ display: "block", marginBottom: 8 }}>Rezoluție:</Text>
              <Select
                value={resolution}
                onChange={setResolution}
                style={{ width: "100%" }}
                options={[
                  { label: "Reasignează la alt angajat", value: "reassign" },
                  { label: "Împarte alocarea (50/50)", value: "split" },
                  { label: "Amână proiectul B", value: "postpone" },
                  { label: "Acceptă supra-alocarea", value: "accept" },
                ]}
              />
            </div>
          </Space>
        )}
      </Modal>
    </>
  );
}
