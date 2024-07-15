import argparse
from wand.image import Image
from pathlib import Path
import random


class PhotoJoin:
    def __init__(self, files, output, file_format="jpg", quality=92, downscale=False, landscape=False):
        self.files = files
        self.output = output
        self.file_format = file_format
        self.quality = quality
        self.downscale = downscale
        self.landscape = landscape
        self.image_info = list()  # Initialize image_info attribute

    @staticmethod
    def path_converter(self, path):
        return Path(path)

    def calculate_scales(self):
        # Extract image data: path, width, height
        image_data = [
            (image_path, img.width, img.height)
            for image_path in self.files
            for img in [Image(filename=image_path)]
        ]

        # Extract widths and heights separately
        widths, heights = zip(*[(width, height) for _, width, height in image_data])

        # Find max and min dimensions
        max_width = max(widths)
        max_height = max(heights)
        min_width = min(widths)
        min_height = min(heights)

        # Determine scale factors based on flags
        scale_width = min_width if self.downscale else max_width
        scale_height = min_height if self.downscale else max_height

        if self.landscape:
            scale_factor = scale_height
        else:
            scale_factor = scale_width

        # Create image_info with appropriate scales
        self.image_info = [
            {"path": image_path, "width": width, "height": height,
             "scale": scale_factor / (height if self.landscape else width)}
            for image_path, width, height in image_data
        ]

    def blob_image(self):
        blobs = list()
        for image in self.image_info:
            with Image(filename=image['path']) as img:
                img.scale(int(img.width * image['scale']), int(img.height * image['scale']))
                img.compression_quality = 92
                # img.save(filename=f"{random.randint(1000, 9999)}.jpg")
                blobs.append(img.make_blob())
        return blobs

    def concat(self, blobs):
        with Image() as img:
            for blob in blobs:
                img.sequence.append(Image(blob=blob))
            img.compression_quality = self.quality
            img.smush(True if not self.landscape else False)
            img.save(filename=f"{self.output}.{self.file_format}")
        # with Image(blob=blobs[0]) as img:
        #     for blob in blobs[1:]:
        #         img.sequence.append(Image(blob=blob))
        #     img.compression_quality = self.quality
        #     img.smush(True if not self.landscape else False)
        #     img.save(filename=f"{self.output}.{self.file_format}")

    def run(self):
        self.calculate_scales()
        blobs = self.blob_image()
        self.concat(blobs)


def main():
    parser = argparse.ArgumentParser(description="Concatenate images after scaling them.")
    parser.add_argument('files', type=Path, nargs='*', help='List of image files to concatenate')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output filename without extension')
    parser.add_argument('-f', '--format', type=str, default="jpg", help='Output filename extension')
    parser.add_argument('-q', '--quality', type=int, default=92, help='Output file quality')
    parser.add_argument('-s', '--small', required=False, action='store_true', help='Scale images down')
    parser.add_argument('-l', '--landscape', required=False, action='store_true', help='Append images horizontally')
    args = parser.parse_args()

    photo_join = PhotoJoin(
        files=args.files,
        output=args.output,
        file_format=args.format,
        quality=args.quality,
        downscale=args.small,
        landscape=args.landscape
    )
    photo_join.run()


if __name__ == '__main__':
    main()
