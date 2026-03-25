/**
 * F137: ThemeProvider — Dynamic Ant Design theme from tenant branding.
 * Wraps ConfigProvider to apply custom colors, fonts, border radius per tenant.
 * Supports white-label: fully branded platform for each organization.
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
  const { primaryColor, secondaryColor, fontFamily, borderRadius } = useBrandingStore();
  const { locale } = useLanguage();

  const antdLocale = LOCALE_MAP[locale] ?? roLocale;

  const themeConfig = useMemo(
    () => ({
      token: {
        colorPrimary: primaryColor,
        colorSuccess: secondaryColor,
        borderRadius,
        fontFamily,
      },
      algorithm: theme.defaultAlgorithm,
    }),
    [primaryColor, secondaryColor, borderRadius, fontFamily]
  );

  return (
    <ConfigProvider locale={antdLocale} theme={themeConfig}>
      {children}
    </ConfigProvider>
  );
}
