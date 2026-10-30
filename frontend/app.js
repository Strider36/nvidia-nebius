/**
 * Aegis AI — Frontend Application Logic
 * Pure Vanilla JavaScript (Zero External Dependencies)
 * Clean, ChatGPT-inspired conversational interface with premium syntax highlighting.
 */

// Application State
const state = {
  activeConversationId: null,
  activeProjectId: null,
  activeSkillId: "",
  activeProvider: "ollama",
  activeAgentBackend: (typeof localStorage !== "undefined" && localStorage && localStorage.getItem) ? (localStorage.getItem("aegis_agent_backend") || "aegis") : "aegis",
  executionMode: (typeof localStorage !== "undefined" && localStorage && localStorage.getItem)
    ? (localStorage.getItem("aegis_execution_mode") || ((localStorage.getItem("aegis_agent_backend") || "aegis") === "hermes" ? "autonomous" : "supervised"))
    : "autonomous",
  health: null,
  providerStatus: null,
  projects: [],
  skills: [],
  pendingApprovals: [],
  allConversations: [],
  lastUserMessage: "",
};

let currentAbortController = null;

// DOM Elements
const dom = {
  appContainer: document.getElementById("appContainer"),
  sidebar: document.getElementById("sidebar"),
  sidebarBackdrop: document.getElementById("sidebarBackdrop"),
  btnToggleSidebar: document.getElementById("btnToggleSidebar"),
  btnMobileMenu: document.getElementById("btnMobileMenu"),
  systemStatusBadge: document.getElementById("systemStatusBadge"),
  systemStatusText: document.getElementById("systemStatusText"),
  sidebarModelId: document.getElementById("sidebarModelId"),
  btnBackendAegis: document.getElementById("btnBackendAegis"),
  btnBackendHermes: document.getElementById("btnBackendHermes"),
  btnModeAutonomous: document.getElementById("btnModeAutonomous"),
  btnModeSupervised: document.getElementById("btnModeSupervised"),
  btnProviderOllama: document.getElementById("btnProviderOllama"),
  btnProviderCloud: document.getElementById("btnProviderCloud"),
  dotProviderOllama: document.getElementById("dotProviderOllama"),
  dotProviderCloud: document.getElementById("dotProviderCloud"),
  topbarProviderTag: document.getElementById("topbarProviderTag"),
  btnNewSession: document.getElementById("btnNewSession"),
  conversationSearchInput: document.getElementById("conversationSearchInput"),
  btnClearSearch: document.getElementById("btnClearSearch"),
  projectSelector: document.getElementById("projectSelector"),
  btnOpenProjectsModal: document.getElementById("btnOpenProjectsModal"),
  conversationList: document.getElementById("conversationList"),
  activeSessionTitle: document.getElementById("activeSessionTitle"),
  btnRenameActiveSession: document.getElementById("btnRenameActiveSession"),
  activeProjectBadge: document.getElementById("activeProjectBadge"),
  activeSkillBadge: document.getElementById("activeSkillBadge"),
  topPendingBanner: document.getElementById("topPendingBanner"),
  topPendingText: document.getElementById("topPendingText"),
  btnQuickReview: document.getElementById("btnQuickReview"),
  btnRefreshStatus: document.getElementById("btnRefreshStatus"),
  messagesContainer: document.getElementById("messagesContainer"),
  welcomeHero: document.getElementById("welcomeHero"),
  pendingApprovalsPanel: document.getElementById("pendingApprovalsPanel"),
  pendingApprovalBody: document.getElementById("pendingApprovalBody"),
  btnCloseApprovalPanel: document.getElementById("btnCloseApprovalPanel"),
  chatForm: document.getElementById("chatForm"),
  messageInput: document.getElementById("messageInput"),
  btnSend: document.getElementById("btnSend"),
  btnStop: document.getElementById("btnStop"),
  toastContainer: document.getElementById("toastContainer"),
  pendingCountBadge: document.getElementById("pendingCountBadge"),
  // Modals
  modalProjects: document.getElementById("modalProjects"),
  modalMemory: document.getElementById("modalMemory"),
  modalSkills: document.getElementById("modalSkills"),
  modalApprovals: document.getElementById("modalApprovals"),
  modalWorkspace: document.getElementById("modalWorkspace"),
  modalAudit: document.getElementById("modalAudit"),
  modalSettings: document.getElementById("modalSettings"),
  btnOpenSettingsModal: document.getElementById("btnOpenSettingsModal"),
  btnTopbarSettings: document.getElementById("btnTopbarSettings"),
  btnRunDiagnostics: document.getElementById("btnRunDiagnostics"),
};

// Utilities
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " · " + d.toLocaleDateString();
  } catch (e) {
    return isoStr;
  }
}

function sanitizeUrl(url) {
  if (!url) return "#";
  const trimmed = url.trim();
  if (/^(https?:\/\/|mailto:|#|\/)/i.test(trimmed)) {
    return trimmed;
  }
  return "#";
}

// Toast Notification
function showToast(message, type = "success") {
  const container = dom.toastContainer || document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.25s";
    setTimeout(() => toast.remove(), 250);
  }, 2200);
}

// Non-destructive Clipboard Copy with Fallback
async function copyToClipboard(text, successMsg = "Copied to clipboard!") {
  if (!text) return false;
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      showToast(successMsg, "success");
      return true;
    }
  } catch (err) {
    // Fallback to execCommand
  }

  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    if (ok) {
      showToast(successMsg, "success");
      return true;
    }
  } catch (e) {}

  showToast("Failed to copy to clipboard", "error");
  return false;
}

// Group conversations by date: Today, Yesterday, Previous 7 Days, Older
function groupConversationsByDate(convs) {
  const groups = {
    today: [],
    yesterday: [],
    previous7Days: [],
    older: [],
  };

  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startOfYesterday = startOfToday - 86400000;
  const startOf7Days = startOfToday - 86400000 * 7;

  convs.forEach(c => {
    let t = 0;
    try {
      t = new Date(c.updated_at || c.created_at).getTime();
    } catch (e) {
      t = 0;
    }

    if (t >= startOfToday) {
      groups.today.push(c);
    } else if (t >= startOfYesterday) {
      groups.yesterday.push(c);
    } else if (t >= startOf7Days) {
      groups.previous7Days.push(c);
    } else {
      groups.older.push(c);
    }
  });

  return groups;
}

