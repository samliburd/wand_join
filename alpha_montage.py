import argparse
import logging
import time
from wand.image import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def parse_args():
    parser = argparse.ArgumentParser(description="Concatenate images after scaling them.")
    parser.add_argument('files', type=Path, nargs='*', help='List of image files to concatenate')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output filename without extension')
    parser.add_argument('-f', '--format', type=str, default="jpg", help='Output filename extension')
    parser.add_argument('-q', '--quality', type=int, default=92, help='Output file quality')
    parser.add_argument('-s', '--small', required=False, action='store_true', help='Scale images down')
    parser.add_argument('-l', '--landscape', required=False, action='store_true', help='Append images horizontally')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help='Enable verbose logging')
    return parser.parse_args()


def even_dimensions(size):
    width, height = size
    return width - width % 2, height - height % 2


def process_image(file):
    with Image(filename=file) as img:
        if img.alpha_channel:
            img.trim()
            new_size = even_dimensions(img.size)
            img.sample(new_size[0], new_size[1])
        return img.size, img.make_blob()


def process_images(files):
    logging.info("Starting to process images")
    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_image, files))
    image_info, processed_blobs = zip(*results)
    end_time = time.time()
    logging.info(f"Finished processing images in {end_time - start_time:.2f} seconds")
    return image_info, processed_blobs


def calculate_image_scales(image_sizes):
    logging.info("Starting to calculate image scales")
    start_time = time.time()

    widths, heights = zip(*image_sizes)
    max_width = max(widths)
    scales = [max_width / width for width in widths]

    end_time = time.time()
    logging.info(f"Finished calculating image scales in {end_time - start_time:.2f} seconds")
    return scales


def scale_image(blob, scale):
    with Image(blob=blob) as img:
        img.sample(int(img.width * scale), int(img.height * scale))
        return img.make_blob()


def scale_images(image_blobs, scales):
    logging.info("Starting to scale images")
    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        scaled_image_blobs = list(executor.map(scale_image, image_blobs, scales))
    end_time = time.time()
    logging.info(f"Finished scaling images in {end_time - start_time:.2f} seconds")
    return scaled_image_blobs


def concatenate_images(image_blobs, args):
    logging.info("Starting to concatenate images")
    start_time = time.time()

    with Image() as final_image:
        for blob in image_blobs:
            with Image(blob=blob) as img:
                img.transform_colorspace("srgb")
                final_image.image_add(img)
        final_image.smush(True)
        final_image.compression_quality = args.quality
        final_image.save(filename=f"{args.output}.{args.format}")

    end_time = time.time()
    logging.info(f"Finished concatenating and saving images in {end_time - start_time:.2f} seconds")


def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting the script")
    start_time = time.time()

    image_info, image_blobs = process_images(args.files)
    scales = calculate_image_scales(image_info)
    scaled_images = scale_images(image_blobs, scales)
    concatenate_images(scaled_images, args)

    end_time = time.time()
    logging.info(f"Finished everything in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()