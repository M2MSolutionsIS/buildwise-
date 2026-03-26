/**
 * E-015: WBS Editor — F069
 * Tree view hierarchy with inline edit, drag & drop reorder.
 * 3-level: phases → activities → sub-activities.
 * Auto-generated WBS codes (1.0, 1.1, 1.1.1).
 */
import { useState, useMemo, useCallback } from "react";
import { useParams } from "react-router-dom";
import {
  Typography,
  Button,
  Tree,
  Space,
  Input,
  Modal,
  Form,
  App,
  Tag,
  Popconfirm,
  Progress,
  Empty,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PartitionOutlined,
  FolderOutlined,
  FileOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pmService } from "../services/pmService";
import { useTranslation } from "../../../i18n";
import type { PMTask } from "../../../types";
import type { DataNode } from "antd/es/tree";

const { Title, Text } = Typography;

interface WBSTreeNode extends DataNode {
  task: PMTask;
  children: WBSTreeNode[];
}

function buildTreeData(nodes: PMTask[]): WBSTreeNode[] {
  const map = new Map<string | undefined, PMTask[]>();
  for (const node of nodes) {
    const parentId = node.parent_task_id || undefined;
    if (!map.has(parentId)) map.set(parentId, []);
    map.get(parentId)!.push(node);
  }

  function buildLevel(parentId: string | undefined, prefix: string): WBSTreeNode[] {
    const children = map.get(parentId) || [];
    children.sort((a, b) => a.sort_order - b.sort_order);
    return children.map((node, idx) => {
      const code = prefix ? `${prefix}.${idx + 1}` : `${idx + 1}`;
      const subChildren = buildLevel(node.id, code);
      const depth = prefix.split(".").filter(Boolean).length;
      return {
        key: node.id,
        title: null as unknown as string,
        task: node,
        icon:
          depth === 0 ? (
            <FolderOutlined style={{ color: "#047857" }} />
          ) : subChildren.length > 0 ? (
            <FolderOutlined style={{ color: "#2563EB" }} />
          ) : (
            <FileOutlined style={{ color: "#64748B" }} />
          ),
        children: subChildren,
        wbsCode: code,
      } as WBSTreeNode & { wbsCode: string };
    });
  }

  return buildLevel(undefined, "");
}

function flattenWithCodes(
  treeNodes: (WBSTreeNode & { wbsCode?: string })[],
  result: Map<string, string> = new Map()
): Map<string, string> {
  for (const node of treeNodes) {
    if ((node as { wbsCode?: string }).wbsCode) {
      result.set(node.key as string, (node as { wbsCode?: string }).wbsCode!);
    }
    if (node.children?.length) {
      flattenWithCodes(node.children as (WBSTreeNode & { wbsCode?: string })[], result);
    }
  }
  return result;
}

