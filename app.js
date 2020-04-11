//Initilize the Clarifai App
const Clarifai = require('clarifai')
const app = new Clarifai.App({
    apiKey: '86481bac6d0847dba50601141a7dba8d'
})

//Send and Recieve Data from Clarifai
async function getData(url) {
  return await app.models.predict(Clarifai.GENERAL_MODEL, url)
}

//Access Completed Data from Clarifiai Predict
async function placeData(img_url) {
  const response = await getData(img_url)
  //Access the Possibilities from the Data
  const data = response.outputs[0].data.concepts
  //Itterate Through the Data and Add Instances With a Probability Higher or Equal to 95%
  var results = []
  for (const item in data) {
    if (Math.round(data[item].value * 100) >= 95) {
      results.push([data[item].name, Math.round(data[item].value * 100)])
    }
  }
  var image_objects = []
  for (const itteration in results) {
    image_objects.push(results[itteration][0])
  }
  console.log("Possible Results:")
  console.log(results)
  console.log(image_objects)
  console.log(isRecycleable(image_objects))
}

//Function to Check if An Item is Recycleable
var objects = ["bottle", "cardboard", "glass", "plastic bottles", "plastic containers", "cereal boxes", "snack boxes", "phonebooks", "magazines", "mail", "paper", "newspaper", "tin cans", "aluminum cans", "steel cans", "food containers", "jars", "soft drink bottles", "beer bottles", "wine bottles", "liquor bottles"];
function isRecycleable(listed_objects) {
  for (const object in listed_objects) {
    if (objects.includes(listed_objects[object])) {
      return "Please Recycle This Object!"
    }
  }
  return "Do Not Recycle This Object!"
}

// placeData("https://webstore.cdlusa.net/content/images/thumbs/0002614_glass-bottle-whisky-spirit-1l-cs12_550.jpeg")

//List of Objects That Are Recycleable

//Setup Certain Node Variables
const http = require("http");
const fs = require("fs");
const bodyParser = require('body-parser');
const express = require('express');
const multer = require('multer');

//Create App
const expressApp = express();
const port = process.env.PORT || 3000;
expressApp.use(bodyParser.urlencoded({extended:false}));
expressApp.use(bodyParser.json());
expressApp.use('/', express.static(__dirname + '/public'));
fs.readFile('./index.html', function (err, html) {
  if (err) {
    throw err;
  }
  http.createServer(function(request, response) {
    response.writeHeader(200, {"Content-Type": "text/html"});
    response.write(html);
    response.end();
  }).listen(process.env.PORT);
});

//Create Multer Config to save photos to temporary server storage
const multerConfig = {
  //Specify Disk Storage
  storage: multer.diskStorage({
    //Specifiy Destination
    destination: function(req, file, next){
      next(null, './public/photo-storage');
    },
    //Specify Filename
    filename: function(req, file, next){
      const ext = file.mimetype.split('/')[1];
      next(null, file.fieldname + '-' + Date.now() + '.'+ext);
    }
  }),
  //Filter Out Non-Images
  fileFilter: function(req, file, next){
    if(!file){
      next();
    }
    const image = file.mimetype.startsWith('image/');
    if(image){
      console.log('Photo Uploaded');
      next(null, true);
    } else {
      console.log("File Not Supported")
      return next();
    }
  }
};

//Routes
expressApp.get('/', function(req, res){
  res.sendfile(__dirname + '/index.html');
});
expressApp.post('/', multer(multerConfig).single('photo'),function(req, res){
  placeData("https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2F3.bp.blogspot.com%2F-pjqbkr1RHkw%2FT9yib919iCI%2FAAAAAAAABCQ%2FB41ubUgapZ4%2Fs1600%2FBurberry-Classic-Streak-Men-Shirt-MB8h.jpg&f=1&nofb=1")
  res.sendfile(__dirname + "/index.html")
  // res.send('Complete! Check out your public/photo-storage folder.  Please note that files not encoded with an image mimetype are rejected. <a href="index.html">try again</a>');
});
expressApp.get('/about-recycling', function(req, res){
  res.sendfile(__dirname + "/about-recycling.html")
});
expressApp.get('/our-team', function(req, res){
  res.sendfile(__dirname + "/our-team.html")
});
expressApp.get('/resources', function(req, res){
    res.sendfile(__dirname + "/resources.html")
});

//Run Sever
expressApp.listen(port,function() {
  console.log(`Server listening on port ${port}`);
});
