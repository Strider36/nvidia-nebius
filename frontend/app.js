/**
 * Aegis AI — Frontend Application Logic
 * Pure Vanilla JavaScript (Zero External Dependencies)
 */

// Application State
const state = {
  activeConversationId: null,
  activeProjectId: null,
  activeSkillId: "",
  health: null,
  projects: [],
  skills: [],
  pendingApprovals: [],
};

// DOM Elements
const dom = {
  systemStatusBadge: document.getElementById("systemStatusBadge"),
  systemStatusText: document.getElementById("systemStatusText"),
  sidebarModelId: document.getElementById("sidebarModelId"),
  btnNewSession: document.getElementById("btnNewSession"),
  projectSelector: document.getElementById("projectSelector"),
  btnOpenProjectsModal: document.getElementById("btnOpenProjectsModal"),
  conversationList: document.getElementById("conversationList"),
  activeSessionTitle: document.getElementById("activeSessionTitle"),
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
  pendingCountBadge: document.getElementById("pendingCountBadge"),
  // Modals
  modalProjects: document.getElementById("modalProjects"),
  modalMemory: document.getElementById("modalMemory"),
  modalSkills: document.getElementById("modalSkills"),
  modalApprovals: document.getElementById("modalApprovals"),
  modalWorkspace: document.getElementById("modalWorkspace"),
  modalAudit: document.getElementById("modalAudit"),
};

// Utilities
function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " " + d.toLocaleDateString();
  } catch (e) {
    return isoStr;
  }
}

