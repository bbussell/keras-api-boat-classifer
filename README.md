# A Keras + Deep Learning API for the classification of marine boats

This was developed using Python 3.7 and will requre Python 3.7 or later to work.

You will require Keras and a Tensorflow backend installed on your system, as well as the packages detailed in the requirements.txt file. 

To install the requrements file, go to the working directory and run:

```sh
$ pip install -r requirements.txt
```

## Starting the Keras server

The Flask + Keras server can be started by running:

```sh
$ python run_keras_server.py
Using TensorFlow backend.
 * Loading Keras model and Flask starting server...please wait until server has fully started
...
 * Running on http://127.0.0.1:5000
```

You can now access the REST API via `http://127.0.0.1:5000`.

## Submitting requests to the Keras server

Here is an example image we wish to classify, a sailing yacht: boat.jpg

Requests can be submitted via the url `http://127.0.0.1:5000`, where you will be required to enter one or more image files. 

OR,

Requests can be submitted via cURL:

```sh
$ curl -X POST -F image=@boat.jpg 'http://localhost:5000/predict'

```
## Accessing requests and responses in the database 

The API automatically populates a database in the working directory : pythonsqlite.db

To access this database use a command line and sqlite3 to access the tables and data using SQL syntax. 

For example:

```sh

$ sqlite3 pythonsqlite.db
  SQLite version 3.33.0 2020-08-14 13:23:32
  Enter ".help" for usage hints.
$ sqlite> .tables
  Boat_API_Responses
$ sqlite> SELECT * from Boat_API_Responses;
1|C:\images//boat3.jpg|gondola|2021-05-08|22-03-12
2|C:\images//boat.jpg|gondola|2021-05-08|22-08-27

```



