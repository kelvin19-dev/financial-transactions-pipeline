# Financial Transaction Data Pipeline & API

A comprehensive data pipeline and API system for processing, storing, and querying financial transaction data. This system simulates a real-world ETL (Extract, Transform, Load) pipeline that ingests financial transaction data from an SFTP server, processes it using modern data engineering techniques, stores it in a columnar database, and exposes the data through a RESTful API with advanced features like pagination, filtering, and authentication.

![Project Architecture](https://via.placeholder.com/800x400?text=Financial+Transaction+Pipeline+Architecture)

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Pipeline](#running-the-pipeline)
  - [Starting the API Server](#starting-the-api-server)
  - [API Authentication](#api-authentication)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Pipeline Components](#pipeline-components)
  - [Data Generation](#data-generation)
  - [SFTP Integration](#sftp-integration)
  - [Data Processing](#data-processing)
  - [Database Operations](#database-operations)
- [Advanced Features](#advanced-features)
  - [Incremental Processing](#incremental-processing)
  - [File Management](#file-management)
  - [Deduplication](#deduplication)
- [Performance Considerations](#performance-considerations)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

---

## Overview

This project implements a complete data pipeline and API system for financial transaction data. It demonstrates best practices in data engineering, API development, and software architecture. The system is designed to be modular, scalable, and maintainable, with each component having a clear responsibility.

The pipeline simulates the entire lifecycle of financial transaction data:

1. **Data Generation:** Creates realistic financial transaction data in both CSV and JSON formats
2. **Data Extraction:** Retrieves files from a simulated SFTP server
3. **Data Transformation:** Processes, validates, and cleans the data
4. **Data Loading:** Stores the processed data in a DuckDB database
5. **Data Serving:** Exposes the data through a RESTful API

The system also includes advanced features like incremental processing, file archiving, deduplication, and efficient pagination to handle real-world scenarios such as repeated pipeline runs and large datasets.

---

## System Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Data Sources   │────▶│  Data Pipeline  │────▶│    Database     │────▶│   API Service   │
│  (SFTP Server)  │     │                 │     │    (DuckDB)     │     │   (FastAPI)     │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

- **Data Sources:** Simulated SFTP server containing CSV and JSON files
- **Data Pipeline:** Python-based ETL process with validation and transformation
- **Database:** DuckDB for efficient storage and querying
- **API Service:** FastAPI application with authentication, pagination, and filtering

---

## Features

### Core Features

- **Modular Design:** Each component is isolated with clear interfaces
- **Data Validation:** Robust validation using Pydantic models
- **Efficient Data Processing:** High-performance data transformations with Polars
- **Analytical Database:** DuckDB for fast SQL-based analytics
- **RESTful API:** Modern API design with FastAPI
- **API Security:** API key authentication and rate limiting
- **Pagination:** Cursor-based pagination for efficient data retrieval
- **Date Filtering:** Filter transactions by date range

### Advanced Features

- **Incremental Processing:** Only process new files since the last run
- **File Archiving:** Automatically archive processed files
- **File Cleanup:** Maintain a configurable number of recent files
- **Database Deduplication:** Prevent duplicate records in the database
- **Transaction Tracking:** Track which files have been processed
- **Robust Error Handling:** Comprehensive logging and error management
- **Configurable Pipeline:** Command-line options for customization

---

## Technical Stack

- **Python 3.8+:** Core programming language
- **FastAPI:** Modern, high-performance web framework for building APIs
- **Pydantic:** Data validation and settings management
- **Polars:** High-performance data manipulation library
- **DuckDB:** In-process analytical SQL database
- **Uvicorn:** ASGI server for serving the API
- **JSON/CSV:** Data interchange formats

---

## Project Structure

```
credable-technical-assement/
├── data/                      # Storage for data files
│   ├── processed/             # Directory for processed files
│   ├── archive/               # Directory for archived files
│   └── processed_files_tracker.pkl  # Tracking file for incremental processing
├── src/
│   ├── data_generator.py      # Generates sample transaction data
│   ├── sftp_client.py         # Simulates SFTP server interaction
│   ├── data_processor.py      # Data cleaning and transformation logic
│   ├── db.py                  # Database connection and operations
│   ├── models.py              # Pydantic models for data validation
│   ├── api.py                 # FastAPI application with endpoints
│   └── main.py                # Pipeline orchestration
├── tests/                     # Unit and integration tests
├── requirements.txt           # Project dependencies
├── README.md                  # Basic project documentation
└── DETAILED_README.md         # Comprehensive documentation (this file)
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step-by-Step Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/credable-technical-assement.git
   cd credable-technical-assement
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**

   The default API key is "test-api-key". To use a custom key:
   
   ```bash
   # Windows
   set API_KEY=your-api-key
   
   # macOS/Linux
   export API_KEY=your-api-key
   ```

5. **Create necessary directories:**

   ```bash
   mkdir -p data/processed data/archive
   ```

---

## Usage

### Running the Pipeline

The pipeline can be run with various configuration options:

```bash
python -m src.main [options]
```

#### Available Options

- `--data-dir`: Directory for raw data files (default: "data")
- `--process-dir`: Directory for processed files (default: "data/processed")
- `--archive-dir`: Directory for archived files (default: "data/archive")
- `--max-files`: Maximum number of files to keep per extension (default: 10)
- `--no-incremental`: Disable incremental processing (process all files)

#### Examples

```bash
# Run with default settings
python -m src.main

# Specify custom directories
python -m src.main --data-dir custom_data --process-dir custom_data/processed

# Keep only 5 most recent files
python -m src.main --max-files 5

# Process all files, even if they've been processed before
python -m src.main --no-incremental
```

### Starting the API Server

After the pipeline has stored data in the database, start the FastAPI server:

```bash
python -m uvicorn src.api:app --reload
```

#### Server Options

- `--host`: Bind socket to this host (default: 127.0.0.1)
- `--port`: Bind socket to this port (default: 8000)
- `--reload`: Enable auto-reload on code changes
- `--workers`: Number of worker processes (default: 1)

#### Examples

```bash
# Start with default settings
python -m uvicorn src.api:app --reload

# Use a different port
python -m uvicorn src.api:app --reload --port 8080

# Bind to all interfaces
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Use multiple workers for production
python -m uvicorn src.api:app --workers 4
```

### API Authentication

The API uses a simple API key authentication mechanism. You must include the API key as a query parameter in all requests to protected endpoints.

Default API key: `test-api-key`

Example:
```
http://localhost:8000/transactions?api_key=test-api-key
```

To change the API key, set the `API_KEY` environment variable before starting the API server.

---

## API Endpoints

### Health Check

```
GET /health
```

Checks if the API service is running properly.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-03-22T07:46:47.493397"
}
```

### Database Test

```
GET /test_db
```

Tests the database connection and returns the total number of records.

**Response:**
```json
{
  "message": "Database connection is active",
  "total_records": 1500
}
```

### Get Transactions

```
GET /transactions
```

Retrieves a paginated list of transactions with optional filtering.

**Query Parameters:**
- `api_key` (required): Your API key for authentication
- `start_date` (optional): Filter transactions from this date (YYYY-MM-DD)
- `end_date` (optional): Filter transactions until this date (YYYY-MM-DD)
- `cursor` (optional): Cursor for pagination
- `limit` (optional): Number of transactions per page (default: 100, min: 1, max: 1000)

**Response:**
```json
{
  "data": [
    {
      "transaction_id": "00192ba2-dabb-4693-82cb-152ad86a79fe",
      "amount": 732.32,
      "currency": "KES",
      "transaction_type": "WITHDRAWAL",
      "status": "CANCELLED",
      "date": "2025-03-05",
      "customer_id": "CUST-6120",
      "customer_name": "Customer 86",
      "customer_email": "customer33@example.com",
      "ip_address": "192.168.0.96",
      "device": "mobile",
      "location": "Eldoret"
    },
    // More transactions...
  ],
  "next_cursor": "00625764-b166-471e-843d-0feff2da65b3",
  "prev_cursor": null,
  "total": 1500
}
```

---

## Data Models

The system uses Pydantic models for data validation and serialization. Here are the key models:

### Transaction Models

- **TransactionBase:** Base model with common transaction fields
  - `transaction_id`: Unique identifier (UUID)
  - `amount`: Transaction amount (positive float)
  - `currency`: Currency code (e.g., "KES")
  - `transaction_type`: Enum (PAYMENT, DEPOSIT, WITHDRAWAL, TRANSFER, REFUND)
  - `status`: Enum (COMPLETED, PENDING, FAILED, CANCELLED)
  - `date`: Transaction date (YYYY-MM-DD)

- **TransactionNested:** Model for nested JSON data
  - Extends TransactionBase
  - `customer`: Nested CustomerModel
  - `metadata`: Nested MetadataModel

- **TransactionFlat:** Model for flattened data (CSV)
  - Extends TransactionBase
  - Flattened customer and metadata fields

- **TransactionResponse:** Model for API responses
  - Extends TransactionBase
  - Flattened customer and metadata fields
  - Used for API responses

### Response Models

- **PaginatedTransactionResponse:** Model for paginated API responses
  - `data`: List of TransactionResponse objects
  - `next_cursor`: Optional cursor for next page
  - `prev_cursor`: Optional cursor for previous page
  - `total`: Total number of records matching the query

---

## Pipeline Components

### Data Generation

The `data_generator.py` module creates realistic financial transaction data for testing and development:

- Generates both CSV and JSON formats
- Creates a configurable number of records
- Uses realistic data patterns for financial transactions
- Timestamps files for easy tracking
- Configurable random seed for reproducibility

### SFTP Integration

The `sftp_client.py` module simulates interaction with an SFTP server:

- In development mode, uses the local filesystem as a mock SFTP server
- Downloads files with specified extensions
- Filters files based on patterns
- Handles connection errors gracefully
- Provides detailed logging

### Data Processing

The `data_processor.py` module handles data transformation and validation:

- Reads and parses CSV and JSON files
- Validates data against Pydantic models
- Cleans and standardizes data
- Handles nested and flat data structures
- Removes duplicates
- Tracks processed files for incremental processing
- Provides detailed error logging

### Database Operations

The `db.py` module manages database interactions:

- Creates and initializes the DuckDB database
- Creates necessary tables and indexes
- Stores processed data efficiently
- Implements deduplication logic
- Provides query capabilities with filtering
- Supports cursor-based pagination
- Handles database errors gracefully

---

## Advanced Features

### Incremental Processing

The system implements incremental processing to avoid reprocessing files that have already been processed:

- Maintains a persistent record of processed files
- Only processes new files in subsequent pipeline runs
- Can be disabled with the `--no-incremental` flag
- Provides detailed logging of skipped and processed files

Implementation details:
```python
# Get list of previously processed files
processed_files = get_processed_files()

# Filter out already processed files
new_files = [f for f in file_paths if f not in processed_files]

# Process only new files
for file_path in new_files:
    # Process file...
    
# Update the processed files tracker
update_processed_files(successfully_processed)
```

### File Management

The system includes comprehensive file management capabilities:

- **File Archiving:** Moves processed files to an archive directory
- **Timestamp Prefixing:** Adds timestamps to archived files
- **File Cleanup:** Keeps only a configurable number of recent files
- **Directory Structure:** Maintains organized directory structure

Implementation details:
```python
# Archive processed files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
for file_path in files:
    if os.path.exists(file_path):
        file_name = os.path.basename(file_path)
        archive_path = os.path.join(archive_dir, f"{timestamp}_{file_name}")
        shutil.move(file_path, archive_path)

# Clean up old files
cleanup_old_files(data_dir, max_files_to_keep)
```

### Deduplication

The system implements robust deduplication at multiple levels:

- **File-level deduplication:** Avoids reprocessing the same files
- **Record-level deduplication:** Prevents duplicate transaction IDs in the database
- **Cross-file deduplication:** Handles duplicates across different files

Implementation details:
```python
# Get existing transaction IDs
existing_ids = self.conn.execute("SELECT transaction_id FROM transactions").fetchall()
existing_ids = [row[0] for row in existing_ids]

# Filter out records with transaction_ids that already exist
new_records = pandas_df[~pandas_df['transaction_id'].isin(existing_ids)]

# Log how many duplicates were found
duplicates_count = len(pandas_df) - len(new_records)
```

---

## Performance Considerations

The system is designed with performance in mind:

- **Polars:** Uses the high-performance Polars library for data processing
- **DuckDB:** Leverages DuckDB's columnar storage for efficient analytics
- **Indexing:** Creates appropriate indexes for efficient querying
- **Pagination:** Implements cursor-based pagination for efficient data retrieval
- **Incremental Processing:** Only processes new files to reduce workload
- **Deduplication:** Efficiently filters out duplicates to minimize database operations

---

## Testing

### Manual Testing

You can manually test the system using the following steps:

1. **Run the pipeline:**
   ```bash
   python -m src.main
   ```

2. **Start the API server:**
   ```bash
   python -m uvicorn src.api:app --reload
   ```

3. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Test the database connection:**
   ```bash
   curl http://localhost:8000/test_db
   ```

5. **Test the transactions endpoint:**
   ```bash
   curl "http://localhost:8000/transactions?api_key=test-api-key&limit=5"
   ```

6. **Test date filtering:**
   ```bash
   curl "http://localhost:8000/transactions?api_key=test-api-key&start_date=2025-03-01&end_date=2025-03-15&limit=5"
   ```

7. **Test pagination:**
   ```bash
   # Get the first page
   curl "http://localhost:8000/transactions?api_key=test-api-key&limit=5"
   
   # Use the next_cursor from the response to get the next page
   curl "http://localhost:8000/transactions?api_key=test-api-key&cursor=NEXT_CURSOR_VALUE&limit=5"
   ```

### Automated Testing

The system includes automated tests for each component:

- **Unit Tests:** Test individual functions and methods
- **Integration Tests:** Test interactions between components
- **API Tests:** Test API endpoints and responses

To run the tests:
```bash
pytest
```

---

## Troubleshooting

### Common Issues

#### Module Not Found Errors

**Problem:** Python cannot find the modules in the project.

**Solution:** Make sure to run commands from the project root directory and that the virtual environment is activated.

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run commands from project root
cd path/to/credable-technical-assement
```

#### Database Issues

**Problem:** Database errors or corruption.

**Solution:** Delete the existing database and run the pipeline again.

```bash
# Windows
Remove-Item -Path "data/transactions.duckdb" -Force

# macOS/Linux
rm -f data/transactions.duckdb

# Run the pipeline again
python -m src.main
```

#### API Key Authentication Fails

**Problem:** API requests return 401 Unauthorized.

**Solution:** Include the correct API key in your requests.

```bash
# Default API key
curl "http://localhost:8000/transactions?api_key=test-api-key"

# If you've set a custom API key
curl "http://localhost:8000/transactions?api_key=your-custom-api-key"
```

#### Port Conflicts

**Problem:** The API server fails to start because the port is in use.

**Solution:** Use a different port.

```bash
python -m uvicorn src.api:app --reload --port 8001
```

### Debugging

For more detailed debugging information, you can increase the logging level:

```python
# In your code
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

Or when running the API server:

```bash
python -m uvicorn src.api:app --reload --log-level debug
```

---

## Future Enhancements

### Potential Improvements

- **Advanced Authentication:** Implement JWT-based authentication
- **Distributed Rate Limiting:** Use Redis for distributed rate limiting
- **Caching:** Add response caching for frequently accessed data
- **Async Database Operations:** Implement asynchronous database operations
- **Data Enrichment:** Add data enrichment capabilities
- **Monitoring:** Add monitoring and alerting
- **Containerization:** Dockerize the application
- **CI/CD:** Set up continuous integration and deployment
- **Schema Evolution:** Handle schema changes gracefully
- **Data Lineage:** Track data provenance
- **Advanced Analytics:** Add analytical capabilities to the API

### Scaling Considerations

- **Database Scaling:** Migrate to a distributed database for larger datasets
- **API Scaling:** Implement horizontal scaling for the API service
- **Pipeline Scaling:** Parallelize data processing for larger files
- **Load Balancing:** Add load balancing for the API service
- **Microservices:** Split into microservices for better scalability

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This project was created as part of a technical assessment for Credable.*
