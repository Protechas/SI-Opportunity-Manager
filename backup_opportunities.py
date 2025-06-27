from app.models import SessionLocal, Opportunity
import json
import csv
from datetime import datetime
import os

def backup_opportunities_json():
    """Create a JSON backup of all opportunities"""
    db = SessionLocal()
    try:
        opportunities = db.query(Opportunity).all()
        
        backup_data = []
        for opp in opportunities:
            opp_data = {
                'id': str(opp.id),
                'title': opp.title,
                'description': opp.description,
                'status': opp.status,
                'year': opp.year,
                'make': opp.make,
                'model': opp.model,
                'systems': opp.systems,
                'affected_portions': opp.affected_portions,
                'meta_data': opp.meta_data,
                'comments': opp.comments,
                'creator_id': str(opp.creator_id) if opp.creator_id else None,
                'acceptor_id': str(opp.acceptor_id) if opp.acceptor_id else None,
                'created_at': opp.created_at.isoformat() if opp.created_at else None,
                'updated_at': opp.updated_at.isoformat() if opp.updated_at else None,
                'completed_at': opp.completed_at.isoformat() if opp.completed_at else None,
                'started_at': opp.started_at.isoformat() if opp.started_at else None,
                'response_time': str(opp.response_time) if opp.response_time else None,
                'work_time': str(opp.work_time) if opp.work_time else None
            }
            backup_data.append(opp_data)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"opportunities_backup_{timestamp}.json"
        
        # Save to backup file
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON backup created: {backup_filename}")
        print(f"  Total opportunities backed up: {len(backup_data)}")
        return backup_filename
        
    except Exception as e:
        print(f"Error creating JSON backup: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def backup_opportunities_csv():
    """Create a CSV backup of opportunity vehicle data (simpler format)"""
    db = SessionLocal()
    try:
        opportunities = db.query(Opportunity).all()
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"opportunities_vehicle_backup_{timestamp}.csv"
        
        # Save to CSV file
        with open(backup_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['id', 'title', 'year', 'make', 'model', 'display_title', 'description_first_line'])
            
            # Write data
            for opp in opportunities:
                first_line = opp.description.split('\n')[0] if opp.description else ''
                writer.writerow([
                    str(opp.id),
                    opp.title,
                    opp.year,
                    opp.make,
                    opp.model,
                    opp.display_title,
                    first_line
                ])
        
        print(f"✓ CSV backup created: {backup_filename}")
        print(f"  Total opportunities backed up: {len(opportunities)}")
        return backup_filename
        
    except Exception as e:
        print(f"Error creating CSV backup: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def verify_backup(backup_filename):
    """Verify the backup file was created correctly"""
    if not os.path.exists(backup_filename):
        print(f"✗ Backup file not found: {backup_filename}")
        return False
    
    file_size = os.path.getsize(backup_filename)
    print(f"✓ Backup file verified: {backup_filename}")
    print(f"  File size: {file_size:,} bytes")
    
    if backup_filename.endswith('.json'):
        try:
            with open(backup_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  JSON records: {len(data)}")
            return True
        except Exception as e:
            print(f"✗ Error reading JSON backup: {e}")
            return False
    elif backup_filename.endswith('.csv'):
        try:
            with open(backup_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            print(f"  CSV rows: {len(rows) - 1} (excluding header)")
            return True
        except Exception as e:
            print(f"✗ Error reading CSV backup: {e}")
            return False
    
    return True

def create_full_backup():
    """Create both JSON and CSV backups"""
    print("=== CREATING OPPORTUNITY BACKUPS ===")
    print("This will backup all opportunity data before making changes.")
    
    # Create JSON backup (complete data)
    print("\n1. Creating JSON backup (complete data)...")
    json_backup = backup_opportunities_json()
    
    # Create CSV backup (vehicle data focus)
    print("\n2. Creating CSV backup (vehicle data focus)...")
    csv_backup = backup_opportunities_csv()
    
    # Verify backups
    print("\n3. Verifying backups...")
    json_ok = verify_backup(json_backup) if json_backup else False
    csv_ok = verify_backup(csv_backup) if csv_backup else False
    
    if json_ok and csv_ok:
        print("\n✓ All backups created successfully!")
        print(f"JSON backup: {json_backup}")
        print(f"CSV backup: {csv_backup}")
        print("\nYou can now safely proceed with the vehicle data extraction.")
        return True
    else:
        print("\n✗ Some backups failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    create_full_backup() 