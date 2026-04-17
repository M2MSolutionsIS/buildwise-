/**
 * Prototype Switcher — allows switching between allowed prototypes.
 * If the organization has only one allowed prototype, shows a read-only Tag.
 * Otherwise shows a Segmented control filtered to the allowed prototypes.
 */
import { Segmented, Tooltip, Tag, Space } from "antd";
import {
  ThunderboltOutlined,
  ToolOutlined,
  CloudOutlined,
} from "@ant-design/icons";
import { usePrototypeStore } from "../stores/prototypeStore";
import { systemService } from "../modules/system/services/systemService";
import type { Prototype } from "../types";

const PROTOTYPES: { value: Prototype; label: string; icon: React.ReactNode; description: string; color: string; featureCount: string }[] = [
  {
    value: "P1",
    label: "P1",
    icon: <ThunderboltOutlined />,
    description: "BuildWise TRL5 — Energy + AI",
    color: "#52c41a",
    featureCount: "82F",
  },
  {
    value: "P2",
    label: "P2",
    icon: <ToolOutlined />,
    description: "BAHM Operational — Construcții + RM",
    color: "#1677ff",
    featureCount: "103F",
  },
  {
    value: "P3",
    label: "P3",
    icon: <CloudOutlined />,
    description: "M2M ERP Lite — SaaS Multi-tenant",
    color: "#722ed1",
    featureCount: "108F",
  },
];

export default function PrototypeSwitcher() {
  const { activePrototype, allowedPrototypes, setPrototype } = usePrototypeStore();

  const current = PROTOTYPES.find((p) => p.value === activePrototype)!;
  const visibleOptions = PROTOTYPES.filter((p) => allowedPrototypes.includes(p.value));

  const handleChange = async (value: string | number) => {
    const proto = value as Prototype;
    const accepted = setPrototype(proto);
    if (accepted) {
      try { await systemService.setPrototype(proto); } catch { /* best effort */ }
    }
  };

  if (visibleOptions.length <= 1) {
    return (
      <Tag color={current.color} style={{ margin: 0 }}>
        <Space size={4}>
          {current.icon}
          <span>Plan: {current.label}</span>
        </Space>
      </Tag>
    );
  }

  return (
    <Space size={4}>
      <Segmented
        size="small"
        value={activePrototype}
        onChange={handleChange}
        options={visibleOptions.map((p) => ({
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
        {current.featureCount}
      </Tag>
    </Space>
  );
}
