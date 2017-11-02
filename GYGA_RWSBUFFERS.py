#!/usr/bin/python
# -*- coding: utf-8 -*-

########################################################################################################
########################################################################################################
"""
GYGA Python script for constructing and selecting  RWS buffer zones
Plant Production Systems, Wageningen UR, Sander C. de Vries, May 2016
Updates can be downloaded from https://github.com/sandercdevries/GYGA-tools

Requirements:
- A version of ESRI ArcMap/ArcGIS, including a Spatial Analyst license 
(from within WUR, you can get that licence online, using the ArcGIS Administrator program on your computer)
- Python 2.7. Your Python installation needs to be ‘linked’ with ArcGIS, so if you already have another Python installation 
on your computer (e.g. Anaconda), do not use that, but use the installation that came with ArcGIS.
Normally the latter can be found in the root of the (C) drive, in a folder C:/Python27/Arcgis10.3. 
In some cases, it may be installed on another drive (D, E, F, etc.)

How to run the script under Windows:
- Simply run it, using the Python 2.7 installation that came with ArcGIS, e.g. in C:/Python27/Arcgis10.3’
If you run in from another installation, you may not be able to import the AcrGIS 'arcpy' module. 

What the script actually does:
- First, it will interactively ask you to provide the paths to a number of required input files (map layers). 
Most of these can be downloaded from http://www.yieldgap.org/web/guest/download_data
- If you already ran the script before, it will ask you to confirm whether you want to use the same inputs again.
 
Inputs required by the script (no worries, it will ask for them) are:
- A shapefile with weather station point locations, either real stations or hypothetical weatherstations. 
The latter may be comprised of a grid of arbitrary locations, or of a file containing point locations of villages
In case of a large number of points, the script may not be able to handle it. 
- A global country borders shapefile, preferably GAUL0.shp (if another file is used, the script will probably need to be adapted)
- The global GYGA climate zonation shapefile, or raster file, depending on the method that you choose in the script. 
- A (global) map of the harvested area of the relevant crop, in GeoTIFF format, obtained from www.mapspam.info 
- Secondly, when above input requirements are met, the script will start constructing RWS buffer zones (http://www.yieldgap.org/web/guest/methods-upscaling) 
Thirdly, it will:
- Calculate the total harvested crop area for the whole country (based on SPAM)
 Calculate the harvested crop area per CZ
- For CZs covering more than 5% of the national harvested crop area, the harvested crop area covered by each individual RWS buffer 
situated within that CZ is calculated. 
- Results will appear on-screen but are also saved in a *.csv file in the same folder where the GYGA_RWSBUFFERS.py script itself is located 
(it will also save all your settings there in a *.cfg file):

In the end, the script will ask whether some of the created ArcGIS layers can be deleted. 
Particularly the file ending with “_Buffers_Dissolved” is handy to keep for future reference: it contains (all) buffer zones. 
If you want a shapefile with only the relevant stations (i.e., the ones in the list, with the ‘right’ percentages, you can manually select 
them in the attribute table of that layer in ArcGIS (of course it could be done automatically by the script in the future). *Todo
Good luck!
SdV

$Author: SanderCdeVries $
"""
########################################################################################################
# Setting screen dimensions:
import os
import subprocess
import time
import re
subprocess.call("mode con:cols=120 lines=100", shell = True)
subprocess.call("color 17", shell = True)

print"*********************************************************************************************************"
print "                 GYGA script for constructing and selecting  RWS buffer zones, Version 1.0"
print "                    Sander de Vries, Plant Production Systems, Wageningen UR, May 2016"
print "             - Download updates or contribute via https://github.com/sandercdevries/GYGA-tools -" 
print"*********************************************************************************************************"
print '\n'

