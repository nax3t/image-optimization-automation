from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from .forms import UploadForm
from .utils import optimize_static_site
import os
import zipfile
# Create your views here.
def index(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            zip_file = request.FILES['zip_file']  # Assuming your form field is named 'zip_file'

            # Extract the zip file
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)  # Create directory if it doesn't exist

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                extracted_folder = zip_ref.namelist()[0]
            # Run the script against the extracted files
            optimize_static_site(temp_dir, extracted_folder)  # Replace with your script's call

            # Create a zip file of the optimized contents
            optimized_zip_path = os.path.join(settings.MEDIA_ROOT, 'optimized_static_site.zip')
            with zipfile.ZipFile(optimized_zip_path, 'w') as zip_ref:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zip_ref.write(file_path, arc_name)
            
            # Provide feedback to the user
            messages.success(request, 'Zip file processed successfully!')
            with open(optimized_zip_path, 'rb') as f:
                response = HttpResponse(f, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=optimized_static_site.zip'
                return response
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = UploadForm()

    return render(request, 'static/index.html', {'form': form})
