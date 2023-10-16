# Stock Buddy API

## Development Notes

### Getting Started

To start working with the Stock Buddy API, follow these steps:

1. Start PostgreSQL either as a service or container. If using Docker, run the following command:

```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword postgres
```

2. Install a recent Python version (3.9 or higher) and pip.

3. Install PostgreSQL development dependencies for binary support.

4. Install the project's Python dependencies using pip:
```python
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

5. Prepare your environment variables file based on the provided example.env file and load it.

6. (Destructive Action) Recreate the database schema:
```bash
python manage.py recreate_db
```

7. (Destructive Action) Perform the initial database migration:
```bash
python manage.py migrate
```

8. Start the Stock Buddy API by running the following command:
```bash
python manage.py runserver
```

Alternatively, you can start the Stock Buddy API using Docker Compose. Build and run it with the following command:
```bash
docker-compose build && docker-compose up
```

## Contributing
We welcome contributions to the Stock Buddy API project. If you'd like to contribute, please read our Contribution Guidelines to get started.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
