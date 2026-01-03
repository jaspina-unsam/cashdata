# 💰 CashData

**Personal finance management application for tracking credit card purchases and monthly statements.**

[![Tests](https://img.shields.io/badge/tests-475%20passing-brightgreen)](backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-%3E90%25-brightgreen)](backend/htmlcov/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19-blue)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🎯 Overview

CashData helps you manage credit card purchases with installment tracking and automatic monthly statement generation. Built with **Clean Architecture** principles for maintainability and scalability.

### Key Features ✨

- 🏦 **Credit Card Management**: Register cards with billing cycles
- 💳 **Purchase Tracking**: Record purchases with automatic installment generation
- 📊 **Monthly Statements**: Auto-generated billing statements per card
- 🏷️ **Categorization**: Organize purchases with categories
- 📈 **Billing Summaries**: View period-based summaries with all installments
- 🧪 **Well Tested**: 475+ tests with >90% coverage

---

## 🏗️ Architecture

### Clean Architecture (4 Layers)

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI)              │  ← HTTP endpoints
├─────────────────────────────────────┤
│     Application Layer                │  ← Use cases, DTOs
├─────────────────────────────────────┤
│     Infrastructure Layer             │  ← Database, External services
├─────────────────────────────────────┤
│     Domain Layer                     │  ← Business logic (pure)
└─────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- Python 3.13
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- pytest (testing)
- Poetry (dependency management)

**Frontend:**
- React 19
- TypeScript
- Vite (bundler)
- TailwindCSS (styling)
- TanStack Query (data fetching)
- Axios (HTTP client)

**Database:**
- SQLite (development)
- PostgreSQL-ready schema

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+ (LTS)
- Poetry (`pip install poetry`)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaspina-unsam/cashdata.git
   cd cashdata
   ```

2. **Backend setup**
   ```bash
   cd backend
   poetry install
   poetry run alembic upgrade head
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

**Option 1: Using helper scripts (from root)**
```bash
./start-backend.sh   # Starts backend on http://localhost:8000
./start-frontend.sh  # Starts frontend on http://localhost:5173
```

**Option 2: Manual start**
```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn cashdata.infrastructure.api.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## 🧪 Testing

```bash
cd backend

# Run all tests
poetry run pytest tests/ -v

# With coverage report
poetry run pytest tests/ --cov=cashdata --cov-report=html

# Run specific test file
poetry run pytest tests/domain/entities/test_purchase.py -v
```

**Current Status:** ✅ 475 tests passing, >90% coverage

---

## 📚 Documentation

Comprehensive documentation is available in the `.support/` directory:

- **[estado_proyecto.md](.support/estado_proyecto.md)**: Current project status (Spanish)
- **[handoff.yaml](.support/handoff.yaml)**: Complete technical documentation for AI agents
- **[unified_board.csv](.support/unified_board.csv)**: All user stories with current status
- **[backburner_stories.csv](.support/backburner_stories.csv)**: Future features backlog

### API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
GET  /health
GET  /api/v1/categories
POST /api/v1/categories
GET  /api/v1/credit-cards
POST /api/v1/credit-cards
GET  /api/v1/credit-cards/{id}/summary?billing_period=YYYYMM
GET  /api/v1/purchases
POST /api/v1/purchases
GET  /api/v1/statements
GET  /api/v1/statements/{id}
```

---

## 📁 Project Structure

```
cashdata/
├── backend/
│   ├── cashdata/
│   │   ├── domain/              # Business entities, VOs, services
│   │   ├── infrastructure/      # DB, repositories, API
│   │   └── application/         # Use cases, DTOs
│   ├── tests/                   # Unit & integration tests
│   ├── alembic/                 # Database migrations
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── application/         # Hooks, services
│   │   ├── domain/              # TypeScript types
│   │   ├── presentation/        # Components, pages
│   │   └── utils/
│   └── package.json
├── .support/                    # Documentation
│   ├── handoff.yaml
│   ├── estado_proyecto.md
│   └── unified_board.csv
└── README.md
```

---

## 🔍 Key Concepts

### Billing Period Calculation

Purchases are assigned to billing periods based on the card's close day:

```python
# Purchase on Aug 10, card closes on day 30
if purchase.day <= card.billing_close_day:  # 10 <= 30
    period = "202508"  # Current period
else:
    period = "202509"  # Next period
```

### Installment Generation

Purchases with multiple installments are automatically divided:

```python
# 10,000 ARS in 3 installments:
base = 10,000 // 3 = 3,333
remainder = 10,000 % 3 = 1

# Installment 1: 3,334 (base + remainder)
# Installment 2: 3,333
# Installment 3: 3,333
# Total: 10,000 ✅
```

### Automatic Statement Creation

Monthly statements are automatically created when purchases are made, ensuring all billing periods are tracked.

---

## 🎯 Roadmap

### ✅ MVP Complete (Current)
- Credit card management
- Purchase tracking with installments
- Monthly statements
- Category organization
- Comprehensive testing

### 🔜 Next Features
- [ ] Edit credit card information
- [ ] Edit/delete purchases
- [ ] User authentication
- [ ] Data export/import
- [ ] Advanced reporting

### 🚀 Future
- [ ] Multiple payment methods (cash, debit)
- [ ] Budget planning
- [ ] Multi-user support
- [ ] Mobile application
- [ ] Bank integration

---

## 🤝 Contributing

This is currently a personal project. If you find any issues or have suggestions, feel free to open an issue.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Javier Spina**

- GitHub: [@jaspina-unsam](https://github.com/jaspina-unsam)
- Repository: [cashdata](https://github.com/jaspina-unsam/cashdata)

---

## 📊 Project Board

Track project progress on [Notion Board](https://www.notion.so/640845aa22fa4727a079e357392e4325?v=7a42b60afd5e43018d1ea6a0f55aa875)

---

**Last Updated:** January 2, 2026  
**Status:** ✅ MVP Complete - Ready for production deployment