ln1 = "Please provide name and location of the geodatabase(.gdb) in which you want to store your results." 
ln2 = "E.g. D:\\UserData\\vries176\\Default.gdb (you can paste it here by right-clicking) " + "\n"
ln3 = "Please provide name and location of the original GYGA Climate Zonation (CZ) shapefile that you plan to use."
ln4 = "E.g. D:\\Downloads\\GYGA\\CZ_AllWorld\\CZ_CNTRY_ALLWORLD.shp (paste = right-click) "
ln5 = "Please provide name and location of the GAUL0.shp country borders shapefi."
ln6 = "E.g. D:\\Downloads\\GYGA\\Country_shapefile_World\\GAUL0.shp (paste = right-click) "
ln7 = "Please provide name and location of a shapefile with relevant weather station (point) locations."
ln8 = "E.g. D:\\userdata\\vries176\\vriesrun1_.shp (paste = right-click) "
ln9 = "Please provide the location of the SPAM (cropping area) geotiff for the relevant crop."
ln10 = "E.g. D:\\Downloads\\GYGA\\harvested-area-SPAM-18-aug-2014\\maiz_r.tiff (paste = right-click) "
ln11 = "Please enter the name of the country you want to analyze. The name (e.g. South Africa) should correspond"
ln12 = "exactly with the name in the Country borders shapefile (GAUL0.shp), including capitalization. "
ln13 = "Please provide name and location of the original GYGA climate zonation raster file."
ln14 = "E.g. D:\\downloads\\gyga\\GygaClimateZonesTif_FROM WEBSITE\\GYGA_ED.tif (paste = right-click) "    

print "Please provide a short run identifyer name to precede the names of the layers and files that are created; "
runnam = raw_input("(name should not start with a number): ")
RUNNAM = re.sub('\W+','', runnam) + "_"
print "Ok, thanks, run name (converted to alphanumerics only) is:", re.sub('\W+','', runnam), "\n"

print "For determining the cropping area per GYGA climate zone and weather station buffer zone, do you want"
print "to use the (standard) Points based method (P) or a method using Zonal Statistics (Z, much faster)?"
Zonal_or_Points = ""
while Zonal_or_Points <> "P" and Zonal_or_Points <> "Z":
    zonpo = raw_input("Please enter P or Z, followed by Enter: ")
    Zonal_or_Points = zonpo.upper()
print "Ok, thanks!", "\n"
if Zonal_or_Points == "P":
    PointsMethod = True
elif Zonal_or_Points == "Z":
    PointsMethod = False
else:
    print "Unknow error, please press Ctrl + c to quit..."
    time.sleep(100)



# Importing required python modules:
print "Importing arcpy Python module from ArcMap...",
try:
    import arcpy
except:
    print "No valid ArcMap license found, not able to run this script :("
    print "Please press Ctrl + c to quit"
    time.sleep(1000)
print "done;", "\n"
    
# Check for Spatial Analyst license:
SAL = arcpy.CheckOutExtension("Spatial")
if SAL == "NotInitialized" or SAL == "Unavailable":
    print "No Spatial Analyst license found, not able to to run this script :("
    print "Please press Ctrl + c to quit"
    time.sleep(1000)
elif SAL == "CheckedOut" and PointsMethod == True:
    from   arcpy.sa import *
    print "Do you prefer to use the original (global!) GYGA CZ Raster and convert it to points (S, very slow) or use a"
    use_gyga_raster = raw_input("country-level GYGA CZ Shapefile created by this script and convert it to points (F, faster; please enter S/F)? ")
    Use_GYGA_Raster = use_gyga_raster.upper()
    print "Ok, thanks!", "\n"
elif SAL == "CheckedOut" and PointsMethod == False:
    from   arcpy.sa import *
    print "Initializing Zonal Statistics method..."
    Use_GYGA_Raster = "Raster file not used"



# Set overwrite mode:
arcpy.env.overwriteOutput = True
# Get working directory:
workingfolder = os.getcwd()


########################################################################################################
# Defining functions for some frequently occurring actions:

def askinput(file_or_folder, line1, line2):
    Check = False
    print line1
    print line2
    #print "You may copy the location and then paste it by right-clicking with the mouse: "
    while Check == False or Check == "": # not Check
        try:
            Directory = raw_input("")
            if file_or_folder == "folder":
                Check = os.path.isdir(Directory)
            elif file_or_folder == "file":
                Check = os.path.isfile(Directory)
            elif file_or_folder == "":
                Check = True
            else:
                print "It should be indicated in the code whether this refers to a file or a folder, but code says: ", file_or_folder, "?"
                print "Please press Ctrl + c to quit"
                time.sleep(1000)
            if Check == False:
                print "\n", "This", file_or_folder, "does not exist, please check carefully and re-enter...", "\n"
            else:
                print "Ok, thanks!", "\n"
        except TypeError:
            Check = False
            print "\n", "You may have entered something strange? Please re-enter:", "\n"
    return Directory

