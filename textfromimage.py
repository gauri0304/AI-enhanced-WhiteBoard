from PIL import Image
from pytesseract import pytesseract
from tkinter import Tk
from tkinter.filedialog import askopenfilename


# Function to extract text from an image using Tesseract
def extract_text(image_path):
    # Defining path to tesseract.exe
    path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Providing the tesseract executable location to pytesseract library
    pytesseract.tesseract_cmd = path_to_tesseract

    # Opening the image & storing it in an image object
    img = Image.open(image_path)

    # Passing the image object to image_to_string() function
    # This function will extract the text from the image
    text = pytesseract.image_to_string(img)

    return text


# Main function
def main():
    # Hiding the root Tkinter window
    Tk().withdraw()

    # Open file dialog to select an image file
    image_path = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp")])

    # If a file was selected
    if image_path:
        # Extract and display the text from the selected image
        text = extract_text(image_path)

        if text:
            print(text[:-1])
        else:
            print("No text found")
    else:
        print("No file selected")


# Run the main function
if __name__ == "__main__":
    main()