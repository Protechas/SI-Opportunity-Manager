from app.models import SessionLocal, Opportunity

def check_opportunities():
    print("Starting opportunity check...")
    db = SessionLocal()
    try:
        print("Database connection established.")
        opportunities = db.query(Opportunity).all()
        print(f'Total opportunities: {len(opportunities)}')
        
        if len(opportunities) == 0:
            print("No opportunities found in database!")
            return
        
        for i, opp in enumerate(opportunities[:5]):  # Show first 5
            print(f'Opportunity {i+1}:')
            print(f'  ID: {opp.id}')
            print(f'  Title: {opp.title}')
            print(f'  Year: "{opp.year}" (type: {type(opp.year)})')
            print(f'  Make: "{opp.make}" (type: {type(opp.make)})')
            print(f'  Model: "{opp.model}" (type: {type(opp.model)})')
            print(f'  Display Title: "{opp.display_title}"')
            print(f'  Year empty: {not opp.year}')
            print(f'  Make empty: {not opp.make}')
            print(f'  Model empty: {not opp.model}')
            print(f'  All fields present: {all([opp.year, opp.make, opp.model])}')
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    check_opportunities() 