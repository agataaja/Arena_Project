import os
import numpy as np
from skimage import io, filters, measure
from skimage.color import rgb2gray
from skimage.draw import polygon_perimeter
from xml.dom.minidom import Document


def png_to_svg(png_path, svg_path):
    # Read the PNG image
    image = io.imread(png_path)

    # Convert the image to grayscale
    gray_image = rgb2gray(image)

    # Apply Gaussian smoothing to the grayscale image
    smoothed_image = filters.gaussian(gray_image, sigma=1)

    # Threshold the smoothed image to create a binary image
    binary_image = smoothed_image > 0.5

    # Find contours in the binary image
    contours = measure.find_contours(binary_image, 0.5, fully_connected='high')

    # Create an SVG document
    doc = Document()
    svg = doc.createElement('svg')
    svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    doc.appendChild(svg)

    # Create a path element for each contour
    for contour in contours:
        path = doc.createElement('path')
        path.setAttribute('d', 'M {} L {}'.format(' '.join([f'{y},{x}' for x, y in contour[::-1]]),
                                                  ' '.join([f'{y},{x}' for x, y in contour[::-1]])))
        svg.appendChild(path)

    # Save the SVG document to a file
    with open(svg_path, 'w') as f:
        f.write(doc.toprettyxml())

# Example usage
input_folder = r'C:\Users\agata\Desktop\clubes svg'
output_folder = r'C:\Users\agata\Desktop\clubes svg new'
os.makedirs(output_folder, exist_ok=True)

for file_name in os.listdir(input_folder):
    if file_name.endswith('.png'):
        png_path = os.path.join(input_folder, file_name)
        svg_path = os.path.join(output_folder, file_name.replace('.png', '.svg'))

        try:
            png_to_svg(png_path, svg_path)

        except:
            pass
# Example usage
# convert_images_to_svg(r'C:\Users\agata\Desktop\clubes svg', r'C:\Users\agata\Desktop\clubes svg new')
