from app.models import SessionLocal, Opportunity
from datetime import datetime

def test_form_submission():
    print("Testing form submission with empty values...")
    
    # Test what happens when we create an opportunity with empty strings
    db = SessionLocal()
    try:
        # Simulate what happens when currentText() returns empty strings
        test_opp = Opportunity(
            title="TEST-2025-00001",
            year="",  # Empty string
            make="",  # Empty string
            model="", # Empty string
            description="Test description",
            status='new',
            systems=[],
            creator_id=None,  # We'll use None for testing
            created_at=datetime.utcnow()
        )
        
        print(f"Before adding to DB:")
        print(f"  Year: '{test_opp.year}' (type: {type(test_opp.year)})")
        print(f"  Make: '{test_opp.make}' (type: {type(test_opp.make)})")
        print(f"  Model: '{test_opp.model}' (type: {type(test_opp.model)})")
        print(f"  Display Title: '{test_opp.display_title}'")
        
        # Don't actually save to avoid polluting the database
        # db.add(test_opp)
        # db.commit()
        
        print("\nTesting with actual values:")
        test_opp2 = Opportunity(
            title="TEST-2025-00002",
            year="2025",
            make="Toyota",
            model="Camry",
            description="Test description",
            status='new',
            systems=[],
            creator_id=None,
            created_at=datetime.utcnow()
        )
        
        print(f"  Year: '{test_opp2.year}' (type: {type(test_opp2.year)})")
        print(f"  Make: '{test_opp2.make}' (type: {type(test_opp2.make)})")
        print(f"  Model: '{test_opp2.model}' (type: {type(test_opp2.model)})")
        print(f"  Display Title: '{test_opp2.display_title}'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_combo_box_behavior():
    """Test what currentText() returns in different scenarios"""
    print("\nTesting combo box behavior simulation:")
    
    # Simulate what happens with empty combo boxes
    empty_text = ""
    print(f"Empty currentText(): '{empty_text}' -> bool: {bool(empty_text)}")
    
    # Test the validation logic
    year_text = ""
    make_text = ""
    model_text = ""
    
    validation_result = all([year_text, make_text, model_text])
    print(f"Validation with empty strings: {validation_result}")
    
    # Test with actual values
    year_text = "2025"
    make_text = "Toyota"
    model_text = "Camry"
    
    validation_result = all([year_text, make_text, model_text])
    print(f"Validation with actual values: {validation_result}")

if __name__ == "__main__":
    test_form_submission()
    test_combo_box_behavior() 