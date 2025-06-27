print("Starting import test...")

try:
    from app.models import Vehicle, SessionLocal
    print("✓ Successfully imported models")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

try:
    db = SessionLocal()
    print("✓ Successfully created database session")
    
    count = db.query(Vehicle).count()
    print(f"✓ Vehicle count: {count}")
    
    if count > 0:
        # Get a sample vehicle
        sample = db.query(Vehicle).first()
        print(f"✓ Sample vehicle: {sample.year} {sample.make} {sample.model}")
        
        # Get unique years
        years = db.query(Vehicle.year).distinct().all()
        year_list = sorted([y[0] for y in years], reverse=True)
        print(f"✓ Available years: {year_list[:10]}")
        
        if '2025' in year_list:
            print("✓ 2025 is available")
        else:
            print("✗ 2025 is NOT available")
            
        if '2026' in year_list:
            print("✓ 2026 is available")
        else:
            print("✗ 2026 is NOT available")
    else:
        print("✗ No vehicles found in database")
        
    db.close()
    
except Exception as e:
    print(f"✗ Database error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.") 