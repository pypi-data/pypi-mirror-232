from typing import Optional


class ApiException(Exception):
    def __init__(self, code: int, status_text: str, message: Optional[str] = None):
        self.code = code
        self.status_text = status_text
        self.message = message or status_text

        super().__init__(f"Status {self.code} {self.status_text}: {self.message}")

    def compose(self):
        return ({"Status": f"{self.code} {self.status_text}"}, self.message)
