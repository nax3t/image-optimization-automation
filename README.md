# Image Optimization Automation with Cloudinary

## Usage

### Check if Python is installed
To check if Python is installed on your system, open a terminal and run: `python --version`

If Python is installed, you should see the version number. If not, you'll need to install it.

### Install Python if needed
Follow the instructions for your operating system:

- **Windows**: Download the installer from [python.org](https://www.python.org/downloads/windows/) and run it.
- **Mac**: Python comes pre-installed on Mac, but you can install the latest version using [Homebrew](https://brew.sh/) with `brew install python`.
- **Linux**: Use your distribution's package manager, for example on Ubuntu use `sudo apt-get install python3`.

### Create Python Virtual Environment
Creating a virtual environment is recommended to manage dependencies.

- **Windows**:
`python -m venv .venv`
- **Mac/Linux**:
`python3 -m venv .venv`

### Activate Virtual Environment
Before running the script, you need to activate the virtual environment.

- **Windows**:
`.venv\Scripts\activate`
- **Mac/Linux**:
`source .venv/bin/activate`

### Install Dependencies
Install the required packages using pip: `pip install beautifulsoup4 cloudinary`

### Create automation.py
Create a file named `automation.py` in your project directory and add your script code to this file.

```py
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
    response = uploader.upload(image_path, format="webp")
    secure_url = response.get('secure_url')
    if secure_url:
        secure_url = secure_url.replace('/upload/', '/upload/q_auto/w_auto/')
    return secure_url

def find_images(directory):
    """
    Recursively searches through a directory and its subdirectories for images,
    uploading them to Cloudinary.
    """
    for filename in os.listdir(directory):
        if "_copy" in filename:
            continue
        path = os.path.join(directory, filename)
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
    with open(path, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    modified = upload_and_replace_images(soup, "img", "src") or \
               upload_and_replace_in_style(soup)

    if modified:
        save_file(soup, path, "_copy.html")

def process_css(path):
    """
    Searches a CSS file for image URLs, uploads them to Cloudinary, and replaces URLs.
    """
    with open(path, "r") as file:
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
    with open(new_path, "w") as file:
        file.write(str(content))

def main():
    cloud_name, api_key, api_secret = get_credentials()
    configure_cloudinary(cloud_name, api_key, api_secret)
    print("Uploading images... Please wait.")
    find_images(".")
    print("Image upload complete.")

if __name__ == "__main__":
    main()
```

### Run Script
To run the automation script, make sure your virtual environment is activated, then run the following command in your terminal: 
- **Windows:** `python automation.py`
- **Mac/Linux:** `python3 automation.py`

This will make copies of your html and css files with a `_copy` suffix, once you have confirmed the changes you can rename the files to overwrite the originals. Please note, the html files will have lost their formatting, but this can easily be fixed with a formatter like Prettier.