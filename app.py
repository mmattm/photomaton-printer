from flask import Flask, request, jsonify
from escpos.printer import Usb
import os
from PIL import Image
import usb.core
import usb.backend.libusb1
import time  # For introducing delay
import tempfile  # Import the tempfile module
import requests


# Attempt to manually specify the path to the libusb library
backend = usb.backend.libusb1.get_backend(
    find_library=lambda x: "/opt/homebrew/lib/libusb-1.0.dylib"
)
print("Backend:", backend)

# Try to find any USB device as a test
dev = usb.core.find(backend=backend)
print("Device found:", dev)

app = Flask(__name__)

# Define your printer USB IDs
PRINTER_VENDOR_ID = 0x04B8
PRINTER_PRODUCT_ID = 0x0E28
printer_width_pixels = 560  # Example width, adjust based on your printer's specs

# Initialize printer outside the loop
printer = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)


@app.route("/")
def hello():
    return "Hello, World!"


def prepare_image(image_path, printer_width):
    """
    Load an image, resize it to fit the printer width, rotate it by 180 degrees,
    and convert it to grayscale.
    :param image_path: Path to the image file
    :param printer_width: Width of the printer in pixels
    :return: A processed PIL Image object
    """
    # Load the image
    img = Image.open(image_path)

    # Calculate the new height to maintain aspect ratio
    aspect_ratio = img.height / img.width
    new_height = int(printer_width * aspect_ratio)

    # Resize the image to fit the printer width
    img_resized = img.resize((printer_width, new_height), Image.Resampling.LANCZOS)

    # Rotate the image by 180 degrees
    img_rotated = img_resized.rotate(180)

    # Convert to grayscale
    img_gray = img_rotated.convert("L")

    return img_gray


@app.route("/print-images", methods=["POST"])
def print_images():
    # Get the JSON data sent to the endpoint
    request_data = request.get_json()

    # Check if "image_urls" key is present in the JSON data
    if "image_urls" not in request_data:
        return jsonify({"error": "No image URLs provided"}), 400

    # Extract the list of image URLs from the JSON data
    image_urls = request_data["image_urls"]

    print("Image URLs: ", image_urls)
    print("————————————————")

    try:
        for url in image_urls:
            # Download the image
            response = requests.get(url)
            if response.status_code == 200:
                # Save the image temporarily
                with tempfile.NamedTemporaryFile(
                    delete=True, suffix=".jpg"
                ) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file.flush()

                    # Process and print the image
                    processed_image = prepare_image(tmp_file.name, printer_width_pixels)
                    printer._raw(b"\x1b\x64\x08")  # Feed
                    printer._raw(b"\x1b\x61\x00")  # Center align
                    printer.image(processed_image)
                    printer._raw(b"\x1b\x64\x08")  # Feed
                    time.sleep(1)  # Delay between prints if needed
            else:
                print(f"Failed to download image from {url}")

        # printer.cut()  # Optionally, move this outside the loop if you want all images as part of a single printout
        # reset printer
        printer._raw(b"\x1B\x40")

        return jsonify({"message": "Images printed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# function to cut paper only
@app.route("/cut-paper", methods=["POST"])
def cut_paper():
    try:
        printer.cut()
        return jsonify({"message": "Paper cut successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5500)
