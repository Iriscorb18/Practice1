from fastapi import FastAPI, File, UploadFile, Query
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
  # Save the uploaded file to the server
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Load the image (grayscale conversion)
    image = Image.open(input_file_path).convert("L")
    image_array = np.array(image)
    


    # Generate wavelet coefficients
    coeffs = wavelet_coding.generate_wavelet(image_array, wavelet, level)

    # Plot and save the transformed output image
    output_file_name = f"wavelet_{wavelet}_level{level}_{file.filename}"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)
    
    # Plot the wavelet coefficients and save the image
    wavelet_coding.plot_coefficients(coeffs)  
    plt.savefig(output_file_path)

    # Construct URL for the output file
    host_url = "http://localhost:8000"
    image_url = f"{host_url}/output_images/{output_file_name}"

    return {
        "message": "Wavelet transformed image generated successfully",
        "image_url": image_url
        }

# Endpoint for resizing the image
@app.post("/resize-image/")
async def resize_image(width: int, height: int, file: UploadFile = File(...)):
      
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
    print(f"Width received: {width}, Height received: {height}")

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
    video_info = colorconversor.extract_video_info(input_file_path)
    
    os.remove(input_file_path)
    
    if video_info:
        return {
            "message": "Video information retrieved successfully",
            "video_info": video_info
        }
    

@app.post("/process-bbb-full/")
async def process_bbb_full(file: UploadFile = File(...)):
    
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

    colorconversor.cut_video(input_file_path, video_output_path)
    colorconversor.extract_audio_aac(input_file_path, audio_output_aac_path)
    colorconversor.extract_audio_mp3(input_file_path, audio_output_mp3_path)
    colorconversor.extract_audio_ac3(input_file_path, audio_output_ac3_path)
    colorconversor.package_video_audio(video_output_path, audio_output_aac_path, audio_output_mp3_path, audio_output_ac3_path, final_output_path)


    host_url = "http://localhost:8000" 
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
    
    # Save the uploaded file to the output directory
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Prepare output file path
    output_file_name = f"motion_{file.filename}"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    print(f"Input file path: {input_file_path}")
    print(f"Output file path: {output_file_path}")
        
    colorconversor.visualize_vectors(input_file_path, output_file_path)
  
    # Construct the output video URL
    host_url = "http://localhost:8000"  # Make sure this is correct
    image_url = f"{host_url}/output_images/{output_file_name}"

    print(f"Generated video URL: {image_url}")

    # Optionally remove the uploaded input file after processing
    os.remove(input_file_path)

    # Return the output video URL
    return {
        "message": "Motion vectors and macroblocks visualized successfully.",
        "output_video_url": image_url
    }
@app.post("/yuv-histogram/")
async def yuv_histogram(file: UploadFile = File(...)):

    # Save the uploaded file to the output directory
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Prepare output file path
    output_file_name = f"yuvHistogram_{file.filename}"
    output_file_path = os.path.join(OUTPUT_DIR, output_file_name)

    print(f"Input file path: {input_file_path}")
    print(f"Output file path: {output_file_path}")


    colorconversor.generate_yuv_histogram(input_file_path, output_file_path)
    # Construct the output video URL
    host_url = "http://localhost:8000"  # Make sure this is correct
    image_url = f"{host_url}/output_images/{output_file_name}"

    print(f"Generated video URL: {image_url}")

    # Optionally remove the uploaded input file after processing
    os.remove(input_file_path)

     
    return {
        "message": "YUV histogram generated successfully.",
        "output_video_url": image_url
    }

