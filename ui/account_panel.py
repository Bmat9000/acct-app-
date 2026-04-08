"""Account detail / edit panel displayed on the right side of the main window."""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any, Optional

BG = "#1e1e2e"
BG2 = "#181825"
FG = "#cdd6f4"
ENTRY_BG = "#313244"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_DEL = "#f38ba8"
MUTED = "#6c7086"
ACCENT = "#cba6f7"

FIELDS = [
    ("account_name",      "Account Name",        False),
    ("description",       "Description",         True),   # multi-line
    ("email",             "Email Address",        False),
    ("email_password",    "Email Password",       False),
    ("ubisoft_username",  "Ubisoft Username",     False),
    ("ubisoft_email",     "Ubisoft Login Email",  False),
    ("ubisoft_password",  "Ubisoft Password",     False),
]

PASSWORD_FIELDS = {"email_password", "ubisoft_password"}


class AccountPanel(tk.Frame):
    """Right-hand panel showing account details and an edit form."""

    def __init__(self, parent, on_save: Callable, on_delete: Callable):
        super().__init__(parent, bg=BG2)
        self._on_save = on_save
        self._on_delete = on_delete
        self._current: Optional[Dict[str, Any]] = None
        self._editing = False

        self._entries: Dict[str, tk.Widget] = {}
        self._vars: Dict[str, tk.StringVar] = {}
        self._eye_btns: Dict[str, tk.Button] = {}

        self._build_ui()
        self.show_empty()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # title bar
        title_bar = tk.Frame(self, bg=BG2)
        title_bar.pack(fill="x", padx=20, pady=(18, 0))

        self._title_lbl = tk.Label(title_bar, text="Select an account",
                                   bg=BG2, fg=FG,
                                   font=("Segoe UI", 14, "bold"))
        self._title_lbl.pack(side="left")

        self._btn_delete = tk.Button(title_bar, text="🗑 Delete",
                                     bg=BTN_DEL, fg=BG,
                                     font=("Segoe UI", 9, "bold"),
                                     bd=0, relief="flat", cursor="hand2",
                                     padx=10, pady=4,
                                     command=self._handle_delete)
        self._btn_edit = tk.Button(title_bar, text="✏️ Edit",
                                   bg=BTN_BG, fg=BTN_FG,
                                   font=("Segoe UI", 9, "bold"),
                                   bd=0, relief="flat", cursor="hand2",
                                   padx=10, pady=4,
                                   command=self._start_edit)
        self._btn_save = tk.Button(title_bar, text="💾 Save",
                                   bg="#a6e3a1", fg=BG,
                                   font=("Segoe UI", 9, "bold"),
                                   bd=0, relief="flat", cursor="hand2",
                                   padx=10, pady=4,
                                   command=self._handle_save)
        self._btn_cancel = tk.Button(title_bar, text="✖ Cancel",
                                     bg=ENTRY_BG, fg=FG,
                                     font=("Segoe UI", 9, "bold"),
                                     bd=0, relief="flat", cursor="hand2",
                                     padx=10, pady=4,
                                     command=self._cancel_edit)

        # scrollable content area
        canvas = tk.Canvas(self, bg=BG2, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._form = tk.Frame(canvas, bg=BG2)
        self._form_window = canvas.create_window((0, 0), window=self._form, anchor="nw")

        self._form.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._form_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._canvas = canvas

        # Build field rows
        for key, label, multiline in FIELDS:
            row = tk.Frame(self._form, bg=BG2)
            row.pack(fill="x", padx=20, pady=(10, 0))

            lbl = tk.Label(row, text=label, bg=BG2, fg=ACCENT,
                           font=("Segoe UI", 9, "bold"))
            lbl.pack(anchor="w")

            inner = tk.Frame(self._form, bg=BG2)
            inner.pack(fill="x", padx=20, pady=(2, 0))

            if multiline:
                widget = tk.Text(inner, bg=ENTRY_BG, fg=FG,
                                 insertbackground=FG,
                                 font=("Segoe UI", 10), bd=0,
                                 highlightthickness=1,
                                 highlightbackground="#45475a",
                                 highlightcolor=BTN_BG,
                                 height=4, wrap="word",
                                 state="disabled")
                widget.pack(side="left", fill="x", expand=True, ipady=4)

                # copy button only for description
                copy_btn = tk.Button(inner, text="📋", bg=ENTRY_BG, fg=FG,
                                     bd=0, relief="flat", cursor="hand2",
                                     command=lambda k=key: self._copy(k))
                copy_btn.pack(side="left", padx=(4, 0))
            else:
                is_pw = key in PASSWORD_FIELDS
                var = tk.StringVar()
                self._vars[key] = var
                widget = tk.Entry(inner, textvariable=var,
                                  show="•" if is_pw else "",
                                  bg=ENTRY_BG, fg=FG,
                                  insertbackground=FG,
                                  font=("Segoe UI", 10), bd=0,
                                  highlightthickness=1,
                                  highlightbackground="#45475a",
                                  highlightcolor=BTN_BG,
                                  state="disabled",
                                  disabledbackground=ENTRY_BG,
                                  disabledforeground=MUTED)
                widget.pack(side="left", fill="x", expand=True, ipady=6)

                copy_btn = tk.Button(inner, text="📋", bg=ENTRY_BG, fg=FG,
                                     bd=0, relief="flat", cursor="hand2",
                                     command=lambda k=key: self._copy(k))
                copy_btn.pack(side="left", padx=(4, 0))

                if is_pw:
                    eye_btn = tk.Button(inner, text="👁", bg=ENTRY_BG, fg=FG,
                                        bd=0, relief="flat", cursor="hand2",
                                        command=lambda w=widget: self._toggle_pw(w))
                    eye_btn.pack(side="left", padx=(2, 0))
                    self._eye_btns[key] = eye_btn

            self._entries[key] = widget

        tk.Frame(self._form, bg=BG2, height=20).pack()  # bottom padding

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def show_empty(self):
        """Reset panel to empty / no-selection state."""
        self._current = None
        self._editing = False
        self._title_lbl.configure(text="Select an account")
        self._btn_edit.pack_forget()
        self._btn_delete.pack_forget()
        self._btn_save.pack_forget()
        self._btn_cancel.pack_forget()
        self._clear_fields()
        self._set_fields_editable(False)

    def show_account(self, account: Dict[str, Any]):
        """Display *account* in read-only mode."""
        self._current = account
        self._editing = False
        self._title_lbl.configure(text=account.get("account_name", "Account"))
        self._btn_save.pack_forget()
        self._btn_cancel.pack_forget()
        self._btn_edit.pack(side="right", padx=(6, 0))
        self._btn_delete.pack(side="right")
        self._populate_fields(account)
        self._set_fields_editable(False)

    def show_new_account(self, default_name: str):
        """Open the panel in edit mode for a brand-new account."""
        self._current = None
        self._editing = True
        self._title_lbl.configure(text="New Account")
        self._btn_edit.pack_forget()
        self._btn_delete.pack_forget()
        self._btn_save.pack(side="right", padx=(6, 0))
        self._btn_cancel.pack(side="right")
        self._clear_fields()
        self._set_fields_editable(True)
        # Pre-fill the default name
        self._set_field_value("account_name", default_name)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _start_edit(self):
        self._editing = True
        self._btn_edit.pack_forget()
        self._btn_delete.pack_forget()
        self._btn_save.pack(side="right", padx=(6, 0))
        self._btn_cancel.pack(side="right")
        self._set_fields_editable(True)

    def _cancel_edit(self):
        if self._current is not None:
            self.show_account(self._current)
        else:
            self.show_empty()

    def _handle_save(self):
        data = self._collect_fields()
        # Validate: at least name or some data
        if not any(data.values()):
            messagebox.showwarning("Empty Account",
                                   "Please fill in at least one field.",
                                   parent=self)
            return
        self._on_save(self._current, data)

    def _handle_delete(self):
        if self._current is None:
            return
        name = self._current.get("account_name", "this account")
        if messagebox.askyesno("Delete Account",
                                f"Delete '{name}'? This cannot be undone.",
                                parent=self):
            self._on_delete(self._current)

    def _populate_fields(self, account: Dict[str, Any]):
        for key, _, multiline in FIELDS:
            value = account.get(key, "")
            self._set_field_value(key, value)

    def _clear_fields(self):
        for key, _, multiline in FIELDS:
            self._set_field_value(key, "")

    def _set_field_value(self, key: str, value: str):
        widget = self._entries[key]
        if isinstance(widget, tk.Text):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
            widget.configure(state="disabled")
        else:
            self._vars[key].set(value)

    def _get_field_value(self, key: str) -> str:
        widget = self._entries[key]
        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end-1c").strip()
        return self._vars[key].get().strip()

    def _collect_fields(self) -> Dict[str, Any]:
        return {key: self._get_field_value(key) for key, _, _m in FIELDS}

    def _set_fields_editable(self, editable: bool):
        state_entry = "normal" if editable else "disabled"
        for key, _, multiline in FIELDS:
            widget = self._entries[key]
            if isinstance(widget, tk.Text):
                widget.configure(state=state_entry)
            else:
                widget.configure(state=state_entry)

    def _copy(self, key: str):
        value = self._get_field_value(key)
        self.clipboard_clear()
        self.clipboard_append(value)

    def _toggle_pw(self, entry: tk.Entry):
        entry.configure(show="" if entry.cget("show") == "•" else "•")
