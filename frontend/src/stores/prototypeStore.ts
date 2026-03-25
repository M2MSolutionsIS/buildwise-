/**
 * Prototype Store — manages active prototype (P1/P2/P3) and feature visibility.
 *
 * P1 — BuildWise TRL5: Energy + AI (82 common features)
 * P2 — BAHM Operational: Construction + RM (82 common + 21 P2+P3)
 * P3 — M2M ERP Lite: SaaS multi-tenant (82 common + 21 P2+P3 + 5 P3-only)
 *
 * Feature visibility:
 * - 82 common: always visible
 * - 21 P2+P3: visible when prototype is P2 or P3
 * - 5 P3 only: visible only when prototype is P3
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
  setPrototype: (p: Prototype) => void;
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
  activePrototype: (localStorage.getItem("buildwise_prototype") as Prototype) || "P3",

  setPrototype: (p) => {
    localStorage.setItem("buildwise_prototype", p);
    set({ activePrototype: p });
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
