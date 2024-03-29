# CRM Pilates

CRM Pilates is an application to manage Pilates classroom for small and medium Pilates offices.

## Development
### Prerequisites

- CRM Pilates is made over `python 3.9.9`
- You need to install poetry
- You need to install postgres and libpq in order to run tests and run the app locally
- You will need a private key to encrypt / decrypt user password (default is provided for tests purpose only), to generate one, just run:
  `openssl rand -hex 32` and keep this key in a safe place (provide the value to the environment key `SECRET_KEY`)

**Documentation:**
- [New domain exploration](https://miro.com/app/board/uXjVOxwEdAo=/)
- [Old domain exploration](https://miro.com/app/board/o9J_leSmQNU=/)

Everything is in the Makefile

### Create a user
Run a python interpreter in your shell once everything is installed and run the following
```shell
>>> from passlib.context import CryptContext
>>> pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
>>> pwd_context.hash('password')
'$2b$12$t.OhZvTO6xAFtUrqdrxkgO9z23VlK0wzkMKg4fESjll6CwayKswXu'
```

And then execute the following SQL request on your database
```sql
INSERT INTO users VALUES (1, 'bertrand', '$2b$12$t.OhZvTO6xAFtUrqdrxkgO9z23VlK0wzkMKg4fESjll6CwayKswXu')
```

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

- Postgres event store test use the postgres test connection (that means you need a postgres installed locally to run the tests)

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

Resources are authenticated by a JWT with header `Authorization: Bearer TOKEN_VALUE`.
To retrieve a token, you need to authenticate on `/token` (see below)

#### Authentication
1. Run the API (see above section)
2. Insert a user in user table (encrypt your password with the key provided in docker-compose :warning: for local installation purpose only!)
3. Use the `curl` command line as below
   ```bash
   curl -X POST http://localhost:8081/token -d 'username=[USERNAME]&password=[PASSWORD]' -H 'Content-Type: application/x-www-form-urlencoded' -v | jq
   ```
   Expected result:
   ```bash
    {
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZXJ0cmFuZCIsImV4cCI6MTY2MTM2NjQ3Mn0.VM37LH4JR0AHn_sn1iGBADhpDh9SoOM9wDc4oDdzmYo",
       "type": "bearer"
    }
   ```
4. The token is valid during 30 minutes


##### Create a classroom
1. Run the API (see above section)
2. Use the `curl` command line as below
   ```bash
   curl http://localhost:8081/classrooms -X POST --data '{"name": "advanced class", "start_date": "2021-05-10T10:00", "position": 3, "duration": {"duration": 50, "unit": "MINUTE"}, "subject": "MAT"}' -H "Content-Type: application/json" -H "Authorization: Bearer [TOKEN_VALUE]" -v | jq
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
   curl http://localhost:8081/clients -X POST --data '{"firstname": "John", "lastname": "Doe"}' -H "Content-Type: application/json" -H "Authorization: Bearer [TOKEN_VALUE]" -v | jq
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
   curl http://localhost:8081/classrooms/{id} -X PATCH --data '{"attendees": [{"id": "A_CLIENT_ID"}]}' -H "Content-Type: application/json" -H "Authorization: Bearer [TOKEN_VALUE]" -v
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
   curl http://localhost:8081/sessions/checkin -X POST --data '{"classroom_id": "CLASSROOM_ID", "session_date": "SESSION_DATE", "attendee": "ATTENDEE_ID"}' -H"Content-Type: application/json" -H "Authorization: Bearer [TOKEN_VALUE]" -v | jq
   ```