// ============================================================================
// Multi-Language Syntax Highlighting Engine (Pure, Offline, Zero-Dependency)
// ============================================================================
function highlightSyntax(code, lang) {
  if (!code) return "";
  const language = (lang || "").toLowerCase().trim();

  const langMap = {
    py: "python", python: "python",
    js: "javascript", javascript: "javascript",
    ts: "typescript", typescript: "typescript",
    java: "java",
    sql: "sql",
    json: "json",
    bash: "bash", sh: "bash", shell: "bash", zsh: "bash",
    ps1: "powershell", powershell: "powershell", ps: "powershell",
    html: "html", xml: "html",
    css: "css", scss: "css", less: "css",
    yaml: "yaml", yml: "yaml",
    md: "markdown", markdown: "markdown",
  };

  const targetLang = langMap[language] || "unknown";

  if (targetLang === "unknown") {
    return escapeHtml(code);
  }

  // Keywords definitions
  const keywords = {
    python: new Set([
      "def", "class", "import", "from", "return", "if", "elif", "else", "while",
      "for", "in", "try", "except", "finally", "with", "as", "lambda", "yield",
      "async", "await", "pass", "raise", "assert", "global", "nonlocal", "self",
      "cls", "is", "not", "and", "or"
    ]),
    javascript: new Set([
      "const", "let", "var", "function", "return", "if", "else", "for", "while",
      "do", "switch", "case", "break", "continue", "new", "this", "class",
      "extends", "super", "import", "export", "default", "from", "try", "catch",
      "finally", "throw", "async", "await", "typeof", "instanceof", "in", "of",
      "yield", "void", "delete"
    ]),
    typescript: new Set([
      "const", "let", "var", "function", "return", "if", "else", "for", "while",
      "do", "switch", "case", "break", "continue", "new", "this", "class",
      "extends", "super", "import", "export", "default", "from", "try", "catch",
      "finally", "throw", "async", "await", "typeof", "instanceof", "in", "of",
      "yield", "void", "delete", "interface", "type", "enum", "implements",
      "private", "public", "protected", "readonly", "declare", "namespace", "as", "any"
    ]),
    java: new Set([
      "public", "private", "protected", "class", "interface", "extends", "implements",
      "new", "this", "super", "return", "if", "else", "for", "while", "do",
      "switch", "case", "break", "continue", "try", "catch", "finally", "throw",
      "throws", "static", "final", "abstract", "void", "package", "import", "instanceof"
    ]),
    sql: new Set([
      "select", "from", "where", "insert", "into", "update", "delete", "create",
      "table", "drop", "alter", "join", "left", "right", "inner", "outer", "on",
      "group", "by", "order", "having", "limit", "offset", "as", "and", "or",
      "not", "in", "is", "null", "primary", "key", "foreign", "references",
      "default", "union", "distinct", "pragma", "values", "set", "index"
    ]),
    bash: new Set([
      "if", "then", "else", "elif", "fi", "for", "while", "do", "done", "case",
      "esac", "function", "return", "exit", "echo", "cd", "ls", "mkdir", "rm",
      "cp", "mv", "grep", "cat", "chmod", "chown", "curl", "export", "source", "sudo"
    ]),
    powershell: new Set([
      "function", "filter", "workflow", "param", "return", "if", "elseif", "else",
      "switch", "foreach", "for", "while", "do", "until", "break", "continue",
      "try", "catch", "finally", "throw", "trap", "exit"
    ]),
    css: new Set([
      "import", "media", "keyframes", "root", "hover", "focus", "active", "before", "after"
    ]),
  };

  const booleans = new Set([
    "true", "false", "null", "undefined", "none", "true", "false", "nan", "nil"
  ]);

  const types = new Set([
    "int", "str", "float", "bool", "list", "dict", "set", "tuple", "string",
    "number", "boolean", "any", "void", "object", "promise", "array", "record",
    "double", "char", "byte", "short", "long"
  ]);

  // JSON specialized tokenizer
  if (targetLang === "json") {
    return code.replace(
      /("(?:\\u[\dA-Fa-f]{4}|\\[^u]|[^\\"])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,
      (match, str, isKey, bool) => {
        if (str) {
          if (isKey) {
            return `<span class="tok-keyword">${escapeHtml(str)}</span>:`;
          }
          return `<span class="tok-string">${escapeHtml(str)}</span>`;
        }
        if (bool) {
          return `<span class="tok-boolean">${escapeHtml(match)}</span>`;
        }
        return `<span class="tok-number">${escapeHtml(match)}</span>`;
      }
    );
  }

  // HTML / XML specialized tokenizer
  if (targetLang === "html") {
    return code.replace(
      /(&lt;!--[\s\S]*?--&gt;)|(&lt;\/?[a-zA-Z0-9_-]+)|([a-zA-Z0-9_-]+)=("[^"]*"|'[^']*')|(&gt;|\/&gt;)/g,
      (match, comment, tag, attr, attrVal, closeTag) => {
        if (comment) return `<span class="tok-comment">${comment}</span>`;
        if (tag) return `<span class="tok-tag">${tag}</span>`;
        if (attr) return `<span class="tok-attr">${attr}</span>=<span class="tok-string">${attrVal}</span>`;
        if (closeTag) return `<span class="tok-tag">${closeTag}</span>`;
        return match;
      }
    );
  }

  // YAML specialized tokenizer
  if (targetLang === "yaml") {
    const lines = code.split("\n");
    return lines.map(line => {
      if (line.trim().startsWith("#")) {
        return `<span class="tok-comment">${escapeHtml(line)}</span>`;
      }
      return line.replace(/^(\s*[\w.-]+)(\s*:)(.*)$/, (m, key, colon, rest) => {
        let valHtml = escapeHtml(rest);
        valHtml = valHtml.replace(/(#.*$)/, '<span class="tok-comment">$1</span>');
        valHtml = valHtml.replace(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/, '<span class="tok-string">$1</span>');
        valHtml = valHtml.replace(/\b(true|false|null|yes|no)\b/gi, '<span class="tok-boolean">$1</span>');
        valHtml = valHtml.replace(/\b\d+(\.\d+)?\b/, '<span class="tok-number">$1</span>');
        return `<span class="tok-keyword">${escapeHtml(key)}</span>${colon}${valHtml}`;
      });
    }).join("\n");
  }

  // General token regex for Python, JS, TS, Java, SQL, Bash, PowerShell, CSS
  const commentRegex = (targetLang === "python" || targetLang === "bash" || targetLang === "powershell")
    ? /(?:#.*$)/m
    : (targetLang === "sql")
    ? /(?:--.*$|\/\*[\s\S]*?\*\/)/m
    : /(?:\/\/[^\n]*|\/\*[\s\S]*?\*\/)/m;

  const stringRegex = /(?:"""[\s\S]*?"""|'''[\s\S]*?'''|`[\s\S]*?`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/;
  const numberRegex = /\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b/;
  const wordRegex = /\b[a-zA-Z_$][a-zA-Z0-9_$]*\b/;

  let remaining = code;
  let result = "";

  while (remaining.length > 0) {
    const commentMatch = remaining.match(commentRegex);
    const stringMatch = remaining.match(stringRegex);
    const numberMatch = remaining.match(numberRegex);
    const wordMatch = remaining.match(wordRegex);

    let earliest = null;
    let type = "";

    const checkEarliest = (match, t) => {
      if (match && (earliest === null || match.index < earliest.index)) {
        earliest = match;
        type = t;
      }
    };

    checkEarliest(commentMatch, "comment");
    checkEarliest(stringMatch, "string");
    checkEarliest(numberMatch, "number");
    checkEarliest(wordMatch, "word");

    if (!earliest) {
      result += escapeHtml(remaining);
      break;
    }

    if (earliest.index > 0) {
      result += escapeHtml(remaining.substring(0, earliest.index));
    }

    const token = earliest[0];
    remaining = remaining.substring(earliest.index + token.length);

    if (type === "comment") {
      result += `<span class="tok-comment">${escapeHtml(token)}</span>`;
    } else if (type === "string") {
      result += `<span class="tok-string">${escapeHtml(token)}</span>`;
    } else if (type === "number") {
      result += `<span class="tok-number">${escapeHtml(token)}</span>`;
    } else if (type === "word") {
      const lower = token.toLowerCase();
      const kwSet = keywords[targetLang];
      if (kwSet && (kwSet.has(token) || (targetLang === "sql" && kwSet.has(lower)))) {
        result += `<span class="tok-keyword">${escapeHtml(token)}</span>`;
      } else if (booleans.has(lower)) {
        result += `<span class="tok-boolean">${escapeHtml(token)}</span>`;
      } else if (types.has(lower)) {
        result += `<span class="tok-type">${escapeHtml(token)}</span>`;
      } else if (remaining.trim().startsWith("(")) {
        result += `<span class="tok-function">${escapeHtml(token)}</span>`;
      } else {
        result += escapeHtml(token);
      }
    }
  }

  return result;
}

// Nested Lists Parser
function parseMarkdownLists(text) {
  const lines = text.split('\n');
  let inList = false;
  let listIndentStack = [];
  let outLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const ulMatch = line.match(/^(\s*)([-*•])\s+(.*)$/);
    const olMatch = line.match(/^(\s*)(\d+)\.\s+(.*)$/);

    if (ulMatch || olMatch) {
      const indent = (ulMatch || olMatch)[1].length;
      const isUl = !!ulMatch;
      const currentType = isUl ? 'ul' : 'ol';
      const content = (ulMatch || olMatch)[3];

      if (!inList) {
        inList = true;
        listIndentStack = [{ indent, type: currentType }];
        outLines.push(`<${currentType} class="msg-${currentType}"><li>${content}`);
      } else {
        const top = listIndentStack[listIndentStack.length - 1];
        if (indent > top.indent) {
          listIndentStack.push({ indent, type: currentType });
          outLines.push(`<${currentType} class="msg-${currentType}"><li>${content}`);
        } else if (indent < top.indent) {
          while (listIndentStack.length > 1 && indent < listIndentStack[listIndentStack.length - 1].indent) {
            const popped = listIndentStack.pop();
            outLines.push(`</li></${popped.type}>`);
          }
          outLines.push(`</li><li>${content}`);
        } else {
          outLines.push(`</li><li>${content}`);
        }
      }
    } else {
      if (inList) {
        while (listIndentStack.length > 0) {
          const popped = listIndentStack.pop();
          outLines.push(`</li></${popped.type}>`);
        }
        inList = false;
        listIndentStack = [];
      }
      outLines.push(line);
    }
  }

  if (inList) {
    while (listIndentStack.length > 0) {
      const popped = listIndentStack.pop();
      outLines.push(`</li></${popped.type}>`);
    }
  }

  return outLines.join('\n');
}

// Enhanced Markdown formatting helper with safe HTML escaping, syntax highlighting, and rich widgets
function renderSafeMarkdown(text) {
  if (!text) return "";

  // Normalize Windows CRLF line endings
  let raw = String(text).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  // 0. Safety catch: if any raw <<<PROPOSE_...>>> tags remain in text, convert to human-readable markdown
  raw = raw.replace(/<<<PROPOSE_TASK\s+([^>]+)>{3,4}/g, (match, attrs) => {
    const titleMatch = attrs.match(/title=["']([^"']+)["']/);
    const descMatch = attrs.match(/description=["']([^"']*)["']/);
    const dueMatch = attrs.match(/due_date=["']([^"']*)["']/);
    const title = titleMatch ? titleMatch[1] : "Proposed Task";
    const desc = descMatch ? descMatch[1] : "";
    const due = dueMatch ? dueMatch[1] : "";
    return `\n> 📋 **Milestone Task:** **${title}**${due ? ` (📅 Due: \`${due}\`)` : ""}${desc ? `\n> ${desc}` : ""}\n`;
  });

  raw = raw.replace(/<<<PROPOSE_COMMAND\s+([^>]+)>{3,4}/g, (match, attrs) => {
    const cmdMatch = attrs.match(/command=["']([^"']+)["']/);
    const cmd = cmdMatch ? cmdMatch[1] : "command";
    return `\n> ⚡ **Proposed Command:** \`${cmd}\`\n`;
  });

  raw = raw.replace(/<<<PROPOSE_PATCH\s+([^>]+)>\n?([\s\S]*?)\n?<\/PROPOSE_PATCH>{2,4}/g, (match, attrs, content) => {
    const pathMatch = attrs.match(/path=["']([^"']+)["']/);
    const path = pathMatch ? pathMatch[1] : "file";
    return `\n> 🛠️ **Proposed Patch:** \`${path}\`\n\`\`\`\n${content}\n\`\`\`\n`;
  });

  // 1. Extract and preserve code blocks (including unclosed blocks)
  const codeBlocks = [];
  const makeBlock = (lang, code) => {
    const placeholder = `@@AEGIS-CODE-BLOCK-${codeBlocks.length}@@`;
    const cleanCode = code.trim();
    const langLabel = lang ? lang.trim().toLowerCase() : "code";
    const highlighted = highlightSyntax(cleanCode, langLabel);
    
    codeBlocks.push(`
      <div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang-tag">${escapeHtml(langLabel)}</span>
          <button type="button" class="btn-copy-code" onclick="handleCopyCodeBlock(this)" data-code="${escapeHtml(cleanCode)}">Copy</button>
        </div>
        <pre><code class="language-${escapeHtml(langLabel)}">${highlighted}</code></pre>
      </div>
    `);
    return placeholder;
  };

  let processed = raw.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => makeBlock(lang, code));
  processed = processed.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]+)$/g, (match, lang, code) => makeBlock(lang, code));

  // 2. Escape remaining text for strict XSS prevention
  processed = escapeHtml(processed);

  // 3. Section Headers (# to ######)
  processed = processed.replace(/^###### (.*?)$/gm, '<h6 class="msg-h6">$1</h6>');
  processed = processed.replace(/^##### (.*?)$/gm, '<h5 class="msg-h5">$1</h5>');
  processed = processed.replace(/^#### (.*?)$/gm, '<h4 class="msg-h4">$1</h4>');
  processed = processed.replace(/^### (.*?)$/gm, '<h3 class="msg-h3">$1</h3>');
  processed = processed.replace(/^## (.*?)$/gm, '<h2 class="msg-h2">$1</h2>');
  processed = processed.replace(/^# (.*?)$/gm, '<h1 class="msg-h1">$1</h1>');

  // 4. Horizontal Rules
  processed = processed.replace(/^(?:---|___|\*\*\*)$/gm, '<hr class="msg-hr">');

  // 5. Blockquotes (lines starting with &gt;)
  processed = processed.replace(/(?:^|\n)(&gt;[^\n]+(?:\n&gt;[^\n]+)*)/g, (match, block) => {
    const content = block.split('\n').map(line => line.replace(/^&gt;\s?/, '')).join('<br>');
    return `\n<blockquote class="msg-blockquote">${content}</blockquote>\n`;
  });

  // 6. Markdown Tables (Required by tests: .msg-table)
  processed = processed.replace(/(?:^|\n)((?:\|[^\n]+\|\n?)+)/g, (match, tableText) => {
    const lines = tableText.trim().split('\n').map(l => l.trim()).filter(l => l.startsWith('|') && l.endsWith('|'));
    if (lines.length < 2) return match;
    const sepIdx = lines.findIndex(l => /^\|[\s\-:|]+\|$/.test(l));
    if (sepIdx === -1) return match;

    const parseRow = (rowLine) => {
      const rawCols = rowLine.slice(1, -1).split('|');
      return rawCols.map(c => {
        let cell = c.trim().replace(/&lt;br\s*\/?&gt;/gi, '<br>');
        cell = cell.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        cell = cell.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        return cell;
      });
    };

    const headerLines = lines.slice(0, sepIdx);
    const bodyLines = lines.slice(sepIdx + 1);

    let html = '<div class="msg-table-wrapper"><table class="msg-table">';
    if (headerLines.length > 0) {
      html += '<thead>';
      headerLines.forEach(hl => {
        html += '<tr>' + parseRow(hl).map(col => `<th>${col}</th>`).join('') + '</tr>';
      });
      html += '</thead>';
    }
    if (bodyLines.length > 0) {
      html += '<tbody>';
      bodyLines.forEach(bl => {
        html += '<tr>' + parseRow(bl).map(col => `<td>${col}</td>`).join('') + '</tr>';
      });
      html += '</tbody>';
    }
    html += '</table></div>';
    return `\n${html}\n`;
  });

  // 7. Nested Lists (Unordered & Ordered)
  processed = parseMarkdownLists(processed);

  // 8. Inline formatting
  processed = processed.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  processed = processed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  processed = processed.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  processed = processed.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  processed = processed.replace(/_([^_]+)_/g, '<em>$1</em>');
  processed = processed.replace(/~~([^~]+)~~/g, '<del>$1</del>');

  // 9. Links [text](url) with safe URL sanitization
  processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
    const safeUrl = sanitizeUrl(url);
    return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" class="msg-link">${linkText}</a>`;
  });

  // 10. Paragraphs / Linebreaks
  processed = processed.replace(/\n\n+/g, '<br><br>');
  processed = processed.replace(/\n/g, '<br>');

  // Clean up superfluous breaks around block-level elements
  processed = processed.replace(/(?:<br\s*\/?>)+(<\/?(?:h[1-6]|ul|ol|li|blockquote|hr|table|thead|tbody|tr|th|td|div|pre))/gi, '$1');
  processed = processed.replace(/(<\/(?:h[1-6]|ul|ol|blockquote|hr|table|div|pre)>)(?:<br\s*\/?>)+/gi, '$1');

  // 11. Restore preserved syntax-highlighted code blocks
  codeBlocks.forEach((block, idx) => {
    processed = processed.replace(`@@AEGIS-CODE-BLOCK-${idx}@@`, block);
  });

  return processed;
}

// Global copy handlers
window.handleCopyCodeBlock = function(btn) {
  const code = btn.dataset.code;
  copyToClipboard(code, "Code copied to clipboard!").then(ok => {
    if (ok) {
      btn.textContent = "Copied!";
      setTimeout(() => { btn.textContent = "Copy"; }, 1600);
    }
  });
};

window.handleCopyAssistantMessage = function(buttonEl) {
  const bubble = buttonEl.closest(".message-bubble");
  if (!bubble) return;
  const clone = bubble.cloneNode(true);
  const actions = clone.querySelector(".message-actions-bar");
  if (actions) actions.remove();
  const text = clone.innerText.trim();

  copyToClipboard(text, "Response copied to clipboard!").then(ok => {
    if (ok) {
      const span = buttonEl.querySelector("span");
      if (span) {
        const orig = span.textContent;
        span.textContent = "Copied!";
        setTimeout(() => { span.textContent = orig; }, 1600);
      }
    }
  });
};

window.handleRetryLastMessage = function() {
  if (state.lastUserMessage) {
    dom.messageInput.value = state.lastUserMessage;
    dom.chatForm.dispatchEvent(new Event("submit"));
  }
};

// API Client
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let errMsg = `Request failed: ${res.status}`;
    try {
      const errObj = await res.json();
      errMsg = errObj.detail || errMsg;
    } catch (e) {}
    throw new Error(errMsg);
  }
  return res.json();
}

// System Health & Dual-Provider Management
async function refreshProviderStatus() {
  try {
    const data = await api("/api/provider");
    state.providerStatus = data;
    state.activeProvider = data.active_provider;
    updateProviderUI(data);
  } catch (err) {
    console.error("Failed to fetch provider status:", err);
  }
}

function updateProviderUI(data) {
  if (!data) return;
  const isOllama = data.active_provider === "ollama";
  if (dom.btnProviderOllama && dom.btnProviderCloud) {
    dom.btnProviderOllama.classList.toggle("active", isOllama);
    dom.btnProviderCloud.classList.toggle("active", !isOllama);
  }

  // Update dots and tooltips
  if (dom.dotProviderOllama) {
    dom.dotProviderOllama.className = `provider-indicator-dot ${data.ollama_available ? "ready" : "offline"}`;
    if (dom.btnProviderOllama) {
      dom.btnProviderOllama.title = data.ollama_available 
        ? `Local — Nemotron via Ollama (${data.ollama_model})` 
        : `Local — Ollama offline at ${data.ollama_base_url}`;
    }
  }

  if (dom.dotProviderCloud) {
    dom.dotProviderCloud.className = `provider-indicator-dot ${data.cloud_has_key ? "ready" : "unconfigured"}`;
    if (dom.btnProviderCloud) {
      dom.btnProviderCloud.title = data.cloud_has_key 
        ? `Cloud — Nebius / OpenRouter (${data.cloud_model})` 
        : `Cloud — API Key required (set OPENROUTER_API_KEY in .env)`;
    }
  }

  // Update model tags in topbar and sidebar
  const activeModel = isOllama ? data.ollama_model : data.cloud_model;
  if (dom.topbarProviderTag) {
    dom.topbarProviderTag.textContent = activeModel.split("/").pop() || activeModel;
    dom.topbarProviderTag.title = `Active Provider: ${data.active_provider.toUpperCase()} | Model: ${activeModel}`;
  }
  if (dom.sidebarModelId) {
    dom.sidebarModelId.textContent = `[${isOllama ? 'Local' : 'Cloud'}] ${activeModel.split("/").pop() || activeModel}`;
  }
}

async function handleSwitchProvider(targetProvider) {
  try {
    const data = await api("/api/provider", {
      method: "POST",
      body: JSON.stringify({ provider: targetProvider }),
    });
    state.providerStatus = data;
    state.activeProvider = data.active_provider;
    updateProviderUI(data);
    await checkHealth();
  } catch (err) {
    alert("Failed to switch provider: " + err.message);
  }
}

async function checkHealth() {
  try {
    const data = await api("/api/health");
    state.health = data;
    if (data.provider) {
      state.activeProvider = data.provider;
    }
    const modelName = data.model_id.split("/").pop() || data.model_id;
    if (dom.sidebarModelId) {
      dom.sidebarModelId.textContent = `[${data.provider === 'ollama' ? 'Local' : 'Cloud'}] ${modelName}`;
    }
    if (dom.topbarProviderTag) {
      dom.topbarProviderTag.textContent = modelName;
    }
    
    if (data.is_ready) {
      dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot ready";
      const provLabel = data.provider === "ollama" ? "Local Nemotron Ready" : "Cloud Ready";
      dom.systemStatusText.textContent = `Ready (${provLabel})`;
    } else {
      dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot";
      if (data.provider === "ollama") {
        dom.systemStatusText.textContent = data.provider_status === "offline" ? "Ollama Offline" : "Model Missing";
      } else {
        dom.systemStatusText.textContent = data.has_api_key ? "Degraded" : "API Key Required";
      }
    }
    refreshProviderStatus();
  } catch (err) {
    dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot";
    dom.systemStatusText.textContent = "Offline";
  }
}

// Conversations Management
async function loadConversations(searchQuery = "") {
  try {
    const url = state.activeProjectId 
      ? `/api/conversations?project_id=${encodeURIComponent(state.activeProjectId)}` 
      : `/api/conversations`;
    const convs = await api(url);
    state.allConversations = convs;

    const filtered = searchQuery 
      ? convs.filter(c => (c.title || "").toLowerCase().includes(searchQuery.toLowerCase()))
      : convs;

    renderConversationList(filtered, !!searchQuery);
  } catch (err) {
    console.error("Failed to load conversations:", err);
  }
}

function renderConversationList(convs, isSearching = false) {
  if (!convs.length) {
    dom.conversationList.innerHTML = `<div class="empty-state">${isSearching ? 'No matching conversations' : 'No conversations yet'}</div>`;
    return;
  }

  if (isSearching) {
    dom.conversationList.innerHTML = convs.map(c => renderConversationItemHtml(c)).join("");
    return;
  }

  const grouped = groupConversationsByDate(convs);
  let html = "";

  const sections = [
    { title: "Today", list: grouped.today },
    { title: "Yesterday", list: grouped.yesterday },
    { title: "Previous 7 Days", list: grouped.previous7Days },
    { title: "Older", list: grouped.older },
  ];

  sections.forEach(sec => {
    if (sec.list.length > 0) {
      html += `<div class="date-group-header">${sec.title}</div>`;
      html += sec.list.map(c => renderConversationItemHtml(c)).join("");
    }
  });

  dom.conversationList.innerHTML = html;
}

function renderConversationItemHtml(c) {
  const isActive = c.id === state.activeConversationId;
  return `
    <div class="conversation-item ${isActive ? 'active' : ''}" data-id="${c.id}" title="${escapeHtml(c.title)} (${formatDate(c.updated_at || c.created_at)})">
      <span class="conversation-title">${escapeHtml(c.title)}</span>
      <div class="conversation-item-actions">
        <button type="button" class="conv-action-btn btn-rename" data-rename-id="${c.id}" title="Rename conversation">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        </button>
        <button type="button" class="conv-action-btn btn-del" data-del-id="${c.id}" title="Delete conversation">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    </div>
  `;
}

async function selectConversation(convId) {
  state.activeConversationId = convId;
  try {
    const conv = await api(`/api/conversations/${convId}`);
    dom.activeSessionTitle.textContent = conv.title || "Active Session";
    renderMessages(conv.messages || []);
    loadConversations(dom.conversationSearchInput.value.trim());
    closeMobileSidebar();
  } catch (err) {
    alert("Error loading conversation: " + err.message);
  }
}

function createNewSession() {
  state.activeConversationId = null;
  dom.activeSessionTitle.textContent = "New Session";
  dom.messagesContainer.innerHTML = "";
  dom.messagesContainer.appendChild(dom.welcomeHero);
  loadConversations(dom.conversationSearchInput.value.trim());
  closeMobileSidebar();
}

async function renameConversationModal(convId) {
  const currentConv = state.allConversations.find(c => c.id === convId);
  const currentTitle = currentConv ? currentConv.title : (dom.activeSessionTitle.textContent || "Conversation");
  const newTitle = prompt("Enter new title for conversation:", currentTitle);
  if (!newTitle || !newTitle.trim() || newTitle.trim() === currentTitle) return;

  try {
    const updated = await api(`/api/conversations/${convId}`, {
      method: "PATCH",
      body: JSON.stringify({ title: newTitle.trim() }),
    });
    if (state.activeConversationId === convId) {
      dom.activeSessionTitle.textContent = updated.title;
    }
    loadConversations(dom.conversationSearchInput.value.trim());
  } catch (err) {
    alert("Failed to rename conversation: " + err.message);
  }
}

// Render Messages & Approvals
function renderMessages(messages) {
  dom.messagesContainer.innerHTML = "";
  if (!messages || messages.length === 0) {
    dom.messagesContainer.appendChild(dom.welcomeHero);
    return;
  }

  messages.forEach(m => {
    appendMessageToDom(m);
  });

  dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
}

function appendMessageToDom(m) {
  const row = document.createElement("div");
  row.className = `message-row ${m.role}`;

  let memoriesHtml = "";
  if (m.retrieved_memories && m.retrieved_memories.length > 0) {
    memoriesHtml = `
      <div class="retrieved-memories-pill" title="Relevant memories retrieved from SQLite">
        <span class="mem-title"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mem-icon" style="vertical-align:-2px; margin-right:4px;"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>Memories Applied:</span>
        ${m.retrieved_memories.map(rm => `<strong>[${escapeHtml(rm.category)}]</strong> ${escapeHtml(rm.content.substring(0, 45))}...`).join(" | ")}
      </div>
    `;
  }

  let actionsBarHtml = "";
  if (m.role === "assistant") {
    actionsBarHtml = `
      <div class="message-actions-bar">
        <button type="button" class="btn-msg-action btn-copy-response" onclick="handleCopyAssistantMessage(this)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <span>Copy</span>
        </button>
        <button type="button" class="btn-msg-action btn-retry" onclick="handleRetryLastMessage()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          <span>Retry</span>
        </button>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-meta">
      <span class="message-role ${m.role}">${m.role === 'user' ? 'Owner' : 'Aegis AI'}</span>
      <span>${formatDate(m.created_at)}</span>
      ${m.skill_id ? `<span class="badge badge-muted">${escapeHtml(m.skill_id)}</span>` : ''}
    </div>
    ${memoriesHtml}
    <div class="message-bubble">
      ${renderSafeMarkdown(m.content)}
      ${actionsBarHtml}
    </div>
  `;

  dom.messagesContainer.appendChild(row);

  // Auto-scroll only if user is already near bottom
  const isNearBottom = dom.messagesContainer.scrollHeight - dom.messagesContainer.scrollTop - dom.messagesContainer.clientHeight < 160;
  if (isNearBottom) {
    dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
  }
}

function renderApprovalCardInMessage(approval) {
  const card = document.createElement("div");
  card.className = "approval-card";
  card.id = `approval-card-${approval.id}`;

  let diffOrCmd = "";
  if (approval.action_type === 'file_patch' || approval.action_type === 'file_create') {
    const diff = approval.details.diff || approval.details.proposed_content || "";
    const lines = diff.split("\n").map(l => {
      if (l.startsWith("+") && !l.startsWith("+++")) return `<span class="diff-add">${escapeHtml(l)}</span>`;
      if (l.startsWith("-") && !l.startsWith("---")) return `<span class="diff-del">${escapeHtml(l)}</span>`;
      return `<span>${escapeHtml(l)}</span>`;
    }).join("");
    diffOrCmd = `<div class="approval-diff-box">${lines}</div>`;
  } else if (approval.action_type === 'run_command') {
    diffOrCmd = `<div class="approval-diff-box"><code>${escapeHtml(approval.details.command || approval.target)}</code></div>`;
  } else if (approval.action_type === 'task_create') {
    const dueBadge = approval.details.due_date ? `<span class="badge badge-muted">Due: ${escapeHtml(approval.details.due_date)}</span>` : '';
    diffOrCmd = `
      <div class="approval-task-card">
        <div class="approval-task-header">
          <span class="approval-task-title"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" style="vertical-align:-2px; margin-right:4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>${escapeHtml(approval.details.title || approval.target)}</span>
          ${dueBadge}
        </div>
        ${approval.details.description ? `<p class="approval-task-desc">${escapeHtml(approval.details.description)}</p>` : ''}
      </div>
    `;
  }

  card.innerHTML = `
    <div class="approval-card-header">
      <span class="approval-card-type"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-2px; margin-right:4px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>Approval Required: ${escapeHtml(approval.action_type)}</span>
      <span class="badge badge-amber" id="status-badge-${approval.id}">${escapeHtml(approval.status)}</span>
    </div>
    <div><strong>Target:</strong> <code>${escapeHtml(approval.target)}</code></div>
    <div class="mt-1"><strong>Reason:</strong> ${escapeHtml(approval.reason)}</div>
    <div><strong>Potential Risk:</strong> ${escapeHtml(approval.risk)}</div>
    ${diffOrCmd}
    <div class="approval-card-actions" id="actions-${approval.id}">
      <button class="btn btn-emerald btn-sm" onclick="handleApproveAction('${approval.id}')">
        ✓ Approve & Apply
      </button>
      <button class="btn btn-rose btn-sm" onclick="handleRejectAction('${approval.id}')">
        ✕ Reject
      </button>
    </div>
  `;

  dom.messagesContainer.appendChild(card);
  dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
}

// Approval Handlers
window.handleApproveAction = async function(id) {
  const actionsDiv = document.getElementById(`actions-${id}`);
  if (actionsDiv) actionsDiv.innerHTML = `<span class="text-muted"><span class="spinner-icon"></span> Executing approved operation...</span>`;
  try {
    const res = await api(`/api/approvals/${id}/approve`, { method: "POST" });
    const badge = document.getElementById(`status-badge-${id}`);
    if (badge) {
      badge.textContent = res.status;
      badge.className = res.status === 'SUCCEEDED' ? 'badge badge-emerald' : 'badge badge-rose';
    }
    if (actionsDiv) {
      actionsDiv.innerHTML = `<span style="color:var(--accent-emerald);">✓ Successfully Applied</span>`;
    }
    refreshPendingApprovals();
  } catch (err) {
    if (actionsDiv) {
      actionsDiv.innerHTML = `<span style="color:var(--accent-rose);">Execution failed: ${escapeHtml(err.message)}</span>`;
    }
  }
};

window.handleRejectAction = async function(id) {
  const actionsDiv = document.getElementById(`actions-${id}`);
  try {
    const res = await api(`/api/approvals/${id}/reject`, { method: "POST" });
    const badge = document.getElementById(`status-badge-${id}`);
    if (badge) {
      badge.textContent = res.status;
      badge.className = 'badge badge-rose';
    }
    if (actionsDiv) {
      actionsDiv.innerHTML = `<span style="color:var(--accent-rose);">✕ Rejected by User</span>`;
    }
    refreshPendingApprovals();
  } catch (err) {
    alert("Reject error: " + err.message);
  }
};

async function refreshPendingApprovals() {
  try {
    const pending = await api("/api/approvals?status=PENDING_APPROVAL");
    state.pendingApprovals = pending;
    if (pending.length > 0) {
      dom.pendingCountBadge.style.display = "inline-block";
      dom.pendingCountBadge.textContent = pending.length;
      dom.topPendingBanner.style.display = "flex";
      dom.topPendingText.textContent = `${pending.length} Action Pending`;
    } else {
      dom.pendingCountBadge.style.display = "none";
      dom.topPendingBanner.style.display = "none";
      dom.pendingApprovalsPanel.style.display = "none";
    }
  } catch (err) {
    console.error("Failed to fetch pending approvals:", err);
  }
}

// Thinking Indicator Helper
function showThinkingIndicator(initialText = "Reasoning & operating...") {
  const row = document.createElement("div");
  row.className = "message-row assistant thinking";
  row.id = "thinkingIndicator";

  row.innerHTML = `
    <div class="message-meta">
      <span class="message-role assistant">Aegis AI</span>
      <span class="badge badge-muted">Thinking</span>
    </div>
    <div class="message-bubble thinking-bubble">
      <div class="thinking-pulse-container">
        <div class="thinking-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <span class="thinking-status-text" id="thinkingStatusText">${escapeHtml(initialText)}</span>
      </div>
    </div>
  `;

  dom.messagesContainer.appendChild(row);
  dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;

  const steps = [
    "Consulting persistent local memory...",
    state.activeProvider === "ollama" 
      ? "Executing local NVIDIA Nemotron (Ollama) reasoning..." 
      : "Executing cloud NVIDIA Nemotron reasoning...",
    "Evaluating workspace security directives...",
    "Formulating response..."
  ];
  let stepIdx = 0;
  const interval = setInterval(() => {
    const textEl = document.getElementById("thinkingStatusText");
    if (!textEl) {
      clearInterval(interval);
      return;
    }
    stepIdx = (stepIdx + 1) % steps.length;
    textEl.textContent = steps[stepIdx];
  }, 2000);

  return () => {
    clearInterval(interval);
    const el = document.getElementById("thinkingIndicator");
    if (el) el.remove();
  };
}

// Request Cancellation Helper
function abortCurrentRequest() {
  if (currentAbortController) {
    currentAbortController.abort();
    currentAbortController = null;
    showToast("Generation stopped", "info");
  }
}

// Helper to create an active streaming message row in DOM
function createStreamingMessageRow(skillId) {
  const row = document.createElement("div");
  row.className = "message-row assistant";

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.innerHTML = `
    <span class="message-role assistant">Aegis AI</span>
    <span>Just now</span>
    ${skillId ? `<span class="badge badge-muted">${escapeHtml(skillId)}</span>` : ""}
  `;
  row.appendChild(meta);

  // Container for memories if returned in stream
  const memoriesContainer = document.createElement("div");
  memoriesContainer.className = "stream-memories-holder";
  row.appendChild(memoriesContainer);

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const contentEl = document.createElement("span");
  contentEl.className = "stream-content";

  const cursorEl = document.createElement("span");
  cursorEl.className = "streaming-cursor";

  bubble.appendChild(contentEl);
  bubble.appendChild(cursorEl);
  row.appendChild(bubble);

  dom.messagesContainer.appendChild(row);

  return { row, bubble, contentEl, cursorEl, memoriesContainer };
}

function createMessageActionsBar() {
  const bar = document.createElement("div");
  bar.className = "message-actions-bar";
  bar.innerHTML = `
    <button type="button" class="btn-msg-action btn-copy-response" onclick="handleCopyAssistantMessage(this)">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span>Copy</span>
    </button>
    <button type="button" class="btn-msg-action btn-retry" onclick="handleRetryLastMessage()">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M23 4v6h-6"></path>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
      </svg>
      <span>Retry</span>
    </button>
  `;
  return bar;
}

// Chat Form Submission (Native SSE Token Streaming with Auto-Scroll & Fallback)
dom.chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = dom.messageInput.value.trim();
  if (!text) return;

  state.lastUserMessage = text;

  // Render user message immediately
  appendMessageToDom({
    role: "user",
    content: text,
    created_at: new Date().toISOString(),
  });

  dom.messageInput.value = "";
  dom.messageInput.style.height = "auto";

  // Switch Send to Stop button
  dom.btnSend.style.display = "none";
  if (dom.btnStop) dom.btnStop.style.display = "flex";

  const removeThinking = showThinkingIndicator();
  currentAbortController = new AbortController();

  let streamRow = null;
  let streamBubble = null;
  let streamContentEl = null;
  let streamCursorEl = null;
  let memoriesContainer = null;
  let accumulatedRaw = "";
  let finalData = null;

  try {
    const payload = {
      message: text,
      conversation_id: state.activeConversationId,
      project_id: state.activeProjectId,
      skill_id: state.activeSkillId || null,
      provider: state.activeProvider || null,
      agent_backend: state.activeAgentBackend || "aegis",
      execution_mode: state.executionMode || (state.activeAgentBackend === "hermes" ? "autonomous" : "supervised"),
    };

    let streamResponse = null;
    let streamFailed = false;

    try {
      streamResponse = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: currentAbortController.signal,
      });

      if (!streamResponse.ok) {
        streamFailed = true;
      }
    } catch (netErr) {
      if (netErr.name === "AbortError" || currentAbortController.signal.aborted) {
        throw netErr;
      }
      streamFailed = true;
    }

    if (streamFailed || !streamResponse || !streamResponse.body) {
      // Graceful fallback to non-streaming /api/chat
      const res = await api("/api/chat", {
        method: "POST",
        body: JSON.stringify(payload),
        signal: currentAbortController.signal,
      });

      removeThinking();
      state.activeConversationId = res.conversation_id;

      appendMessageToDom({
        role: "assistant",
        content: res.assistant_message,
        retrieved_memories: res.retrieved_memories,
        skill_id: state.activeSkillId,
        created_at: new Date().toISOString(),
      });

      if (res.pending_approvals && res.pending_approvals.length > 0) {
        res.pending_approvals.forEach(appr => renderApprovalCardInMessage(appr));
        refreshPendingApprovals();
      } else if (res.pending_approval) {
        renderApprovalCardInMessage(res.pending_approval);
        refreshPendingApprovals();
      }

      loadConversations(dom.conversationSearchInput.value.trim());
      return;
    }

    // Stream SSE consumption
    const reader = streamResponse.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let sseBuffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      sseBuffer += decoder.decode(value, { stream: true });
      const lines = sseBuffer.split("\n");
      sseBuffer = lines.pop(); // Keep incomplete line in buffer

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;
        const jsonStr = trimmed.slice(5).trim();
        if (!jsonStr) continue;

        let data = null;
        try {
          data = JSON.parse(jsonStr);
        } catch (e) {
          continue;
        }

        if (data.error) {
          throw new Error(data.error);
        }

        if (data.token) {
          if (!streamRow) {
            removeThinking();
            const created = createStreamingMessageRow(state.activeSkillId);
            streamRow = created.row;
            streamBubble = created.bubble;
            streamContentEl = created.contentEl;
            streamCursorEl = created.cursorEl;
            memoriesContainer = created.memoriesContainer;
          }

          accumulatedRaw += data.token;
          streamContentEl.textContent = accumulatedRaw;

          // Auto-scroll lock: only auto-scroll if user is near the bottom
          const isNearBottom = dom.messagesContainer.scrollHeight - dom.messagesContainer.scrollTop - dom.messagesContainer.clientHeight < 160;
          if (isNearBottom) {
            dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
          }
        }

        if (data.done) {
          finalData = data;
        }
      }
    }

    // Stream finished successfully
    removeThinking();

    if (streamRow && streamBubble) {
      if (streamCursorEl) streamCursorEl.remove();

      // Render formatted safe Markdown with syntax highlighting
      const finalText = (finalData && finalData.assistant_message) ? finalData.assistant_message : accumulatedRaw;
      streamBubble.innerHTML = renderSafeMarkdown(finalText);
      streamBubble.appendChild(createMessageActionsBar());

      // If retrieved memories were sent, populate memories pill
      if (finalData && finalData.retrieved_memories && finalData.retrieved_memories.length > 0 && memoriesContainer) {
        memoriesContainer.innerHTML = `
          <div class="retrieved-memories-pill" title="Relevant memories retrieved from SQLite">
            <span class="mem-title"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mem-icon" style="vertical-align:-2px; margin-right:4px;"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>Memories Applied:</span>
            ${finalData.retrieved_memories.map(rm => `<strong>[${escapeHtml(rm.category)}]</strong> ${escapeHtml(rm.content.substring(0, 45))}...`).join(" | ")}
          </div>
        `;
      }

      // If actions were proposed, render approval cards directly
      if (finalData && finalData.pending_approvals && finalData.pending_approvals.length > 0) {
        finalData.pending_approvals.forEach(appr => renderApprovalCardInMessage(appr));
        refreshPendingApprovals();
      } else if (finalData && finalData.pending_approval) {
        renderApprovalCardInMessage(finalData.pending_approval);
        refreshPendingApprovals();
      }

      if (finalData && finalData.conversation_id) {
        state.activeConversationId = finalData.conversation_id;
        loadConversations(dom.conversationSearchInput.value.trim());
      }

      // Auto-scroll lock check at completion
      const isNearBottom = dom.messagesContainer.scrollHeight - dom.messagesContainer.scrollTop - dom.messagesContainer.clientHeight < 160;
      if (isNearBottom) {
        dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
      }
    } else if (finalData) {
      // Completed without tokens (e.g. empty or direct metadata)
      appendMessageToDom({
        role: "assistant",
        content: finalData.assistant_message || "(Empty response)",
        retrieved_memories: finalData.retrieved_memories,
        skill_id: state.activeSkillId,
        created_at: new Date().toISOString(),
      });
      if (finalData.conversation_id) {
        state.activeConversationId = finalData.conversation_id;
        loadConversations(dom.conversationSearchInput.value.trim());
      }
    }
  } catch (err) {
    removeThinking();
    const isAborted = err.name === "AbortError" || (err.message && err.message.toLowerCase().includes("abort"));

    if (isAborted) {
      if (streamRow && streamBubble) {
        if (streamCursorEl) streamCursorEl.remove();
        streamBubble.innerHTML = renderSafeMarkdown(accumulatedRaw) + `\n\n<div class="text-muted mt-2" style="font-size:0.8rem; font-style:italic;">— Generation stopped by user</div>`;
        streamBubble.appendChild(createMessageActionsBar());
      } else {
        appendMessageToDom({
          role: "assistant",
          content: "*Generation stopped by user.*",
          created_at: new Date().toISOString(),
        });
      }
    } else {
      if (streamRow && streamBubble) {
        if (streamCursorEl) streamCursorEl.remove();
        streamBubble.innerHTML = renderSafeMarkdown(accumulatedRaw) + `\n\n<div class="banner-alert mt-2" style="display:flex;">⚠️ Operational Notice: ${escapeHtml(err.message)}</div>`;
        streamBubble.appendChild(createMessageActionsBar());
      } else {
        appendMessageToDom({
          role: "assistant",
          content: `⚠️ Aegis AI Operational Notice: ${err.message}`,
          created_at: new Date().toISOString(),
        });
      }
    }
  } finally {
    currentAbortController = null;
    if (dom.btnStop) dom.btnStop.style.display = "none";
    dom.btnSend.style.display = "flex";
    dom.btnSend.disabled = false;
    dom.messageInput.focus();
  }
});

