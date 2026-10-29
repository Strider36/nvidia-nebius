# Aegis AI — Product Requirements Document (PRD)

**Document Version:** 0.4.0  
**Status:** Approved / Active Baseline  
**Date:** 2026-10-29  
**System Name:** Aegis AI Operator  

---

## 1. Product Vision & Target Users

### 1.1 Vision
Aegis AI is a private, security-first personal AI assistant and autonomous coding operator designed for software engineers, security researchers, and systems developers. It combines the seamless, distraction-free conversational experience of modern conversational AI (inspired by ChatGPT) with absolute data sovereignty, persistent contextual memory, and a sandboxed human-in-the-loop execution engine.

### 1.2 Target Users
- **Privacy-Conscious Developers**: Engineers working on proprietary codebases or sensitive intellectual property who require zero data leakage to cloud servers.
- **Full-Stack & Systems Engineers**: Developers requiring an assistant capable of reviewing code, planning multi-phase architectures, generating unit tests, and proposing concrete file patches without risk of unauthorized execution.
- **AI Operators**: Users who switch between local GPU acceleration (via Ollama and NVIDIA Nemotron 3.5 Bolt) and high-throughput cloud models (Nebius Token Factory / OpenRouter) based on connectivity, hardware availability, and workload complexity.

---

## 2. Problem Statement

1. **Cloud Data Leakage Risk**: Traditional cloud AI assistants transmit raw proprietary code, environment secrets, and intellectual property across third-party networks, violating strict corporate governance and compliance mandates.
2. **Uncontrolled Agent Execution**: Fully autonomous agents that write directly to the host filesystem or execute arbitrary shell commands pose severe risks of data loss, configuration corruption, or remote code execution.
3. **Disjointed Developer Response Experience**: Many local LLM interfaces suffer from broken Markdown rendering, lack of syntax highlighting, missing language tags, unformatted tables, unreadable code diffs, and lack of one-click copy and cancellation actions.
4. **Context Amnesia**: Standard LLM chats lose context between sessions, requiring developers to repeatedly restate environment details, architectural constraints, and personal workflow preferences.

---

## 3. High-Level System Architecture

Aegis AI operates as a self-contained local web application:
- **Frontend**: Obsidian-dark single-page application served directly from FastAPI, featuring a ChatGPT-inspired centered reading column, collapsible history sidebar, zero-dependency tokenizing syntax highlighter, clipboard management, and an `AbortController` cancellation engine.
- **Backend Service**: Asynchronous Python FastAPI application exposing REST APIs for provider switching, health probes, conversation management, approval tracking, workspace interaction, and audit logging.
- **Inference Layer**: Dual-provider architecture supporting:
  - **Local**: Ollama HTTP API (`http://127.0.0.1:11434`) running NVIDIA Nemotron 3.5 Bolt E4B.
  - **Cloud**: OpenAI-compatible client connecting to Nebius Token Factory or OpenRouter.
- **Storage Layer**: Embedded SQLite database (`aegis.db`) storing semantic memory, conversation sessions, human approvals, and an immutable audit log.
- **Workspace Jail**: Sandboxed workspace directory (`./workspace`) enforcing path traversal prevention, pre-modification backups (`.aegis_backups`), and human approval gates.

---

## 4. Functional Requirements

### 4.1 Response Rendering & Markdown Engine
- **FR-1.1 Headings & Typography**: Render `#`, `##`, `###` headings with proportional typography, distinct margins, and comfortable line heights.
- **FR-1.2 Lists**: Support ordered, unordered, and arbitrary nested lists with clean bullet hierarchies and proper indentation.
- **FR-1.3 Tables**: Render standard GitHub Flavored Markdown tables with column alignments (`:---`, `:---:`, `---:`) enclosed in horizontal overflow wrappers preventing layout breakage.
- **FR-1.4 Inline Formatting**: Support bold (`**text**`), italic (`*text*`), strikethrough (`~~text~~`), inline code (`` `code` ``), and blockquotes (`> text`).
- **FR-1.5 XSS Sanitization**: Strip or escape arbitrary `<script>`, `<iframe>`, and `object` tags. Strictly allow only `http://`, `https://`, and `mailto:` protocols on hyperlinks while blocking `javascript:` and `data:` schemes.

