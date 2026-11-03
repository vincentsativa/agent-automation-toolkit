---
name: windows-desktop-app-builder
description: Use when Vinny asks for a local desktop app or prompt tool.
---

# Windows Desktop App Builder (tkinter)

Pattern for building self-contained local Windows GUI apps for Vinny that launch via a desktop shortcut. Used for the **PhantomByte Article Uploader** and the **PhantomByte Prompt Library**. Every new request of this kind should mirror this structure.

## Packaging structure (copy this exactly)

One folder on the real desktop (NOT OneDrive Desktop, Vinny's uploader lives at `C:\Users\<user>\Desktop\PhantomByteUploader\`, prompt library at `...\PhantomBytePromptLibrary\`):

- `<app>.py`, the tkinter app (see below)
- `launch.bat`, runs via the Python launcher with `pyw.exe` (windowless)
- `setup_shortcuts.ps1`, PowerShell: creates desktop + Start Menu `.lnk`, points at `launch.bat`, sets `.ico`
- `<name>.ico`, multi-size Windows icon resource
- (optional) `icon.png`, source PNG for regeneration

`launch.bat` content (exact):
```bat
@echo off
start "" "C:\Users\<user>\AppData\Local\Programs\Python\Launcher\pyw.exe" "C:\Users\<user>\Desktop\PHOLDER\<app>.py"
```

`setup_shortcuts.ps1` pattern (mirror the uploader's; use `[Environment]::GetFolderPath("Desktop")` for the real desktop and `$env:APPDATA\...\Start Menu\Programs` for Start-pin):
```powershell
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$desktop\AppName.lnk")
$lnk.TargetPath = "$dir\launch.bat"
$lnk.WorkingDirectory = $dir
$lnk.IconLocation = "$dir\<name>.ico,0"
$lnk.Description = "..."
$lnk.Save()
```
Verify `pyw.exe` exists (fallback `py.exe`). Run the ps1 FROM WSL via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\\..."`. It creates real `.lnk` files (do not hand-write them).

## Brand dashboard theme (identical palette across apps)

```python
BG="#050507" PANEL="#101018" LINE="#1c1c26" GREEN="#00FF88"
PURPLE="#9D4EDD" TEXT="#e6e6f0" DIM="#8a8a9a"
```
Header: emoji glyph + "PHANTOM"(white)/"BYTE"(purple) + lowercase subtitle in GREEN. Buttons flat (`relief="flat"`, `cursor="hand2"`), Consolas font, GREEN buttons with dark text for "copy", PURPLE for "upload/pick". LabelFrame sections with purple title. ScrolledText preview pane (PANEL bg, selectbackground=PURPLE).

## Icon (robot, or per-app glyph) via PIL → .ico

Generate the PNG with `ImageDraw` (rounded rects + ellipses), then save multi-size ICO:
```python
img.save("name.ico", format="ICO", sizes=[(s,s) for s in [16,32,48,64,128,256]])
```
Verify with `file` / `identify` (must read "MS Windows icon resource - N icons"). The current deepseek model has NO vision, do not call vision_analyze on the icon, just trust the deterministic drawing code and verify via file type + that tkinter loads it (`iconbitmap`).

## Centering (mandatory: Vinny wants the dashboard centered and fully on screen)

```python
def center_on_screen(self):
    self.update_idletasks()
    w,h = 980,860; sw=self.winfo_screenwidth(); sh=self.winfo_screenheight()
    h=min(h,sh-40); w=min(w,sw-40)
    x=max((sw-w)//2,0); y=max((sh-h)//2,0)
    self.geometry(f"{w}x{h}+{x}+{y}")
```

## Copy-to-clipboard prompt tools

Store prompts as module constants (triple-quoted). For prompts with a placeholder (like `Outline: [ARTICLE OULINE TEXT]`), use a `TEMPLATE.format(...)` and a build function. Two clipboard calls per copy:
```python
self.clipboard_clear()
self.clipboard_append(prompt)
```

## CRITICAL PITFALLS (learned the hard way)

1. **File LOCATION, not file CONTENT.** Vinny's article prompt says "the file location is added to the prompt where it says [ARTICLE OULINE TEXT]". The prior draft (in the session log) wrongly embedded the file *contents* into the prompt. The uploader reads paths; the prompt library substitutes the **path string** (`self.outline_path`) into the template, NOT `f.read()`. Read the file only if the prompt genuinely wants its text inline; for "add the file location" you substitute the path.

2. **`\U` unicode-escape SyntaxError.** A Python triple-quoted template containing a Windows path like `C:\Users\...` raises `SyntaxError: (unicode error) 'unicodeescape' ... truncated \UXXXXXXXX escape` at write/lint time. Fix: make the template a raw string, `ARTICLE_PROMPT_TEMPLATE = r"""..."""`. Verify no `\U00` appears in the rendered output.

3. **Prompts must be byte-for-byte as Vinny wrote them.** He said "make sure to follow the instructions AS written, the prompts must look exactly as they are above". Copy the wording exactly (including his typos like "actction pact", "DON NOT", "I want to been seen"). Do NOT correct or polish them.

4. **No em dashes / dashes-as-commas in ANY output**, this is Vinny's standing writing rule (see `writing-style` skill). It applies to prompts he reuses and to the app's own text.

5. **Testing is mandatory**, "You must make sure this functions properly before telling me it's done." Two-tier test:
   - **WSL/Xvfb:** `xvfb-run -a python3`, import the module, instantiate the App, invoke each button handler, assert `clipboard_get()` equals expected. Also assert window center = `(sw//2, sh//2)`.
   - **Real Windows Python:** write a tiny smoke script, run via `powershell.exe -NoProfile -Command "& 'C:\...\py.exe' 'C:\...\_smoke.py'"`, assert it prints screen size, centered coords, no exception on `apply_icon()`. Windows Python 3.12 has tkinter; `pyw.exe` is windowless so stdout goes to the GUI session, use `py.exe` (console) for smoke-test stdout.

6. **Quoting hell running inline python on Windows.** `cmd.exe /c "py -c \"import tkinter\""` mangles quotes into `"import` errors. Always write a `_smoke.py` file and run it, never an inline `-c` through cmd/powershell from WSL.

7. **Desktop path.** The OneDrive Desktop (`C:\Users\<user>\OneDrive\Desktop\`) holds Vinny's loose files/shortcuts, but the app FOLDER goes on the real Desktop (`C:\Users\<user>\Desktop\`). The uploader does exactly this. The desktop `.lnk` can point wherever you choose; just be consistent with the prior app.

8. **The icon file must exist before `iconbitmap`**, guard with `os.path.isfile()` + try/except so the app still runs without it.

## Verification checklist (before reporting done)

- [ ] `python3 -c "import <app>"` imports clean (no SyntaxError)
- [ ] Xvfb run: all 5 button handlers copy expected strings; preview pane holds last output; article button disabled until a file is picked
- [ ] Window center matches screen midpoint under Xvfb AND real Windows
- [ ] `setup_shortcuts.ps1` printed `pyw.exe OK` + `SHORTCUTS CREATED`; `.lnk` files on disk (desktop + Start Menu)
- [ ] `.ico` verified as "MS Windows icon resource"
- [ ] Real-Windows smoke run: screen dims, centered, icon applies

See `references/` for the Prompt Library implementation and test transcript.
