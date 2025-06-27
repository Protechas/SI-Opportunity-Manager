import pandas as pd

print("=== Debugging 2026 Vehicle Addition ===")

# Check CSV first
print("\n1. Checking CSV file...")
try:
    df = pd.read_csv('VehicleDataSheet.csv')
    years = sorted(df['Year'].unique(), reverse=True)
    print(f"Years in CSV: {years[:5]}")
    
    count_2024 = len(df[df['Year'] == 2024])
    count_2026 = len(df[df['Year'] == 2026])
    print(f"2024 vehicles in CSV: {count_2024}")
    print(f"2026 vehicles in CSV: {count_2026}")
    
    if count_2024 > 0:
        print("✓ 2024 data exists - can duplicate for 2026")
        
        # Create 2026 data
        df_2024 = df[df['Year'] == 2024].copy()
        df_2026 = df_2024.copy()
        df_2026['Year'] = 2026
        
        # Add to existing data
        df_updated = pd.concat([df, df_2026], ignore_index=True)
        df_updated = df_updated.drop_duplicates()
        
        # Save
        df_updated.to_csv('VehicleDataSheet.csv', index=False)
        print(f"✓ Added {len(df_2026)} vehicles for 2026 to CSV")
        
        # Verify
        df_check = pd.read_csv('VehicleDataSheet.csv')
        count_2026_after = len(df_check[df_check['Year'] == 2026])
        print(f"✓ Verification: {count_2026_after} vehicles for 2026 in CSV")
        
    else:
        print("✗ No 2024 data found to duplicate")
        
except Exception as e:
    print(f"✗ Error with CSV: {e}")
    import traceback
    traceback.print_exc()

# Check database
print("\n2. Checking database...")
try:
    from app.models import SessionLocal, Vehicle
    
    db = SessionLocal()
    
    # Check current state
    count_2024_db = db.query(Vehicle).filter(Vehicle.year == '2024').count()
    count_2026_db = db.query(Vehicle).filter(Vehicle.year == '2026').count()
    
    print(f"2024 vehicles in database: {count_2024_db}")
    print(f"2026 vehicles in database: {count_2026_db}")
    
    if count_2024_db > 0 and count_2026_db == 0:
        print("✓ Can add 2026 vehicles to database")
        
        # Get 2024 vehicles
        vehicles_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').all()
        
        added_count = 0
        for vehicle in vehicles_2024:
            # Create 2026 version
            new_vehicle = Vehicle(
                year='2026',
                make=vehicle.make,
                model=vehicle.model,
                is_custom=False
            )
            db.add(new_vehicle)
            added_count += 1
            
            # Commit in batches
            if added_count % 100 == 0:
                db.commit()
                print(f"  Added {added_count} vehicles...")
        
        db.commit()
        print(f"✓ Added {added_count} vehicles for 2026 to database")
        
        # Verify
        count_2026_after = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        print(f"✓ Verification: {count_2026_after} vehicles for 2026 in database")
        
    elif count_2026_db > 0:
        print(f"✓ 2026 vehicles already exist: {count_2026_db}")
    else:
        print("✗ No 2024 vehicles found to duplicate")
    
    db.close()
    
except Exception as e:
    print(f"✗ Error with database: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Final Check ===")
try:
    from app.models import SessionLocal, Vehicle
    db = SessionLocal()
    
    years = db.query(Vehicle.year).distinct().all()
    year_list = sorted([y[0] for y in years], reverse=True)
    print(f"Available years in database: {year_list[:10]}")
    
    if '2026' in year_list:
        print("✅ SUCCESS: 2026 is now available!")
    else:
        print("❌ FAILED: 2026 is still not available")
    
    db.close()
    
except Exception as e:
    print(f"Error in final check: {e}")

print("\nDone!") 