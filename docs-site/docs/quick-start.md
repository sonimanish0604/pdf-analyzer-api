# 🚀 Quick Start Guide

This page will walk you through how to clone, install, configure, and run the PDF Analyzer API locally.

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/sonimanish0604/pdf-analyzer-api.git
cd pdf-analyzer-api
```

---

## 2️⃣ Install Python Dependencies

Ensure you have Python 3.9+ installed. Then install all required packages:

```bash
pip install -r requirements.txt
```

> This includes: `fastapi`, `uvicorn`, `PyMuPDF`, `PyPDF2`, `requests`, and `filetype`

---

## 3️⃣ Set the VirusTotal API Key (optional)

This API can integrate with VirusTotal to scan URLs found inside PDFs.

### On PowerShell (Windows):

```powershell
$env:VT_API_KEY = "your_virustotal_key_here"
```

### On macOS/Linux:

```bash
export VT_API_KEY=your_virustotal_key_here
```

> If no key is set, the API will still function, but VirusTotal scoring will be skipped.

---

## 4️⃣ Run the Server

Use `uvicorn` to launch the API server:

```bash
uvicorn main:app --reload
```

Visit the Swagger UI:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Or send a file to the API via curl:

```bash
curl -X POST http://127.0.0.1:8000/analyze-pdf -F "file=@test.pdf"
```

---

## ✅ You’re Ready!

You now have the PDF Analyzer API running locally. Use it to:

* Analyze suspicious files
* Flag phishing URLs
* Detect JavaScript and embedded threats
* Score URLs using VirusTotal (if enabled)

---

➡️ Continue to the **API Usage** section to learn how to format requests and interpret responses.
