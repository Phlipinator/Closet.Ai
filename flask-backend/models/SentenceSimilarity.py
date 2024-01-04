import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import pickle

# Load the preprocessed amazon data
with open('models/amazon_data_V3_preprocessed.pickle', 'rb') as pkl:
    df_preprocessed = pickle.load(pkl)

# Load the sentence transformer
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

def getResults(user_input, category='top', top_results=1):

    # Create a embedding of the user input
    query_embedding = similarity_model.encode(user_input)

    # get the right category
    if category == 'shoes':
        df_category = df_preprocessed[df_preprocessed['category'].isin(['shoes', 'sandals'])]
        df_category = df_category.reset_index(drop=True)
    if category == 'pants':
        df_category = df_preprocessed[df_preprocessed['category'].isin(['trousers', 'shorts'])]
        df_category = df_category.reset_index(drop=True)
    if category == 'top':
        df_category = df_preprocessed[df_preprocessed['category'].isin(['t-shirt', 'shirt', 'jacket', 'sweater' ])]
        df_category = df_category.reset_index(drop=True)

    # Compute the Cosine Similarity between the review embedding and the user input embedding
    df_category['cos_score'] = df_category['embedding'].apply(lambda x: util.cos_sim(query_embedding, x))
    df_category['cos_score'] = df_category['cos_score'].astype(float)

    # Find the n most similar results
    top_n = df_category.nlargest(top_results, 'cos_score')
    top_n = top_n['image_url'].values.astype(str)
    return(top_n)