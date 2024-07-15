from wand.image import Image
from wand.display import display

# with Image() as img:
#     for src in ["4816.jpg", "5347.jpg", "7789.jpg"]:
#         with Image(width=1920, height=4650, pseudo=src) as item:
#             img.image_add(item)
#     img.montage(thumbnail="1920x1080!+5+5")
#     # img.border('magenta', 0, 0)
#     img.save(filename='montage-default.png')
#     # display(img)

with Image() as img:
    for src in ["4816.jpg", "5347.jpg", "7789.jpg"]:
        with Image(width=1920, height=4650, pseudo=src) as item:
            img.image_add(item)
        # img.concat(stacked=True)
        img.smush(True)
        img.save(filename="montagetest.jpg")
