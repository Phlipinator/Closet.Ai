import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np


vit_model = tf.keras.models.load_model("./models/vit_model")

image_path = 'UserImage.png'


def preprocess_data(image_path):
    img_width,img_height = 224, 224
    image = tf.keras.utils.load_img(image_path, target_size=(img_height, img_width, 3))
    # Normalize pixel values to be in the range [-1, 1]
    image = (image / 127.5) - 1
    image = np.expand_dims(image, axis=0)
    print(image.shape)
    return image 

def getResults():
    img_width,img_height = 224, 224
    image = tf.keras.utils.load_img(image_path, target_size=(img_height, img_width, 3))
    image = tf.keras.utils.img_to_array(image)
    image =  image / 255
    image = np.expand_dims(image, axis=0)
    label_mapping = {0 : 'jacket', 1 : 'pants', 2 : 'shirt', 3 : 'shoe', 4: 'sweater', 5: 'tshirt'}
    prediction = label_mapping.get(vit_model.predict(image).argmax())
    return prediction

