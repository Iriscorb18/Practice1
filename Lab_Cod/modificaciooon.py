import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
import os
import io
import cv2
from threading import Thread

# API Configuration
API_URL = "http://127.0.0.1:8000"  # Update this to your backend's URL


class MonsterAPIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Monster API GUI")
        self.geometry("1000x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main Title
        self.label_title = ctk.CTkLabel(
            self,
            text="Monster API GUI",
            font=("Arial", 30, "bold"),
        )
        self.label_title.pack(pady=10)

        # Create tabbed navigation system
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.create_controls_tab()
        self.create_image_display_tab()
        self.create_console_tab()

    # Change of colors and some positions of the Controls interface
    # def create_controls_tab(self):
    #     """Set up the controls tab for endpoint selection and file upload."""
    #     self.controls_tab = self.tab_view.add("Controls")

    #     # Section for endpoint selection
    #     self.options_frame = ctk.CTkFrame(self.controls_tab, corner_radius=15)
    #     self.options_frame.pack(pady=20, padx=10, fill="x")

    #     # Endpoint selection dropdown
    #     self.endpoint_var = ctk.StringVar(value="dct_encode")
    #     options_label = ctk.CTkLabel(
    #         self.options_frame,
    #         text="Select Endpoint:",
    #         font=("Roboto", 16, "bold"),
    #     )
    #     options_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    #     endpoints = [
    #         ("DCT Encode", "dct_encode"),
    #         ("DCT Decode", "dct_decode"),
    #         ("Black & White", "blackwhite-image"),
    #         ("Resize Image", "resize-image"),
    #         ("Wavelet Transform", "wavelet"),
    #         ("Show Info Video", "video_info"),
    #         ("Motion Visualization", "visualize-motion"),
    #         ("YUV Histogram", "yuv-histogram"),
    #     ]
    #     row_counter = 1
    #     for text, value in endpoints:
    #         button = ctk.CTkRadioButton(
    #             self.options_frame,
    #             text=text,
    #             variable=self.endpoint_var,
    #             value=value,
    #             font=("Roboto", 14),  
    #             command=self.toggle_parameter_inputs,  # Bind the endpoint selection change
    #         )
    #         button.grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
    #         row_counter += 1

    #     # File Upload Section
    #     self.upload_button = ctk.CTkButton(
    #         self.options_frame,
    #         text="Upload File",
    #         font=("Roboto", 14, "bold"),
    #         fg_color="#1E90FF",  # Electric blue color
    #         hover_color="#4682B4",
    #         command=self.upload_file,
    #     )
    #     self.upload_button.grid(row=0, column=1, padx=10, pady=5)
        
    #     # Parameter Input Section
    #     self.param_entry_label = ctk.CTkLabel(
    #         self.options_frame,
    #         text="Additional Parameters (e.g., 400,400):",
    #         font=("Roboto", 12),
    #     )
    #     self.param_entry = ctk.CTkEntry(
    #         self.options_frame,
    #         placeholder_text="e.g. 400, 400",
    #         font=("Roboto", 12),
    #     )
    #     # Initially hidden
    #     self.param_entry_label.grid(row=2, column=1, padx=5, pady=5)
    #     self.param_entry.grid(row=3, column=1, padx=5, pady=5)

    #     self.param_entry_label.grid_remove()
    #     self.param_entry.grid_remove()

    #     # Run Button
    #     self.run_button = ctk.CTkButton(
    #         self.controls_tab,
    #         text="Execute Endpoint",
    #         font=("Roboto", 14, "bold"),
    #         fg_color="#32CD32",  # Green for action
    #         hover_color="#228B22",
    #         command=self.execute_endpoint,
    #     )
    #     self.run_button.pack(pady=10)

    #     # Stop Playback Button
    #     self.stop_button = ctk.CTkButton(
    #         self.controls_tab,
    #         text="Stop Playback",
    #         font=("Roboto", 14, "bold"),
    #         fg_color="#FF6347",  # Red for stop
    #         hover_color="#CD5C5C",
    #         command=self.stop_video,
    #     )
    #     self.stop_button.pack(pady=5)
        





    
    def create_controls_tab(self):
        """Set up the controls tab for endpoint selection and file upload."""
        self.controls_tab = self.tab_view.add("Controls")

        # Section for endpoint selection
        self.options_frame = ctk.CTkFrame(self.controls_tab, corner_radius=10)
        self.options_frame.pack(pady=20, padx=10, fill="x")

        # Endpoint selection dropdown
        self.endpoint_var = ctk.StringVar(value="dct_encode")
        options_label = ctk.CTkLabel(
            self.options_frame, text="Select Endpoint:", font=("Arial", 14)
        )
        options_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        endpoints = [
            ("DCT Encode", "dct_encode"),
            ("DCT Decode", "dct_decode"),
            ("Black & White", "blackwhite-image"),
            ("Resize Image", "resize-image"),
            ("Wavelet Transform", "wavelet"),
            ("Show Info Video", "video_info"),
            ("Motion Visualization", "visualize-motion"),
            ("YUV Histogram", "yuv-histogram"),
        ]
        row_counter = 1
        for text, value in endpoints:
            button = ctk.CTkRadioButton(
                self.options_frame,
                text=text,
                variable=self.endpoint_var,
                value=value,
                command=self.toggle_parameter_inputs  # Bind the endpoint selection change
            )
            button.grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
            row_counter += 1

        # File Upload Section
        self.upload_button = ctk.CTkButton(
            self.options_frame,
            text="Upload File",
            command=self.upload_file,
        )
        self.upload_button.grid(row=0, column=1, padx=10, pady=5)

        # Parameter Input Section
        self.param_entry_label = ctk.CTkLabel(
            self.options_frame, text="Additional Parameters (e.g., 400,400):", font=("Arial", 12)
        )
        self.param_entry = ctk.CTkEntry(
            self.options_frame, placeholder_text="e.g. 400, 400"
        )
        # Initially hidden
        self.param_entry_label.grid(row=2, column=1, padx=5, pady=5)
        self.param_entry.grid(row=3, column=1, padx=5, pady=5)

        self.param_entry_label.grid_remove()
        self.param_entry.grid_remove()

        # Run Button
        self.run_button = ctk.CTkButton(
            self.controls_tab, text="Execute Endpoint", command=self.execute_endpoint
        )
        self.run_button.pack(pady=10)

        # Stop Playback Button
        self.stop_button = ctk.CTkButton(
            self.controls_tab, text="Stop Playback", command=self.stop_video
        )
        self.stop_button.pack(pady=5)

    def toggle_parameter_inputs(self):
        """Dynamically show or hide the parameter inputs based on endpoint selection."""
        if self.endpoint_var.get() == "resize-image":
            # Show the parameter input fields only when Resize Image is selected
            self.param_entry_label.grid()
            self.param_entry.grid()
        else:
            # Hide the parameter input fields for other endpoints
            self.param_entry_label.grid_remove()
            self.param_entry.grid_remove()

    def create_image_display_tab(self):
        """Set up a separate tab for result image display."""
        self.display_tab = self.tab_view.add("Display")
        self.canvas = ctk.CTkCanvas(
            self.display_tab, width=700, height=500, bg="gray50"
        )
        self.canvas.pack(pady=10, padx=10)

    def create_console_tab(self):
        """Set up a console/logging tab for debug feedback."""
        self.console_tab = self.tab_view.add("Console")
        self.text_console = ctk.CTkTextbox(self.console_tab, height=400, width=700)
        self.text_console.pack(padx=10, pady=10)

    def upload_file(self):
        """Handle file upload dialog."""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Images and Videos", "*.jpg *.png *.jpeg *.mp4 *.mkv *.webm *.avi")],
        )
        if file_path:
            self.uploaded_file = file_path
            self.show_message(f"File ready for upload: {file_path}")

    def execute_endpoint(self):
        """Main logic to call API endpoints."""
        if not hasattr(self, "uploaded_file") or not self.uploaded_file:
            self.show_message("Upload a file first to proceed.")
            return

        endpoint = self.endpoint_var.get()
        params = self.param_entry.get().strip().replace(" ", "")
        url = f"{API_URL}/{endpoint}"

        self.show_message(f"Params entered: '{params}'")  # Log entered parameters

        try:
            if params and endpoint == "resize-image":
                parts = params.split(",")
                if len(parts) != 2:
                    raise ValueError("Incorrect format for parameters. Use 'width,height'.")
                width, height = map(int, parts)
                data = {"width": width, "height": height}
            else:
                data = {}

            with open(self.uploaded_file, "rb") as file:
                self.show_message("Making request...")

                # Request to the API
                if params and endpoint == "resize-image":
                    response = requests.post(url, files={"file": file}, params=data)
                else:
                    response = requests.post(url, files={"file": file}, data=data)

                if response.status_code == 200:
                    json_response = response.json()
                    self.show_message(f"Received JSON response: {json_response}")
                    if "output_video_url" in json_response:
                        # If the response contains video URL
                        self.fetch_and_display_media(json_response["output_video_url"])
                    elif "image_url" in json_response:
                        # If the response contains image URL
                        self.fetch_and_display_media(json_response["image_url"])
                    else:
                        self.show_message("No media URL found in response.")
                else:
                    self.show_message(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            self.show_message(f"Error: {e}")

    def fetch_and_display_media(self, media_url):
        """Fetch media (image or video) from URL and dynamically resize canvas for display."""
        try:
            # Check if media is video or image
            if media_url.endswith((".mp4", ".mkv", ".webm", ".avi")):
                # Clean up the URL if there are redundant 'output_images' paths
                if 'output_images/output_images' in media_url:
                    media_url = media_url.replace('output_images/output_images', 'output_images', 1)
                self.play_video(media_url)  # If it's a video, play it
            else:
                # Otherwise, assume it's an image
                response = requests.get(media_url)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))

                    # Update canvas size dynamically based on image size
                    self.canvas.config(width=image.width, height=image.height)

                    # Convert image to a format tkinter can use
                    img = ImageTk.PhotoImage(image)

                    # Clear canvas and draw image (centered)
                    self.canvas.delete("all")
                    self.canvas.create_image(
                        self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                        anchor="center", image=img
                    )

                    # Prevent garbage collection
                    self.canvas.image = img

                    self.show_message("Image successfully fetched and displayed.")
                else:
                    self.show_message(f"Failed to fetch image. Status code: {response.status_code}")
        except Exception as e:
            self.show_message(f"Error fetching or displaying media: {e}")

    def play_video(self, video_url):
        """Fetch and play video in a loop."""
        try:
            # Fetch the video file
            video_resp = requests.get(video_url, stream=True)
            if video_resp.status_code == 200:
                temp_video_path = os.path.join("temp_video.mp4")
                with open(temp_video_path, "wb") as f:
                    for chunk in video_resp.iter_content(chunk_size=1024):
                        f.write(chunk)

                self.show_message("Video downloaded successfully. Starting playback...")

                # Use OpenCV to read and play the video
                self.video_capture = cv2.VideoCapture(temp_video_path)

                def play():
                    frame_number = 0

                    # Loop to read and show video frames
                    def show_frame():
                        nonlocal frame_number
                        ret, frame = self.video_capture.read()
                        if not ret:
                            self.video_capture.release()
                            os.remove(temp_video_path)
                            self.show_message("Video playback finished.")
                            return

                        # Convert frame to a format tkinter can use
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_image = Image.fromarray(frame_rgb)
                        frame_tk = ImageTk.PhotoImage(frame_image)

                        # Update the canvas (centered)
                        self.canvas.config(width=frame.shape[1], height=frame.shape[0])
                        self.canvas.delete("all")
                        self.canvas.create_image(
                            self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                            anchor="center", image=frame_tk
                        )
                        self.canvas.image = frame_tk  # Prevent garbage collection

                        # Schedule next frame update
                        frame_number += 1
                        self.canvas.after(30, show_frame)  # Adjust delay for video playback speed

                    show_frame()  # Start video playback loop

                # Run playback in a separate thread
                Thread(target=play, daemon=True).start()

            else:
                self.show_message(f"Failed to fetch video. Status code: {video_resp.status_code}")
        except Exception as e:
            self.show_message(f"Error playing video: {e}")

    def stop_video(self):
        """Stop video playback."""
        if hasattr(self, "video_capture") and self.video_capture.isOpened():
            self.video_capture.release()
            self.show_message("Video playback stopped.")

    def show_message(self, message):
        """Helper function to show feedback to users."""
        self.text_console.insert("end", f"{message}\n")
        self.text_console.see("end")
        self.text_console.update()


if __name__ == "__main__":
    app = MonsterAPIApp()
    app.mainloop()
