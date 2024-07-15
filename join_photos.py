from wand.image import Image
from wand.display import display
from pprint import pprint
from pathlib import Path
import sys

args = sys.argv


def path_converter(path):
    return Path(path)


def calculate_scales(images):
    image_data = [
        (image_path, img.width, img.height)
        for image_path in images
        for img in [Image(filename=image_path)]
    ]
    [max_width, max_height] = [max(image_data, key=lambda x: x[1])[1], max(image_data, key=lambda x: x[2])[2]]
    [min_width, min_height] = [min(image_data, key=lambda x: x[1])[1], min(image_data, key=lambda x: x[2])[2]]
    image_info = [
        {"path": image_path, "width": width, "height": height, "scale": max_width / width}
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


def concat(blobs, output):
    with Image(blob=blobs[0]) as img:
        for blob in blobs[1:]:
            img.sequence.append(Image(blob=blob))
        img.smush(True)
        img.save(filename=f"{output}.jpg")


def main():
    # Separate the output filename from the list of input files
    files = list(map(path_converter, args[1:-1]))
    output_filename = args[-1]

    # Calculate scales and generate blobs
    # calculate_scales(files)
    blobs = blob_image(calculate_scales(files))

    # Concatenate the blobs into the output file
    concat(blobs, output_filename)


if __name__ == '__main__':
    main()
