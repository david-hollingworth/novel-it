/**
 * editor.js — bespoke markdown editor for NovelIt
 *
 * No external library dependencies. Requires marked.umd.js to be loaded first.
 *
 * Usage:
 *   const editor = initEditor({
 *       elementId:    'my-textarea',      // required
 *       wordCountId:  'word-count',       // optional — element to update with live word count
 *       saveStatusId: 'save-status',      // optional — element to show Saved / Unsaved / Saving
 *       saveBtnId:    'save-btn',         // optional — button to disable during save
 *       saveUrl:      '/path/to/save/',   // optional — enables Ctrl+S and save()
 *       csrfToken:    'abc123',           // required if saveUrl is set
 *       placeholder:  'Start writing…',  // optional
 *   });
 *
 *   // editor.getValue()  → current markdown content
 *   // editor.save()      → programmatically trigger a save
 */
function initEditor(options = {}) {
    const {
        elementId,
        wordCountId   = null,
        saveStatusId  = null,
        saveBtnId     = null,
        saveUrl       = null,
        csrfToken     = null,
        placeholder   = 'Start writing…',
    } = options;

    const textarea = document.getElementById(elementId);
    if (!textarea) {
        console.error(`initEditor: element #${elementId} not found`);
        return null;
    }

    // -----------------------------------------------------------------------
    // Helper refs
    // -----------------------------------------------------------------------
    const wordCountEl  = wordCountId  ? document.getElementById(wordCountId)  : null;
    const saveStatusEl = saveStatusId ? document.getElementById(saveStatusId) : null;
    const saveBtnEl    = saveBtnId    ? document.getElementById(saveBtnId)    : null;

    // -----------------------------------------------------------------------
    // Build editor DOM
    //
    // Structure:
    //   .ni-editor                  — outer container (also fullscreen target)
    //     .ni-toolbar               — button bar
    //     .ni-edit-area             — the plain textarea
    //     .ni-preview-area          — rendered HTML preview (hidden by default)
    //     .ni-help-modal            — markdown cheat sheet modal
    // -----------------------------------------------------------------------
    const container = document.createElement('div');
    container.className = 'ni-editor';

    // Insert container before the textarea, then move textarea inside
    textarea.parentNode.insertBefore(container, textarea);

    // --- Toolbar ---
    const toolbar = document.createElement('div');
    toolbar.className = 'ni-toolbar';
    container.appendChild(toolbar);

    // --- Edit area (wraps textarea) ---
    const editArea = document.createElement('div');
    editArea.className = 'ni-edit-area';
    textarea.placeholder = placeholder;
    editArea.appendChild(textarea);
    container.appendChild(editArea);

    // --- Preview area ---
    const previewArea = document.createElement('div');
    previewArea.className = 'ni-preview-area';
    previewArea.style.display = 'none';
    container.appendChild(previewArea);

    // --- Help modal ---
    const helpModal = document.createElement('div');
    helpModal.className = 'ni-help-modal';
    helpModal.style.display = 'none';
    helpModal.innerHTML = `
        <div class="ni-help-inner">
            <div class="ni-help-header">
                <h3>Markdown Reference</h3>
                <button class="ni-help-close" title="Close">&times;</button>
            </div>
            <div class="ni-help-body">
                <table class="ni-help-table">
                    <thead><tr><th>Syntax</th><th>Result</th></tr></thead>
                    <tbody>
                        <tr><td><code># Heading 1</code></td><td>Heading 1</td></tr>
                        <tr><td><code>## Heading 2</code></td><td>Heading 2</td></tr>
                        <tr><td><code>### Heading 3</code></td><td>Heading 3</td></tr>
                        <tr><td><code>**bold**</code></td><td><strong>bold</strong></td></tr>
                        <tr><td><code>*italic*</code></td><td><em>italic</em></td></tr>
                        <tr><td><code>~~strikethrough~~</code></td><td><s>strikethrough</s></td></tr>
                        <tr><td><code>> blockquote</code></td><td>Blockquote</td></tr>
                        <tr><td><code>- item</code></td><td>Unordered list</td></tr>
                        <tr><td><code>1. item</code></td><td>Ordered list</td></tr>
                        <tr><td><code>---</code></td><td>Horizontal rule</td></tr>
                        <tr><td><code>&#96;inline code&#96;</code></td><td><code>inline code</code></td></tr>
                        <tr><td><code>&#96;&#96;&#96;</code> (fenced block)</td><td>Code block</td></tr>
                        <tr><td><code>[text](url)</code></td><td>Link</td></tr>
                        <tr><td><code>![alt](url)</code></td><td>Image</td></tr>
                    </tbody>
                </table>
            </div>
        </div>`;
    container.appendChild(helpModal);

    // -----------------------------------------------------------------------
    // Toolbar button definitions
    // -----------------------------------------------------------------------
    const buttons = [
        {
            title: 'Bold (Ctrl+B)',
            label: '<strong>B</strong>',
            action: () => wrapSelection('**', '**'),
        },
        {
            title: 'Italic (Ctrl+I)',
            label: '<em>I</em>',
            action: () => wrapSelection('*', '*'),
        },
        {
            title: 'Strikethrough',
            label: '<s>S</s>',
            action: () => wrapSelection('~~', '~~'),
        },
        { separator: true },
        {
            title: 'Heading 1',
            label: 'H1',
            action: () => prefixLine('# '),
        },
        {
            title: 'Heading 2',
            label: 'H2',
            action: () => prefixLine('## '),
        },
        {
            title: 'Heading 3',
            label: 'H3',
            action: () => prefixLine('### '),
        },
        { separator: true },
        {
            title: 'Blockquote',
            label: '❝',
            action: () => prefixLine('> '),
        },
        {
            title: 'Unordered list',
            label: '•≡',
            action: () => prefixLine('- '),
        },
        {
            title: 'Ordered list',
            label: '1≡',
            action: () => prefixLine('1. '),
        },
        { separator: true },
        {
            title: 'Horizontal rule',
            label: '—',
            action: () => insertBlock('\n---\n'),
        },
        { separator: true },
        {
            id:    'ni-preview-btn',
            title: 'Toggle preview (Ctrl+P)',
            label: '👁',
            action: togglePreview,
        },
        {
            id:    'ni-fullscreen-btn',
            title: 'Toggle fullscreen (F11)',
            label: '⛶',
            action: toggleFullscreen,
        },
        { separator: true },
        {
            title: 'Markdown help',
            label: '?',
            action: toggleHelp,
        },
    ];

    buttons.forEach(btn => {
        if (btn.separator) {
            const sep = document.createElement('span');
            sep.className = 'ni-toolbar-sep';
            toolbar.appendChild(sep);
            return;
        }
        const b = document.createElement('button');
        b.type = 'button';
        b.title = btn.title;
        b.innerHTML = btn.label;
        b.className = 'ni-toolbar-btn';
        if (btn.id) b.id = btn.id;
        b.addEventListener('click', (e) => { e.preventDefault(); btn.action(); });
        toolbar.appendChild(b);
    });

    // -----------------------------------------------------------------------
    // Word count — mirrors server-side calculate_word_count() in models.py
    // -----------------------------------------------------------------------
    function clientWordCount(text) {
        if (!text || !text.trim()) return 0;
        // Remove fenced code blocks
        text = text.replace(/```[\s\S]*?```/g, '');
        // Remove inline code
        text = text.replace(/`[^`]*`/g, '');
        // Remove links but keep link text
        text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
        // Remove images
        text = text.replace(/!\[[^\]]*\]\([^)]+\)/g, '');
        // Remove headers
        text = text.replace(/^#+\s+/gm, '');
        // Remove bold/italic markers
        text = text.replace(/[*_]{1,3}/g, '');
        // Remove HTML tags
        text = text.replace(/<[^>]+>/g, '');
        // Count words
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        return words.length;
    }

    // -----------------------------------------------------------------------
    // Editor state
    // -----------------------------------------------------------------------
    let isPreviewing  = false;
    let isFullscreen  = false;
    let isDirty       = false;   // true whenever there are unsaved changes

    // -----------------------------------------------------------------------
    // Formatting helpers
    // -----------------------------------------------------------------------

    // Wrap the current selection with prefix/suffix, or insert placeholder
    function wrapSelection(before, after) {
        const start  = textarea.selectionStart;
        const end    = textarea.selectionEnd;
        const sel    = textarea.value.substring(start, end) || 'text';
        const insert = before + sel + after;
        textarea.setRangeText(insert, start, end, 'select');
        // Adjust selection to cover just the inner text
        textarea.selectionStart = start + before.length;
        textarea.selectionEnd   = start + before.length + sel.length;
        textarea.focus();
        triggerChange();
    }

    // Prefix the current line with a string
    function prefixLine(prefix) {
        const start     = textarea.selectionStart;
        const lineStart = textarea.value.lastIndexOf('\n', start - 1) + 1;
        textarea.setRangeText(prefix, lineStart, lineStart, 'end');
        textarea.focus();
        triggerChange();
    }

    // Insert a block (e.g. horizontal rule) at cursor position
    function insertBlock(text) {
        const pos = textarea.selectionStart;
        textarea.setRangeText(text, pos, pos, 'end');
        textarea.focus();
        triggerChange();
    }

    // -----------------------------------------------------------------------
    // Preview toggle
    // -----------------------------------------------------------------------
    function togglePreview() {
        isPreviewing = !isPreviewing;
        const btn = document.getElementById('ni-preview-btn');

        if (isPreviewing) {
            previewArea.innerHTML = marked.parse(textarea.value || '');
            editArea.style.display = 'none';
            previewArea.style.display = 'block';
            if (btn) btn.classList.add('ni-btn-active');
        } else {
            editArea.style.display = 'flex';
            previewArea.style.display = 'none';
            if (btn) btn.classList.remove('ni-btn-active');
            textarea.focus();
        }
    }

    // -----------------------------------------------------------------------
    // Fullscreen toggle
    // -----------------------------------------------------------------------
    function toggleFullscreen() {
        isFullscreen = !isFullscreen;
        const btn = document.getElementById('ni-fullscreen-btn');
        container.classList.toggle('ni-fullscreen', isFullscreen);
        if (btn) btn.classList.toggle('ni-btn-active', isFullscreen);
        if (!isPreviewing) textarea.focus();
    }

    // -----------------------------------------------------------------------
    // Help modal toggle
    // -----------------------------------------------------------------------
    function toggleHelp() {
        helpModal.style.display = helpModal.style.display === 'none' ? 'flex' : 'none';
    }

    // Close help when clicking the × button
    helpModal.querySelector('.ni-help-close').addEventListener('click', () => {
        helpModal.style.display = 'none';
    });

    // Close help when clicking the backdrop (outside the inner panel)
    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) helpModal.style.display = 'none';
    });

    // -----------------------------------------------------------------------
    // Keyboard shortcuts
    // -----------------------------------------------------------------------
    textarea.addEventListener('keydown', (e) => {
        const ctrl = e.ctrlKey || e.metaKey;
        if (ctrl && e.key === 'b') { e.preventDefault(); wrapSelection('**', '**'); }
        if (ctrl && e.key === 'i') { e.preventDefault(); wrapSelection('*', '*'); }
        if (ctrl && e.key === 'p') { e.preventDefault(); togglePreview(); }
        if (ctrl && e.key === 's') { e.preventDefault(); save(); }
        if (e.key  === 'F11')      { e.preventDefault(); toggleFullscreen(); }
        if (e.key  === 'Escape' && isFullscreen) { toggleFullscreen(); }
    });

    // -----------------------------------------------------------------------
    // Word count + unsaved indicator
    // -----------------------------------------------------------------------
    function triggerChange() {
        const words = clientWordCount(textarea.value);
        if (wordCountEl)  wordCountEl.textContent = words;
        if (saveStatusEl) {
            saveStatusEl.textContent = 'Unsaved changes';
            saveStatusEl.className   = 'text-xs text-amber-500 italic';
        }
        isDirty = true;
    }

    textarea.addEventListener('input', triggerChange);

    // -----------------------------------------------------------------------
    // Save function
    // -----------------------------------------------------------------------
    async function save() {
        if (!saveUrl || !csrfToken) return;

        if (saveStatusEl) {
            saveStatusEl.textContent = 'Saving…';
            saveStatusEl.className   = 'text-xs text-slate-400 italic';
        }
        if (saveBtnEl) {
            saveBtnEl.disabled    = true;
            saveBtnEl.textContent = 'Saving…';
        }

        try {
            const response = await fetch(saveUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken':  csrfToken,
                },
                body: JSON.stringify({ content: textarea.value }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (wordCountEl)  wordCountEl.textContent = data.word_count;
                if (saveStatusEl) {
                    saveStatusEl.textContent = 'Saved';
                    saveStatusEl.className   = 'text-xs text-green-500 italic';
                }
                isDirty = false;
            } else {
                if (saveStatusEl) {
                    saveStatusEl.textContent = 'Save failed';
                    saveStatusEl.className   = 'text-xs text-red-500 italic';
                }
                console.error('Save error:', data.message);
            }
        } catch (err) {
            if (saveStatusEl) {
                saveStatusEl.textContent = 'Save failed';
                saveStatusEl.className   = 'text-xs text-red-500 italic';
            }
            console.error('Network error:', err);
        } finally {
            if (saveBtnEl) {
                saveBtnEl.disabled    = false;
                saveBtnEl.textContent = 'Save Now';
            }
        }
    }

    // -----------------------------------------------------------------------
    // Autosave — every 30 seconds, but only when there are unsaved changes
    // -----------------------------------------------------------------------
    if (saveUrl && csrfToken) {
        setInterval(() => {
            if (isDirty) save();
        }, 30000);
    }

    // -----------------------------------------------------------------------
    // Navigation guard — warn before leaving with unsaved changes
    // -----------------------------------------------------------------------
    window.addEventListener('beforeunload', (e) => {
        if (isDirty) {
            // Modern browsers show their own generic message; setting
            // returnValue is required to trigger the dialog at all.
            e.preventDefault();
            e.returnValue = '';
        }
    });

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------
    function getValue() { return textarea.value; }

    return { getValue, save };
}
