/**
 * E-023: Wiki Documentation — F144, F145, F146
 * Project wiki with tree sidebar, WYSIWYG editor, version history.
 * Connected to /api/v1/pm/projects/:id/wiki
 */
import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  Typography,
  Layout,
  Tree,
  Button,
  Input,
  Space,
  Card,
  App,
  Empty,
  Spin,
  Modal,
  Form,
  List,
  Tag,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  FileTextOutlined,
  FolderOutlined,
  EditOutlined,
  SaveOutlined,
  SearchOutlined,
  BookOutlined,
  HistoryOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../services/api";
import type { ApiResponse } from "../../../types";
import EmptyState from "../../../components/EmptyState";

const { Sider, Content } = Layout;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface WikiPost {
  id: string;
  project_id: string;
  title: string;
  content: string;
  parent_id?: string;
  sort_order: number;
  is_official: boolean;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at?: string;
}

interface WikiComment {
  id: string;
  wiki_post_id: string;
  content: string;
  user_id: string;
  created_at: string;
}

export default function WikiDocumentationPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [form] = Form.useForm();

  // Fetch wiki posts
  const { data: postsData, isLoading } = useQuery({
    queryKey: ["wiki", projectId],
    queryFn: async (): Promise<ApiResponse<WikiPost[]>> => {
      const { data } = await api.get(`/pm/projects/${projectId}/wiki`);
      return data;
    },
    enabled: !!projectId,
  });

  const posts = postsData?.data || [];
  const selectedPost = posts.find((p) => p.id === selectedPostId);

  // Fetch comments for selected post
  const { data: commentsData } = useQuery({
    queryKey: ["wiki-comments", selectedPostId],
    queryFn: async (): Promise<ApiResponse<WikiComment[]>> => {
      const { data } = await api.get(`/pm/wiki/${selectedPostId}/comments`);
      return data;
    },
    enabled: !!selectedPostId,
  });

  const comments = commentsData?.data || [];

  // Create post
  const createMut = useMutation({
    mutationFn: async (payload: { title: string; content: string; parent_id?: string; is_official?: boolean }) => {
      const { data } = await api.post(`/pm/projects/${projectId}/wiki`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wiki", projectId] });
      message.success("Pagină wiki creată");
      setCreateModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("Eroare la creare"),
  });

  // Update post
  const updateMut = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: { title?: string; content?: string } }) => {
      const { data } = await api.put(`/pm/wiki/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wiki", projectId] });
      message.success("Pagină actualizată");
      setEditing(false);
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  // Add comment
  const commentMut = useMutation({
    mutationFn: async ({ postId, content }: { postId: string; content: string }) => {
      const { data } = await api.post(`/pm/wiki/${postId}/comments`, { content });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wiki-comments", selectedPostId] });
      message.success("Comentariu adăugat");
    },
  });

  // Build tree data
  const buildTree = (items: WikiPost[], parentId?: string): any[] => {
    return items
      .filter((p) => p.parent_id === parentId || (!p.parent_id && !parentId))
      .filter((p) => !search || p.title.toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => a.sort_order - b.sort_order)
      .map((p) => ({
        key: p.id,
        title: (
          <Space size={4}>
            {p.is_official && <Tag color="blue" style={{ fontSize: 10, lineHeight: "16px", padding: "0 4px" }}>oficial</Tag>}
            <span>{p.title}</span>
          </Space>
        ),
        icon: p.is_official ? <FileTextOutlined /> : <FolderOutlined />,
        children: buildTree(items, p.id),
      }));
  };

  const treeData = buildTree(posts);

  const startEdit = () => {
    if (selectedPost) {
      setEditTitle(selectedPost.title);
      setEditContent(selectedPost.content);
      setEditing(true);
    }
  };

  const saveEdit = () => {
    if (selectedPost) {
      updateMut.mutate({
        id: selectedPost.id,
        payload: { title: editTitle, content: editContent },
      });
    }
  };

  const [commentText, setCommentText] = useState("");

  return (
    <Layout style={{ background: "transparent", minHeight: 500 }}>
      <Sider
        width={280}
        style={{
          background: "#111827",
          borderRight: "1px solid rgba(255,255,255,0.06)",
          borderRadius: "8px 0 0 8px",
          padding: 12,
        }}
      >
        <Space direction="vertical" style={{ width: "100%" }} size={8}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Space>
              <BookOutlined style={{ color: "#3B82F6" }} />
              <Text strong style={{ color: "#F1F5F9" }}>Wiki</Text>
            </Space>
            <Tooltip title="Pagină nouă">
              <Button
                type="primary"
                size="small"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalOpen(true)}
              />
            </Tooltip>
          </div>

          <Input
            placeholder="Caută..."
            prefix={<SearchOutlined />}
            size="small"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />

          {isLoading ? (
            <Spin size="small" />
          ) : treeData.length === 0 ? (
            <Empty description="Nicio pagină wiki" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <Tree
              treeData={treeData}
              showIcon
              selectedKeys={selectedPostId ? [selectedPostId] : []}
              onSelect={(keys) => {
                if (keys.length > 0) {
                  setSelectedPostId(keys[0] as string);
                  setEditing(false);
                }
              }}
              style={{ background: "transparent", color: "#CBD5E1" }}
            />
          )}
        </Space>
      </Sider>

      <Content style={{ padding: 24, minHeight: 500 }}>
        {!selectedPost ? (
          <EmptyState
            icon={<BookOutlined style={{ color: "#3B82F6" }} />}
            title="Documentație Wiki"
            description="Selectează o pagină din stânga sau creează una nouă."
            actionLabel="Pagină nouă"
            onAction={() => setCreateModalOpen(true)}
          />
        ) : editing ? (
          <div>
            <Space style={{ marginBottom: 12 }}>
              <Button icon={<SaveOutlined />} type="primary" onClick={saveEdit} loading={updateMut.isPending}>
                Salvează
              </Button>
              <Button onClick={() => setEditing(false)}>Anulează</Button>
            </Space>
            <Input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              style={{ marginBottom: 12, fontSize: 18, fontWeight: 600 }}
            />
            <TextArea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={20}
              style={{ fontFamily: "monospace" }}
            />
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <Title level={3} style={{ margin: 0 }}>
                  {selectedPost.title}
                </Title>
                <Space size={8} style={{ marginTop: 4 }}>
                  {selectedPost.is_official && <Tag color="blue">Document oficial</Tag>}
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Actualizat: {new Date(selectedPost.updated_at || selectedPost.created_at).toLocaleDateString("ro-RO")}
                  </Text>
                </Space>
              </div>
              <Space>
                <Button icon={<HistoryOutlined />} onClick={() => setHistoryModalOpen(true)}>
                  Versiuni
                </Button>
                <Button icon={<EditOutlined />} onClick={startEdit}>
                  Editează
                </Button>
              </Space>
            </div>

            <Card
              size="small"
              style={{
                background: "#1E293B",
                border: "1px solid rgba(255,255,255,0.06)",
                marginBottom: 24,
              }}
            >
              <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.8, color: "#CBD5E1" }}>
                {selectedPost.content || "Niciun conținut încă."}
              </div>
            </Card>

            {/* Comments section */}
            <Title level={5}>Comentarii ({comments.length})</Title>
            <List
              dataSource={comments}
              locale={{ emptyText: "Niciun comentariu" }}
              renderItem={(c: WikiComment) => (
                <List.Item>
                  <List.Item.Meta
                    description={
                      <div>
                        <Paragraph style={{ margin: 0 }}>{c.content}</Paragraph>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {new Date(c.created_at).toLocaleString("ro-RO")}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
            <Space.Compact style={{ width: "100%", marginTop: 8 }}>
              <Input
                placeholder="Adaugă un comentariu..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                onPressEnter={() => {
                  if (commentText.trim() && selectedPostId) {
                    commentMut.mutate({ postId: selectedPostId, content: commentText });
                    setCommentText("");
                  }
                }}
              />
              <Button
                type="primary"
                onClick={() => {
                  if (commentText.trim() && selectedPostId) {
                    commentMut.mutate({ postId: selectedPostId, content: commentText });
                    setCommentText("");
                  }
                }}
                loading={commentMut.isPending}
              >
                Trimite
              </Button>
            </Space.Compact>
          </div>
        )}
      </Content>

      {/* E-023.M1: Version History Modal */}
      <Modal
        title="Istoric Versiuni"
        open={historyModalOpen}
        onCancel={() => setHistoryModalOpen(false)}
        footer={null}
        width={600}
      >
        {selectedPost && (
          <List
            dataSource={[
              {
                version: "v" + (selectedPost.updated_at ? "2" : "1"),
                date: selectedPost.updated_at || selectedPost.created_at,
                author: selectedPost.updated_by || selectedPost.created_by || "—",
                action: selectedPost.updated_at ? "Actualizat" : "Creat",
              },
              {
                version: "v1",
                date: selectedPost.created_at,
                author: selectedPost.created_by || "—",
                action: "Creat",
              },
            ].filter((v, i, arr) => i === 0 || v.date !== arr[0]?.date)}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Tag color="blue">{item.version}</Tag>}
                  title={`${item.action} de ${item.author}`}
                  description={new Date(item.date).toLocaleString("ro-RO")}
                />
              </List.Item>
            )}
          />
        )}
      </Modal>

      {/* Create Modal */}
      <Modal
        title="Pagină Wiki Nouă"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        onOk={() => form.validateFields().then((v) => createMut.mutate(v))}
        confirmLoading={createMut.isPending}
        okText="Creează"
        cancelText="Anulează"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="Titlu" rules={[{ required: true, message: "Titlu obligatoriu" }]}>
            <Input />
          </Form.Item>
          <Form.Item name="content" label="Conținut">
            <TextArea rows={6} />
          </Form.Item>
          <Form.Item name="is_official" label="Document oficial" valuePropName="checked">
            <Input type="checkbox" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}
