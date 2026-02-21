import { expect, test } from "@playwright/test";
import { createDocument, createTeam, uniqueName } from "./helpers/app-flows";

// ─────────────────────────────────────────
// FLOW: ERR-01..04 — Error and recovery handling
// TESTS: not-found routes, cancel flows, destructive confirmations
// AUDIT COVERAGE: principal + security error handling concerns
// ─────────────────────────────────────────

test.describe("Error Handling", () => {
  test("ERR-01: invalid document route does not render document details", async ({
    page,
  }) => {
    await page.goto("/documents/j7f7f7f7f7f7f7f7f7f7f7f7");
    await expect(page.getByText("Document Details")).toHaveCount(0);
  });

  test("ERR-02: cancelling new-document dialog resets form fields", async ({
    page,
  }) => {
    await createTeam(page);
    await page.getByTestId("new-doc-open").click();
    await page.getByTestId("new-doc-name").fill(uniqueName("reset-doc"));
    await page.getByRole("button", { name: "Cancel" }).click();
    await page.getByTestId("new-doc-open").click();
    await expect(page.getByTestId("new-doc-name")).toHaveValue("");
  });

  test("ERR-03: cancelling document delete keeps document visible", async ({
    page,
  }) => {
    await createTeam(page);
    const docName = await createDocument(page);

    page.once("dialog", (dialog) => dialog.dismiss());
    await page.locator("[data-testid^='doc-actions-']").first().click();
    await page.locator("[data-testid^='doc-delete-']").first().click();
    await expect(page.getByText(docName).first()).toBeVisible();
  });

  test("ERR-04: cancelling team delete keeps user on settings page", async ({
    page,
  }) => {
    const { teamName } = await createTeam(page);
    await page.goto(`${page.url()}/settings`);
    page.once("dialog", (dialog) => dialog.dismiss());
    await page.getByRole("button", { name: "Delete Team" }).click();
    await expect(page.getByRole("heading", { name: "Team Settings" })).toBeVisible();
    await expect(page.getByText(teamName)).toBeVisible();
  });
});