// Enhanced Markdown formatting helper with safe HTML escaping and rich widgets
function renderSafeMarkdown(text) {
  if (!text) return "";

  // 0. Safety catch: if any raw <<<PROPOSE_...>>> tags remain in text, convert to human-readable markdown
  let raw = text.replace(/<<<PROPOSE_TASK\s+([^>]+)>{3,4}/g, (match, attrs) => {
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

  // 1. Extract and preserve code blocks
  const codeBlocks = [];
  let processed = raw.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
    const cleanCode = code.trim();
    const escapedCode = escapeHtml(cleanCode);
    const langLabel = lang ? escapeHtml(lang) : "code";
    codeBlocks.push(`
      <div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang-tag">${langLabel}</span>
          <button type="button" class="btn-copy-code" onclick="navigator.clipboard.writeText(this.dataset.code); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 1500);" data-code="${escapeHtml(cleanCode)}">Copy</button>
        </div>
        <pre><code class="language-${langLabel}">${escapedCode}</code></pre>
      </div>
    `);
    return placeholder;
  });

  // 2. Escape remaining text for strict XSS prevention
  processed = escapeHtml(processed);

  // 3. Inline code
  processed = processed.replace(/`([^`]+)`/g, (match, code) => `<code class="inline-code">${code}</code>`);

  // 4. Bold and italics
  processed = processed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  processed = processed.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // 5. Blockquotes (lines starting with &gt;)
  processed = processed.replace(/(?:^|\n)(&gt;[^\n]+(?:\n&gt;[^\n]+)*)/g, (match, block) => {
    const content = block.split('\n').map(line => line.replace(/^&gt;\s?/, '')).join('<br>');
    return `\n<blockquote class="msg-blockquote">${content}</blockquote>\n`;
  });

  // 6. Section Headers
  processed = processed.replace(/^#### (.*?)$/gm, '<h4 class="msg-h4">$1</h4>');
  processed = processed.replace(/^### (.*?)$/gm, '<h3 class="msg-h3">$1</h3>');
  processed = processed.replace(/^## (.*?)$/gm, '<h2 class="msg-h2">$1</h2>');
  processed = processed.replace(/^# (.*?)$/gm, '<h1 class="msg-h1">$1</h1>');

  // 7. Horizontal Rules
  processed = processed.replace(/^(?:---|___|\*\*\*)$/gm, '<hr class="msg-hr">');

  // 7.5 Markdown Tables
  processed = processed.replace(/(?:^|\n)((?:\|[^\n]+\|\n?)+)/g, (match, tableText) => {
    const lines = tableText.trim().split('\n').map(l => l.trim()).filter(l => l.startsWith('|') && l.endsWith('|'));
    if (lines.length < 2) return match;
    const sepIdx = lines.findIndex(l => /^\|[\s\-:|]+\|$/.test(l));
    if (sepIdx === -1) return match;

    const parseRow = (rowLine) => {
      const rawCols = rowLine.slice(1, -1).split('|');
      return rawCols.map(c => c.trim().replace(/&lt;br\s*\/?&gt;/gi, '<br>'));
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

  // 8. Unordered Lists (lines starting with - or * or •)
  processed = processed.replace(/(?:^|\n)((?:[-*•] [^\n]+\n?)+)/g, (match, list) => {
    const items = list.trim().split('\n').map(item => {
      const clean = item.replace(/^[-*•]\s+/, '');
      return `<li>${clean}</li>`;
    }).join('');
    return `\n<ul class="msg-ul">${items}</ul>\n`;
  });

  // 9. Ordered Lists (lines starting with 1. 2. etc)
  processed = processed.replace(/(?:^|\n)((?:\d+\. [^\n]+\n?)+)/g, (match, list) => {
    const items = list.trim().split('\n').map(item => {
      const clean = item.replace(/^\d+\.\s+/, '');
      return `<li>${clean}</li>`;
    }).join('');
    return `\n<ol class="msg-ol">${items}</ol>\n`;
  });

  // 10. Paragraphs / Linebreaks
  processed = processed.replace(/\n\n+/g, '<br><br>');
  processed = processed.replace(/\n/g, '<br>');

  // Clean up superfluous breaks around block-level elements
  processed = processed.replace(/(?:<br\s*\/?>)+(<\/?(?:h[1-4]|ul|ol|li|blockquote|hr|table|thead|tbody|tr|th|td|div|pre))/gi, '$1');
  processed = processed.replace(/(<\/(?:h[1-4]|ul|ol|blockquote|hr|table|div|pre)>)(?:<br\s*\/?>)+/gi, '$1');

  // 11. Restore preserved code blocks
  codeBlocks.forEach((block, idx) => {
    processed = processed.replace(`__CODE_BLOCK_${idx}__`, block);
  });

  return processed;
}

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

// System Health
async function checkHealth() {
  try {
    const data = await api("/api/health");
    state.health = data;
    dom.sidebarModelId.textContent = data.model_id.split("/").pop() || data.model_id;
    
    if (data.is_ready) {
      dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot ready";
      dom.systemStatusText.textContent = "Ready (Nebius Connected)";
    } else {
      dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot";
      dom.systemStatusText.textContent = data.has_api_key ? "Degraded" : "API Key Required";
    }
  } catch (err) {
    dom.systemStatusBadge.querySelector(".status-dot").className = "status-dot";
    dom.systemStatusText.textContent = "Offline";
  }
}

// Conversations Management
async function loadConversations() {
  try {
    const url = state.activeProjectId 
      ? `/api/conversations?project_id=${encodeURIComponent(state.activeProjectId)}` 
      : `/api/conversations`;
    const convs = await api(url);
    renderConversationList(convs);
  } catch (err) {
    console.error("Failed to load conversations:", err);
  }
}

function renderConversationList(convs) {
  if (!convs.length) {
    dom.conversationList.innerHTML = `<div class="empty-state">No conversations yet</div>`;
    return;
  }
  dom.conversationList.innerHTML = convs.map(c => `
    <div class="conversation-item ${c.id === state.activeConversationId ? 'active' : ''}" data-id="${c.id}">
      <span class="conversation-title">${escapeHtml(c.title)}</span>
      <button class="btn-close btn-del" data-del-id="${c.id}" title="Delete session">&times;</button>
    </div>
  `).join("");
}

async function selectConversation(convId) {
  state.activeConversationId = convId;
  try {
    const conv = await api(`/api/conversations/${convId}`);
    dom.activeSessionTitle.textContent = conv.title || "Active Session";
    renderMessages(conv.messages || []);
    loadConversations();
  } catch (err) {
    alert("Error loading conversation: " + err.message);
  }
}

function createNewSession() {
  state.activeConversationId = null;
  dom.activeSessionTitle.textContent = "New Session";
  dom.messagesContainer.innerHTML = "";
  dom.messagesContainer.appendChild(dom.welcomeHero);
  loadConversations();
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
        <span>🧠 Memories Applied:</span>
        ${m.retrieved_memories.map(rm => `<strong>[${escapeHtml(rm.category)}]</strong> ${escapeHtml(rm.content.substring(0, 45))}...`).join(" | ")}
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
    </div>
  `;

  dom.messagesContainer.appendChild(row);
  dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
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
    const dueBadge = approval.details.due_date ? `<span class="badge badge-muted">📅 Due: ${escapeHtml(approval.details.due_date)}</span>` : '';
    diffOrCmd = `
      <div class="approval-task-card">
        <div class="approval-task-header">
          <span class="approval-task-title">📋 ${escapeHtml(approval.details.title || approval.target)}</span>
          ${dueBadge}
        </div>
        ${approval.details.description ? `<p class="approval-task-desc">${escapeHtml(approval.details.description)}</p>` : ''}
      </div>
    `;
  }

  card.innerHTML = `
    <div class="approval-card-header">
      <span class="approval-card-type">⚠️ Approval Required: ${escapeHtml(approval.action_type)}</span>
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
      dom.topPendingText.textContent = `${pending.length} Action Pending Approval`;
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
      <div class="thinking-shimmer-bar"></div>
    </div>
  `;

  dom.messagesContainer.appendChild(row);
  dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;

  const steps = [
    "Consulting persistent local memory...",
    "Executing NVIDIA Nemotron reasoning...",
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

// Chat Form Submission
dom.chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = dom.messageInput.value.trim();
  if (!text) return;

  // Render user message immediately
  appendMessageToDom({
    role: "user",
    content: text,
    created_at: new Date().toISOString(),
  });

  dom.messageInput.value = "";
  dom.messageInput.style.height = "auto";
  dom.btnSend.disabled = true;
  const originalSendContent = dom.btnSend.innerHTML;
  dom.btnSend.innerHTML = '<span class="spinner-icon"></span>';

  const removeThinking = showThinkingIndicator();

  try {
    const payload = {
      message: text,
      conversation_id: state.activeConversationId,
      project_id: state.activeProjectId,
      skill_id: state.activeSkillId || null,
    };

    const res = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    removeThinking();
    state.activeConversationId = res.conversation_id;

    // Render assistant message
    appendMessageToDom({
      role: "assistant",
      content: res.assistant_message,
      retrieved_memories: res.retrieved_memories,
      skill_id: state.activeSkillId,
      created_at: new Date().toISOString(),
    });

    // If action(s) were proposed, render approval cards directly
    if (res.pending_approvals && res.pending_approvals.length > 0) {
      res.pending_approvals.forEach(appr => renderApprovalCardInMessage(appr));
      refreshPendingApprovals();
    } else if (res.pending_approval) {
      renderApprovalCardInMessage(res.pending_approval);
      refreshPendingApprovals();
    }

    loadConversations();
  } catch (err) {
    removeThinking();
    appendMessageToDom({
      role: "assistant",
      content: `⚠️ Communication Error: ${err.message}`,
      created_at: new Date().toISOString(),
    });
  } finally {
    dom.btnSend.disabled = false;
    dom.btnSend.innerHTML = originalSendContent;
  }
});

