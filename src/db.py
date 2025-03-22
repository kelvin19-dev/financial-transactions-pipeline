import duckdb
import os
import polars as pl
import logging
from typing import List, Dict, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DuckDBHandler:
    def __init__(self, db_path: str = "data/transactions.duckdb"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = duckdb.connect(self.db_path)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id VARCHAR PRIMARY KEY,
                amount DOUBLE,
                currency VARCHAR,
                transaction_type VARCHAR,
                status VARCHAR,
                date VARCHAR,
                customer_id VARCHAR,
                customer_name VARCHAR,
                customer_email VARCHAR,
                ip_address VARCHAR,
                device VARCHAR,
                location VARCHAR
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_date ON transactions(date);
        """)
        logger.info("Database initialized successfully")
    
    def store_data(self, df: pl.DataFrame) -> int:
        if df.is_empty():
            logger.warning("No data to store in database")
            return 0

        try:
            # Convert Polars DataFrame to Pandas DataFrame
            pandas_df = df.to_pandas()
            
            # Get existing transaction IDs to avoid duplicates
            existing_ids = self.conn.execute("SELECT transaction_id FROM transactions").fetchall()
            existing_ids = [row[0] for row in existing_ids]
            
            # Filter out records with transaction_ids that already exist in the database
            if not pandas_df.empty and 'transaction_id' in pandas_df.columns:
                new_records = pandas_df[~pandas_df['transaction_id'].isin(existing_ids)]
                
                if new_records.empty:
                    logger.info("No new records to insert - all transaction IDs already exist in the database")
                    return 0
                
                # Log how many duplicates were found
                duplicates_count = len(pandas_df) - len(new_records)
                if duplicates_count > 0:
                    logger.info(f"Skipping {duplicates_count} duplicate records that already exist in the database")
                
                # Append only the new records to the transactions table
                self.conn.append("transactions", new_records)
                
                # Get the total record count from the database
                count = self.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
                logger.info(f"Stored {len(new_records)} new records; database now has {count} records")
                return len(new_records)
            else:
                logger.warning("DataFrame is missing transaction_id column, cannot check for duplicates")
                return 0
        except Exception as e:
            logger.error(f"Error storing data in database: {str(e)}")
            return 0
    
    def get_transactions(self, 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None,
                         cursor: Optional[str] = None,
                         limit: int = 100) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str], int]:
        where_clauses = []
        params = []
        
        if start_date:
            where_clauses.append("date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        count_query = f"SELECT COUNT(*) FROM transactions WHERE {where_clause}"
        total_count = self.conn.execute(count_query, params).fetchone()[0]
        
        cursor_clause = ""
        if cursor:
            cursor_clause = "AND transaction_id > ?"
            params.append(cursor)
        
        query = f"""
            SELECT * FROM transactions 
            WHERE {where_clause} {cursor_clause}
            ORDER BY transaction_id
            LIMIT {limit + 1}
        """
        
        try:
            results = self.conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            records = [{columns[i]: value for i, value in enumerate(row)} for row in results[:limit]]
            
            next_cursor = results[limit-1][0] if len(results) > limit else None
            prev_cursor = cursor if cursor else None
            
            return records, next_cursor, prev_cursor, total_count
        except Exception as e:
            logger.error(f"Error retrieving transactions: {str(e)}")
            return [], None, None, 0
    
    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
