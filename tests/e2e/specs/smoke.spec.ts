import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('home page loads', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'SiteWatcher' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign In' })).toBeVisible();
  });

  test('API health check', async ({ request }) => {
    const response = await request.get('http://localhost:8000/healthz');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
  });

  test('dashboard page is accessible', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
});