# A function just to add "_ftl" (for feature layer) to a layer name:
def ftl_name(layername):
    feature_layer_name = layername + "_ftl"
    return feature_layer_name


########################################################################################################
# Set paths to:
# - the Arcmap geodatabase(.gdb) where you want to store your results  
# - GYGA climate zonation shapefile
# - Country borders shapefile (best to use GAUL0.shp; alternatives are possible but may have different column names in the attribute table)
# - Relevant SPAM data raster file (geotiff format; *.tiff)

config_file                   = workingfolder + "\\" + "GYGA_" + "settings.cfg"
config_file_exists            = os.path.isfile(config_file)
results_file                  =  workingfolder + "\\" + "GYGA_" + RUNNAM[:-1] + ".csv"

if  config_file_exists       == True:
    print "Attempting to read previously given file names and paths from configuration file..."
    settings                  = open(config_file, 'r')
    regels                    = settings.readlines()
    settings.close()

    if  len(regels)               == 8:
        settings                   = open(config_file, 'r')
        wrkspc                     = settings.readline()[:-1] # GEODATABASE
        arcpy.env.workspace        = wrkspc
        GYGA_Climate_Zonation_map  = settings.readline()[:-1] # CLIMATE ZONATION
        Country_shapefile_world    = settings.readline()[:-1] # COUNTRY SHAPEFILE WORLD
        print "Analyze the same set of weather stations/same country as in previous run (y/n)? "
        stationcfg                 = settings.readline()[:-1]
        print "This was", stationcfg, 
        same = raw_input("(y/n)? ")
        print "Ok!", "\n" 
        SAME = same.upper()
        if SAME == "N":
            Station_XYs = askinput("file", ln7, ln8) # WEATHER STATIONS  
            #settings.readline()[:-1]
            
            nocolname                 = True
            Column_Names = []
            All_Columns               = arcpy.ListFields(Station_XYs)
            for Column in All_Columns:
                Column_Names.append(str(Column.name))
            while nocolname == True:
                Station_Name_Column       = raw_input("Please enter the name (header) of the the column in this shapefile that contains the weather station names: ")
                if Station_Name_Column in Column_Names:
                    nocolname = False
                else:
                    print "That column does not exist, please retry..."
            print "Ok, thanks!", "\n"
            settings.readline()[:-1]
            
        elif SAME == "Y":
            Station_XYs = stationcfg # WEATHER STATIONS   
            Station_Name_Column = settings.readline()[:-1]
        print "Analyze the same crop as in previous run (y/n)? "
        spamcfg                 = settings.readline()[:-1]
        print "This was", spamcfg,
        same2 = raw_input("(y/n)? ")
        print "Ok!", "\n" 
        SAME2 = same2.upper()
        if SAME2 == "N":
            SPAM_data = askinput("file", ln9, ln10) # SPAM DATA             
            #settings.readline()[:-1]
        elif SAME2 == "Y":
            SPAM_data = spamcfg
        Raster = settings.readline()[:-1]
        print Raster
        if Use_GYGA_Raster == "S" and os.path.isfile(str(Raster)) == False:
            print "Name and location of original GYGA climate zonation raster file not previously given..."
            Raster = askinput("file", ln13, ln14)     
            #Raster                     = settings.readline()[:-1] #   
        settings.close()

