<align align="center">
  <img src="https://img.icons8.com/wired/128/3498db/computer.png" width="100" />
  <h1 align="center">PC Diagnostics Tool</h1>
  <p align="center">
    <strong>A high-performance, modern desktop application for automated system diagnostics and reporting.</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/CustomTkinter-Modern_UI-eb6b34?style=for-the-badge" />
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
    <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" />
  </p>
</align>

---

## 🚀 Overview
**PC Diagnostics Tool** is a premium desktop application that provides a one-click solution for collecting deep system hardware and software diagnostics. It generates a professional HTML dashboard and can automatically dispatch it via secure SMTP email.

### ✨ Key Features
- 🖥️ **Modern UI**: Built with **CustomTkinter** for a native dark-mode experience.
- 🔍 **Deep Scanning**: Collects CPU, RAM, Disk, Network, Battery, and Process data.
- 📄 **Professional Reports**: Generates a sleek, responsive HTML dashboard.
- 📧 **Auto-Email**: Securely sends reports via Gmail SMTP using App Passwords.
- 🔐 **Security First**: Environment-based credential management via `.env`.

---

## 📸 Interface Preview
*(The app features a sleek Zinc-900 Dark Theme with Blue-500 accents)*

---

## 🛠️ Quick Start

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/pc-spec-fetcher.git
cd pc-spec-fetcher

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the template and add your credentials:
```bash
cp .env.example .env
```
Open `.env` and fill in your Gmail SMTP details securely.

### 4. Launch
```bash
python main.py
# OR double-click run.bat
```

---

## 📂 Project Architecture
```text
pc-spec-fetcher/
├── main.py             # Main Entry Point (CustomTkinter UI)
├── diagnostics.py      # Hardware Data Collection Engine
├── report.py           # HTML Dashboard Generator
├── mailer.py           # SMTP Email Service
├── .env                # Private Credentials (ignored by Git)
└── requirements.txt    # Project Dependencies
```

---

## 📦 Distribution
To build a standalone Windows executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "PC_Diagnostics" --add-data "config.ini;." main.py
```
Find your build in the `dist/` directory.

---

## 🔐 Security
This project uses `python-dotenv` for managing sensitive keys. **Never** commit your `.env` file to version control. Use Gmail **App Passwords** to keep your primary account password safe.

---

