from typing import List
from uuid import UUID

from crm_pilates.domain.client.client import Credits
from crm_pilates.event.event_store import EventSourced, Event


@EventSourced
class ClientCreditsUpdated(Event):
    def __init__(self, root_id: UUID, credits: List[Credits]) -> None:
        self.credits = credits
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "credits": list(
                map(
                    lambda credit: {
                        "value": credit.value,
                        "subject": credit.subject.value,
                    },
                    self.credits,
                )
            ),
        }
