import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
import imagehash
from io import BytesIO

def download_images_from_page(url):
    print(f"Fetching images from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    img_urls = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        # Handle relative URLs
        img_url = urljoin(url, src)
        # Only HTTP/HTTPS
        if urlparse(img_url).scheme in ['http', 'https']:
            img_urls.append(img_url)
    return img_urls

def download_image(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content))
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

def find_similar_images_on_web(target_image_path, website_urls, threshold=5):
    target_image = Image.open(target_image_path)
    target_hash = imagehash.phash(target_image)

    results = []

    for site_url in website_urls:
        img_urls = download_images_from_page(site_url)
        print(f"Found {len(img_urls)} images on {site_url}")

        for img_url in img_urls:
            img = download_image(img_url)
            if img is None:
                continue
            try:
                img_hash = imagehash.phash(img)
                diff = target_hash - img_hash
                if diff <= threshold:
                    results.append((site_url, img_url, diff))
            except Exception as e:
                print(f"Error processing image {img_url}: {e}")

    return results

# Example usage
if __name__ == "__main__":
    target_img = r"C:\Users\bsccybs001\Pictures\Kani.png"  # Path to your local image to check
    websites_to_check = [
        "https://www.google.com",
        "https://www.facebook.com",
        "https://www.fsh.srmrmp.edu.in/",
        "https://www.linkedin.edu.in/"
        
    ]

    matches = find_similar_images_on_web(target_img, websites_to_check)

    if matches:
        print("\nPotential breaches found:")
        for site, img_url, diff in matches:
            print(f"Site: {site}")
            print(f"Image URL: {img_url}")
            print(f"Hash difference: {diff}")
            print("-" * 40)
    else:
        print("No similar images found on the given websites.")
