# R6 Smurf Account Manager

A **secure, local desktop application** for managing Rainbow Six Siege smurf accounts.  
All data is stored **fully encrypted on your PC** — nothing leaves your machine.

---

## ✨ Features

- 🔐 **Master password** protects all your data with strong encryption (Fernet + PBKDF2HMAC)
- 💾 Stores email credentials, Ubisoft login info, and custom notes per account
- 👁️ Show/hide toggle on every password field
- 📋 Copy-to-clipboard button on every field
- ✏️ Rename accounts at any time; auto-names as "Account 1", "Account 2", … if left blank
- 🗑️ Delete accounts with a confirmation prompt
- 🌑 Full dark theme

---

## 📦 Installation

### 1. Install Python

Download and install Python 3.10+ from <https://www.python.org/downloads/>.  
Make sure to tick **"Add Python to PATH"** during installation on Windows.

### 2. Install dependencies

Open a terminal / Command Prompt in the project folder and run:

```
pip install -r requirements.txt
```

---

## ▶️ Running the app

```
python main.py
```

The first time you run it, you will be asked to **create a master password**.  
On every subsequent launch you will need to enter that password to unlock the app.

---

## ⚠️ Important security note

The master password is **never stored anywhere**.  
If you forget your master password, your account data **cannot be recovered**.  
Make sure to keep your master password somewhere safe.

---

## 📁 File structure

```
acct-app/
├── main.py              # Entry point
├── app.py               # Main app window and logic
├── crypto.py            # Encryption/decryption helpers
├── storage.py           # Load/save accounts to encrypted file
├── ui/
│   ├── login_window.py  # Master password setup and login screen
│   └── account_panel.py # Account detail view/edit UI
├── accounts.dat         # Encrypted account data (created at runtime)
├── salt.bin             # Encryption salt (created at runtime)
├── requirements.txt     # cryptography
└── README.md            # This file
```