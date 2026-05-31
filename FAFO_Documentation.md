# FAFO - Full Project Documentation

Generated documentation for the FAFO (Forensic Analysis & Forensic Operations) project.

---

## 1. System Design Explanation

**Overview:**

FAFO is a Streamlit-based web application designed to collect, store, and manage multimedia evidence for online incidents. The architecture is modular, combining a Streamlit frontend with a Python backend composed of modules for authentication, OCR, video processing, hashing, storage management, notifications, and role-based access control.

**Components:**

- Frontend: `app.py` built with Streamlit.
- Modules: `modules/` directory containing business logic (`auth.py`, `ocr_engine.py`, `ffmpeg_processor.py`, `repository.py`, etc.).
- Configuration: `config/` with `settings.py` and `roles.py`.
- Storage: `evidence_repository/` for uploaded evidence and a `database/` folder containing schema and initialization scripts.
- External binaries: Tesseract (OCR) and FFmpeg/ffprobe (video processing) detected at runtime with fallbacks.

**Data Flow:**

1. User logs in and selects a role (submitter/reviewer/lawyer/admin).
2. Submitter fills form and uploads evidence or provides source URL.
3. Backend generates Incident ID, timestamps, stores files into an organized incident folder, computes hashes, runs OCR or media analysis, and logs activity.
4. Notifications are sent automatically to configured recipients.
5. Reviewers and admins manage evidence and approve access for lawyers.

---

## 2. Screenshots of the Website

> NOTE: Replace the placeholders below with actual screenshots taken from the running app. Place images in the `docs/screenshots/` folder and edit this file or insert them into Word/PDF.

- **Login Page** — [PLACEHOLDER]
- **Submitter Form** — [PLACEHOLDER]
- **Reviewer Dashboard** — [PLACEHOLDER]
- **Lawyer Portal** — [PLACEHOLDER]

Instructions to capture screenshots:

1. Run locally: `streamlit run app.py` and open `http://localhost:8501`.
2. Use OS screenshot tools (Snipping Tool / macOS Screenshot / GNOME Screenshot).
3. Resize/crop images to fit page.

---

## 3. Database / Storage Explanation

**Storage Model:**

FAFO supports a filesystem-based evidence repository and an optional relational database for metadata. The `database/schema.sql` defines the tables for incidents, evidence items, users, roles, and audit trails. The recommended production deployment uses a managed database (PostgreSQL) for robustness and the filesystem (or object storage like S3) for large binary evidence files.

**Key tables and purpose:**

- `incidents`: Incident metadata (id, title, category, status, timestamps).
- `evidence`: Records for each evidence file (path, hash, mimetype, size, incident_id, uploaded_by).
- `users`: Authentication and role assignment.
- `audit_logs`: Immutable log of actions for chain-of-custody and compliance.

**Storage best practices:**

- Store binary evidence separately from metadata.
- Use object storage with versioning and lifecycle rules for retention.
- Keep cryptographic hashes (SHA-256) in the database for integrity verification.

---

## 4. Evidence Folder Structure

Recommended directory layout for each incident:

```
evidence_repository/
└── INC-<YYYYMMDD>-<ID>/
    ├── documents/    (PDFs, text reports)
    ├── images/       (screenshots, photos)
    ├── audio/        (recorded interviews, calls)
    ├── video/        (screen recordings, footage)
    ├── metadata.json (incident metadata and file index)
    └── hashes.json   (SHA-256 hashes for each file)
```

Example: `evidence_repository/INC-20260530-P5LZ/images/shot1.png`

---

## 5. User Tutorial

Follow these steps to use FAFO:

1. Open the FAFO web application.
2. Enter the correct password.
3. Choose the correct role area: submitter, reviewer, lawyer, or admin.
4. To submit a case, paste the social media source URL.
5. Enter incident details, including category, target, notes, and submitter name.
6. Upload screenshots, screen recordings, audio files, PDFs, or other evidence.
7. Click “Submit Incident.”
8. The system automatically creates an incident ID, timestamps the submission, stores uploaded files, generates file hashes, and sends an email notification.
9. Reviewers can search cases, review evidence, and update case status.
10. Admins can approve evidence for lawyer access.
11. Lawyers can access approved evidence through the lawyer portal and download case packets.

