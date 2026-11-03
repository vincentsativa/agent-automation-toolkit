"""Reusable two-tier verification for a PhantomByte-style tkinter app.

Run tier 1 (WSL/Xvfb) from the app folder:
    xvfb-run -a python3 verify_gui.py
Run tier 2 (real Windows) by copying this file next to the app and running via py.exe:
    powershell.exe -NoProfile -Command "& 'C:\...\py.exe' 'C:\...\verify_gui.py'"

Adapt the handler-name list to the app under test.
"""
import sys
import prompt_library as pl  # <-- change to the app module

app = pl.App()
app.update_idletasks()

# --- centering check ---
sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
w, h = app.winfo_width(), app.winfo_height()
x, y = app.winfo_x(), app.winfo_y()
cx, cy = x + w // 2, y + h // 2
print(f"SCREEN {sw}x{sh} WIN {w}x{h} center=({cx},{cy}) expected=({sw//2},{sh//2})")
assert cx == sw // 2 and cy == sh // 2, "window not centered"
print("CENTER OK")

# --- icon applies (no exception) ---
pl.App.apply_icon(app)
print("ICON OK")

# --- clipboard round-trip for each copy handler ---
for name in ["copy_outline", "copy_article_image", "copy_x", "copy_pinterest"]:
    getattr(app, name)()
    got = app.clipboard_get()
    assert got.strip(), f"{name} produced empty clipboard"
    print(f"HANDLER OK {name} ({len(got)} chars)")

# --- article guard: disabled until file picked, then works ---
assert str(app.article_copy_btn["state"]) == "disabled", "article btn should start disabled"
app.outline_path = "/tmp/test-outline.txt"
app.copy_article()
got = app.clipboard_get()
assert "/tmp/test-outline.txt" in got, "outline path not injected"
print("HANDLER OK copy_article (path injected)")

# --- preview pane mirrors last copy ---
assert app.output.get("1.0", "end-1c") == got
print("PREVIEW OK")

app.destroy()
print("ALL CHECKS PASSED")
