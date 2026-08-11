from __future__ import annotations


class FlyvbjergError(Exception):
    def __init__(self, code: str, message: str, hint: str | None = None, *, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.exit_code = exit_code


class NotFound(FlyvbjergError):
    def __init__(self, message: str, hint: str | None = None):
        super().__init__("NOT_FOUND", message, hint, exit_code=1)


class Conflict(FlyvbjergError):
    def __init__(self, message: str, hint: str | None = None):
        super().__init__("ALREADY_EXISTS", message, hint, exit_code=2)


class ValidationError(FlyvbjergError):
    def __init__(self, message: str, hint: str | None = None):
        super().__init__("VALIDATION_ERROR", message, hint, exit_code=1)

