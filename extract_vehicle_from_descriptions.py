from app.models import SessionLocal, Opportunity
import re

def extract_vehicle_from_descriptions():
    """Extract vehicle data from descriptions and populate the proper database fields"""
    db = SessionLocal()
    try:
        # Get broken opportunities (those without vehicle data in proper fields)
        broken_opps = db.query(Opportunity).filter(
            (Opportunity.year.is_(None)) |
            (Opportunity.make.is_(None)) |
            (Opportunity.model.is_(None))
        ).all()
        
        print(f"Found {len(broken_opps)} opportunities with missing vehicle data in database fields")
        
        fixed_count = 0
        failed_count = 0
        
        for opp in broken_opps:
            if not opp.description:
                print(f"Skipping {opp.title} - no description")
                failed_count += 1
                continue
            
            # Look for "Vehicle: YYYY Make Model" pattern in description (first line only)
            first_line = opp.description.split('\n')[0]
            vehicle_match = re.search(r'Vehicle:\s*(\d{4})\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)\s+([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]*)*)', first_line)
            
            if vehicle_match:
                year = vehicle_match.group(1)
                make = vehicle_match.group(2).strip()
                model = vehicle_match.group(3).strip()
                
                # Update the opportunity with extracted vehicle data
                opp.year = year
                opp.make = make  
                opp.model = model
                
                print(f"✓ Fixed {opp.title}: {year} {make} {model}")
                fixed_count += 1
            else:
                print(f"✗ Could not extract vehicle from {opp.title}: {first_line}")
                failed_count += 1
        
        if fixed_count > 0:
            print(f"\nReady to update {fixed_count} opportunities.")
            print(f"Failed to extract vehicle data from {failed_count} opportunities.")
            
            response = input(f"\nDo you want to commit these {fixed_count} updates to the database? (y/N): ")
            
            if response.lower() == 'y':
                db.commit()
                print(f"✓ Successfully updated {fixed_count} opportunities!")
                
                # Verify the fix
                remaining_broken = db.query(Opportunity).filter(
                    (Opportunity.year.is_(None)) |
                    (Opportunity.make.is_(None)) |
                    (Opportunity.model.is_(None))
                ).count()
                
                print(f"Remaining opportunities with missing vehicle data: {remaining_broken}")
            else:
                db.rollback()
                print("Changes rolled back - no updates made.")
        else:
            print("No vehicle data could be extracted from descriptions.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def preview_extraction():
    """Preview what would be extracted without making changes"""
    db = SessionLocal()
    try:
        broken_opps = db.query(Opportunity).filter(
            (Opportunity.year.is_(None)) |
            (Opportunity.make.is_(None)) |
            (Opportunity.model.is_(None))
        ).all()
        
        print("=== PREVIEW - NO CHANGES WILL BE MADE ===")
        print(f"Analyzing {len(broken_opps)} opportunities...")
        
        extractable_count = 0
        
        for opp in broken_opps[:10]:  # Show first 10 as preview
            if not opp.description:
                continue
                
            first_line = opp.description.split('\n')[0]
            vehicle_match = re.search(r'Vehicle:\s*(\d{4})\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)\s+([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]*)*)', first_line)
            
            if vehicle_match:
                year = vehicle_match.group(1)
                make = vehicle_match.group(2).strip()
                model = vehicle_match.group(3).strip()
                
                print(f"✓ {opp.title}: Would extract '{year} {make} {model}'")
                print(f"   From: {first_line}")
                extractable_count += 1
            else:
                print(f"✗ {opp.title}: No extractable vehicle data")
                print(f"   First line: {first_line}")
        
        print(f"\nPreview complete. Found extractable data in {extractable_count} of first 10 opportunities.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("1. Preview extraction")
    print("2. Run actual extraction")
    choice = input("Choose option (1 or 2): ")
    
    if choice == "1":
        preview_extraction()
    elif choice == "2":
        extract_vehicle_from_descriptions()
    else:
        print("Invalid choice") 