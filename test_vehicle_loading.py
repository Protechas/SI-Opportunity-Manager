from app.models import SessionLocal, Vehicle

def test_vehicle_loading():
    print("Testing vehicle loading...")
    db = SessionLocal()
    try:
        print("Database connection established.")
        vehicles = db.query(Vehicle).all()
        print(f'Total vehicles: {len(vehicles)}')
        
        if len(vehicles) == 0:
            print("No vehicles found in database!")
            return
        
        # Test what would be in the combo boxes
        years = sorted(set(v.year for v in vehicles), reverse=True)
        print(f"Available years: {years[:10]}")  # Show first 10
        
        if years:
            test_year = years[0]
            print(f"Testing with year: {test_year}")
            
            makes = sorted(set(v.make for v in vehicles if str(v.year) == test_year))
            print(f"Makes for {test_year}: {makes[:5]}")  # Show first 5
            
            if makes:
                test_make = makes[0]
                print(f"Testing with make: {test_make}")
                
                models = sorted(set(v.model for v in vehicles 
                                  if str(v.year) == test_year and v.make == test_make))
                print(f"Models for {test_year} {test_make}: {models[:5]}")  # Show first 5
        
        # Test a few sample vehicles
        print("\nSample vehicles:")
        for i, v in enumerate(vehicles[:5]):
            print(f"  {i+1}. {v.year} {v.make} {v.model}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    test_vehicle_loading() 