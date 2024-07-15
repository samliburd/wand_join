from wand.image import Image
import sys

args = sys.argv[1:]
files = args
print(args)
for filename in files:
    with Image(filename=filename) as img:
        print(img.alpha_channel)
        print(img.size)
        img.trim()
        print(img.size)