// Projects Management
async function loadProjects() {
  try {
    const list = await api("/api/projects");
    state.projects = list;
    
    // Populate select
    dom.projectSelector.innerHTML = `<option value="">(Global / No Project)</option>` + 
      list.map(p => `<option value="${p.id}" ${p.id === state.activeProjectId ? 'selected' : ''}>${escapeHtml(p.name)}</option>`).join("");
    
    // Update badge
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
    container.innerHTML = `<div class="empty-state">No projects created yet</div>`;
    return;
  }
  container.innerHTML = list.map(p => `
    <div class="list-item-card ${p.id === state.activeProjectId ? 'selected' : ''}" onclick="selectProjectModal('${p.id}')">
      <div>
        <strong>${escapeHtml(p.name)}</strong>
        <div class="text-muted" style="font-size:0.75rem;">${escapeHtml(p.description || 'No description')}</div>
      </div>
      <button class="btn-close" onclick="event.stopPropagation(); deleteProject('${p.id}')">&times;</button>
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
    container.innerHTML = `<div class="empty-state">Select a project to view tasks</div>`;
    return;
  }
  try {
    const tasks = await api(`/api/tasks?project_id=${projectId}`);
    if (!tasks.length) {
      container.innerHTML = `<div class="empty-state">No tasks in this project</div>`;
      return;
    }
    container.innerHTML = tasks.map(t => `
      <div class="list-item-card">
        <div>
          <strong>${escapeHtml(t.title)}</strong>
          <div class="text-muted" style="font-size:0.75rem;">${escapeHtml(t.description || '')}</div>
          <span class="badge ${t.status === 'completed' ? 'badge-emerald' : 'badge-amber'}">${t.status}</span>
        </div>
        <div class="btn-group">
          <button class="btn btn-xs btn-outline" onclick="toggleTaskStatus('${t.id}', '${t.status}')">
            ${t.status === 'completed' ? 'Reopen' : 'Complete'}
          </button>
          <button class="btn-close" onclick="deleteTask('${t.id}', '${projectId}')">&times;</button>
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
      grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">No persistent memories stored</div>`;
      return;
    }

    grid.innerHTML = memories.map(m => `
      <div class="memory-card">
        <div class="memory-category-tag">${escapeHtml(m.category)}</div>
        <p>${escapeHtml(m.content)}</p>
        ${m.keywords ? `<div class="text-muted mt-1" style="font-size:0.72rem;">Keywords: ${escapeHtml(m.keywords)}</div>` : ''}
        <button class="btn-close" style="position:absolute; top:8px; right:8px;" onclick="deleteMemoryItem('${m.id}')">&times;</button>
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
        <button class="btn btn-outline btn-sm" onclick="activateSkill('${s.id}', '${s.name}')">
          Use This Skill
        </button>
      </div>
    `).join("");
  } catch (err) {
    grid.innerHTML = `<div class="empty-state">Failed to load skills: ${err.message}</div>`;
  }
}

