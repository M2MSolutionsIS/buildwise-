/**
 * E-025: Notifications Center — Full page
 * Feed complet + preferences matrix (event × channel).
 * Route: /notifications
 */
import { useState } from "react";
import {
  Typography,
  Card,
  Tabs,
  List,
  Button,
  Tag,
  Space,
  App,
  Badge,
  Switch,
  Table,
  Tooltip,
} from "antd";
import {
  BellOutlined,
  CheckOutlined,
  CheckCircleOutlined,
  MailOutlined,
  MobileOutlined,
  DesktopOutlined,
  FilterOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationService } from "../services/notificationService";
import type { AppNotification } from "../../../types";
import EmptyState from "../../../components/EmptyState";

const { Title, Text, Paragraph } = Typography;

const EVENT_TYPES = [
  { key: "opportunity_created", label: "Oportunitate creată", module: "Pipeline" },
  { key: "opportunity_won", label: "Oportunitate câștigată", module: "Pipeline" },
  { key: "opportunity_lost", label: "Oportunitate pierdută", module: "Pipeline" },
  { key: "offer_sent", label: "Ofertă trimisă", module: "Pipeline" },
  { key: "offer_accepted", label: "Ofertă acceptată", module: "Pipeline" },
  { key: "contract_signed", label: "Contract semnat", module: "Pipeline" },
  { key: "task_assigned", label: "Task asignat", module: "PM" },
  { key: "task_overdue", label: "Task depășit", module: "PM" },
  { key: "project_milestone", label: "Milestone proiect", module: "PM" },
  { key: "budget_alert", label: "Alertă buget", module: "PM" },
  { key: "contact_created", label: "Contact creat", module: "CRM" },
  { key: "follow_up_due", label: "Follow-up scadent", module: "CRM" },
  { key: "stock_low", label: "Stoc scăzut", module: "RM" },
  { key: "equipment_maintenance", label: "Mentenanță echipament", module: "RM" },
  { key: "kpi_threshold", label: "Alertă KPI", module: "BI" },
];

const CHANNELS = [
  { key: "in_app", label: "In-App", icon: <DesktopOutlined /> },
  { key: "email", label: "Email", icon: <MailOutlined /> },
  { key: "push", label: "Push", icon: <MobileOutlined /> },
];

