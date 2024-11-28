from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles  # Correct import for StaticFiles
from seminar1 import colorconversor, DCT_coding, wavelet_coding
import numpy as np
import io
import uuid
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import shutil
import subprocess
from PIL import Image
import logging
import os



app = FastAPI()

# # Color Conversion Endpoints
# @app.get("/rgb_to_yuv/")
# async def rgb_to_yuv(R: int, G: int, B: int):
#     Y, U, V = colorconversor.rgb_to_yuv(R, G, B)
#     return {"Y": Y, "U": U, "V": V}

# @app.get("/yuv_to_rgb/")
# async def yuv_to_rgb(Y: float, U: float, V: float):
#     R, G, B = colorconversor.yuv_to_rgb(Y, U, V)
#     return {"R": R, "G": G, "B": B}

#Directory to save generated images
OUTPUT_DIR = "output_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Create the directory if it doesn't exist
#Mount the directory 
app.mount("/output_images", StaticFiles(directory=OUTPUT_DIR), name="output_images")

@app.post("/modify-chroma/")
async def modify_chroma(file: UploadFile = File(...), subsampling: str = "yuv420p"):

    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    output_file_name = f"chroma_{subsampling}_{file.filename}"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    colorconversor.chroma_subsampling_ffmpeg(input_file_path, output_file_path, subsampling)

    host_url = "http://localhost:8000"
    file_url = f"{host_url}/output_images/{output_file_name}"

    os.remove(input_file_path)

    return {
        "message": f"Chroma subsampling modified to {subsampling} successfully",
        "file_url": file_url,
    }

# DCT Encoding Endpoints
@app.post("/dct_encode/")
async def dct_encode(file: UploadFile = File(...)):
    

    image = Image.open(io.BytesIO(await file.read()))

    encoded = DCT_coding.encoding_DCT(image)
    
    encoded_normalized = (encoded - encoded.min()) / (encoded.max() - encoded.min())

    output_file = os.path.join(OUTPUT_DIR, "encoded_image.jpeg")
    plt.imsave(output_file, encoded_normalized)
    host_url = "http://localhost:8000" 
    image_url = f"{host_url}/output_images/encoded_image.jpeg"
        
    return {"message": "DCT encoded image generated successfully", "image_url": image_url}


@app.post("/dct_decode/")
async def dct_decode(file: UploadFile = File(...)):
  
    image = Image.open(io.BytesIO(await file.read()))
    decoded = DCT_coding.encoding_DCT(image)
    
    decoded_normalized = (decoded - decoded.min()) / (decoded.max() - decoded.min())

    output_file = os.path.join(OUTPUT_DIR, "decoded_image.jpeg")
    plt.imsave(output_file, decoded_normalized)

    host_url = "http://localhost:8000" 
    image_url = f"{host_url}/output_images/decoded_image.jpeg"
        
    return {"message": "DCT encoded image generated successfully", "image_url": image_url}

 

# Wavelet Generation Endpoint
@app.post("/wavelet/")
async def wavelet(file: UploadFile = File(...), wavelet: str = 'haar', level: int = 1):
  # Read and process the uploaded image
    image = Image.open(io.BytesIO(await file.read()))  # Convert to grayscale

    coeffs = wavelet_coding.generate_wavelet(image, wavelet, level)

      
    output_file = os.path.join(OUTPUT_DIR, "wavelet_image.jpeg")
    wavelet_coding.plot_coefficients(coeffs)  # Plot the coefficients
 
    plt.savefig(output_file)


    host_url = "http://localhost:8000"
    image_url = f"{host_url}/output_images/wavelet_image.jpeg"
        
    return {"message": "Wavelet transformed image generated successfully", "image_url": image_url}

# Endpoint for resizing the image
@app.post("/resize-image/")
async def resize_image(file: UploadFile = File(...), width: int = 200, height: int = 200):
      
    
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)


    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    output_file_name = f"resized_{width}x{height}_{file.filename}"  
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    colorconversor.resize_image_ffmpeg(input_file_path, output_file_path, width, height)

    host_url = "http://localhost:8000"
    image_url = f"{host_url}/output_images/{output_file_name}"

    #Delete the temporary input file
    os.remove(input_file_path)

    return {
        "message": "Image resized successfully",
        "image_url": image_url,
    }

@app.post("/blackwhite-image/")
async def blackwhite_image(file: UploadFile = File(...)):

        input_file_path = os.path.join(OUTPUT_DIR, file.filename)
        with open(input_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        output_file_name = f"bw_{file.filename}"  #Prefix
        output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

        colorconversor.blackwhite_image_ffmpeg(input_file_path, output_file_path)

        host_url = "http://localhost:8000"
        image_url = f"{host_url}/output_images/{output_file_name}"

        os.remove(input_file_path)

        return {
            "message": "Image converted to black and white successfully",
            "image_url": image_url,
        }

