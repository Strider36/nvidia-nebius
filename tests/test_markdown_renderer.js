/**
 * Automated tests for Aegis AI frontend Markdown Renderer & Syntax Highlighter.
 * Runs via Node.js: node tests/test_markdown_renderer.js
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Read app.js
const appJsPath = path.join(__dirname, '..', 'frontend', 'app.js');
const appJsContent = fs.readFileSync(appJsPath, 'utf8');

// Mock browser environment for extraction
const vm = require('vm');
const dummyEl = {
  style: {},
  classList: { add: () => {}, remove: () => {}, toggle: () => {} },
  appendChild: () => {},
  addEventListener: () => {},
  querySelector: () => null,
  querySelectorAll: () => [],
};

const sandbox = {
  document: {
    getElementById: () => dummyEl,
    querySelectorAll: () => [],
    querySelector: () => dummyEl,
    createElement: (tag) => ({ ...dummyEl, tagName: tag.toUpperCase() }),
    body: { ...dummyEl },
  },
  window: {
    addEventListener: () => {},
  },
  navigator: {},
  setInterval: () => 1,
  clearInterval: () => {},
  setTimeout: (fn) => fn(),
  console: console,
};
vm.createContext(sandbox);

// Extract helper functions
vm.runInContext(`
  ${appJsContent}
`, sandbox);

const { escapeHtml, sanitizeUrl, highlightSyntax, renderSafeMarkdown } = sandbox;

console.log('--- Running Aegis AI Markdown & Syntax Highlighter Tests ---');

// 1. Safe URL Sanitizer
assert.strictEqual(sanitizeUrl('https://example.com'), 'https://example.com');
assert.strictEqual(sanitizeUrl('http://localhost:8000'), 'http://localhost:8000');
assert.strictEqual(sanitizeUrl('mailto:dev@example.com'), 'mailto:dev@example.com');
assert.strictEqual(sanitizeUrl('#section-1'), '#section-1');
assert.strictEqual(sanitizeUrl('/workspace'), '/workspace');
// Disallowed XSS schemes
assert.strictEqual(sanitizeUrl('javascript:alert(1)'), '#');
assert.strictEqual(sanitizeUrl('data:text/html,<script>'), '#');
assert.strictEqual(sanitizeUrl('vbscript:msgbox(1)'), '#');
console.log('✓ Safe URL sanitizer tests passed');

// 2. Syntax Highlighter - Python
const pyCode = 'def calculate_sum(a: int) -> int:\n    # Return result\n    return a + 10';
const pyHigh = highlightSyntax(pyCode, 'python');
assert(pyHigh.includes('class="tok-keyword">def</span>'), 'def should be keyword');
assert(pyHigh.includes('class="tok-keyword">return</span>'), 'return should be keyword');
assert(pyHigh.includes('class="tok-comment"># Return result</span>'), 'comment should be highlighted');
assert(pyHigh.includes('class="tok-number">10</span>'), '10 should be number');
console.log('✓ Python syntax highlighting tests passed');

// 3. Syntax Highlighter - JavaScript / TypeScript
const jsCode = 'const fetchData = async () => {\n  // Fetch items\n  return true;\n};';
const jsHigh = highlightSyntax(jsCode, 'javascript');
assert(jsHigh.includes('class="tok-keyword">const</span>'), 'const should be keyword');
assert(jsHigh.includes('class="tok-keyword">async</span>'), 'async should be keyword');
assert(jsHigh.includes('class="tok-boolean">true</span>'), 'true should be boolean');
console.log('✓ JavaScript/TypeScript syntax highlighting tests passed');

// 4. Syntax Highlighter - SQL
const sqlCode = 'SELECT id, name FROM users WHERE status = 1;';
const sqlHigh = highlightSyntax(sqlCode, 'sql');
assert(sqlHigh.includes('class="tok-keyword">SELECT</span>'), 'SELECT should be keyword');
assert(sqlHigh.includes('class="tok-keyword">FROM</span>'), 'FROM should be keyword');
assert(sqlHigh.includes('class="tok-keyword">WHERE</span>'), 'WHERE should be keyword');
console.log('✓ SQL syntax highlighting tests passed');

// 5. Syntax Highlighter - JSON
const jsonCode = '{\n  "status": "ready",\n  "count": 42,\n  "ok": true\n}';
const jsonHigh = highlightSyntax(jsonCode, 'json');
assert(jsonHigh.includes('class="tok-keyword">&quot;status&quot;</span>'), 'json key should be keyword');
assert(jsonHigh.includes('class="tok-string">&quot;ready&quot;</span>'), 'json string should be string');
assert(jsonHigh.includes('class="tok-number">42</span>'), 'json number should be number');
assert(jsonHigh.includes('class="tok-boolean">true</span>'), 'json boolean should be boolean');
console.log('✓ JSON syntax highlighting tests passed');

// 6. Syntax Highlighter - Bash
const bashCode = 'if [ -f "test.txt" ]; then\n  echo "found"\nfi';
const bashHigh = highlightSyntax(bashCode, 'bash');
assert(bashHigh.includes('class="tok-keyword">if</span>'), 'if should be keyword');
assert(bashHigh.includes('class="tok-keyword">then</span>'), 'then should be keyword');
assert(bashHigh.includes('class="tok-keyword">echo</span>'), 'echo should be keyword');
console.log('✓ Bash syntax highlighting tests passed');

// 7. Markdown Link Rendering & XSS Protection
const mdWithSafeLink = 'Here is [Docs](https://docs.aegis.dev) for reference.';
const htmlSafeLink = renderSafeMarkdown(mdWithSafeLink);
assert(htmlSafeLink.includes('<a href="https://docs.aegis.dev" target="_blank" rel="noopener noreferrer" class="msg-link">Docs</a>'));

const mdWithXssLink = 'Malicious link: [Click Me](javascript:stealCookies())';
const htmlXssLink = renderSafeMarkdown(mdWithXssLink);
assert(!htmlXssLink.includes('javascript:stealCookies()'), 'javascript: link must be blocked');
assert(htmlXssLink.includes('href="#"'), 'sanitized to #');

const mdWithRawScript = 'Hello <script>alert("hack")</script> World';
const htmlRawScript = renderSafeMarkdown(mdWithRawScript);
assert(!htmlRawScript.includes('<script>'), 'raw script tag must be escaped');
assert(htmlRawScript.includes('&lt;script&gt;'));
console.log('✓ Markdown link rendering and XSS sanitization tests passed');

// 8. Markdown Headings & Formatting
const mdHeadings = '# Heading 1\n## Heading 2\n### Heading 3\n\n**Bold Text** and *Italic Text* and `inline code`.';
const htmlHeadings = renderSafeMarkdown(mdHeadings);
assert(htmlHeadings.includes('<h1 class="msg-h1">Heading 1</h1>'));
assert(htmlHeadings.includes('<h2 class="msg-h2">Heading 2</h2>'));
assert(htmlHeadings.includes('<h3 class="msg-h3">Heading 3</h3>'));
assert(htmlHeadings.includes('<strong>Bold Text</strong>'));
assert(htmlHeadings.includes('<em>Italic Text</em>'));
assert(htmlHeadings.includes('<code class="inline-code">inline code</code>'));
console.log('✓ Markdown headings and inline formatting tests passed');

// 9. Markdown Tables
const mdTable = '| Name | Role | Status |\n| :--- | :---: | ---: |\n| Alice | Lead | Active |\n| Bob | Dev | Inactive |';
const htmlTable = renderSafeMarkdown(mdTable);
assert(htmlTable.includes('class="msg-table-wrapper"'));
assert(htmlTable.includes('class="msg-table"'));
assert(htmlTable.includes('<th>Name</th>'));
assert(htmlTable.includes('<td>Alice</td>'));
console.log('✓ Markdown tables tests passed');

// 10. Nested Lists
const mdNested = '- Item 1\n  - Subitem 1a\n  - Subitem 1b\n- Item 2';
const htmlNested = renderSafeMarkdown(mdNested);
assert(htmlNested.includes('<ul class="msg-ul"><li>Item 1'));
assert(htmlNested.includes('Subitem 1a'));
assert(htmlNested.includes('Item 2'));
console.log('✓ Nested lists tests passed');

// 11. Unclosed Fenced Code Block
const mdUnclosedCode = '```python\ndef unfinished():\n    pass';
const htmlUnclosed = renderSafeMarkdown(mdUnclosedCode);
assert(htmlUnclosed.includes('class="code-block-wrapper"'), 'Unclosed code block should be handled gracefully');
assert(htmlUnclosed.includes('class="tok-keyword">def</span>'));
console.log('✓ Unclosed code block recovery tests passed');

console.log('ALL 11 JAVASCRIPT MARKDOWN & SYNTAX TESTS PASSED SUCCESFULLY!\n');
