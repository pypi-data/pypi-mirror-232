import pandas as pd

from kami_gsuite.gsuite import KamiGsuite


class KamiGsheetException(Exception):
    pass


class KamiGsheet(KamiGsuite):
    def __init__(self, credentials_path: str, api_version: str):
        super().__init__(
            service_name='sheets',
            service_version=api_version,
            service_scope='spreadsheets',
            credentials_path=credentials_path,
        )

    def get_sheets_service(self):
        if self.service is None:
            self.connect()

    def clear_range(self, sheet_id: str, sheet_range: str) -> bool:
        status = False
        try:
            if self.service is None:
                self.connect()
            clear_values_request_body = {
                'ranges': [sheet_range],
            }
            self.service.spreadsheets().values().clear(
                spreadsheetId=sheet_id, range=sheet_range
            ).execute()
            status = True
        except Exception as e:
            status = False
            raise KamiGsheetException(f'Error clearing range: {e}')
        return status

    def append_dataframe(
        self, df: pd.DataFrame, sheet_id: str, sheet_range: str
    ) -> bool:
        try:
            if self.service is None:
                self.connect()
            values = df.values.tolist()            
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=sheet_range,
                body=body,
                valueInputOption='RAW',
            ).execute()
            status = True
        except Exception as e:
            status = False
            raise KamiGsheetException(f'Error appending dataframe: {e}')
        return status

    def convert_range_to_dataframe(
        self, sheet_id: str, sheet_range: str
    ) -> pd.DataFrame:
        df = pd.DataFrame()
        try:
            if self.service is None:
                self.connect()
            response = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet_id, range=sheet_range)
                .execute()
            )
            values = response.get('values', [])
            if not values:
                return pd.DataFrame()
            df = pd.DataFrame(values[1:], columns=values[0])
        except Exception as e:
            raise KamiGsheetException(
                f'Error converting range to dataframe: {e}'
            )
        return df