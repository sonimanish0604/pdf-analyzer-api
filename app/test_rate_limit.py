import requests

API_URL = "https://pdf-analyzer-api-staging.onrender.com/analyze-pdf"
API_KEY = "c6035ee5d451.Tae_iK4iNjSVRGRrNA570Yeaxw4UWQtfgmn_82eVmk0"  # Replace with your real key
FILE_PATH = "C:\\Users\\sonim\\OneDrive\\Documents\\GitHub\\aegisdocs-rebuilt\\pdf-analyzer-api\\samples\\pdfanalyzer-testdoc.pdf"  # Replace with an actual test PDF path

HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json"
}

def test_burst_requests(n=15):
    for i in range(n):
        print(f"\nRequest {i+1}:")

        with open(FILE_PATH, "rb") as f:
            files = {'file': f}
            response = requests.post(API_URL, headers=HEADERS, files=files)

        print(f"Status: {response.status_code}")
        print("Response text:", response.text[:200])  # first 200 chars

        try:
            data = response.json()
            if response.status_code == 429:
                print("Rate limited:", data)
            else:
                print("Verdict:", data.get("verdict"))
        except Exception as e:
            print("JSON decode failed:", e)

if __name__ == "__main__":
    test_burst_requests()
