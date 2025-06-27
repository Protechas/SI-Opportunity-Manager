import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from app.database.connection import get_db_with_retry

def run_migration():
    print("Running migration 010: Add 2026 vehicles...")
    
    db = get_db_with_retry()
    try:
        # Read the SQL file
        sql_file = os.path.join(os.path.dirname(__file__), '010_add_2026_vehicles.sql')
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Execute the migration
        result = db.execute(text(sql_content))
        db.commit()
        
        print(f"✓ Migration completed successfully")
        print(f"✓ Added 2026 vehicle data")
        
        # Verify the results
        count_result = db.execute(text("SELECT COUNT(*) FROM vehicles WHERE year = '2026'"))
        count_2026 = count_result.scalar()
        print(f"✓ Total 2026 vehicles: {count_2026}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_migration() 