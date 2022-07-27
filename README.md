# CRM Pilates

CRM Pilates is an application to manage Pilates classroom for small and medium Pilates offices.

## Development
### Prerequisites

- CRM Pilates is made over `python 3.9.9`
- You need to install postgres and libpq in order to run tests and run the app locally

[Documentation](https://miro.com/app/board/o9J_leSmQNU=/)

Everything is in the Makefile

### ADR

Nat Pryce [ADR tools](https://github.com/npryce/adr-tools)

ADR index is kept [here](./adr/README.md)

### Installation
  
  `make install` will install the virtual env, all needed dependencies, setup your local environment and setup local sqlite database

### Tests

1. in tests folder run `docker-compose up` in order to boot a postgres database for tests
1. `make test` will run all the tests (you can specify `args="--db-type sqlite"` or `args="--db-type postgres"` to run tests under sqlite (by default) or postgres)
1. `make coverage` will run coverage

**NB:**

Postgres event store test use the postgres test connection

### Run the API

#### Locally
  `make run` will run the application with all the modules

#### Docker
There is a `Dockerfile` within root directory. It builds the api then creates an image.

There is also a `docker-compose.yml` file

- `docker-compose --env-file .env.local up` will:
    1. boot a postgres database container named `crm-pilates-postgres` (login: `crm-pilates`, password: `example`)
    2. boot an adminer container
    3. boot the `crm-pilates-api` and load the events persisted in database 

### API

The API documentation is available in 3 formats:
- [openapi](http://localhost:8081/openapi.json)
- [swagger](http://localhost:8081/docs)
- [redoc](http://localhost:8081/redoc)

##### Create a classroom
1. Run the API (see above section)
2. Use the `curl` command line as below
   ```bash
   curl http://localhost:8081/classrooms -X POST --data '{"name": "advanced class", "start_date": "2021-05-10T10:00", "position": 3, "duration": {"duration": 50, "unit": "MINUTE"}}' -H"Content-Type: application/json" -v | jq
   ```
   Expected result:
   ```bash
    {
      "name": "advanced class",
      "id": "33da6f12-efda-4c16-b8af-e5e822fc5459",
      "position": 3,
      "start_date": "2021-05-10T10:00:00",
      "stop_date": null,
      "duration": {
        "duration": 50,
        "unit": "MINUTE"
      }
    }
   ```

##### Create a client
1. Run the API (see above section)
2. Use the `curl` command line as below
   ```bash
   curl http://localhost:8081/clients -X POST --data '{"firstname": "John", "lastname": "Doe"}' -H"Content-Type: application/json" -v | jq
   ```
   Expected result:
   ```bash
    {
      "firstname": "John",
      "lastname": "Doe",
      "id": "33da6f12-efda-4c16-b8af-e5e822fc5459",
    }
   ```

#### Add attendees to a classroom
1. Run the API (see above section)
1. Create a classroom (see above section)
1. Use the `curl` command line as below
   ```bash
   curl http://localhost:8081/classrooms/{id} -X PATCH --data '{"attendees": [{"id": "A_CLIENT_ID"}]}' -H"Content-Type: application/json" -v
   ```
   Expected result:
   ```bash
    HTTP/1.1 204 No Content
   ```

#### Checkin
1. Run the API (see above section)
1. Add attendees to a classroom (see above section)
1. Use the `curl` command line as below
   ```bash
   curl http://localhost:8081/sessions/checkin -X POST --data '{"classroom_id": "CLASSROOM_ID", "session_date": "SESSION_DATE", "attendee": "ATTENDEE_ID"}' -H"Content-Type: application/json" -v | jq
   ```