if  config_file_exists      == False or len(regels) <> 8:
    print "\n", "No previous run information found (or file not in good order). In order to run the script, please"
    print "enter the names and locations of 5 (or 6) required input files, depending on your preferences:", "\n"
    wrkspc                    = askinput("folder", ln1, ln2) # GEODATABASE
    arcpy.env.workspace       = wrkspc
    GYGA_Climate_Zonation_map = askinput("file", ln3, ln4) # CLIMATE ZONATION
    Country_shapefile_world   = askinput("file", ln5, ln6) # COUNTRY SHAPEFILE WORLD
    Station_XYs               = askinput("file", ln7, ln8) # WEATHER STATIONS   
    nocolname                 = True
    while nocolname == True:
        Station_Name_Column       = raw_input("Please enter the name (header) of the the column that contains the station names: ")
        All_Columns               = arcpy.ListFields(Station_XYs)
        Column_Names = []
        for Column in All_Columns:
            Column_Names.append(str(Column.name))
        if Station_Name_Column in Column_Names:
            nocolname = False
        else:
            print "That column does not exist, please retry..."
    print "Ok, thanks!"    
    SPAM_data                 = askinput("file", ln9, ln10) # SPAM DATA             
    if Use_GYGA_Raster == "S":
        Raster = askinput("file", ln13, ln14)     
    else:
        Raster = "Original GYGA climate zonation raster file: not used"

settings = open(config_file, 'w')    
settings.write(wrkspc + '\n')
settings.write(GYGA_Climate_Zonation_map + '\n')
settings.write(Country_shapefile_world + '\n')
settings.write(Station_XYs + '\n')
settings.write(Station_Name_Column + '\n')
settings.write(SPAM_data + '\n')
settings.write(str(Raster) + '\n')
settings.write("*************end of file***************")
settings.close()    
print "Current settings written to configuration file " , config_file, "\n"


perc_crop_in_DCZ = 5
perc_crop_in_Buffer = 0.8

########################################################################################################
# Construction of Buffer Zones

print"*********************************************************************************************************"
print "Now starting to create GYGA Weather Station Buffer zones..."
print"*********************************************************************************************************"

Created_Layer_Files = []
Created_Temp_Files = []

print r"(1/13) Intersecting countries map and weather station point locations shapefile...",
Stations_Countries = RUNNAM + "Stations_Countries"
arcpy.Intersect_analysis  ([Country_shapefile_world, Station_XYs], Stations_Countries)
#Created_Temp_Files.append(Stations_Countries) # temp file
print "done;"

listcountries = []
rows = arcpy.UpdateCursor(Stations_Countries)
for row in rows:
    listcountries.append(row.REG_NAME)
setcountries = set(listcountries)
listcountries = list(setcountries)

if len(listcountries) > 1:
    choices = {}
    q = 1
    print "\n", "The shapefile with weather station (point) locations contains locations in multiple countries. "
    print "Currently only one country at a time can be handled... your weather stations are located in:", "\n"
    for land in listcountries:
        print q, land
        choices[q] = land
        q+=1
    print "\n"
    select = input("Please enter the number that is listed before the country you want to analyze: ")
    Country = choices[select]
    print Country
    print r"(1/13) Selecting only weather stations in selected country and creating a new layer from that selection...",
    Select_Country = "REG_NAME = " + repr(str(Country))
    #print repr(Select_Country)
#    time.sleep(100)
    Station_XYs_root = os.path.splitext(Station_XYs)[0]
    Station_XYs_ext = os.path.splitext(Station_XYs)[1]
    Station_XYs_temp = Station_XYs_root + RUNNAM + Station_XYs_ext
    arcpy.MakeFeatureLayer_management(Stations_Countries, ftl_name(Stations_Countries))
    arcpy.SelectLayerByAttribute_management (ftl_name(Stations_Countries), "NEW_SELECTION", Select_Country)
    arcpy.CopyFeatures_management(ftl_name(Stations_Countries), Station_XYs_temp)
    Created_Temp_Files.append(Station_XYs_temp)
    
    print "done;"
elif len(listcountries) == 1:
    Country = listcountries[0]
    Station_XYs_temp = Station_XYs
    #Created_Temp_Files.append(Station_XYs_temp)
else:
    print "Error, no country names found... "
    print "Please press Ctrl + c to quit"
    time.sleep(100)
    
