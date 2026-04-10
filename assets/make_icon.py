from PIL import Image, ImageDraw
import math

size = 256
img = Image.new('RGBA', (size, size), (223, 241, 255, 255))

draw = ImageDraw.Draw(img)

# Sun
sun_center = (78, 88)
sun_r = 42
draw.ellipse([sun_center[0]-sun_r, sun_center[1]-sun_r, sun_center[0]+sun_r, sun_center[1]+sun_r], fill=(255, 198, 64, 255))

# Rays
for angle in range(0, 360, 30):
    r1 = sun_r + 8
    r2 = sun_r + 22
    x1 = sun_center[0] + r1 * math.cos(math.radians(angle))
    y1 = sun_center[1] + r1 * math.sin(math.radians(angle))
    x2 = sun_center[0] + r2 * math.cos(math.radians(angle))
    y2 = sun_center[1] + r2 * math.sin(math.radians(angle))
    draw.line([x1, y1, x2, y2], fill=(255, 198, 64, 255), width=6)

# Cloud
cloud_color = (90, 156, 214, 255)
shadow = (60, 120, 170, 255)

draw.rounded_rectangle([70, 120, 210, 200], radius=36, fill=cloud_color)

draw.ellipse([60, 130, 130, 200], fill=cloud_color)
draw.ellipse([110, 110, 190, 190], fill=cloud_color)

draw.line([70, 200, 210, 200], fill=shadow, width=6)

img.save('assets/icon.png')
img.save('assets/icon.ico', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
