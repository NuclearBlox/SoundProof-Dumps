import os
import json
from datetime import datetime, timezone
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

TABLES_TO_EXPORT = ["artists"]
os.makedirs("data", exist_ok=True)

change_summary = {
    "last_updated_utc": datetime.now(timezone.utc).isoformat(),
    "changes": {}
}

for table in TABLES_TO_EXPORT:
    # 1. Fetch data
    new_data = []
    batch_size = 1000
    start = 0
    
    while True:
        response = supabase.table(table).select("*").range(start, start + batch_size - 1).execute()
        chunk = response.data
        if not chunk:
            break
        new_data.extend(chunk)
        if len(chunk) < batch_size:
            break
        start += batch_size

    # 2. Check the old one
    file_path = f"data/{table}.json"
    old_data_map = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                old_records = json.load(f)
                # Assuming your table has a primary key column called 'id'
                old_data_map = {str(row.get("id")): row for row in old_records}
        except Exception:
            pass

    # 3. See whats new
    new_records_found = []
    for row in new_data:
        row_id = str(row.get("id"))
        if row_id not in old_data_map:
            new_records_found.append(row)

    # 4. Write that down
    change_summary["changes"][table] = {
        "total_rows": len(new_data),
        "new_rows_added_count": len(new_records_found),
        "new_rows": new_records_found
    }

    # 5. Save it
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
        
    print(f"Exported {len(new_data)} rows from '{table}'. Found {len(new_records_found)} new rows.")

# 6. Save the changes
with open("data/recent_changes.json", "w", encoding="utf-8") as f:
    json.dump(change_summary, f, indent=2)

print("Successfully generated data/recent_changes.json change log.")
