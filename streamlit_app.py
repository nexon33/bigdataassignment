import json
import streamlit as st
import os
from PIL import Image
import torch
from torchvision import models, transforms
from fastbook import resnet50, load_learner
import pathlib
import platform
plt = platform.system()
if plt == 'Linux': pathlib.WindowsPath = pathlib.PosixPath
    
# Function to load a limited number of images from a given folder
def load_images(folder, start_idx, end_idx):
    images = []
    for i, filename in enumerate(os.listdir(folder)):
        if start_idx <= i < end_idx and (filename.endswith('.jpg') or filename.endswith('.png')):
            img_path = os.path.join(folder, filename)
            images.append(img_path)
    return images

# Function to load a pre-saved PyTorch model
def load_pretrained_model(model_path):
    model = load_learner(model_path)
    # model = models.resnet50(pretrained=True )  # Initialize an empty ResNet model
    # resnet50.
    # state_dict = torch.load(model_path)
    
    # # Map the keys from the loaded state dictionary to the ResNet model's state_dict
    # mapped_state_dict = {}
    # for key, value in state_dict.items():
    #     if key.startswith("model."):  # Adjust this prefix based on your saved model structure
    #         mapped_state_dict[key[len("model.") :]] = value
    # model.load_state_dict(mapped_state_dict)

    # model.eval()
    return model

# Streamlit UI Components
def main():
    st.title('Image Data Explorer')

    # Dropdown to select the class
    class_option = st.sidebar.selectbox(
        'Select Class', ('random.vehicle.volkswagen.t2', 'random.vehicle.audi.a2', 'random.vehicle.audi.etron', 'random.vehicle.audi.tt', 'random.vehicle.volkswagen.t2_2021')
    )

    # Load images from the selected class
    folder_path = f'images/mixedimages/{class_option}'

    # Pagination
    total_images = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
    images_per_page = 10
    page_number = st.sidebar.number_input(label="Page Number", min_value=1, max_value=(total_images // images_per_page) + 1, value=1)
    start_idx = (page_number - 1) * images_per_page
    end_idx = start_idx + images_per_page

    # Load images from the selected class
    images = load_images(folder_path, start_idx, end_idx)

    # Display images
    for img_path in images:
        image = Image.open(img_path)
        st.image(image, caption=os.path.basename(img_path), use_column_width=True)

    # Dataset Information
    st.sidebar.subheader("Dataset Information:")
    st.sidebar.text(f"Total Images in {class_option}: {total_images}")

    # Test Pre-Saved Model
    st.sidebar.subheader("Test Pre-Saved Model:")
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        # Load pre-trained model
        model_path = "resnet50_modelmixedimages.pkl"
        model = load_pretrained_model(model_path)

        # Preprocess the uploaded image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),

            # Normalize the image according to the ImageNet standards
            # transforms.ToTensor(),
            # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            # transforms.ToPILImage()
        ])
        #convert to RGB to get rid of alpha channel
        image = Image.open(uploaded_file).convert('RGB')
        results = model.predict(transform(image))

        # Print the predicted class
        data = {}
        predindex= results[1].tolist()
        predconfidences =  [ '%.4f' % elem for elem in results[2].tolist() ]  #round to 4 decimal places
        data['predicted'] = results[0]
        data['predicted_index'] = predindex
        data['predicted_confidence'] = predconfidences[predindex]
        data['all_confidences'] = predconfidences
        
        st.sidebar.text(f"\"prediction\": {json.dumps(data, indent=4)}")

if __name__ == '__main__':
    main()
