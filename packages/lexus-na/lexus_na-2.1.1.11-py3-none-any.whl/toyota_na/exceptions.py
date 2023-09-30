class AuthError(Exception):
    pass


class NotLoggedIn(AuthError):
    pass


class TokenExpired(AuthError):
    pass


class LoginError(AuthError):
    pass


class OtpRequired(AuthError):
    def __init__(self, auth_data):
        self.auth_data = auth_data
