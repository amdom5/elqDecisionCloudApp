## Eloqua AppCloud Decision Service Integration with FastAPI

This FastAPI application demonstrates integration with the Eloqua AppCloud Decision Service, focusing on OAuth2 authentication and processing contacts based on country rules from a PostgreSQL database.

### Application Overview

The application receives contact information from Eloqua, evaluates each contact based on their Country field by looking up the country value in a database table, and processes the contact with an of "Yes" or "No" depending on whether a specific rule corresponds to that country.

### Features

- OAuth2 authentication with Eloqua.
- Decision service endpoint to process contacts.
- PostgreSQL database integration for country rules lookup.
- Modular design for easy maintenance and scalability.

### Project Structure

- eloqua_oauth_fastapi.py: Handles OAuth2 authentication flow with Eloqua.
- models.py: Defines SQLAlchemy models for database interactions.
- database.py: Configures the database connection and session management.
- crud.py: Contains CRUD operations for database interaction.
- schemas.py: Pydantic models for request and response validation.
- app.py: The core FastAPI application file with the decision service endpoint.

### Installation

Clone the repository:

```
git clone <repository-url>
```

Install the required dependencies:

```
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

Ensure PostgreSQL is running and the database is configured according to the provided schema.

### Running the Application

Start the FastAPI application using Uvicorn:

```
uvicorn app:app --reload
```

This command starts the application on http://localhost:8000. The --reload flag enables auto-reload during development.

### Usage

- OAuth2 Authentication: Follow the OAuth2 flow to authenticate with Eloqua and access the decision service endpoint.
- Decision Service Endpoint: Send a POST request to /decision/ with the contact's information in the request body. The application will return the Sync Action based on the country rule.
