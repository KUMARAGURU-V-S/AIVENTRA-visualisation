#!/bin/bash

# Ensure .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.template..."
    cp .env.template .env
    echo "Please edit .env and add your FEATHERLESS_API_KEY."
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "Step 1: Generating Forensic Data..."
python data_generator.py

echo -e "\nStep 2: Building GraphRAG Index (Requires FEATHERLESS_API_KEY)..."
python indexer.py

echo -e "\nStep 3: Running Comparison Query..."
python query.py "How is Alice connected to the unauthorized login on Charlie's server?"
