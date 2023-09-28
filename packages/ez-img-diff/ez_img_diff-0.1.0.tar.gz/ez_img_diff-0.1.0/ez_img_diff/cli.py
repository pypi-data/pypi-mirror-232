"""This is the primary entrypoint for the img_diff script

```bash
Usage: 
    img_diff [-h] [-v]
    img_diff (<img1> <img2>) [-o OUTPUT_FOLDER] 
    
Options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -o OUTPUT_FOLDER, --output OUTPUT_FOLDER 
                        the folder to output difference files to
```
"""
import os
import sys


from ez_img_diff import __version__
from docopt import docopt
from ez_img_diff.api import compare_images


usage = """ez img diff

A tool for doing quick perceptual image difference analysis

Usage: 
    img_diff [-h] [-v]
    img_diff (<img1> <img2>) [-o OUTPUT_FOLDER] 

Options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -o OUTPUT_FOLDER, --output OUTPUT_FOLDER 
                        the folder to output difference files to
"""

def main():
    """The primary entrypoint for img_diff script for help run: `img_diff -h`"""
    if len(sys.argv) == 1:
        print("\n", usage)
        sys.exit()
    args = docopt(usage, version=__version__)
    if args["--output"]:
        if not os.path.isdir(args["--output"]):
            os.mkdir(args["--output"])
        diff = compare_images(args["<img1>"], args["<img2>"], os.path.join(args["--output"], "diff.png"), os.path.join(args["--output"], "thresh.png"))
    else:
        diff = compare_images(args["<img1>"], args["<img2>"])
    print(diff) # Show result to stdout so it can be piped into other programs
    

if __name__ == "__main__": # Code inside this statement will only run if the file is explicitly called and not just imported.
    pass