# In ArcMap layer names, no spaces are allowed, so remove spaces for naming layers etc.:
Country_AlphaNum = re.sub('\W+','', Country)

    
print r"(2/13) Selecting relevant countries on world map and creating a new layer from that selection...",
Select_Country = "REG_NAME = " + repr(str(Country))
arcpy.MakeFeatureLayer_management(Country_shapefile_world, ftl_name(Country_shapefile_world))
arcpy.SelectLayerByAttribute_management (ftl_name(Country_shapefile_world), "NEW_SELECTION", Select_Country)
arcpy.CopyFeatures_management(ftl_name(Country_shapefile_world), Country_AlphaNum)
Created_Temp_Files.append(Country_AlphaNum) # temp file
print "done;"

print r"(3/13) Intersecting countries map and GYGA CZ shapefile, creating a (much smaller) CZ map...",
arcpy.MakeFeatureLayer_management(Country_AlphaNum, ftl_name(Country_AlphaNum))  
GYGA_CZ_Country = Country_AlphaNum + "_GYGA_CZ"
arcpy.Intersect_analysis  ([GYGA_Climate_Zonation_map, Country_AlphaNum], GYGA_CZ_Country)
Created_Layer_Files.append(GYGA_CZ_Country) # file
print "done;"

print r"(4/13) Intersecting the weather stations with the smaller CZ map, to give them a CZ attribute...",
Stations_with_CZ = RUNNAM + Country_AlphaNum + "_Stations_with_CZ"
arcpy.MakeFeatureLayer_management(Station_XYs_temp, ftl_name(Station_XYs_temp))  
arcpy.Intersect_analysis  ([Station_XYs_temp, GYGA_CZ_Country], Stations_with_CZ)
Created_Layer_Files.append(Stations_with_CZ) # file
print "done;"

print r"(5/13) Creating buffers with a radius of 100 km aroud the weather stations...",
Circles = RUNNAM + Country_AlphaNum + "_Circles"
arcpy.Buffer_analysis     (Stations_with_CZ, Circles, '100 Kilometers', "FULL", "ROUND", "NONE")
Created_Temp_Files.append(Circles) # temp file
print "done;"

print r"(6/13) Creating a union of the buffers and the CZ map...",
Circles_CZs_union = RUNNAM + Country_AlphaNum + "_Circles_CZs_union"
arcpy.Union_analysis      ([Circles, GYGA_CZ_Country], Circles_CZs_union)
Created_Temp_Files.append(Circles_CZs_union) # temp file
print "done;"

print r"(7/13) Selecting areas within the union layer where CZ = CZ weather station...",
criterion = "GRIDCODE = GRIDCODE_1" 
BufferCZ_is_CZ = Country_AlphaNum + "_BufferCZ_is_CZ"
arcpy.MakeFeatureLayer_management(Circles_CZs_union, ftl_name(Circles_CZs_union))  
arcpy.SelectLayerByAttribute_management (ftl_name(Circles_CZs_union), "NEW_SELECTION", criterion)
arcpy.CopyFeatures_management(ftl_name(Circles_CZs_union), BufferCZ_is_CZ)
Created_Temp_Files.append(BufferCZ_is_CZ) # temp file
print "done;"

print r"(8/13) Dissolving unnecessary borders...", 
Buffers_dissolved = RUNNAM + Country_AlphaNum + "_Buffers_dissolved"
arcpy.Dissolve_management(BufferCZ_is_CZ, Buffers_dissolved,
                          [Station_Name_Column, "GRIDCODE", "GRIDCODE_1"]) #todo
arcpy.MakeFeatureLayer_management(Buffers_dissolved, ftl_name(Buffers_dissolved))  
Created_Layer_Files.append(Buffers_dissolved) # file
print "done;"

########################################################################################################
# Calculating cropping area per CZ

