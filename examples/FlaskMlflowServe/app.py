'''
Created on 13-Feb-2020

@author: srinivasan
'''
from flask import Flask, request, jsonify, render_template
import os
import pickle

import numpy as np

model_path = os.path.join(os.environ['MODEL_PATH'], 'model.pkl')
# model_path = 'model/model.pkl'
app = Flask(__name__)
model = pickle.load(open(model_path, 'rb'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    int_features = [float(x) for x in 
                    request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    output = round(prediction[0], 2)
    return render_template('index.html',
                           prediction_text='Wine Quantity should be {}'.format(output))


@app.route('/predict_new', methods=['POST'])
def predict_result():
    print(request.get_json())
    data = request.get_json()
    out = model.predict(data)
    return jsonify(out=out,
                    status='success')


@app.route('/results', methods=['POST'])
def results():
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])
    output = prediction[0]
    return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9791)
    
