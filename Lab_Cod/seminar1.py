#Various imports used through the seminar

import scipy.sparse
from scipy.fftpack import dct, idct
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import subprocess
from PIL import Image
import numpy as np
import pywt
import os
import json


# #Class code
# class colorconversor_1:
#     def rgb_to_yuv(R,G,B):
#         Y= 0.257*R+0.504*G+0.0098*B+16
#         Cb = -0.148*R-0.291*G+0.439*B+128
#         Cr = 0.439*R-0.368*G-0.071*B+128
#         return Y,Cb,Cr
#     def yuv_to_rgb (Y,Cb,Cr):
#         B = 1.164*(Y-16)+2.018*(Cb-128)
#         G = 1.164*(Y-16)-0.813*(Cr-128)-0.391*(Cb-128)
#         R = 1.164*(Y-16)+1.596*(Cr-128)
#         return R,G,B

    
# rgb_to_yuv_1 = colorconversor_1.rgb_to_yuv(246,38,129)
# yuv_to_rgb_1 = colorconversor_1.yuv_to_rgb(99.6382, 137.165, 212.851) #The conversion is not correct since it does not return the exact same color as provided in rgb_to_yuv

#Since previous code does not work correctly, we use the Wikipedia code for the colorconversor class
class colorconversor:

    def rgb_to_yuv(R,G,B):
        Y=0.299*R+0.587*G+0.114*B

        U= -0.14713*R - 0.28886*G+0.436*B

        V=0.615*R -0.51498*G-0.10001*B
        return Y,U,V
    def yuv_to_rgb (Y,U,V):
        R = Y+1.14*V
        G = Y-0.396*U-0.581*V
        B = Y +2.029*U
        return R,G,B
    def resize_image_ffmpeg(input_image, output_image, width, height):
    
        input_image = f"/app/output_images/{os.path.basename(input_image)}"  
        output_image = f"/app/output_images/{os.path.basename(output_image)}" 
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",  
            "ffmpeg",
            "-y",
            "-i", input_image,
            "-vf", f"scale={width}:{height}",
            output_image
        ]
            
        
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Resized image saved to {output_image}")
        print(result.stdout.decode())  
        return result

    def serpentine_scan(image):
        rows, cols, _ = image.shape  #3 channels
        result = []

        for i in range(rows):
            if i % 2 == 0:  # Even rows 
                result.extend(image[i, :, :])
            else:  # Odd rows
                result.extend(image[i, ::-1, :])

        return result

    def blackwhite_image_ffmpeg(input_image, output_image):
       
        input_image = f"/app/output_images/{os.path.basename(input_image)}"  
        output_image = f"/app/output_images/{os.path.basename(output_image)}"  
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg",
            "-y",                  
            "-i", input_image,
            "-vf", f"format=gray",
            output_image
        ]
        
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Resized image saved to {output_image}")
        print(result.stdout.decode())  # Print FFmpeg's output
        return result

    def run_length_encode(data):
        encoded = []
        current_byte = data[0]
        count = 1

        for byte in data[1:]:
            if byte == current_byte:
                    count += 1
            else:
                encoded.append((current_byte, count))
                current_byte = byte
                count = 1
                
        #Appending last iteration
        encoded.append((current_byte, count))
        return encoded
    def chroma_subsampling_ffmpeg(input_image, output_image,  pix_fmt):
        
        input_image = f"/app/output_images/{os.path.basename(input_image)}" 
        output_image = f"/app/output_images/{os.path.basename(output_image)}" 
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", "-y","-i", input_image,  # Input file
            "-c:v", "libx264",          # Video codec
            "-vf", f"format={pix_fmt}", # Video filter to set pixel format
            output_image                 # Output file                   
        ]
        
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Resized image saved to {output_image}")
        print(result.stdout.decode()) 
        return result
    def extract_video_info(video_path):
        input_image = f"/app/output_images/{os.path.basename(video_path)}"  
 
        # Run ffprobe command to get video info in JSON format
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            'ffprobe',
            '-v', 'error',  # Suppress non-error messages
            '-select_streams', 'v:0',  # Select the first video stream
            '-show_entries', 'stream=duration,codec_name,width,height,r_frame_rate',  # Specify the data we want
            '-of', 'json',  # Output format as JSON
            input_image  # Input video file
        ]
        
        # Run the command and capture the output and errors
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Ensure that stdout contains valid JSON
        if result.stdout:
            video_info = json.loads(result.stdout)
            stream = video_info['streams'][0]
            video_details = {
                "duration": stream['duration'],  # Duration of the video
                "codec": stream['codec_name'],  # Video codec
                "width": stream['width'],  # Video width
                "height": stream['height'],  # Video height
                "frame_rate": eval(stream['r_frame_rate'])  # Frame rate (r_frame_rate is in "numerator/denominator" format)
            }
            return video_details
            
    def cut_video(input_file_path, output_file_path):
        input_file_in_container = f"/app/output_images/{os.path.basename(input_file_path)}"
        output_file_in_container = f"/app/output_images/{os.path.basename(output_file_path)}"

        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", "-y",
            "-i", input_file_in_container,  # Input file path in container
            "-t", "20",  # Duration of 20 seconds
            "-c:v", "copy",                 # Avoid re-encoding
            output_file_in_container        # Output file path in container
        ]

        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
        

    # Function to extract audio as AAC mono
    def extract_audio_aac(input_file_path, output_file_path):
        input_file_in_container = f"/app/output_images/{os.path.basename(input_file_path)}"
        output_file_in_container = f"/app/output_images/{os.path.basename(output_file_path)}"
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",  # Docker container
            "ffmpeg","-y" ,"-i", input_file_in_container,  # Input audio file
            "-t", "20",  # Duration of 20 seconds
            "-ac", "1", #Mono audio
            "-c:a", "aac", #AAC Codec
            "-b:a", "128k", output_file_in_container #Bitrate for AAC
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Function to extract audio as MP3 stereo with lower bitrate
    def extract_audio_mp3(input_file_path, output_file_path):
        input_file_in_container = f"/app/output_images/{os.path.basename(input_file_path)}"
        output_file_in_container = f"/app/output_images/{os.path.basename(output_file_path)}"
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg","-y" ,"-i", input_file_in_container,
            "-t", "20",  # Duration of 20 seconds
            "-ac", "2",  # Stereo audio
            "-c:a", "libmp3lame",  # MP3 codec
            "-b:a", "64k",  # Lower bitrate (64kbps)
            output_file_in_container
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


    # Function to extract audio as AC3 codec
    def extract_audio_ac3(input_file_path, output_file_path):
        input_file_in_container = f"/app/output_images/{os.path.basename(input_file_path)}"
        output_file_in_container = f"/app/output_images/{os.path.basename(output_file_path)}"
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", "-y" ,"-i", input_file_in_container,
            "-t", "20",  # Duration of 20 seconds
            "-ac", "2",  # Stereo audio
            "-c:a", "ac3",  # AC3 codec
            "-b:a", "192k",  # Bitrate for AC3
            output_file_in_container
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Function to package video and audio into a .mp4 file
    def package_video_audio(video_path, audio_aac_path, audio_mp3_path, audio_ac3_path, output_path):
        video_path = f"/app/output_images/{os.path.basename(video_path)}"
        audio_aac_path = f"/app/output_images/{os.path.basename(audio_aac_path)}"
        audio_mp3_path = f"/app/output_images/{os.path.basename(audio_mp3_path)}"
        audio_ac3_path = f"/app/output_images/{os.path.basename(audio_ac3_path)}"
        output_path = f"/app/output_images/{os.path.basename(output_path)}"
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", 
            "-i", video_path, 
            "-i", audio_aac_path, 
            "-i", audio_mp3_path, 
            "-i", audio_ac3_path,
            "-c:v", "copy", 
            "-map", "0:v", 
            "-map", "1:a", 
            "-map", "2:a", 
            "-map", "3:a", 
            "-c:a:0", "aac", 
            "-c:a:1", "mp3", 
            "-c:a:2", "ac3", 
            "-y", output_path
        ]
       
    def count_tracks_in_mp4(input_file_path):
        input_file_path = f"/app/output_images/{os.path.basename(input_file_path)}"  
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffprobe", "-v", "error",
            "-show_entries", "stream=index",
            "-of", "csv=p=0",
            input_file_path
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Each line in the output corresponds to a track
        track_count = len(result.stdout.strip().split("\n"))
        return track_count
    def visualize_vectors(input_file_path, output_file_path):
        input_file_path = f"/app/output_images/{os.path.basename(input_file_path)}"  
        output_file_path = f"/app/output_images/{os.path.basename(output_file_path)}" 
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", "-y","-flags2", "+export_mvs",  # Enable motion vector export
            "-i", input_file_path,
            "-vf", "codecview=mv=pf+bf+bb",  # Visualize motion vectors and macroblocks
            "-c:v", "libx264",  # Output codec
            "-preset", "fast",  # Speed optimization
            "-crf", "23",  # Quality control
            output_file_path
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def generate_yuv_histogram(input_file_path, output_file_path):
        input_file_path = f"/app/output_images/{os.path.basename(input_file_path)}"  
        output_file_path = f"/app/output_images/{os.path.basename(output_file_path)}" 
        command = [
            "docker", "exec", "lab_cod-ffmpeg-1",
            "ffmpeg", "-y",
            "-i", input_file_path,
            "-vf", "split=2[a][b];[b]histogram,format=yuv420p[hh];[a][hh]overlay",  # Split video and add histogram
            "-c:v", "libx264",  # Output codec
            "-preset", "fast",  # Speed optimization
            "-crf", "23",  # Quality control
            output_file_path
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)





