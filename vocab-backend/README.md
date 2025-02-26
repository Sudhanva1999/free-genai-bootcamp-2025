# Word Groups API

A Flask-based backend application that provides word groups and their translations in Marathi. The application first checks a local SQLite database for words and falls back to an Amazon Bedrock LLM when needed.

## Features

- RESTful API for retrieving words by group ID or name
- SQLite database for persistent storage
- Integration with Amazon Bedrock for LLM-generated words
- Response validation to ensure consistent format
- Initial database seeding with common word categories

## Setup

### 1. Prerequisites

- Python 3.8+
- AWS account with Amazon Bedrock access
- AWS credentials configured locally

### 2. Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd word-groups-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following configuration:
   ```
   DATABASE_PATH=word_groups.db
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   DEBUG=False
   ```

### 3. Initialize the Database

Run the setup script to create and populate the database with initial data:

```
python setup.py
```

### 4. Run the Application

Start the Flask application:

```
python app.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Get Words by Group ID

```
GET /api/groups/words/{group_id}
```

- If words exist in the database for this group ID, they are returned
- If no words are found, the LLM generates new words, stores them, and returns them

### Get Words by Group Name

```
GET /api/groups/words/{group_name}
```

- Always calls the LLM to generate words for this group name
- Stores the generated words in the database
- Returns the generated words

## Response Format

All successful responses follow this format:

```json
{
  "group_name": "Basic Marathi Vocabulary",
  "words": [
    {
      "english": "water",
      "marathi": "पाणी"
    },
    {
      "english": "food",
      "marathi": "अन्न"
    }
  ]
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes and JSON error messages:

```json
{
  "error": "Error message"
}
```

## AWS Setup

Ensure that you have:

1. AWS CLI installed and configured with appropriate credentials
2. Access to Amazon Bedrock with the specified model
3. Proper IAM permissions to invoke Bedrock models