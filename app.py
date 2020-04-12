from flask import Flask, render_template, session, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

app = Flask(__name__)

upload_folder = "static/uploads"
allowed_extentions = set(['png', 'jpeg', 'jpg'])

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['SECRET_KEY'] = 'fjhasldkfjhasdflkhasdflkjh'

mlApp = ClarifaiApp(api_key='86481bac6d0847dba50601141a7dba8d')
model = mlApp.public_models.general_model

recyclable_objects = ["bottle", "metal bottle", "cardboard", "glass", "plastic bottle", "plastic container", "cereal box",
                     "snack box", "phonebook", "magazine", "mail", "paper", "newspaper", "tin cans",
                      "aluminum can", "steel can", "food container", "jar", "soft drink bottle", "beer bottle",
                       "wine bottle", "liquor bottle", "carton", "aersol", "aersol can", "aluminum", "aluminum foil",
                       "aluminum tray", "stryrofoam", "stryrofoam packaging", "stryrofoam food container",
                        "stryrofoam drink container", "paper box", "pizza box", "paper bag", "shredded paper",
                        "plastic bucket", "plastic tubs", "plastic pot", "plastic tray", "plastic toy",
                         "plastic food container", "plastic cup", "metal can", "aluminum can", "wrapping paper",
                         "mail", "newspaper", "book"]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extentions

def is_recyclable(detected_objects):
    for o in detected_objects:
        for r in recyclable_objects:
            if r in o:
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
                img = ClImage(filename=position)
                response = model.predict([img])
                results = response["outputs"][0]["data"]["concepts"]
                correct_results = []
                for i in results:
                    name = i["name"]
                    value = round((i["value"]) * 100)
                    if (value > 95):
                        correct_results.append(name)
                percent_sure = "We are " + str(response["outputs"][0]["data"]["concepts"][0]["value"]*100) + "% sure that your object is recyclable!"
                os.remove(position)
                if is_recyclable(correct_results):
                    recyclable = "Please recycle your object."
                    flash("Success! Press \"See results\" to see our analysis of your item.")
                    return render_template("index.html", recyclable=recyclable, percent_sure=percent_sure,
                     completed=True, isRecyclable=True)
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
    app.run()
