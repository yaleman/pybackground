#!/usr/bin/env python
""" takes an image and overlays stdin, pretty hacky but worked for me. """

import os

# make these sane paths if you want, this is so it can run from wherever.
SOURCEFILE = '{}/input.jpg'.format(os.path.dirname(os.path.realpath(__file__)))
DESTFILE = '{}/output.jpg'.format(os.path.dirname(os.path.realpath(__file__)))

# season to taste
OUTPUT_SIZE = (1280, 800)

# mercilessly pilfered with love from https://github.com/adobe-fonts/source-sans-pro
FONT_FILENAME = '{}/source-sans-pro-regular.ttf'.format(os.path.dirname(os.path.realpath(__file__)))
FONT_SIZE = 25
# white, mostly opaque
FONT_RGBA = (255, 255, 255, 240)

import argparse
import sys
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Please install PIL/pillow")




# deal with command line arguments
parser = argparse.ArgumentParser(description='Take an image and stdin, overlay it.')
parser.add_argument('--debug', dest='debug', action='store_true', help='debug mode')
args = parser.parse_args()

# open the image, if you can
if os.path.exists(SOURCEFILE):
    im = Image.open(SOURCEFILE).convert('RGBA')
else:
    sys.exit("Couldn't find file {}".format(SOURCEFILE))

# show the stats
if args.debug:
    print("Input image stats: {}".format((im.format, im.size, im.mode)))

# resize the image
im = im.resize(OUTPUT_SIZE, resample=Image.LANCZOS)
if args.debug:
    print("Output image stats: {}".format((im.format, im.size, im.mode)))

# make a blank image for the text, initialized to transparent text color
txt = Image.new('RGBA', im.size, (255, 255, 255, 0))

# load the font
fnt = ImageFont.truetype(FONT_FILENAME, FONT_SIZE)
# make a drawing object
drawobj = ImageDraw.Draw(txt)

# initial text location
texty = OUTPUT_SIZE[1] - (FONT_SIZE + (FONT_SIZE / 2))
# take reversed STDIN and work up from the bottom
for line in list(sys.stdin)[::-1]:
	# draw text, full opacity
    drawobj.text((FONT_SIZE / 3, texty), line, font=fnt, fill=FONT_RGBA)
	# move the "insertion point"
    texty -= (FONT_SIZE * 1.2)

# compose the image
out = Image.alpha_composite(im, txt)

out.save(open(DESTFILE, 'w'), "JPEG")
