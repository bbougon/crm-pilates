# CRM Pilates

CRM Pilates is an application to manage Pilates classroom for small and medium Pilates offices.

## Development
CRM Pilates is made with `python 3.9.2`

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
   curl http://localhost:8000/classroom -X POST --data '{"name": "advanced class", "hour": "10:00"}' -H"Content-Type: application/json" -v | jq
   ```
   Expected result:
   ```bash
   {
     "name": "advanced class",
     "hour": "10:00",
     "id": "52329b48-726e-40ef-b780-58c93d467a41"
   }
   ```