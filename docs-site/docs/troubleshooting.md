# 🛠️ Troubleshooting & Error Handling

This section covers common problems encountered while using the PDF Analyzer API and how to fix them.

---

## ❗ Issue: "File appears safe" but known JavaScript present

**Cause:** Older versions of `PyMuPDF` or malformed JS triggers.

**Solution:**

* Ensure you're using `PyMuPDF >= 1.21`
* Use CLI version to cross-validate
* Check console logs for `get_javascript` errors

---

## ❗ Issue: Embedded files not detected

**Cause:** The file might use non-standard `/EmbeddedFile` wrappers or compressed object streams.

**Solution:**

* Try uncompressing the PDF externally and re-scan
* Look for base64-encoded embedded streams manually

---

## 🔐 Issue: File is encrypted or password protected

**Cause:** API is designed not to attempt brute-forcing.

**Solution:**

* Verdict will return `"encrypted": true`
* Decrypt manually if you trust the source

---

## 🌐 Issue: VirusTotal returns `dns_error`

**Cause:** The domain could not be resolved.

### Possible reasons:

| Symbol | Reason                       |
| ------ | ---------------------------- |
| 🌐     | No internet connection       |
| 🔒     | DNS blocked by VPN/firewall  |
| 🧪     | Test URLs are spoofed/fake   |
| 🚫     | Typos or placeholder domains |

**Solution:**

* Make sure you're online
* Test resolving the domain with `ping` or `nslookup`

---

## 🧪 Issue: VirusTotal key not found

**Cause:** The `VT_API_KEY` environment variable is not set.

**Solution:**

* Set the variable before starting your server:

  **Windows PowerShell**:

  ```powershell
  $env:VT_API_KEY = "your_key_here"
  ```

  **Linux/macOS**:

  ```bash
  export VT_API_KEY=your_key_here
  ```

* Restart the server after setting the key

---

➡️ Go to the **Future Roadmap** to see what features are planned next.
