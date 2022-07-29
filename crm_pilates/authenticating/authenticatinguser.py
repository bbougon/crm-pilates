from dataclasses import dataclass


@dataclass
class AuthenticatingUser:
    username: str
    password: str
