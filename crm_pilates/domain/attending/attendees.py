from __future__ import annotations

from typing import List
from uuid import UUID

from crm_pilates.domain.exceptions import AggregateNotFoundException, DomainException
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


class Attendees:
    @classmethod
    def by_ids(cls, attendees: List[UUID]) -> List[Attendee]:
        try:
            return list(
                map(
                    lambda id: RepositoryProvider.write_repositories.attendee.get_by_id(
                        id
                    ),
                    attendees,
                )
            )
        except AggregateNotFoundException as e:
            raise DomainException(
                f"One of the attendees with id '{e.unknown_id}' has not been found"
            )
