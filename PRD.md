# Aegis AI — Product Requirements Document (PRD)

**Document Version:** 0.8.0  
**Status:** Approved / Active Baseline  
**Date:** 2026-10-30  
**System Name:** Aegis AI Operator  

---

## 1. Product Vision & Target Users

### 1.1 Vision
Aegis AI is a private, security-first personal AI assistant and autonomous coding operator designed for software engineers, security researchers, and systems developers. It combines the distraction-free conversational experience of modern conversational AI with a unified **Obsidian, Graphite, Platinum, and Electric Violet** design system across all 7 application views (Main Chat, Skills, Memory, Approvals, Workspace, Audit, Settings), absolute data sovereignty, persistent contextual memory, pluggable agent backends (Native Aegis and Hermes Agent), and a sandboxed human-in-the-loop execution engine.

---

## 2. Problem Statement

1. **Fragmented Application Views**: Disconnected modal dialogs and inconsistent styling across peripheral tools (Skills, Memory, Approvals, Workspace, Audit, Settings) erode developer focus and perceived software quality.
2. **Cloud Data Leakage Risk**: Traditional cloud AI assistants transmit raw proprietary code, environment secrets, and intellectual property across third-party networks, violating strict corporate governance.
3. **Uncontrolled Agent Execution**: Fully autonomous agents that write directly to the host filesystem or execute arbitrary shell commands pose severe risks of data loss or remote code execution.
4. **Context Amnesia**: Standard LLM chats lose context between sessions, requiring developers to repeatedly restate environment details, architectural constraints, and personal workflow preferences.
5. **Backend Inflexibility**: Rigid single-engine architectures prevent developers from exploring specialized external agent runtimes without sacrificing workspace isolation or audit trails.

---

## 3. High-Level System Architecture

Aegis AI operates as a self-contained local web application:
- **Frontend**: Obsidian-dark single-page application served directly from FastAPI, featuring a centered 48rem reading column, collapsible history sidebar, zero-dependency tokenizing syntax highlighter, clipboard management, an `AbortController` cancellation engine, a cohesive physics-based motion system, topbar Agent Mode switcher (`#agentModeSwitcher`), and unified components reused across all 7 views.
- **Backend Service**: Asynchronous Python FastAPI application exposing REST APIs for agent backend routing, provider switching, health probes, conversation management, approval tracking, workspace interaction, and audit logging.
- **Agent Reasoning Backends**:
  - **Native Aegis**: Internal prompt synthesizer, skill director, and direct model API client.
  - **Hermes Agent Subprocess Adapter**: Sandboxed subprocess runner (`hermes.exe chat`) decoding streaming JSONL tokens, tied to the active inference provider with tools disabled (`--toolsets ""`).
- **Inference Layer**: Dual-provider architecture supporting:
  - **Local**: Ollama HTTP API (`http://127.0.0.1:11434`) running NVIDIA Nemotron 3.5 Bolt E4B.
  - **Cloud**: OpenAI-compatible client connecting to Nebius Token Factory or OpenRouter.
- **Storage Layer**: Embedded SQLite database (`aegis.db`) storing semantic memory, conversation sessions, human approvals, and an immutable audit log.
- **Workspace Jail**: Sandboxed workspace directory (`./workspace`) enforcing path traversal prevention, pre-modification backups (`.aegis_backups`), and human approval gates.

---

## 4. Unified Design System & Component Architecture (v0.7.0)