if  PointsMethod == True:
    if Use_GYGA_Raster == "F":

        print r"(9/13) Converting CZ map for selected country to a raster, then raster to points...",
        GYGA_CZ_Country_Raster = RUNNAM + GYGA_CZ_Country + "_Raster"
        arcpy.PolygonToRaster_conversion(GYGA_CZ_Country, "GRIDCODE", GYGA_CZ_Country_Raster, "MAXIMUM_COMBINED_AREA", "", 0.083333333)
        GYGA_CZ_Country_Points = RUNNAM + GYGA_CZ_Country + "_Points"
        arcpy.RasterToPoint_conversion(GYGA_CZ_Country_Raster, GYGA_CZ_Country_Points)
        Created_Temp_Files.append(GYGA_CZ_Country_Raster)
        Created_Temp_Files.append(GYGA_CZ_Country_Points)
        print "done;"

    elif Use_GYGA_Raster == "S":
        #print "\n"
        #Raster = askinput("file", ln13, ln14) # SPAM DATA             
        #Check if GYGA_CZ_Temp_Points already exists, if left there for the next run...
        print r"(9/13) Trying to intersect global GYGA CZ Points with country border...",
        GYGA_CZ_Country_Points = RUNNAM + Country_AlphaNum + "_GYGA_CZ_Points"
        try:
            arcpy.Intersect_analysis  (["GYGA_CZ_World_Points", Country_AlphaNum], GYGA_CZ_Country_Points)
            
        except:
            print "No global GYGA CZ Points file found yet; converting global CZ raster to points; this will take quite some time..."
            arcpy.RasterToPoint_conversion(Raster, "GYGA_CZ_World_Points", "Value")
            arcpy.Intersect_analysis  (["GYGA_CZ_World_Points", Country_AlphaNum], GYGA_CZ_Country_Points)
        print "done;"
        
        #arcpy.Delete_management("GYGA_CZ_Temp_Raster")    

    print r"(10/13) Extracting SPAM data to points...",
    ExtractMultiValuesToPoints(GYGA_CZ_Country_Points, SPAM_data, "NONE")
    print "done;"

    print r"(11/13) Calculating totals per GYGA CZ...", 
    listzones = []
    totalcrop = 0.
    rows = arcpy.UpdateCursor(GYGA_CZ_Country_Points)
    for row in rows:
        if row.grid_code > 1:
            listzones.append(row.grid_code)
            if row.maiz_r > 0.:
                totalcrop += float(row.maiz_r)
    setzones = set(listzones)
    listzones = list(setzones)
    print "done;", "\n"
    print "The total area of the selected crop in the country is", totalcrop, "ha", "\n"
    print "The CZs present in the selected country are:", "\n"
    for z in listzones:
        print z,
    print "\n"
    print r"(12/13) Calculating percentages of total national crop area present in each CZ:"
    zonetotalsall = {}
    for zone in listzones:
        print "CZ", zone,   
        zonetotal = 0.
        rows = arcpy.UpdateCursor(GYGA_CZ_Country_Points)
        for row in rows:
            if row.grid_code == zone and row.maiz_r > 0.:
                zonetotal += 100. * (row.maiz_r/totalcrop)
        print round(zonetotal, 2), "%; ",
        if zonetotal >= 5.:
            zonetotalsall[zonetotal] = zone
            enoz = sorted(zonetotalsall, reverse = True)        
    print "done;", "\n", "DCZs, i.e. CZs with more than", str(perc_crop_in_DCZ), "% of the national maize area are:", "\n"
    DCZ_percs = zonetotalsall.keys()
    DCZs = zonetotalsall.values()
    print DCZs, "with:", DCZ_percs, "% of the relevant national crop area, respectively.", "\n"
    