// Sidebar & Mobile Drawer Toggles
function toggleSidebarCollapse() {
  dom.sidebar.classList.toggle("collapsed");
}

function openMobileSidebar() {
  dom.sidebar.classList.add("open");
  dom.sidebarBackdrop.classList.add("active");
}

function closeMobileSidebar() {
  dom.sidebar.classList.remove("open");
  dom.sidebarBackdrop.classList.remove("active");
}

// Projects Management
async function loadProjects() {
  try {
    const list = await api("/api/projects");
    state.projects = list;
    
    dom.projectSelector.innerHTML = `<option value="">(Global / No Project)</option>` + 
      list.map(p => `<option value="${p.id}" ${p.id === state.activeProjectId ? 'selected' : ''}>${escapeHtml(p.name)}</option>`).join("");
    
    if (state.activeProjectId) {
      const activeP = list.find(p => p.id === state.activeProjectId);
      if (activeP) {
        dom.activeProjectBadge.style.display = "inline-block";
        dom.activeProjectBadge.textContent = `Project: ${activeP.name}`;
      }
    } else {
      dom.activeProjectBadge.style.display = "none";
    }

    renderModalProjects(list);
  } catch (err) {
    console.error("Failed to load projects:", err);
  }
}

function renderModalProjects(list) {
  const container = document.getElementById("modalProjectsList");
  if (!list.length) {
    container.innerHTML = `<div class="empty-state">
      <div class="empty-state-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
      </div>
      <div class="empty-state-title">No projects created yet</div>
      <div class="empty-state-desc">Create your first project milestone to organize and track autonomous tasks.</div>
    </div>`;
    return;
  }
  container.innerHTML = list.map(p => `
    <div class="list-item-card ${p.id === state.activeProjectId ? 'selected' : ''}" onclick="selectProjectModal('${p.id}')">
      <div>
        <strong>${escapeHtml(p.name)}</strong>
        <div class="text-muted" style="font-size:0.75rem;">${escapeHtml(p.description || 'No description')}</div>
      </div>
      <button class="btn-close" onclick="event.stopPropagation(); deleteProject('${p.id}')" title="Delete project" aria-label="Delete project">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  `).join("");
}

