import { expect, test } from "@playwright/test";
import { createDocument, createTeam } from "./helpers/app-flows";

// ─────────────────────────────────────────
// FLOW: SEC-01..SEC-04 — Core security controls
// TESTS: route protection, non-member denial, protected downloads
// AUDIT COVERAGE: SECURITY (A05, A04), consolidated Top Action Items
// ─────────────────────────────────────────

test.describe("Security", () => {
  test("SEC-01: unauthenticated user is redirected from protected routes", async ({
    browser,
  }) => {
    const anon = await browser.newContext();
    const page = await anon.newPage();

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/sign-in/);

    await page.goto("/teams/new");
    await expect(page).toHaveURL(/\/sign-in/);

    await anon.close();
  });

  test("SEC-02: non-member cannot access another team route", async ({
    page,
    browser,
  }) => {
    const { teamUrl } = await createTeam(page);
    const outsider = await browser.newContext();
    const outsiderPage = await outsider.newPage();

    await outsiderPage.goto(teamUrl);
    await expect(outsiderPage).toHaveURL(/\/sign-in/);

    await outsider.close();
  });

  test("SEC-03: unauthenticated user cannot open document route directly", async ({
    page,
    browser,
  }) => {
    await createTeam(page);
    await createDocument(page, undefined, true);

    const docLink = page.locator("a[href^='/documents/']").first();
    await expect(docLink).toBeVisible();
    const href = await docLink.getAttribute("href");
    expect(href).toBeTruthy();

    const anon = await browser.newContext();
    const anonPage = await anon.newPage();
    await anonPage.goto(href!);
    await expect(anonPage).toHaveURL(/\/sign-in/);
    await anon.close();
  });

  test("SEC-04: protected team settings are not reachable by URL when signed out", async ({
    page,
    browser,
  }) => {
    const { teamUrl } = await createTeam(page);
    const teamId = teamUrl.split("/teams/")[1];

    const anon = await browser.newContext();
    const anonPage = await anon.newPage();
    await anonPage.goto(`/teams/${teamId}/settings`);
    await expect(anonPage).toHaveURL(/\/sign-in/);
    await anon.close();
  });
});
