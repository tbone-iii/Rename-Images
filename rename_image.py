# python3

""" Rename images given with a common regex string type by hand.
    Sweeps through all files in a given directory and renames
    with the date. E.G. "20190413 - <user input string>"
"""

import re
from PIL import Image, ImageFile
import os
import argparse


# Function for retrieving the date of an image using PIL's image
def get_date_taken(path, image):
    """ Gets the date of when image was taken."""
    return image._getexif()[36867]


# Renaming function which accounts for multiple copies
def rename(old_pathname, directory, new_name, extension):
    """ Renames the image given the old path name and the new path name. """
    try:
        os.rename(old_pathname, os.path.join(directory, new_name + extension))
    except WindowsError as e:
        if e.winerror == 183:
            new_name = input(
                f'\nFile name  "{new_name}" already exists...'
                ' rename the file.\nFile name: ')
            rename(old_pathname, directory, new_name, extension)
        else:
            raise('Unhandled WindowsError')


# Determines the new name for the file based on date and user input
def new_file_name(_file_absolute, image, extension):
    """ Requests a user input for the new file name
        and determine the date format.
    """
    new_name = input('File name:         ')
    if new_name:
        # Remove illegal characters and strip spaces
        new_name = new_name.replace(r'\/:*?"<>|', '')
        new_name = new_name.strip()

        # Get date of image taken
        try:
            if extension in ['.jpg', '.JPG']:
                date = get_date_taken(path=_file_absolute, image=image)
            else:
                date = input('Write the date:    ')
        except KeyError as e:
            if e.args[0] == 36867:
                date = '_'
            else:
                raise Exception(f'\nUnhandled KeyError: {e}')

        # Convert the string in the following manner:
        # '2018:06:30 15:04:33' to '20180630'
        date = date[0:10].replace(':', '')

        # Finalize file name with the desired format:
        # 'YYYYMMDD - <text>'
        new_name = date + ' - ' + new_name
    else:
        # if there's no user input for file name, leave the name alone
        return None
    return new_name


# Main code of the rename_image feature
def main():
    # Load truncated images to prevent lazy loading by PIL
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # Parse through given options in the command line.
    parser = argparse.ArgumentParser(
        description='Rename some images in a directory.')
    parser.add_argument('directory', type=str,
                        help='the path of the directory to be used')
    parser.add_argument('file_name_pattern', metavar='file name pattern',
                        help='the regex pattern for the image file names')

    args = parser.parse_args()
    directory = args.directory
    file_name_pattern = args.file_name_pattern

    # File types to search for
    file_types = ['.png', '.jpg', '.tiff', '.bmp', '.JPG', '.PNG', '.BMP']

    # TODO: Add verbose option for explaining this.
    # Establish the regex string. Here is an example for file names that look
    # like the following:
    # file: "IMG_20180603_144921372.jpg"
    # regex: "IMG_\d+_.+"
    re_string = re.compile(file_name_pattern)

    # Search through the directory for file
    for _file in os.listdir(directory):
        # Defines the absolute path of the file
        _file_absolute = os.path.join(directory, _file)

        # If any file ends with the listed image file types AND fits the regex
        if (any(list(map(_file.endswith, file_types)))
                and re.search(re_string, _file)):
            # Open the image file
            with Image.open(_file_absolute) as image:
                # Print the current file name
                print(f'\nCurrent file name: {_file}')

                # Show the image
                image.show()

                # Determine the file extension
                _, extension = os.path.splitext(_file)

                # Request a new name for the file
                new_name = new_file_name(_file_absolute, image, extension)

                # Rename the image file
                if new_name:
                    rename(_file_absolute, directory, new_name, extension)
                else:
                    # if the input is empty, do nothing to the image name
                    pass

    print('\nAll available image files renamed!')


# Runs main() code if this file is directly called.
if __name__ == '__main__':
    main()
