/**
 * E-031 / F132: AI Assistant — Chatbot integrat (P2+P3)
 * Chat interface cu:
 * - Input + predefined suggestions
 * - Messages (user + assistant) cu visual cards inline
 * - KPI cards, chart cards, table cards, suggestion cards
 * - Sidebar cu quick suggestions + model info
 * - Conversation history list
 */
import { useState, useRef, useEffect, useMemo } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Input,
  Space,
  List,
  Tag,
  Spin,
  Avatar,
  Divider,
  Empty,
  Statistic,
  Tooltip,
} from "antd";
import {
  RobotOutlined,
  SendOutlined,
  UserOutlined,
  PlusOutlined,
  MessageOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  BarChartOutlined,
  TableOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  HistoryOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { biService } from "../services/biService";
import type { AIConversation, AIMessage, AIResponseCard } from "../../../types";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// ─── Predefined suggestion categories ────────────────────────────────────────

const QUICK_SUGGESTIONS = [
  { label: "Cum stă pipeline-ul?", icon: <BarChartOutlined />, category: "pipeline" },
  { label: "Arată KPI-urile critice", icon: <ThunderboltOutlined />, category: "kpi" },
  { label: "Care sunt proiectele active?", icon: <BulbOutlined />, category: "pm" },
  { label: "Cine are cele mai multe task-uri?", icon: <UserOutlined />, category: "rm" },
  { label: "Raport vânzări luna asta", icon: <TableOutlined />, category: "pipeline" },
  { label: "Previziune venituri Q2", icon: <BarChartOutlined />, category: "forecast" },
];

// ─── Visual Card Components ──────────────────────────────────────────────────

function KPICard({ data }: { data: Record<string, unknown> }) {
  const value = Number(data.value ?? 0);
  const delta = Number(data.delta ?? 0);
  const unit = String(data.unit ?? "");
  const label = String(data.label ?? "KPI");

  return (
    <Card size="small" style={{ display: "inline-block", marginRight: 8, marginBottom: 8, minWidth: 140 }}>
      <Statistic
        title={label}
        value={value}
        suffix={unit}
        prefix={
          delta > 0 ? <ArrowUpOutlined style={{ color: "#52c41a" }} /> :
          delta < 0 ? <ArrowDownOutlined style={{ color: "#ff4d4f" }} /> : undefined
        }
        valueStyle={{ fontSize: 18 }}
      />
      {delta !== 0 && (
        <Text style={{ fontSize: 11, color: delta > 0 ? "#52c41a" : "#ff4d4f" }}>
          {delta > 0 ? "+" : ""}{delta}%
        </Text>
      )}
    </Card>
  );
}

function ChartCard({ data }: { data: Record<string, unknown> }) {
  const title = String(data.title ?? "Chart");
  const values = (data.values ?? []) as number[];
  const max = Math.max(...values, 1);
  const barWidth = 100 / Math.max(values.length, 1);

  return (
    <Card size="small" style={{ marginBottom: 8 }} title={title}>
      <div style={{ display: "flex", alignItems: "flex-end", height: 60, gap: 2 }}>
        {values.map((v, i) => (
          <Tooltip key={i} title={v}>
            <div
              style={{
                width: `${barWidth}%`,
                height: `${(v / max) * 100}%`,
                background: `linear-gradient(180deg, #1677ff, #69b1ff)`,
                borderRadius: "2px 2px 0 0",
                minHeight: 4,
              }}
            />
          </Tooltip>
        ))}
      </div>
      {(data.labels as string[] | undefined) && (
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#999", marginTop: 4 }}>
          {(data.labels as string[]).map((l, i) => <span key={i}>{l}</span>)}
        </div>
      )}
    </Card>
  );
}

function TableCard({ data }: { data: Record<string, unknown> }) {
  const title = String(data.title ?? "Tabel");
  const headers = (data.headers ?? []) as string[];
  const rows = (data.rows ?? []) as string[][];

  return (
    <Card size="small" style={{ marginBottom: 8 }} title={title}>
      <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i} style={{ textAlign: "left", padding: "4px 8px", borderBottom: "1px solid #f0f0f0", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} style={{ padding: "4px 8px", borderBottom: "1px solid #f0f0f0" }}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

function SuggestionCard({ data, onSend }: { data: Record<string, unknown>; onSend: (msg: string) => void }) {
  const suggestions = (data.suggestions ?? []) as string[];
  return (
    <div style={{ marginTop: 4 }}>
      <Text type="secondary" style={{ fontSize: 11 }}>Sugestii:</Text>
      <div style={{ marginTop: 4, display: "flex", flexWrap: "wrap", gap: 4 }}>
        {suggestions.map((s, i) => (
          <Tag
            key={i}
            color="blue"
            style={{ cursor: "pointer" }}
            onClick={() => onSend(s)}
          >
            {s}
          </Tag>
        ))}
      </div>
    </div>
  );
}

function ResponseCard({ card, onSend }: { card: AIResponseCard; onSend: (msg: string) => void }) {
  switch (card.type) {
    case "kpi":
      return <KPICard data={card.data} />;
    case "chart":
      return <ChartCard data={card.data} />;
    case "table":
      return <TableCard data={card.data} />;
    case "suggestion":
      return <SuggestionCard data={card.data} onSend={onSend} />;
    default:
      return <Text>{JSON.stringify(card.data)}</Text>;
  }
}

// ─── Simulated assistant responses (placeholder until real AI backend) ────────

function simulateResponse(userMsg: string): { content: string; cards: AIResponseCard[] } {
  const lower = userMsg.toLowerCase();

  if (lower.includes("pipeline") || lower.includes("vânzări") || lower.includes("vanzari")) {
    return {
      content: "Iată un sumar al pipeline-ului curent:",
      cards: [
        { type: "kpi", data: { label: "Oportunități Active", value: 24, delta: 12, unit: "" } },
        { type: "kpi", data: { label: "Valoare Pipeline", value: 1250000, delta: 8, unit: "RON" } },
        { type: "kpi", data: { label: "Win Rate", value: 34, delta: -2, unit: "%" } },
        { type: "chart", data: { title: "Pipeline per Etapă", values: [8, 6, 4, 3, 2, 1], labels: ["Identificare", "Evaluare", "Ofertă", "Negociere", "Contract", "Execuție"] } },
        { type: "suggestion", data: { suggestions: ["Arată ofertele în așteptare", "Care este valoarea medie?", "Compară cu luna trecută"] } },
      ],
    };
  }

  if (lower.includes("kpi") || lower.includes("critic")) {
    return {
      content: "KPI-uri care necesită atenție:",
      cards: [
        { type: "kpi", data: { label: "CPI (Cost Index)", value: 0.87, delta: -5, unit: "" } },
        { type: "kpi", data: { label: "SPI (Schedule Index)", value: 0.92, delta: -3, unit: "" } },
        { type: "kpi", data: { label: "Satisfacție Client", value: 72, delta: -8, unit: "%" } },
        { type: "suggestion", data: { suggestions: ["Detalii CPI per proiect", "Istoric SPI", "Ce cauzează scăderea?"] } },
      ],
    };
  }

  if (lower.includes("proiect") || lower.includes("active")) {
    return {
      content: "Proiectele active în acest moment:",
      cards: [
        { type: "table", data: { title: "Proiecte Active", headers: ["Proiect", "Status", "Progres", "Buget"], rows: [
          ["Renovare Bloc A3", "În execuție", "67%", "245,000 RON"],
          ["Termoizolare Birouri", "Planificare", "15%", "180,000 RON"],
          ["Fațadă Spitalul Municipal", "În execuție", "43%", "520,000 RON"],
        ] } },
        { type: "kpi", data: { label: "Total Proiecte", value: 12, delta: 3, unit: "" } },
        { type: "suggestion", data: { suggestions: ["Arată proiectele cu risc", "Care proiect e în întârziere?", "Buget total alocat"] } },
      ],
    };
  }

  if (lower.includes("previziune") || lower.includes("forecast") || lower.includes("q2")) {
    return {
      content: "Previziune venituri bazată pe datele istorice (placeholder ML):",
      cards: [
        { type: "chart", data: { title: "Forecast Venituri Q2 2026", values: [420, 480, 510, 530, 560, 590], labels: ["Ian", "Feb", "Mar", "Apr*", "Mai*", "Iun*"] } },
        { type: "kpi", data: { label: "Forecast Q2", value: 1680, delta: 15, unit: "k RON" } },
        { type: "kpi", data: { label: "Confidence", value: 82, delta: 0, unit: "%" } },
        { type: "suggestion", data: { suggestions: ["Ce factori influențează?", "Arată scenariul pesimist", "Compară cu anul trecut"] } },
      ],
    };
  }

  if (lower.includes("task") || lower.includes("angajat") || lower.includes("echip")) {
    return {
      content: "Distribuția task-urilor pe echipă:",
      cards: [
        { type: "table", data: { title: "Top Angajați per Task-uri", headers: ["Angajat", "Task-uri Active", "Completate"], rows: [
          ["Ion Popescu", "8", "23"],
          ["Maria Ionescu", "6", "31"],
          ["Andrei Marin", "5", "18"],
        ] } },
        { type: "suggestion", data: { suggestions: ["Cine are disponibilitate?", "Arată alocările pe proiecte", "Overtime luna aceasta"] } },
      ],
    };
  }

  return {
    content: "Îți pot ajuta cu informații despre pipeline, KPI-uri, proiecte, resurse sau previziuni. Ce ai dori să afli?",
    cards: [
      { type: "suggestion", data: { suggestions: ["Cum stă pipeline-ul?", "Arată KPI-urile critice", "Proiecte active", "Previziune venituri Q2"] } },
    ],
  };
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function AIAssistantPage() {
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = useState("");
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [localMessages, setLocalMessages] = useState<AIMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  // Conversations list
  const { data: convsData } = useQuery({
    queryKey: ["ai-conversations"],
    queryFn: () => biService.listConversations({ per_page: 50 }),
  });

  const conversations = (convsData?.data ?? []) as AIConversation[];

  // Create conversation
  const createConvMut = useMutation({
    mutationFn: (title?: string) => biService.createConversation(title),
    onSuccess: (res) => {
      const conv = res.data as AIConversation;
      setActiveConvId(conv.id);
      setLocalMessages([]);
      queryClient.invalidateQueries({ queryKey: ["ai-conversations"] });
    },
  });

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages, isTyping]);

  // Load conversation
  const loadConversation = async (convId: string) => {
    setActiveConvId(convId);
    try {
      const res = await biService.getConversation(convId);
      const conv = res.data as AIConversation;
      setLocalMessages(conv.messages ?? []);
    } catch {
      setLocalMessages([]);
    }
  };

  // Send message
  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    // If no active conversation, create one
    let convId = activeConvId;
    if (!convId) {
      try {
        const res = await biService.createConversation(content.slice(0, 50));
        const conv = res.data as AIConversation;
        convId = conv.id;
        setActiveConvId(conv.id);
        queryClient.invalidateQueries({ queryKey: ["ai-conversations"] });
      } catch {
        convId = `local-${Date.now()}`;
        setActiveConvId(convId);
      }
    }

    // Add user message locally
    const userMsg: AIMessage = {
      id: `msg-${Date.now()}`,
      conversation_id: convId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    setLocalMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsTyping(true);

    // Try sending to backend, fall back to simulated response
    try {
      await biService.sendMessage(convId, content);
    } catch {
      // Backend may not be running — use simulated response
    }

    // Simulated response (placeholder until real AI)
    await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200));
    const simulated = simulateResponse(content);
    const assistantMsg: AIMessage = {
      id: `msg-${Date.now()}-reply`,
      conversation_id: convId,
      role: "assistant",
      content: simulated.content,
      cards: simulated.cards,
      created_at: new Date().toISOString(),
    };
    setLocalMessages((prev) => [...prev, assistantMsg]);
    setIsTyping(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const activeConvTitle = useMemo(() => {
    const conv = conversations.find((c) => c.id === activeConvId);
    return conv?.title ?? "Conversație nouă";
  }, [conversations, activeConvId]);

  return (
    <div style={{ padding: 24, height: "calc(100vh - 120px)", display: "flex", flexDirection: "column" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16, flexShrink: 0 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <RobotOutlined /> AI Assistant (E-031 / F132)
          </Title>
          <Text type="secondary">Asistență, navigare, sugestii și previziuni</Text>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => createConvMut.mutate("Conversație nouă")}
          >
            Conversație Nouă
          </Button>
        </Col>
      </Row>

      <Row gutter={16} style={{ flex: 1, overflow: "hidden" }}>
        {/* ─── Conversation History ─── */}
        <Col xs={0} md={6} style={{ height: "100%", overflow: "auto" }}>
          <Card
            title={<><HistoryOutlined /> Istoric</>}
            size="small"
            style={{ height: "100%" }}
            styles={{ body: { padding: "4px 0", overflow: "auto" } }}
          >
            {conversations.length === 0 ? (
              <Empty description="Nicio conversație" style={{ padding: 16 }} />
            ) : (
              <List
                dataSource={conversations}
                size="small"
                renderItem={(conv: AIConversation) => (
                  <List.Item
                    style={{
                      padding: "8px 12px",
                      cursor: "pointer",
                      background: conv.id === activeConvId ? "#e6f4ff" : undefined,
                    }}
                    onClick={() => loadConversation(conv.id)}
                  >
                    <Space>
                      <MessageOutlined />
                      <Text ellipsis style={{ maxWidth: 120 }}>
                        {conv.title ?? "Fără titlu"}
                      </Text>
                    </Space>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        {/* ─── Chat Area ─── */}
        <Col xs={24} md={12} style={{ height: "100%", display: "flex", flexDirection: "column" }}>
          <Card
            title={activeConvTitle}
            size="small"
            style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}
            styles={{ body: { flex: 1, overflow: "auto", padding: 12 } }}
          >
            {/* Messages */}
            <div style={{ flex: 1, overflow: "auto", paddingBottom: 8 }}>
              {localMessages.length === 0 && !isTyping && (
                <div style={{ textAlign: "center", padding: 40 }}>
                  <RobotOutlined style={{ fontSize: 48, color: "#d9d9d9" }} />
                  <Paragraph type="secondary" style={{ marginTop: 16 }}>
                    Salut! Sunt asistentul AI BuildWise. Întreabă-mă orice despre datele din platformă.
                  </Paragraph>
                  <Space wrap style={{ marginTop: 8 }}>
                    {QUICK_SUGGESTIONS.slice(0, 4).map((s) => (
                      <Tag
                        key={s.label}
                        color="blue"
                        style={{ cursor: "pointer", padding: "4px 8px" }}
                        onClick={() => sendMessage(s.label)}
                      >
                        {s.icon} {s.label}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}

              {localMessages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    display: "flex",
                    justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                    marginBottom: 12,
                  }}
                >
                  <div style={{ maxWidth: "85%", display: "flex", gap: 8, flexDirection: msg.role === "user" ? "row-reverse" : "row" }}>
                    <Avatar
                      size="small"
                      icon={msg.role === "user" ? <UserOutlined /> : <RobotOutlined />}
                      style={{ backgroundColor: msg.role === "user" ? "#1677ff" : "#722ed1", flexShrink: 0, marginTop: 2 }}
                    />
                    <div>
                      <div
                        style={{
                          background: msg.role === "user" ? "#1677ff" : "#f5f5f5",
                          color: msg.role === "user" ? "#fff" : "#000",
                          padding: "8px 12px",
                          borderRadius: 12,
                          borderTopLeftRadius: msg.role === "assistant" ? 4 : 12,
                          borderTopRightRadius: msg.role === "user" ? 4 : 12,
                        }}
                      >
                        <Text style={{ color: msg.role === "user" ? "#fff" : undefined }}>
                          {msg.content}
                        </Text>
                      </div>
                      {/* Visual cards for assistant */}
                      {msg.role === "assistant" && msg.cards && msg.cards.length > 0 && (
                        <div style={{ marginTop: 8 }}>
                          {msg.cards.map((card, idx) => (
                            <ResponseCard key={idx} card={card} onSend={sendMessage} />
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <Avatar size="small" icon={<RobotOutlined />} style={{ backgroundColor: "#722ed1" }} />
                  <div style={{ background: "#f5f5f5", padding: "8px 16px", borderRadius: 12 }}>
                    <Spin size="small" /> <Text type="secondary" style={{ marginLeft: 4 }}>Se gândește...</Text>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </Card>

          {/* Input Area */}
          <div style={{ marginTop: 8, flexShrink: 0 }}>
            <Space.Compact style={{ width: "100%" }}>
              <TextArea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Scrie o întrebare... (Enter pentru a trimite)"
                autoSize={{ minRows: 1, maxRows: 3 }}
                style={{ borderRadius: "8px 0 0 8px" }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={() => sendMessage(inputValue)}
                disabled={!inputValue.trim()}
                style={{ height: "auto", borderRadius: "0 8px 8px 0" }}
              />
            </Space.Compact>
          </div>
        </Col>

        {/* ─── Suggestions Sidebar ─── */}
        <Col xs={0} md={6} style={{ height: "100%", overflow: "auto" }}>
          <Card title={<><BulbOutlined /> Sugestii Rapide</>} size="small" style={{ marginBottom: 12 }}>
            <Space direction="vertical" size={4} style={{ width: "100%" }}>
              {QUICK_SUGGESTIONS.map((s) => (
                <Button
                  key={s.label}
                  type="text"
                  block
                  icon={s.icon}
                  style={{ textAlign: "left", height: "auto", padding: "6px 8px", whiteSpace: "normal" }}
                  onClick={() => sendMessage(s.label)}
                >
                  {s.label}
                </Button>
              ))}
            </Space>
          </Card>

          <Card title="Model Info" size="small">
            <Space direction="vertical" size={8} style={{ width: "100%" }}>
              <div>
                <Text type="secondary" style={{ fontSize: 11 }}>Versiune Model</Text>
                <div><Tag color="purple">BuildWise AI v0.1</Tag></div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 11 }}>Date Antrenare</Text>
                <div><Text>Placeholder — TRL7</Text></div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 11 }}>Capabilități</Text>
                <div>
                  <Tag>Pipeline Analytics</Tag>
                  <Tag>KPI Monitoring</Tag>
                  <Tag>PM Reports</Tag>
                </div>
              </div>
              <Divider dashed style={{ margin: "8px 0" }} />
              <Text type="secondary" style={{ fontSize: 10 }}>
                Implementare reală AI/ML la TRL7. Acum: date simulate pentru demonstrare UX.
              </Text>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
