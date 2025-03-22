# src/data_processor.py
import polars as pl
import json
import logging
import os
import pickle
from datetime import datetime
from typing import List, Dict, Any, Union, Set, Tuple
from .models import TransactionNested, TransactionFlat

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to store the processed files tracking information
PROCESSED_FILES_TRACKER = "data/processed_files_tracker.pkl"

def get_processed_files() -> Set[str]:
    """Get the set of files that have already been processed"""
    if os.path.exists(PROCESSED_FILES_TRACKER):
        try:
            with open(PROCESSED_FILES_TRACKER, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading processed files tracker: {str(e)}")
    return set()

def update_processed_files(file_paths: List[str]) -> None:
    """Update the set of processed files"""
    processed_files = get_processed_files()
    processed_files.update(file_paths)
    
    try:
        with open(PROCESSED_FILES_TRACKER, 'wb') as f:
            pickle.dump(processed_files, f)
        logger.info(f"Updated processed files tracker with {len(file_paths)} new files")
    except Exception as e:
        logger.error(f"Error updating processed files tracker: {str(e)}")

def read_csv_file(file_path: str) -> pl.DataFrame:
    """Read and parse a CSV file into a Polars DataFrame"""
    try:
        df = pl.read_csv(file_path)
        logger.info(f"Successfully read CSV file: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        return pl.DataFrame()

def read_json_file(file_path: str) -> pl.DataFrame:
    """Read and parse a JSON file into a Polars DataFrame"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Flatten nested JSON data
        flat_data = []
        for item in data:
            flat_item = {
                "transaction_id": item.get("transaction_id"),
                "amount": item.get("amount"),
                "currency": item.get("currency"),
                "transaction_type": item.get("transaction_type"),
                "status": item.get("status"),
                "date": item.get("date"),
                "customer_id": item.get("customer", {}).get("customer_id"),
                "customer_name": item.get("customer", {}).get("name"),
                "customer_email": item.get("customer", {}).get("email"),
                "ip_address": item.get("metadata", {}).get("ip_address"),
                "device": item.get("metadata", {}).get("device"),
                "location": item.get("metadata", {}).get("location")
            }
            flat_data.append(flat_item)
        
        df = pl.DataFrame(flat_data)
        logger.info(f"Successfully read JSON file: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {str(e)}")
        return pl.DataFrame()

def validate_data(df: pl.DataFrame) -> pl.DataFrame:
    """Validate data using Pydantic models"""
    valid_rows = []
    invalid_count = 0
    
    for row in df.iter_rows(named=True):
        try:
            # Validate the data using the appropriate Pydantic model
            TransactionFlat(**row)
            valid_rows.append(row)
        except Exception as e:
            invalid_count += 1
            logger.warning(f"Invalid row: {row}, Error: {str(e)}")
    
    if invalid_count > 0:
        logger.warning(f"Removed {invalid_count} invalid records")
    
    if valid_rows:
        return pl.DataFrame(valid_rows)
    else:
        return pl.DataFrame()

def clean_data(df: pl.DataFrame) -> pl.DataFrame:
    """Clean and standardize the data"""
    if df.is_empty():
        return df

    # Make a copy to avoid modifying the original DataFrame
    cleaned_df = df.clone()

    # Handle missing values: fill missing values in non-critical columns
    if "ip_address" in cleaned_df.columns:
        cleaned_df = cleaned_df.with_columns([pl.col("ip_address").fill_null("unknown")])
    if "device" in cleaned_df.columns:
        cleaned_df = cleaned_df.with_columns([pl.col("device").fill_null("unknown")])
    if "location" in cleaned_df.columns:
        cleaned_df = cleaned_df.with_columns([pl.col("location").fill_null("unknown")])

    # Standardize case for enum values
    cleaned_df = cleaned_df.with_columns([pl.col("transaction_type").map_elements(lambda x: str(x).upper() if x else None)])
    cleaned_df = cleaned_df.with_columns([pl.col("status").map_elements(lambda x: str(x).upper() if x else None)])

    # Drop duplicates based on transaction_id
    cleaned_df = cleaned_df.unique(subset=["transaction_id"])

    logger.info(f"Cleaned data: {len(cleaned_df)} records after cleaning")
    return cleaned_df


def process_file(file_path: str) -> pl.DataFrame:
    """Process a data file based on its extension"""
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() == '.csv':
        df = read_csv_file(file_path)
    elif ext.lower() == '.json':
        df = read_json_file(file_path)
    else:
        logger.warning(f"Unsupported file format: {ext}")
        return pl.DataFrame()
    
    if df.is_empty():
        return df
    
    # Validate the data
    validated_df = validate_data(df)
    
    # Clean and standardize the data
    cleaned_df = clean_data(validated_df)
    
    return cleaned_df

def process_multiple_files(file_paths: List[str], incremental: bool = True) -> pl.DataFrame:
    """
    Process multiple files and combine the results
    
    Args:
        file_paths: List of file paths to process
        incremental: If True, only process files that haven't been processed before
    """
    # Get list of previously processed files if incremental processing is enabled
    processed_files = set()
    if incremental:
        processed_files = get_processed_files()
        
        # Filter out already processed files
        new_files = [f for f in file_paths if f not in processed_files]
        
        if not new_files:
            logger.info("No new files to process - all files have been processed before")
            return pl.DataFrame()
        
        logger.info(f"Found {len(new_files)} new files out of {len(file_paths)} total files")
        file_paths = new_files
    
    dfs = []
    successfully_processed = []
    
    for file_path in file_paths:
        df = process_file(file_path)
        if not df.is_empty():
            dfs.append(df)
            successfully_processed.append(file_path)
    
    # Update the processed files tracker with successfully processed files
    if incremental and successfully_processed:
        update_processed_files(successfully_processed)
    
    if not dfs:
        return pl.DataFrame()
    
    # Combine all DataFrames
    combined_df = pl.concat(dfs)
    
    # Remove duplicates across files
    combined_df = combined_df.unique(subset=["transaction_id"])
    
    logger.info(f"Processed {len(file_paths)} files, resulting in {len(combined_df)} unique records")
    return combined_df