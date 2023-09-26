from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from os import path
from .constants import ROOT_DIR
class KamiGsuiteException(Exception):
    pass


class KamiGsuite:
    def __init__(
        self,
        service_name: str = None,
        service_version: str = None,
        service_scope: str = None,
        credentials_path: str = None,        
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.service_scope = service_scope
        self.credentials_path = credentials_path        
        self.credentials = None
        self.service = None

    def _load_credentials(self):
        if not path.exists(self.credentials_path):
            raise KamiGsuiteException(f'Credentials file not found: {self.credentials_path}')
        
        self.credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=[f'https://www.googleapis.com/auth/{self.service_scope}'],
        )

    def _create_service(self):
        self.service = build(self.service_name, self.service_version, credentials=self.credentials)

    def connect(self) -> bool:            
        try:
            self._load_credentials()
            self._create_service()                
            if not self.credentials.valid:                              
                self.credentials = self.credentials.refresh(Request())                
                        
            return True if self.service else None        
        except Exception as e:
            raise KamiGsuiteException(
                f'Error connecting to {self.service_name}: {e}'
            )
