import awsgi
from flask import Flask
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET'])
@cross_origin()
def main():
    return {'message': 'Hello, world!'}


def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})