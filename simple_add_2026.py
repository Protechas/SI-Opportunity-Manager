print("Adding 2026 vehicles...")

try:
    from app.models import SessionLocal, Vehicle
    
    db = SessionLocal()
    
    # Check current state
    count_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').count()
    count_2026 = db.query(Vehicle).filter(Vehicle.year == '2026').count()
    
    print(f"Current 2024 vehicles: {count_2024}")
    print(f"Current 2026 vehicles: {count_2026}")
    
    if count_2024 > 0 and count_2026 == 0:
        print("Adding 2026 vehicles...")
        
        # Get all 2024 vehicles
        vehicles_2024 = db.query(Vehicle).filter(Vehicle.year == '2024').all()
        
        added = 0
        for vehicle in vehicles_2024:
            new_vehicle = Vehicle(
                year='2026',
                make=vehicle.make,
                model=vehicle.model,
                is_custom=False
            )
            db.add(new_vehicle)
            added += 1
            
            if added % 50 == 0:
                print(f"Added {added} vehicles...")
        
        db.commit()
        print(f"Successfully added {added} vehicles for 2026")
        
        # Verify
        final_count = db.query(Vehicle).filter(Vehicle.year == '2026').count()
        print(f"Final 2026 count: {final_count}")
        
    else:
        print("Cannot add 2026 vehicles:")
        if count_2024 == 0:
            print("- No 2024 vehicles to duplicate")
        if count_2026 > 0:
            print(f"- 2026 vehicles already exist ({count_2026})")
    
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Done!") 