class DCT_coding:
    def encoding_DCT(input):
        return (dct(input, norm = 'ortho'))
    def decoding_DCT(input):
        return (idct(input, norm = 'ortho'))
    

class wavelet_coding:
    def generate_wavelet(img, string, level = 1):
        coeffs = pywt.wavedec2(img, string, level)
        return coeffs
    
    def plot_coefficients(coeffs):
        
        cA, (cH, cV, cD) = coeffs
    
        cA = cA[:, :, 0]
        cH = cH[:, :, 0]
        cV = cV[:, :, 0]
        cD = cD[:, :, 0]
        
        plt.figure(figsize=(10, 10))
        plt.subplot(2, 2, 1)
        plt.title('Approximation')
        plt.imshow(cA, cmap='gray')

        plt.subplot(2, 2, 2)
        plt.title('Horizontal Detail')
        plt.imshow(cH, cmap='gray')

        plt.subplot(2, 2, 3)
        plt.title('Vertical Detail')
        plt.imshow(cV, cmap='gray')

        plt.subplot(2, 2, 4)
        plt.title('Diagonal Detail')
        plt.imshow(cD, cmap='gray')

        plt.show()
        

# #1) Run ‘ffmpeg’ and upload a screenshot of the first line


# #2) Start a script called first_seminar.py . Then create a class and a method , which is a
# # translator from 3 values in RGB into the 3 YUV values, plus the opposite operation.
# rgb_to_yuv_1 = colorconversor.rgb_to_yuv(246, 38, 129)
# print("RGB to YUV:", rgb_to_yuv_1)
    
