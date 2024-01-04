import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

# Define the columns of the csv file
columns = ['category','image_url','reviews']

# Read the csv file, skipping the lines with errors
df = pd.read_csv('amazon_data_V3.csv', delimiter=',', header=None, names=columns, error_bad_lines=False)

# Remove rows with empty 'reviews' column
df = df[df['reviews'] != '[]']

# Reset the index of the dataframe
df = df.reset_index(drop=True)

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Add a new column 'embedding' and populate it with the encodings of the 'reviews' column
df['embedding'] = df['reviews'].apply(lambda x: model.encode(x))

# Save the preprocessed dataframe to a pickle file
with open('amazon_data_V3_preprocessed.pickle', 'wb') as pkl:
    pickle.dump(df, pkl)

