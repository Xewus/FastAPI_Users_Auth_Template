from fastapi.param_functions import Form

from src.core.exceptions import InvalidLoginDataException


class PhoneAuthForm:
    """Form for authorization by phone number.
    """
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ):
        self.__set_phone(username)
        self.grant_type = grant_type
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

    def __set_phone(self, phone: str):
        """Checking the entered phone number.

        #### Args:
          - phone (str):
            Entered phone number.

        #### Raises:
          - InvalidLoginDataException:
            Invalid phone number.
        """
        if phone.isdigit():
            phone = int(phone)
            if 7_900_000_0000 <= phone <= 7_999_999_9999:
                self.username = phone
                return
        raise InvalidLoginDataException('Invalid phone number')
