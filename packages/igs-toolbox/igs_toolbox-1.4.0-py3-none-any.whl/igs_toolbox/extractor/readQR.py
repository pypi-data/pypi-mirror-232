# Requirements
# mamba install poppler

# Import modules
import os
import sys
from pdf2image import convert_from_path
import cv2
import argparse
import logging
import igs_toolbox
from os.path import basename


def read_qr_code(filename):
    try:
        img = cv2.imread(filename)
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(img)
        return value
    except Exception:
        return "Error during QR code detection."


def main(args=None):
    input_files = parse(args).files
    for file in input_files:
        if not os.path.isfile(file):
            logging.error(f"{file} does not point to a file. Aborting.")
            sys.exit(1)

    # Iterate over files
    if len(input_files) > 0:
        for file in input_files:
            filename = basename(file).split(".")[0]
            images = convert_from_path(file)

            # Go through pages and save them as PNG
            for i in range(len(images)):
                pageName = f"{file}_{str(i)}.png"
                images[i].save(pageName, "PNG")

                # Detect QR code and print it
                id = read_qr_code(pageName)
                print(f"{filename}\t{id}")
                os.remove(pageName)
    else:
        sys.exit(2)


# Read command line arguments
def parse(args=None):
    parser = argparse.ArgumentParser(prog=basename(__file__).split(".")[0])
    parser.add_argument("files", nargs="*")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {igs_toolbox.__version__}",
    )
    args = parser.parse_args(args)
    return args


if __name__ == "__main__":
    main()
