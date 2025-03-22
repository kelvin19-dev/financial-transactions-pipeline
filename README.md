# Financial Transaction Data Pipeline & API

A simple yet robust data pipeline that ingests simulated financial transaction data from a simulated sftp server, processes it, stores it in a DuckDB database, and exposes an API to query the data with date filtering and pagination. This project is ideal for learning how to build a modular data processing system and API service using Python, FastAPI, DuckDB, and other modern libraries.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Pipeline](#running-the-pipeline)
  - [Starting the API Server](#starting-the-api-server)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## Overview

This project simulates a real-world data pipeline and API system for financial transaction processing. It covers:
- **Data Generation:** Create simulated transaction data in both CSV and JSON formats.
- **SFTP File Retrieval:** A simulated SFTP client downloads files from a designated directory.
- **Data Processing:** Read, validate, and clean data using Polars and Pydantic.
- **Database Storage:** Store processed data into a DuckDB database with efficient indexing.
- **API Service:** Expose a RESTful API using FastAPI with endpoints for querying transactions with filtering and pagination.
- **Testing:** Automated tests using pytest ensure the correctness of each component.

---

## Features

- **Modular Design:** Each component of the pipeline is separated into individual modules.
- **Data Validation:** Uses Pydantic v2 models for ensuring data quality.
- **Efficient Data Processing:** Leverages Polars for high-performance data transformations.
- **Local Analytics:** DuckDB provides lightweight, fast SQL-based analytics.
- **API Security:** Implements simple API key authentication and basic rate limiting.
- **Pagination:** Cursor-based pagination for efficient data retrieval.
- **Date Filtering:** Filter transactions by date range.

---

## Project Structure

```
credable-technical-assement/
├── data/                     # Storage for generated and processed data files
├── src/
│   ├── data_generator.py     # Script to generate sample data (CSV & JSON)
│   ├── sftp_client.py        # SFTP client simulation for file retrieval
│   ├── data_processor.py     # Data cleaning and transformation logic
│   ├── db.py                 # DuckDB database connection and operations
│   ├── models.py             # Pydantic models for data validation
│   ├── api.py                # FastAPI application with endpoints
│   └── main.py               # Pipeline runner to orchestrate data processing
├── requirements.txt          # List of project dependencies
└── README.md                 # Project documentation (this file)
```

---

## Installation

1. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   ```

2. **Install Dependencies:**

   ```bash
   pip install duckdb fastapi uvicorn polars pandas
   ```

3. **Set Up Environment Variables (Optional):**

   The default API key is "test-api-key". To use a custom key:
   ```bash
   # On Windows
   set API_KEY=your-api-key
   ```

---

## Usage

### Running the Pipeline

To generate sample data, simulate SFTP file downloads, process the data, and store it in DuckDB, run:

```bash
python -m src.main
```

### Starting the API Server

After the pipeline has stored the data, start the FastAPI server with:

```bash
python -m uvicorn src.api:app --reload
```

- **Access the API documentation** at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## API Endpoints

### GET `/health`
- **Description:** Health check endpoint.
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-03-22T06:33:23.060746"
  }
  ```

### GET `/test_db`
- **Description:** Test database connection and get total record count.
- **Response:**
  ```json
  {
    "message": "Database connection is active",
    "total_records": 500
  }
  ```

### GET `/transactions`
- **Description:** Retrieve a paginated list of transactions.
- **Query Parameters:**
  - `api_key`: (required) Your API key (default: "test-api-key").
  - `start_date`: (optional) Filter transactions from this date (YYYY-MM-DD).
  - `end_date`: (optional) Filter transactions until this date (YYYY-MM-DD).
  - `cursor`: (optional) Cursor for pagination.
  - `limit`: (optional) Number of transactions per page (default: 100, min: 1, max: 1000).
- **Response Example:**
  ```json
  {
    "data": [
      {
        "transaction_id": "uuid-string",
        "amount": 793.47,
        "currency": "KES",
        "transaction_type": "PAYMENT",
        "status": "FAILED",
        "date": "2025-03-22",
        "customer_id": "CUST-3327",
        "customer_name": "Customer 97",
        "customer_email": "customer29@example.com",
        "ip_address": "192.168.0.197",
        "device": "mobile",
        "location": "Nairobi"
      }
    ],
    "next_cursor": "next-transaction-id",
    "prev_cursor": "prev-transaction-id",
    "total": 500
  }
  ```

---

## Troubleshooting

- **Module Not Found Errors:**
  Make sure to run the commands from the project root directory.

- **Database Issues:**
  If you encounter database errors, try:
  ```bash
  # Delete the existing database
  Remove-Item -Path "data/transactions.duckdb" -Force
  # Run the pipeline again
  python -m src.main
  ```

- **API Key Authentication Fails:**
  The default API key is "test-api-key". Make sure to include it in your requests:
  ```bash
  http://localhost:8000/transactions?api_key=test-api-key
  ```

- **Port Conflicts:**
  If port 8000 is in use, change the port:
  ```bash
  python -m uvicorn src.api:app --reload --port 8001
  ```

---

## Future Enhancements

- **Advanced Rate Limiting:** Use Redis for distributed rate limiting.
- **OAuth2 or JWT Authentication:** Secure API access.
- **Integration with Real SFTP Servers:** Enhance real-world use cases.
- **Monitoring & Logging:** Add observability tools.
- **Data Archival:** Implement data retention policies.
- **Advanced Filtering:** Add more query parameters (e.g., by transaction type, status).
- **Bulk Operations:** Add endpoints for batch processing.
