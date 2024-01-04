import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

sentiment_model = tf.keras.models.load_model("models/sentiment_model_bert")


def getResults(user_input):
    input_tokenized = tokenizer(user_input, max_length=128, padding=True, truncation=True, return_tensors='tf')
    output = sentiment_model(input_tokenized)
    prediction = tf.nn.softmax(output['logits'], axis=-1)
    labels = ['Negative','Positive']
    label = tf.argmax(prediction, axis=1)
    label = label.numpy()
    print(label)
    most_similar = labels[label[0]]
    return most_similar
