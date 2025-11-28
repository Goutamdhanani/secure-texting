<div align="center">

# 🔐 Secure Texting API

### End-to-End Encrypted Messaging Backend

[![Python](https://img. shields.io/badge/Python-3. 11-3776AB? style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0. 100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi. tiangolo.com/)
[![Docker](https://img. shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
[![License](https://img. shields.io/badge/License-MIT-green? style=for-the-badge)](LICENSE)

<p align="center">
  <strong>A high-performance, secure REST API for encrypted messaging with real-time capabilities</strong>
</p>

[Features](#-features) • [API Docs](#-api-documentation) • [Installation](#-installation) • [Deployment](#-deployment) • [Architecture](#-architecture)

---

</div>

## ✨ Features

<table>
<tr>
<td>

### 🔒 Military-Grade Security
- **AES-256 Encryption** - Messages encrypted at rest
- **Fernet Symmetric Encryption** - Industry-standard cryptography
- **No Plaintext Storage** - Only encrypted data in database

</td>
<td>

### ⚡ High Performance
- **FastAPI Framework** - One of the fastest Python frameworks
- **Async Support** - Non-blocking I/O operations
- **SQLite/PostgreSQL** - Flexible database options

</td>
</tr>
<tr>
<td>

### 📊 Monitoring & Metrics
- **Prometheus Integration** - Real-time metrics
- **Health Endpoints** - Service monitoring
- **Request Logging** - Debug and audit trails

</td>
<td>

### 🐳 Cloud Ready
- **Docker Support** - Containerized deployment
- **Kubernetes Configs** - K8s manifests included
- **CI/CD Ready** - GitHub Actions workflows

</td>
</tr>
</table>

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 👤 Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/` | List all users |
| `GET` | `/users/{id}` | Get user by ID |

#### 💬 Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/messages/` | Send encrypted message |
| `GET` | `/conversations/{user_a}/{user_b}` | Get conversation between users |
| `GET` | `/conversations/user/{user_id}` | Get contact summaries for user |
| `POST` | `/conversations/{user_id}/{contact_id}/read` | Mark conversation as read |

#### 🏥 Health & Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |

### Example Requests

<details>
<summary><b>Create User</b></summary>

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

**Response:**
```json
{
  "id": 1,
  "name": "Alice"
}
```
</details>

<details>
<summary><b>Send Message</b></summary>

```bash
curl -X POST "http://localhost:8000/messages/" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": 1,
    "recipient_id": 2,
    "message": "Hello, this is a secret message!"
  }'
```

**Response:**
```json
{
  "id": 1,
  "sender_id": 1,
  "recipient_id": 2,
  "ciphertext": "gAAAAABl.. .",
  "nonce": "abc123.. .",
  "timestamp": "2024-01-15T10:30:00Z"
}
```
</details>

<details>
<summary><b>Get Conversation</b></summary>

```bash
curl "http://localhost:8000/conversations/1/2"
```

**Response:**
```json
[
  {
    "id": 1,
    "sender_id": 1,
    "recipient_id": 2,
    "decrypted": "Hello, this is a secret message!",
    "timestamp": "2024-01-15T10:30:00Z",
    "read": false
  }
]
```
</details>

---

## 🚀 Installation

### Prerequisites

- **Python** 3.11+
- **pip** or **pipenv**
- **Docker** (optional)

### Local Development

```bash
# Clone the repository
git clone https://github.com/Goutamdhanani/secure-texting.git
cd secure-texting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export ENCRYPTION_KEY="your-32-byte-base64-key"
export TESTMAIL_KEY="your-testmail-api-key"
export TESTMAIL_NAMESPACE="your-namespace"
export ALERT_EMAIL="your-email@example. com"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t secure-texting .
docker run -p 8000:8000 secure-texting
```

---

## 🐳 Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - DATABASE_URL=sqlite:///./data/messages.db
    volumes:
      - ./data:/src/data
    restart: unless-stopped
```

### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENCRYPTION_KEY` | 32-byte base64 encryption key | Auto-generated |
| `DATABASE_URL` | Database connection string | `sqlite:///./messages.db` |
| `TESTMAIL_KEY` | TestMail. app API key | - |
| `TESTMAIL_NAMESPACE` | TestMail.app namespace | - |
| `ALERT_EMAIL` | Email for notifications | - |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (React UI)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX (Reverse Proxy)                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   main.py   │  │   crud.py   │  │  crypto.py  │              │
│  │  (Routes)   │  │   (CRUD)    │  │ (Encryption)│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  models.py  │  │ schemas.py  │  │ metrics.py  │              │
│  │ (DB Models) │  │ (Pydantic)  │  │(Prometheus) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite / PostgreSQL                           │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │       Users         │  │      Messages       │               │
│  │  - id               │  │  - id               │               │
│  │  - name             │  │  - sender_id        │               │
│  │                     │  │  - recipient_id     │               │
│  │                     │  │  - ciphertext       │               │
│  │                     │  │  - nonce            │               │
│  │                     │  │  - timestamp        │               │
│  └─────────────────────┘  └─────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
secure-texting/
├── 📂 app/
│   ├── 📄 __init__.py       # Package init
│   ├── 📄 main.py           # FastAPI app & routes
│   ├── 📄 crud.py           # Database operations
│   ├── 📄 models.py         # SQLAlchemy models
│   ├── 📄 schemas.py        # Pydantic schemas
│   ├── 📄 crypto.py         # Encryption utilities
│   ├── 📄 db. py             # Database connection
│   └── 📄 metrics.py        # Prometheus metrics
├── 📂 k8s/                  # Kubernetes manifests
├── 📂 data/                 # Database files
├── 📂 static/               # Static files
├── 📄 Dockerfile            # Docker image
├── 📄 docker-compose.yml    # Docker Compose config
├── 📄 requirements.txt      # Python dependencies
├── 📄 nginx.conf            # Nginx configuration
├── 📄 prometheus.yml        # Prometheus config
└── 📄 README.md
```

---

## 🔐 Security

### Encryption Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Plaintext  │ ──▶ │   Encrypt    │ ──▶ │  Ciphertext  │
│   Message    │     │  (Fernet)    │     │   + Nonce    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Database   │
                     │  (Encrypted) │
                     └──────────────┘
```

### Security Features

- 🔒 **Fernet Encryption** - Symmetric encryption using AES-128-CBC
- 🔑 **Unique Keys** - Each deployment generates unique encryption keys
- 📧 **Email Alerts** - Notifications for specific users (configurable)
- 🚫 **No Plaintext** - Messages are never stored in plaintext

---

## 📊 Monitoring

### Prometheus Metrics

Access metrics at `/metrics`:

```
# HELP messages_sent_total Total messages sent
# TYPE messages_sent_total counter
messages_sent_total 1234

# HELP active_users Current active users
# TYPE active_users gauge
active_users 42
```

### Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [text-ui](https://github. com/Aaryanrao0001/text-ui) | React Frontend for CyberChat |

---

## 🤝 Contributing

1. **Fork** the repository
2.  **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 

---

## 👨‍💻 Authors

<div align="center">

**Goutam Dhanani** | **Aaryan Rao**

[![GitHub](https://img. shields.io/badge/-Goutamdhanani-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Goutamdhanani)
[![GitHub](https://img. shields.io/badge/-Aaryanrao0001-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Aaryanrao0001)

</div>

---

<div align="center">

### ⭐ Star this repo if you find it helpful! 

<p>Made with ❤️ and lots of ☕</p>

**[Backend](https://github.com/Goutamdhanani/secure-texting)** · **[Frontend](https://github.com/Aaryanrao0001/text-ui)**

</div>
