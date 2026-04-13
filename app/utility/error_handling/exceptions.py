class ServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class URLFetchError(ServiceError):
    def __init__(self, url: str, reason: str):
        super().__init__(
            message=f"Failed to fetch URL '{url}': {reason}", status_code=502
        )


class InvalidURLError(ServiceError):
    def __init__(self, url: str):
        super().__init__(message=f"Invalid URL: '{url}'", status_code=400)


class DuplicateURLError(ServiceError):
    def __init__(self, url: str):
        super().__init__(
            message=f"Metadata for URL '{url}' already exists", status_code=409
        )
