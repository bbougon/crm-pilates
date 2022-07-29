# 1. Inject repositories in aggregate root

Date: 2021-06-30

## Status

Accepted

## Context

The application processes many events issued from a user or from the domain. It seems accurate to have an event sourced
architecture.

## Decision

use an event sourced architecture to ease any events send to the application. The idea is to persist all the events to
be able to retrieve the application state and deal with each event on its Bounded Context. Therefore to have an event
sourced architecture, we will use the command pattern which will be responsible to produce the events to be stored

## Consequences

The command handlers will have the responsability to handle every events sent / produced on the application and call the
domain. The command handlers will persist the necessary events
