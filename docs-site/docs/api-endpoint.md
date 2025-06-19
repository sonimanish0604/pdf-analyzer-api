# 📮 API Usage: `POST /analyze-pdf`

This is the main endpoint to upload and scan a PDF for potential threats.

---

## 🔧 Endpoint Details

* **Method:** `POST`
* **URL:** `/analyze-pdf`
* **Content-Type:** `multipart/form-data`
* **Form Field:** `file` (PDF document)

---

## 🧪 Sample cURL Request

```bash
curl -X POST http://127.0.0.1:8000/analyze-pdf \
  -F "file=@test.pdf"
```

---

## 📥 Request Example (form-data)

| Field | Type   | Description             |
| ----- | ------ | ----------------------- |
| file  | binary | PDF file to be analyzed |

---

## 📤 Example JSON Response

```json
{
  "summary": {
    "valid_pdf": true,
    "encrypted": false,
    "embedded_javascript": false,
    "embedded_files": true,
    "embedded_file_names": ["invoice.zip"],
    "urls_found": {
      "safe": [
        {
          "url": "https://example.com",
          "vt_status": "clean",
          "vt_score": "0/91",
          "vt_comment": "✅ No engines flagged"
        }
      ],
      "suspicious": [
        {
          "url": "http://badsite.ru",
          "vt_status": "malicious",
          "vt_score": "5/91",
          "vt_comment": "⚠️ Flagged by 5 of 91 engines"
        }
      ]
    }
  },
  "verdict": "⚠️ Suspicious file — contains JavaScript or embedded files"
}
```

---

## ✅ Verdict Explanation

| Verdict Message                                   | Meaning                                  |
| ------------------------------------------------- | ---------------------------------------- |
| ✅ File appears safe                               | No issues found                          |
| 🔒 File is encrypted                              | Cannot inspect content                   |
| ⚠️ Suspicious file — contains JavaScript or files | Detected risky features                  |
| 🚫 Contains suspicious URLs                       | One or more links flagged by VirusTotal  |
| ❌ Invalid or spoofed PDF                          | File is not a real PDF or has wrong MIME |

---

➡️ Continue to the **Threat Categories** section to understand each risk flag in more detail.
