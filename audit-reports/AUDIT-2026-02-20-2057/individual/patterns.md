# Patterns Auditor Report (`src/`)

Date: 2026-02-20

## Findings (Top 3 fixes only)

### 1) 🟡 Duplicate upload + version-creation workflow in two feature flows
- **Severity:** Medium
- **Type:** DRY violation / abstraction opportunity
- **Evidence:** `src/app/teams/[teamId]/page.tsx`, `src/components/upload-dialog.tsx`
- **Why it matters:** File upload to storage, `storageId` extraction, and version record creation are implemented in both places. Changes to upload behavior (validation, error mapping, metadata fields, retry logic) now require multi-file edits and are prone to drift.
- **Concrete fix:** Extract shared logic into `src/hooks/useDocumentUpload.ts` (or `src/lib/documents/uploadAndCreateVersion.ts`) with a single API like:
  - `uploadAndCreateVersion({ file, comment, documentId, teamId, createDocumentName? })`
  - Reuse from both `TeamPage` and `UploadDialog`.

### 2) 🟡 `formatFileSize` duplicated across components
- **Severity:** Medium
- **Type:** Utility duplication
- **Evidence:** `src/components/document-table.tsx`, `src/components/version-history.tsx`
- **Why it matters:** Formatting behavior is duplicated and can diverge (precision, unit list, edge-case handling). This is a shared presentation concern used by document/version surfaces.
- **Concrete fix:** Move to `src/lib/format-file-size.ts` (or `src/lib/formatters.ts`) and import in both components.

### 3) 🔵 Repeated error-to-toast mapping boilerplate
- **Severity:** Low
- **Type:** Reusable error-handling abstraction
- **Evidence:** `src/components/member-manager.tsx`, `src/components/document-table.tsx`, `src/components/upload-dialog.tsx`, `src/app/teams/new/page.tsx`, `src/app/teams/[teamId]/settings/page.tsx`, `src/app/teams/[teamId]/page.tsx`
- **Why it matters:** `error instanceof Error ? error.message : "...fallback..."` is repeated in many mutation handlers. This is noisy and makes fallback text and behavior inconsistent over time.
- **Concrete fix:** Introduce `src/lib/get-error-message.ts` (and optionally `src/lib/toast-error.ts`) to centralize extraction and standardize fallback behavior.

## Deferred (not expanded due to 3-fix cap)

Additional pattern opportunities were identified but intentionally deferred:
- Repeated loading skeleton JSX blocks across route pages/components.
- Repeated role permission checks (`admin || editor`) that could be centralized in role helpers.
- Repeated date formatting (`new Date(...).toLocaleDateString()`) that could use shared formatter utilities.

## Severity Totals
- **High:** 0
- **Medium:** 2
- **Low:** 1
# Patterns & DRY Audit — src/

**Scope:** `src/`  
**Role:** Patterns Auditor  
**Date:** 2026-02-20

---

## Summary

| Severity | Count |
|----------|-------|
| High     | 1     |
| Medium   | 2     |
| Low      | 5+ (deferred) |

**Concrete fixes provided:** 3 (highest-impact only)

---

## High Priority — Active Duplication

### 1. `formatFileSize` — Duplicated in 2 files

Identical implementation in:
- `src/components/version-history.tsx` (lines 37–43)
- `src/components/document-table.tsx` (lines 64–70)

Additionally, `upload-dialog.tsx` and `teams/[teamId]/page.tsx` use inline `(file.size / 1024).toFixed(1)} KB`, which is inconsistent and does not handle MB/GB.

**Fix:** Consolidate into `lib/utils.ts` or `lib/format.ts`:

```
lib/utils.ts (or lib/format.ts)
  formatFileSize(bytes: number): string
```

---

## Medium Priority — Maintenance Risk

### 2. Avatar initials — Duplicated logic

