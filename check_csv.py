import pandas as pd

print("Checking VehicleDataSheet.csv...")

try:
    df = pd.read_csv('VehicleDataSheet.csv')
    print(f"Total rows in CSV: {len(df)}")
    
    years = sorted(df['Year'].unique(), reverse=True)
    print(f"All years in CSV: {years}")
    
    print(f"Year range: {min(years)} to {max(years)}")
    
    # Check for 2025 and 2026 specifically
    count_2025 = len(df[df['Year'] == 2025])
    count_2026 = len(df[df['Year'] == 2026])
    
    print(f"2025 vehicles in CSV: {count_2025}")
    print(f"2026 vehicles in CSV: {count_2026}")
    
    # Show year distribution
    year_counts = df['Year'].value_counts().sort_index(ascending=False)
    print("\nYear distribution:")
    for year, count in year_counts.head(10).items():
        print(f"  {year}: {count} vehicles")
        
except Exception as e:
    print(f"Error reading CSV: {e}")
    import traceback
    traceback.print_exc() 