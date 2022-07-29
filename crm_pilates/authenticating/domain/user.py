from crm_pilates.domain.repository import AggregateRoot


class User(AggregateRoot):

    def __init__(self, username: str, password: str):
        super().__init__()
        self._username = username
        self._password = password

    @property
    def password(self):
        return self._password

    @property
    def username(self):
        return self._username
