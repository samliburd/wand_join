from wand.image import Image
from wand.display import display
from pprint import pprint
from pathlib import Path
import sys
import argparse


def path_converter(path):
    return Path(path)


def calculate_scales(images, downscale=False, landscape=False):
    # Extract image data: path, width, height
    image_data = [
        (image_path, img.width, img.height)
        for image_path in images
        for img in [Image(filename=image_path)]
    ]

    # Find max and min dimensions
    max_width = max(image_data, key=lambda x: x[1])[1]
    max_height = max(image_data, key=lambda x: x[2])[2]
    min_width = min(image_data, key=lambda x: x[1])[1]
    min_height = min(image_data, key=lambda x: x[2])[2]

    # Determine scale factors based on flags
    scale_width = min_width if downscale else max_width
    scale_height = min_height if downscale else max_height

    if landscape:
        scale_factor = scale_height
        scale_dimension = "height"
    else:
        scale_factor = scale_width
        scale_dimension = "width"

    # Create image_info with appropriate scales
    image_info = [
        {"path": image_path, "width": width, "height": height, "scale": scale_factor / (height if landscape else width)}
        for image_path, width, height in image_data
    ]

    return image_info


def blob_image(images):
    return [
        img.make_blob()
        for image in images
        for img in [Image(filename=image['path'])]
        if img.scale(int(img.width * image['scale']), int(img.height * image['scale']))
    ]


def concat(blobs, output, landscape=False):
    with Image(blob=blobs[0]) as img:
        for blob in blobs[1:]:
            img.sequence.append(Image(blob=blob))
        img.smush(True if not landscape else False)
        img.save(filename=f"{output}.jpg")


def main():
    parser = argparse.ArgumentParser(description="Concatenate images after scaling them.")
    parser.add_argument('files', type=Path, nargs='*', help='List of image files to concatenate')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output filename without extension')
    parser.add_argument('-s', '--small', required=False, action='store_true',
                        help='Scale images down')
    parser.add_argument('-l', '--landscape', required=False, action='store_true',
                        help='Scale images down')
    args = parser.parse_args()

    # Separate the output filename from the list of input files
    files = args.files
    output_filename = args.output

    # Calculate scales and generate blobs
    blobs = blob_image(calculate_scales(files, args.small, args.landscape))

    # Concatenate the blobs into the output file
    concat(blobs, output_filename, args.landscape)


if __name__ == '__main__':
    main()
