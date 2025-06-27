from app.models import SessionLocal, Opportunity

def check_mixed_opportunities():
    print("Checking for mixed opportunity data...")
    db = SessionLocal()
    try:
        opportunities = db.query(Opportunity).all()
        print(f'Total opportunities: {len(opportunities)}')
        
        # Separate opportunities by whether they have vehicle data
        with_vehicle = []
        without_vehicle = []
        
        for opp in opportunities:
            if all([opp.year, opp.make, opp.model]):
                with_vehicle.append(opp)
            else:
                without_vehicle.append(opp)
        
        print(f"Opportunities WITH vehicle data: {len(with_vehicle)}")
        print(f"Opportunities WITHOUT vehicle data: {len(without_vehicle)}")
        
        # Show some examples of each
        if with_vehicle:
            print("\nSample opportunities WITH vehicle data:")
            for i, opp in enumerate(with_vehicle[:3]):
                print(f"  {i+1}. {opp.title} - {opp.display_title}")
                print(f"      Year: '{opp.year}', Make: '{opp.make}', Model: '{opp.model}'")
        
        if without_vehicle:
            print("\nSample opportunities WITHOUT vehicle data:")
            for i, opp in enumerate(without_vehicle[:3]):
                print(f"  {i+1}. {opp.title} - {opp.display_title}")
                print(f"      Year: '{opp.year}', Make: '{opp.make}', Model: '{opp.model}'")
        
        # Check if there's a pattern based on creation date
        if with_vehicle and without_vehicle:
            print("\nAnalyzing creation dates...")
            
            # Get the newest and oldest with vehicle data
            with_vehicle_sorted = sorted(with_vehicle, key=lambda x: x.created_at or datetime.min)
            oldest_with = with_vehicle_sorted[0] if with_vehicle_sorted else None
            newest_with = with_vehicle_sorted[-1] if with_vehicle_sorted else None
            
            # Get the newest and oldest without vehicle data
            without_vehicle_sorted = sorted(without_vehicle, key=lambda x: x.created_at or datetime.min)
            oldest_without = without_vehicle_sorted[0] if without_vehicle_sorted else None
            newest_without = without_vehicle_sorted[-1] if without_vehicle_sorted else None
            
            if oldest_with and oldest_with.created_at:
                print(f"Oldest WITH vehicle data: {oldest_with.created_at}")
            if newest_with and newest_with.created_at:
                print(f"Newest WITH vehicle data: {newest_with.created_at}")
            if oldest_without and oldest_without.created_at:
                print(f"Oldest WITHOUT vehicle data: {oldest_without.created_at}")
            if newest_without and newest_without.created_at:
                print(f"Newest WITHOUT vehicle data: {newest_without.created_at}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    check_mixed_opportunities() 