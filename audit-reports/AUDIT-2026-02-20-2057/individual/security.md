# Security Audit Report

Role: Security Auditor  
Scope: `src/`  
Date: 2026-02-20

## Findings

### 🟡 Medium — Internal error details exposed to end users (A05: Security Misconfiguration)
- **Evidence:** Multiple UI flows display raw exception text directly to users via `toast.error(error.message)`.
- **Affected paths:**  
  - `src/components/member-manager.tsx`  
  - `src/components/document-table.tsx`  
  - `src/components/upload-dialog.tsx`  
  - `src/app/teams/new/page.tsx`  
  - `src/app/teams/[teamId]/settings/page.tsx`  
  - `src/app/teams/[teamId]/page.tsx`
- **Risk:** Backend/infra exception content can leak implementation details (function names, validation internals, stack fragments, IDs), improving attacker recon and exposing sensitive internals to untrusted clients.
- **Fix (1/3):** Replace user-facing raw error text with generic messages; log detailed errors only to controlled observability tooling.
  - Example pattern: show `"Operation failed. Please try again."` to user; send full error to server-side logs/monitoring.

### 🟡 Medium — Unrestricted client-side file upload surface (A04: Insecure Design)
- **Evidence:** File inputs accept any file type and no size constraints before generating upload URLs and posting file bytes.
- **Affected paths:**  
  - `src/components/upload-dialog.tsx`  
  - `src/app/teams/[teamId]/page.tsx`
- **Risk:** Users can upload unexpectedly large or dangerous file types, increasing abuse and storage DoS risk. Client checks are not sufficient alone, but their absence broadens attack surface and operational risk.
- **Fix (2/3):** Enforce strict upload policy at both client and server: allowlist MIME/extensions, hard max size, and reject disallowed content before upload URL issuance and again at version creation.

### 🔵 Low — Verbose client console logging of mutation failures (A02: Cryptographic Failures / Sensitive Data Exposure)
- **Evidence:** Client code logs full error objects in browser console.
- **Affected path:**  
  - `src/components/providers.tsx`
- **Risk:** Detailed error objects may expose internal messages, identifiers, or backend details to any signed-in user with browser devtools.
- **Fix (3/3):** Replace raw `console.error(..., err)` with sanitized logs (or remove in production builds). Keep detailed diagnostics in server-side telemetry.

## Deferred

- Additional hardening opportunities may exist outside these top-impact items, but concrete remediation recommendations were intentionally capped to 3 fixes per audit constraints.

## Totals

- High: 0
- Medium: 2
- Low: 1
# Security Audit — src/

**Role:** Application Security Auditor  
**Scope:** src/  
**Date:** 2026-02-20  
**OWASP Top 10 Focus:** A02, A03, A04, A05, A07

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 High  | 0     |
| 🟡 Medium| 2     |
| 🔵 Low  | 1     |

---

## Findings

### 🟡 [SECURITY] Error Message Exposure (A05 — Security Misconfiguration)

**Location:** Multiple components  
- `src/components/upload-dialog.tsx` (lines 114–118)  
- `src/app/teams/[teamId]/page.tsx` (lines 109–113)  
- `src/components/document-table.tsx` (lines 95–97, 113–115)  
- `src/app/teams/[teamId]/settings/page.tsx` (lines 79–84)  
- `src/components/member-manager.tsx` (lines 90–92, 106–108, 117–119, 127–129)

**Issue:** `toast.error(error instanceof Error ? error.message : "…")` surfaces raw backend error messages to the client. Backend errors such as `"Requires one of: admin, editor. You have: viewer"` reveal authorization logic and role structure.

**Fix:** Use generic, user-facing messages in catch blocks. Log the real error server-side or via a secure logging path; do not pass `error.message` to the UI.

```ts
// Instead of:
toast.error(error instanceof Error ? error.message : "Failed to rename");

// Use:
toast.error("Operation failed. Please try again.");
// Optionally log: console.error("Rename failed:", error);
```

**OWASP:** A05 — Security Misconfiguration

---

### 🟡 [SECURITY] File Upload Lacks Client-Side Validation (A04 — Insecure Design)

**Location:**  
- `src/components/upload-dialog.tsx` (lines 50–59, 71–75)  
- `src/app/teams/[teamId]/page.tsx` (lines 55–62, 76–81)

**Issue:** File inputs accept any type and size. No `accept` attribute or size limit. Large uploads can cause poor UX, memory pressure, and unnecessary bandwidth use. Malicious or oversized files can be attempted before server-side checks.

**Fix:** Add client-side validation before upload:

1. Enforce a max file size (e.g. 50MB).
2. Restrict allowed types via `accept` or validation.
3. Reject oversized or disallowed files before calling `generateUploadUrl()`.

```ts
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = ["application/pdf", "image/*", "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];

const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
  const selectedFile = e.target.files?.[0];
  if (!selectedFile) return;
  if (selectedFile.size > MAX_FILE_SIZE) {
    toast.error("File too large. Maximum size is 50MB.");
    e.target.value = "";
    return;
  }
  // ... rest of logic
};
```

**OWASP:** A04 — Insecure Design

---

### 🔵 [SECURITY] NEXT_PUBLIC_* Usage Verification (A02 — Cryptographic Failures)

**Location:** `src/components/providers.tsx` (line 11)

**Issue:** `process.env.NEXT_PUBLIC_CONVEX_URL` is used for the Convex client. Per Convex docs, this URL is intended to be public. The checklist asks to ensure no secrets use `NEXT_PUBLIC_`.

**Fix:** Confirm no secrets (API keys, tokens, etc.) are exposed via `NEXT_PUBLIC_*`. `NEXT_PUBLIC_CONVEX_URL` is acceptable. Add a comment or env validation to document this.

**OWASP:** A02 — Cryptographic Failures (verification only)

---

## Deferred Findings

Additional items were identified but not included in the 3-fix limit:

- **console.error in UserSync** (`providers.tsx` line 24): May log sensitive errors in production; consider a logging abstraction.
- **Backend error messages** (`convex/lib/permissions.ts`): Messages like `"Requires one of: admin, editor. You have: viewer"` leak role structure; consider generic messages in backend.
- **Rate limiting**: Auth flows rely on Clerk; no custom rate limiting in `src/`; acceptable if Clerk provides it.

---

## Positive Observations

- ✅ **A01 — Access Control:** Clerk middleware protects non-public routes; Convex enforces team membership and roles.
- ✅ **A03 — Injection:** No `dangerouslySetInnerHTML`; React escapes user content; no SQL/command injection in `src/`.
- ✅ **A07 — Auth:** Clerk handles auth; Convex validates identity; no custom JWT/session logic in `src/`.
- ✅ **Redirects:** Links use static or builder paths; no open redirects from user input.

---

```
/* ═══════════════════════════════════════════
   SECURITY AUDIT — src/ — 2026-02-20
   🔴 Critical: 0  🟡 Medium: 2  🔵 Hardening: 1
   ═══════════════════════════════════════════ */
```
