/**
 * F137 + F138: Branding store — tenant-level visual customization (P3)
 * Stores logo, colors, fonts, app name for white-label.
 * Persisted in localStorage and synced with backend Organization.
 */
import { create } from "zustand";

export interface BrandingConfig {
  /** Custom app name replacing "BuildWise" (F137 white-label) */
  appName: string;
  /** Logo URL (uploaded or external) */
  logoUrl: string;
  /** Primary brand color */
  primaryColor: string;
  /** Secondary brand color */
  secondaryColor: string;
  /** Font family for the platform */
  fontFamily: string;
  /** Border radius for components */
  borderRadius: number;
  /** Whether white-label mode is active (hide BuildWise branding) */
  whiteLabelEnabled: boolean;
}

interface BrandingState extends BrandingConfig {
  /** Apply branding from Organization data (after login/fetch) */
  applyBranding: (config: Partial<BrandingConfig>) => void;
  /** Reset to defaults */
  resetBranding: () => void;
}

const DEFAULTS: BrandingConfig = {
  appName: "BuildWise",
  logoUrl: "",
  primaryColor: "#1677ff",
  secondaryColor: "#52c41a",
  fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
  borderRadius: 6,
  whiteLabelEnabled: false,
};

function loadFromStorage(): Partial<BrandingConfig> {
  try {
    const raw = localStorage.getItem("buildwise_branding");
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveToStorage(config: BrandingConfig) {
  localStorage.setItem("buildwise_branding", JSON.stringify(config));
}

export const useBrandingStore = create<BrandingState>((set) => {
  const stored = loadFromStorage();
  const initial = { ...DEFAULTS, ...stored };

  return {
    ...initial,

    applyBranding: (config) =>
      set((state) => {
        const updated = { ...state, ...config };
        saveToStorage({
          appName: updated.appName,
          logoUrl: updated.logoUrl,
          primaryColor: updated.primaryColor,
          secondaryColor: updated.secondaryColor,
          fontFamily: updated.fontFamily,
          borderRadius: updated.borderRadius,
          whiteLabelEnabled: updated.whiteLabelEnabled,
        });
        return updated;
      }),

    resetBranding: () =>
      set(() => {
        saveToStorage(DEFAULTS);
        return { ...DEFAULTS };
      }),
  };
});
