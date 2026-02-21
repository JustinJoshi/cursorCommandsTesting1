import { expect, test } from "@playwright/test";
import { createTeam } from "./helpers/app-flows";
import { hasSecondaryUserEnv, signIn } from "./helpers/auth";

// ─────────────────────────────────────────
// FLOW: SEC-ROLE-01..03 — Role enforcement
// TESTS: viewer restrictions, admin-only settings actions
// AUDIT COVERAGE: SECURITY + role authorization checks
// ─────────────────────────────────────────

test.describe("Security Roles", () => {
  test("SEC-ROLE-01: viewer cannot see create-document action", async ({
    page,
    browser,
  }) => {
    test.skip(!hasSecondaryUserEnv(), "Requires editor/viewer test users");

    const { teamUrl } = await createTeam(page);
    await page.goto(teamUrl.replace(/\/teams\/([^/]+)$/, "/teams/$1/settings"));
    await page.getByTestId("member-email-input").fill(process.env.TEST_VIEWER_EMAIL!);
    await page.getByRole("button", { name: "Add" }).click();
    await expect(page.getByText(/member added successfully|invite sent/i)).toBeVisible();

    const viewer = await browser.newContext();
    const viewerPage = await viewer.newPage();
    await signIn(viewerPage, {
      email: process.env.TEST_VIEWER_EMAIL!,
      password: process.env.TEST_VIEWER_PASSWORD!,
    });
    await viewerPage.goto(teamUrl);
    await expect(viewerPage.getByTestId("new-doc-open")).toHaveCount(0);
    await viewer.close();
  });

  test("SEC-ROLE-02: viewer cannot access team settings page", async ({
    page,
    browser,
  }) => {
    test.skip(!hasSecondaryUserEnv(), "Requires editor/viewer test users");

    const { teamUrl } = await createTeam(page);
    const settingsUrl = `${teamUrl}/settings`;
    await page.goto(settingsUrl);
    await page.getByTestId("member-email-input").fill(process.env.TEST_VIEWER_EMAIL!);
    await page.getByRole("button", { name: "Add" }).click();

    const viewer = await browser.newContext();
    const viewerPage = await viewer.newPage();
    await signIn(viewerPage, {
      email: process.env.TEST_VIEWER_EMAIL!,
      password: process.env.TEST_VIEWER_PASSWORD!,
    });
    await viewerPage.goto(settingsUrl);
    await expect(viewerPage.getByText("Access Denied")).toBeVisible();
    await viewer.close();
  });

  test("SEC-ROLE-03: admin can access team settings page", async ({ page }) => {
    const { teamUrl } = await createTeam(page);
    await page.goto(`${teamUrl}/settings`);
    await expect(page.getByRole("heading", { name: "Team Settings" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Members" })).toBeVisible();
  });
});
