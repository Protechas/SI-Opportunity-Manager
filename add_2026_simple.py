# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.models import SessionLocal, Vehicle

def main():
    print("Adding 2026 Vehicle Data")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Check current state
        count_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').count()
        count_2026 = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        total_vehicles = db.query(Vehicle).count()
        
        print(f"Current Status:")
        print(f"  Total vehicles: {total_vehicles}")
        print(f"  2024 vehicles: {count_2024}")
        print(f"  2026 vehicles: {count_2026}")
        
        if count_2026 > 0:
            print("2026 vehicles already exist. Skipping.")
            return
            
        if count_2024 == 0:
            print("No 2024 vehicles found to duplicate.")
            return
            
        print(f"\nAdding {count_2024} vehicles for 2026...")
        
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
        new_total = db.query(Vehicle).count()
        
        print(f"Successfully added {final_count} vehicles for 2026")
        print(f"Total vehicles increased from {total_vehicles} to {new_total}")
        
        # Show sample vehicles
        sample_vehicles = db.query(Vehicle).filter(Vehicle.year == '2026').limit(3).all()
        print(f"\nSample 2026 vehicles:")
        for vehicle in sample_vehicles:
            print(f"  - {vehicle.year} {vehicle.make} {vehicle.model}")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\nProcess completed!")

if __name__ == "__main__":
    main() 