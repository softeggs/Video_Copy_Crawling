# Initialize Hierarchical AGENTS Knowledge Base

## TL;DR
> **Summary**: Generate an `AGENTS.md` hierarchy for this repository in update mode by default, using focused discovery to exclude artifacts and to place child instruction files only where responsibilities diverge enough to justify them.
> **Deliverables**:
> - Root `AGENTS.md`
> - `core/AGENTS.md`
> - `backend/AGENTS.md`
> - `ios_app/iOS_Video_Intelligence/AGENTS.md`
> - Conditional `READM/AGENTS.md` if scoring stays at or above the distinct-domain threshold during execution
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: 1 → 3 → 6/7/8/9/11 → 12 → 13/14/15

## Context
### Original Request
- Run `/init-deep` using the supplied workflow: concurrent discovery, directory scoring, root-first AGENTS generation, subdirectory generation, then deduplication and validation.
- Default behavior is update mode; `--create-new` and `--max-depth=N` are alternate execution modes.

### Interview Summary
- No blocking preference questions remained after repo exploration.
- Default applied: treat the request as update mode because no flags were supplied.
- Validation will rely on repository scans, file existence checks, and generated-file review because the repo has no formal test runner or CI.
- LSP symbol extraction is not dependable in this environment, so AST/grep/path analysis is the required fallback.

### Metis Review (gaps addressed)
- Canonical scope now explicitly excludes sandbox/artifact trees from scoring and generation.
- Update mode is defined as: create missing canonical target files, fully regenerate canonical target files after reading them, preserve sandbox/non-canonical AGENTS by excluding them from rewrite scope.
- Scoring is deterministic and includes explicit expected candidates and non-candidates for this repo.
- De-duplication is executable: fail if a child repeats root content verbatim in blocks longer than 15 lines or if duplicated normalized text exceeds 30% of the child file.
- `test/` is root-covered by default and is not a mandatory child AGENTS target because the subtree is ignored, noisy, and dominated by manual smoke scripts plus sandbox/cache state.

## Work Objectives
### Core Objective
Create a decision-complete execution plan for generating a repo-specific `AGENTS.md` hierarchy that reflects the actual codebase seams (`core`, `backend`, iOS app, docs) while keeping tests root-covered and explicitly excluding artifact-heavy and sandbox-only paths.

### Deliverables
- One root `AGENTS.md` covering repo-wide navigation, exclusions, commands, and cross-cutting guardrails.
- Child `AGENTS.md` files for the confirmed high-value split points.
- Optional child `AGENTS.md` for `READM/` only if the focused scoring pass confirms it is distinct enough from root guidance.
- No child `AGENTS.md` under `test/`; that subtree is documented from the root unless a future scoring rule changes.
- Verification evidence showing file existence, line-count bounds, duplicate-content review, and exclusion compliance.

### Definition of Done (verifiable conditions with commands)
- Expected `AGENTS.md` files exist at the approved locations and no new `AGENTS.md` files appear in excluded artifact directories.
- Root and child files stay within the requested size bands and do not substantially repeat parent content.
- Existing sandbox file `test/openclaw-workspace/AGENTS.md` is preserved or explicitly excluded from rewrite scope.
- No `test/AGENTS.md` is created in the default run; test guidance remains at root level.
- Execution report states whether `READM/AGENTS.md` was created and why.

### Must Have
- Discovery excludes `downloads/`, `outputs/`, `logs/`, `test/xdg_*`, and similar artifact/cache directories from scoring.
- Existing instruction files are read before any update-mode edits.
- Update mode creates missing canonical targets and fully rewrites only canonical target files selected by scoring; sandbox-only AGENTS are never treated as rewrite targets.
- Root AGENTS content reflects real repo structure, not stale README assumptions.
- Child files are domain-specific and omit parent-level generic guidance.
- Verification is zero-human and produces concrete evidence files.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- Do not create AGENTS files for data/artifact folders.
- Do not create `test/AGENTS.md` in the default hierarchy.
- Do not treat `docs/` as the canonical docs hub; `READM/` is the real documentation subtree.
- Do not overwrite sandbox/workspace content under `test/openclaw-workspace/` unless the command scope explicitly includes sandbox data.
- Do not include secrets, copied credentials, or instructions derived from `.env` or `cookies*.txt`.
- Do not repeat root-level advice verbatim inside child files.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: TDD-style snapshot/validation checks + repository scan / generated-file review (no formal framework present)
- QA policy: Every task has agent-executed scenarios
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks for max parallelism.

Wave 1: discovery normalization, existing-instructions inventory, focused scoring, root content contract, child-scope matrix

