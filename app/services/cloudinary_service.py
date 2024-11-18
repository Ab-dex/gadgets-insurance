import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
import os
from flask import current_app

class CloudinaryService:
    def __init__(self):
        # You can set up your configuration here (optional if set via environment variables)
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )

    def upload_image(self, file, filename, folder="uploads"):
        """
        Upload an image to Cloudinary.
        :param file: the file object to be uploaded (e.g., from a Flask form).
        :param folder: the folder in Cloudinary where the image will be uploaded.
        :return: the public URL of the uploaded image
        """
        try:
            # Secure the filename before uploading
            filename = secure_filename(filename)
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                public_id=filename,
                unique_filename=True
            )
            return result.get("url")  # Return the public URL of the uploaded image
        except cloudinary.exceptions.Error as e:
            # Handle any Cloudinary-specific exceptions
            current_app.logger.error(f"Error uploading to Cloudinary: {e}")
            return None

    def delete_image(self, public_id):
        """
        Delete an image from Cloudinary by public_id.
        :param public_id: The public ID of the image to be deleted.
        :return: True if deletion is successful, False otherwise.
        """
        try:
            cloudinary.uploader.destroy(public_id)
            return True
        except cloudinary.exceptions.Error as e:
            current_app.logger.error(f"Error deleting image from Cloudinary: {e}")
            return False
