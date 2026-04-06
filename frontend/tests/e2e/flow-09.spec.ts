/**
 * Flow 09 — Onboarding și Setup Inițial (12 pași)
 *
 * F-codes: F040, F136, F139, F140, F141, F143, F157, F158
 * Pași:
 *  1. Register user + auto-create org
 *  2. Verificare organizație creată
 *  3. Creare roluri (F040)
 *  4. Verificare roluri default
 *  5. Creare valute (F139)
 *  6. Creare cursuri de schimb
 *  7. Configurare feature flags
 *  8. Configurare pipeline stages
 *  9. Verificare TrueCast status (F140)
 * 10. Verificare sync status (F143)
 * 11. Creare template notificări (F141)
 * 12. Verificare setup complet
 */
import { test, expect } from '@playwright/test';
import { expectOk } from './helpers';

test.describe.configure({ mode: 'serial' });

test.describe('Flow 09 — Onboarding și Setup Inițial', () => {
  let accessToken: string;
  const email = `onboard-${Date.now()}@buildwise.ro`;
  const password = 'Onboard123!';

  test('Pas 1 — Register user + login', async ({ request }) => {
    const regRes = await request.post('/api/v1/auth/register', {
      data: {
        email,
        password,
        first_name: 'Setup',
        last_name: 'Admin',
        company_name: 'Onboarding Corp',
        gdpr_consent: true,
      },
    });
    expect(regRes.ok()).toBeTruthy();

    // Login to get tokens
    const loginRes = await request.post('/api/v1/auth/login', {
      data: { email, password },
    });
    const loginData: any = await loginRes.json();
    accessToken = loginData.access_token;
    expect(accessToken).toBeTruthy();
  });

  test('Pas 2 — Verificare org creată', async ({ request }) => {
    const res = await request.get('/api/v1/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const data: any = await expectOk(res);
    expect(data.organization_id || data.org_id).toBeTruthy();
  });

  test('Pas 3 — Creare rol custom (F040)', async ({ request }) => {
    const res = await request.post('/api/v1/system/roles', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { name: 'Manager Vânzări', code: 'sales_mgr', permissions: ['crm:read', 'pipeline:write'] },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 4 — Verificare roluri', async ({ request }) => {
    const res = await request.get('/api/v1/system/roles', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const data: any = await expectOk(res);
    const items = Array.isArray(data) ? data : data.items || [];
    expect(items.length).toBeGreaterThanOrEqual(1);
  });

  test('Pas 5 — Creare valută (F139)', async ({ request }) => {
    const res = await request.post('/api/v1/system/currencies', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { code: 'EUR', name: 'Euro', symbol: '€', is_default: false },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 6 — Creare curs de schimb', async ({ request }) => {
    const res = await request.post('/api/v1/system/exchange-rates', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { from_currency: 'EUR', to_currency: 'RON', rate: 4.97, effective_date: '2026-04-01T00:00:00' },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 7 — Configurare feature flags', async ({ request }) => {
    const res = await request.get('/api/v1/system/feature-flags', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 8 — Pipeline stages config', async ({ request }) => {
    const res = await request.post('/api/v1/system/pipeline-stages', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { name: 'Evaluare Tehnică', code: 'evaluare_tehnica', sort_order: 2, probability: 30 },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 9 — TrueCast status (F140)', async ({ request }) => {
    const res = await request.get('/api/v1/system/truecast', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 10 — Sync status (F143)', async ({ request }) => {
    const res = await request.get('/api/v1/system/sync-status', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 11 — Template notificări (F141)', async ({ request }) => {
    const res = await request.post('/api/v1/system/notification-templates', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: {
        name: 'Welcome Email',
        event_type: 'user_registered',
        subject: 'Bine ați venit!',
        body: 'Cont creat cu succes.',
        channel: 'email',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 12 — Verificare setup complet', async ({ request }) => {
    const res = await request.get('/api/health', {});
    expect(res.ok()).toBeTruthy();
    const data: any = await res.json();
    expect(data.status).toBe('ok');
  });
});
