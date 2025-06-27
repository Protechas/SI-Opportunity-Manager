from app.models import SessionLocal, Opportunity
import json

def investigate_ticket_data():
    """Investigate all fields in opportunities to find where vehicle data is stored"""
    db = SessionLocal()
    try:
        # Get all opportunities
        opportunities = db.query(Opportunity).all()
        
        # Separate good and broken opportunities
        good_opps = [opp for opp in opportunities if all([opp.year, opp.make, opp.model])]
        broken_opps = [opp for opp in opportunities if not all([opp.year, opp.make, opp.model])]
        
        print("=== INVESTIGATING TICKET DATA ===")
        print(f"Good opportunities: {len(good_opps)}")
        print(f"Broken opportunities: {len(broken_opps)}")
        
        if good_opps:
            print("\n=== ANALYZING GOOD OPPORTUNITIES ===")
            for i, opp in enumerate(good_opps[:3]):  # Look at first 3 good ones
                print(f"\nOpportunity {i+1}: {opp.title}")
                print(f"  Year: '{opp.year}'")
                print(f"  Make: '{opp.make}'")
                print(f"  Model: '{opp.model}'")
                print(f"  Display Title: '{opp.display_title}'")
                print(f"  Description: '{opp.description[:100]}...'")
                
                # Check systems field for vehicle data
                if opp.systems:
                    print(f"  Systems: {opp.systems}")
                
                # Check meta_data field for vehicle data
                if opp.meta_data:
                    print(f"  Meta Data: {opp.meta_data}")
                
                # Check affected_portions field
                if opp.affected_portions:
                    print(f"  Affected Portions: {opp.affected_portions}")
        
        if broken_opps:
            print(f"\n=== ANALYZING BROKEN OPPORTUNITIES ===")
            for i, opp in enumerate(broken_opps[:3]):  # Look at first 3 broken ones
                print(f"\nBroken Opportunity {i+1}: {opp.title}")
                print(f"  Year: '{opp.year}'")
                print(f"  Make: '{opp.make}'")
                print(f"  Model: '{opp.model}'")
                print(f"  Display Title: '{opp.display_title}'")
                print(f"  Description: '{opp.description[:100] if opp.description else 'None'}...'")
                
                # Check if vehicle data might be in other fields
                if opp.systems:
                    print(f"  Systems: {opp.systems}")
                    # Look for vehicle data in systems
                    if isinstance(opp.systems, list):
                        for system in opp.systems:
                            if isinstance(system, dict):
                                print(f"    System dict: {system}")
                
                if opp.meta_data:
                    print(f"  Meta Data: {opp.meta_data}")
                    # Look for vehicle data in meta_data
                    if isinstance(opp.meta_data, dict):
                        for key, value in opp.meta_data.items():
                            if any(word in key.lower() for word in ['vehicle', 'year', 'make', 'model']):
                                print(f"    Potential vehicle data in meta_data: {key} = {value}")
                
                if opp.affected_portions:
                    print(f"  Affected Portions: {opp.affected_portions}")
                
                # Check the description for vehicle information
                if opp.description:
                    desc_lower = opp.description.lower()
                    if any(word in desc_lower for word in ['year', 'make', 'model', '2024', '2025', '2023', 'toyota', 'honda', 'ford', 'nissan']):
                        print(f"  *** Potential vehicle info in description: {opp.description}")
        
        print(f"\n=== SUMMARY ===")
        print("Looking for patterns in where vehicle data might be stored...")
        print("Check the output above for any vehicle information in:")
        print("- systems field")
        print("- meta_data field") 
        print("- affected_portions field")
        print("- description field")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    investigate_ticket_data() 