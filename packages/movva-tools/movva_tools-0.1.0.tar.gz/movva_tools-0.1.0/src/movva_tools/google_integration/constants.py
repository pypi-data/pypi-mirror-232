from constants import BaseEnum


class GoogleSheets(BaseEnum):

    DEFAULT_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
    READ_ONLY_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']