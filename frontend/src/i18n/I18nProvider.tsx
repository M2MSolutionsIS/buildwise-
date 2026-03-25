/**
 * F138: I18n Context Provider — manages language state and translations.
 * Supports bilingual document generation (RO+EN for offers/contracts).
 */
import { createContext, useContext, useState, useCallback, useMemo } from "react";
import ro from "./locales/ro";
import en from "./locales/en";
import type { TranslationKeys } from "./locales/ro";

type SupportedLocale = "ro" | "en";

const LOCALES: Record<SupportedLocale, TranslationKeys> = { ro, en };

interface I18nContextValue {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => void;
  t: TranslationKeys;
  /** Get translations for a specific locale (used for bilingual docs) */
  getLocaleTranslations: (locale: SupportedLocale) => TranslationKeys;
  /** Whether bilingual documents are enabled */
  bilingualDocs: boolean;
  setBilingualDocs: (enabled: boolean) => void;
  /** Secondary language for bilingual docs */
  secondaryLocale: SupportedLocale;
  setSecondaryLocale: (locale: SupportedLocale) => void;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children, defaultLocale = "ro" }: { children: React.ReactNode; defaultLocale?: SupportedLocale }) {
  const [locale, setLocaleState] = useState<SupportedLocale>(() => {
    const stored = localStorage.getItem("buildwise_locale");
    return (stored === "en" ? "en" : stored === "ro" ? "ro" : defaultLocale) as SupportedLocale;
  });

  const [bilingualDocs, setBilingualDocsState] = useState(() => {
    return localStorage.getItem("buildwise_bilingual") === "true";
  });

  const [secondaryLocale, setSecondaryLocaleState] = useState<SupportedLocale>(() => {
    const stored = localStorage.getItem("buildwise_secondary_locale");
    return (stored === "ro" || stored === "en" ? stored : "en") as SupportedLocale;
  });

  const setLocale = useCallback((l: SupportedLocale) => {
    setLocaleState(l);
    localStorage.setItem("buildwise_locale", l);
  }, []);

  const setBilingualDocs = useCallback((enabled: boolean) => {
    setBilingualDocsState(enabled);
    localStorage.setItem("buildwise_bilingual", String(enabled));
  }, []);

  const setSecondaryLocale = useCallback((l: SupportedLocale) => {
    setSecondaryLocaleState(l);
    localStorage.setItem("buildwise_secondary_locale", l);
  }, []);

  const getLocaleTranslations = useCallback((l: SupportedLocale) => LOCALES[l], []);

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale,
      t: LOCALES[locale],
      getLocaleTranslations,
      bilingualDocs,
      setBilingualDocs,
      secondaryLocale,
      setSecondaryLocale,
    }),
    [locale, setLocale, getLocaleTranslations, bilingualDocs, setBilingualDocs, secondaryLocale, setSecondaryLocale]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useTranslation() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useTranslation must be used within I18nProvider");
  return ctx.t;
}

export function useLanguage() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useLanguage must be used within I18nProvider");
  return ctx;
}
