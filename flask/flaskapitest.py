import requests

url = "http://localhost:5000"  # replace with your URL
filepath = "D:/NLP/Toxic-Comment-Classification-Challenge-master/images/mixedimages/random.vehicle.audi.tt/ang0.02h3.17p-27.48dist9.33lshift-1.87color143,158,223.png"  # replace with your file path

with open(filepath, 'rb') as file:
    files = {'file': file}
    response = requests.post(url, files=files)

print(response.json())