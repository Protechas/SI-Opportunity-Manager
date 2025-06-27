from app.models import SessionLocal, Opportunity, Vehicle
from datetime import datetime

def fix_existing_opportunities():
    """Fix existing opportunities that have None values for vehicle data"""
    db = SessionLocal()
    try:
        # Find opportunities with None vehicle data
        broken_opportunities = db.query(Opportunity).filter(
            (Opportunity.year.is_(None)) |
            (Opportunity.make.is_(None)) |
            (Opportunity.model.is_(None))
        ).all()
        
        print(f"Found {len(broken_opportunities)} opportunities with missing vehicle data:")
        
        if len(broken_opportunities) == 0:
            print("No opportunities need fixing!")
            return
        
        # Get a default vehicle to use (most recent 2025 vehicle)
        default_vehicle = db.query(Vehicle).filter(Vehicle.year == '2025').first()
        
        if not default_vehicle:
            print("No default vehicle found! Please ensure vehicles are loaded.")
            return
        
        print(f"Using default vehicle: {default_vehicle.year} {default_vehicle.make} {default_vehicle.model}")
        
        # Ask user for confirmation
        response = input(f"\nDo you want to update all {len(broken_opportunities)} opportunities with the default vehicle? (y/N): ")
        
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Update all broken opportunities
        updated_count = 0
        for opp in broken_opportunities:
            opp.year = default_vehicle.year
            opp.make = default_vehicle.make
            opp.model = default_vehicle.model
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f"Updated {updated_count} opportunities...")
        
        db.commit()
        print(f"Successfully updated {updated_count} opportunities!")
        
        # Verify the fix
        remaining_broken = db.query(Opportunity).filter(
            (Opportunity.year.is_(None)) |
            (Opportunity.make.is_(None)) |
            (Opportunity.model.is_(None))
        ).count()
        
        print(f"Remaining opportunities with missing vehicle data: {remaining_broken}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def list_available_vehicles():
    """List available vehicles for reference"""
    db = SessionLocal()
    try:
        # Get some sample vehicles from each year
        years = ['2026', '2025', '2024']
        
        print("Available vehicles by year:")
        for year in years:
            vehicles = db.query(Vehicle).filter(Vehicle.year == year).limit(5).all()
            print(f"  {year}:")
            for v in vehicles:
                print(f"    - {v.year} {v.make} {v.model}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

def manual_fix_opportunity(opportunity_id, year, make, model):
    """Manually fix a specific opportunity"""
    db = SessionLocal()
    try:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            print(f"Opportunity {opportunity_id} not found!")
            return
        
        print(f"Before: {opp.display_title}")
        opp.year = year
        opp.make = make
        opp.model = model
        db.commit()
        print(f"After: {opp.display_title}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Vehicle Data Fix Tool")
    print("=" * 50)
    
    print("\n1. Listing available vehicles...")
    list_available_vehicles()
    
    print("\n2. Checking for broken opportunities...")
    fix_existing_opportunities() 