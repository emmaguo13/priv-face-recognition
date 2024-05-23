from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import cv2
from facenet_pytorch import MTCNN
from PIL import Image
import numpy as np
import torch
from torch.autograd import Variable
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

mtcnn = MTCNN(keep_all=False)

def ReadImage(base64_image):
    # Decode the base64 image
    image_data = base64.b64decode(base64_image.split(",")[1])
    img_pil = Image.open(BytesIO(image_data))
    
    # Detect and align the face
    aligned_face, prob = mtcnn(img_pil, return_prob=True)

    if aligned_face is not None:
        # Convert the tensor to a numpy array and change from CHW to HWC format
        aligned_face_np = aligned_face.permute(1, 2, 0).cpu().numpy()

        aligned_face_np = np.clip(aligned_face_np, 0, 1) * 255
        aligned_face_np = aligned_face_np.astype(np.uint8)
        
        # Convert the numpy array to BGR format expected by OpenCV
        aligned_face_bgr = cv2.cvtColor(aligned_face_np, cv2.COLOR_RGB2BGR)
        
        # Resize the image to 96x96 pixels (OpenFace input size)
        resized_face = cv2.resize(aligned_face_bgr, (96, 96))
        
        # Normalize the pixel values
        resized_face = resized_face.astype(np.float32) / 255.0
        
        # Convert to PyTorch tensor and change from HWC to CHW format
        aligned_face_tensor = torch.tensor(resized_face).permute(2, 0, 1).float()
        
        return aligned_face_tensor.unsqueeze(0)  # Add batch dimension
    else:
        print("No face detected")
        return None

def process_image(base64_imgs):
    # must take in 2 images

    imgs = []
    for image in base64_imgs:
        img_tensor = ReadImage(image)
        if img_tensor is not None:
            imgs.append(img_tensor)

    if len(imgs) == 2:
        I_ = torch.cat(imgs, 0)
        I_ = Variable(I_, requires_grad=False)

        data_array = (I_.detach().numpy()).reshape([-1]).tolist()
        data = dict(input_data=[data_array])

        return data
    else:
        return {"error": "Two images are required"}

@app.route('/process_images', methods=['POST'])
@cross_origin(origin='*')
def process_images():
    data = request.json
    base64_imgs = data.get('images')
    if not base64_imgs or len(base64_imgs) != 2:
        return jsonify({"error": "Exactly two base64 encoded images are required"}), 400

    result = process_image(base64_imgs)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)