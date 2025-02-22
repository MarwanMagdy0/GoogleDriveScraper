import requests
from bs4 import BeautifulSoup

URL = "https://drive.google.com/drive/folders/1W17L4b31ORQOKgb415XFu2FseSaV_pCB"  # Replace with your actual folder URL
BASE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="  # Google Drive direct download format

# Send a request to fetch the page content
response = requests.get(URL)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all divs that have a 'data-id' attribute
    divs_with_data_id = soup.find_all("div", attrs={"data-id": True})

    for div in divs_with_data_id:
        data_id = div.get("data-id")
        span = div.find("span")  # Find the first span inside the div
        file_name = span.text.strip() if span else f"{data_id}.pdf"  # Default name if no span

        download_url = f"{BASE_DOWNLOAD_URL}{data_id}"  # Construct the direct download URL
        print(f"Downloading: {file_name} from {download_url}")

        # Send request to download the file
        file_response = requests.get(download_url, stream=True)

        if file_response.status_code == 200:
            with open(file_name, "wb") as file:
                for chunk in file_response.iter_content(1024):  # Download in chunks
                    file.write(chunk)
            print(f"✔ Downloaded: {file_name}")
        else:
            print(f"❌ Failed to download {file_name} (Status: {file_response.status_code})")

else:
    print(f"Failed to fetch the page. Status Code: {response.status_code}")
