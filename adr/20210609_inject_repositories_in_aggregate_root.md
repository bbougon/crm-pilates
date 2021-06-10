# 1. Inject repositories in aggregate root

Date: 2021-06-08

## Status

Rejected

## Context

Sometimes the creation of a Domain Object (AggregateRoot) may produce an event (e.g, a classroom creation produces the following event `ClassroomCreated`).
In case this Domain Object needs to be persisted, we need to inject the repository to the Domain Object.  

## Decision

Inject the repository into a Domain Object is not such a good idea when the purpose is to generate an event (with the idea of this event is sent to a queue and wil be cosumed).

We should use a pattern luke the Command pattern that wil be responsible to return a result that might be an event.

## Consequences

The Domain Object will have the responsabilities to perform any persisting action