import json
from fastapi import HTTPException

class CustomHTTPException(HTTPException):
    def __init__(self, status_code, detail=None, headers=None):
        super().__init__(status_code, detail, headers)

    def __str__(self):
        return json.dumps(self.detail)

