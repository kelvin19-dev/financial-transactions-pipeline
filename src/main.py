# src/main.py
import os
import logging
import argparse
import shutil
from datetime import datetime
import glob
from .data_generator import generate_transaction_data
from .sftp_client import get_mock_sftp_client
from .data_processor import process_multiple_files
from .db import DuckDBHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline(data_dir="data", process_dir="data/processed", archive_dir="data/archive", max_files_to_keep=10, incremental=True):
    try:
        # Create archive directory if it doesn't exist
        os.makedirs(archive_dir, exist_ok=True)
        
        logger.info("Generating sample transaction data...")
        generate_transaction_data(num_records=500, output_dir=data_dir, seed=42)
        
        logger.info("Connecting to SFTP and downloading files...")
        sftp_client = get_mock_sftp_client()
        files = sftp_client.download_all_files(local_dir=process_dir, extensions=['.csv', '.json'])
        sftp_client.close()
        
        if not files:
            logger.warning("No files downloaded from SFTP")
            return
        
        logger.info(f"Processing {len(files)} downloaded files...")
        processed_data = process_multiple_files(files, incremental=incremental)
        
        if processed_data.is_empty():
            logger.warning("No valid data after processing")
            return
        
        logger.info("Storing processed data in DuckDB...")
        db = DuckDBHandler()
        records_stored = db.store_data(processed_data)
        db.close()
        
        # Archive processed files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for file_path in files:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                archive_path = os.path.join(archive_dir, f"{timestamp}_{file_name}")
                shutil.move(file_path, archive_path)
                logger.info(f"Archived {file_path} to {archive_path}")
        
        # Clean up old files in data directory
        cleanup_old_files(data_dir, max_files_to_keep)
        
        logger.info(f"Pipeline completed successfully. Stored {records_stored} records in the database.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

def cleanup_old_files(directory, max_files_to_keep=10, extensions=None):
    """
    Clean up old files in a directory, keeping only the most recent ones.
    
    Args:
        directory (str): Directory to clean up
        max_files_to_keep (int): Maximum number of files to keep per extension
        extensions (list): List of extensions to clean up, e.g. ['.csv', '.json']
    """
    if extensions is None:
        extensions = ['.csv', '.json']
    
    logger.info(f"Cleaning up old files in {directory}, keeping {max_files_to_keep} most recent files per extension")
    
    for ext in extensions:
        # Get all files with this extension
        files = glob.glob(os.path.join(directory, f"*{ext}"))
        
        # Sort files by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Remove old files beyond the max to keep
        if len(files) > max_files_to_keep:
            for old_file in files[max_files_to_keep:]:
                try:
                    os.remove(old_file)
                    logger.info(f"Removed old file: {old_file}")
                except Exception as e:
                    logger.error(f"Failed to remove {old_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the data pipeline')
    parser.add_argument('--data-dir', default='data', help='Directory for raw data files')
    parser.add_argument('--process-dir', default='data/processed', help='Directory for processed files')
    parser.add_argument('--archive-dir', default='data/archive', help='Directory for archived files')
    parser.add_argument('--max-files', type=int, default=10, help='Maximum number of files to keep per extension')
    parser.add_argument('--no-incremental', action='store_true', help='Disable incremental processing')
    
    args = parser.parse_args()
    
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.process_dir, exist_ok=True)
    
    run_pipeline(args.data_dir, args.process_dir, args.archive_dir, args.max_files, not args.no_incremental)
