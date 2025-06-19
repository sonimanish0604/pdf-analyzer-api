# 🔍 Threat Categories Explained

This section describes the different types of threats the PDF Analyzer API can detect.

---

## 🧾 1. Valid PDF Check

Ensures the uploaded file:

* Has a `.pdf` extension
* Contains a valid PDF header and structure
* Isn't a renamed or spoofed file (e.g., a ZIP pretending to be PDF)

**Verdict if failed:** `❌ Invalid or spoofed PDF`

---

## 🔒 2. Password Protection / Encryption

Detects whether a PDF:

* Is encrypted or password-protected
* Cannot be opened without user input

**Impact:** File cannot be inspected for other threats.

**Verdict if encrypted:** `🔒 File is encrypted`

---

## 📜 3. Embedded JavaScript

JavaScript embedded inside a PDF can:

* Open popups or malicious links
* Auto-execute code upon open
* Be used for phishing or remote access

**Detection Method:**

* Looks for `/JavaScript` objects and triggers

**Verdict if found:** `⚠️ Suspicious file — contains JavaScript`

---

## 📎 4. Embedded Files (DOCX, ZIP, EXE)

PDFs can include attachments:

* `.doc`, `.xls`, `.zip`, `.exe`, `.scr`, `.js`

**Detection Method:**

* Scans for `/EmbeddedFile` references
* Extracts MIME info from embedded streams

**Verdict if found:** `⚠️ Suspicious file — contains embedded files`

---

## 🌐 5. URLs Inside PDFs

Extracts and inspects all URLs embedded in the document.

**Risky examples:**

* `http://paypal.com.secure-login.biz`
* `http://update.microsoft.com.securitycheck.ru`

### Lookup checks:

* DNS resolution using `socket.gethostbyname`
* VirusTotal API score (if API key provided)

**Verdict if flagged:** `🚫 Contains suspicious URLs`

---

➡️ Next: See how verdicts are summarized in the response, and how to troubleshoot false negatives or integration issues.
