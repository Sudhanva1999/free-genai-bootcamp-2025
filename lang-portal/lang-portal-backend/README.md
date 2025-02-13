# lang-portal-backend

## Project Overview

The `lang-portal-backend` project is a Node.js and Express-based backend for a language learning portal. It serves as an API for managing vocabulary words, study sessions, and user progress in language learning activities.

## Directory Structure

The project follows a structured directory layout:

```
lang-portal-backend
├── src
│   ├── controllers          # Contains controller files for handling requests
│   ├── routes               # Contains route definitions for the API
│   ├── models               # Contains database models
│   ├── migrations           # Contains SQL migration files
│   ├── seeds                # Contains seed data for populating the database
│   ├── app.js               # Entry point of the application
│   └── database.js          # Database connection and setup
├── package.json             # Project dependencies and scripts
├── .env                     # Environment variables
└── README.md                # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd lang-portal-backend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your database connection settings.

4. **Initialize the Database**
   Run the following command to initialize the SQLite database:
   ```bash
   npm run init-db
   ```

5. **Run Migrations**
   Execute the migrations to set up the database schema:
   ```bash
   npm run migrate
   ```

6. **Seed the Database**
   Populate the database with initial data:
   ```bash
   npm run seed
   ```

7. **Start the Server**
   Launch the application:
   ```bash
   npm start
   ```

## API Usage

The backend provides various API endpoints for managing vocabulary words, study sessions, and user progress. Below are some key endpoints:

- **Dashboard**
  - `GET /api/dashboard/last_study_session`: Retrieve the most recent study session.
  - `GET /api/dashboard/study_progress`: Get study progress statistics.

- **Study Activities**
  - `GET /api/study_activities/:id`: Fetch details of a specific study activity.
  - `POST /api/study_activities`: Create a new study activity.

- **Words**
  - `GET /api/words`: Retrieve a list of vocabulary words.
  - `GET /api/words/:id`: Get details of a specific word.

- **Groups**
  - `GET /api/groups`: Retrieve a list of groups.
  - `GET /api/groups/:id`: Get details of a specific group.

- **Study Sessions**
  - `GET /api/study_sessions`: Retrieve a list of study sessions.
  - `GET /api/study_sessions/:id`: Get details of a specific study session.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.