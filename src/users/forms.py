from fastapi.param_functions import Form


class PhoneAuthForm:
    """Form for authorization by phone number.
    """
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: int = Form(
            title='Phone number',
            description='The phone number is used for registration.',
            ge=7_900_000_0000,
            le=7_999_999_9999,
        ),
        password: str = Form(
            title='Password for authorization',
            min_length=8,
            max_length=64,
        ),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
