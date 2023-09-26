from os import makedirs, path
from typing import Dict, List

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from kami_filemanager import get_file_list_from

from kami_gsuite.gsuite import KamiGsuite


class KamiGdriveException(Exception):
    pass


class KamiGdrive(KamiGsuite):
    def __init__(self, credentials_path: str, api_version: str):
        super().__init__(service_name='drive', service_version=api_version, service_scope='drive', credentials_path=credentials_path)

    def _verify_filepath(self, filepath: str):
        if not path.exists(filepath) or not path.isfile(filepath):
            raise FileNotFoundError(f'File not found: {filepath}')

    def _verify_folderpath(self, folderpath: str):
        if not path.exists(folderpath) or not path.isdir(folderpath):
            raise FileNotFoundError(f'Folder not found: {folderpath}')

    def _get_file_metadata(self, filepath: str, folder_id: str) -> dict:
        return {'name': path.basename(filepath), 'parents': [folder_id]}

    def exists(self, object_id: str) -> bool:
        object_exists = False
        try:
            if self.service is None:
                self.connect()

            file = (
                self.service.files()
                .get(fileId=object_id, fields='id')
                .execute()
            )
            object_exists = 'id' in file

        except Exception as e:
            raise KamiGdriveException(f'Error: {e}')

        return object_exists

    def get_folder_id(self, parent_folder_id: str, folder_name: str) -> str:
        try:
            if self.service is None:
                self.connect()

            if not parent_folder_id:
                raise KamiGdriveException(f'parent_folder_id is empty.')
            if not folder_name:
                raise KamiGdriveException(f'folder_name is empty.')

            if parent_folder_id and folder_name:
                query = (
                    f"'{parent_folder_id}' in parents and name='{folder_name}'"
                )
                results = self.service.files().list(q=query).execute()
                files = results.get('files', [])

            if files:
                return files[0]['id']
            else:
                return None
        except Exception as e:
            raise KamiGdriveException(f'Error searching for folder: {e}')

    def create_folder(
        self, parent_folder_id: str, new_folder_name: str
    ) -> str:
        new_folder_id = None
        try:
            existing_folder_id = self.get_folder_id(
                parent_folder_id, new_folder_name
            )

            if existing_folder_id:
                new_folder_id = existing_folder_id

            file_metadata = {
                'name': new_folder_name,
                'parents': [parent_folder_id],
                'mimeType': 'application/vnd.google-apps.folder',
            }
            folder = self.service.files().create(body=file_metadata).execute()
            new_folder_id = folder['id']

        except Exception as e:
            raise KamiGdriveException(f'Error creating folder: {e}')

        return new_folder_id

    def upload_file_to(self, filepath: str, folder_id: str) -> str:
        try:
            if self.service is None:
                self.connect()

            self._verify_filepath(filepath)
            file_metadata = self._get_file_metadata(filepath, folder_id)
            media = MediaFileUpload(filepath)
            uploaded_file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields='id',
                )
                .execute()
            )

            return uploaded_file.get('id')

        except FileNotFoundError as e:
            raise KamiGdriveException(f'File not found: {e}')
        except Exception as e:
            raise KamiGdriveException(f'Error uploading file: {e}')

    def is_folder(self, object_id: str) -> bool:
        try:
            if not self.exists(object_id):
                raise KamiGdriveException(
                    f"Object with ID '{object_id}' does not exist."
                )

            file = (
                self.service.files()
                .get(fileId=object_id, fields='mimeType')
                .execute()
            )
            mime_type = file.get('mimeType', '')

            return mime_type == 'application/vnd.google-apps.folder'

        except Exception as e:
            raise KamiGdriveException(f'Error getting object type: {e}')

    def upload(self, object_path: str, folder_id: str) -> List[dict]:
        uploaded_file_list = List[dict]
        object_name = path.basename(object_path)
        try:
            if not self.exists(folder_id):
                raise KamiGdriveException(
                    f"Folder with ID '{folder_id}' does not exist."
                )

            if path.isfile(object_path):
                file_id = self.upload_file_to(object_path, folder_id)
                uploaded_file_list.append(
                    {'filename': object_name, 'gdrive_id': file_id}
                )

            if path.isdir(object_path):
                folder_id = self.create_folder(folder_id, object_name)
                for new_object in get_file_list_from(object_path):
                    self.upload(new_object, folder_id)

        except Exception as e:
            raise KamiGdriveException(f'Error uploading file: {e}')

        return uploaded_file_list

    def get_object_name(self, object_id: str) -> str:
        object_name = None
        try:
            if self.exists(object_id):
                file = (
                    self.service.files()
                    .get(fileId=object_id, fields='name')
                    .execute()
                )
                object_name = file.get('name')

                if not object_name:
                    raise KamiGdriveException(
                        f"Unable to retrieve object name for ID '{object_id}'."
                    )
        except Exception as e:
            raise KamiGdriveException(f'Error: {e}')

        return object_name

    def get_objects_from(self, folder_id: str) -> List[Dict]:
        objects_list = List[Dict]

        try:
            if not self.is_folder(folder_id):
                raise KamiGdriveException(
                    f"Object with ID '{folder_id}' is not a folder."
                )

            query = f"'{folder_id}' in parents"
            results = (
                self.service.files()
                .list(q=query, fields='files(id, name, mimeType)')
                .execute()
            )

            for result in results.get('files', []):
                object_id = result['id']
                object_name = result['name']
                object_type = 'folder' if self.is_folder(object_id) else 'file'
                object_dict = {
                    'name': object_name,
                    'id': object_id,
                    'type': object_type,
                }

                if self.is_folder(object_id):
                    object_dict['content'] = self.get_objects_from(object_id)
                else:
                    object_dict['content'] = None

                objects_list.append(object_dict)

            return objects_list

        except Exception as e:
            raise KamiGdriveException(
                f'Error getting objects from folder: {e}'
            )

    def download_file_from(self, file_id: str, folderpath: str) -> str:
        try:
            if not self.exists(file_id):
                raise KamiGdriveException(
                    f"File with ID: '{folderpath}' does not exist."
                )

            if self.is_folder(file_id):
                raise KamiGdriveException(
                    f"Object with ID: '{folderpath}' is not a file."
                )

            if not path.exists(folderpath):
                raise KamiGdriveException(
                    f"Folderpath '{folderpath}' does not exist."
                )

            filename = self.get_object_name(file_id)
            file_path = path.join(folderpath, filename)

            request = self.service.files().get_media(fileId=file_id)
            with open(file_path, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return file_path

        except Exception as e:
            raise KamiGdriveException(f'Error downloading file: {e}')

    def download(self, object_id: str, folderpath: str) -> str:
        destination_path = None
        try:
            self._verify_folderpath(folderpath)

            if not self.exists(object_id):
                raise KamiGdriveException(
                    f"Object with ID '{object_id}' does not exist."
                )
            object_name = self.get_object_name(object_id)
            destination_path = path.join(folderpath, object_name)
            if self.is_folder(object_id):                
                if not path.exists(destination_path):
                    makedirs(destination_path)

                objects = self.get_objects_from(object_id)
                for obj in objects:
                    self.download(obj['id'], destination_path)
            else:
                self.download_file_from(object_id, folderpath)

            return destination_path

        except Exception as e:
            raise KamiGdriveException(f'Error downloading object: {e}')
