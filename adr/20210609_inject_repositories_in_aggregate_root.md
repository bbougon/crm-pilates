# 1. Inject repositories in aggregate root

Date: 2021-06-08

## Status

Proposed

## Context

Sometimes the creation of a Domain Object (AggregateRoot) may produce an event (e.g, a classroom creation produces the following event `ClassroomCreated`).
In case this Domain Object needs to be persisted, we need to inject the repository to the Domain Object.  

## Decision



## Consequences

The Domain Object will have the responsabilities to perform any persisting action