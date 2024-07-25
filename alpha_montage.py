import argparse
from wand.image import Image
from wand.display import display
from pathlib import Path
import random


def parse_args():
    parser = argparse.ArgumentParser(description="Concatenate images after scaling them.")
    parser.add_argument('files', type=Path, nargs='*', help='List of image files to concatenate')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output filename without extension')
    parser.add_argument('-f', '--format', type=str, default="jpg", help='Output filename extension')
    parser.add_argument('-q', '--quality', type=int, default=92, help='Output file quality')
    parser.add_argument('-s', '--small', required=False, action='store_true', help='Scale images down')
    parser.add_argument('-l', '--landscape', required=False, action='store_true', help='Append images horizontally')
    return parser.parse_args()


def even_dimensions(size):
    width, height = size
    width -= width % 2
    height -= height % 2
    return width, height


def process_images(files):
    image_info = list()
    processed_blobs = list()
    for file in files:
        with Image(filename=file) as img:
            if img.alpha_channel:
                img.trim()
                img.resize(even_dimensions(img.size)[0], even_dimensions(img.size)[1])
            image_info.append(img.size)
            processed_blobs.append(img.make_blob())
    return image_info, processed_blobs


# def calculate_image_scales(image_info):
#     scales = list()
#     widths, heights = zip(*[(image["width"], image["height"]) for image in image_info])
#     max_width = max(widths)
#     max_height = max(heights)
#     for image in image_info:
#         scale = max_width / image["width"]
#         image["scale"] = scale
#         scales.append(scale)
#     scaled_images_info = [{"width": image["width"], "height": image["height"], "scale": image["scale"]} for image in
#                           image_info]
#     return scales
def calculate_image_scales(image_sizes):
    scales = []
    widths, heights = zip(*image_sizes)
    max_width = max(widths)
    max_height = max(heights)
    for size in image_sizes:
        width, height = size
        scale = max_width / width
        scales.append(scale)
    return scales


def scale_images(image_blobs, scales):
    scaled_image_blobs = []
    for index, blob in enumerate(image_blobs):
        with Image(blob=blob) as img:
            img.scale(int(img.width * scales[index]), int(img.height * scales[index]))
            scaled_image_blobs.append(img.make_blob())
    return scaled_image_blobs


def concatenate_images(image_blobs):
    with Image() as final_image:
        for blob in image_blobs:
            with Image(width=Image(blob=blob).width, height=Image(blob=blob).height, blob=blob) as img:
                img.transform_colorspace("srgb")
                final_image.image_add(img)
        final_image.smush(True)
        return final_image.make_blob()


def save_final_image(image_blob, args):
    with Image(blob=image_blob) as img:
        img.compression_quality = args.quality
        img.save(filename=f"{args.output}.{args.format}")


def main():
    args = parse_args()
    (image_info, image_blobs) = process_images(args.files)
    # trimmed_images = process_images(args.files)
    scales = calculate_image_scales(image_info)
    scaled_images = scale_images(image_blobs, scales)
    # scaled_images = calculate_image_scales(trimmed_images_info)
    # resized_images = resize_images(scaled_images)
    final_image_blob = concatenate_images(scaled_images)
    save_final_image(final_image_blob, args)


if __name__ == "__main__":
    main()
