# PhantomByte Prompt Library, implementation notes (Aug 22, 2026)

Built as the second app in this pattern (first was the Article Uploader on Aug 21).

## App: `C:\Users\<user>\Desktop\PhantomBytePromptLibrary\prompt_library.py`

- **5 prompt tools**, each a button. Static prompts (outline, article-image) copy verbatim; templated prompts (article, X, Pinterest) substitute a value then copy.
- **Article prompt** substitutes the OUTLINE FILE *path* into `Outline: {outline}`, NOT file contents. Vinny's wording: "the file location is added to the prompt where it says [ARTICLE OULINE TEXT]".
- **X/Pinterest** read from an `tk.Entry`, substitute into `...telling a story: {post}` / `...for the following: {post}`.
- Build+copy flow: `self.clipboard_clear(); self.clipboard_append(prompt)`.
- Live "LAST BUILT PROMPT" ScrolledText preview shows the last copied prompt.
- Article copy button starts `disabled` and enables only after an outline file is picked.

## Key constants (byte-for-byte from Vinny's draft)

- `OUTLINE_PROMPT` starts `Go to articles.phantom-byte.com ...`
- `ARTICLE_PROMPT_TEMPLATE` is a RAW string (`r"""..."""`) because it embeds `C:\Users\<user>\...` paths. Non-raw triple-quote throws `SyntaxError: (unicode error) 'unicodeescape' ... truncated \UXXXXXXXX escape`.
- `ARTICLE_IMAGE_PROMPT` keeps all his "DO NOT DRAW" lines verbatim.
- `X_PROMPT_TEMPLATE` / `PINTEREST_PROMPT_TEMPLATE` lowercase-as-written.

## Verification results (recorded this session)

- Xvfb unit test: all 5 builders asserted against `clipboard_get()`; window centered at exact midpoint.
- Real Windows Python 3.12.10: screen 1536x864; app 980x824 at (278,20) => center (768,432) exact; `apply_icon()` no exception.
- Shortcut setup via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File` => `pyw.exe OK`, `SHORTCUTS CREATED`. `.lnk` files on real desktop + Start Menu.
- Robot icon: PIL-drawn rounded robot head + antenna + eyes + mouth on `#101018` panel, saved as 6-size ICO, `file` reads "MS Windows icon resource - 6 icons".

## Quoting trap (avoid next time)

`cmd.exe /c "py -c \"import tkinter; ...\""` and the PowerShell equivalent mangle quotes into `SyntaxError: unterminated string literal` on `"import`. Always write a `_smoke.py` file, run it via `py.exe` (console), then delete it. `pyw.exe` is windowless so its stdout never reaches WSL.
