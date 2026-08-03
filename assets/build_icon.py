"""Generate the application PNG and ICO assets with Pillow."""
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

# Soft shadow and deep navy app tile.
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle((68, 82, 956, 970), radius=210, fill=(2, 6, 23, 150))
shadow = shadow.filter(ImageFilter.GaussianBlur(30))
img.alpha_composite(shadow)
d = ImageDraw.Draw(img)
d.rounded_rectangle((52, 52, 972, 972), radius=220, fill="#0B1224", outline="#263653", width=10)
d.rounded_rectangle((78, 78, 946, 946), radius=195, outline="#FFFFFF1A", width=7)

# Media card.
d.rounded_rectangle((220, 214, 804, 816), radius=116, fill="#14213D", outline="#40557E", width=10)

# Play symbol and subtitle lines.
d.polygon([(426, 332), (426, 636), (682, 484)], fill="#34D7C7")
d.rounded_rectangle((322, 684, 702, 716), radius=16, fill="#F2F7FF")
d.rounded_rectangle((372, 742, 652, 768), radius=13, fill="#91A8CE")

# Two rename arrows around the card.
teal = "#34D7C7"
blue = "#6C8CFF"
d.arc((100, 388, 250, 600), start=105, end=255, fill=teal, width=28)
d.line([(144, 405), (190, 438), (143, 472)], fill=teal, width=24, joint="curve")
d.arc((774, 388, 924, 600), start=-75, end=75, fill=blue, width=28)
d.line([(880, 596), (834, 562), (881, 529)], fill=blue, width=24, joint="curve")

img.save("assets/app_icon.png")
img.save("assets/app_icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
