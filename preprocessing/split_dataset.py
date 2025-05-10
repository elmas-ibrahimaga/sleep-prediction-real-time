import pandas as pd

# Step 1: Load the dataset
file_path = 'datasets/Sleep_health_and_lifestyle_dataset.csv'  # Moved under datasets
df = pd.read_csv(file_path)

# Step 2: Check unique values in the 'Sleep Disorder' column
unique_values = df['Sleep Disorder'].unique()
print("Unique Sleep Disorder values:", unique_values)

# Step 3: Map unique values to numerical indices
disorder_mapping = {value: idx for idx, value in enumerate(unique_values)}
print("Mapping of Sleep Disorders to indices:", disorder_mapping)

# Step 4: Add a new column 'Sleep Disorder Index'
df['Sleep Disorder Index'] = df['Sleep Disorder'].map(disorder_mapping)

# Step 5: Split the dataset
train_df = df.sample(frac=0.8, random_state=42)  # 80% for training
test_df = df.drop(train_df.index)

# Step 6: Save to datasets/
train_output_path = 'datasets/train_datasett.csv'
test_output_path = 'datasets/test_datasett.csv'

train_df.to_csv(train_output_path, index=False)
test_df.to_csv(test_output_path, index=False)

print(f"✅ Train dataset saved to {train_output_path}")
print(f"✅ Test dataset saved to {test_output_path}")
