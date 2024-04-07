# Short description
Set up a render queue for multiple floors in Blender
Using Floor Generator 2.0 by NodeCrafted https://blendermarket.com/products/floor-generator (you require a license to use the file, go buy it at Blender Market. The use of this script is free.)

Script imports CSV
Writes all floor data into instance of Floordata class
Changes all textures and tile size in the floor generator
Renders 'MAIN_CAMERA'

# BEFORE YOU RUN THIS SCRIPT
Make sure to make the following changes in the Floor Generator 2.0 Blendfile:
- Floor object should be called 'floor'
- Floor material should be called 'floor_material'
- Render camera should be called 'MAIN CAMERA'
- The 9 TEXTURE NODES in floor material should be called **tex00, tex01, tex02 ... tex08**

# TO DO
Possibly create separate settings file
If less than 9 textures found, make sure multi texture node connects correct amount of textures
Implement patterns and grouts