/**
 * Flow 14 — Planificare Financiară RM (8 pași) — P2
 *
 * F-codes: F115, F116
 * Pași:
 *  1. Creare buget per centru cost (F115)
 *  2. Verificare buget creat
 *  3. Update buget — ajustare previziuni
 *  4. Creare al doilea buget (alt centru cost)
 *  5. Analiză costuri reale vs bugetate (F116)
 *  6. Verificare dashboard costuri
 *  7. Verificare totale agregate
 *  8. Verificare alertă depășire
 */
import { test, expect } from '@playwright/test';
import { getAuthTokens, authHeader, expectOk } from './helpers';

test.describe.configure({ mode: 'serial' });

test.describe('Flow 14 — Planificare Financiară RM', () => {
  let tokens: Awaited<ReturnType<typeof getAuthTokens>>;
  let budgetId: string;

  test.beforeAll(async ({ request }) => {
    tokens = await getAuthTokens(request);
  });

  test('Pas 1 — Creare buget (F115)', async ({ request }) => {
    const res = await request.post('/api/v1/rm/budgets', {
      headers: authHeader(tokens),
      data: {
        cost_center: 'Execuție',
        category: 'Salarii',
        period_month: 4,
        period_year: 2026,
        planned_amount: 150000,
        actual_amount: 0,
      },
    });
    const data: any = await expectOk(res);
    budgetId = data.id;
    expect(budgetId).toBeTruthy();
  });

  test('Pas 2 — Verificare buget', async ({ request }) => {
    const res = await request.get('/api/v1/rm/budgets', {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    expect(data).toBeTruthy();
  });

  test('Pas 3 — Update buget', async ({ request }) => {
    const res = await request.put(`/api/v1/rm/budgets/${budgetId}`, {
      headers: authHeader(tokens),
      data: { planned_amount: 175000 },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 4 — Creare buget alt centru cost', async ({ request }) => {
    const res = await request.post('/api/v1/rm/budgets', {
      headers: authHeader(tokens),
      data: {
        cost_center: 'Vânzări',
        category: 'Materiale',
        period_month: 5,
        period_year: 2026,
        planned_amount: 80000,
        actual_amount: 0,
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 5 — Analiză costuri (F116)', async ({ request }) => {
    const res = await request.get('/api/v1/rm/cost-analysis', {
      headers: authHeader(tokens),
    });
    expect(res.ok()).toBeTruthy();
    const data: any = await expectOk(res);
    expect(data).toBeTruthy();
  });

  test('Pas 6 — Dashboard costuri', async ({ request }) => {
    const res = await request.get('/api/v1/rm/cost-analysis', {
      headers: authHeader(tokens),
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 7 — Totale agregate', async ({ request }) => {
    const res = await request.get('/api/v1/rm/budgets', {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    const items = Array.isArray(data) ? data : data.items || [];
    expect(items.length).toBeGreaterThanOrEqual(2);
  });

  test('Pas 8 — Verificare utilization', async ({ request }) => {
    const res = await request.get('/api/v1/rm/utilization', {
      headers: authHeader(tokens),
    });
    expect(res.ok()).toBeTruthy();
  });
});
