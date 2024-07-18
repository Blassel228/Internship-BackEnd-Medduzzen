Internship Backend Project
This is a FastAPI-based backend project for an internship. The project includes endpoints for health checks and database connectivity checks. It uses PostgreSQL as the database and Redis for caching. The project is containerized using Docker and Docker Compose.

Features
Health Checks: Endpoints to monitor the status of the server and database connections.
Database Connectivity: Checks PostgreSQL connection.
Caching: Integrates Redis for efficient data caching.
Docker Containerization: Simplifies deployment and environment consistency.

Clone the repository:
git clone https://github.com/Blassel228/Internship-BackEnd-Medduzzen

Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the dependencies:
pip install -r requirements.txt

Running the Project
Ensure PostgreSQL and Redis are running in docker.
Start the FastAPI server:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Running Using Docker
Build and start the Docker containers:
docker-compose up --build
The FastAPI server will be available at http://localhost:8000.

Endpoints:
GET /: Root endpoint to check if the server is running.
GET /db_check/redis_check: Endpoint to check Redis connection.
GET /db_check/postgres_check: Endpoint to check PostgreSQL connection.