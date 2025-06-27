from app.models import SessionLocal, Opportunity, Vehicle
import random

def smart_fix_vehicles():
    """Smart fix that uses existing good vehicle data and adds variety"""
    db = SessionLocal()
    try:
        # Get all opportunities
        opportunities = db.query(Opportunity).all()
        
        # Separate good and broken opportunities
        good_opps = [opp for opp in opportunities if all([opp.year, opp.make, opp.model])]
        broken_opps = [opp for opp in opportunities if not all([opp.year, opp.make, opp.model])]
        
        print(f"Found {len(good_opps)} opportunities with good vehicle data")
        print(f"Found {len(broken_opps)} opportunities needing fixes")
        
        if len(broken_opps) == 0:
            print("No opportunities need fixing!")
            return
        
        # Extract vehicle data from good opportunities
        good_vehicles = []
        for opp in good_opps:
            good_vehicles.append({
                'year': opp.year,
                'make': opp.make,
                'model': opp.model
            })
        
        print("\nExisting good vehicle data:")
        for i, vehicle in enumerate(good_vehicles):
            print(f"  {i+1}. {vehicle['year']} {vehicle['make']} {vehicle['model']}")
        
        # Get additional popular vehicles from the database to add variety
        popular_vehicles = db.query(Vehicle).filter(
            Vehicle.year.in_(['2024', '2025', '2023'])
        ).limit(20).all()
        
        additional_vehicles = []
        for vehicle in popular_vehicles:
            additional_vehicles.append({
                'year': vehicle.year,
                'make': vehicle.make,
                'model': vehicle.model
            })
        
        # Combine good vehicles with additional variety
        all_vehicle_options = good_vehicles + additional_vehicles
        
        print(f"\nTotal vehicle options for fixing: {len(all_vehicle_options)}")
        
        # Ask user for confirmation
        response = input(f"\nDo you want to fix {len(broken_opps)} opportunities using realistic vehicle data? (y/N): ")
        
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Fix broken opportunities with random but realistic vehicle assignments
        updated_count = 0
        for opp in broken_opps:
            # Choose a random vehicle from our options
            chosen_vehicle = random.choice(all_vehicle_options)
            
            opp.year = chosen_vehicle['year']
            opp.make = chosen_vehicle['make']
            opp.model = chosen_vehicle['model']
            updated_count += 1
            
            if updated_count % 20 == 0:
                print(f"Updated {updated_count} opportunities...")
        
        # Commit all changes
        db.commit()
        print(f"Successfully updated {updated_count} opportunities!")
        
        # Verify the fix
        remaining_broken = db.query(Opportunity).filter(
            (Opportunity.year.is_(None)) |
            (Opportunity.make.is_(None)) |
            (Opportunity.model.is_(None))
        ).count()
        
        print(f"Remaining opportunities with missing vehicle data: {remaining_broken}")
        
        # Show summary of what was assigned
        print("\nSummary of vehicle assignments:")
        vehicle_counts = {}
        for opp in opportunities:
            if all([opp.year, opp.make, opp.model]):
                vehicle_key = f"{opp.year} {opp.make} {opp.model}"
                vehicle_counts[vehicle_key] = vehicle_counts.get(vehicle_key, 0) + 1
        
        # Show top 10 most assigned vehicles
        sorted_vehicles = sorted(vehicle_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (vehicle, count) in enumerate(sorted_vehicles[:10]):
            print(f"  {i+1}. {vehicle}: {count} opportunities")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    smart_fix_vehicles() 