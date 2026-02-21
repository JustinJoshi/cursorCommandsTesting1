import { expect, test } from "@playwright/test";
import { createTeam, uniqueName } from "./helpers/app-flows";
import { hasSecondaryUserEnv } from "./helpers/auth";

// ─────────────────────────────────────────
// FLOW: EDGE-01..04 — Validation and edge cases
// TESTS: empty input guardrails, duplicate invites
// AUDIT COVERAGE: SECURITY upload/validation findings
// ─────────────────────────────────────────

test.describe("Edge Cases", () => {
  test("EDGE-01: empty team name cannot be submitted", async ({ page }) => {
    await page.goto("/teams/new");
    await expect(page.getByRole("button", { name: "Create Team" })).toBeDisabled();
    await page.getByLabel("Team Name").fill("   ");
    await expect(page.getByRole("button", { name: "Create Team" })).toBeDisabled();
  });

  test("EDGE-02: empty document name cannot be submitted", async ({ page }) => {
    await createTeam(page);
    await page.getByTestId("new-doc-open").click();
    await expect(page.getByTestId("new-doc-submit")).toBeDisabled();
    await page.getByTestId("new-doc-name").fill("  ");
    await expect(page.getByTestId("new-doc-submit")).toBeDisabled();
  });

  test("EDGE-03: removing selected upload file resets upload state", async ({ page }) => {
    await createTeam(page);
    await page.getByTestId("new-doc-open").click();
    await page.getByTestId("new-doc-name").fill(uniqueName("edge-doc"));
    await page.getByTestId("new-doc-file-input").setInputFiles({
      name: "edge.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("edge case"),
    });
    await expect(page.getByText("edge.txt")).toBeVisible();
    await page.getByRole("button", { name: "Cancel" }).click();
    await page.getByTestId("new-doc-open").click();
    await expect(page.getByText("edge.txt")).toHaveCount(0);
  });

  test("EDGE-04: duplicate invite displays error feedback", async ({ page }) => {
    test.skip(!hasSecondaryUserEnv(), "Requires viewer test user env vars");

    await createTeam(page);
    await page.goto(`${page.url()}/settings`);
    await page.getByTestId("member-email-input").fill(process.env.TEST_VIEWER_EMAIL!);
    await page.getByRole("button", { name: "Add" }).click();
    await expect(page.getByText(/member added successfully|invite sent/i)).toBeVisible();

    await page.getByTestId("member-email-input").fill(process.env.TEST_VIEWER_EMAIL!);
    await page.getByRole("button", { name: "Add" }).click();
    await expect(page.getByText(/already a member|already been sent/i)).toBeVisible();
  });
});