window.selectProjectModal = function(id) {
  state.activeProjectId = id;
  dom.projectSelector.value = id;
  loadProjects();
  loadTasksForProject(id);
};

window.deleteProject = async function(id) {
  if (!confirm("Delete this project?")) return;
  try {
    await api(`/api/projects/${id}`, { method: "DELETE" });
    if (state.activeProjectId === id) state.activeProjectId = null;
    loadProjects();
  } catch (err) {
    alert("Delete failed: " + err.message);
  }
};

async function loadTasksForProject(projectId) {
  const container = document.getElementById("modalTasksList");
  if (!projectId) {
    container.innerHTML = `<div class="empty-state">
      <div class="empty-state-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line></svg>
      </div>
      <div class="empty-state-title">Select a project</div>
      <div class="empty-state-desc">Choose a project on the left to inspect and manage its tasks.</div>
    </div>`;
    return;
  }
  try {
    const tasks = await api(`/api/tasks?project_id=${projectId}`);
    if (!tasks.length) {
      container.innerHTML = `<div class="empty-state">
        <div class="empty-state-title">No tasks in this project</div>
        <div class="empty-state-desc">Click '+ Add Task' above to add an actionable development task.</div>
      </div>`;
      return;
    }
    container.innerHTML = tasks.map(t => `
      <div class="list-item-card">
        <div>
          <strong>${escapeHtml(t.title)}</strong>
          <div class="text-muted" style="font-size:0.75rem;">${escapeHtml(t.description || '')}</div>
          <span class="status-pill ${t.status === 'completed' ? 'ready' : 'pending'}" style="margin-top:4px;">
            <span class="status-pill-dot"></span>
            <span>${escapeHtml(t.status)}</span>
          </span>
        </div>
        <div class="btn-group">
          <button class="btn btn-xs btn-outline" onclick="toggleTaskStatus('${t.id}', '${t.status}')">
            ${t.status === 'completed' ? 'Reopen' : 'Complete'}
          </button>
          <button class="btn-close" onclick="deleteTask('${t.id}', '${projectId}')" title="Delete task" aria-label="Delete task">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Failed to load tasks: ${err.message}</div>`;
  }
}

window.toggleTaskStatus = async function(taskId, currentStatus) {
  const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
  try {
    await api(`/api/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({ status: newStatus }),
    });
    loadTasksForProject(state.activeProjectId);
  } catch (err) {
    alert("Update task failed: " + err.message);
  }
};

window.deleteTask = async function(taskId, projectId) {
  try {
    await api(`/api/tasks/${taskId}`, { method: "DELETE" });
    loadTasksForProject(projectId);
  } catch (err) {
    alert("Delete task failed: " + err.message);
  }
};

// Memory Management
async function loadMemories(category = "", query = "") {
  const grid = document.getElementById("memoryCardsGrid");
  try {
    let url = `/api/memories?`;
    if (category) url += `category=${encodeURIComponent(category)}&`;
    if (query) url += `q=${encodeURIComponent(query)}&`;
    const memories = await api(url);

    if (!memories.length) {
      grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">
        <div class="empty-state-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
        </div>
        <div class="empty-state-title">No persistent memories stored</div>
        <div class="empty-state-desc">Add developer preferences or architecture directives that persist across all conversations.</div>
      </div>`;
      return;
    }

    grid.innerHTML = memories.map(m => `
      <div class="memory-card">
        <div class="memory-category-tag">${escapeHtml(m.category)}</div>
        <p>${escapeHtml(m.content)}</p>
        ${m.keywords ? `<div class="text-muted mt-1" style="font-size:0.72rem;">Keywords: ${escapeHtml(m.keywords)}</div>` : ''}
        <button class="btn-close" style="position:absolute; top:12px; right:12px;" onclick="deleteMemoryItem('${m.id}')" title="Delete memory" aria-label="Delete memory">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    `).join("");
  } catch (err) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load memories: ${err.message}</div>`;
  }
}

window.deleteMemoryItem = async function(id) {
  if (!confirm("Delete this memory?")) return;
  try {
    await api(`/api/memories/${id}`, { method: "DELETE" });
    loadMemories();
  } catch (err) {
    alert("Failed to delete memory: " + err.message);
  }
};

// Skills Catalog
async function loadSkillsCatalog() {
  const grid = document.getElementById("skillsCatalogGrid");
  try {
    const skills = await api("/api/skills");
    state.skills = skills;

    grid.innerHTML = skills.map(s => `
      <div class="skill-catalog-card">
        <div>
          <h4>${escapeHtml(s.name)}</h4>
          <p>${escapeHtml(s.purpose)}</p>
          <div class="skill-tools-tags">
            ${(s.permitted_tools || []).map(t => `<span class="tool-tag">${escapeHtml(t)}</span>`).join("")}
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="activateSkill('${s.id}', '${s.name}')">
          Activate Skill
        </button>
      </div>
    `).join("");
  } catch (err) {
    grid.innerHTML = `<div class="empty-state">Failed to load skills: ${err.message}</div>`;
  }
}

window.activateSkill = function(id, name) {
  state.activeSkillId = id;
  document.querySelectorAll(".skill-pill").forEach(p => {
    p.classList.toggle("active", p.dataset.skill === id);
  });
  dom.activeSkillBadge.style.display = id ? "inline-block" : "none";
  dom.activeSkillBadge.textContent = `Skill: ${name || id}`;
  closeAllModals();
};

// Workspace Browser
async function loadWorkspaceBrowser() {
  const listEl = document.getElementById("workspaceFilesList");
  try {
    const data = await api("/api/workspace/files");
    document.getElementById("wsRootDisplay").textContent = data.workspace_root;
    if (!data.files.length) {
      listEl.innerHTML = `<div class="empty-state">
        <div class="empty-state-title">No files in authorized workspace</div>
        <div class="empty-state-desc">The workspace sandbox is currently empty.</div>
      </div>`;
      return;
    }
    listEl.innerHTML = data.files.map(f => `
      <div class="list-item-card" onclick="previewWorkspaceFile('${escapeHtml(f.path)}')">
        <span style="display:inline-flex; align-items:center; gap:8px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
          <strong>${escapeHtml(f.name)}</strong>
        </span>
        <span class="text-muted" style="font-family:var(--font-mono); font-size:0.75rem;">${f.size} B</span>
      </div>
    `).join("");
  } catch (err) {
    listEl.innerHTML = `<div class="empty-state">Failed to load workspace files: ${err.message}</div>`;
  }
}

window.previewWorkspaceFile = async function(path) {
  const box = document.getElementById("workspaceFilePreview");
  try {
    const file = await api(`/api/workspace/file?path=${encodeURIComponent(path)}`);
    box.textContent = file.content;
  } catch (err) {
    box.textContent = `Error reading file: ${err.message}`;
  }
};

// Audit Trail
async function loadAuditTrail() {
  const tbody = document.getElementById("auditTableBody");
  try {
    const logs = await api("/api/audit");
    if (!logs.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No audit records recorded yet</td></tr>`;
      return;
    }
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td><span class="mono-time">${formatDate(l.timestamp)}</span></td>
        <td><code style="font-size:0.75rem;">${escapeHtml(l.action_type)}</code></td>
        <td>${escapeHtml(l.proposed_operation)}</td>
        <td>
          <span class="status-pill ${l.approval_status === 'APPROVED' ? 'approved' : (l.approval_status === 'REJECTED' ? 'rejected' : 'pending')}">
            <span class="status-pill-dot"></span>
            <span>${escapeHtml(l.approval_status)}</span>
          </span>
        </td>
        <td>${escapeHtml(l.execution_outcome)}</td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Failed to load audit logs: ${err.message}</td></tr>`;
  }
}

// Modal Helpers
function openModal(modalEl) {
  closeAllModals();
  if (modalEl) modalEl.classList.add("active");
}

function closeAllModals() {
  document.querySelectorAll(".modal").forEach(m => m.classList.remove("active"));
}

document.querySelectorAll("[data-close-modal]").forEach(btn => {
  btn.addEventListener("click", closeAllModals);
});

// Event Listeners Setup
function setupEventListeners() {
  // Sidebar collapse & Mobile drawer
  if (dom.btnToggleSidebar) {
    dom.btnToggleSidebar.addEventListener("click", toggleSidebarCollapse);
  }
  if (dom.btnMobileMenu) {
    dom.btnMobileMenu.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        openMobileSidebar();
      } else {
        toggleSidebarCollapse();
      }
    });
  }
  if (dom.sidebarBackdrop) {
    dom.sidebarBackdrop.addEventListener("click", closeMobileSidebar);
  }

  // Stop Generation button
  if (dom.btnStop) {
    dom.btnStop.addEventListener("click", abortCurrentRequest);
  }

  // New session button
  dom.btnNewSession.addEventListener("click", createNewSession);

  // Search Conversations
  if (dom.conversationSearchInput) {
    dom.conversationSearchInput.addEventListener("input", (e) => {
      const q = e.target.value;
      if (dom.btnClearSearch) {
        dom.btnClearSearch.style.display = q ? "block" : "none";
      }
      loadConversations(q);
    });
  }
  if (dom.btnClearSearch) {
    dom.btnClearSearch.addEventListener("click", () => {
      dom.conversationSearchInput.value = "";
      dom.btnClearSearch.style.display = "none";
      loadConversations("");
    });
  }

  // Active Session Title Click / Rename
  if (dom.btnRenameActiveSession) {
    dom.btnRenameActiveSession.addEventListener("click", () => {
      if (state.activeConversationId) {
        renameConversationModal(state.activeConversationId);
      }
    });
  }
  if (dom.activeSessionTitle) {
    dom.activeSessionTitle.addEventListener("click", () => {
      if (state.activeConversationId) {
        renameConversationModal(state.activeConversationId);
      }
    });
  }

  // Status refresh button
  dom.btnRefreshStatus.addEventListener("click", () => {
    checkHealth();
    refreshPendingApprovals();
  });

  // Project selector
  dom.projectSelector.addEventListener("change", (e) => {
    state.activeProjectId = e.target.value || null;
    loadProjects();
    loadConversations(dom.conversationSearchInput ? dom.conversationSearchInput.value.trim() : "");
  });

  dom.btnOpenProjectsModal.addEventListener("click", () => {
    openModal(dom.modalProjects);
    loadProjects();
    loadTasksForProject(state.activeProjectId);
  });

  // Navigation Tabs in Sidebar
  document.querySelectorAll(".sidebar-nav .nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      document.querySelectorAll(".sidebar-nav .nav-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      if (target === "sessions") {
        closeAllModals();
      } else if (target === "skills") {
        openModal(dom.modalSkills);
        loadSkillsCatalog();
      } else if (target === "memory") {
        openModal(dom.modalMemory);
        loadMemories();
      } else if (target === "approvals") {
        openModal(dom.modalApprovals);
        loadModalApprovals();
      } else if (target === "workspace") {
        openModal(dom.modalWorkspace);
        loadWorkspaceBrowser();
      } else if (target === "audit") {
        openModal(dom.modalAudit);
        loadAuditTrail();
      }
      closeMobileSidebar();
    });
  });

  // ChatGPT Suggestion Chips on Welcome Screen
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.dataset.prompt;
      if (prompt) {
        dom.messageInput.value = prompt;
        dom.messageInput.focus();
        dom.chatForm.dispatchEvent(new Event("submit"));
      }
    });
  });

  // Auto-resize & Enter-to-send (Shift+Enter for newline)
  dom.messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      dom.chatForm.dispatchEvent(new Event("submit"));
    }
  });
  dom.messageInput.addEventListener("input", () => {
    dom.messageInput.style.height = "auto";
    dom.messageInput.style.height = Math.min(dom.messageInput.scrollHeight, 180) + "px";
  });

  // Skill Pills
  document.querySelectorAll(".skill-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const skillId = pill.dataset.skill;
      activateSkill(skillId, pill.textContent);
    });
  });

  // Agent Backend Switcher Buttons (Aegis vs Hermes)
  function updateAgentBackendButtons() {
    if (dom.btnBackendAegis && dom.btnBackendHermes) {
      if (state.activeAgentBackend === "hermes") {
        dom.btnBackendHermes.classList.add("active");
        dom.btnBackendAegis.classList.remove("active");
      } else {
        dom.btnBackendAegis.classList.add("active");
        dom.btnBackendHermes.classList.remove("active");
      }
    }
  }
  updateAgentBackendButtons();

  // Execution Mode Switcher Buttons (Autonomous vs Supervised)
  function updateExecutionModeButtons() {
    if (dom.btnModeAutonomous && dom.btnModeSupervised) {
      if (state.executionMode === "autonomous") {
        dom.btnModeAutonomous.classList.add("active");
        dom.btnModeSupervised.classList.remove("active");
      } else {
        dom.btnModeSupervised.classList.add("active");
        dom.btnModeAutonomous.classList.remove("active");
      }
    }
    const modeSettingEl = document.getElementById("settingsHermesMode");
    if (modeSettingEl) {
      modeSettingEl.textContent = state.executionMode === "autonomous" ? "Autonomous (Permitted Workspace Edits)" : "Supervised (Human Approval Required)";
    }
  }
  updateExecutionModeButtons();

  if (dom.btnBackendAegis) {
    dom.btnBackendAegis.addEventListener("click", () => {
      state.activeAgentBackend = "aegis";
      state.executionMode = "supervised";
      if (typeof localStorage !== "undefined" && localStorage && localStorage.setItem) {
        localStorage.setItem("aegis_agent_backend", "aegis");
        localStorage.setItem("aegis_execution_mode", "supervised");
      }
      updateAgentBackendButtons();
      updateExecutionModeButtons();
      showToast("Agent Mode: Aegis Native Reasoning Engine (Supervised)", "info");
    });
  }
  if (dom.btnBackendHermes) {
    dom.btnBackendHermes.addEventListener("click", () => {
      state.activeAgentBackend = "hermes";
      state.executionMode = "autonomous";
      if (typeof localStorage !== "undefined" && localStorage && localStorage.setItem) {
        localStorage.setItem("aegis_agent_backend", "hermes");
        localStorage.setItem("aegis_execution_mode", "autonomous");
      }
      updateAgentBackendButtons();
      updateExecutionModeButtons();
      showToast("Agent Mode: Hermes Agent (Autonomous Execution Enabled)", "info");
    });
  }

  if (dom.btnModeAutonomous) {
    dom.btnModeAutonomous.addEventListener("click", () => {
      state.executionMode = "autonomous";
      if (typeof localStorage !== "undefined" && localStorage && localStorage.setItem) {
        localStorage.setItem("aegis_execution_mode", "autonomous");
      }
      updateExecutionModeButtons();
      showToast("Execution Mode: Autonomous (Auto-executes permitted actions)", "info");
    });
  }
  if (dom.btnModeSupervised) {
    dom.btnModeSupervised.addEventListener("click", () => {
      state.executionMode = "supervised";
      if (typeof localStorage !== "undefined" && localStorage && localStorage.setItem) {
        localStorage.setItem("aegis_execution_mode", "supervised");
      }
      updateExecutionModeButtons();
      showToast("Execution Mode: Supervised (Requires human approval)", "info");
    });
  }

  // Dual-Provider Switcher Buttons
  if (dom.btnProviderOllama) {
    dom.btnProviderOllama.addEventListener("click", () => handleSwitchProvider("ollama"));
  }
  if (dom.btnProviderCloud) {
    dom.btnProviderCloud.addEventListener("click", () => handleSwitchProvider("cloud"));
  }

  // Quick review banner
  dom.btnQuickReview.addEventListener("click", () => {
    openModal(dom.modalApprovals);
    loadModalApprovals("PENDING_APPROVAL");
  });

  if (dom.btnCloseApprovalPanel) {
    dom.btnCloseApprovalPanel.addEventListener("click", () => {
      dom.pendingApprovalsPanel.style.display = "none";
    });
  }

  // Stop Generation button
  if (dom.btnStop) {
    dom.btnStop.addEventListener("click", () => {
      abortCurrentRequest();
    });
  }

  // Session item clicks (select, rename, delete)
  dom.conversationList.addEventListener("click", (e) => {
    const delBtn = e.target.closest("[data-del-id]");
    if (delBtn) {
      e.stopPropagation();
      const id = delBtn.dataset.delId;
      if (confirm("Delete this conversation session?")) {
        api(`/api/conversations/${id}`, { method: "DELETE" }).then(() => {
          if (state.activeConversationId === id) createNewSession();
          loadConversations(dom.conversationSearchInput.value.trim());
        });
      }
      return;
    }

    const renameBtn = e.target.closest("[data-rename-id]");
    if (renameBtn) {
      e.stopPropagation();
      const id = renameBtn.dataset.renameId;
      renameConversationModal(id);
      return;
    }

    const item = e.target.closest(".conversation-item");
    if (item) {
      selectConversation(item.dataset.id);
    }
  });

  // Memory Modal Actions
  document.getElementById("btnShowAddMemory").addEventListener("click", () => {
    document.getElementById("addMemoryForm").style.display = "block";
  });
  document.getElementById("btnCancelMemory").addEventListener("click", () => {
    document.getElementById("addMemoryForm").style.display = "none";
  });
  document.getElementById("btnSaveMemory").addEventListener("click", async () => {
    const cat = document.getElementById("newMemoryCategory").value;
    const content = document.getElementById("newMemoryContent").value.trim();
    const kw = document.getElementById("newMemoryKeywords").value.trim();
    if (!content) return alert("Content required");

    try {
      await api("/api/memories", {
        method: "POST",
        body: JSON.stringify({ category: cat, content, keywords: kw || null }),
      });
      document.getElementById("newMemoryContent").value = "";
      document.getElementById("addMemoryForm").style.display = "none";
      loadMemories();
    } catch (err) {
      alert("Save failed: " + err.message);
    }
  });

  // Memory Filters
  document.querySelectorAll("[data-mem-filter]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-mem-filter]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadMemories(btn.dataset.memFilter, document.getElementById("memorySearchInput").value);
    });
  });
  document.getElementById("memorySearchInput").addEventListener("input", (e) => {
    const activeTab = document.querySelector("[data-mem-filter].active");
    loadMemories(activeTab ? activeTab.dataset.memFilter : "", e.target.value);
  });

  // Projects Modal Form
  document.getElementById("btnShowNewProjectForm").addEventListener("click", () => {
    document.getElementById("newProjectForm").style.display = "block";
  });
  document.getElementById("btnCancelProject").addEventListener("click", () => {
    document.getElementById("newProjectForm").style.display = "none";
  });
  document.getElementById("btnSaveProject").addEventListener("click", async () => {
    const name = document.getElementById("newProjectName").value.trim();
    const desc = document.getElementById("newProjectDesc").value.trim();
    if (!name) return alert("Project name required");
    try {
      const p = await api("/api/projects", {
        method: "POST",
        body: JSON.stringify({ name, description: desc }),
      });
      state.activeProjectId = p.id;
      document.getElementById("newProjectName").value = "";
      document.getElementById("newProjectDesc").value = "";
      document.getElementById("newProjectForm").style.display = "none";
      loadProjects();
      loadTasksForProject(p.id);
    } catch (err) {
      alert("Failed to create project: " + err.message);
    }
  });

  // Task Add in Project Modal
  document.getElementById("btnShowNewTaskForm").addEventListener("click", () => {
    if (!state.activeProjectId) return alert("Please select or create a project first.");
    document.getElementById("newTaskForm").style.display = "block";
  });
  document.getElementById("btnCancelTask").addEventListener("click", () => {
    document.getElementById("newTaskForm").style.display = "none";
  });
  document.getElementById("btnSaveTask").addEventListener("click", async () => {
    const title = document.getElementById("newTaskTitle").value.trim();
    const desc = document.getElementById("newTaskDesc").value.trim();
    const due = document.getElementById("newTaskDueDate").value || null;
    if (!title) return alert("Task title required");
    try {
      await api("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          project_id: state.activeProjectId,
          title,
          description: desc,
          due_date: due,
        }),
      });
      document.getElementById("newTaskTitle").value = "";
      document.getElementById("newTaskDesc").value = "";
      document.getElementById("newTaskForm").style.display = "none";
      loadTasksForProject(state.activeProjectId);
    } catch (err) {
      alert("Failed to create task: " + err.message);
    }
  });

  // Propose Test Run from Workspace modal
  document.getElementById("btnProposeTestRun").addEventListener("click", async () => {
    const cmd = prompt("Enter allowlisted test command to propose:", "pytest -v");
    if (!cmd) return;
    try {
      const prop = await api("/api/workspace/command", {
        method: "POST",
        body: JSON.stringify({ command: cmd, reason: "Manual workspace test execution trigger" }),
      });
      alert(`Approval proposed (#${prop.id.substring(0, 8)}). Review and approve in Approvals tab.`);
      refreshPendingApprovals();
    } catch (err) {
      alert("Error: " + err.message);
    }
  });

  // Settings Modal Triggers
  if (dom.btnOpenSettingsModal) {
    dom.btnOpenSettingsModal.addEventListener("click", () => {
      openModal(dom.modalSettings);
      loadSettingsModal();
    });
  }
  if (dom.btnTopbarSettings) {
    dom.btnTopbarSettings.addEventListener("click", () => {
      openModal(dom.modalSettings);
      loadSettingsModal();
    });
  }
  if (dom.btnRunDiagnostics) {
    dom.btnRunDiagnostics.addEventListener("click", async () => {
      dom.btnRunDiagnostics.disabled = true;
      showToast("Running provider connectivity diagnostics...", "info");
      await checkHealth();
      await loadSettingsModal();
      dom.btnRunDiagnostics.disabled = false;
      showToast("Diagnostics passed: Engine is ready", "success");
    });
  }

  // Global Keyboard Shortcuts
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (currentAbortController) {
        abortCurrentRequest();
      } else {
        closeAllModals();
        closeMobileSidebar();
      }
    }
    if ((e.ctrlKey || e.metaKey) && e.key === "[") {
      e.preventDefault();
      toggleSidebarCollapse();
    }
  });
}

