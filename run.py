import bpy, csv, os, sys
# TODO: Specify the location of the local Git repo:
sys.path.append('/Users/gebruiker/Documents/GitHub/blender-floor-batch/')
from utils.floordata import Floordata, BlenderFloorProcessor, CSVvariations

# DECLARE VARIABLES
camera_name = 'MAIN_CAMERA'
texture_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/textures/'
output_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/output/'
csv_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/assets/demo_floors.csv'

def detect_column_names(header, CSVvariations):
    detected_names = {}
    for standard_name, variations in CSVvariations.items():
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
    column_names = detect_column_names(header, CSVvariations)
    for row in csv_reader:
        sku = row[column_names['sku']]
        if sku == '':
            continue        
        else:            
            size = row[column_names['size']]
            pattern = row[column_names['pattern']]
            grout = row[column_names['grout']]
            suffix = row[column_names['suffix']]
            floor_data = Floordata(sku, size, pattern, grout, suffix, texture_location)
            floordata_list.append(floor_data)

    for i in floordata_list:
        if i.texture_count == 0:
            missing_floordata.append(i.sku)
        else:
            render_floordata.append(i)

# Initiate Blender
processor = BlenderFloorProcessor(camera_name, texture_location, output_location)

# Start batch render process
processor.batch_process(render_floordata)

# Print missing textures
print("\n###############################################")
print("###  Couldn't find the following textures:  ###")
print("###############################################")
print(missing_floordata)