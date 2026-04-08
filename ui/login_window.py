"""Login / setup window for the master password."""

import tkinter as tk
from tkinter import messagebox


BG = "#1e1e2e"
FG = "#cdd6f4"
ENTRY_BG = "#313244"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
ERR_FG = "#f38ba8"


def _apply_dark(widget):
    """Recursively apply dark-theme colours to a widget tree."""
    try:
        widget.configure(bg=BG)
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        _apply_dark(child)


class LoginWindow(tk.Toplevel):
    """Blocking dialog that resolves to a (password, is_new_setup) tuple.

    Call ``LoginWindow.run(root)`` — it blocks until the user authenticates
    and returns the entered password, or raises ``SystemExit`` if the window
    is closed without authenticating.
    """

    def __init__(self, parent: tk.Tk, is_first_run: bool):
        super().__init__(parent)
        self.title("R6 Account Manager — " + ("Create Master Password" if is_first_run else "Unlock"))
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()            # modal
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._is_first_run = is_first_run
        self._result: str | None = None

        self._build_ui()
        self.update_idletasks()
        self._center()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 20, "pady": 8}

        header = "🔐 Create a master password" if self._is_first_run else "🔐 Enter master password to unlock"
        tk.Label(self, text=header, bg=BG, fg=FG,
                 font=("Segoe UI", 13, "bold")).pack(**pad)

        tk.Label(self, text="Master Password:", bg=BG, fg=FG,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20)
        self._pw_var = tk.StringVar()
        pw_frame = tk.Frame(self, bg=BG)
        pw_frame.pack(fill="x", padx=20, pady=(0, 8))
        self._pw_entry = tk.Entry(pw_frame, textvariable=self._pw_var,
                                  show="•", bg=ENTRY_BG, fg=FG,
                                  insertbackground=FG,
                                  font=("Segoe UI", 11), bd=0,
                                  highlightthickness=1,
                                  highlightbackground="#45475a",
                                  highlightcolor=BTN_BG)
        self._pw_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(pw_frame, text="👁", bg=ENTRY_BG, fg=FG, bd=0,
                  relief="flat", cursor="hand2",
                  command=lambda: self._toggle(self._pw_entry)
                  ).pack(side="left", padx=(4, 0))

        if self._is_first_run:
            tk.Label(self, text="Confirm Password:", bg=BG, fg=FG,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=20)
            self._conf_var = tk.StringVar()
            conf_frame = tk.Frame(self, bg=BG)
            conf_frame.pack(fill="x", padx=20, pady=(0, 8))
            self._conf_entry = tk.Entry(conf_frame, textvariable=self._conf_var,
                                        show="•", bg=ENTRY_BG, fg=FG,
                                        insertbackground=FG,
                                        font=("Segoe UI", 11), bd=0,
                                        highlightthickness=1,
                                        highlightbackground="#45475a",
                                        highlightcolor=BTN_BG)
            self._conf_entry.pack(side="left", fill="x", expand=True, ipady=6)
            tk.Button(conf_frame, text="👁", bg=ENTRY_BG, fg=FG, bd=0,
                      relief="flat", cursor="hand2",
                      command=lambda: self._toggle(self._conf_entry)
                      ).pack(side="left", padx=(4, 0))
            self._conf_entry.bind("<Return>", lambda _e: self._submit())
        else:
            self._conf_var = None
            self._conf_entry = None

        self._err_lbl = tk.Label(self, text="", bg=BG, fg=ERR_FG,
                                 font=("Segoe UI", 9))
        self._err_lbl.pack()

        btn_text = "Create Password" if self._is_first_run else "Unlock"
        tk.Button(self, text=btn_text, bg=BTN_BG, fg=BTN_FG,
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  padx=16, pady=6, relief="flat",
                  command=self._submit).pack(pady=(0, 16))

        self._pw_entry.bind("<Return>", lambda _e: self._submit())
        self._pw_entry.focus_set()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _toggle(self, entry: tk.Entry):
        entry.configure(show="" if entry.cget("show") == "•" else "•")

    def _submit(self):
        pw = self._pw_var.get()
        if not pw:
            self._err_lbl.configure(text="Password cannot be empty.")
            return
        if self._is_first_run:
            conf = self._conf_var.get()
            if pw != conf:
                self._err_lbl.configure(text="Passwords do not match.")
                return
            if len(pw) < 8:
                self._err_lbl.configure(text="Password must be at least 8 characters.")
                return
        self._result = pw
        self.grab_release()
        self.destroy()

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _center(self):
        w, h = self.winfo_width(), self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    @classmethod
    def run(cls, parent: tk.Tk, is_first_run: bool) -> str:
        """Show the dialog and return the entered password.

        Raises ``SystemExit`` when the user closes the window."""
        dlg = cls(parent, is_first_run)
        parent.wait_window(dlg)
        if dlg._result is None:
            raise SystemExit(0)
        return dlg._result
