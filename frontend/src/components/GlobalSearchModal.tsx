/**
 * E-026: Global Search Modal — F137, F138
 * Caută în contacte, oportunități, proiecte, oferte.
 * Ctrl+K / Cmd+K shortcut. Keyboard navigation.
 */
import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Modal, Input, Typography, Tag, Empty, Spin, Space } from "antd";
import {
  SearchOutlined,
  TeamOutlined,
  FunnelPlotOutlined,
  ProjectOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import api from "../services/api";

const { Text } = Typography;

/* ─── Types ───────────────────────────────────────────────────────────────── */

interface SearchResult {
  id: string;
  title: string;
  subtitle?: string;
  type: "contact" | "opportunity" | "project" | "offer";
  status?: string;
  link: string;
}

interface SearchResponse {
  contacts: { id: string; company_name: string; stage: string; city?: string }[];
  opportunities: { id: string; title: string; stage: string; estimated_value?: number }[];
  projects: { id: string; name: string; project_number: string; status: string }[];
  offers: { id: string; title: string; offer_number: string; status: string }[];
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  contact: <TeamOutlined />,
  opportunity: <FunnelPlotOutlined />,
  project: <ProjectOutlined />,
  offer: <FileTextOutlined />,
};

const TYPE_LABELS: Record<string, string> = {
  contact: "Contacte",
  opportunity: "Oportunități",
  project: "Proiecte",
  offer: "Oferte",
};

const TYPE_COLORS: Record<string, string> = {
  contact: "blue",
  opportunity: "purple",
  project: "green",
  offer: "orange",
};

/* ─── Component ───────────────────────────────────────────────────────────── */

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function GlobalSearchModal({ open, onClose }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Reset on open
  useEffect(() => {
    if (open) {
      setQuery("");
      setResults([]);
      setSelectedIdx(0);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  // Debounced search
  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.get<{ data: SearchResponse }>("/search", {
        params: { q, limit: 5 },
      });
      const resp = data.data;
      const mapped: SearchResult[] = [
        ...(resp.contacts ?? []).map((c) => ({
          id: c.id,
          title: c.company_name,
          subtitle: c.city ?? "",
          type: "contact" as const,
          status: c.stage,
          link: `/crm/contacts/${c.id}`,
        })),
        ...(resp.opportunities ?? []).map((o) => ({
          id: o.id,
          title: o.title,
          subtitle: o.estimated_value
            ? `${new Intl.NumberFormat("ro-RO").format(o.estimated_value)} RON`
            : "",
          type: "opportunity" as const,
          status: o.stage,
          link: `/pipeline/opportunities/${o.id}`,
        })),
        ...(resp.projects ?? []).map((p) => ({
          id: p.id,
          title: p.name,
          subtitle: p.project_number,
          type: "project" as const,
          status: p.status,
          link: `/pm/projects/${p.id}/gantt`,
        })),
        ...(resp.offers ?? []).map((o) => ({
          id: o.id,
          title: o.title,
          subtitle: o.offer_number,
          type: "offer" as const,
          status: o.status,
          link: `/pipeline/offers/${o.id}`,
        })),
      ];
      setResults(mapped);
      setSelectedIdx(0);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleQueryChange = (val: string) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(val), 300);
  };

  const handleSelect = (result: SearchResult) => {
    onClose();
    navigate(result.link);
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIdx((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && results[selectedIdx]) {
      e.preventDefault();
      handleSelect(results[selectedIdx]);
    }
  };

  // Group results by type
  const grouped = results.reduce<Record<string, SearchResult[]>>((acc, r) => {
    if (!acc[r.type]) acc[r.type] = [];
    acc[r.type].push(r);
    return acc;
  }, {});

  // Flat index for keyboard nav
  let flatIdx = 0;

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      closable={false}
      width={560}
      styles={{ body: { padding: 0 } }}
      style={{ top: 80 }}
    >
      <div style={{ padding: "12px 16px", borderBottom: "1px solid #f0f0f0" }}>
        <Input
          ref={inputRef as never}
          placeholder="Caută contacte, oportunități, proiecte, oferte..."
          prefix={<SearchOutlined />}
          suffix={
            <Text type="secondary" style={{ fontSize: 11 }}>
              ESC pentru închidere
            </Text>
          }
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          variant="borderless"
          size="large"
          allowClear
        />
      </div>

      <div
        style={{
          maxHeight: 400,
          overflow: "auto",
          padding: results.length > 0 || loading ? "8px 0" : 0,
        }}
      >
        {loading && (
          <div style={{ textAlign: "center", padding: 24 }}>
            <Spin size="small" />
            <Text type="secondary" style={{ marginLeft: 8 }}>
              Se caută...
            </Text>
          </div>
        )}

        {!loading && query.length >= 2 && results.length === 0 && (
          <Empty
            description="Niciun rezultat găsit"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ padding: 24 }}
          />
        )}

        {!loading &&
          Object.entries(grouped).map(([type, items]) => (
            <div key={type}>
              <div
                style={{
                  padding: "6px 16px",
                  background: "#fafafa",
                  fontSize: 11,
                  fontWeight: 600,
                  color: "#888",
                  textTransform: "uppercase",
                }}
              >
                <Space size={4}>
                  {TYPE_ICONS[type]}
                  {TYPE_LABELS[type]}
                  <Tag style={{ fontSize: 10 }}>{items.length}</Tag>
                </Space>
              </div>
              {items.map((item) => {
                const idx = flatIdx++;
                const isSelected = idx === selectedIdx;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleSelect(item)}
                    style={{
                      padding: "8px 16px",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      background: isSelected ? "#e6f4ff" : "transparent",
                      borderLeft: isSelected ? "3px solid #1677ff" : "3px solid transparent",
                    }}
                    onMouseEnter={() => setSelectedIdx(idx)}
                  >
                    <div>
                      <Text strong style={{ fontSize: 13 }}>
                        {highlightMatch(item.title, query)}
                      </Text>
                      {item.subtitle && (
                        <Text type="secondary" style={{ fontSize: 11, marginLeft: 8 }}>
                          {item.subtitle}
                        </Text>
                      )}
                    </div>
                    {item.status && (
                      <Tag color={TYPE_COLORS[type]} style={{ fontSize: 11 }}>
                        {item.status}
                      </Tag>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
      </div>

      {/* Footer with keyboard hints */}
      {results.length > 0 && (
        <div
          style={{
            padding: "8px 16px",
            borderTop: "1px solid #f0f0f0",
            display: "flex",
            gap: 16,
            fontSize: 11,
            color: "#888",
          }}
        >
          <span>
            <kbd style={kbdStyle}>↑↓</kbd> navigare
          </span>
          <span>
            <kbd style={kbdStyle}>Enter</kbd> selectare
          </span>
          <span>
            <kbd style={kbdStyle}>Esc</kbd> închidere
          </span>
        </div>
      )}
    </Modal>
  );
}

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

const kbdStyle: React.CSSProperties = {
  display: "inline-block",
  padding: "1px 5px",
  fontSize: 10,
  background: "#f0f0f0",
  borderRadius: 3,
  border: "1px solid #d9d9d9",
  marginRight: 4,
};

function highlightMatch(text: string, query: string): React.ReactNode {
  if (!query) return text;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark style={{ background: "#ffd666", padding: 0 }}>
        {text.slice(idx, idx + query.length)}
      </mark>
      {text.slice(idx + query.length)}
    </>
  );
}
