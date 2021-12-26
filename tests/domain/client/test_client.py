import pytest

from domain.classroom.classroom_type import ClassroomSubject
from domain.client.client import Client
from domain.exceptions import DomainException


def test_cannot_refund_credits_when_none_available():
    with pytest.raises(DomainException) as e:
        client: Client = Client.create("Bertrand", "Bougon")
        client.refund_credits_for(ClassroomSubject.MAT)

    assert e.value.message == f"Credits for client with id '{str(client.id)}' cannot be refund as the client has no credits available."
