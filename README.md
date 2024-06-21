# Personal Assistant App

The code for the personal assistant application, developed by Team 8 as part of the Python web course at GoIT

## Getting Started

### Prerequisites

- **Docker and Docker Compose:** Ensure you have Docker and Docker Compose installed on your system to handle the application and database containers.
- **Python:** Ensure Python 3.10 or higher is installed on your system.
- **Poetry:** This project uses Poetry for dependency management.

### Installation

- **Clone the repository:**
```bash
git clone https://github.com/alex-nuclearboy/goit-py-web-project-team-8.git
```

- **Navigate to the project directory:**
```bash
cd goit-py-web-project-team-8
```

- **To set up the environment** use the following commands depending on your operating system:
   - Unix/Linux/macOS:
   ```bash
   cp .env.example .env
   ```
   - Windows:
   ```powershell
   copy .env.example .env
   ```

**NOTE:** Adjust `.env` file with your settings

- **Activate the Poetry environment and install dependencies:**
```bash
poetry shell
poetry install --no-root
```

- **Start the PostgreSQL server:**
```bash
docker compose up -d
```

- **Navigate further into the Django project directory:**
```bash
cd personal_assistant/
```

- **Perform database migrations and data transfers:**
```bash
python manage.py migrate
```

- **Create a superuser to manage the app as an administrator:**
```bash
python manage.py createsuperuser
```

- **Start the Django development server**:
```bash
python manage.py runserver
```

### Accessing the Application

After starting the server, open a web browser and visit the following URL to access the application:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