---

## 6. Reflection Paper

**Purpose and findings:**

FAFO demonstrates how accessible tools can support responsible digital evidence collection and preservation while balancing privacy and integrity. The modular architecture simplifies testing, extension, and replacement of components such as OCR or media analysis. Emphasis on role-based access ensures limited exposure of sensitive content to authorized personnel only.

**Technical lessons:**

- Runtime detection for system binaries (Tesseract/FFmpeg) increases portability.
- Separating metadata from binary storage enables efficient indexing and secure transfer.
- Cryptographic hashing and audit logging are critical for chain-of-custody.

---

## Reflection Questions (with answers)

1. **Why is digital evidence preservation important?**

Digital evidence preservation is crucial to maintain a verifiable record of events for investigations and legal proceedings. Without proper preservation, evidence may be altered, lost, or challenged in court.

2. **How does hashing support file integrity?**

Hashing (e.g., SHA-256) provides a fingerprint of file content. Any modification changes the hash, enabling detection of tampering and ensuring integrity during transfer and storage.

3. **What privacy risks exist when storing sensitive evidence?**

Risks include unauthorized access, data leakage, inadequate retention policies, and improper sharing. Sensitive metadata (names, locations) can expose individuals if not handled correctly.

4. **Why should the system remain private instead of public?**

Keeping the system private minimizes exposure, reduces attack surface, and helps ensure controlled access to sensitive evidence. Public systems risk unauthorized retrieval or misuse.

5. **How can notification automation improve response time?**

Automated notifications alert stakeholders immediately when new evidence is submitted, enabling faster triage and timely investigative actions.

6. **Why is role-based access important?**

Role-based access enforces least privilege: users only see and perform actions allowed by their role, protecting sensitive data and maintaining separation of duties.

7. **What are the limitations of this system?**

Limitations include reliance on host binaries for advanced processing, possible scalability constraints for large-scale media repositories, and the need for secure hosting and rigorous access controls.

8. **How could the system be improved in the future?**

Future improvements: cloud-native object storage integration, strong encryption at rest, multi-factor authentication, immutable storage/backups, advanced analytics, and finer-grained access controls.

---

## 7. Cost Estimate

High-level estimated monthly costs for a small production deployment (USD):

- Hosting & compute: $20 - $100 (small VM or managed app services)
- Object storage (S3 or equivalent): $5 - $50 depending on volume
- Database (managed PostgreSQL): $15 - $50
- Backup & retention: $5 - $30
- Domain, email, operational costs: $5 - $20

**Estimated monthly total:** $50 - $250 (varies with usage)

---

## 8. Security & Privacy Explanation

**Security controls and recommendations:**

- Authentication: Enforce strong passwords and consider MFA.
- Authorization: Role-based access control with least privilege.
- Encryption: Use TLS in transit and encrypt sensitive data at rest.
- Audit: Maintain immutable audit logs for all access and exports.
- Hashing: Record SHA-256 hashes for integrity checks.
- Retention: Define retention policies and secure deletion procedures.
- Access approvals: Admin approval flow before granting lawyers access to sensitive packs.

---

## Final Project Summary

FAFO is a secure multimedia evidence preservation platform designed for documenting online incidents. It combines information systems, cybersecurity, digital forensics, automation, file management, and user workflow design. The system demonstrates how technology can support responsible documentation, evidence integrity, privacy, and organized incident response.

---

## How to convert this Markdown to Word (.docx)

If you want a Word document, run this locally (requires Pandoc):

```bash
pandoc FAFO_Documentation.md -o FAFO_Documentation.docx
```

Or open the Markdown in Microsoft Word and save as `.docx`.

---

*Document generated programmatically; update placeholders and add screenshots as needed.*
