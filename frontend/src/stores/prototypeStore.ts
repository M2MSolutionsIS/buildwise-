/**
 * Prototype Store — manages active prototype (P1/P2/P3) and feature visibility.
 *
 * P1 — BuildWise TRL5: Energy + AI (82 common features)
 * P2 — BAHM Operational: Construction + RM (82 common + 21 P2+P3)
 * P3 — M2M ERP Lite: SaaS multi-tenant (82 common + 21 P2+P3 + 5 P3-only)
 *
 * Source of truth: server (Organization.active_prototype + allowed_prototypes).
 * localStorage is used only as a cache until the server responds.
 */
import { create } from "zustand";
import type { Prototype } from "../types";

/** Modules that require P2+P3 */
const P2_P3_MODULES = ["rm"];

/** Sidebar keys requiring P2+P3 */
const P2_P3_ROUTES = [
  "/rm",
  "/rm/dashboard",
  "/rm/employees",
  "/rm/equipment",
  "/rm/materials",
  "/rm/capacity",
  "/rm/financial",
  "/settings/rm",
];

/** Sidebar keys requiring P3 only */
const P3_ONLY_ROUTES = [
  "/settings/branding",
  "/bi/reports",
  "/bi/forecast",
  "/setup",
];

interface PrototypeState {
  activePrototype: Prototype;
  allowedPrototypes: Prototype[];
  /** True once the server has been queried and the store is initialized */
  initialized: boolean;
  /** Sync from server organization data */
  syncFromOrganization: (active: Prototype, allowed: Prototype[]) => void;
  /** Set prototype (validates against allowedPrototypes) */
  setPrototype: (p: Prototype) => boolean;
  /** Check if a module key is visible for current prototype */
  isModuleVisible: (moduleKey: string) => boolean;
  /** Check if a route is visible for current prototype */
  isRouteVisible: (route: string) => boolean;
  /** Is P2 or P3 */
  isP2Plus: () => boolean;
  /** Is P3 */
  isP3: () => boolean;
}

export const usePrototypeStore = create<PrototypeState>((set, get) => ({
  activePrototype: (localStorage.getItem("buildwise_prototype") as Prototype) || "P1",
  allowedPrototypes: ["P1", "P2", "P3"],
  initialized: false,

  syncFromOrganization: (active, allowed) => {
    localStorage.setItem("buildwise_prototype", active);
    set({ activePrototype: active, allowedPrototypes: allowed, initialized: true });
  },

  setPrototype: (p) => {
    const { allowedPrototypes } = get();
    if (!allowedPrototypes.includes(p)) return false;
    localStorage.setItem("buildwise_prototype", p);
    set({ activePrototype: p });
    return true;
  },

  isModuleVisible: (moduleKey) => {
    const proto = get().activePrototype;
    if (P2_P3_MODULES.includes(moduleKey)) {
      return proto === "P2" || proto === "P3";
    }
    return true;
  },

  isRouteVisible: (route) => {
    const proto = get().activePrototype;
    if (P3_ONLY_ROUTES.some((r) => route.startsWith(r))) {
      return proto === "P3";
    }
    if (P2_P3_ROUTES.some((r) => route.startsWith(r))) {
      return proto === "P2" || proto === "P3";
    }
    return true;
  },

  isP2Plus: () => {
    const proto = get().activePrototype;
    return proto === "P2" || proto === "P3";
  },

  isP3: () => get().activePrototype === "P3",
}));
