from flask import Flask, render_template, session, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
metadata = (('authorization', 'Key 24f6926e2f1744aa8e83199cb554d8b0'),)

app = Flask(__name__)

upload_folder = "static/uploads"
allowed_extentions = set(['png', 'jpeg', 'jpg'])

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['SECRET_KEY'] = 'fjhasldkfjhasdflkhasdflkjh'

recyclable_objects = ["bottle", "cardboard", "glass", "plastic bottle", "plastic container", "cereal box",
                     "snack box", "phonebook", "magazine", "mail", "paper", "newspaper", "tin cans",
                      "aluminum can", "steel can", "food container", "jar", "soft drink bottle", "beer bottle",
                       "wine bottle", "liquor bottle", "carton", "aersol", "aersol can", "aluminum", "aluminum foil",
                       "aluminum tray", "stryrofoam", "stryrofoam packaging", "stryrofoam food container",
                        "stryrofoam drink container", "paper box", "pizza box", "paper bag", "shredded paper",
                        "plastic bucket", "plastic tubs", "plastic pot", "plastic tray", "plastic toy",
                         "plastic food container", "plastic cup", "metal can", "aluminum can", "wrapping paper",
                         "mail", "newspaper", "book"]

tech_objects = ["computer", "phone", "watch", "laptop", "eletronics", "tablet", 'iPad', 'iPhone', 'apple watch',
                'pc', 'personal computer', 'mac', 'ram', 'ram card', 'processor', 'mother board', 'screen',
                'display', 'monitor', 'calculator', 'speaker', 'kindle', 'key board', 'mouse', 'mice']

not_recycleable = ['plate', 'towel', 'napkin', 'metal bottle', 'plastic rap', 'food',
                    'ceramic', 'packing peanut', 'light bulb', 'photograph', 'wood', 'egg carton', 'metal water bottle',
                    'plastic wrap', 'egg carton', 'bulb']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extentions

def is_recyclable(detected_objects):
    for o in detected_objects:
        for r in recyclable_objects:
            if r in o:
                return True
    return False

def tech_is_recyclable(detected_objects):
    for o in detected_objects:
        for r in tech_objects:
            if r in o:
                return True
    return False

def is_not_recyclable(detected_objects):
    for o in detected_objects:
        for r in not_recycleable:
            if r in o:
                correct_results = o
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    completed = False
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('Please select a file.')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                position = upload_folder + "/" + filename
                with open(position, "rb") as file:
                    file_bytes = file.read()
                api_request = service_pb2.PostModelOutputsRequest(
                    model_id='aaa03c23b3724a16a56b629203edc62c',
                    inputs=[
                      resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes)))
                    ])
                response = stub.PostModelOutputs(api_request, metadata=metadata)
                if response.status.code != status_code_pb2.SUCCESS:
                    flash("API request failed")
                correct_results = []
                for concept in response.outputs[0].data.concepts:
                    value = round(concept.value * 100)
                    if value > 85:
                        correct_results.append(concept.name)
                percent_sure = "We are " + str((response.outputs[0].data.concepts[0].value)*100) + "% sure that your object is recyclable!"
                os.remove(position)
                if is_recyclable(correct_results):
                    recyclable = "Please recycle your object."
                    flash("Success! Press \"See results\" to see our analysis of your item.")
                    return render_template("index.html", recyclable=recyclable, percent_sure=percent_sure,
                     completed=True, isRecyclable=True)
                elif is_not_recyclable(correct_results):
                    recyclable = "Contrary to popular belief, your object is not recyclable."
                    flash("Success! Press \"See results\" to see our analysis of your item.")
                    return render_template("index.html", recyclable=recyclable, percent_sure=percent_sure,
                     completed=True, isRecyclable=False)
                elif tech_is_recyclable(correct_results):
                    recyclable = "Your object can be recycled at any technology recycling place, or your nearest Apple Store for free."
                    flash("Success! Press \"See results\" to see our analysis of your item.")
                    return render_template("index.html", recyclable=recyclable, percent_sure=percent_sure,
                     completed=True, isRecyclable=False)
                else:
                    flash("Success! Press \"See results\" to see our analysis of your item.")
                    recyclable = "Your object is not recyclable."
                    percent_sure = ""
                    return render_template("index.html", percent_sure=percent_sure,
                     recyclable=recyclable, completed=True, isRecyclable=False)
            else:
                flash("File type not supported. Please upload a png, jpg or a jpeg.")
        except:
            flash("Please try a different file.")
    return render_template("index.html", recyclable="", percent_sure="", completed=False, isRecyclable=False)

@app.route('/our-team')
def our_team():
    return render_template("our-team.html")

@app.route('/about-recycling')
def about_recycling():
    return render_template("about-recycling.html")

@app.route('/resources')
def resources():
    return render_template("resources.html")


if __name__ == "__main__":
    app.run(debug = True)
