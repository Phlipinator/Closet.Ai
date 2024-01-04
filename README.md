# Structure #
This README will
- Provide an overview of the project
- Introduce the team members
- Give an installation guide
- Explain the additional recourses that were created during the project but are not needed in the final product

# Overview #
Closet.AI is a chatbot AI, that allows the user to generate an outfit based on a text input (regarding the days plans, the mood or similar) and a piece of clothing that the outfit should be built around. After the user made the two requested inputs he will be presented with four options for each part of clothing that is missing.
At the end the user will be presented with the finished outfit.
For simplicity we defined the human body as three categories: Top, Pants & Shoes (if a user provides a picture of a t-shirt -> top, he will be provided with 4 options of shoes and 4 options of pants).
We also only considered mens clothing.

# Team Members #
- Sebastian Müller (Seb.Mueller@campus.lmu.de)
- Sami Strack (S.Strack@campus.lmu.de)
- Michael Huber (mi.huber@campus.lmu.de)
- Agnes Reda (A.Reda@campus.lmu.de)
- Philipp Thalhammer (philipp.thalhammer@campus.lmu.de)

# Installation Guide #
1. create a python virtual environment (venv) within flask-backend
        
        python -m venv venv
    
    on macOS, replace ```python``` with ```python3```
2. activate the venv
    
    * Windows: ```venv\Scripts\activate```
    * Mac: ```source venv_mac/bin/activate```
3. install all packages

    Windows:
        
        pip install flask numpy pandas tensorflow pillow transformers sentence-transformers flask-socketio simple-websocket

    macOS:
        
        pip3 install flask numpy pandas tensorflow-macos pillow transformers sentence-transformers flask-socketio simple-websocket

4. start the backend with ```python server.py``` on windows and ```python3 server.py``` on macOS.
5. navigate to react-frontend
6. install all packages

        npm install react-dropzone socket.io-client react-scroll-to-bottom
        
7. start the frontend with ```npm start```

# Resources #
Everything described in this paragraph can be found in the resources folder.

## Amazon Webscraper ##
The amazon Webscraper was created using python and beautiful soup.
To run it, first install the libraries that are listed at the top of scraper.py.
The scraper uses a typical amazon search link and adds an array of search strings into that to scrape the ASINs into a CSV file. After that part is concluded productScraper.py gets run automatically and takes the previously scraped ASINS to look at each product individually.
Here a category is added (based on the search term) as well as the link to the first image of an item and up to 5 comments (if they have more than 20 characters).
How the parameters can be changed is described in the code.

## NLP Model ##
The user should be generated the most suitable outfit based on his input. For this purpose, the reviews stored by the web scraper for each product are compared with the input. We decided to use the package sentence_transformer (https://www.sbert.net/) for this purpose, as transformers provide very accurate and robust results. 
First, the transformer calculates an embedding of all amazon reviews. To avoid having to do this calculation at runtime, it is done in the Python file preprocess_amazon_data.py in the models directory and stored in a pickle file.
In SenetenceSimilarity.py the user input is also translated into an embedding by the transformer and then the products with the most suitable reviews are selected using cosine similarity.

At the beginning of the project, we wanted to perform a sentiment analysis of the user reaction to a recommendation in order to possibly make a new recommendation based on this. However, during the course of the project, we abandoned this plan because it seemed much more user-friendly to show the user several recommendations and let him choose from them. The code is strongly inspired by this blog https://towardsdatascience.com/sentiment-analysis-in-10-minutes-with-bert-and-hugging-face-294e8a04b671 and adjusted to our dataset. You find the notebook called Clothing_Sentiment_Analysis_BERT.ipynb in the resources directory.

## Visual Recognition Model ##
The visual recognition model is used to recognize the photo input and define it as a category we will not recommend. For example, if we put in a T-shirt, the IA will recognize it as a top cloth and will not recommend a different T-shirt or any cloth from this category. 

The model recognition notebook is in the file vgg_vit_finetune.ipynb. We have used google collab to take advantage of the GPU which improve the data training time. What we want to do is to finetune 2 models to compare them and take the best. 
In the first lines, we take only the first 40 000 lines of the dataset we want to finetune on. Of course, we didn't take all of the dataset because the training time would have been too high and we had sufficient result with this subset. 

In this dataset, we don't want to take every lines. We didn't see the necessity of taking all of the categories. To take the most relevant, we plotted the category by the number of elements in it and regrouped them in a most general category. For example, sports shoes and casual shoes are regrouped in shoes category. 

Then we use ImageDataGenerator for data augmentation that will artificially expand the dataset and making the model more reliable. The flow_from_generator will help us to divide the dataset in a training and validation dataset as well as doing preprocessing such as reformatting the images to use for the model. Furthermore, this method automatically encodes labels. 

The first model we finetune is the vgg16. We add layers and only train on them by freezing the others layers. This model has about 15,000,000 parameters but only 1% of it is trainable. 

The second model we finetune is vit_b8. This model has the best results on imagenet dataset between the vit models available on tensorhub. To finetune it, we freeze layer to the -3 level and add Dense, Dropout and Flate layers. This model has much more parameters and about 1.6 % of them are trainable. As a consequence, we have better results but in counterpart it takes about 4x more time to train than the vgg16. 

By comparing the results, we decide to take the vit_b8 as the base model. Indeed, it has better results in less epochs but also accuracy between training and validations set are less divergent. 

Different resources used for this task : 
- https://tfhub.dev/sayakpaul/vit_b8_classification/1 model code for finetune
- https://www.tensorflow.org/hub/tutorials?hl=fr code to import the model 
- https://openai.com/blog/chatgpt/ to help with debugging 
- https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator code for datagenerator
