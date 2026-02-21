import { clerk } from "@clerk/testing/playwright";
import { expect, Page } from "@playwright/test";

function requiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required env var: ${name}`);
  }
  return value;
}

export async function signIn(
  page: Page,
  creds?: { email: string; password: string }
) {
  const email = creds?.email ?? requiredEnv("TEST_USER_EMAIL");
  void creds?.password;

  // Clerk testing helper creates authenticated sessions via secret key,
  // bypassing interactive verification prompts (email code/MFA UI).
  await page.goto("/");
  await clerk.signIn({
    page,
    emailAddress: email,
  });
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/dashboard/);
}

export async function signOut(page: Page) {
  await page.goto("/");
  await clerk.signOut({ page });
}

export function hasSecondaryUserEnv() {
  return !!(
    process.env.TEST_VIEWER_EMAIL &&
    process.env.TEST_VIEWER_PASSWORD &&
    process.env.TEST_EDITOR_EMAIL &&
    process.env.TEST_EDITOR_PASSWORD
  );
}
