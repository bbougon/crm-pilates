# CRM Pilates

CRM Pilates is an application to manage Pilates classroom for small and medium Pilates offices.

## Development
CRM Pilates is made with `python 3.9.2`

[Documentation](https://miro.com/app/board/o9J_leSmQNU=/)

Everything is in the Makefile

- Installation
  
  `make requirements` will install the virtual env and all dependencies needed
- Test

  `make test` will run all the tests
- Run the API

  `make run-all` will run the application with all the modules

#### ADR

Nat Pryce [ADR tools](https://github.com/npryce/adr-tools) 

ADR index is kept [here](./adr/README.md)

#### API

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
   curl http://localhost:8081/classrooms -X PATCH --data '{"attendees": [{"client_id": "A_CLIENT_ID"}]}' -H"Content-Type: application/json" -v
   ```
   Expected result:
   ```bash
    HTTP/1.1 204 No Content
   ```