class CustomException(Exception):
    def __init__(self, *args, **kwargs):
        self.error_code = kwargs.get('error_code', None)
        self.payload = kwargs.get('payload', None)
        self.status_code = kwargs.get('status_code', 400)