export default function WBSEditorPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const t = useTranslation();
  const { message } = App.useApp();
  const queryClient = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingNode, setEditingNode] = useState<PMTask | null>(null);
  const [parentId, setParentId] = useState<string | undefined>();
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ["wbs", projectId],
    queryFn: () => pmService.listWbsNodes(projectId!),
    enabled: !!projectId,
  });

  const nodes = data?.data || [];
  const treeData = useMemo(() => buildTreeData(nodes), [nodes]);
  const wbsCodes = useMemo(() => flattenWithCodes(treeData as (WBSTreeNode & { wbsCode?: string })[]), [treeData]);

  const createMut = useMutation({
    mutationFn: (payload: { title: string; parent_task_id?: string; description?: string }) =>
      pmService.createWbsNode(projectId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wbs", projectId] });
      message.success("Nod WBS creat");
      closeModal();
    },
    onError: () => message.error("Eroare la creare"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<PMTask> }) =>
      pmService.updateWbsNode(projectId!, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wbs", projectId] });
      message.success("Nod actualizat");
      closeModal();
    },
    onError: () => message.error("Eroare la actualizare"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => pmService.deleteWbsNode(projectId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wbs", projectId] });
      message.success("Nod șters");
    },
    onError: () => message.error("Eroare la ștergere"),
  });

  const openCreate = useCallback(
    (parent?: string) => {
      setEditingNode(null);
      setParentId(parent);
      form.resetFields();
      setModalOpen(true);
    },
    [form]
  );

  const openEdit = useCallback(
    (node: PMTask) => {
      setEditingNode(node);
      setParentId(node.parent_task_id || undefined);
      form.setFieldsValue({ title: node.title, description: node.description });
      setModalOpen(true);
    },
    [form]
  );

  const closeModal = () => {
    setModalOpen(false);
    setEditingNode(null);
    setParentId(undefined);
    form.resetFields();
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    if (editingNode) {
      updateMut.mutate({ id: editingNode.id, payload: values });
    } else {
      createMut.mutate({ ...values, parent_task_id: parentId });
    }
  };

  // Render tree node title with actions
  const renderTitle = useCallback(
    (nodeData: WBSTreeNode & { wbsCode?: string }) => {
      const { task } = nodeData;
      const code = wbsCodes.get(task.id) || nodeData.wbsCode || "";
      const depth = code.split(".").length - 1;
      const depthColors = ["#047857", "#2563EB", "#7C3AED"];

      return (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
            padding: "4px 0",
          }}
        >
          <Space>
            <Tag
              color={depthColors[depth] || "#64748B"}
              style={{ fontFamily: "monospace", fontSize: 11 }}
            >
              {code}
            </Tag>
            <Text strong={depth === 0} style={{ fontSize: depth === 0 ? 14 : 13 }}>
              {task.title}
            </Text>
            {task.percent_complete > 0 && (
              <Progress
                percent={task.percent_complete}
                size="small"
                style={{ width: 80, margin: 0 }}
                strokeColor={depthColors[depth]}
              />
            )}
          </Space>
          <Space size="small" onClick={(e) => e.stopPropagation()}>
            {depth < 2 && (
              <Button
                type="text"
                size="small"
                icon={<PlusOutlined />}
                onClick={() => openCreate(task.id)}
                title="Adaugă sub-element"
              />
            )}
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => openEdit(task)}
            />
            <Popconfirm
              title="Ștergeți acest nod WBS?"
              onConfirm={() => deleteMut.mutate(task.id)}
              okText={t.common.yes}
              cancelText={t.common.no}
            >
              <Button type="text" size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Space>
        </div>
      );
    },
    [wbsCodes, openCreate, openEdit, deleteMut, t]
  );

  // Apply custom title renderer
  const renderableTree = useMemo(() => {
    function applyTitles(items: WBSTreeNode[]): WBSTreeNode[] {
      return items.map((item) => ({
        ...item,
        title: renderTitle(item as WBSTreeNode & { wbsCode?: string }),
        children: item.children?.length ? applyTitles(item.children) : [],
      }));
    }
    return applyTitles(treeData);
  }, [treeData, renderTitle]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <PartitionOutlined style={{ fontSize: 20, color: "#047857" }} />
          <Title level={4} style={{ margin: 0 }}>
            {t.pm.wbsEditor}
          </Title>
        </Space>
        <Space>
          <Button
            size="small"
            onClick={() =>
              setExpandedKeys(nodes.map((n) => n.id))
            }
          >
            Expand All
          </Button>
          <Button size="small" onClick={() => setExpandedKeys([])}>
            Collapse All
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => openCreate()}>
            {t.pm.phase}
          </Button>
        </Space>
      </div>

      {/* Stats */}
      <div style={{ marginBottom: 16, display: "flex", gap: 16 }}>
        <Tag>{nodes.length} noduri WBS</Tag>
        <Tag color="green">
          {nodes.filter((n) => !n.parent_task_id).length} faze
        </Tag>
        <Tag color="blue">
          {nodes.filter((n) => n.parent_task_id && nodes.some((c) => c.parent_task_id === n.id)).length} activități
        </Tag>
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: 48 }}>
          <Text type="secondary">{t.common.loading}</Text>
        </div>
      ) : nodes.length === 0 ? (
        <Empty
          description="Niciun element WBS definit"
          style={{ padding: 48 }}
        >
          <Button type="primary" icon={<PlusOutlined />} onClick={() => openCreate()}>
            Adaugă prima fază
          </Button>
        </Empty>
      ) : (
        <div
          style={{
            background: "#1A1A2E",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.06)",
            padding: 16,
          }}
        >
          <Tree
            treeData={renderableTree}
            showIcon
            blockNode
            expandedKeys={expandedKeys}
            onExpand={(keys) => setExpandedKeys(keys)}
            draggable
            style={{ background: "transparent" }}
          />
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        title={editingNode ? `${t.common.edit} — ${editingNode.title}` : `${t.common.add} ${t.pm.phase}`}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSubmit}
        confirmLoading={createMut.isPending || updateMut.isPending}
        okText={t.common.save}
        cancelText={t.common.cancel}
      >
        <Form form={form} layout="vertical" size="middle">
          <Form.Item
            name="title"
            label={t.common.name}
            rules={[{ required: true, message: "Nume obligatoriu" }]}
          >
            <Input placeholder="Ex: Lucrări structură" />
          </Form.Item>
          <Form.Item name="description" label={t.common.description}>
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