Wave 2: root AGENTS generation plus parallel child AGENTS generation for `core`, `backend`, `ios_app/iOS_Video_Intelligence`, conditional `READM`, and explicit root-coverage validation for `test/`

Wave 3: hierarchy review, duplicate trimming, exclusion validation, final report assembly

### Dependency Matrix (full, all tasks)
- 1 blocks 3, 4, 5
- 2 blocks 4, 5, 12
- 3 blocks 6, 7, 8, 9, 10, 11
- 4 blocks 6
- 5 blocks 7, 8, 9, 11
- 6/7/8/9/10/11 block 12
- 12 blocks 13, 14, 15

### Agent Dispatch Summary (wave → task count → categories)
- Wave 1 → 5 tasks → deep / unspecified-high / writing
- Wave 2 → 6 tasks → writing / unspecified-high / quick
- Wave 3 → 4 tasks → writing / unspecified-high / quick

### Deterministic Scoring Rubric
- Root `.`: always create.
- +6: focused file count > 20 after exclusions
- +4: distinct language/toolchain boundary (e.g. Swift/Xcode vs Python)
- +4: distinct app/domain boundary (e.g. FastAPI backend vs processing core)
- +3: directory owns entrypoint/composition file (`main.py`, app root, Xcode app root, etc.)
- +2: concentrated docs/manuals subtree with 10+ Markdown files
- -6: path is primarily artifact/cache/sandbox/manual-local state
- Approve child AGENTS at score ≥10; conditional review at 6-9; reject at ≤5
- Expected approvals in this repo: `core/`, `backend/`, `ios_app/iOS_Video_Intelligence/`
- Expected conditional path: `READM/`
- Expected rejections: `docs/`, `test/`, `downloads/`, `outputs/`, `logs/`, `test/xdg_*`, `test/openclaw-workspace/`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [ ] 1. Normalize discovery scope and exclusion rules

  **What to do**: Build the focused discovery inventory that `/init-deep` will rely on. Exclude artifact and cache paths from counts, scoring, and placement decisions; include real source, docs, and test directories only. Persist the raw-vs-focused comparison into evidence so later tasks do not regress to inflated counts.
  **Must NOT do**: Do not score `downloads/`, `outputs/`, `logs/`, `__pycache__/`, `.git/`, `node_modules/`, `test/xdg_*`, or sandbox-only workspace data as if they were source modules.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: repo-wide inventory with exclusion logic and evidence capture
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 3, 4, 5 | Blocked By: none

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `README.md:107-124` — current high-level project structure to validate against real scans
  - Pattern: `READM/PROJECT_STRUCTURE.md:31-54` — distinguishes docs/data/config areas that must not all be treated equally
  - Pattern: `.gitignore:14-35` — existing artifact ignores (`downloads`, `outputs`, `logs`, `test/*`) that influence exclusion rules
  - Pattern: `test/` directory listing — contains both real smoke tests and cache/workspace noise; must be separated during discovery

  **Acceptance Criteria** (agent-executable only):
  - [ ] A focused inventory is saved to `.sisyphus/evidence/task-1-discovery.json` with raw counts, focused counts, excluded paths, and top candidate source directories.
  - [ ] The focused inventory excludes `downloads/`, `outputs/`, `logs/`, and `test/xdg_*` from all scoring inputs.
  - [ ] The evidence clearly shows the raw-vs-focused delta so later scoring can be audited.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path focused scan
    Tool: Bash
    Steps: Run a repo scan; write raw counts and focused counts to `.sisyphus/evidence/task-1-discovery.json`; verify excluded directories are listed explicitly.
    Expected: Evidence shows focused counts materially smaller than raw counts and none of the excluded directories appear in the candidate-source list.
    Evidence: .sisyphus/evidence/task-1-discovery.json

  Scenario: Failure/edge case artifact pollution
    Tool: Bash
    Steps: Run the validation check against the focused inventory, asserting that `test/xdg_cache`, `downloads`, `outputs`, and `logs` are absent from candidate-source directories.
    Expected: Validation fails loudly if any excluded directory leaks into the scoring set.
    Evidence: .sisyphus/evidence/task-1-discovery-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 2. Inventory existing instruction files, stale docs, and sensitive-file guardrails

  **What to do**: Identify all existing `AGENTS.md`/`CLAUDE.md` files, document whether they are canonical or sandbox-only, and capture repo-specific guardrails from stale docs and secret-sensitive files. Freeze a “do not trust blindly” list for later authoring tasks.
  **Must NOT do**: Do not overwrite or inherit sandbox instructions from `test/openclaw-workspace/AGENTS.md` as if they were repo policy.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: cross-checking docs drift, sensitive files, and existing instruction artifacts
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 5, 12 | Blocked By: none

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `test/openclaw-workspace/AGENTS.md:1-18` — confirms an existing AGENTS file exists only inside sandbox workspace data
  - Pattern: `.gitignore:1-35` — `.env` is commented out while `test/*` is ignored; both must become authoring guardrails
  - Pattern: `README.md:68-89` — references helper scripts that are not present in the root scan; demonstrates doc drift
  - Pattern: `plans/PLAN.md:24-37` — stale plan still claims backend scaffold creation is pending even though `backend/` exists
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-18` — hardcoded Feishu/server configuration must not be recopied into AGENTS content

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-2-guardrails.md` lists every discovered instruction file and classifies it as canonical, sandbox-only, or ignore.
  - [ ] The guardrail evidence includes stale-doc examples, secret-sensitive paths to avoid, and a note that `READM/` is the actual docs hub.
  - [ ] No later generation task needs to rediscover whether existing AGENTS files already exist.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path instruction inventory
    Tool: Bash
    Steps: Search for `AGENTS.md` and `CLAUDE.md`; classify results; search for `.env` and `cookies*.txt` references; write findings to `.sisyphus/evidence/task-2-guardrails.md`.
    Expected: Evidence identifies `test/openclaw-workspace/AGENTS.md` as sandbox-only and records secret-handling guardrails.
    Evidence: .sisyphus/evidence/task-2-guardrails.md

  Scenario: Failure/edge case hidden canonical file
    Tool: Bash
    Steps: Re-run the instruction-file validation before authoring; fail if any non-sandbox `AGENTS.md` or `CLAUDE.md` exists but is missing from the inventory.
    Expected: Validation halts generation until the missing file is added to the guardrail inventory.
    Evidence: .sisyphus/evidence/task-2-guardrails-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 3. Score directories and freeze the target AGENTS hierarchy

  **What to do**: Apply the command’s deterministic scoring matrix using the focused inventory, then freeze `AGENTS_LOCATIONS` with reasons. The expected default outcome is root plus `core`, `backend`, and `ios_app/iOS_Video_Intelligence`, with `READM` treated as conditional and `test/` explicitly kept root-covered.
  **Must NOT do**: Do not let raw file counts from caches or logs decide the hierarchy; do not create AGENTS for `docs/`, `test/`, `downloads/`, `outputs/`, `logs/`, or sandbox workspace folders.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: combines repo metrics with domain-boundary judgment while still staying evidence-based
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 6, 7, 8, 9, 10, 11 | Blocked By: 1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `backend/main.py:1-22` — proves `backend/` is a distinct FastAPI surface
  - Pattern: `core/pipeline.py:12-40` — shows `core/` is the processing orchestration center
  - Pattern: `core/scheduler.py:15-30` — shows `core/` also owns scheduling and retry orchestration
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-31` — confirms the iOS subtree is a separate product surface with its own config path
  - Pattern: `test/test_scheduler.py:1-20` — shows `test/` is a manual smoke-test area that should stay root-covered rather than become a child AGENTS target
  - Pattern: `READM/PROJECT_STRUCTURE.md:31-42` — confirms `READM/` is a concentrated documentation subtree

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-3-scoring.json` contains the score table, thresholds applied, approved paths, rejected paths, and reasons.
  - [ ] Approved paths include the root and all confirmed distinct-domain children; conditional paths are explicitly labeled conditional.
  - [ ] Rejected paths include `docs/`, `test/`, `downloads/`, `outputs/`, `logs/`, and sandbox/cache subtrees with explicit reasons.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path scoring
    Tool: Bash
    Steps: Compute directory scores from the focused inventory; write approved and rejected paths to `.sisyphus/evidence/task-3-scoring.json`.
    Expected: Root, `core`, `backend`, and `ios_app/iOS_Video_Intelligence` are approved; `READM` is either approved or explicitly marked conditional; `test/` is explicitly rejected as root-covered.
    Evidence: .sisyphus/evidence/task-3-scoring.json

  Scenario: Failure/edge case artifact wins by raw count
    Tool: Bash
    Steps: Run a guard check that rejects any approved path matching `downloads`, `outputs`, `logs`, `test/xdg_*`, or `openclaw-workspace`.
    Expected: Validation fails if an excluded artifact path is approved.
    Evidence: .sisyphus/evidence/task-3-scoring-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 4. Define the root AGENTS content contract

  **What to do**: Freeze the exact sections, emphasis, and repo-specific notes for the root `AGENTS.md` before any file writing starts. The contract must include actual app surfaces, where to look by task, command hints, docs hub correction, exclusion rules, and sensitive-file guardrails.
  **Must NOT do**: Do not allow generic “always write tests” or “follow best practices” filler; root guidance must reflect this repository’s actual shape and current validation limits.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: convert discovered repo truth into concise, high-signal root guidance
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 6 | Blocked By: 1, 2

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `README.md:17-25` — core stack summary
  - Pattern: `README.md:107-124` — current published project structure, useful but incomplete/stale
  - Pattern: `READM/PROJECT_STRUCTURE.md:15-48` — fuller module/data/doc map
  - Pattern: `backend/main.py:7-22` — backend app and router composition
  - Pattern: `.gitignore:1-35` — artifact and secret-handling caveats
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-18` — sensitive config risk that root AGENTS must warn about without copying values

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-4-root-contract.md` defines the exact root sections and the bullet points each section must contain.
  - [ ] The contract explicitly states that `READM/` is the docs hub and that artifact/cache folders are out of scope for source exploration.
  - [ ] The contract includes repo-specific anti-patterns: trusting stale README links, editing secrets, and treating sandbox AGENTS as canonical.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path root contract
    Tool: Bash
    Steps: Assemble the root content contract from the referenced files and save it to `.sisyphus/evidence/task-4-root-contract.md`.
    Expected: Contract covers overview, structure, where-to-look, conventions, anti-patterns, commands, and notes without generic filler.
    Evidence: .sisyphus/evidence/task-4-root-contract.md

  Scenario: Failure/edge case stale-doc contamination
    Tool: Bash
    Steps: Validate the contract against the live root directory and reject any section that references a missing root file or treats `docs/` as the main docs hub.
    Expected: Validation fails if stale docs assumptions leak into the root contract.
    Evidence: .sisyphus/evidence/task-4-root-contract-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`

- [ ] 5. Define the child AGENTS scope matrix

  **What to do**: For each approved child path, define exactly what its AGENTS file must cover, what it inherits from root, and what it must omit to avoid duplication. Include a conditional branch for `READM/` so generation is skipped cleanly if the score falls below threshold, and explicitly record that `test/` remains root-covered.
  **Must NOT do**: Do not let child files repeat root sections unchanged; do not invent module ownership beyond what the repo structure proves.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: content decomposition and anti-duplication matrix across multiple child files
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 7, 8, 9, 10, 11 | Blocked By: 1, 2, 3

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `core/pipeline.py:12-47` — processing pipeline responsibility boundary for `core/`
  - Pattern: `core/ai_processor.py:30-80` — AI-provider behavior belongs in `core/` guidance
  - Pattern: `backend/main.py:1-22` — backend entry and router composition for `backend/`
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift:1-18` — iOS repository abstraction boundary
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/APIService.swift:16-90` — iOS/backend contract drift that the iOS AGENTS should call out
  - Pattern: `READM/README.md` — documentation subtree is operational/manual-guide oriented if approved

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-5-child-matrix.md` lists each child target, required sections, inherited sections, omissions, and repo-specific caveats.
  - [ ] The matrix explicitly distinguishes mandatory child files from conditional ones.
  - [ ] The matrix includes one sentence per child explaining why that directory deserves its own AGENTS file, plus one sentence explaining why `test/` does not.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path child matrix
    Tool: Bash
    Steps: Produce the scope matrix for all approved child targets; save it to `.sisyphus/evidence/task-5-child-matrix.md`.
    Expected: Each child target has unique responsibilities, explicit omissions, and no root-text duplication.
    Evidence: .sisyphus/evidence/task-5-child-matrix.md

  Scenario: Failure/edge case duplicate child scope
    Tool: Bash
    Steps: Compare child section definitions and fail if two child files have effectively identical scopes or if a skipped conditional target still has generation instructions.
    Expected: Validation flags duplicated or contradictory child scopes before authoring starts.
    Evidence: .sisyphus/evidence/task-5-child-matrix-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `core/AGENTS.md`, `backend/AGENTS.md`, `ios_app/iOS_Video_Intelligence/AGENTS.md`, `READM/AGENTS.md`

