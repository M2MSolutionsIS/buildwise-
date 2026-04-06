/**
 * Flow 10 — Configurare Resurse RM (10 pași) — P2
 *
 * F-codes: F107, F108, F109, F110, F111
 * Pași:
 *  1. Creare angajat (F107)
 *  2. Adăugare detalii angajat (departament, funcție)
 *  3. Verificare angajat creat
 *  4. Planificare angajare (F108)
 *  5. Creare concediu (F109)
 *  6. Verificare disponibilitate
 *  7. Filtrare angajați per departament
 *  8. Căutare angajați per skill (F110)
 *  9. Update salarizare (F111)
 * 10. Verificare listă angajați completă
 */
import { test, expect } from '@playwright/test';
import { getAuthTokens, authHeader, expectOk } from './helpers';

test.describe.configure({ mode: 'serial' });

test.describe('Flow 10 — Configurare Resurse RM', () => {
  let tokens: Awaited<ReturnType<typeof getAuthTokens>>;
  let employeeId: string;

  test.beforeAll(async ({ request }) => {
    tokens = await getAuthTokens(request);
  });

  test('Pas 1 — Creare angajat (F107)', async ({ request }) => {
    const res = await request.post('/api/v1/rm/employees', {
      headers: authHeader(tokens),
      data: {
        first_name: 'Andrei',
        last_name: 'Ionescu',
        email: `andrei-${Date.now()}@test.ro`,
        department: 'Execuție',
        position: 'Inginer Montaj',
        employment_type: 'full_time',
        hourly_rate: 75,
      },
    });
    const data: any = await expectOk(res);
    employeeId = data.id;
    expect(employeeId).toBeTruthy();
  });

  test('Pas 2-3 — Verificare angajat', async ({ request }) => {
    const res = await request.get(`/api/v1/rm/employees/${employeeId}`, {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    expect(data.first_name).toBe('Andrei');
    expect(data.department).toBe('Execuție');
  });

  test('Pas 4 — Planificare angajare (F108)', async ({ request }) => {
    const res = await request.post('/api/v1/rm/hr-planning', {
      headers: authHeader(tokens),
      data: {
        entry_type: 'hire',
        position: 'Electrician',
        target_date: '2026-06-01T00:00:00',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 5 — Creare concediu (F109)', async ({ request }) => {
    const res = await request.post('/api/v1/rm/leaves', {
      headers: authHeader(tokens),
      data: {
        employee_id: employeeId,
        leave_type: 'annual',
        start_date: '2026-07-01T00:00:00',
        end_date: '2026-07-14T00:00:00',
        status: 'approved',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 6 — Verificare disponibilitate', async ({ request }) => {
    const res = await request.get(
      `/api/v1/rm/employees/${employeeId}/availability?start_date=2026-07-01&end_date=2026-07-14`,
      { headers: authHeader(tokens) },
    );
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 7 — Filtrare per departament', async ({ request }) => {
    const res = await request.get(
      '/api/v1/rm/employees?department=Execuție',
      { headers: authHeader(tokens) },
    );
    const data: any = await expectOk(res);
    expect(data).toBeTruthy();
  });

  test('Pas 8 — Căutare per skill (F110)', async ({ request }) => {
    const res = await request.get(
      '/api/v1/rm/employees?search=Andrei',
      { headers: authHeader(tokens) },
    );
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 9 — Update salarizare (F111)', async ({ request }) => {
    const res = await request.put(`/api/v1/rm/employees/${employeeId}`, {
      headers: authHeader(tokens),
      data: { hourly_rate: 85, salary_gross: 8500 },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 10 — Listă angajați completă', async ({ request }) => {
    const res = await request.get('/api/v1/rm/employees', {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    const items = Array.isArray(data) ? data : data.items || [];
    expect(items.length).toBeGreaterThanOrEqual(1);
  });
});