Same pattern in 2 components:
- `version-history.tsx` (lines 119–124): `version.uploader?.name?.split(" ").map((n) => n[0]).join("").toUpperCase() ?? "?"`
- `member-manager.tsx` (lines 199–203): `member.user?.name?.split(" ").map((n) => n[0]).join("").toUpperCase() ?? "?"`

**Fix:** Extract as `lib/utils.ts`:

```
getInitials(name: string | null | undefined): string
```

---

### 3. Error-to-toast pattern — Repeated 8+ times

Pattern `error instanceof Error ? error.message : "Failed to X"` with `toast.error(...)` appears in:
- `member-manager.tsx` (4 handlers)
- `document-table.tsx` (2 handlers)
- `upload-dialog.tsx` (1 handler)
- `teams/new/page.tsx` (1 handler)
- `teams/[teamId]/settings/page.tsx` (1 handler)
- `teams/[teamId]/page.tsx` (1 handler)

**Fix:** Extract shared utility:

```
lib/toastError.ts
  toToastError(error: unknown, fallback: string): void
  // Calls toast.error with extracted message
```

---

## Low Priority — Abstraction Opportunities (Deferred)

### 4. File upload flow duplication

`teams/[teamId]/page.tsx` (lines 65–116) contains inline create-document + upload logic that mirrors `upload-dialog.tsx`. Same flow: `generateUploadUrl` → `fetch` → `createVersion` / `createDocument`. File picker UI is also duplicated (lines 209–244 vs upload-dialog 152–188).

**Deferred suggestion:** Use `UploadDialog` in team page for new-doc-with-file flow, or extract `useUploadFile` hook.

---

### 5. Empty state pattern

Similar structure across:
- `dashboard/page.tsx`: icon + "No teams yet" + description + CTA
- `document-table.tsx`: icon + "No documents yet" + description
- `version-history.tsx`: icon + "No versions yet" + description

**Deferred suggestion:** Extract `components/EmptyState` with props for icon, title, description, action.

---

### 6. Loading skeleton pattern

Similar skeleton markup across:
- `teams/[teamId]/settings/page.tsx`
- `teams/[teamId]/page.tsx`
- `documents/[documentId]/page.tsx`
- `dashboard/page.tsx`

**Deferred suggestion:** Extract `components/PageSkeleton` or `components/ContentSkeleton`.

---

### 7. `canEdit` role check

`role === "admin" || role === "editor"` appears in:
- `document-table.tsx` (line 83)
- `documents/[documentId]/page.tsx` (lines 49–50)
- `teams/[teamId]/page.tsx` (lines 52–53)

**Deferred suggestion:** Extract `lib/roles.ts` — `canEdit(role: Role): boolean`, `canDelete(role: Role): boolean`.

---

### 8. Route strings

`/dashboard`, `/teams/new`, `/teams/${id}`, `/documents/${id}` hardcoded in multiple files.

**Deferred suggestion:** `lib/routes.ts` or `constants/routes.ts`.

---

## Recommended Fixes (Top 3)

| # | Fix | Location | Impact |
|---|-----|----------|--------|
| 1 | Add `formatFileSize` and `getInitials` to `lib/utils.ts` | `lib/utils.ts` | Removes 2 duplicates, unifies file size display |
| 2 | Add `toToastError(error, fallback)` to `lib/toastError.ts` | New file | Replaces 8+ inline patterns |
| 3 | Use shared `formatFileSize` in upload-dialog and team page | `upload-dialog.tsx`, `teams/[teamId]/page.tsx` | Consistent file size display |

---

## Severity Key

- **High** — Active duplication causing maintenance risk
- **Medium** — Duplication or repeated pattern, moderate risk
- **Low** — Abstraction opportunity, improves maintainability

---

```
/* ═══════════════════════════════════════════
   DRY / PATTERNS AUDIT — src/ 2026-02-20
   High: 1  Medium: 2  Low: 5+ (deferred)
   Suggested extractions: lib/utils (formatFileSize, getInitials), lib/toastError, components/EmptyState, components/PageSkeleton, lib/roles
   ═══════════════════════════════════════════ */
```
