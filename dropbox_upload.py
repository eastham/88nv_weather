import dropbox

class DropboxUploader:
    def __init__(self, app_key: str, app_secret: str, refresh_token: str):
        self.dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret)

    def upload_file(self, local_file: str, dropbox_file: str) -> bool:
        """
        Uploads a file to Dropbox.

        Args:
            local_file (str): The path to the local file to be uploaded.
            dropbox_file (str): The path to the file in Dropbox.

        Returns:
            bool: True if the file was successfully uploaded, False otherwise.
        """
        try:
            with open(local_file, "rb") as f:
                self.dbx.files_upload(f.read(), dropbox_file, 
                                      mode=dropbox.files.WriteMode("overwrite"))
            return True
        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to upload file: {e}")
            return False
