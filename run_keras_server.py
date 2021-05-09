# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'

# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from keras.models import load_model
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import flask
from flask import Flask, request, render_template
import io
import os
import sqlite3
from sqlite3 import Error
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# initialize our Flask application and the Keras model
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD FOLDER'] = 'static/images/'

# Initialize database
DATABASE = "pythonsqlite.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


# create a database connection
def create_table(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :return:
    """
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS Boat_API_Responses (
                                            id integer PRIMARY KEY,
                                            image text NOT NULL,
                                            prediction text NOT NULL,
                                            begin_date text,
                                            end_date text
                                        ); """
    try:
        c = conn.cursor()
        c.execute(sql_create_projects_table)
    except Error as e:
        print(e)


def insert_data(project):
    """
    Create a new project into the projects table
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO Boat_API_Responses(image,prediction,begin_date,end_date)
              VALUES(?,?,?,?) '''
    conn = create_connection(DATABASE)
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid


def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image


# return predict()
# return send_from_directory("uploads",filename,as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():
    target = app.config['UPLOAD FOLDER']
    print(target)  # debugging

    if not os.path.isdir(target):
        os.mkdir(target)
    # initialize the data dictionary that will be returned from the view
    # if flask.request.files.get("file"):

    classification_results = []
    if request.files['file'].filename == '':
        return 'No File Selected'
    for image_file in request.files.getlist("file"):  # returns list of filenames
        data = {"success": False}
        # if flask.request.files.get("image"):

        print(image_file)
        filename = secure_filename(image_file.filename)
        destination = "/".join([target, filename])
        print(destination)
        image_file.save(destination)
        # Reading in image to PIL format

        # image = flask.request.files["image"].read()
        # image = Image.open(io.BytesIO(image_file))
        image = Image.open(destination)
        image = prepare_image(image, target=(150, 150))
        # classify the input image and then initialize the list
        # of predictions to return to the client
        preds = model.predict(image)
        pred_digits = np.argmax(preds, axis=1)

        # results = imagenet_utils.decode_predictions(preds)
        data["predictions"] = []
        labels = {"buoy": 0, "cruise ship": 1, "ferry": 2, "freight ship": 3, "gondola": 4, "inflatable boat": 5,
                  "kayak": 6, "paper boat": 7, "sailing yacht": 8}
        labels_list = list(labels)
        # loop over the results and add them to the list of returned predictions

        results = {"label": labels_list[pred_digits[0]], "probability": float(pred_digits[0])}
        data["predictions"].append(results)

        # indicate that the request was a success
        data["success"] = True

        # updating database
        datestring = datetime.strftime(datetime.now(), "%Y-%m-%d")
        timestring = datetime.strftime(datetime.now(), "%H-%M-%S")

        # create a new project
        project = (destination, results["label"], datestring, timestring)
        create_connection(DATABASE)
        insert_data(project)

        # prediction = predict_class(image, data)

        # prediction = flask.jsonify(data)
        data['filename'] = filename
        classification_results.append(data)

    return render_template("complete.html", results=classification_results)


# Predict API
@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint

    if flask.request.files.get("image"):
        image = flask.request.files["image"].read()
        image = Image.open(io.BytesIO(image))

        # preprocess the image and prepare it for classification
        image = prepare_image(image, target=(150, 150))
        preds = model.predict(image)
        pred_digits = np.argmax(preds, axis=1)
        # s = imagenet_utils.decode_predictions(preds)
        data["predictions"] = []
        labels = {"buoy": 0, "cruise ship": 1, "ferry": 2, "freight ship": 3, "gondola": 4, "inflatable boat": 5,
                  "kayak": 6, "paper boat": 7, "sailing yacht": 8}
        labels_list = list(labels)
        # loop over the results and add them to the list of
        # returned predictions

        r = {"label": labels_list[pred_digits[0]], "probability": float(pred_digits[0])}
        data["predictions"].append(r)

        # indicate that the request was a success
        data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)


@app.route('/', methods=['GET'])
def index():
    return render_template('upload_file.html')
    # return '''<h1>Boat Image Classifer</h1>


# <p>A prototype API for classifying images of different types of boat</p>'''

# if this is the main thread of execution first load the model and
# then start the server

if __name__ == "__main__":
    print("* Loading Keras model and Flask starting server..."
          "please wait until server has fully started")
    model = load_model('boat_classification_model.h5')
    print("Model Fully Loaded.")
    print("Loading database connection...")
    connection = create_connection(DATABASE)
    create_table(connection)
    print("Database loaded")
    app.run(debug=False)
