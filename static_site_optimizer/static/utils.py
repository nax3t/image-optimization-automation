import os
import re
import cloudinary
from cloudinary import uploader
from bs4 import BeautifulSoup

def get_credentials():
    """
    Retrieves Cloudinary credentials from environment variables or user input.
    """
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME") or input("Enter Cloudinary Cloud Name: ")
    api_key = os.getenv("CLOUDINARY_API_KEY") or input("Enter Cloudinary API Key: ")
    api_secret = os.getenv("CLOUDINARY_API_SECRET") or input("Enter Cloudinary API Secret: ")
    return cloud_name, api_key, api_secret

def configure_cloudinary(cloud_name, api_key, api_secret):
    """
    Configures Cloudinary with the provided credentials.
    """
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)

def upload_image(image_path):
    """
    Uploads an image to Cloudinary and returns its secure URL.
    """
    print("IMAGE PATH", image_path)
    full_image_path = os.path.join(temp_dir, extracted_folder, image_path)
    response = uploader.upload(full_image_path, format="webp")
    secure_url = response.get('secure_url')
    if secure_url:
        secure_url = secure_url.replace('/upload/', '/upload/f_auto,q_auto/w_auto/')
    return secure_url

def find_images(directory):
    """
    Recursively searches through a directory and its subdirectories for images,
    uploading them to Cloudinary.
    """
    for filename in os.listdir(directory):
        if "_copy" in filename:
            continue
        path = os.path.join(temp_dir, filename)
        if os.path.isfile(path):
            process_file(path)
        elif os.path.isdir(path):
            find_images(path)

def process_file(path):
    """
    Processes a single file, either HTML or CSS, and uploads images to Cloudinary.
    """
    if "_copy" in path:
        return
    if path.endswith(".html"):
        process_html(path)
    elif path.endswith(".css"):
        process_css(path)

def process_html(path):
    """
    Parses an HTML file, uploads images to Cloudinary, and replaces image URLs.
    """
    with open(path, "r", encoding='utf-8') as file:
        soup = BeautifulSoup(file, "html.parser")

    modified = upload_and_replace_images(soup, "img", "src") or \
               upload_and_replace_in_style(soup)

    if modified:
        save_file(soup, path, "_copy.html")

def process_css(path):
    """
    Searches a CSS file for image URLs, uploads them to Cloudinary, and replaces URLs.
    """
    with open(path, "r", encoding='utf-8') as file:
        content = file.read()

    modified = False
    pattern = r"url\(['\"]?(.*?)['\"]?\)"
    for match in re.findall(pattern, content):
        image_path = match.strip('\'"')
        if not image_path.startswith("http"):
            secure_url = upload_image(image_path)
            if secure_url:
                content = content.replace(match, secure_url)
                modified = True

    if modified:
        save_file(content, path, "_copy.css")

def upload_and_replace_images(soup, tag_name, attribute):
    """
    Finds and replaces image URLs in the specified tag and attribute.
    """
    modified = False
    for element in soup.find_all(tag_name):
        image_url = element.get(attribute)
        if image_url and not image_url.startswith("http"):
            secure_url = upload_image(image_url)
            if secure_url:
                element[attribute] = secure_url
                modified = True
    return modified

def upload_and_replace_in_style(soup):
    """
    Finds and replaces image URLs in inline styles.
    """
    modified = False
    style_pattern = r"background-image\s*:\s*url\(['\"]?(.*?)['\"]?\)"
    for element in soup.find_all(style=True):
        style = element.get("style")
        for match in re.findall(style_pattern, style, re.IGNORECASE):
            image_url = match.strip('\'"')
            if not image_url.startswith("http"):
                secure_url = upload_image(image_url)
                if secure_url:
                    new_style = style.replace(match, secure_url)
                    element['style'] = new_style
                    modified = True
    return modified

def save_file(content, original_path, new_extension):
    """
    Saves the modified content to a new file, asking for confirmation if the file already exists.
    """
    new_path = original_path.rsplit('.', 1)[0] + new_extension
    if os.path.exists(new_path):
        confirm = input(f"The file {new_path} already exists. Do you want to overwrite it? (y/n): ")
        if confirm.lower() != 'y':
            print("Not overwriting the existing file.")
            return
    with open(new_path, "w", encoding='utf-8') as file:
        file.write(str(content))

def optimize_static_site(temp_dir_from_view, extracted_folder_from_view):
    global temp_dir
    global extracted_folder
    temp_dir = temp_dir_from_view
    extracted_folder = extracted_folder_from_view
    cloud_name, api_key, api_secret = get_credentials()
    configure_cloudinary(cloud_name, api_key, api_secret)
    print("Uploading images... Please wait.")
    find_images(temp_dir)
    print("Image upload complete.")
