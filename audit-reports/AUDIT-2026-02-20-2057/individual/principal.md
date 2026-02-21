# Principal Engineer Audit

Date: 2026-02-20  
Scope: `src/`

## Findings (Top 3 Fixes)

### 1) 🔴 High — `UploadDialog` breaks controlled dialog contract and can prevent opening
- **Where:** `src/components/upload-dialog.tsx`
- **Why it matters:** `Dialog` calls `onOpenChange(true)` when the trigger is clicked, but the current handler ignores the `open` argument and always calls `onOpenChange(false)`. In controlled mode, this can immediately close the dialog and block upload flows.
- **Evidence:** `onOpenChange={handleClose}` with `handleClose()` always resetting state and forcing `onOpenChange(false)`.
- **Fix:** Change handler signature to `(nextOpen: boolean)` and only reset state when `nextOpen === false`; pass `nextOpen` through to parent unchanged.

### 2) 🔴 High — N+1 query pattern for version download URLs
- **Where:** `src/components/version-history.tsx`
- **Why it matters:** Each row renders `VersionDownloadButton`, and each button runs `useQuery(api.documentVersions.getDownloadUrl, { storageId })`. On documents with many versions this creates one reactive query per row, increasing client/server load and hurting list performance.
- **Evidence:** `versions.map(...)` + per-item `useQuery(...)` in `VersionDownloadButton`.
- **Fix:** Replace per-row query with a single batched API (e.g., `getDownloadUrlsForVersions(documentId)`), or lazily fetch URL on click via one mutation/action/query call path.

### 3) 🟡 Medium — Duplicate upload/version-creation workflow across components
- **Where:** `src/app/teams/[teamId]/page.tsx`, `src/components/upload-dialog.tsx`
- **Why it matters:** File upload + storage + version creation logic is duplicated in two places. This is already diverging (different open/close behavior and UX branches), making fixes and validation inconsistent over time.
- **Evidence:** Both implement near-identical 4-step flows: generate upload URL, POST file, parse `storageId`, create document/version.
- **Fix:** Extract a shared upload service/hook (e.g., `useDocumentUpload`) that owns the async workflow and error mapping; keep UI components focused on input/state presentation.

## Deferred Findings

Additional lower-priority items were identified but deferred to honor the 3-fix cap.  
Example deferred item: `members={members as any}` in `src/app/teams/[teamId]/settings/page.tsx` weakens type safety and can hide contract drift between query results and `MemberManager` props.

## Severity Totals

- High: 2
- Medium: 1
- Low: 0
