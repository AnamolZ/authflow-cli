# OAuth Finance: Production-Grade API and CLI

This project serves as a comprehensive example of a production-ready Python application. It integrates professional authentication standards with real-time data processing, managed through a modern dependency environment.

---

### Understanding the Architecture

The project has been reorganized from a collection of scripts into a formal Python package structure. This separation of concerns ensures that each part of the system can be developed, tested, and scaled independently.

#### Core Package (src/authflow_cli)
- **Configuration Layer**: Centrally managed via `core/config.py`. It utilizes Pydantic Settings to handle environment variables and system constants. This approach prevents hardcoding sensitive information and allows the application to adapt to different environments (development, staging, production) without code changes.
- **Authentication Service**: Located in `auth/service.py`, this module implements the OAuth2 Password Flow using JSON Web Tokens (JWT). It handles user validation, secure password comparison using bcrypt hashing, and the issuance of signed tokens.
- **Financial Services**: The `services/stock_service.py` module contains the business logic. It performs multi-threaded scraping of financial data. By using a thread pool, the system can fetch data for multiple stock symbols simultaneously, significantly reducing the total response time.
- **Interface Layer**: The project provides two main entry points:
  - A **FastAPI** web server (`main.py`) for programmatic access via HTTP.
  - A **CLI Tool** (`cli/finance_cli.py`) for direct terminal interaction.

---

### How the System Works

#### 1. The Authentication Lifecycle
The security model is built around standard Bearer Token authentication:
- **Request**: A user provides their credentials (username and password) to the `/token` endpoint. 
- **Verification**: The system hashes the incoming password and compares it against the secure hash stored in the data directory.
- **Issuance**: If valid, the system generates a JWT signed with a secret key and a set expiration time.
- **Authorization**: For subsequent requests, the client must include this token in the header. The system decodes and validates the signature of the token before allowing access to internal services.

#### 2. Real-Time Data Processing
When a request for stock data is made:
- The system initializes a `StockInfoFetcher`.
- It spawns a pool of worker threads. Each thread is responsible for navigating to a specific financial source, retrieving the raw HTML, and parsing out the market price.
- It includes logic to handle localization (such as removing commas from currency strings) to ensure the data is numerically accurate and ready for analysis.

---

### Operational Guide

#### Environment Setup
The project utilizes `uv` for environment management. This ensures that every developer or server running the code uses the exact same dependency versions, eliminating the "it works on my machine" problem.

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

#### Application Execution
**The API Server**
The server provides a RESTful interface and interactive documentation.
```bash
uv run uvicorn authflow_cli.main:app --reload
```
Once running, you can visit `http://127.0.0.1:8000/docs` to see the full API specification.

**The CLI Tool**
This tool demonstrates how to consume the internal services directly.
```bash
uv run python -m authflow_cli.cli.finance_cli
```
You will be prompted for an access token. You can generate one via Postman or the Swagger documentation mentioned above.

---

### Technical Security Details
- **Encryption**: Passwords are never stored in plain text. We use the bcrypt algorithm, which includes a unique salt for every user to prevent rainbow table attacks.
- **Token Integrity**: JWTs are signed with the HS256 algorithm. This ensure that a token cannot be modified by a user without invalidating the signature.
- **Scalability**: The `src` layout used here is the standard for professional Python development, making the project ready to be built into a distributable wheel or containerized for cloud deployment.
