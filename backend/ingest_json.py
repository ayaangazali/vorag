"""
Script to ingest JSON data directly into the vector store.
Use this when you have structured data from Bright Data.
"""

import json
import sys
from langchain_core.documents import Document
from app.storage import get_vector_store
from app.config import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def ingest_json_file(json_path: str):
 
    
    print(f"📖 Reading JSON from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
   
    documents = []
    
    if isinstance(data, list):
        items = data
    else:
        items = [data]
    
    for item in items:
        # Create a comprehensive text representation
        text_parts = []
        
        # Add all key-value pairs as text
        for key, value in item.items():
            if key == 'input' or key == 'fund_materials':
                continue  # Skip these
            
            if isinstance(value, dict):
                # Handle nested dicts (like performance data)
                for sub_key, sub_value in value.items():
                    text_parts.append(f"{key} {sub_key}: {sub_value}")
            elif isinstance(value, list):
                # Handle lists
                for list_item in value:
                    if isinstance(list_item, dict):
                        text_parts.append(f"{key}: {json.dumps(list_item)}")
                    else:
                        text_parts.append(f"{key}: {list_item}")
            else:
                # Simple key-value
                text_parts.append(f"{key}: {value}")
        
        # Combine all text
        full_text = "\n".join(text_parts)
        
        # Create document
        doc = Document(
            page_content=full_text,
            metadata={
                "source": item.get("input", {}).get("url", "brightdata_json"),
                "fund_name": item.get("fund_name", "Unknown"),
                "data_type": "structured_json"
            }
        )
        documents.append(doc)
    
    print(f"✅ Created {len(documents)} documents from JSON")
    
    # Chunk the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  Split into {len(chunks)} chunks (size={settings.CHUNK_SIZE})")
    
    # Add to vector store
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    
    print(f"🎉 Successfully ingested {len(chunks)} chunks into vector store!")
    print(f"📊 Total documents in store: {vector_store.get_document_count()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_json.py <path_to_json_file>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    ingest_json_file(json_path)
