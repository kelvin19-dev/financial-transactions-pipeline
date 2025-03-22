from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import os
import time
import logging
from datetime import datetime, timedelta

from .models import PaginatedTransactionResponse, TransactionResponse
from .db import DuckDBHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Transactions API", 
    description="API for accessing processed financial transaction data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Simple rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # For this simple example, we'll just add a small delay
    time.sleep(0.1)
    response = await call_next(request)
    return response

# Simple API key authentication
def get_api_key(api_key: str = Query(..., description="API key for authentication")):
    # In a real application, you would verify this against a database
    valid_api_key = os.environ.get("API_KEY", "test-api-key")
    if api_key != valid_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Database connection dependency
def get_db():
    db = DuckDBHandler()
    try:
        yield db
    finally:
        db.close()

@app.get("/transactions", response_model=PaginatedTransactionResponse)
def get_transactions(
    db: DuckDBHandler = Depends(get_db),
    api_key: str = Depends(get_api_key),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items per page")
):
    """
    Get a paginated list of transactions with optional date filtering
    """
    try:
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Get transactions from the database
        transactions, next_cursor, prev_cursor, total = db.get_transactions(start_date, end_date, cursor, limit)
        logger.info(f"Retrieved {len(transactions)} transactions from database")
        
        # Convert to response models
        transaction_responses = []
        for t in transactions:
            try:
                response = TransactionResponse(**t)
                transaction_responses.append(response)
            except Exception as e:
                logger.error(f"Error converting transaction {t['transaction_id']}: {str(e)}")
        
        # Return paginated response
        return PaginatedTransactionResponse(
            data=transaction_responses,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            total=total
        )
    except Exception as e:
        logger.error(f"Error in get_transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/test_db")
def test_db(db: DuckDBHandler = Depends(get_db)):
    try:
        count = db.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        return {"message": "Database connection is active", "total_records": count}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