- [ ] 6. Create or update the root `AGENTS.md`

  **What to do**: Author the root `AGENTS.md` using the frozen root contract. Include overview, structure, where-to-look guidance for Streamlit/core/backend/iOS/tests/docs, artifact exclusions, command hints, stale-doc warnings, and sensitive-file guardrails. In update mode, read any existing canonical root file first, salvage any still-valid repo-specific notes, then fully regenerate the root file from the approved contract; if no canonical root file exists, create a new one.
  **Must NOT do**: Do not copy sandbox instructions from `test/openclaw-workspace/AGENTS.md`; do not include secrets, hardcoded credentials, or false claims about missing/present files.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: concise repo-level authoring from a fixed contract
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 4

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `README.md:17-25` — stack summary
  - Pattern: `README.md:107-124` — published top-level structure
  - Pattern: `READM/PROJECT_STRUCTURE.md:15-48` — expanded structure and subsystem roles
  - Pattern: `.gitignore:1-35` — exclusions and secret-handling caveats
  - Pattern: `backend/main.py:7-22` — backend exists and should be discoverable from root guidance
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-18` — root guidance must warn about sensitive config drift without reproducing values

  **Acceptance Criteria** (agent-executable only):
  - [ ] `AGENTS.md` exists at repo root.
  - [ ] Root file stays between 50 and 150 lines.
  - [ ] Root file explicitly marks `READM/` as the main docs hub and `downloads/`, `outputs/`, `logs/`, `test/xdg_*` as non-source/generated.
  - [ ] Root file includes cross-cutting warnings about stale docs, sandbox AGENTS, and secret-bearing files.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path root authoring
    Tool: Bash
    Steps: Create/update `AGENTS.md`; count lines; grep for required sections and repo-specific exclusions; save checks to `.sisyphus/evidence/task-6-root.txt`.
    Expected: Root file exists, line count is within bounds, and required repo-specific guardrails are present.
    Evidence: .sisyphus/evidence/task-6-root.txt

  Scenario: Failure/edge case generic or stale content
    Tool: Bash
    Steps: Validate that the root file does not reference missing helper scripts as canonical commands and does not contain copied secrets or sandbox-only rules.
    Expected: Validation fails if stale or secret-bearing content appears.
    Evidence: .sisyphus/evidence/task-6-root-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`

