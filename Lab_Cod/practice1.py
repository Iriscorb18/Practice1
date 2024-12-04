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

@app.post("/modify-chroma-subsampling/")
async def modify_chroma_subsampling(file: UploadFile = File(...), pix_fmt: str = "yuv420p"):
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

     # Define the output file path
    output_file_name = f"chroma_{pix_fmt}_{file.filename}"  # Descriptive name
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    colorconversor.chroma_subsampling_ffmpeg(input_file_path, output_file_path, pix_fmt)

    host_url = "http://localhost:8000"
    file_url = f"{host_url}/output_images/{output_file_name}"

    os.remove(input_file_path)

    return {
        "message": f"Chroma subsampling modified to {pix_fmt} successfully",
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

@app.post("/video_info/")
async def video_info(file: UploadFile = File(...)):
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Get video info using ffprobe
    video_info = colorconversor.extract_video_info(input_file_path)
    
    # Delete the temporary video file after extraction
    os.remove(input_file_path)
    
    if video_info:
        return {
            "message": "Video information retrieved successfully",
            "video_info": video_info
        }
    

@app.post("/process-bbb-full/")
async def process_bbb_full(file: UploadFile = File(...)):
    
    
    # Save uploaded file temporarily
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    
    video_file_name = f"20s_{file.filename}"  #Prefix
    video_output_path = os.path.join(OUTPUT_DIR, video_file_name)

    audio_output_aac_name = f"audio_aac_{file.filename}"
    audio_output_aac_path = os.path.join(OUTPUT_DIR, audio_output_aac_name)

    audio_output_mp3_name = f"audio_mp3_{file.filename}"
    audio_output_mp3_path = os.path.join(OUTPUT_DIR, audio_output_mp3_name)

    audio_output_ac3_name = f"audio_ac3_{file.filename}"
    audio_output_ac3_path = os.path.join(OUTPUT_DIR, audio_output_ac3_name)

    final_output_name = f"final_{file.filename}"
    final_output_path = os.path.join(OUTPUT_DIR, final_output_name)

        # Step 1: Cut the video to 20 seconds
    colorconversor.cut_video(input_file_path, video_output_path)

        # Step 2: Extract audio as AAC mono
    colorconversor.extract_audio_aac(input_file_path, audio_output_aac_path)

        # Step 3: Extract audio as MP3 stereo with lower bitrate
    colorconversor.extract_audio_mp3(input_file_path, audio_output_mp3_path)

        # Step 4: Extract audio as AC3 codec
    colorconversor.extract_audio_ac3(input_file_path, audio_output_ac3_path)

        # Step 5: Package video and audio into final MP4 container
    colorconversor.package_video_audio(video_output_path, audio_output_aac_path, audio_output_mp3_path, audio_output_ac3_path, final_output_path)

        # Return the paths of the generated files
    host_url = "http://localhost:8000"  # Adjust this if your server address changes
    video_url = f"{host_url}/output_images/{video_file_name}"
    aac_url = f"{host_url}/output_images/{audio_output_aac_name}"
    mp3_url = f"{host_url}/output_images/{audio_output_mp3_name}"
    ac3_url = f"{host_url}/output_images/{audio_output_ac3_name}"
    final_url = f"{host_url}/output_images/{final_output_name}"
    return {
            "message": "Video and audio processed successfully",
            "video_output_url": video_url,
            "audio_aac_output_url": aac_url,
            "audio_mp3_output_url": mp3_url,
            "audio_ac3_output_url": ac3_url,
            "final_video_url": final_url
    }


@app.post("/get-tracks/")
async def get_tracks(file: UploadFile = File(...)):

    # Save the uploaded file temporarily
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    track_count = colorconversor.count_tracks_in_mp4(input_file_path)

    return {
        "message": "MP4 container analyzed successfully.",
        "file_name": file.filename,
        "track_count": track_count
    }

@app.post("/visualize-motion/")
async def visualize_motion(file: UploadFile = File(...)):
    
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    output_file_name = f"motion_{file.filename}"  #Prefix
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    colorconversor.visualize_vectors(input_file_path, output_file_path)

    host_url = "http://localhost:8000"  # Update with your actual host URL
    image_url = f"{host_url}/output_images/{output_file_name}"

    #Delete the temporary input file
    os.remove(input_file_path)
    return {
        "message": "Motion vectors and macroblocks visualized successfully.",
        "output_video_url": image_url
    }

@app.post("/yuv-histogram/")
async def yuv_histogram(file: UploadFile = File(...)):

    # Save the uploaded file temporarily
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Define output file path
    output_file_path = os.path.join(OUTPUT_DIR, f"yuv_histogram_{file.filename}")

    # Generate video with YUV histogram
    colorconversor.generate_yuv_histogram(input_file_path, output_file_path)

    host_url = "http://localhost:8000"  # Update with your actual host URL
    image_url = f"{host_url}/output_images/{output_file_path}"

    #Delete the temporary input file
    os.remove(input_file_path)
    return {
        "message": "YUV histogram generated successfully.",
        "output_video_url": image_url
    }




