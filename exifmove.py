import os
import sys
from pathlib import Path
from exif import Image
import click
import datetime


def get_exif_date(image_file):
    ''' Extracts exif date from a file. Provide full path to file as string. 
    Returns: pathlib.Path object '''
    try:
        with open(image_file, 'rb') as file_handle:
            my_image = Image(file_handle)
            date_str = my_image.datetime
            date = datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            return date
    except:
        return False


def get_dst_file(dst_root, image_file, img_date):
    ''' Returns full path with filename to the destination when given a root-dst folder
    a full path and a image date is provided'''
    img_dst_folder = img_date.strftime("%Y-%m-%d")
    img_dst_name = Path(image_file).name
    img_dst = Path(dst_root) / str(img_date.year) / img_dst_folder / img_dst_name
    return img_dst

    
def get_jpgs(path):
    ''' Generator the returns all the jpg files in provided folder.
    Each file is returned as a pathlib.Path object'''
    for dir_name, subdirList, fileList in os.walk(path):
        for fname in fileList:
            src_img = Path(os.path.join(dir_name, fname))
            extension = src_img.suffix.lower()
            if (extension == ".jpg"):
                yield src_img


def get_file_date(filename):
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))
    


def exif_move(source_dir, destination_dir, delete_oldest):
    ''' Internal move command that does all the work. This is invoked by click-cmd-line
    Functionality is explained in exifmove function '''
    for src_file in get_jpgs(source_dir):
        img_date = get_exif_date(src_file)
    
        if img_date:
            dst_file = get_dst_file(destination_dir, src_file, img_date)
            if src_file != dst_file: # Only move files that are in the wrong place
                os.makedirs(dst_file.parent, exist_ok=True)
                if dst_file.exists():
                    print(f'Target Exist: {src_file} -> {dst_file}')
                    if delete_oldest:
                        src_date = get_file_date(src_file)
                        dst_date = get_file_date(dst_file)
                        if src_date < dst_date:
                            src_file.unlink()
                            print(f'Old deleted in src: {src_file}')
                        else:
                            dst_file.unlink()
                            print(f'Old deleted in dst: {dst_file}')
                            src_file.rename(dst_file)
                            print(f'Moved: {src_file} -> {dst_file}')
                else: 
                    src_file.rename(dst_file)
                    print(f'Moved: {src_file} -> {dst_file}')
            else:
                print(f'OK: {src_file}')
        else:
            print(f'No exif date: {src_file}')
            

@click.command()
@click.argument('source-dir', type=click.Path(exists=True))
@click.argument('destination-dir', type=click.Path(exists=True), required=False)
@click.option('--delete-oldest', '-d', default=False, is_flag=True, help='If this parameter provided the oldest file is deleted if filename exists in both source and destination dir') 
def exifmove(source_dir, destination_dir, delete_oldest):
    '''
    This cmd will scan through all the files in the SOURCE_DIR for jpg-files. When
    a file is found, the exif date is extracted. Then the DESTINATION_DIR is scanned
    to see if the file is in /YEAR/YEAR-MONTH-DAY folder. If not, it is moved there.
    If it's already there nothing is done unless --delete-oldest option is 
    provided. If provided, the oldest for the source and destination file will be deleted.
    If DESTINATION_DIR is omitted then destination will be the same as the source.
    '''
    if not destination_dir: destination_dir = source_dir
    exif_move(source_dir, destination_dir, delete_oldest)

if __name__ == '__main__':
    print('Should be run from command line. From package dir run:')
    print('pip install --editable .')
    #exif_move('c:\\temp\\imgtest', 'c:\\temp\\imgtest', True) 
