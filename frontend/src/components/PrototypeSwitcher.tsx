/**
 * Prototype Switcher — allows switching between P1/P2/P3 prototypes.
 * Shows in the header bar. Changes feature visibility across the app.
 *
 * P1 — BuildWise TRL5: Energy + AI
 * P2 — BAHM Operational: Construction + RM
 * P3 — M2M ERP Lite: SaaS multi-tenant
 */
import { Segmented, Tooltip, Tag, Space } from "antd";
import {
  ThunderboltOutlined,
  ToolOutlined,
  CloudOutlined,
} from "@ant-design/icons";
import { usePrototypeStore } from "../stores/prototypeStore";
import type { Prototype } from "../types";

const PROTOTYPES: { value: Prototype; label: React.ReactNode; icon: React.ReactNode; description: string; color: string }[] = [
  {
    value: "P1",
    label: "P1",
    icon: <ThunderboltOutlined />,
    description: "BuildWise TRL5 — Energy + AI",
    color: "#52c41a",
  },
  {
    value: "P2",
    label: "P2",
    icon: <ToolOutlined />,
    description: "BAHM Operational — Construcții + RM",
    color: "#1677ff",
  },
  {
    value: "P3",
    label: "P3",
    icon: <CloudOutlined />,
    description: "M2M ERP Lite — SaaS Multi-tenant",
    color: "#722ed1",
  },
];

export default function PrototypeSwitcher() {
  const { activePrototype, setPrototype } = usePrototypeStore();

  const current = PROTOTYPES.find((p) => p.value === activePrototype)!;

  return (
    <Space size={4}>
      <Segmented
        size="small"
        value={activePrototype}
        onChange={(v) => setPrototype(v as Prototype)}
        options={PROTOTYPES.map((p) => ({
          value: p.value,
          label: (
            <Tooltip title={p.description}>
              <Space size={4}>
                {p.icon}
                <span>{p.label}</span>
              </Space>
            </Tooltip>
          ),
        }))}
      />
      <Tag color={current.color} style={{ margin: 0, fontSize: 10 }}>
        {activePrototype === "P1" ? "82F" : activePrototype === "P2" ? "103F" : "108F"}
      </Tag>
    </Space>
  );
}
