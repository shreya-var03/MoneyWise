import pandas as pd
import os

# Put the exact name of your dataset CSV here
DATASET_FILE = "rupeeRoast_dataset.csv" 

if os.path.exists(DATASET_FILE):
    # Load the dataset
    df = pd.read_csv(DATASET_FILE)
    original_count = len(df)
    
    # Remove all exact duplicate rows
    df = df.drop_duplicates()
    new_count = len(df)
    
    # Save it back clean
    df.to_csv(DATASET_FILE, index=False)
    
    print("✅ Dataset Cleaned Successfully!")
    print(f"Removed {original_count - new_count} duplicate rows.")
    print(f"Total unique transactions remaining: {new_count}")
else:
    print(f"⚠️ Could not find {DATASET_FILE}. Please check the file name.")