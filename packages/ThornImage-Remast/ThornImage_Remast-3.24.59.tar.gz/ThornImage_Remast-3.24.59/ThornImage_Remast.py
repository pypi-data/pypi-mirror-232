# ThornImage_Remast/image_thorn.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ImageThorn:
    def __init__(self):
        self.session = requests.Session()

    def scrape_images(self, url, output_folder):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Create the output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Find and download images
            img_tags = soup.find_all('img')
            for img_tag in img_tags:
                img_url = img_tag.get('src')
                if img_url:
                    img_url = urljoin(url, img_url)
                    img_data = self.session.get(img_url).content
                    img_filename = os.path.join(output_folder, os.path.basename(img_url))
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(img_data)
                    print(f"Downloaded: {img_filename}")

            print(f"Images scraped and saved to {output_folder}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
