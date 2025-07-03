import pandas as pd

# Step 1: Load the dataset
file_path = 'Sleep_health_and_lifestyle_dataset.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Check unique values in the 'Sleep Disorder' column
unique_values = df['Sleep Disorder'].unique()
print("Unique Sleep Disorder values:", unique_values)

# Step 3: Map unique values to numerical indices
disorder_mapping = {value: idx for idx, value in enumerate(unique_values)}
print("Mapping of Sleep Disorders to indices:", disorder_mapping)

# Step 4: Add a new column 'Sleep Disorder Index'
df['Sleep Disorder Index'] = df['Sleep Disorder'].map(disorder_mapping)

# Step 5: Save the modified dataset
output_file_path = 'Modified_Sleep_health_and_lifestyle_dataset.csv'  # Desired output file path
df.to_csv(output_file_path, index=False)

print(f"Modified dataset saved to {output_file_path}")

