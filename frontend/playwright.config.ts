import { defineConfig } from '@playwright/test';

/**
 * Playwright config for BuildWise E2E API flow tests.
 *
 * Uses Playwright's API request context to test all 17 business flows
 * end-to-end against the FastAPI backend (no browser required).
 */
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  retries: 0,
  reporter: [
    ['list'],
    ['json', { outputFile: 'tests/e2e/results.json' }],
  ],
  use: {
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
    extraHTTPHeaders: {
      'Content-Type': 'application/json',
    },
  },
  projects: [
    {
      name: 'common-flows',
      testMatch: /flow-(0[1-9])\.spec\.ts/,
    },
    {
      name: 'p2-flows',
      testMatch: /flow-(1[0-7])\.spec\.ts/,
    },
  ],
});
