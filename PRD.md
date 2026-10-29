# Aegis AI — Product Requirements Document (PRD)

**Document Version:** 0.6.0  
**Status:** Approved / Active Baseline  
**Date:** 2026-10-30  
**System Name:** Aegis AI Operator  

---

## 1. Product Vision & Target Users

### 1.1 Vision
Aegis AI is a private, security-first personal AI assistant and autonomous coding operator designed for software engineers, security researchers, and systems developers. It combines the distraction-free conversational experience of modern conversational AI with a distinctive **Obsidian, Graphite, Platinum, and Electric Violet** design identity, absolute data sovereignty, persistent contextual memory, and a sandboxed human-in-the-loop execution engine.

### 1.2 Target Users
- **Privacy-Conscious Developers**: Engineers working on proprietary codebases or sensitive intellectual property who require zero data leakage to cloud servers.
- **Full-Stack & Systems Engineers**: Developers requiring an assistant capable of reviewing code, planning multi-phase architectures, generating unit tests, and proposing concrete file patches without risk of unauthorized execution.
- **AI Operators**: Users who switch between local GPU acceleration (via Ollama and NVIDIA Nemotron 3.5 Bolt) and high-throughput cloud models (Nebius Token Factory / OpenRouter) based on connectivity, hardware availability, and workload complexity.

---

## 2. Problem Statement

1. **Generic AI-Dashboard Aesthetic**: Many developer tools rely on generic card-heavy layouts, low-contrast palettes, and platform-dependent emojis that degrade perceived tool quality.
2. **Cloud Data Leakage Risk**: Traditional cloud AI assistants transmit raw proprietary code, environment secrets, and intellectual property across third-party networks, violating strict corporate governance.
3. **Uncontrolled Agent Execution**: Fully autonomous agents that write directly to the host filesystem or execute arbitrary shell commands pose severe risks of data loss or remote code execution.
4. **Context Amnesia**: Standard LLM chats lose context between sessions, requiring developers to repeatedly restate environment details, architectural constraints, and personal workflow preferences.

---

## 3. High-Level System Architecture

Aegis AI operates as a self-contained local web application:
- **Frontend**: Obsidian-dark single-page application served directly from FastAPI, featuring a centered 48rem reading column, collapsible history sidebar, zero-dependency tokenizing syntax highlighter, clipboard management, an `AbortController` cancellation engine, and a cohesive physics-based motion system.
- **Backend Service**: Asynchronous Python FastAPI application exposing REST APIs for provider switching, health probes, conversation management, approval tracking, workspace interaction, and audit logging.
- **Inference Layer**: Dual-provider architecture supporting:
  - **Local**: Ollama HTTP API (`http://127.0.0.1:11434`) running NVIDIA Nemotron 3.5 Bolt E4B.
  - **Cloud**: OpenAI-compatible client connecting to Nebius Token Factory or OpenRouter.
- **Storage Layer**: Embedded SQLite database (`aegis.db`) storing semantic memory, conversation sessions, human approvals, and an immutable audit log.
- **Workspace Jail**: Sandboxed workspace directory (`./workspace`) enforcing path traversal prevention, pre-modification backups (`.aegis_backups`), and human approval gates.

---

## 4. Distinctive Design System & Motion Specification (v0.5.0)

### 4.1 Color System & Tokens
Centralized in `frontend/styles.css` `:root`:
- **Main Canvas (`--bg-primary`)**: `#0B0C0F` (Obsidian deep black)
- **Sidebar (`--bg-sidebar`)**: `#101116` (Graphite dark panel)
- **Secondary Surfaces (`--bg-secondary`)**: `#15171D` (Composer, cards, nav items)
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
- **Success (`--color-success`)**: `#62C9A0` (Sage / Mint)
- **Warning (`--color-warning`)**: `#E7B96A` (Warm Amber)
- **Error (`--color-error`)**: `#F07878` (Coral Rose)

### 4.2 Motion System Specification
- **Timing Tokens**:
  - `--ease-out`: `cubic-bezier(0.16, 1, 0.3, 1)`
  - `--ease-in-out`: `cubic-bezier(0.4, 0, 0.2, 1)`
  - `--duration-fast`: `150ms` (hover, active press, focus rings)
  - `--duration-normal`: `220ms` (toasts, cards, panels)
  - `--duration-slow`: `360ms` (welcome hero, modal entrances)
- **Interaction Rules**:
  - Buttons press down slightly on active (`transform: scale(0.98)`).
  - Welcome hero gently rises on load (`@keyframes heroEntrance`).
  - Suggestion chips stagger their entrance (`60ms`, `110ms`, `160ms`, `210ms`).
  - Full support for `@media (prefers-reduced-motion: reduce)` disabling non-essential motion.

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

### In Scope (v0.6.0 — Delivered)
- **Native Server-Sent Events (SSE) Token Streaming**:
  - `POST /api/chat/stream` delivering real-time chunked tokens.
  - Native streaming integration with local Ollama HTTP API (`stream: true`) and cloud OpenAI SDK (`stream=True`).
  - Zero silent fallback: strict provider isolation enforced on streaming failures.
  - Client-side incremental token renderer in `app.js` with `ReadableStream` reader and `TextDecoder`.
  - Realistic blinking streaming cursor (`.streaming-cursor`) with smooth completion transition to formatted Markdown.
  - Viewport auto-scroll lock: auto-scrolls when user is near the bottom (<=160px), preserves position when scrolled up.
  - Active stream cancellation: `#btnStop` and `Escape` key immediately abort stream and halt backend generator.
  - Automatic fallback: gracefully degrades to `/api/chat` if streaming endpoint is unavailable.
- Distinctive Obsidian, Graphite, Platinum, and Electric Violet design system.
- Cohesive physics-based motion system (`--ease-out`, `--duration-fast/normal/slow`).
- Clean bespoke geometric SVGs replacing all decorative emoji glyphs.
- Zero-dependency syntax highlighter for 12+ programming languages.
- Safe Markdown sanitizer blocking XSS and invalid URLs.
- Message actions: copy response, copy code, retry prompt, stop generation.
- Responsive table overflow wrappers and nested list hierarchies.
- 66 automated tests (55 Python + 11 JavaScript) with 100% pass rate.
- Complete synchronized documentation suite.

### Future Roadmap (v0.7.0+)
- **Tree-sitter Syntax Highlighting**: Optional WebAssembly-based AST highlighting for deeper semantic colorization.
- **Multi-File Workspace Diffs**: Interactive multi-tab diff viewer for large refactorings touching dozens of files.
- **Offline Embeddings Vector Search**: Local SQLite-vec integration for dense retrieval in place of keyword-based memory matching.