### 4.1 Color System & Surface Tokens
Centralized in `frontend/styles.css` `:root`:
- **Main Canvas (`--bg-primary`)**: `#0B0C0F` (Obsidian deep black)
- **Sidebar (`--bg-sidebar`)**: `#101116` (Graphite dark panel)
- **Secondary Surfaces (`--bg-secondary`)**: `#15171D` (Composer, cards, nav items, table headers)
- **Elevated Surfaces (`--bg-elevated`)**: `#1B1D25` (Modals, popovers, active pills)
- **Subtle Borders (`--border-subtle`)**: `#292B32` (Hairline boundary)
- **Active Borders (`--border-active`)**: `#3D414D` (Interactive focus border)
- **Primary Text (`--text-primary`)**: `#E6E4EC` (Platinum high contrast, WCAG AAA)
- **Secondary Text (`--text-secondary`)**: `#A2A2AF` (Slate secondary, WCAG AA)
- **Muted Text (`--text-muted`)**: `#777986` (Slate muted captions, WCAG AA)
- **Primary Accent (`--accent-primary`)**: `#A78BFA` (Electric Violet base)
- **Accent Hover (`--accent-hover`)**: `#B9A5FF` (Bright electric violet)
- **Accent Subtle (`--accent-subtle`)**: `rgba(167, 139, 250, 0.12)`
- **Accent Glow (`--accent-glow`)**: `rgba(167, 139, 250, 0.28)`
- **Success (`--color-success`)**: `#62C9A0` (Sage Mint)
- **Warning (`--color-warning`)**: `#E7B96A` (Warm Amber)
- **Error (`--color-error`)**: `#F07878` (Coral Rose)

### 4.2 Typography & Spacing Scale
- **Scale**: `--font-size-2xs` (0.68rem) to `--font-size-2xl` (1.60rem) with proportional line heights.
- **Spacing**: `--space-3xs` (2px) to `--space-2xl` (32px) standardizing all padding and margins.
- **Elevations**: `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-popover`.

### 4.3 Shared Components Across All 7 Views
- **Buttons**: `.btn-primary` (Electric violet gradient), `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-danger`, `.btn-close` (accessible 28x28 geometric SVG button).
- **Cards**: `.panel-card`, `.list-item-card`, `.memory-card`, `.skill-catalog-card`, `.approval-item-card`. Card-in-card nesting is strictly forbidden.
- **Status Indicators**: `.status-pill` with pulsing state dot (`.ready`, `.pending`, `.warning`, `.rejected`).
- **Data Tables**: `.data-table` / `.audit-table` with sticky header, monospace timestamps (`.mono-time`), and alternating row contrast.
- **Empty States**: `.empty-state` with centered geometric SVG icon, headline, and call to action.
- **Settings Inspector**: `#modalSettings` dedicated dialog for runtime provider, model IDs, network loopback binding (`127.0.0.1:8000`), SQLite engine, and connectivity diagnostics.

---

## 5. Functional Requirements

### 5.1 Response Rendering & Markdown Engine
- **FR-1.1 Headings & Typography**: Render `#`, `##`, `###` headings with proportional typography, distinct margins, and comfortable line heights.
- **FR-1.2 Lists**: Support ordered, unordered, and arbitrary nested lists with clean bullet hierarchies and proper indentation.
- **FR-1.3 Tables**: Render standard GitHub Flavored Markdown tables with column alignments (`:---`, `:---:`, `---:`) enclosed in horizontal overflow wrappers preventing layout breakage.
- **FR-1.4 Inline Formatting**: Support bold (`**text**`), italic (`*text*`), strikethrough (`~~text~~`), inline code (`` `code` ``), and blockquotes (`> text`).
- **FR-1.5 XSS Sanitization**: Strip or escape arbitrary `<script>`, `<iframe>`, and `object` tags. Strictly allow only `http://`, `https://`, and `mailto:` protocols on hyperlinks while blocking `javascript:` and `data:` schemes.

### 5.2 Multi-Language Syntax Highlighting
- **FR-2.1 Supported Languages**: Native tokenizer without external CDN dependencies supporting Python, JavaScript, TypeScript, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, and Markdown.
- **FR-2.2 Code Block Chrome**: Header bar displaying detected language badge, monospace code canvas, horizontal scrolling for long lines, and a dedicated copy button.
- **FR-2.3 Fallback Grace**: Cleanly format unknown languages or untagged code blocks without breaking formatting or throwing exceptions.
- **FR-2.4 Unclosed Code Blocks**: Gracefully handle incomplete or streaming code blocks without destroying trailing document structure.