- [ ] 7. Create or update `core/AGENTS.md`

  **What to do**: Author `core/AGENTS.md` around processing-pipeline ownership: downloading, audio handling, transcription, AI polishing, Feishu sync, scheduler interactions, temp-file cleanup, and retry/side-effect risks. Make it clear that `core/` is the operational heart of the Python app.
  **Must NOT do**: Do not restate root-level repo overview or backend/iOS guidance; do not omit async/side-effect warnings.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: targeted subsystem guidance for the densest Python domain
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `core/pipeline.py:12-47` — end-to-end processing orchestration
  - Pattern: `core/pipeline.py:94-127` — Markdown output and temp-file cleanup behavior
  - Pattern: `core/scheduler.py:15-30` — scheduler state and retry constants
  - Pattern: `core/scheduler.py:63-151` — blank-record detection flow
  - Pattern: `core/ai_processor.py:30-80` — provider resolution and AI-mode behavior

  **Acceptance Criteria** (agent-executable only):
  - [ ] `core/AGENTS.md` exists and stays within 30-80 lines.
  - [ ] File explains `core/` responsibilities, side effects, and where to look first for pipeline/scheduler/AI changes.
  - [ ] File does not repeat root-level structure tables verbatim.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path core authoring
    Tool: Bash
    Steps: Create/update `core/AGENTS.md`; verify required subsystem references and line count; save checks to `.sisyphus/evidence/task-7-core.txt`.
    Expected: File is concise, core-specific, and references pipeline/scheduler/AI concerns.
    Evidence: .sisyphus/evidence/task-7-core.txt

  Scenario: Failure/edge case root duplication
    Tool: Bash
    Steps: Compare `core/AGENTS.md` against root `AGENTS.md` for large duplicated blocks.
    Expected: Validation fails if the child file largely mirrors root content.
    Evidence: .sisyphus/evidence/task-7-core-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `core/AGENTS.md`

