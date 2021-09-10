__author__ = 'Junghwan Kim'
__copyright__ = 'Copyright 2016-2019 Junghwan Kim. All Rights Reserved.'
__version__ = '1.0.0'

import os
from PIL import Image, ImageDraw, ImageFont
import shutil
import json
import ast


def main():
    global num

    # Set path
    path = '/home/jkim/nas/members/sko/SHARE/2019/0118/SET1/1785964_20190113'
    path_img = '/home/jkim/nas/members/sko/SHARE/2019/0118/SET1/1785964_20190113/IMG'
    path_map = '/home/jkim/nas/members/sko/SHARE/2019/0118/SET1/1785964_20190113/MAP2'
    path_png = '/home/jkim/nas/members/sko/SHARE/2019/0118/SET1/1785964_20190113/png'

    # Read JSON file
    with open('/home/jkim/nas/members/sko/SHARE/2019/0118/SET1json/1785964_20190113.out') as f:
        data = json.load(f)
    data = ast.literal_eval(json.dumps(data))

    i = 0
    dict = {}
    while i < 32:
        key = data['diagnosis'][i]['case']
        value = data['diagnosis'][i]['legend']
        dict[key] = value
        i += 1

    i = 0
    dict_nor = {}
    while i < 32:
        key = data['diagnosis'][i]['case']
        value = data['diagnosis'][i]['classification']
        if value[0][0] == 'NOR':
            value_nor = value[0][1]
        else:
            value_nor = value[1][1]
        dict_nor[key] = value_nor
        i += 1

    i = 0
    dict_abn = {}
    while i < 32:
        key = data['diagnosis'][i]['case']
        value = data['diagnosis'][i]['classification']
        if value[0][0] == 'ABN':
            value_abn = value[0][1]
        else:
            value_abn = value[1][1]
        dict_abn[key] = value_abn
        i += 1

    # Function
    def append_list(path, list, label):
        for paths, dirs, files in sorted(os.walk(path)):
            for name in sorted(files):
                if name.endswith(label):
                    list.append(name)

        return None

    # New folder
    print '[INFO] Making the result folder...'
    if not os.path.exists(path_img):
        os.makedirs(path_img)
    else:
        shutil.rmtree(path_img)
        os.makedirs(path_img)
    print '[SUCCESS] Made it successfully.\n'

    # Initialize list
    list = []
    list_fill = []
    list_line = []

    # Append list
    print '[INFO] Creating the image list. It takes a lot of time. Please wait...'
    append_list(path_png, list, '.png')
    append_list(path_map, list_fill, 'fill.png')
    append_list(path_map, list_line, 'line.png')
    print '[SUCCESS] Created all list.\n'

    # Validate list
    print '[INFO] Checking the validation...'
    if len(list) == len(list_fill) == len(list_line):
        pass
    else:
        print '[ERROR] List size is different.'
        exit(1)
    print '[SUCCESS] Passed the validation.\n'

    # Overlay anatomy
    print '[INFO] Making the overlay image...'
    num = 1
    total = len(list)

    def overlay(list, list_label):
        global num
        os.makedirs(path_img + '/temp')
        for name, name_label in zip(sorted(list), sorted(list_label)):
            img = Image.open(path_png + '/' + name)
            img = img.convert('RGBA')
            img_label = Image.open(path_map + '/' + name_label)
            img_new = Image.new("RGBA", img.size)
            img_new.paste(img, (0, 0), img)
            img_new.paste(img_label, (0, 0), img_label)
            img_new.save(path_img + '/temp/' + name)
            progress = '(' + str(num) + '/' + str(total) + ')'
            print progress, 'Overlay is completed:', path_img + '/temp/' + name
            num += 1

        return None

    overlay(list, list_fill)

    # Merge images
    print '\n[INFO] Merging the three images...'
    i = 1
    for name, name_fill, name_line in zip(sorted(list), sorted(list_fill), sorted(list_line)):
        img1 = Image.open(path_png + '/' + name)
        img2 = Image.open(path_map + '/' + name_fill)

        img_width, img_height = img1.size
        img_size = (img_width*2, img_height)
        img_new = Image.new("RGB", img_size)
        img_new.paste(img1, (0, 0), img1)
        img_new.paste(img1, (img_width, 0), img1)
        img_new.paste(img2, (img_width, 0), img2)

        draw = ImageDraw.Draw(img_new)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 18)
        legend = str(dict[name[:-4]])[1:-1]
        legend = legend.replace("'", "")
        draw.text((10, 10), name, font=font, fill=(255,255,255))
        draw.text((10, 30), 'NOR: ' + str(dict_nor[name[:-4]]), font=font, fill=(0, 255, 0))
        draw.text((10, 50), 'ABN: ' + str(dict_abn[name[:-4]]), font=font, fill=(255, 0, 0))
        draw.text((img_width + 10, 10), legend, font=font, fill=(100, 200, 255))

        img_new.save(path_img + '/' + name)
        progress = '(' + str(i) + '/' + str(len(list)) + ')'
        print progress, 'Merging is completed:', path_img + '/' + name
        i += 1

    # Delete temp images
    shutil.rmtree(path_img + '/temp')
    print '[SUCCESS] Finished all process.'

    return None


if __name__ == '__main__':
    main()
