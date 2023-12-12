

import json
from flask import Flask, request, render_template, send_file
import cv2
from PIL import Image
import cv2
from ultralytics import YOLO
import numpy as np
from io import BytesIO
from fastbook import resnet50, load_learner

model=load_learner("resnet50_modelmixedimages.pkl")
classes = model.dls.vocab
print(classes)
# Import YOLOv8 library here

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process uploaded file
        file = request.files['file']
        
        image = cv2.imread(file)
        # Make a prediction using the model
        results = model.predict(image)
        
        # Return the result with confidence score
        data = {}
        predindex= results[1].tolist()
        predconfidences =  [ '%.4f' % elem for elem in results[2].tolist() ]  #round to 4 decimal places
        data['predicted'] = results[0]
        data['predicted_index'] = predindex
        data['predicted_confidence'] = predconfidences[predindex]
        data['all_confidences'] = predconfidences
        return json.dumps(data)
        
        # Convert the NumPy array to a PNG image
        # image = Image.fromarray(results[0].plot())
        # img_io = BytesIO()
        # image.save(img_io, 'JPEG', quality=100)
        # img_io.seek(0)
        # return send_file(img_io, mimetype='image/jpeg')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