### 5.3 Message Lifecycle & Assistant Actions
- **FR-3.1 Copy Response**: Provide a one-click copy button on every assistant message that copies raw plain-text content to the system clipboard with toast feedback.
- **FR-3.2 Copy Code Block**: Independent copy buttons for each code block that copy exact, unescaped source code with visual checkmark confirmation.
- **FR-3.3 Idempotent Retry**: Re-send the last user prompt without duplicating conversation history or mutating message IDs.
- **FR-3.4 Request Cancellation**: Real client-side cancellation via `AbortController` bound to the `#btnStop` button and the `Escape` key, restoring composer state immediately.

### 5.4 Dual-Provider Inference & Isolation
- **FR-4.1 Runtime Provider Switching**: Switch between Local (Ollama) and Cloud (Nebius/OpenRouter) dynamically via UI toggle or `POST /api/provider` without restarting the server.
- **FR-4.2 Anti-Fallback Invariant**: Strictly forbid silent fallback from local to cloud. If local Ollama is offline or times out, return an explicit error and stop.
- **FR-4.3 Request-Level Isolation**: Snapshot the active provider at the start of each request to eliminate race conditions during concurrent multi-turn interactions.
- **FR-4.4 Error Sanitization**: Detect missing models (HTTP 404), daemon unreachability, and cloud authentication errors, returning actionable remediation steps.

### 5.5 Human-in-the-Loop Developer Tools & Security
- **FR-5.1 Propose Patches**: Parse `<<<PROPOSE_PATCH>>>` tags from LLM responses, generate unified diffs, compute conflict detection, and require manual user approval.
- **FR-5.2 Propose Commands**: Parse `<<<PROPOSE_COMMAND>>>` tags, validate against strict allowlisted test runner commands (`pytest`, `unittest`, `npm test`), and require user approval.
- **FR-5.3 Automatic Backups**: Create timestamped rollback copies in `.aegis_backups/` before applying any approved file patch.
- **FR-5.4 Workspace Sandboxing**: Confine all file reads and writes to `./workspace`, rejecting path traversal attempts (`../`) and forbidden files (`.env`, `.git`).
### 5.6 Persistent Memory & Project Backlog
- **FR-6.1 Semantic SQLite Memory**: Store facts, user preferences, and project context in SQLite. Automatically inject top keyword-indexed memories into prompt context.
- **FR-6.2 Secret Shield**: Filter out passwords, API keys, and sensitive tokens at the memory gateway before saving to database.
- **FR-6.3 Project & Task Tracking**: Organize development efforts into projects with backlog task states (`pending`, `in_progress`, `completed`).

### 5.7 Pluggable Agent Backend & Hermes Integration
- **FR-7.1 Backend Selection**: Dynamic per-request selection between Native Aegis and Hermes Agent via `agent_backend: "aegis" | "hermes"` in `POST /api/chat` and `POST /api/chat/stream`. Topbar switcher persists user preference in `localStorage`.
- **FR-7.2 Subprocess Invocation**: Hermes CLI (`hermes.exe chat --query-file ... --format stream-json --oneshot`) executed via isolated subprocess using temporary prompt files with clean teardown.
- **FR-7.3 Workspace Sandboxing**: Hermes execution locked strictly to the workspace root (`--in <workspace_path>`) with unsupervised internal tools suppressed (`--toolsets ""`).
- **FR-7.4 JSONL Streaming**: Decode Hermes JSONL stdout events (`{"type": "text", "text": "..."}`) into real-time SSE tokens on `/api/chat/stream`.
- **FR-7.5 Human Approval Extraction**: Parse `<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>`, and `<<<PROPOSE_TASK>>>` emitted by Hermes and route into SQLite `pending_approvals`.
- **FR-7.6 Anti-Fallback Guarantee**: Local Ollama timeouts or failures when running Hermes strictly fail with HTTP 503/502; silent cloud failover is prohibited.
- **FR-7.7 Diagnostic Probing**: `GET /api/hermes/status` exposes binary location, version string, availability, and active provider readiness.