#if PointsMethod == True:
    print "(13/13) Selecting the buffer zones that are in these DCZs ..."
    Points_in_Buffers = RUNNAM + Country_AlphaNum + "_Points_in_Buffers"
    arcpy.Intersect_analysis  ([GYGA_CZ_Country_Points, Buffers_dissolved], Points_in_Buffers)
    rows       = arcpy.UpdateCursor(Points_in_Buffers)
    listbuffers = []
    rows = arcpy.UpdateCursor(Points_in_Buffers)
    for row in rows:
        if row.grid_code in zonetotalsall.values():
            StatNaam = row.getValue(Station_Name_Column)
            listbuffers.append(StatNaam)
    setbuffers = set(listbuffers)
    listbuffers = list(setbuffers)
    print "done;"# buffer zones in DCZs are:", 
    #for buf in listbuffers: 
    #    print buf,
    print "\n", "(14/13) Now calculating percentage of national cropping area in each of these buffer zones...", "n"
    buffertotalsall = {}
    for buff in listbuffers:
        buffertotal = 0.
        rows = arcpy.UpdateCursor(Points_in_Buffers)
        for row in rows:
            Enam = row.getValue(Station_Name_Column)
            if Enam == buff and row.maiz_r > 0.:
                buffertotal += 100. * (row.maiz_r/totalcrop)
                #print row.Name
        print buff, "-",
        if buffertotal >= 0.8:
            buffertotalsall[buffertotal] = buff
            reffub = sorted(buffertotalsall, reverse = True)        
    print 2* "\n", "Calculations completed. For each RWS buffer zone, the percentages of the national crop area contained are: ", "\n"
    
    
    results = open(results_file, 'w')
    for h in reffub:
        print buffertotalsall[h], h
        resultsline = str(buffertotalsall[h]) +"," + str(h) + "\n"
        results.write(resultsline)
    print "\n", "Saving results..."
    stationsline = "Weather station poin locations file" + "," + Station_XYs + "\n"
    results.write(stationsline)
    spamline = "SPAM data file" + "," + SPAM_data + "\n"
    results.write(spamline)
    methodline = "Points method used (if False: zonal statistics were used)" + "," + str(PointsMethod) + "\n"
    rasterline = "Official GYGA CZ Raster used (S = yes; F = converted on the fly from CZ shapefile)" + "," + str(Use_GYGA_Raster) + "\n"
    results.write(methodline)
    results.write(rasterline)
    results.close()
    print "Done! Above results saved in", results_file
    
########################################################################################################

