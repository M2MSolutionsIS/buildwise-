/**
 * F137: ThemeProvider — Dark theme from BuildWise wireframes.
 * Uses Ant Design darkAlgorithm with custom tokens matching the design system.
 */
import { useMemo } from "react";
import { ConfigProvider, theme } from "antd";
import roLocale from "antd/locale/ro_RO";
import enLocale from "antd/locale/en_US";
import { useBrandingStore } from "../stores/brandingStore";
import { useLanguage } from "../i18n";

const LOCALE_MAP = {
  ro: roLocale,
  en: enLocale,
} as const;

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { primaryColor, fontFamily, borderRadius } = useBrandingStore();
  const { locale } = useLanguage();

  const antdLocale = LOCALE_MAP[locale] ?? roLocale;

  const themeConfig = useMemo(
    () => ({
      token: {
        // Colors
        colorPrimary: primaryColor || "#2563EB",
        colorBgContainer: "#1A1A2E",
        colorBgElevated: "#1A1A33",
        colorBgLayout: "#0B0F19",
        colorBgSpotlight: "#0F172A",
        colorBorder: "rgba(255,255,255,0.08)",
        colorBorderSecondary: "rgba(255,255,255,0.06)",
        colorText: "#F1F5F9",
        colorTextSecondary: "#94A3B8",
        colorTextTertiary: "#64748B",
        colorTextQuaternary: "#475569",
        colorFill: "rgba(255,255,255,0.06)",
        colorFillSecondary: "rgba(255,255,255,0.04)",
        colorFillTertiary: "rgba(255,255,255,0.03)",
        // Typography
        fontFamily,
        fontSize: 13,
        // Shape
        borderRadius,
        // Sizing
        controlHeight: 32,
      },
      algorithm: theme.darkAlgorithm,
      components: {
        Layout: {
          siderBg: "#0F172A",
          headerBg: "#0F172A",
          bodyBg: "#0B0F19",
          triggerBg: "#0F172A",
        },
        Menu: {
          darkItemBg: "transparent",
          darkSubMenuItemBg: "transparent",
          darkItemColor: "#94A3B8",
          darkItemHoverColor: "#F1F5F9",
          darkItemHoverBg: "rgba(255,255,255,0.05)",
          darkItemSelectedBg: "rgba(37,99,235,0.15)",
          darkItemSelectedColor: "#F1F5F9",
          itemHeight: 36,
          itemBorderRadius: 6,
          iconSize: 16,
          fontSize: 13,
        },
        Card: {
          colorBgContainer: "#1A1A2E",
          colorBorderSecondary: "rgba(255,255,255,0.08)",
        },
        Table: {
          headerBg: "#0F172A",
          headerColor: "#64748B",
          colorBgContainer: "transparent",
          rowHoverBg: "rgba(255,255,255,0.03)",
          rowSelectedBg: "rgba(37,99,235,0.08)",
          rowSelectedHoverBg: "rgba(37,99,235,0.12)",
          borderColor: "rgba(255,255,255,0.04)",
        },
        Input: {
          colorBgContainer: "#0F172A",
          colorBorder: "rgba(255,255,255,0.1)",
          activeBorderColor: "#2563EB",
          fontSize: 13,
          controlHeight: 32,
        },
        Select: {
          colorBgContainer: "#0F172A",
          colorBorder: "rgba(255,255,255,0.1)",
          controlHeight: 32,
        },
        Button: {
          primaryColor: "#fff",
          borderRadius: 6,
          controlHeight: 32,
          fontSize: 13,
          defaultBorderColor: "rgba(255,255,255,0.12)",
          defaultColor: "#F1F5F9",
          defaultBg: "transparent",
        },
        Modal: {
          contentBg: "#1A1A33",
          headerBg: "#1A1A33",
        },
        Dropdown: {
          colorBgElevated: "#1A1A33",
        },
        Drawer: {
          colorBgElevated: "#1A1A33",
        },
        Breadcrumb: {
          fontSize: 13,
          itemColor: "#64748B",
          linkColor: "#64748B",
          linkHoverColor: "#94A3B8",
          separatorColor: "#475569",
        },
        Statistic: {
          titleFontSize: 12,
          contentFontSize: 24,
        },
        Tooltip: {
          colorBgSpotlight: "#1A1A33",
          colorTextLightSolid: "#F1F5F9",
        },
        Segmented: {
          trackBg: "#0F172A",
          itemSelectedBg: "#1A1A2E",
        },
      },
    }),
    [primaryColor, borderRadius, fontFamily]
  );

  return (
    <ConfigProvider locale={antdLocale} theme={themeConfig}>
      {children}
    </ConfigProvider>
  );
}
