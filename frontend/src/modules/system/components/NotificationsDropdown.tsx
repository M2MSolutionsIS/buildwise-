/**
 * F141 — Notifications Center (Bell icon dropdown)
 */
import { Badge, Button, Dropdown, List, Typography, Space, Empty, App } from "antd";
import {
  BellOutlined,
  CheckOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { notificationService } from "../services/notificationService";
import type { AppNotification } from "../../../types";

const { Text } = Typography;

export default function NotificationsDropdown() {
  const navigate = useNavigate();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["notifications", { status: "unread" }],
    queryFn: () =>
      notificationService.list({ notification_status: "unread", per_page: 10 }),
    refetchInterval: 60_000,
  });

  const markReadMutation = useMutation({
    mutationFn: notificationService.markRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: notificationService.markAllRead,
    onSuccess: (result) => {
      message.success(`${result.data.marked_read} notificări marcate ca citite.`);
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const generateFollowUpMutation = useMutation({
    mutationFn: notificationService.generateFollowUps,
    onSuccess: (result) => {
      const count = result.data.length;
      if (count > 0) {
        message.success(`${count} reminder-uri follow-up generate.`);
      } else {
        message.info("Nu sunt follow-up-uri noi de generat.");
      }
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const notifications: AppNotification[] = data?.data ?? [];
  const unreadCount = data?.meta?.total ?? 0;

  const handleClick = (notif: AppNotification) => {
    markReadMutation.mutate(notif.id);
    if (notif.link) {
      navigate(notif.link);
    }
  };

  const formatTime = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return "acum";
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}z`;
  };

  const dropdownContent = (
    <div
      style={{
        width: 380,
        maxHeight: 480,
        background: "#fff",
        borderRadius: 8,
        boxShadow: "0 6px 16px rgba(0,0,0,0.12)",
      }}
    >
      <div
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid #f0f0f0",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Text strong>Notificări</Text>
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<ClockCircleOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              generateFollowUpMutation.mutate();
            }}
            loading={generateFollowUpMutation.isPending}
          >
            Follow-up
          </Button>
          {unreadCount > 0 && (
            <Button
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                markAllReadMutation.mutate();
              }}
            >
              Citește tot
            </Button>
          )}
        </Space>
      </div>
      <div style={{ maxHeight: 380, overflow: "auto" }}>
        {notifications.length === 0 ? (
          <Empty
            description="Nicio notificare nouă"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ padding: 24 }}
          />
        ) : (
          <List
            dataSource={notifications}
            renderItem={(notif) => (
              <List.Item
                style={{
                  padding: "10px 16px",
                  cursor: "pointer",
                  background:
                    notif.status === "unread" ? "#f6ffed" : "transparent",
                }}
                onClick={() => handleClick(notif)}
              >
                <List.Item.Meta
                  title={
                    <Text
                      strong={notif.status === "unread"}
                      style={{ fontSize: 13 }}
                    >
                      {notif.title}
                    </Text>
                  }
                  description={
                    <div>
                      <Text
                        type="secondary"
                        style={{ fontSize: 12, display: "block" }}
                      >
                        {notif.message.length > 80
                          ? notif.message.slice(0, 80) + "..."
                          : notif.message}
                      </Text>
                      <Text
                        type="secondary"
                        style={{ fontSize: 11, marginTop: 2 }}
                      >
                        {formatTime(notif.created_at)}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>
    </div>
  );

  return (
    <Dropdown
      dropdownRender={() => dropdownContent}
      trigger={["click"]}
      placement="bottomRight"
    >
      <Badge count={unreadCount} size="small">
        <Button type="text" icon={<BellOutlined />} />
      </Badge>
    </Dropdown>
  );
}