elif PointsMethod == False:
    print"*********************************************************************************************************"
    print "Now calculating cropping area per CZ and selecting DCZs..."
    print"*********************************************************************************************************"

    print r"(9/13) Calculating crop area per CZ, using zonal statistics...",
    Cropping_Area_per_CZ = RUNNAM + Country_AlphaNum + "_Cropping_Area_per_CZ"
    ZonalStatisticsAsTable(GYGA_CZ_Country, "GRIDCODE", SPAM_data, Cropping_Area_per_CZ, "DATA", "SUM")
    Created_Layer_Files.append(Cropping_Area_per_CZ)
    print "done;"

    print r"(10/13) Reading raw data from table row by row, calculating total cropping area over all CZs...",
    rows       = arcpy.UpdateCursor(Cropping_Area_per_CZ)
    All_CZ_sum = 0.
    for row in rows:
        All_CZ_sum += (row.SUM)
    print "done;"#, "\n"

    print r"(11/13) Calculating percentage of national cropping in each CZ, selecting DCZs...",
    Cropping_Area_per_CZ_dict = {}
    rows       = arcpy.UpdateCursor(Cropping_Area_per_CZ)
    for row in rows:
        CZ_sum_as_perc = 100. * (row.SUM)/All_CZ_sum
        CZ_ID  = (row.GRIDCODE)
        if CZ_sum_as_perc > float(perc_crop_in_DCZ):
            Cropping_Area_per_CZ_dict[CZ_sum_as_perc] = CZ_ID

    Relevant_CZs = Cropping_Area_per_CZ_dict.values()

    print "done: ", "\n"
    print "...DCZs, i.e. CZs with more than", str(perc_crop_in_DCZ), "% of the national maize area are:",
    for relcz in Relevant_CZs:
        print relcz, 
    
    print "...", "\n"
    print"*********************************************************************************************************"
    print "Now selecting buffers in DCZs and calculating contained cropping areas..."
    print"*********************************************************************************************************"
    print r"(12/13) For each DCZ, selecting the buffers that fall within it and creating a temporary layer...", 
    
    tempCZlayernames_list = []
    for CZ in Relevant_CZs:
        tempCZlayername = "CZ" + str(CZ)
        tempCZlayernames_list.append(tempCZlayername)
        criterion = "GRIDCODE = " + str(CZ)
        arcpy.SelectLayerByAttribute_management (ftl_name(Buffers_dissolved), "NEW_SELECTION", criterion)
        arcpy.CopyFeatures_management(ftl_name(Buffers_dissolved), tempCZlayername)
        arcpy.MakeFeatureLayer_management(tempCZlayername, ftl_name(tempCZlayername))  
        Created_Temp_Files.append(tempCZlayername)
    print "done;"
    Crop_Area_per_Buffer_dict = {}    
    print r"(13/13) Creating separate temporary layers from each buffer in each temporary layer and",     
    print "calculating crop area per relevant buffer zone, using zonal statistics. Now calculating: ", "\n"
    for temp in tempCZlayernames_list:
        rows       = arcpy.UpdateCursor(temp)
        tempbuffers = []
        for row in rows:
            Maan = row.getValue(Station_Name_Column)
            tempbuffers.append(Maan)
        for temp2 in tempbuffers:
            print temp2,
            temp2_alphanum = re.sub('\W+','', temp2) 
            criterion2 = Station_Name_Column + " = " + repr(str(temp2))
            #print criterion2, ftl_name(tempCZlayername)
            arcpy.SelectLayerByAttribute_management(ftl_name(temp), "NEW_SELECTION", criterion2)
            arcpy.CopyFeatures_management(ftl_name(temp), temp2_alphanum)
            #print temp2_alphanum
            print "- done;",
            
            
            Crop_Area_per_Buffer_Table = temp2_alphanum + "_Crop_Area"
            ZonalStatisticsAsTable(temp2_alphanum, Station_Name_Column, SPAM_data, Crop_Area_per_Buffer_Table, "DATA", "SUM")
            Created_Temp_Files.append(Crop_Area_per_Buffer_Table)
            rows = arcpy.UpdateCursor(Crop_Area_per_Buffer_Table)
            for row in rows:
                Buffer_sum_as_perc = 100. * (row.SUM)/All_CZ_sum
                Buffer_name  = row.getValue(Station_Name_Column)
                if Buffer_sum_as_perc > perc_crop_in_Buffer:
                    Crop_Area_per_Buffer_dict[Buffer_sum_as_perc] = Buffer_name
    
    print "\n"    
    RWS = sorted(Crop_Area_per_Buffer_dict.keys(), reverse = True)
    Coverage = round(sum(RWS))        
    
    results = open(results_file, 'w')
    for rws in RWS:
        print '{:>7}'.format(str(round(rws, 3))),'{:>1}'.format("%"), '{:>25}'.format(Crop_Area_per_Buffer_dict[rws]) 
        resultsline = Crop_Area_per_Buffer_dict[rws] + "," + str(rws) + "\n"
        results.write(resultsline)    
    print "\n", "Saving results..."
    stationsline = "Weather station poin locations file" + "," + Station_XYs + "\n"
    results.write(stationsline)
    spamline = "SPAM data file" + "," + SPAM_data + "\n"
    results.write(spamline)
    methodline = "Points method used (if False: zonal statistics were used)" + "," + str(PointsMethod) + "\n"
    rasterline = "Official GYGA CZ Raster used (S = yes; F = converted on the fly from CZ shapefile)" + "," + str(Use_GYGA_Raster) + "\n"
    results.write(methodline)
    results.write(rasterline)
    results.close()
    print "Done! Above results saved in", results_file


print "\n", "Created layer files are", 
for z in Created_Layer_Files:
    print z, ";",
Delete_Layers = ""
while Delete_Layers <> "Y" and Delete_Layers <> "N":
    delete_layers = raw_input ("can these files be deleted (y/n)? ")
    Delete_Layers = delete_layers.upper()
print "Ok, thanks!", "\n"

if Delete_Layers == "Y":
    for y in Created_Layer_Files:
        print "Deleting layer files... "
        arcpy.Delete_management(y)    
    print "Done; ", "\n"

Delete_Temp_Layers     = ""
while Delete_Temp_Layers <> "Y" and Delete_Layers <> "N":
    delete_temp_layers = raw_input ("Delete all intermediate layers and files too (recommended, y/n)? ")
    Delete_Temp_Layers = delete_temp_layers.upper()
print "Ok, thanks!", "\n"

if Delete_Temp_Layers == "Y":
    for y in Created_Temp_Files:
        print "Deleting temp files... "
        arcpy.Delete_management(y)    
    print "Done; ",    
print  "That's it for now!"
print"*********************************************************************************************************", "\n"

