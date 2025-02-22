import requests
from bs4 import BeautifulSoup

def is_connected_to_internet():
    try:
        if requests.get('https://google.com').ok:
            return True
    except:
        return False

class GoogleDriveAPI:
    @staticmethod
    def list_files(folder_url):
        response = requests.get(folder_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            divs_with_data_id = soup.find_all("div", attrs={"data-id": True})

            # Store in a dictionary to ensure uniqueness
            file_dict = {}
            for div in divs_with_data_id:
                file_id = div.get("data-id")
                span = div.find("span")  # Find the span inside the div
                file_name = span.text.strip() if span else "Unknown"  # Extract text if found
                
                file_dict[file_id] = file_name  # Dictionary ensures unique file_id keys

            return file_dict
        else:
            print(f"Failed to fetch the page. Status Code: {response.status_code}")
            return {}
    
    def download_file(file_id, file_name):
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))  # Get total file size
            downloaded_size = 0

            with open(file_name, "wb") as file:
                for chunk in response.iter_content(1024):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        # Yield progress as a percentage
                        if total_size > 0:
                            yield int((downloaded_size / total_size) * 100)

            yield 100  # Ensure it reaches 100% at the end
        else:
            yield None  # Indicate failure

if __name__ == "__main__":
    folder_url = "https://drive.google.com/drive/folders/1W17L4b31ORQOKgb415XFu2FseSaV_pCB"
    files = GoogleDriveAPI.list_files(folder_url)
    
    # Print results
    for file_id, file_name in files.items():
        print(f"File ID: {file_id}, File Name: {file_name}")
        GoogleDriveAPI.download_file(file_id, file_name)