---

## 6. Nonfunctional Requirements

- **NFR-1 Latency & Performance**: Client-side Markdown parsing and syntax highlighting must complete in under 16ms for responses up to 50,000 characters.
- **NFR-2 Memory Footprint**: Frontend memory footprint must remain under 50MB with 100+ conversation turns loaded.
- **NFR-3 Browser Compatibility**: Support evergreen browsers: Chrome 110+, Firefox 115+, Edge 110+, Safari 16+.
- **NFR-4 Accessibility & Contrast**: WCAG AA/AAA compliant contrast on all text surfaces; ARIA labels on icon buttons; keyboard focus indicators with Electric Violet glow ring; `prefers-reduced-motion` compliance.
- **NFR-5 Security & Privacy**: Zero third-party trackers, zero CDN script injections, zero external telemetry, complete redaction of API keys in logs and health probes.

---

## 7. AI Provider Behavior Specification

| Provider | Target Endpoint | Target Model | Intended Workload | Failure Behavior |
|---|---|---|---|---|
| **Local (Ollama)** | `http://127.0.0.1:11434` | `nemotron-3.5-bolt:e4b` | Proprietary code, confidential data, offline development | Hard fail with connection error; zero cloud leakage |
| **Cloud (Nebius / OpenRouter)** | `https://openrouter.ai/api/v1` | `nvidia/nemotron-3-nano-30b-a3b` | Large context tasks, complex planning, remote development | Return API error or quota alert; no local fallback |

---

## 8. Current Release Scope & Roadmap

### In Scope (v0.8.0 — Delivered)
- **Hermes Agent Optional Backend Integration**:
  - Subprocess adapter (`HermesService`) wrapping local Hermes CLI (`C:\Users\jayan\AppData\Local\hermes\bin\hermes.exe` v0.22.5).
  - Compatible with local NVIDIA Nemotron via Ollama (`http://127.0.0.1:11434/v1`) and Cloud provider.
  - Subprocess sandboxed inside `./workspace` (`--in <workspace_path>`) with tools disabled (`--toolsets ""`).
  - Full human approval preservation for patches, commands, and tasks.
  - JSONL streaming token decoder integrated with native SSE (`/api/chat/stream`).
  - Anti-fallback invariant strictly maintained: local Ollama failures never failover to cloud.
  - Frontend Agent Mode switcher in topbar and Hermes status card in Settings modal.
  - Status & diagnostic endpoint `GET /api/hermes/status`.
- **Unified Design System Across All 7 Views (v0.7.0)**:
  - Main Chat, Skills, Memory, Approvals, Workspace, Audit, and Settings share 100% of tokens and interaction patterns.
  - Mathematical typography scale (`--font-size-*`) and spacing scale (`--space-*`).
  - Pure geometric SVG close icon buttons (`aria-label="Close modal"`).
  - Dedicated Settings & Provider Diagnostics dialog (`#modalSettings`).
- **Native Server-Sent Events (SSE) Token Streaming (v0.6.0)**:
  - `POST /api/chat/stream` delivering real-time chunked tokens.
  - Blinking streaming cursor (`.streaming-cursor`) with smooth completion transition to formatted Markdown.
  - Viewport auto-scroll lock.
- **76 automated tests** (65 Python + 11 JavaScript) with 100% pass rate.
- Complete synchronized documentation suite across all 7 core markdown files.

### Future Roadmap (v0.9.0+)
- **Tree-sitter Syntax Highlighting**: Optional WebAssembly-based AST highlighting for deeper semantic colorization.
- **Multi-File Workspace Diffs**: Interactive multi-tab diff viewer for large refactorings touching dozens of files.
- **Offline Embeddings Vector Search**: Local SQLite-vec integration for dense retrieval in place of keyword-based memory matching.