- [ ] 8. Create or update `backend/AGENTS.md`

  **What to do**: Author `backend/AGENTS.md` around FastAPI entrypoints, router boundaries, auth/dependency flow, schema/model coordination, and API contract stability. Make it clear that this subtree is separate from the Streamlit `core/` pipeline.
  **Must NOT do**: Do not document backend as if it were the only app surface; do not repeat root-level instructions or claim routes that the code does not expose.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: concise API-specific guidance
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `backend/main.py:1-22` — backend entrypoint, DB startup, router inclusion
  - Pattern: `backend/` directory listing — separate API subtree with auth/database/models/schemas/routers
  - Pattern: `plans/PLAN.md:24-37` — stale planning artifact that proves docs about backend scaffolding may be outdated and must not be copied blindly

  **Acceptance Criteria** (agent-executable only):
  - [ ] `backend/AGENTS.md` exists and stays within 30-80 lines.
  - [ ] File points agents to `main.py`, `routers/`, `models.py`, `schemas.py`, and auth/dependency files.
  - [ ] File includes a guardrail to verify live routes/contracts from code, not from stale plan documents.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path backend authoring
    Tool: Bash
    Steps: Create/update `backend/AGENTS.md`; verify route/auth/model references and line count; save checks to `.sisyphus/evidence/task-8-backend.txt`.
    Expected: File is backend-specific and grounded in current code, not old planning docs.
    Evidence: .sisyphus/evidence/task-8-backend.txt

  Scenario: Failure/edge case invented API guidance
    Tool: Bash
    Steps: Validate that every route or module mentioned in `backend/AGENTS.md` exists in `backend/`.
    Expected: Validation fails if the file mentions nonexistent endpoints/modules.
    Evidence: .sisyphus/evidence/task-8-backend-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `backend/AGENTS.md`

