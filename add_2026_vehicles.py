import pandas as pd
from app.models import SessionLocal, Vehicle

def add_2026_to_csv():
    """Add 2026 vehicle data to the CSV by duplicating 2024 data"""
    print("Reading current CSV file...")
    df = pd.read_csv('VehicleDataSheet.csv')
    
    # Get 2024 data
    df_2024 = df[df['Year'] == 2024].copy()
    print(f"Found {len(df_2024)} vehicles for 2024")
    
    if len(df_2024) == 0:
        print("No 2024 data found to duplicate for 2026")
        return False
    
    # Create 2026 data by changing the year
    df_2026 = df_2024.copy()
    df_2026['Year'] = 2026
    
    # Combine with existing data
    df_updated = pd.concat([df, df_2026], ignore_index=True)
    
    # Remove duplicates (in case 2026 data already exists)
    df_updated = df_updated.drop_duplicates()
    
    # Save updated CSV
    df_updated.to_csv('VehicleDataSheet.csv', index=False)
    print(f"Updated CSV with {len(df_2026)} new 2026 vehicles")
    
    # Show year distribution
    year_counts = df_updated['Year'].value_counts().sort_index(ascending=False)
    print("\nUpdated year distribution:")
    for year, count in year_counts.head(5).items():
        print(f"  {year}: {count} vehicles")
    
    return True

def add_2026_to_database():
    """Add 2026 vehicles directly to the database"""
    db = SessionLocal()
    try:
        # Get all 2024 vehicles from database
        vehicles_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').all()
        print(f"Found {len(vehicles_2024)} vehicles for 2024 in database")
        
        if len(vehicles_2024) == 0:
            print("No 2024 vehicles found in database to duplicate")
            return False
        
        added_count = 0
        for vehicle_2024 in vehicles_2024:
            # Check if 2026 version already exists
            existing = db.query(Vehicle).filter(
                Vehicle.year == '2026',
                Vehicle.make == vehicle_2024.make,
                Vehicle.model == vehicle_2024.model
            ).first()
            
            if not existing:
                # Create new 2026 vehicle
                new_vehicle = Vehicle(
                    year='2026',
                    make=vehicle_2024.make,
                    model=vehicle_2024.model,
                    is_custom=False
                )
                db.add(new_vehicle)
                added_count += 1
        
        db.commit()
        print(f"Added {added_count} new 2026 vehicles to database")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error adding 2026 vehicles to database: {e}")
        return False
    finally:
        db.close()

def verify_2026_data():
    """Verify that 2026 data is now available"""
    db = SessionLocal()
    try:
        count_2026 = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        print(f"Total 2026 vehicles in database: {count_2026}")
        
        if count_2026 > 0:
            # Show some examples
            sample_vehicles = db.query(Vehicle).filter(Vehicle.year == '2026').limit(5).all()
            print("Sample 2026 vehicles:")
            for vehicle in sample_vehicles:
                print(f"  - {vehicle.year} {vehicle.make} {vehicle.model}")
            return True
        else:
            print("No 2026 vehicles found")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding 2026 vehicle data...")
    print("=" * 50)
    
    # Method 1: Update CSV and re-run populate script
    print("Method 1: Updating CSV file...")
    if add_2026_to_csv():
        print("✓ CSV updated successfully")
        
        # Re-run populate script
        print("\nRe-running populate script...")
        from app.scripts.populate_vehicles import populate_vehicles
        populate_vehicles()
    else:
        print("✗ Failed to update CSV")
    
    print("\n" + "=" * 50)
    
    # Method 2: Add directly to database (as backup)
    print("Method 2: Adding directly to database...")
    add_2026_to_database()
    
    print("\n" + "=" * 50)
    print("Verification:")
    verify_2026_data()
    
    print("\nDone!") 