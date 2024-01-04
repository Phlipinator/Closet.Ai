# This is set up to work with a virtual environment of python
# To activate use:
#
# FOR WINDOWS: venv\Scripts\activate
# If this does not work try running windows power-shell as administrator and run the command "Set-ExecutionPolicy Unrestricted", then try again
# ALSO you might get an import issue with flask. If that is the case you have to manually set the interpreter Path to the virtual environment
# The path for this is \venv\Scripts\python.exe
# If there are questions talk to me (Philipp Thalhammer) about the setup process
#
# FOR MAC: source venv_mac/bin/activate
# To deactivate the virtual env just type deactivate into the terminal
# Note: The Interpreter-Path has to be added MANUALLY. It does NOT suffice to select it by going through the filesystem
# Go to "add manually" and enter the following path:
# ./flask-backend/venv_mac/bin/python3
#
# To start the Server:
# FOR WINDOWS: python server.py
# FOR MAC: python3 server.py
#
# Be sure that you are in the correct directory and have the virtual env activated
# The server will start on localhost port 5000

from flask import Flask, request
import base64
# import models.SentimentClassification as sentiment
import models.SentenceSimilarity as similarity
import models.ClothingClassification as classification

# imports needed for socket functionality
# socketio implementation based on https://hackmd.io/@jpshafto/r1BLkFVwu
from flask_socketio import SocketIO
# import os
import time
import json

from datetime import datetime


    

#the maximum imageSize in MB
maxImageSize = 5


#create the socket
socketio = SocketIO(cors_allowed_origins='*', max_http_buffer_size=maxImageSize*1048576)

app = Flask(__name__)
socketio.init_app(app)

# Global variables can be defined here and accessed with dataStore.variableName
class DataStore():
    messageCount = 0
    userInput = None
    userCategory = None
    top = None
    pants = None
    shoes = None
    topSelected = False
    pantsSelected = False
    shoesSelected = False
    topsPresented = False
    pantsPresented = False
    shoesPresented = False

dataStore = DataStore()

def getTime():
    now = datetime.now() 
    return now.strftime("%H:%M:%S")

