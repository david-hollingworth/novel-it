/**
 * editor.js — shared EasyMDE initialisation for NovelIt
 *
 * Usage:
 *   const editor = initEditor({
 *       elementId:    'my-textarea',      // required
 *       wordCountId:  'word-count',       // optional — element to update with live word count
 *       saveStatusId: 'save-status',      // optional — element to show Saved / Unsaved / Saving
 *       saveBtnId:    'save-btn',         // optional — button to disable during save
 *       saveUrl:      '/path/to/save/',   // optional — if provided, enables Ctrl+S and saveContent()
 *       csrfToken:    'abc123',           // required if saveUrl is set
 *       placeholder:  'Start writing…',  // optional
 *   });
 *
 *   // editor.instance  → the EasyMDE instance
 *   // editor.save()    → programmatically trigger a save
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

    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`initEditor: element #${elementId} not found`);
        return null;
    }

    // -----------------------------------------------------------------------
    // Toolbar — standard prose writing set
    // -----------------------------------------------------------------------
    const toolbar = [
        'bold', 'italic', 'strikethrough', '|',
        'heading-1', 'heading-2', 'heading-3', '|',
        'quote', 'unordered-list', 'ordered-list', '|',
        'horizontal-rule', '|',
        'preview', 'side-by-side', 'fullscreen', '|',
        'guide',
    ];

    // -----------------------------------------------------------------------
    // Instantiate EasyMDE
    // -----------------------------------------------------------------------
    const instance = new EasyMDE({
        element:     el,
        autofocus:   true,
        spellChecker: false,
        autosave:    { enabled: false },
        placeholder,
        status:      ['words'],
        toolbar,
        shortcuts: {
            toggleSideBySide: null,
            toggleFullScreen: null,
        },
    });

    // -----------------------------------------------------------------------
    // Helper refs
    // -----------------------------------------------------------------------
    const wordCountEl  = wordCountId  ? document.getElementById(wordCountId)  : null;
    const saveStatusEl = saveStatusId ? document.getElementById(saveStatusId) : null;
    const saveBtnEl    = saveBtnId    ? document.getElementById(saveBtnId)    : null;

    // -----------------------------------------------------------------------
    // Live word count + unsaved indicator
    // -----------------------------------------------------------------------
    instance.codemirror.on('change', function () {
        const text  = instance.value();
        const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
        if (wordCountEl)  wordCountEl.textContent = words;
        if (saveStatusEl) {
            saveStatusEl.textContent = 'Unsaved changes';
            saveStatusEl.className   = 'text-xs text-amber-500 italic';
        }
    });

    // -----------------------------------------------------------------------
    // Save function (only wired up if saveUrl is provided)
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
                body: JSON.stringify({ content: instance.value() }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (wordCountEl)  wordCountEl.textContent = data.word_count;
                if (saveStatusEl) {
                    saveStatusEl.textContent = 'Saved';
                    saveStatusEl.className   = 'text-xs text-green-500 italic';
                }
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

    // Ctrl+S / Cmd+S
    if (saveUrl) {
        instance.codemirror.addKeyMap({
            'Ctrl-S': function () { save(); },
            'Cmd-S':  function () { save(); },
        });
    }

    return { instance, save };
}
