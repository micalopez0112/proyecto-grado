## Getting Started

To run this application, make sure you have the following dependencies installed:

- [Neo4j](https://neo4j.com/download/)
- [Python](https://www.python.org/downloads/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)

## Step 1: Install Dependencies

### Neo4j

1. Download and install Neo4j: [https://neo4j.com/download/](https://neo4j.com/download/)
2. Follow the installation instructions for your operating system.

### Python & FastAPI

1. Install Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Install FastAPI using pip:

```shell
$ pip install fastapi
```

### React

Install Node.js: https://nodejs.org/en/download/

Install React using npm:

```shell
$ npm install react
```

### Step 2: Create a .env File

Create a file named .env in backend/app of your project and add the following variables:

# Neo4j settings

```shell
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
```

Replace the empty values with your actual Neo4j credentials.

## Step 3: Run the Application

### Frontend (React)

```shell
$ cd frontend
$ npm install
$ npm start
```

### Backend (FastAPI)

```shell
$ cd backend
$ pip install -r requirements.txt
$ cd app
$ fastapi dev main.py
```

Open your browser and navigate to http://localhost:3000 to access the React frontend.

Use tools like curl, Postman, or any REST client to interact with the FastAPI backend at http://localhost:8000.
