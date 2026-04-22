/**
 * Shared helpers for BuildWise E2E flow tests.
 *
 * Provides auth, data factories, and assertion utilities
 * used across all 17 flow test files.
 */
import { APIRequestContext, expect } from '@playwright/test';

/* ------------------------------------------------------------------ */
/*  Auth helpers                                                       */
/* ------------------------------------------------------------------ */

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  user_id: string;
  org_id: string;
}

let _cachedTokens: AuthTokens | null = null;

/**
 * Register a fresh user + org OR login if already registered.
 * Returns JWT tokens and user/org IDs.
 */
export async function getAuthTokens(
  api: APIRequestContext,
  email = 'e2e-test@buildwise.ro',
  password = 'E2eTestPass123!',
): Promise<AuthTokens> {
  if (_cachedTokens) return _cachedTokens;

  // Try register first
  const regRes = await api.post('/api/v1/auth/register', {
    data: {
      email,
      password,
      first_name: 'E2E',
      last_name: 'Tester',
      company_name: 'E2E Test Corp',
      gdpr_consent: true,
    },
  });

  let tokens: AuthTokens;

  if (regRes.ok()) {
    // Register returns user in data but no tokens — must login
    const loginRes = await api.post('/api/v1/auth/login', {
      data: { email, password },
    });
    expect(loginRes.ok()).toBeTruthy();
    const loginData = await loginRes.json();
    tokens = {
      access_token: loginData.access_token,
      refresh_token: loginData.refresh_token,
      user_id: '',
      org_id: '',
    };
  } else {
    // Already exists — login
    const loginRes = await api.post('/api/v1/auth/login', {
      data: { email, password },
    });
    expect(loginRes.ok()).toBeTruthy();
    const loginData = await loginRes.json();
    tokens = {
      access_token: loginData.access_token,
      refresh_token: loginData.refresh_token,
      user_id: '',
      org_id: '',
    };
  }

  _cachedTokens = tokens;
  return tokens;
}

export function authHeader(tokens: AuthTokens) {
  return { Authorization: `Bearer ${tokens.access_token}` };
}

/** Reset cached tokens (call in afterAll if needed) */
export function resetTokenCache() {
  _cachedTokens = null;
}

/* ------------------------------------------------------------------ */
/*  Data factory helpers                                               */
/* ------------------------------------------------------------------ */

let _seq = Date.now();
function seq() {
  return ++_seq;
}

export function contactPayload(overrides: Record<string, unknown> = {}) {
  const s = seq();
  return {
    company_name: `E2E Company ${s}`,
    stage: 'prospect',
    contact_type: 'IMM',
    email: `e2e-${s}@test.ro`,
    phone: `072000${s}`,
    cui: `RO${s}`,
    ...overrides,
  };
}

export function opportunityPayload(
  contactId: string,
  overrides: Record<string, unknown> = {},
) {
  const s = seq();
  return {
    title: `E2E Opportunity ${s}`,
    contact_id: contactId,
    estimated_value: 50_000 + s,
    currency: 'RON',
    stage: 'new',
    source: 'direct',
    ...overrides,
  };
}

export function milestonePayload(
  opportunityId: string,
  overrides: Record<string, unknown> = {},
) {
  const s = seq();
  return {
    opportunity_id: opportunityId,
    title: `Milestone ${s}`,
    status: 'pending',
    estimated_days: 10,
    ...overrides,
  };
}

export function offerPayload(
  opportunityId: string,
  contactId: string,
  overrides: Record<string, unknown> = {},
) {
  const s = seq();
  return {
    opportunity_id: opportunityId,
    contact_id: contactId,
    title: `E2E Offer ${s}`,
    currency: 'RON',
    total_value: 45_000,
    items: [
      {
        product_name: 'Geam termoizolant',
        quantity: 100,
        unit_price: 450,
      },
    ],
    ...overrides,
  };
}

export function contractPayload(
  opportunityId: string,
  contactId: string,
  overrides: Record<string, unknown> = {},
) {
  const s = seq();
  return {
    opportunity_id: opportunityId,
    contact_id: contactId,
    title: `E2E Contract ${s}`,
    contract_type: 'standard',
    total_value: 45_000,
    currency: 'RON',
    ...overrides,
  };
}

export function projectPayload(overrides: Record<string, unknown> = {}) {
  const s = seq();
  return {
    project_number: `PRJ-E2E-${s}`,
    name: `E2E Project ${s}`,
    project_type: 'client',
    status: 'planning',
    budget: 100_000,
    currency: 'RON',
    ...overrides,
  };
}

/* ------------------------------------------------------------------ */
/*  Response assertion helpers                                         */
/* ------------------------------------------------------------------ */

/** Extract `data` from standard BuildWise API response wrapper */
export function extractData(body: Record<string, unknown>): unknown {
  return body.data ?? body;
}

/** Expect response OK and return parsed JSON data field */
export async function expectOk(res: { ok(): boolean; json(): Promise<Record<string, unknown>>; status(): number }) {
  if (!res.ok()) {
    const body = await res.json().catch(() => ({}));
    throw new Error(`Expected OK but got ${res.status()}: ${JSON.stringify(body)}`);
  }
  const json = await res.json();
  return extractData(json);
}
