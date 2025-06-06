#!/bin/sh

# This script is used to run the application
# Under different OS, the line endings may be different
# Under Windows, the line endings are CRLF
# Under Unix, the line endings are LF
# When running in Docker(Linux), the line endings are LF

set -e

# Set collection name and local path (update these as needed)
# Collection name is the name of the vector store in S3
COLLECTION_NAME="all_docs_db_small_chunks"
# Local path is the path to the directory where the vector store will be stored
# It is relative to the app directory e.g. app/vector_stores
LOCAL_PATH="plan_creator_bundle/vector_stores"

echo ""
echo "Running startup script:"
echo "Checking if vector store exists..."
echo "If not, creating vector store..."
echo "This may take a while."
echo ""
echo "Collection name: $COLLECTION_NAME"
echo "Local path: $LOCAL_PATH"
echo ""

# Run the vector store script and capture its exit code
python -m plan_creator_bundle.scripts.download_vectorstore_from_s3 "$COLLECTION_NAME" "$LOCAL_PATH"
VECTOR_STORE_STATUS=$?

# Check if the script failed
if [ $VECTOR_STORE_STATUS -ne 0 ]; then
    echo "ERROR: Failed to load or create vector store. Exiting..."
    exit 1
fi

# If we get here, the vector store is ready
echo "Vector store is ready. Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 