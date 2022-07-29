# 1. ES/CQRS architecture

Date: 2021-06-30

## Status

Proposed

## Context

The business is highly event as it is around the classroom activities of a Pilates teacher.

It handles classroom session, presence of the clients, checkin / checkouts and so on.

## Decision

Use an ES/CQRS architecture to stick to the teacher and clients actions.


## Consequences

- It will ease the design of the application and will be easy to identify what events are emit and what they do.
- It forces us to have 2 models, one for writing and one for reading