@app.post("/convert-video/")
async def convert_video(file: UploadFile = File(...)):

    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

 
    base_name = os.path.splitext(file.filename)[0]
    vp8_name = f"{base_name}_vp8.webm"
    output_vp8 = os.path.join(OUTPUT_DIR, vp8_name)
    vp9_name = f"{base_name}_vp9.webm"
    output_vp9 = os.path.join(OUTPUT_DIR, vp9_name)
    h265_name = f"{base_name}_h265.mp4"
    output_h265 = os.path.join(OUTPUT_DIR, h265_name)
    av1_name = f"{base_name}_av1.mkv"
    output_av1 = os.path.join(OUTPUT_DIR, av1_name)

    colorconversor.vp8_change(input_file_path, output_vp8)
    colorconversor.vp9_change(input_file_path, output_vp9)
    colorconversor.h265_change(input_file_path, output_h265)
    colorconversor.av1_change(input_file_path, output_av1)

    
    os.remove(input_file_path)

   
    host_url = "http://localhost:8000"
    vp8_url = f"{host_url}/output_images/{vp8_name}"
    vp9_url = f"{host_url}/output_images/{vp9_name}"
    h265_url = f"{host_url}/output_images/{h265_name}"
    av1_url = f"{host_url}/output_images/{av1_name}"

    return {
        "message": "Video conversion completed",
     
        "VP8": vp8_url,
        "VP9": vp9_url,
        "H265": h265_url,
        "AV1": av1_url  
    }
@app.post("/encoding-ladder/")
async def generate_encoding_ladder(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

      # Process encoding ladder one by one
    output_urls = {}
    host_url = "http://localhost:8000"
    base_name = os.path.splitext(file.filename)[0]

    vp8_name = f"{base_name}_vp8.webm"
    output_vp8 = os.path.join(OUTPUT_DIR, vp8_name)
    # Entry 1: 240p
    resolution_240p = "240"
    bitrate_240p = "500k"
    output_file_name_240p = f"{base_name}_240p.mp4"
    output_file_path_240p = os.path.join(OUTPUT_DIR, output_file_name_240p)

    colorconversor.encode_video(input_file_path, output_file_path_240p, resolution_240p, bitrate_240p)
    resolution_240p_url = f"{host_url}/output_images/{output_file_name_240p}"

    # Entry 2: 360p
    resolution_360p = "360"
    bitrate_360p = "800k"
    output_file_name_360p =  f"{base_name}_360p.mp4"
    output_file_path_360p = os.path.join(OUTPUT_DIR, output_file_name_360p)

    colorconversor.encode_video(input_file_path, output_file_path_360p, resolution_360p, bitrate_360p)
    resolution_360p_url = f"{host_url}/output_images/{output_file_name_360p}"

    # Entry 3: 480p
    resolution_480p = "480"
    bitrate_480p = "1500k"
    output_file_name_480p = f"{base_name}_480p.mp4"
    output_file_path_480p = os.path.join(OUTPUT_DIR, output_file_name_480p)

    colorconversor.encode_video(input_file_path, output_file_path_480p, resolution_480p, bitrate_480p)
    resolution_480p_url  = f"{host_url}/output_images/{output_file_name_480p}"

    # Entry 4: 720p
    resolution_720p = "720"
    bitrate_720p = "3000k"
    output_file_name_720p =  f"{base_name}_720p.mp4"
    output_file_path_720p = os.path.join(OUTPUT_DIR, output_file_name_720p)

    colorconversor.encode_video(input_file_path, output_file_path_720p, resolution_720p, bitrate_720p)
    resolution_720p_url = f"{host_url}/output_images/{output_file_name_720p}"

    # Entry 5: 1080p
    resolution_1080p = "1080"
    bitrate_1080p = "5000k"
    output_file_name_1080p =  f"{base_name}_1080p.mp4"
    output_file_path_1080p = os.path.join(OUTPUT_DIR, output_file_name_1080p)

    colorconversor.encode_video(input_file_path, output_file_path_1080p, resolution_1080p, bitrate_1080p)
    resolution_1080p_url = f"{host_url}/output_images/{output_file_name_1080p}"
    os.remove(input_file_path)
    output_urls = [resolution_240p_url,resolution_360p_url, resolution_480p_url, resolution_720p_url, resolution_1080p_url]
    return {
        "message": "Encoding ladder processed successfully",
        "output_urls": output_urls
    }







