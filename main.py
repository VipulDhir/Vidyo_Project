from flask import Flask
from flask_pymongo import PyMongo

app=Flask(__name__)

app.config['MONGO_URI']='mongodb+srv://<username>:<password>@cluster0.63f54ws.mongodb.net/users?retryWrites=true&w=majority'
mongo=PyMongo(app)


@app.route('/')
def home():
    return 'Welcome to my Vidyo project!'


from endpoints import *

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
