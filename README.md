# Short description
Set up a render queue for multiple floors in Blender
Using Floor Generator 2.0 by NodeCrafted https://blendermarket.com/products/floor-generator (you require a license to use the file, go buy it at Blender Market. The use of this script is free.)

Script imports CSV
Writes all floor data into instance of Floordata class
Changes all textures, tile sizes and patterns in the floor generator
Renders 'MAIN_CAMERA'

# BEFORE YOU RUN THIS SCRIPT
<!-- Make sure to make the following changes in the Floor Generator 2.0 Blendfile: -->
<!-- - Regular floor object should be called: 'floor_regular', for herringbone: 'floor_herringbone' -->
<!-- - Regular floor material should be called: 'floor_mat_regular', for herringbone: 'floor_mat_herringbone' -->
- Render camera should be called 'MAIN_CAMERA'
<!-- - The 9 TEXTURE NODES in both floor materials should be named AND labeled **tex00, tex01, tex02 ... tex08** -->
<!-- - The MultiTexture Group in both floor materials (the one with the 16 outputs) must be named AND labeled 'MultiTexGroup' -->
<!-- - The reroute node in both floor materials next to the MultiTexGroup must be named AND labeled 'MultiTexReroute' -->

# TO DO
Possibly create separate settings file
Implement grouts