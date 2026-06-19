"""
Upload raw data collections to MongoDB Atlas
Run this script from the notebook data directory
"""

import json
import certifi
import pandas as pd
from pathlib import Path
from pymongo import MongoClient

# Configuration
MONGO_URI = "mongodb+srv://omar_yasser_311:omar_yasser_311@cluster0.8pykbmn.mongodb.net/?appName=Cluster0"
DB_NAME = "StudentaAnalytics"

# Assumes you've downloaded the data locally or have access to it
# For now, we'll try to create minimal sample data or load from existing collections

def _to_docs(df):
    """Converts a DataFrame to a JSON-safe list of dicts for MongoDB."""
    temp_df = df.copy()
    for col in temp_df.select_dtypes(include=['datetime64[ns]', 'period[M]']).columns:
        temp_df[col] = temp_df[col].astype(str)
    for col in temp_df.select_dtypes(include=['category']).columns:
        temp_df[col] = temp_df[col].astype(str)
    return json.loads(temp_df.to_json(orient='records'))

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    client.admin.command('ping')
    print(f"✓ Connected to MongoDB: {DB_NAME}")
    
    # Load existing collections
    students_master = pd.DataFrame(list(db['students_master'].find({}, {'_id': 0})))
    cluster_segments = pd.DataFrame(list(db['cluster_segments'].find({}, {'_id': 0})))
    at_risk_students = pd.DataFrame(list(db['at_risk_students'].find({}, {'_id': 0})))
    group_summaries = pd.DataFrame(list(db['group_summaries'].find({}, {'_id': 0})))
    
    print(f"✓ Loaded {len(students_master)} students from students_master")
    
    # Create synthetic raw collections from derived data
    # This is a workaround until the Jupyter notebook uploads the raw data
    
    # students collection
    students = students_master[['student_id', 'full_name', 'age', 'group_id', 'enrollment_date']].drop_duplicates('student_id')
    
    # groups collection  
    groups = group_summaries[['group_id', 'group_name', 'course_id', 'course_name', 'instructor']].drop_duplicates('group_id')
    
    # courses collection
    courses = groups[['course_id', 'course_name']].drop_duplicates('course_id')
    
    print(f"✓ Created {len(students)} student records")
    print(f"✓ Created {len(groups)} group records")
    print(f"✓ Created {len(courses)} course records")
    
    # Upload to MongoDB
    upload_map = {
        "students": students,
        "groups": groups,
        "courses": courses,
        "cluster_segments": cluster_segments,
        "students_master": students_master,
        "at_risk_students": at_risk_students,
        "group_summaries": group_summaries,
    }
    
    for coll_name, data_df in upload_map.items():
        if data_df.empty:
            print(f"⊘ Skipped '{coll_name}' (empty)")
            continue
            
        collection = db[coll_name]
        collection.delete_many({})
        docs = _to_docs(data_df)
        collection.insert_many(docs)
        print(f"✓ Uploaded {len(docs)} records to '{coll_name}'")
    
    print("\n✓ Raw data upload complete!")
    
    # Verify
    all_collections = sorted(db.list_collection_names())
    print(f"\n✓ Total collections: {len(all_collections)}")
    for coll in all_collections:
        count = db[coll].count_documents({})
        print(f"  • {coll}: {count} records")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