export default function NotificationsCenterPage() {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("all");
  const [preferences, setPreferences] = useState<Record<string, Record<string, boolean>>>(() => {
    // Initialize all events with all channels enabled
    const prefs: Record<string, Record<string, boolean>> = {};
    EVENT_TYPES.forEach((e) => {
      prefs[e.key] = { in_app: true, email: true, push: false };
    });
    return prefs;
  });

  const statusFilter = activeTab === "unread" ? "unread" : activeTab === "read" ? "read" : undefined;

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["notifications", statusFilter],
    queryFn: () => notificationService.list({ notification_status: statusFilter, per_page: 50 }),
  });

  const markReadMut = useMutation({
    mutationFn: notificationService.markRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMut = useMutation({
    mutationFn: notificationService.markAllRead,
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      message.success(`${res.data.marked_read} notificări marcate ca citite`);
    },
  });

  const notifications = data?.data || [];
  const unreadCount = notifications.filter((n) => n.status === "unread").length;

  const getTimeAgo = (dateStr: string) => {
    const now = new Date();
    const date = new Date(dateStr);
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "acum";
    if (diffMin < 60) return `${diffMin}m`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}h`;
    const diffD = Math.floor(diffH / 24);
    return `${diffD}z`;
  };

  const togglePreference = (eventKey: string, channelKey: string) => {
    setPreferences((prev) => ({
      ...prev,
      [eventKey]: {
        ...prev[eventKey],
        [channelKey]: !prev[eventKey]?.[channelKey],
      },
    }));
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <BellOutlined style={{ fontSize: 20, color: "#3B82F6" }} />
          <Title level={4} style={{ margin: 0 }}>
            Centrul de Notificări
          </Title>
          {unreadCount > 0 && <Badge count={unreadCount} />}
        </Space>
        <Space>
          <Tooltip title="Reîncarcă">
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </Tooltip>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => markAllReadMut.mutate()}
            loading={markAllReadMut.isPending}
          >
            Marchează toate ca citite
          </Button>
        </Space>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "all",
            label: (
              <Space>
                Toate
                <Badge count={notifications.length} style={{ backgroundColor: "#64748B" }} size="small" />
              </Space>
            ),
            children: (
              <NotificationsList
                notifications={notifications}
                loading={isLoading}
                onMarkRead={(id) => markReadMut.mutate(id)}
                getTimeAgo={getTimeAgo}
              />
            ),
          },
          {
            key: "unread",
            label: (
              <Space>
                Necitite
                <Badge count={unreadCount} size="small" />
              </Space>
            ),
            children: (
              <NotificationsList
                notifications={notifications}
                loading={isLoading}
                onMarkRead={(id) => markReadMut.mutate(id)}
                getTimeAgo={getTimeAgo}
              />
            ),
          },
          {
            key: "read",
            label: "Citite",
            children: (
              <NotificationsList
                notifications={notifications}
                loading={isLoading}
                onMarkRead={(id) => markReadMut.mutate(id)}
                getTimeAgo={getTimeAgo}
              />
            ),
          },
          {
            key: "preferences",
            label: (
              <Space>
                <FilterOutlined /> Preferințe
              </Space>
            ),
            children: (
              <Card
                title="Matrice preferințe notificări (Eveniment × Canal)"
                size="small"
                style={{ background: "#111827", border: "1px solid rgba(255,255,255,0.06)" }}
              >
                <Table
                  dataSource={EVENT_TYPES}
                  rowKey="key"
                  size="small"
                  pagination={false}
                  columns={[
                    {
                      title: "Modul",
                      dataIndex: "module",
                      key: "module",
                      width: 100,
                      render: (m: string) => {
                        const colors: Record<string, string> = {
                          Pipeline: "blue", PM: "green", CRM: "purple", RM: "orange", BI: "cyan",
                        };
                        return <Tag color={colors[m]}>{m}</Tag>;
                      },
                    },
                    { title: "Eveniment", dataIndex: "label", key: "label" },
                    ...CHANNELS.map((ch) => ({
                      title: (
                        <Space size={4}>
                          {ch.icon}
                          <span>{ch.label}</span>
                        </Space>
                      ),
                      key: ch.key,
                      width: 100,
                      align: "center" as const,
                      render: (_: unknown, record: { key: string }) => (
                        <Switch
                          size="small"
                          checked={preferences[record.key]?.[ch.key] ?? false}
                          onChange={() => togglePreference(record.key, ch.key)}
                        />
                      ),
                    })),
                  ]}
                />
                <div style={{ marginTop: 16, textAlign: "right" }}>
                  <Button type="primary" onClick={() => message.success("Preferințe salvate")}>
                    Salvează preferințe
                  </Button>
                </div>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}

function NotificationsList({
  notifications,
  loading,
  onMarkRead,
  getTimeAgo,
}: {
  notifications: AppNotification[];
  loading: boolean;
  onMarkRead: (id: string) => void;
  getTimeAgo: (date: string) => string;
}) {
  if (!loading && notifications.length === 0) {
    return (
      <EmptyState
        icon={<BellOutlined style={{ color: "#3B82F6" }} />}
        title="Nicio notificare"
        description="Vei primi notificări când apar evenimente importante."
      />
    );
  }

  return (
    <List
      loading={loading}
      dataSource={notifications}
      renderItem={(item: AppNotification) => (
        <List.Item
          style={{
            background: item.status === "unread" ? "rgba(59,130,246,0.05)" : "transparent",
            borderRadius: 8,
            padding: "12px 16px",
            marginBottom: 4,
            border: item.status === "unread" ? "1px solid rgba(59,130,246,0.15)" : "1px solid transparent",
          }}
          actions={[
            item.status === "unread" && (
              <Tooltip title="Marchează ca citit" key="read">
                <Button
                  type="text"
                  size="small"
                  icon={<CheckOutlined />}
                  onClick={() => onMarkRead(item.id)}
                />
              </Tooltip>
            ),
          ].filter(Boolean)}
        >
          <List.Item.Meta
            avatar={
              <Badge dot={item.status === "unread"} offset={[-2, 2]}>
                <BellOutlined style={{ fontSize: 18, color: item.status === "unread" ? "#3B82F6" : "#64748B" }} />
              </Badge>
            }
            title={
              <Space>
                <Text strong={item.status === "unread"}>{item.title}</Text>
                {item.entity_type && <Tag style={{ fontSize: 10 }}>{item.entity_type}</Tag>}
              </Space>
            }
            description={
              <div>
                <Paragraph style={{ margin: 0, color: "#94A3B8", fontSize: 13 }}>{item.message}</Paragraph>
                <Text type="secondary" style={{ fontSize: 11 }}>{getTimeAgo(item.created_at)}</Text>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
}
