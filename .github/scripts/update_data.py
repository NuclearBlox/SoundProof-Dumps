import os
import json
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

TABLES_TO_EXPORT = ["artists"]

os.makedirs("data", exist_ok=True)

for table in TABLES_TO_EXPORT:
    all_data = []
    batch_size = 1000
    start = 0
    
    # Loop through the table in chunks to bypass the 1,000-row  limit
    while True:
        response = supabase.table(table).select("*").range(start, start + batch_size - 1).execute()
        chunk = response.data
        
        if not chunk:
            break
            
        all_data.extend(chunk)
        
        # Do we have it all
        if len(chunk) < batch_size:
            break
            
        start += batch_size

    # Save it
    file_path = f"data/{table}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully exported {len(all_data)} rows from '{table}' to JSON.")
