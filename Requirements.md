This document objective is to scope the project and have a direction before writing code.


## Functional Requirements

- Fetch Dam data from SINA Public API
- Parse Dam Data JSON response to a Data Model
- Store the data in a local database
- Extract data from 4/5 years, from Valle de Bravo for now.
- Use TensorFlow to create a prediction Model

## Non Functional

- Use **Requests** library for API fetching.
- Do batch requests, so we don't saturate the server.
- Use CSV to store locally. We just need to do this once and won't be modifying later. 