### 4.2 Multi-Language Syntax Highlighting
- **FR-2.1 Supported Languages**: Native tokenizer without external CDN dependencies supporting Python, JavaScript, TypeScript, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, and Markdown.
- **FR-2.2 Code Block Chrome**: Header bar displaying detected language badge, monospace code canvas, horizontal scrolling for long lines, and a dedicated copy button.
- **FR-2.3 Fallback Grace**: Cleanly format unknown languages or untagged code blocks without breaking formatting or throwing exceptions.
- **FR-2.4 Unclosed Code Blocks**: Gracefully handle incomplete or streaming code blocks without destroying trailing document structure.

### 4.3 Message Lifecycle & Assistant Actions
- **FR-3.1 Copy Response**: Provide a one-click copy button on every assistant message that copies raw plain-text content to the system clipboard with toast feedback.
- **FR-3.2 Copy Code Block**: Independent copy buttons for each code block that copy exact, unescaped source code with visual checkmark confirmation.
- **FR-3.3 Idempotent Retry**: Re-send the last user prompt without duplicating conversation history or mutating message IDs.
- **FR-3.4 Request Cancellation**: Real client-side cancellation via `AbortController` bound to the `#btnStop` button and the `Escape` key, restoring composer state immediately.

### 4.4 Dual-Provider Inference & Isolation
- **FR-4.1 Runtime Provider Switching**: Switch between Local (Ollama) and Cloud (Nebius/OpenRouter) dynamically via UI toggle or `POST /api/provider` without restarting the server.
- **FR-4.2 Anti-Fallback Invariant**: Strictly forbid silent fallback from local to cloud. If local Ollama is offline or times out, return an explicit error and stop.
- **FR-4.3 Request-Level Isolation**: Snapshot the active provider at the start of each request to eliminate race conditions during concurrent multi-turn interactions.
- **FR-4.4 Error Sanitization**: Detect missing models (HTTP 404), daemon unreachability, and cloud authentication errors, returning actionable remediation steps.

### 4.5 Human-in-the-Loop Developer Tools & Security
- **FR-5.1 Propose Patches**: Parse `<<<PROPOSE_PATCH>>>` tags from LLM responses, generate unified diffs, compute conflict detection, and require manual user approval.
- **FR-5.2 Propose Commands**: Parse `<<<PROPOSE_COMMAND>>>` tags, validate against strict allowlisted test runner commands (`pytest`, `unittest`, `npm test`), and require user approval.
- **FR-5.3 Automatic Backups**: Create timestamped rollback copies in `.aegis_backups/` before applying any approved file patch.
- **FR-5.4 Workspace Sandboxing**: Confine all file reads and writes to `./workspace`, rejecting path traversal attempts (`../`) and forbidden files (`.env`, `.git`).

### 4.6 Persistent Memory & Project Backlog
- **FR-6.1 Semantic SQLite Memory**: Store facts, user preferences, and project context in SQLite. Automatically inject top keyword-indexed memories into prompt context.
- **FR-6.2 Secret Shield**: Filter out passwords, API keys, and sensitive tokens at the memory gateway before saving to database.
- **FR-6.3 Project & Task Tracking**: Organize development efforts into projects with backlog task states (`pending`, `in_progress`, `completed`).

---

## 5. Nonfunctional Requirements

