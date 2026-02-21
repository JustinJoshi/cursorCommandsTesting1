import fs from "node:fs";
import path from "node:path";
import { clerkSetup } from "@clerk/testing/playwright";
import { test as setup } from "@playwright/test";
import { signIn } from "./helpers/auth";

const authFile = path.join(__dirname, ".auth/user.json");

setup.describe.configure({ mode: "serial" });

setup("authenticate", async ({ page }) => {
  fs.mkdirSync(path.dirname(authFile), { recursive: true });
  await clerkSetup();
  await signIn(page);
  await page.context().storageState({ path: authFile });
});
