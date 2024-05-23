import cv2
from facenet_pytorch import MTCNN
from PIL import Image
import numpy
import torch
from torch.autograd import Variable
import base64
from io import BytesIO

mtcnn = MTCNN(keep_all=False)

def ReadImage(base64_image):
    # Decode the base64 image
    image_data = base64.b64decode(base64_image.split(",")[1])
    img_pil = Image.open(BytesIO(image_data))
    
    # Convert the image to RGB (PIL default is already RGB)
    img_rgb = numpy.array(img_pil)
    
    # Convert the RGB image to BGR for OpenCV
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    
    # Convert the image from BGR to RGB for further processing
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image format
    img_pil = Image.fromarray(img_rgb)
    
    # Detect and align the face
    aligned_face, prob = mtcnn(img_pil, return_prob=True)

    if aligned_face is not None:
        # Convert the tensor to a numpy array and change from CHW to HWC format
        aligned_face_np = aligned_face.permute(1, 2, 0).cpu().numpy()

        aligned_face_np = numpy.clip(aligned_face_np, 0, 1) * 255
        aligned_face_np = aligned_face_np.astype(numpy.uint8)
        
        # Convert the numpy array to BGR format expected by OpenCV
        aligned_face_bgr = cv2.cvtColor(aligned_face_np, cv2.COLOR_RGB2BGR)
        
        # Resize the image to 96x96 pixels (OpenFace input size)
        resized_face = cv2.resize(aligned_face_bgr, (96, 96))
        
        # Normalize the pixel values
        resized_face = resized_face.astype(numpy.float32) / 255.0
        
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
        imgs.append(ReadImage(image))

    I_ = torch.cat(imgs, 0)
    I_ = Variable(I_, requires_grad=False)

    data_array = (I_.detach().numpy()).reshape([-1]).tolist()
    data = dict(input_data = [data_array])

    return data


