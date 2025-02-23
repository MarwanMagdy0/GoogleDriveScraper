import requests
from bs4 import BeautifulSoup
import pyzipper, os

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
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            download_url = GoogleDriveAPI.generate_download_link(response.text)
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
            
            yield 0 # Ensure it reaches 100% at the end

            GoogleDriveAPI.extract_zip(file_name)

            yield 100  # Ensure it reaches 100% at the end
        else:
            yield None  # Indicate failure
    
    @staticmethod
    def generate_download_link(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        form = soup.find('form', id='download-form')
        base_url = form['action']
        params = {input_tag['name']: input_tag['value'] for input_tag in form.find_all('input', type='hidden')}

        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

        download_url = f"{base_url}?{query_string}"

        return download_url
    
    @staticmethod
    def extract_zip(file_name):
        extract_to = os.path.dirname(os.path.abspath(file_name))  # Extract to the same folder
        print(f"Extracting to: {extract_to}")

        with pyzipper.AESZipFile(file_name, "r") as zip_ref:
            zip_ref.setpassword(b"(AESZipFile)")  # Set password for extraction
            zip_ref.extractall(extract_to)  # Extract all files

        print("Extraction completed.")
        os.remove(file_name)

if __name__ == "__main__":
    folder_url = "https://drive.google.com/drive/folders/1W17L4b31ORQOKgb415XFu2FseSaV_pCB"
    files = GoogleDriveAPI.list_files(folder_url)
    
    # Print results
    for file_id, file_name in files.items():
        print(f"File ID: {file_id}, File Name: {file_name}")
        GoogleDriveAPI.download_file(file_id, file_name)