# yuv_to_rgb_1 = colorconversor.yuv_to_rgb(*rgb_to_yuv_1)
# print("YUV to RGB:", yuv_to_rgb_1)

# #3) Use ffmpeg to resize images into lower quality. Use any image you like
# colorconversor.resize_image_ffmpeg("imagen_prueba.jpeg", "output_prueba.jpeg")
# img = mpimg.imread('imagen_prueba.jpeg')
# img_output = mpimg.imread('output_prueba.jpeg')
    
# #4) Create a method called serpentine which should be able to read the bytes of a JPEG file in


# image_array = np.array(img_output)
# print("Image shape:", image_array.shape)
# serpentine_result = colorconversor.serpentine_scan(img_output)
# print("Serpentine Scan Result:")
# print(serpentine_result)
# print("Length of the result:", len(serpentine_result))


# #5) Use FFMPEG to transform the previous image into b/w. Do the hardest compression you can.
# colorconversor.blackwhite_image_ffmpeg("imagen_prueba.jpeg", "output_blanconegro.jpeg")
# img_bw = mpimg.imread('output_blanconegro.jpeg')

# plt.figure(1)
# plt.subplot(1, 3, 1)
# plt.title("Original Image")
# plt.imshow(img)
    
# plt.subplot(1, 3, 2)
# plt.title("Resized Image")
# plt.imshow(img_output)
    
# plt.subplot(1, 3, 3)
# plt.title("Black and White Image")
# plt.imshow(img_bw, cmap='gray')
# plt.show()

# #5) Create a method which applies a run-lenght encoding from a series of bytes given.
# data = bytes([1,1,2,3,4,1,1,1,2,3])
# rle_encoded = colorconversor.run_length_encode(data)
# print("Run-length encoded data:", rle_encoded)

# #6) Create a class which can convert, can decode (or both) an input using the DCT. Not necessary a
# # JPG encoder or decoder. A class only about DCT is OK too
# img_DCT = DCT_coding.encoding_DCT(img)
# img_IDCT = DCT_coding.decoding_DCT(img_DCT)
# #Since its not a raw image, we lose some information in the process

# plt.figure(2)
# plt.title("DCT of Image")
# plt.imshow(img_DCT)
# plt.show()
    
# plt.figure(3)
# plt.title("IDCT Reconstruction")
# plt.imshow(img_IDCT)
# plt.show()

    
# #7) Create a class which can convert, can decode (or both) an input using the DWT. Not necessary a
# #JPEG2000 encoder or decoder. A class only about DWT is OK too
# coeffs = wavelet_coding.generate_wavelet(img, 'bior1.1', level=1)
# wavelet_coding.plot_coefficients(coeffs)

# reconstructed_image = pywt.waverec2(coeffs, 'bior1.1')

# plt.figure(5)
# plt.subplot(1, 2, 1)
# plt.title("Original Image")
# plt.imshow(img, cmap='gray')

# plt.subplot(1, 2, 2)
# plt.title("Reconstructed Image")
# plt.imshow(reconstructed_image, cmap='gray')
# plt.show()