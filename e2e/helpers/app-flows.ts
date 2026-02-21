import { expect, Page } from "@playwright/test";

export function uniqueName(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
}

export async function createTeam(page: Page, name?: string) {
  const teamName = name ?? uniqueName("qa-team");
  await page.goto("/teams/new");
  await page.getByLabel("Team Name").fill(teamName);
  await page.getByRole("button", { name: "Create Team" }).click();
  await page.waitForURL(/\/teams\/[^/]+$/);
  await expect(page.getByRole("heading", { name: teamName })).toBeVisible();
  return { teamName, teamUrl: page.url() };
}

export async function createDocument(
  page: Page,
  docName?: string,
  withFile = false
) {
  const name = docName ?? uniqueName("qa-doc");
  await page.getByTestId("new-doc-open").click();
  await page.getByTestId("new-doc-name").fill(name);

  if (withFile) {
    await page.getByTestId("new-doc-file-input").setInputFiles({
      name: "sample.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("test file contents"),
    });
  }

  await page.getByTestId("new-doc-submit").click();
  await expect(page.getByText(name).first()).toBeVisible();
  return name;
}

export async function openFirstTeamFromDashboard(page: Page) {
  await page.goto("/dashboard");
  const teamLinks = page.locator("a[href^='/teams/']").filter({ hasText: /.+/ });
  await expect(teamLinks.first()).toBeVisible();
  await teamLinks.first().click();
  await page.waitForURL(/\/teams\/[^/]+$/);
}

export async function openFirstDocumentFromTeam(page: Page) {
  const docLinks = page.locator("a[href^='/documents/']");
  await expect(docLinks.first()).toBeVisible();
  await docLinks.first().click();
  await page.waitForURL(/\/documents\/[^/]+$/);
}
