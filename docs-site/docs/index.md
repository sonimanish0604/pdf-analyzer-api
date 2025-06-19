# Welcome to PDF Analyzer API Docs

This is the documentation site for the **PDF Analyzer API**, a lightweight Python FastAPI service to detect common threats in PDF files.

---

## Why this project?

Security researchers and developers need a quick way to:

* Scan uploaded PDF files
* Check for embedded threats like JavaScript, ZIP files, or obfuscated links
* Avoid storing uploaded content on disk
* Leverage threat intelligence (VirusTotal) without writing complex code

This API helps solve those problems with:

* ⚡ In-memory file scanning
* 🌐 URL validation and scoring
* 🔒 Secure for PII workflows

---

## Key Capabilities

| Capability               | Description                    |
| ------------------------ | ------------------------------ |
| Valid PDF Check          | Ensures file is parseable PDF  |
| JavaScript Detection     | Detects embedded scripts       |
| Encryption Check         | Flags password-protected files |
| Embedded File Detection  | Finds DOCX/ZIP in PDF stream   |
| URL Extraction & Scoring | DNS lookup + VirusTotal score  |

---

Use the left navigation to:

* ⚙️ Set up and run the app
* 📮 Try the endpoint
* 🧠 Learn what each threat means
* 🚀 Track future roadmap ideas

Happy scanning! ✨