- [ ] 9. Create or update `ios_app/iOS_Video_Intelligence/AGENTS.md`

  **What to do**: Author the iOS child file around SwiftUI/Xcode structure, service/repository/model/view boundaries, and the current direct-Feishu-vs-server split. Call out that the subtree has its own tests and that server mode is incomplete.
  **Must NOT do**: Do not copy sensitive Feishu credentials into documentation; do not present backend mode as fully implemented when `AppConfig` still defaults to direct Feishu.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: separate language/toolchain/domain guidance
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `ios_app/iOS_Video_Intelligence` directory listing — subtree shape (`Models`, `Services`, `Views`, tests)
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-31` — current direct-Feishu default and incomplete server mode
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift:1-18` — repository abstraction boundary
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/APIService.swift:16-90` — server API expectations and contract drift risk

  **Acceptance Criteria** (agent-executable only):
  - [ ] `ios_app/iOS_Video_Intelligence/AGENTS.md` exists and stays within 30-80 lines.
  - [ ] File explains where to look for models, services, views, and tests.
  - [ ] File warns that current production behavior is direct Feishu and that server/API assumptions must be verified from code.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path iOS authoring
    Tool: Bash
    Steps: Create/update `ios_app/iOS_Video_Intelligence/AGENTS.md`; verify section coverage and line count; save checks to `.sisyphus/evidence/task-9-ios.txt`.
    Expected: File is Swift/iOS-specific and accurately notes the direct-Feishu default.
    Evidence: .sisyphus/evidence/task-9-ios.txt

  Scenario: Failure/edge case secret leakage or false server claims
    Tool: Bash
    Steps: Validate that the file contains no copied credential strings and does not claim server mode is implemented end-to-end.
    Expected: Validation fails on leaked secrets or overstated backend support.
    Evidence: .sisyphus/evidence/task-9-ios-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `ios_app/iOS_Video_Intelligence/AGENTS.md`

- [ ] 10. Validate that `test/` remains root-covered and no child AGENTS is generated there

  **What to do**: Prove that `test/` is intentionally handled by the root `AGENTS.md` instead of a child file. Capture evidence that the subtree is ignored/manual/noisy, ensure root guidance mentions manual smoke tests, and verify that no `test/AGENTS.md` is created.
  **Must NOT do**: Do not create `test/AGENTS.md`; do not portray `/test` as a formal CI suite; do not encourage edits inside `test/xdg_*` or `openclaw-*` unless explicitly needed.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: deterministic validation of a deliberate non-generation decision
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 6

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `test/test_scheduler.py:1-20` — representative manual scheduler smoke test
  - Pattern: `.gitignore:35` — `test/*` is ignored, so local test state is not authoritative repo history
  - Pattern: `test/openclaw-workspace/AGENTS.md:1-18` — sandbox workspace instructions must be treated separately
  - Pattern: `AGENTS.md` — root guidance must carry the `test/` caveats if no child file is created

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-10-test-scope.txt` confirms `test/` is excluded from child generation and covered by root guidance.
  - [ ] No `test/AGENTS.md` exists after generation.
  - [ ] Root `AGENTS.md` includes a note that `test/` contains manual smoke/integration scripts plus sandbox/cache noise.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path root-covered test handling
    Tool: Bash
    Steps: Verify that no `test/AGENTS.md` exists, confirm root `AGENTS.md` mentions the manual/noisy nature of `test/`, and save the result to `.sisyphus/evidence/task-10-test-scope.txt`.
    Expected: `test/` is documented from root and no child AGENTS file exists.
    Evidence: .sisyphus/evidence/task-10-test-scope.txt

  Scenario: Failure/edge case sandbox confusion
    Tool: Bash
    Steps: Fail if `test/AGENTS.md` exists or if root guidance treats `test/openclaw-workspace/AGENTS.md` as canonical policy.
    Expected: Validation fails on accidental child generation or sandbox-policy inheritance.
    Evidence: .sisyphus/evidence/task-10-test-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`

- [ ] 11. Conditionally create or skip `READM/AGENTS.md`

  **What to do**: Use the frozen scoring decision to either create `READM/AGENTS.md` or explicitly skip it. If created, the file should cover documentation organization, doc drift, and operational-guide conventions. If skipped, record the skip reason in evidence and the final report.
  **Must NOT do**: Do not create `READM/AGENTS.md` just because the folder is large; it must meet the distinct-domain threshold. Do not treat `docs/` as a substitute.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: conditional docs-specific authoring/skip logic
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 12 | Blocked By: 3, 5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `READM/` directory listing — concentrated documentation subtree
  - Pattern: `READM/PROJECT_STRUCTURE.md:31-42` — docs inventory
  - Pattern: `docs/` directory listing — proves `docs/` is only a small setup-script folder, not the main docs hub
  - Pattern: `README.md:70-74` — doc navigation points into `READM/`

  **Acceptance Criteria** (agent-executable only):
  - [ ] If approved by scoring, `READM/AGENTS.md` exists and stays within 30-80 lines.
  - [ ] If not approved, `.sisyphus/evidence/task-11-readm-skip.txt` explains the skip and no file is created.
  - [ ] Outcome is consistent with the score table from Task 3.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path conditional docs outcome
    Tool: Bash
    Steps: Check Task 3 score output; either create/update `READM/AGENTS.md` or write a skip note; save verification to `.sisyphus/evidence/task-11-readm.txt`.
    Expected: The action taken matches the frozen scoring decision exactly.
    Evidence: .sisyphus/evidence/task-11-readm.txt

  Scenario: Failure/edge case inconsistent conditional branch
    Tool: Bash
    Steps: Validate that `READM/AGENTS.md` existence matches the score decision.
    Expected: Validation fails if the file exists after a skip decision or is missing after an approve decision.
    Evidence: .sisyphus/evidence/task-11-readm-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `READM/AGENTS.md`

- [ ] 12. Deduplicate parent/child guidance across the hierarchy

  **What to do**: Review the root and all child AGENTS files together, then trim repeated content so each child file only contains domain-specific instructions that are not already obvious from the parent. Preserve shared navigation at the root, specialized guidance in children.
  **Must NOT do**: Do not leave near-identical section blocks across multiple files; do not delete child-specific warnings just to reduce length.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: cross-file editorial review with hierarchy awareness
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 13, 14, 15 | Blocked By: 2, 6, 7, 8, 9, 10, 11

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `AGENTS.md` — parent guidance baseline
  - Pattern: `core/AGENTS.md`, `backend/AGENTS.md`, `ios_app/iOS_Video_Intelligence/AGENTS.md`, `READM/AGENTS.md` — child files to compare against parent
  - Pattern: `.sisyphus/evidence/task-5-child-matrix.md` — intended scope/omission matrix

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-12-dedup.txt` records the duplicate-review result for every generated AGENTS file.
  - [ ] No child file contains verbatim duplicated blocks longer than 15 lines or normalized duplicated text exceeding 30% of the child file.
  - [ ] Each child still retains at least one repo-specific guardrail unique to that subtree.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path hierarchy dedup
    Tool: Bash
    Steps: Compare root and child files for repeated blocks; trim duplicates; save final duplicate-check report.
    Expected: Duplicate review passes and each child still has unique domain guidance.
    Evidence: .sisyphus/evidence/task-12-dedup.txt

  Scenario: Failure/edge case over-trimming
    Tool: Bash
    Steps: Validate that each child file still mentions its unique domain boundary after deduplication.
    Expected: Validation fails if dedup removes the child-specific purpose statement or domain warnings.
    Evidence: .sisyphus/evidence/task-12-dedup-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 13. Validate file existence, placement, and size limits

  **What to do**: Run a mechanical validation pass across all expected AGENTS files. Confirm root exists, mandatory child files exist, conditional files match the scoring decision, rejected paths remain absent, and line counts stay within the plan’s size ranges.
  **Must NOT do**: Do not rely on visual inspection; this must be command-driven and saved as evidence.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: deterministic post-generation validation
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 15 | Blocked By: 12

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `.sisyphus/evidence/task-3-scoring.json` — expected target list
  - Pattern: `AGENTS.md` and all approved child paths — actual generated outputs to validate

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-13-validation.json` records every expected path, existence state, line count, and pass/fail result.
  - [ ] Mandatory files pass existence and size checks.
  - [ ] Conditional file outcomes match Task 3 exactly.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path existence and size validation
    Tool: Bash
    Steps: Count lines for each approved AGENTS file and compare against expected ranges; save results to `.sisyphus/evidence/task-13-validation.json`.
    Expected: Every mandatory file exists and meets its size bound.
    Evidence: .sisyphus/evidence/task-13-validation.json

  Scenario: Failure/edge case missing or oversized file
    Tool: Bash
    Steps: Fail validation if any mandatory file is missing or any file breaches its line-count range.
    Expected: Validation produces a binary fail with the offending path listed.
    Evidence: .sisyphus/evidence/task-13-validation-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 14. Validate exclusions, sandbox preservation, and secret-safe content

  **What to do**: Run a final guardrail pass ensuring no AGENTS file was created in excluded directories, sandbox files were not overwritten unless explicitly in scope, and generated guidance contains no copied secrets or sensitive values.
  **Must NOT do**: Do not assume the hierarchy is safe because authoring completed; this is the explicit anti-regression pass.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: safety-oriented review across paths and content
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 15 | Blocked By: 12

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `.gitignore:1-35` — existing artifact/secret caveats
  - Pattern: `test/openclaw-workspace/AGENTS.md:1-18` — sandbox file that should not be treated as canonical rewrite target
  - Pattern: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-18` — sensitive values that must never appear in generated AGENTS files

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-14-guardrails.txt` confirms no AGENTS files exist in excluded artifact paths.
  - [ ] Evidence confirms `test/openclaw-workspace/AGENTS.md` was preserved unless the operator explicitly chose sandbox scope.
  - [ ] Evidence confirms no generated AGENTS file contains copied credential strings or `.env` values.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path guardrail validation
    Tool: Bash
    Steps: Search all generated AGENTS files for excluded placements and secret-pattern leakage; save results to `.sisyphus/evidence/task-14-guardrails.txt`.
    Expected: No excluded-path AGENTS files exist and no sensitive values are present.
    Evidence: .sisyphus/evidence/task-14-guardrails.txt

  Scenario: Failure/edge case sandbox or secret regression
    Tool: Bash
    Steps: Fail validation if a new AGENTS file appears under an excluded directory or if a known credential string/value is present in generated content.
    Expected: Validation clearly identifies the violating path or leaked value.
    Evidence: .sisyphus/evidence/task-14-guardrails-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

- [ ] 15. Assemble the final hierarchy report and execution summary

  **What to do**: Produce the final report that mirrors the command’s requested output: mode, analyzed directories, created vs updated file counts, final hierarchy tree, and any conditional skips. Include links to the evidence files so the result is auditable.
  **Must NOT do**: Do not report success without attaching the validation outcomes from Tasks 13 and 14.

  **Recommended Agent Profile**:
  - Category: `writing` — Reason: final structured handoff summary with evidence linkage
  - Skills: `[]` — no specialized skill required
  - Omitted: `[git-master]` — no git operation required

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: none | Blocked By: 12, 13, 14

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `.sisyphus/evidence/task-3-scoring.json` — final hierarchy basis
  - Pattern: `.sisyphus/evidence/task-13-validation.json` — existence/size validation
  - Pattern: `.sisyphus/evidence/task-14-guardrails.txt` — safety/exclusion validation

  **Acceptance Criteria** (agent-executable only):
  - [ ] `.sisyphus/evidence/task-15-final-report.md` includes mode, analyzed directory count, created/updated AGENTS counts, final hierarchy tree, and conditional skip decisions.
  - [ ] The report links back to the scoring and validation evidence files.
  - [ ] The report can be pasted directly into a completion message for `/init-deep`.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Happy path final report
    Tool: Bash
    Steps: Read the scoring and validation evidence, assemble the final report, and save it to `.sisyphus/evidence/task-15-final-report.md`.
    Expected: Report matches the actual generated hierarchy and references the validation evidence.
    Evidence: .sisyphus/evidence/task-15-final-report.md

  Scenario: Failure/edge case unsupported success claim
    Tool: Bash
    Steps: Validate that the final report is not emitted if Tasks 13 or 14 failed.
    Expected: Report generation halts or marks the run failed when validation evidence is missing or failing.
    Evidence: .sisyphus/evidence/task-15-final-report-error.txt
  ```

  **Commit**: NO | Message: `docs(agents): initialize hierarchical workspace guidance` | Files: `AGENTS.md`, `**/AGENTS.md`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Do not create a git commit unless the user explicitly asks for one.
- If a commit is later requested, use atomic commits in this order: (1) discovery/scoring validation harness, (2) authoring/update-mode behavior, (3) generated AGENTS hierarchy, (4) review/evidence fixes.
- If the user prefers a single commit instead, squash those logical phases into one docs-style commit only after Tasks 13 and 14 pass.
- Suggested final message: `docs(agents): initialize hierarchical workspace guidance`

## Success Criteria
- Agents can navigate the repo using the new hierarchy without consulting stale READMEs first.
- Child instructions map cleanly to real responsibility boundaries: processing core, backend API, iOS app, and optional docs, while `test/` stays intentionally root-covered.
- Artifact-heavy folders are excluded from both scoring and generation.
- Generated guidance is concise, repo-specific, and free of duplicated parent text.
