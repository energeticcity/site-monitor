import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display sign in page', async ({ page }) => {
    await page.goto('/auth/signin');

    await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send Magic Link' })).toBeVisible();
  });

  test('should request magic link', async ({ page }) => {
    await page.goto('/auth/signin');

    await page.getByPlaceholder('you@example.com').fill('test@example.com');
    await page.getByRole('button', { name: 'Send Magic Link' }).click();

    await expect(page.getByText('Check your console!')).toBeVisible();
  });
});

