Take an image and overlay it with text from stdin.

Requires the PIL or pillow library to be installed.

    usage: pybackground.py [-h] [-D] [-q QUALITY] [-i SOURCEFILE | -r RANDOMDIR]

    Take the text from STDIN and overlay it on an image.

    optional arguments:
    -h, --help            show this help message and exit
    -D, --debug           enable debug mode
    -q QUALITY, --quality QUALITY
                            set jpeg quality, default is 85
    -i SOURCEFILE, --input SOURCEFILE
                            source file to use - default is "input.jpg"
    -r RANDOMDIR, --randomdir RANDOMDIR
                            directory to pull random file from