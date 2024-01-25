import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile
import shutil

def download_file(url, folder):
    response = requests.get(url)
    filename = os.path.join(folder, url.split("/")[-1])
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")
    return filename

def extract_zip(zip_path, extract_folder):
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print(f"Extracted: {zip_path}")

def download_and_extract_zip(url, download_folder, extract_folder):
    zip_path = download_file(url, download_folder)
    extract_zip(zip_path, extract_folder)

def download_zip_files(url, download_folder, extract_folder):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Create the download folder if it doesn't exist
    os.makedirs(download_folder, exist_ok=True)

    # Find all hyperlinks on the page
    for link in soup.find_all('a'):
        href = link.get('href')
        if href.endswith('.zip'):
            # Join the URL to get the absolute path
            absolute_url = urljoin(url, href)
            print(absolute_url)
            download_and_extract_zip(absolute_url, download_folder, extract_folder)

if __name__ == "__main__":
    url = "https://tikipeter.github.io/packages/"  # Replace with the actual URL
    download_folder = "zips"
    extract_folder = "repo"

    download_zip_files(url, download_folder, extract_folder)
    shutil.rmtree(download_folder)
