import { expect, test } from "@playwright/test";
import { createDocument, createTeam } from "./helpers/app-flows";

// ─────────────────────────────────────────
// FLOW: A11Y-01..05 — Accessibility regression checks
// TESTS: skip link, icon button names, dialog labels
// AUDIT COVERAGE: a11y.md Fix 1/2/3
// ─────────────────────────────────────────

test.describe("Accessibility", () => {
  test("A11Y-01: skip-to-content link is keyboard reachable", async ({ page }) => {
    await page.goto("/dashboard");
    await page.keyboard.press("Tab");
    const skipLink = page.getByRole("link", { name: /skip to main content/i });
    await expect(skipLink).toBeVisible();
    await expect(skipLink).toHaveAttribute("href", "#main-content");
  });

  test("A11Y-02: document actions trigger has accessible name", async ({ page }) => {
    await createTeam(page);
    await createDocument(page);
    const actionsTrigger = page.locator("[data-testid^='doc-actions-']").first();
    await expect(actionsTrigger).toHaveAttribute("aria-label", /Actions for/i);
  });

  test("A11Y-03: rename dialog input has proper label and description", async ({
    page,
  }) => {
    await createTeam(page);
    await createDocument(page);
    await page.locator("[data-testid^='doc-actions-']").first().click();
    await page.locator("[data-testid^='doc-rename-']").first().click();
    const input = page.getByTestId("rename-doc-input");
    await expect(input).toBeVisible();
    await expect(page.getByText("New name")).toBeVisible();
    await expect(input).toHaveAttribute("aria-describedby", "rename-doc-hint");
  });

  test("A11Y-04: upload dialog icon-only button is named", async ({ page }) => {
    await createTeam(page);
    await page.getByTestId("new-doc-open").click();
    await page.getByTestId("new-doc-name").fill("a11y-upload");
    await page.getByTestId("new-doc-file-input").setInputFiles({
      name: "a11y.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("a11y"),
    });
    await expect(page.getByTestId("new-doc-remove-file")).toHaveAttribute(
      "aria-label",
      "Remove selected file"
    );
  });

  test("A11Y-05: member/invite icon-only controls are named", async ({ page }) => {
    const { teamUrl } = await createTeam(page);
    await page.goto(`${teamUrl}/settings`);
    await page.getByTestId("member-email-input").fill(`invite-${Date.now()}@example.com`);
    await page.getByRole("button", { name: "Add" }).click();
    const cancelInvite = page.locator("[data-testid^='cancel-invite-']").first();
    await expect(cancelInvite).toHaveAttribute("aria-label", /Cancel invite for/i);
  });
});