# Handles a new chat text message received from the client via socketio
@socketio.on("chat")
def handleInput(chatData):
    dataStore.messageCount = dataStore.messageCount + 1

    message = json.loads(chatData)
    messageExtracted = message['msgContent']

    if messageExtracted == "reset":
        reset()
    else:
        if dataStore.messageCount == 1:
            dataStore.userInput = messageExtracted
            socketio.emit("chat", {"msgContent": "Thank you, please upload an image that you want me to design you an outfit around", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        else:
            # "error handling" - if user sends message outside of the interaction flow, he get's an appropriate answer from the server
            socketio.emit("chat", {"msgContent": "I cannot handle this request of yours right now.", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
            dataStore.messageCount = dataStore.messageCount - 1


#handles images sent to the server via socketio
@socketio.on("upload")
def handleUpload(uploadData):
    # Save the image String into a variable
    imgMessage = json.loads(uploadData)
    imgString = imgMessage['msgContent']

    
    if dataStore.messageCount == 0:
        socketio.emit("chat", {"msgContent": "Please first describe your plans for the day before sending me images 🤪", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
    elif dataStore.messageCount > 1:
        socketio.emit("chat", {"msgContent": "I cannot handle this image of yours right now.", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
    else:
        dataStore.messageCount = dataStore.messageCount +1
        # There is some preprocessing done on the frontend that removes the "data:image/png;base64," in the beginning so the decoding works properly

        # Decode the String and save it into a file
        # This part can MAYBE be removed again, depending on how the further processing of the image is done
        # Inspiration for this part was found here:
        # https://www.codegrepper.com/tpc/how+to+decode+base64+string+to+image+in+python
        with open("UserImage.png", "wb") as fh:
            fh.write(base64.b64decode(imgString))

        # the file is now saved in flask-backend as 'UserImage.png'

        # Handling of the Image can be done here

        socketio.emit("chat", {"msgContent": "Thank you, I will now create an outfit for you. This may take a while ⚙️", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        category = classification.getResults()
        dataStore.userCategory = switchCategory(category)

        if dataStore.userCategory == "top":
            dataStore.topSelected = True
            with open("UserImage.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                dataStore.top = f"data:image/png;base64,{encoded_string.decode()}"
        if dataStore.userCategory == "pants":
            dataStore.pantsSelected = True
            with open("UserImage.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                dataStore.pants = f"data:image/png;base64,{encoded_string.decode()}"
        if dataStore.userCategory == "shoes":
            dataStore.shoesSelected = True
            with open("UserImage.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                dataStore.shoes = f"data:image/png;base64,{encoded_string.decode()}"
        
        socketio.emit("chat", {"msgContent": "Great " + category + ", by the way! 😁", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)

        createOutfit()

# change the detected clothing category into one of our 3 pre-defined categories
def switchCategory(classifiedAs):
    if classifiedAs == "jacket" or classifiedAs == "shirt" or classifiedAs == "tshirt" or classifiedAs == "sweater":
        return "top"
    elif classifiedAs == 'pants':
        return "pants"
    elif classifiedAs == 'shoe':
        return "shoes"

# Encode a given file to Base64
def encodeImg(path):
    with open(path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())

    # Formats the String so the front-end can properly display it
    formattedString = str(b64_string)
    formattedString = formattedString[2:]
    formattedString = formattedString[:-1]
    return (formattedString)

@socketio.on("select")
def selectImage(image, category):
        if dataStore.userInput != None:
            time.sleep(1)
            if category == "shoes":
                if dataStore.shoesSelected:
                    socketio.emit("chat", {"msgContent": "You already selected shoes", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                else:
                    socketio.emit("chat", {"msgContent": "Nice choice!", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                    dataStore.shoes = image
                    dataStore.shoesSelected = True
            
            if category == "top":
                if dataStore.topSelected:
                    socketio.emit("chat", {"msgContent": "You already selected a top", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                else:
                    socketio.emit("chat", {"msgContent": "Nice choice!", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                    dataStore.top = image
                    dataStore.topSelected = True
            
            if category == "pants":
                if dataStore.pantsSelected:
                    socketio.emit("chat", {"msgContent": "You already selected pants", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                else:
                    socketio.emit("chat", {"msgContent": "Nice choice!", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                    dataStore.pants = image
                    dataStore.pantsSelected = True

            if dataStore.topSelected and dataStore.shoesSelected and dataStore.pantsSelected:
                socketio.emit("chat", {"msgContent": "Your final outfit:", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
                socketio.emit("chat", {"msgContent": dataStore.top, "msgTime": getTime(), "msgSender": "bot", "msgType": "image"}, broadcast = True)
                socketio.emit("chat", {"msgContent": dataStore.pants, "msgTime": getTime(), "msgSender": "bot", "msgType": "image"}, broadcast = True)
                socketio.emit("chat", {"msgContent": dataStore.shoes, "msgTime": getTime(), "msgSender": "bot", "msgType": "image"}, broadcast = True)

                # indicate end of recommendations
                socketio.emit("chat", {"msgContent": "I hope this outfit pleases you! 😇", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)

                
                #reset the dataStore
                reset()

                # artificial delay to make interaction seem more natural
                time.sleep(4)

                # ends the interaction (for now)
                socketio.emit("chat", {"msgContent": "If I should help you again, just provide me information about your plans for the day again 😊",
                            "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
            else:
                createOutfit()
                    

        else:
            time.sleep(1)
            socketio.emit("chat", {"msgContent": "Sorry, you cant chose options from a past conversation."
                                   + " If I should help you again, just provide me information about your plans for the day again 😊",
                            "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        

def createOutfit():
    if dataStore.topSelected == False and dataStore.topsPresented == False:

        dataStore.topsPresented = True
        # get similarity results for user text input
        result = similarity.getResults(dataStore.userInput, "top", top_results=3)
        #present the user the results
        socketio.emit("chat", {"msgContent": "My selection of tops 🧥 for you:", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        time.sleep(1)
        socketio.emit("chat", {"msgContent": result[0], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "top"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[1], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "top"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[2], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "top"}, broadcast = True)

        time.sleep(1)
        socketio.emit("chat", {"msgContent": "Just select one of the above ⬆️ by clicking on it 😎", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)   

    elif dataStore.pantsSelected == False and dataStore.pantsPresented == False:
        
        dataStore.pantsPresented = True
        # get similarity results for user text input
        result = similarity.getResults(dataStore.userInput, "pants", top_results=3)
        #present the user the results
        socketio.emit("chat", {"msgContent": "My selection of pants 👖 for you:", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        time.sleep(1)
        socketio.emit("chat", {"msgContent": result[0], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "pants"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[1], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "pants"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[2], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "pants"}, broadcast = True)

        time.sleep(1)
        socketio.emit("chat", {"msgContent": "Just select one of the above ⬆️ by clicking on it 😎", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)   

    elif dataStore.shoesSelected == False and dataStore.shoesPresented == False:

        dataStore.shoesPresented = True
        # get similarity results for user text input
        result = similarity.getResults(dataStore.userInput, "shoes", top_results=3)
        #present the user the results
        socketio.emit("chat", {"msgContent": "My selection of shoes 👞 for you:", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)
        time.sleep(1)
        socketio.emit("chat", {"msgContent": result[0], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "shoes"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[1], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "shoes"}, broadcast = True)
        socketio.emit("chat", {"msgContent": result[2], "msgTime": getTime(), "msgSender": "bot", "msgType": "selectableImage", "category": "shoes"}, broadcast = True)
        
        time.sleep(1)
        socketio.emit("chat", {"msgContent": "Just select one of the above ⬆️ by clicking on it 😎", "msgTime": getTime(), "msgSender": "bot", "msgType": "text"}, broadcast = True)   

        

# Reset all data to initial status
def reset():
    print("RESET")
    dataStore.messageCount = 0
    dataStore.userCategory = None
    dataStore.userInput = None
    dataStore.pants = None
    dataStore.top = None
    dataStore.shoes = None
    dataStore.topSelected = False
    dataStore.pantsSelected = False
    dataStore.shoesSelected = False
    dataStore.topsPresented = False
    dataStore.pantsPresented = False
    dataStore.shoesPresented = False

# Starts the App
if __name__ == "__main__":
    socketio.run(app)
