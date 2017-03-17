#!/usr/bin/env python
# coding=utf-8

""" takes an image and overlays stdin, pretty hacky but worked for me. """

# import all the things
from os import path, listdir
from random import choice
import re
from argparse import ArgumentParser
from sys import stdin
import colorsys
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    exit("Please install PIL/pillow")

# make these sane paths if you want, this is so it can run from wherever.
SOURCEFILE = '{}/input.jpg'.format(path.dirname(path.realpath(__file__)))
DESTFILE = '{}/output.jpg'.format(path.dirname(path.realpath(__file__)))

# season to taste
OUTPUT_SIZE = (1280, 800)
DEFAULT_QUALITY=85
# mercilessly pilfered with love from https://github.com/adobe-fonts/source-sans-pro
FONT_FILENAME = '{}/source-sans-pro-regular.ttf'.format(path.dirname(path.realpath(__file__)))
FONT_SIZE = 25
# white, mostly opaque
FONT_RGBA = (255, 255, 255, 240)

# deal with command line arguments
parser = ArgumentParser(description='Take the text from STDIN and overlay it on an image.')
parser.add_argument('-D', '--debug', dest='debug', action='store_true', help='enable debug mode')
parser.add_argument('-q', '--quality', type=int, default=DEFAULT_QUALITY, dest='quality', help='set jpeg quality, default is 85')
parser.add_argument('-s', '--size', dest='output_size', default="{}x{}".format(*OUTPUT_SIZE), help='dimensions of output eg. 800x600')
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', '--input', dest='sourcefile', default=SOURCEFILE, help='source file to use - default is "input.jpg"')
group.add_argument('-r', '--randomdir', dest='randomdir', default=False, help='directory to pull random file from')
args = parser.parse_args()

image_extensions = ('jpeg', 'png', 'bmp', 'jpg', 'tif')

# make sure it's vaguely right
if re.match(r'\d+x\d+', args.output_size):
    OUTPUT_SIZE = args.output_size.split("x")
    x, y = OUTPUT_SIZE
    OUTPUT_SIZE = (int(x), int(y))
elif args.output_size:
    print("Invalid output size specified: '{}' ignoring.".format(args.output_size))

if args.debug:
    print("Output dimensions: '{}'".format(OUTPUT_SIZE))

if args.randomdir:
    fileoptions = listdir(args.randomdir)
    files = [filename for filename in fileoptions if filename.lower().split(".")[-1] in image_extensions]
    #random.choice(os.listdir('/Users/yaleman/Dropbox/dotfiles/Wallpapers/'))
    args.sourcefile = "{}/{}".format(args.randomdir, choice(files))

# open the image, if you can
if path.exists(args.sourcefile):
    if args.debug:
        print("Opening: {}".format(args.sourcefile))
    baseimage = Image.open(args.sourcefile).convert('RGBA')
else:
    exit("Couldn't find file {}".format(args.sourcefile))

# show the stats
if args.debug:
    print("Input image stats: {}".format((baseimage.format, baseimage.size, baseimage.mode)))

# resize the image
baseimage = baseimage.resize(OUTPUT_SIZE, resample=Image.ANTIALIAS)
if args.debug:
    print("Output image stats: {}".format((baseimage.format, baseimage.size, baseimage.mode)))

# make a blank image for the text, initialized to transparent text color
textimage = Image.new('RGBA', baseimage.size, (255, 255, 255, 0))

# load the font
fontobject = ImageFont.truetype(FONT_FILENAME, FONT_SIZE)
# make a drawing object
drawobj = ImageDraw.Draw(textimage)
# grab stdin because we'll use it a few times
textlines = stdin.readlines()

# work out the average colour for the text box
# had the basic idea, but this helped: http://grokbase.com/t/python/python-list/061p3cg5r2/dominant-color-pil
textbox_y = len(textlines) * (FONT_SIZE * 1.2) + (FONT_SIZE / 2)
# I love python list comprehensions.
textbox_x = max([drawobj.textsize(line, fontobject)[0] for line in textlines]) + (FONT_SIZE / 3)

x0, y0 = 0.0, OUTPUT_SIZE[1]-textbox_y
x1, y1 = textbox_x, OUTPUT_SIZE[1]-1
# pull out the text box area
cropbox = baseimage.crop((int(x0), int(y0), int(x1), int(y1)))

if args.debug:
    print("textbox_y:{}".format(textbox_y))
    print("textbox_x:{}".format(textbox_x))
    print("Adding text bounding box: ({}, {}) ({}, {})".format(x0, y0, x1, y1))
    drawobj.rectangle([(x0, y0), (x1, y1)], outline=(255, 0, 0, 255))
    print("Dumping cropbox image to cropbox.jpg")
    cropbox.save(open('cropbox.jpg', 'w'), "JPEG")
# find the average colour by shrinking it to a single pixel
cropbox = cropbox.resize((1, 1), resample=Image.ANTIALIAS).resize((100, 100))
averagecolour = cropbox.getpixel((0, 0))
# process from http://serennu.com/colour/rgbtohsl.php
# 1. Convert your colour to HSL.
averagecolour = [colour/255.0 for colour in averagecolour[:3]]
hls = colorsys.rgb_to_hls(*averagecolour)

# 2. Change the Hue value to that of the Hue opposite (e.g., if your Hue is 50°, the opposite one will be at 230° on the wheel — 180° further around).
newhls = (abs(hls[0]-1.0), abs(1.0-hls[1]), hls[2])
#3. Leave the Saturation and Lightness values as they were.
#4. Convert this new HSL value back to your original colour notation (RGB or whatever).
newrgb = colorsys.hls_to_rgb(*newhls)
newrgb = (int(255*newrgb[0]), int(255*newrgb[1]), int(255*newrgb[2]))

if args.debug:
    print("Averaged colour seq: {}".format(averagecolour))
    print("Dumping average image")
    cropbox.save(open('cropbox-average.jpg', 'w'), "JPEG")
    print("RGB:  {}".format(averagecolour[:3]))
    print("HLS:  {}".format(hls))
    print("RGB2: {}".format(newrgb))
    print("HLS2: {}".format(newhls))

# initial text location
texty = OUTPUT_SIZE[1] - (FONT_SIZE + (FONT_SIZE / 2))
# take reversed STDIN and work up from the bottom
for line in list(textlines)[::-1]:
	# draw text, full opacity
    #drawobj.text(((FONT_SIZE / 3)+2, texty+2), line, font=fontobject, fill=averagecolour) # was FONT_RGBA
    drawobj.text((FONT_SIZE / 3, texty), line.strip(), font=fontobject, fill=newrgb) # was FONT_RGBA
	# move the "insertion point"
    texty -= (FONT_SIZE * 1.2)

# compose the image
out = Image.alpha_composite(baseimage, textimage)



out.save(open(DESTFILE, 'w'), "JPEG", quality=args.quality, progressive=True, optimize=True)
