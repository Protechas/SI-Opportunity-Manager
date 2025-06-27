from app.models import SessionLocal, Vehicle

def check_years():
    db = SessionLocal()
    try:
        print("Connecting to database...")
        vehicles = db.query(Vehicle).all()
        print(f"Total vehicles in database: {len(vehicles)}")
        
        if len(vehicles) == 0:
            print("No vehicles found in database!")
            return
            
        years = sorted(set(v.year for v in vehicles), reverse=True)
        print('Available years:', years[:15])  # Show first 15 years
        print(f'Total unique years: {len(years)}')
        
        # Check specifically for 2025 and 2026
        if '2025' in years:
            print('✓ 2025 is available')
        else:
            print('✗ 2025 is NOT available')
            
        if '2026' in years:
            print('✓ 2026 is available')
        else:
            print('✗ 2026 is NOT available')
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_years() 