# TODO: Specify the location of the local Git repo:
github_repo_location = r'C:\Users\Jasper\Documents\GitHub\blender-floor-batch'

import bpy, csv, os, sys, importlib
from PIL import Image, ImageStat
sys.path.append(github_repo_location)
import utils.floordata
from utils.floordata import Floordata, BlenderFloorProcessor, writing_variations

def fix_directory(directory):
    directory = directory.replace('\\', '/')
    if directory[-1] != '/':
        directory += '/'
    return directory

github_repo_location = fix_directory(github_repo_location)

# DECLARE VARIABLES
min_light, max_light = 4, 13
texture_location = github_repo_location + 'textures/'
output_location = github_repo_location + 'output/'
csv_location = github_repo_location + 'assets/demo_floors.csv'

def detect_column_names(header, writing_variations):
    detected_names = {}
    for standard_name, variations in writing_variations.items():
        for variation in variations:
            if variation in header:
                detected_names[standard_name] = variation
                break
    return detected_names

floordata_list = []
render_floordata = []
missing_floordata = []
with open(csv_location) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    header = csv_reader.fieldnames
    column_names = detect_column_names(header, writing_variations)
    for row in csv_reader:
        sku = row[column_names['sku']]
        if sku == '':
            continue        
        else:            
            size = row[column_names['size']]
            pattern = row[column_names['pattern']]
            grout = row[column_names['grout']]
            suffix = row[column_names['suffix']]
            scene = row[column_names['scene']]
            # Dynamically reload the floordata module before creating Floordata objects
            importlib.reload(utils.floordata)
            floor_data = Floordata(sku, size, pattern, grout, suffix, texture_location, scene)
            floordata_list.append(floor_data)

    for i in floordata_list:
        if len(i.textures) == 0:
            missing_floordata.append(i.sku)
        else:
            render_floordata.append(i)

# Initiate Blender
processor = BlenderFloorProcessor(texture_location, output_location, min_light, max_light)

# Start batch render process
processor.batch_process(render_floordata)

# Print missing textures
print("\n###############################################")
print("###  Couldn't find the following textures:  ###")
print("###############################################")
print(missing_floordata)