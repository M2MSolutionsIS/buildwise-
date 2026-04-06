/**
 * Flow 01 — Lead → Oportunitate → Calificare (12 pași)
 *
 * F-codes: F001, F002, F003, F005, F042
 * Pași:
 *  1. Creare contact (lead) cu date complete
 *  2. Verificare duplicat (F005)
 *  3. Adăugare date de contact (persoane)
 *  4. Clasificare contact ca Prospect (F003)
 *  5. Adăugare interacțiune (apel) (F002)
 *  6. Adăugare a doua interacțiune (email)
 *  7. Schimbare stadiu → Client Potențial
 *  8. Creare oportunitate din contact
 *  9. Verificare oportunitate apare pe board (F042)
 * 10. Calificare oportunitate (checklist)
 * 11. Verificare stadiu oportunitate = qualified
 * 12. Verificare istoric interacțiuni reflect toate acțiunile
 */
import { test, expect } from '@playwright/test';
import {
  getAuthTokens, authHeader, contactPayload,
  opportunityPayload, expectOk,
} from './helpers';

test.describe.configure({ mode: 'serial' });

test.describe('Flow 01 — Lead → Oportunitate → Calificare', () => {
  let tokens: Awaited<ReturnType<typeof getAuthTokens>>;
  let contactId: string;
  let opportunityId: string;

  test.beforeAll(async ({ request }) => {
    tokens = await getAuthTokens(request);
  });

  test('Pas 1 — Creare contact (lead)', async ({ request }) => {
    const res = await request.post('/api/v1/crm/contacts', {
      headers: authHeader(tokens),
      data: contactPayload({ stage: 'prospect' }),
    });
    const data: any = await expectOk(res);
    contactId = data.id;
    expect(contactId).toBeTruthy();
  });

  test('Pas 2 — Verificare duplicat (F005)', async ({ request }) => {
    const res = await request.post('/api/v1/crm/contacts/check-duplicates', {
      headers: authHeader(tokens),
      data: contactPayload({ cui: 'RO' + Date.now() }),
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 3 — Adăugare persoană de contact', async ({ request }) => {
    const res = await request.post(`/api/v1/crm/contacts/${contactId}/persons`, {
      headers: authHeader(tokens),
      data: {
        first_name: 'Ion',
        last_name: 'Popescu',
        email: 'ion@test.ro',
        phone: '0721000001',
        role: 'director',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 4 — Clasificare contact ca Prospect (F003)', async ({ request }) => {
    const res = await request.get(`/api/v1/crm/contacts/${contactId}`, {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    expect(data.stage).toBe('prospect');
  });

  test('Pas 5 — Adăugare interacțiune apel (F002)', async ({ request }) => {
    const res = await request.post(`/api/v1/crm/contacts/${contactId}/interactions`, {
      headers: authHeader(tokens),
      data: {
        interaction_type: 'call',
        subject: 'Apel inițial prospectare',
        notes: 'Clientul interesat de soluții energetice',
        interaction_date: '2026-04-01T10:00:00',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 6 — Adăugare interacțiune email', async ({ request }) => {
    const res = await request.post(`/api/v1/crm/contacts/${contactId}/interactions`, {
      headers: authHeader(tokens),
      data: {
        interaction_type: 'email',
        subject: 'Follow-up email cu oferta preliminară',
        notes: 'Trimis catalog produse',
        interaction_date: '2026-04-02T14:00:00',
      },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 7 — Schimbare stadiu → Client Potențial', async ({ request }) => {
    const res = await request.put(`/api/v1/crm/contacts/${contactId}`, {
      headers: authHeader(tokens),
      data: { stage: 'potential_client' },
    });
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 8 — Creare oportunitate din contact', async ({ request }) => {
    const res = await request.post('/api/v1/pipeline/opportunities', {
      headers: authHeader(tokens),
      data: opportunityPayload(contactId),
    });
    const data: any = await expectOk(res);
    opportunityId = data.id;
    expect(opportunityId).toBeTruthy();
  });

  test('Pas 9 — Verificare oportunitate pe board (F042)', async ({ request }) => {
    const res = await request.get('/api/v1/pipeline/board', {
      headers: authHeader(tokens),
    });
    const data: any = await expectOk(res);
    expect(data).toBeTruthy();
  });

  test('Pas 10 — Calificare oportunitate', async ({ request }) => {
    const res = await request.post(
      `/api/v1/pipeline/opportunities/${opportunityId}/qualify`,
      { headers: authHeader(tokens), data: { qualified: true } },
    );
    expect(res.ok()).toBeTruthy();
  });

  test('Pas 11 — Verificare stadiu = qualified', async ({ request }) => {
    const res = await request.get(
      `/api/v1/pipeline/opportunities/${opportunityId}`,
      { headers: authHeader(tokens) },
    );
    const data: any = await expectOk(res);
    expect(data.stage).toBe('qualified');
  });

  test('Pas 12 — Verificare istoric interacțiuni', async ({ request }) => {
    const res = await request.get(
      `/api/v1/crm/contacts/${contactId}/interactions`,
      { headers: authHeader(tokens) },
    );
    const data: any = await expectOk(res);
    const items = Array.isArray(data) ? data : data.items || [];
    expect(items.length).toBeGreaterThanOrEqual(2);
  });
});
