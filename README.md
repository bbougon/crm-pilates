# CRM Pilates

CRM Pilates is an application to manage Pilates classroom for small and medium Pilates offices.

## Development
CRM Pilates is made with `python 3.9.2`

[Documentation](https://miro.com/app/board/o9J_leSmQNU=/)

Everything is in the Makefile

- Installation
  
  `make requirements` will install the virtual env and all dependencies needed
- Test

  `make tests` will run all the tests
- Run the API

  `make run-all` will run the application with all the modules

#### API

##### Create a classroom
1. Run the API (see above section)
2. Use the `curl` command line as below
   ```bash
   curl http://localhost:8000/classrooms -X POST --data '{"name": "advanced class", "schedule": "10:00", "start_date": "2021-05-10", "duration": {"duration": 50, "unit": "MINUTE"}}' -H"Content-Type: application/json" -v | jq
   ```
   Expected result:
   ```bash
    {
        "name": "advanced class",
        "schedule": "10:00:00",
        "id": "19ac6a81-9eca-4137-9c47-c40e0e49f03c",
        "start_date": "2021-05-10",
        "duration": {
          "duration": 50,
          "unit": "MINUTE"
          }
    }
   ```