- **NFR-1 Latency & Performance**: Client-side Markdown parsing and syntax highlighting must complete in under 16ms for responses up to 50,000 characters to prevent frame drops.
- **NFR-2 Memory Footprint**: Frontend memory footprint must remain under 50MB even with 100+ conversation turns loaded.
- **NFR-3 Browser Compatibility**: Support modern evergreen browsers: Google Chrome 110+, Mozilla Firefox 115+, Microsoft Edge 110+, Apple Safari 16+.
- **NFR-4 Accessibility**: Support keyboard navigation (Tab, Enter, Escape, `Ctrl+[`), ARIA labels on all icon-only buttons, high-contrast dark palette, and `prefers-reduced-motion` compliance.
- **NFR-5 Security Compliance**: Zero third-party tracker scripts, zero CDN script injections, zero external telemetry, and complete redaction of API keys in logs and health endpoints.

---

## 6. AI Provider Behavior Specification

| Provider | Target Endpoint | Target Model | Intended Workload | Failure Behavior |
|---|---|---|---|---|
| **Local (Ollama)** | `http://127.0.0.1:11434` | `nemotron-3.5-bolt:e4b` | Proprietary code, confidential data, offline development | Hard fail with connection error; zero cloud leakage |
| **Cloud (Nebius / OpenRouter)** | `https://openrouter.ai/api/v1` | `nvidia/nemotron-3-nano-30b-a3b` | Large context tasks, complex planning, remote development | Return API error or quota alert; no local fallback |

---

## 7. User Journeys

### Journey 1: Developing with Local Privacy
1. Developer opens Aegis AI at `http://127.0.0.1:8000`.
2. Developer checks the top bar: the provider toggle is set to **Local (Ollama)** with a green connectivity dot showing `nemotron-3.5-bolt:e4b`.
3. Developer inputs a prompt: `"Refactor the user authentication router to add rate limiting."`
4. Assistant responds with formatted Markdown, explanatory text, and a syntax-highlighted Python block.
5. Developer clicks the copy button on the code block to copy the implementation into their IDE.
6. The assistant proposes a patch: a human approval card appears showing a unified diff.
7. Developer reviews the diff and clicks **Approve**. Aegis backups the original file and applies the change.

### Journey 2: Request Cancellation on Long Output
1. Developer sends a prompt requesting a large test suite.
2. The model begins generating. The composer switches to the generating state, displaying the glowing stop button (`⏹️`).
3. Developer realizes they made a typo in their prompt and presses `Escape` or clicks the Stop button.
4. The client halts the HTTP connection immediately, displays a cancellation notice, and re-enables the composer without duplicating messages or corrupting session history.

---

## 8. Acceptance Criteria

- [x] Full GFM Markdown rendering including nested lists, tables, quotes, headings, and inline formatting.
- [x] Zero-dependency syntax highlighting for 12+ major languages.
- [x] One-click copy for complete responses and individual code blocks with toast notifications.
- [x] Client-side cancellation via `#btnStop` and `Escape` key without backend or session corruption.
- [x] Strict dual-provider switching with zero silent fallback.
- [x] Sandboxed workspace modifications backed by automated rollback copies.
- [x] Human approval lifecycle enforced for all patch applications and command runs.
- [x] 100% test pass rate across both Python pytest suite and Node.js frontend renderer suite.

---

## 9. Current Release Scope & Future Roadmap

### In Scope (v0.4.0 — Delivered)
- Complete ChatGPT-inspired obsidian dark response UI.
- Multi-language syntax highlighting engine with dark theme tokens.
- Safe Markdown sanitizer blocking XSS and invalid URLs.
- Message actions: copy response, copy code, retry prompt, stop generation.
- Responsive table overflow wrappers and nested list hierarchies.
- 56 automated tests verifying backend and frontend invariants.
- Comprehensive six-core project documentation suite.

### Future Roadmap (v0.5.0+)
- **Server-Sent Events (SSE) Streaming**: Native incremental token streaming from Ollama and cloud providers without breaking non-streaming fallback.
- **Tree-sitter Syntax Highlighting**: Optional WebAssembly-based AST highlighting for deeper semantic colorization.
- **Multi-File Workspace Diffs**: Interactive multi-tab diff viewer for large refactorings touching dozens of files.
- **Offline Embeddings Vector Search**: Local SQLite-vec integration for dense retrieval in place of keyword-based memory matching.
