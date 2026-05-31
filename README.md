# FAFO: Secure Multimedia Evidence Logging and Incident Preservation Platform

FAFO (Facts, Accountability, Forensics, and Observation) is a private, enterprise-grade digital forensics and cybersecurity incident response evidence management platform. It is designed to securely preserve digital evidence (such as online harassment, cyberbullying, doxxing, and threats), maintain evidence integrity using cryptographic hashing, track chain-of-custody, and facilitate secure review and legal-ready exports.

This system is built using **Streamlit** (Frontend) and **Python/SQLite** (Backend) in a modular, secure, and highly visual cyber-forensics dark theme.

---

## 📁 Directory Structure Overview

```text
c:\Users\HP\Downloads\FAFO/
├── app.py                     # Streamlit web interface entrypoint
├── requirements.txt           # Python application package dependencies
├── README.md                  # This documentation guide
├── config/
│   ├── __init__.py            # Config module package marker
│   ├── settings.py            # Global variables, MIME limits, and folder configurations
│   └── roles.py               # RBAC Roles, default passwords, and Permissions definitions
├── database/
│   ├── __init__.py            # Database module package marker
│   ├── init_db.py             # Checks, initializes DB, and seeds credentials
│   └── schema.sql             # SQL statements to create all FAFO SQLite tables
├── modules/
│   ├── __init__.py            # Package marker
│   ├── auth.py                # Login panels, bcrypt matches, and session timeouts
│   ├── utils.py               # Custom cybersecurity glassmorphism dark CSS injection
│   ├── incident_manager.py    # Persistent SQLite CRUD and audit DB hooks
│   ├── repository.py          # Physical folder structures partitioning (Screenshots, etc.)
│   ├── security.py            # Passwords, files, URLs, and path traversal sanitizers
│   ├── hashing.py             # SHA-256 calculators and hashes.json manifests checks
│   ├── audit_logger.py        # Double-entry persistent logging (DB + audit_trail.log)
│   ├── ocr_engine.py          # Pillow and Tesseract OCR with ASCII regex fallback
│   ├── ai_classifier.py       # Offline classification scoring and triage
│   ├── ffmpeg_processor.py    # Video spec decoders with native MP4 atom parser fallback
│   ├── dashboard.py           # Dashboard graphs, KPIs, and status telemetry views
│   ├── lawyer_portal.py       # Lawyer read-only audit dashboard with integrity checks
│   └── notifications.py       # Automated SMTP alert notices and offline notifications log
├── logs/
│   ├── audit_trail.log        # Immutable chronological audit trail text logs
│   └── notifications.log      # Outbox summary of mock emails sent
├── evidence_repository/        # Secured preservation vault (Incident subfolders)
└── scratch/                   # Temporary testing scripts directory
```

---

## 🚀 Quick Start Guide

### 1. Prerequisite Installations
Ensure Python 3.10+ is installed on your Windows machine. Install dependencies with pip:
```bash
pip install -r requirements.txt
```

*(Note: If Tesseract OCR or FFmpeg are missing, the FAFO platform automatically triggers advanced Python-native binary fallbacks: a binary-level ASCII regex screenshot scanner and a custom MP4 box structure atom parser. No extra software installation is required to test or run the platform!)*

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` in the root folder to customize SMTP details, upload size limits, session timeout thresholds, or specific storage paths.

### 3. Launch Platform
Simply execute the following Streamlit command inside the workspace directory:
```bash
streamlit run app.py
```
This will automatically initialize the database (`fafo_database.db` will be created and seeded), create folder directories, and open the web dashboard in your browser.

---

## 🔑 Secure Sandbox Credentials (Demo Accounts)

To demonstrate role-based access controls, the database is pre-seeded with the following default accounts:

| Custodian Username | Default Passphrase | Vault Role Access | Capabilities |
| :--- | :--- | :--- | :--- |
| `submitter` | `Submitter@123` | **SUBMITTER** | Upload digital evidence, add notes, check own submissions history |
| `reviewer` | `Reviewer@123` | **REVIEWER** | View SOC dashboard telemetry, audit pending submissions, override classification, modify release status |
| `lawyer` | `Lawyer@123` | **LAWYER** | Strict read-only case access, download forensic ZIP, run cryptographic disk verification |
| `admin` | `Admin@123` | **ADMIN** | Full administrative rights, view immutable system audit logs, create user accounts, diagnostic status checks |

---

## 🛡️ Forensics & Security Controls

*   **Zero-Tampering Verification:** Reviewers and lawyers can trigger a live integrity verification check. The system scans the physical repository on disk, recalculates the SHA-256 fingerprint of every file, and verifies them against the companion `hashes.json` manifest compiled at upload time. Any file modification, addition, or deletion by third parties immediately triggers a compromised alarm.
*   **Immutable Double Logging:** System events are recorded both to the SQLite `audit_logs` table and written as a continuous stream to the append-only `logs/audit_trail.log` file, ensuring a chronological, legally certifiable record of who accessed or released what evidence.
*   **Strict Folder Segmentation:** Files are logically isolated by Incident Key (e.g. `INC-20260528-ABCD`) and automatically sorted into subfolders: `screenshots/`, `videos/`, `audio/`, or `documents/` depending on checked MIME-types.
*   **Session Inactivity Timeout:** Standard banking-level session verification is active. Session handles expire automatically after 30 minutes of inactivity to protect custody workstations, logging operators out automatically.
