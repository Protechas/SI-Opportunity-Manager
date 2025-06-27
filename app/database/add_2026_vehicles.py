import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import text
from app.database.connection import SessionLocal
from app.models.models import Vehicle

def add_2026_vehicles():
    """Add 2026 vehicles by duplicating 2024 data"""
    db = SessionLocal()
    try:
        print("Checking current vehicle data...")
        
        # Check current counts
        count_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').count()
        count_2026 = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        
        print(f"Current 2024 vehicles: {count_2024}")
        print(f"Current 2026 vehicles: {count_2026}")
        
        if count_2026 > 0:
            print("2026 vehicles already exist. Skipping...")
            return
            
        if count_2024 == 0:
            print("No 2024 vehicles found to duplicate. Cannot proceed.")
            return
            
        print(f"Adding 2026 vehicles by duplicating {count_2024} vehicles from 2024...")
        
        # Use raw SQL for efficiency
        sql = """
        INSERT INTO vehicles (id, year, make, model, is_custom, created_at)
        SELECT 
            gen_random_uuid() as id,
            '2026' as year,
            make,
            model,
            false as is_custom,
            CURRENT_TIMESTAMP as created_at
        FROM vehicles 
        WHERE year = '2024'
        """
        
        result = db.execute(text(sql))
        db.commit()
        
        # Verify results
        final_count = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        print(f"Successfully added {final_count} vehicles for 2026")
        
        # Show sample
        sample_vehicles = db.query(Vehicle).filter(Vehicle.year == '2026').limit(3).all()
        print("Sample 2026 vehicles:")
        for vehicle in sample_vehicles:
            print(f"  - {vehicle.year} {vehicle.make} {vehicle.model}")
            
    except Exception as e:
        db.rollback()
        print(f"Error adding 2026 vehicles: {str(e)}")
        raise
    finally:
        db.close()

def verify_years():
    """Verify all available years"""
    db = SessionLocal()
    try:
        years = db.query(Vehicle.year).distinct().all()
        year_list = sorted([y[0] for y in years], reverse=True)
        print(f"Available years: {year_list[:10]}")
        
        for year in ['2026', '2025', '2024']:
            count = db.query(Vehicle).filter(Vehicle.year == year).count()
            print(f"{year}: {count} vehicles")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding 2026 vehicle data...")
    print("=" * 50)
    
    add_2026_vehicles()
    
    print("\nVerification:")
    print("=" * 50)
    verify_years()
    
    print("\nDone!") 