// Approvals Modal Loader
async function loadModalApprovals(statusFilter = "") {
  const container = document.getElementById("modalApprovalsList");
  try {
    const url = statusFilter ? `/api/approvals?status=${statusFilter}` : `/api/approvals`;
    const list = await api(url);
    if (!list.length) {
      container.innerHTML = `<div class="empty-state">
        <div class="empty-state-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        </div>
        <div class="empty-state-title">No approval records found</div>
        <div class="empty-state-desc">Actions requiring human confirmation (file patches, commands, tasks) will appear here.</div>
      </div>`;
      return;
    }
    container.innerHTML = list.map(a => `
      <div class="approval-item-card">
        <div class="approval-item-header">
          <strong style="font-size:0.86rem; color:var(--text-primary);"><code style="font-size:0.75rem; color:var(--accent-primary);">${escapeHtml(a.action_type)}</code> on ${escapeHtml(a.target)}</strong>
          <span class="status-pill ${a.status === 'SUCCEEDED' ? 'ready' : (a.status === 'REJECTED' ? 'rejected' : 'pending')}">
            <span class="status-pill-dot"></span>
            <span>${escapeHtml(a.status)}</span>
          </span>
        </div>
        <div class="text-muted" style="font-size:0.75rem;">Reason: ${escapeHtml(a.reason)} | Risk: ${escapeHtml(a.risk)}</div>
        ${a.status === 'PENDING_APPROVAL' ? `
          <div class="btn-group mt-1">
            <button class="btn btn-xs btn-emerald" onclick="handleApproveAction('${a.id}'); loadModalApprovals('${statusFilter}');">Approve</button>
            <button class="btn btn-xs btn-rose" onclick="handleRejectAction('${a.id}'); loadModalApprovals('${statusFilter}');">Reject</button>
          </div>
        ` : ''}
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Failed to load approvals: ${err.message}</div>`;
  }
}

// Settings & Provider Diagnostics Loader
async function loadSettingsModal() {
  try {
    const health = await api("/api/health");
    const activeProvider = health.active_provider || state.activeProvider || "ollama";
    const isLocal = activeProvider === "ollama";

    const pillEl = document.getElementById("settingsProviderPill");
    const textEl = document.getElementById("settingsProviderText");
    const activeEl = document.getElementById("settingsActiveProvider");
    const localModelEl = document.getElementById("settingsLocalModel");
    const cloudModelEl = document.getElementById("settingsCloudModel");
    const ollamaUrlEl = document.getElementById("settingsOllamaUrl");
    const wsPathEl = document.getElementById("settingsWorkspacePath");

    if (pillEl && textEl) {
      pillEl.className = `status-pill ${health.is_ready ? 'ready' : 'warning'}`;
      textEl.textContent = isLocal ? "Local Nemotron (Ollama)" : "Cloud Nemotron (Nebius)";
    }
    if (activeEl) activeEl.textContent = activeProvider.toUpperCase();
    if (localModelEl) localModelEl.textContent = health.model || "nemotron-3.5-bolt:e4b";
    if (cloudModelEl) cloudModelEl.textContent = "nvidia/nemotron-3-super-70b-instruct";
    if (ollamaUrlEl) ollamaUrlEl.textContent = "http://127.0.0.1:11434";
    if (wsPathEl) wsPathEl.textContent = "./workspace";

    // Query Hermes Agent Backend Status
    try {
      const hStatus = await api("/api/hermes/status");
      const hPill = document.getElementById("settingsHermesStatusPill");
      const hText = document.getElementById("settingsHermesStatusText");
      const hPath = document.getElementById("settingsHermesPath");
      const hVer = document.getElementById("settingsHermesVersion");

      if (hPill && hText) {
        hPill.className = `status-pill ${hStatus.available ? 'ready' : 'warning'}`;
        hText.textContent = hStatus.available
          ? (hStatus.ollama_ready ? "Ready (Ollama Nemotron)" : "Ready (Cloud)")
          : "Unavailable";
      }
      if (hPath) hPath.textContent = hStatus.binary_path || "Not found";
      if (hVer) hVer.textContent = hStatus.version || "0.22.5";
    } catch (hermesErr) {
      console.warn("Failed to load Hermes status diagnostics:", hermesErr);
    }
  } catch (err) {
    console.error("Failed to load settings diagnostics:", err);
  }
}

// Initial Boot
window.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  checkHealth();
  loadConversations();
  loadProjects();
  refreshPendingApprovals();
});
