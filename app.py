"""Main application window and logic."""

import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Optional

from crypto import load_or_create_salt, derive_key
from storage import load_accounts, save_accounts
from ui.login_window import LoginWindow
from ui.account_panel import AccountPanel
from cryptography.fernet import InvalidToken

BG = "#1e1e2e"
BG_SIDE = "#181825"
FG = "#cdd6f4"
SELECTED_BG = "#313244"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
MUTED = "#6c7086"
ACCENT = "#cba6f7"


class App:
    """Top-level application controller."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("R6 Smurf Account Manager")
        self._root.configure(bg=BG)
        self._root.geometry("960x620")
        self._root.minsize(700, 480)

        self._key: Optional[bytes] = None
        self._accounts: List[Dict[str, Any]] = []
        self._selected_index: Optional[int] = None

        self._authenticate()
        self._build_ui()
        self._refresh_list()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self):
        salt = load_or_create_salt()
        is_first_run = not os.path.exists("accounts.dat")
        password = LoginWindow.run(self._root, is_first_run)
        key = derive_key(password, salt)

        if is_first_run:
            # Create empty encrypted file so next launch detects it
            save_accounts([], key)
            self._accounts = []
        else:
            try:
                self._accounts = load_accounts(key)
            except (InvalidToken, Exception):
                messagebox.showerror(
                    "Wrong Password",
                    "The password you entered is incorrect.\nThe application will now close.",
                    parent=self._root,
                )
                raise SystemExit(1)

        self._key = key

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ---- sidebar ----
        sidebar = tk.Frame(self._root, bg=BG_SIDE, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        sidebar_header = tk.Frame(sidebar, bg=BG_SIDE)
        sidebar_header.pack(fill="x", padx=12, pady=(14, 6))

        tk.Label(sidebar_header, text="Accounts", bg=BG_SIDE, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(side="left")

        tk.Button(sidebar_header, text="＋", bg=BTN_BG, fg=BTN_FG,
                  font=("Segoe UI", 11, "bold"), bd=0, relief="flat",
                  cursor="hand2", padx=8, pady=2,
                  command=self._add_account).pack(side="right")

        # list frame with scrollbar
        list_frame = tk.Frame(sidebar, bg=BG_SIDE)
        list_frame.pack(fill="both", expand=True)

        self._listbox = tk.Listbox(
            list_frame,
            bg=BG_SIDE, fg=FG,
            selectbackground=SELECTED_BG, selectforeground=FG,
            font=("Segoe UI", 10),
            bd=0, highlightthickness=0,
            activestyle="none",
            relief="flat",
        )
        sb = tk.Scrollbar(list_frame, orient="vertical",
                          command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # ---- right panel ----
        self._panel = AccountPanel(
            self._root,
            on_save=self._save_account,
            on_delete=self._delete_account,
        )
        self._panel.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------------
    # Listbox helpers
    # ------------------------------------------------------------------

    def _refresh_list(self, select_index: Optional[int] = None):
        self._listbox.delete(0, "end")
        for acc in self._accounts:
            self._listbox.insert("end", "  " + acc.get("account_name", "Account"))
        if select_index is not None:
            self._listbox.selection_set(select_index)
            self._listbox.see(select_index)
            self._selected_index = select_index
            self._panel.show_account(self._accounts[select_index])
        else:
            self._selected_index = None
            self._panel.show_empty()

    def _on_select(self, _event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._selected_index = idx
        self._panel.show_account(self._accounts[idx])

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def _next_default_name(self) -> str:
        n = len(self._accounts) + 1
        existing = {a.get("account_name", "") for a in self._accounts}
        while f"Account {n}" in existing:
            n += 1
        return f"Account {n}"

    def _add_account(self):
        self._listbox.selection_clear(0, "end")
        self._selected_index = None
        self._panel.show_new_account(self._next_default_name())

    def _save_account(self, original: Optional[Dict], data: Dict[str, Any]):
        # If name left blank, assign default
        if not data.get("account_name"):
            data["account_name"] = self._next_default_name()

        if original is None:
            # New account
            self._accounts.append(data)
            new_index = len(self._accounts) - 1
        else:
            # Existing account
            idx = self._accounts.index(original)
            self._accounts[idx] = data
            new_index = idx

        save_accounts(self._accounts, self._key)
        self._refresh_list(new_index)

    def _delete_account(self, account: Dict[str, Any]):
        if account in self._accounts:
            self._accounts.remove(account)
            save_accounts(self._accounts, self._key)
        self._refresh_list()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        self._root.mainloop()