window.activateSkill = function(id, name) {
  state.activeSkillId = id;
  // Update pills
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
      listEl.innerHTML = `<div class="empty-state">No files in authorized workspace</div>`;
      return;
    }
    listEl.innerHTML = data.files.map(f => `
      <div class="list-item-card" onclick="previewWorkspaceFile('${escapeHtml(f.path)}')">
        <span>📄 <strong>${escapeHtml(f.name)}</strong></span>
        <span class="text-muted">${f.size} B</span>
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
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No audit records yet</td></tr>`;
      return;
    }
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>${formatDate(l.timestamp)}</td>
        <td><code>${escapeHtml(l.action_type)}</code></td>
        <td>${escapeHtml(l.proposed_operation)}</td>
        <td><span class="badge ${l.approval_status === 'APPROVED' ? 'badge-emerald' : (l.approval_status === 'REJECTED' ? 'badge-rose' : 'badge-amber')}">${l.approval_status}</span></td>
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
  dom.btnNewSession.addEventListener("click", createNewSession);

  dom.btnRefreshStatus.addEventListener("click", () => {
    checkHealth();
    refreshPendingApprovals();
  });

  dom.projectSelector.addEventListener("change", (e) => {
    state.activeProjectId = e.target.value || null;
    loadProjects();
    loadConversations();
  });

  dom.btnOpenProjectsModal.addEventListener("click", () => {
    openModal(dom.modalProjects);
    loadProjects();
    loadTasksForProject(state.activeProjectId);
  });

  // Navigation Tabs
  document.querySelectorAll(".sidebar-nav .nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
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
    });
  });

  // Feature Card Prompts
  document.querySelectorAll(".feature-card").forEach(card => {
    card.addEventListener("click", () => {
      const prompt = card.dataset.prompt;
      if (prompt) {
        dom.messageInput.value = prompt;
        dom.messageInput.focus();
        dom.messageInput.dispatchEvent(new Event("input"));
      }
    });
  });

  // Auto-resize & Enter-to-send
  dom.messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      dom.chatForm.dispatchEvent(new Event("submit"));
    }
  });
  dom.messageInput.addEventListener("input", () => {
    dom.messageInput.style.height = "auto";
    dom.messageInput.style.height = Math.min(dom.messageInput.scrollHeight, 160) + "px";
  });

  // Skill Pills
  document.querySelectorAll(".skill-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const skillId = pill.dataset.skill;
      activateSkill(skillId, pill.textContent);
    });
  });

  // Quick review banner
  dom.btnQuickReview.addEventListener("click", () => {
    openModal(dom.modalApprovals);
    loadModalApprovals("PENDING_APPROVAL");
  });

  // Session click in sidebar
  dom.conversationList.addEventListener("click", (e) => {
    const delBtn = e.target.closest("[data-del-id]");
    if (delBtn) {
      e.stopPropagation();
      const id = delBtn.dataset.delId;
      if (confirm("Delete this session?")) {
        api(`/api/conversations/${id}`, { method: "DELETE" }).then(() => {
          if (state.activeConversationId === id) createNewSession();
          loadConversations();
        });
      }
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
}

// Approvals Modal Loader
async function loadModalApprovals(statusFilter = "") {
  const container = document.getElementById("modalApprovalsList");
  try {
    const url = statusFilter ? `/api/approvals?status=${statusFilter}` : `/api/approvals`;
    const list = await api(url);
    if (!list.length) {
      container.innerHTML = `<div class="empty-state">No approval records found</div>`;
      return;
    }
    container.innerHTML = list.map(a => `
      <div class="list-item-card" style="flex-direction:column; align-items:flex-start; gap:8px;">
        <div style="display:flex; justify-content:space-between; width:100%;">
          <strong><code>${escapeHtml(a.action_type)}</code> on ${escapeHtml(a.target)}</strong>
          <span class="badge ${a.status === 'SUCCEEDED' ? 'badge-emerald' : (a.status === 'REJECTED' ? 'badge-rose' : 'badge-amber')}">${a.status}</span>
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

// Initial Boot
window.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  checkHealth();
  loadConversations();
  loadProjects();
  refreshPendingApprovals();
});

