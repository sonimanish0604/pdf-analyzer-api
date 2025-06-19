
### 📍 Project Roadmap

This roadmap outlines potential future enhancements for the PDF Analyzer API. Community feedback and real-world use cases will shape development priorities.

---

#### ✅ Recently Completed
- JavaScript embedded detection (via PyMuPDF/PyPDF2 dual approach)
- Spoofed ZIP/PDF detection via MIME signature
- URL threat scoring using VirusTotal
- In-memory file handling for PII compliance
- MkDocs-based documentation site

---

#### 🚧 Upcoming Enhancements

| Feature | Description | Status |
|--------|-------------|--------|
| 🔁 Background URL scanning | Async queue to scan large URLs in PDFs post-upload | Planned |
| 🧪 YARA Rule Integration | Plug in open-source YARA rules to detect malware families | Planned |
| 🗂️ PDF Stream Dump | Save risky content (like embedded DOCX) as temp files for download | Planned |
| 📦 Docker Package | Dockerfile for containerized deployment | In Progress |
| 🧩 Plugin System | Allow users to extend detection with custom modules | Planned |

---

#### 💡 Stretch Goals

- 🧠 AI-based risk scoring model for PDF heuristics
- 🕵️ Live phishing domain reputation checks
- 🔍 Open Threat Exchange (OTX) and AbuseIPDB integration

---

### 🫱🏽‍🫲 Want to Contribute?

You can:
- Submit issues on GitHub
- Create feature branches and pull requests
- Share real-world threat samples

Let's build a safer PDF world, together!
