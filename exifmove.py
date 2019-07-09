import os
import sys
from pathlib import Path
from exif import Image
from datetime import datetime
import click


def get_exif_date(image_file):
    ''' Extracts exif date from a file. Provide full path to file as string. 
    Returns: pathlib.Path object '''
    try:
        with open(image_file, 'rb') as file_handle:
            my_image = Image(file_handle)
            date_str = my_image.datetime
            date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
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


def exif_move(source_dir, destination_dir, remove_if_dest_exist):
    ''' Internal move command that does all the work. This is invoked by click-cmd-line
    Functionality is explained in exifmove function '''
    for src_file in get_jpgs(source_dir):
        img_date = get_exif_date(src_file)
    
        if img_date:
            dst_file = get_dst_file(destination_dir, src_file, img_date)
            if src_file != dst_file: # Only move files that are in the wrong place
                os.makedirs(dst_file.parent, exist_ok=True)
                if dst_file.exists():
                    print(f'{src_file} -> {dst_file}   # TARGET ALREADY EXISTS')
                    if remove_if_dest_exist:
                        src_file.unlink()
                        print(f'{src_file}   # REMOVED')
                else: 
                    src_file.rename(dst_file)
                    print(f'{src_file} -> {dst_file}   # MOVED')
            else:
                print(f'{src_file}   # OK PLACED')
        else:
            print(f'{src_file}   # NO EXIF DATE')
            

@click.command()
@click.argument('source-dir', type=click.Path(exists=True))
@click.argument('destination-dir', type=click.Path(exists=True), required=False)
@click.option('--remove-if-dest-exist', '-r', default=False, is_flag=True, help='If provided then the source file will be deleted if the same filename exists in destination directory')
def exifmove(source_dir, destination_dir, remove_if_dest_exist):
    '''
    This cmd will scan through all the files in the SOURCE_DIR for jpg-files. When
    a file is found, the exif date is extracted. Then the DESTINATION_DIR is scanned
    to see if the file is in /YEAR/YEAR-MONTH-DAY folder. If not, it is moved there.
    If it's already there nothing is done unless --remove-if-dest-exist option is 
    provided. If provided, the source file will be deleted.
    If DESTINATION_DIR is omitted then destination will be the same as the source.
    '''
    if not destination_dir:
        destination_dir = source_dir
    exif_move(source_dir, destination_dir, remove_if_dest_exist)

if __name__ == '__main__':
    print('Should be run from command line')
    #exif_move('c:\\temp\\imgtest', 'c:\\temp\\imgtest', True) 
