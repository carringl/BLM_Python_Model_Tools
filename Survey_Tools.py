import arcpy, os, datetime, sys
from arcpy import mapping
from arcpy import env
from arcpy.sa import *
env.addOutputsToMap = False
arcpy.env.overwriteOutput = True
def deleteInMemory():
    #Set the workspace to in_memory
    env.workspace = "in_memory"
    #Delete all in memory tables
    fcs = arcpy.ListFeatureClasses()
    if len(fcs) > 0:
        for fc in fcs:
            arcpy.Delete_management(fc)
    #Delete all in memory tables 
    tbls = arcpy.ListTables()
    if len(tbls) > 0:
        for tbl in tbls:
            arcpy.Delete_management(tbl)
class Toolbox(object):
    def __init__(self):
        self.label = "Survey_Tool"
        self.alias = "Survey_Tool"
        self.tools = [Survey_Tool]
class Survey_Tool(object):
    def __init__(self):
        self.label = "Survey_Tool"
        self.description = ""
        self.canRunInBackground = False  
    def getParameterInfo(self):
        param0=arcpy.Parameter(
            displayName="Input Survey Shapefile",
            name="input_Survey",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input")
        param1=arcpy.Parameter(
            displayName="Output Location and File Naming Convention",
            name="out_location",
            datatype="File",
            parameterType="Required",
            direction="Output")
        param2=arcpy.Parameter(
            displayName="Input Site Layer",
            name="in_Site",
            datatype="Feature Layer",
            parameterType="Required",
            category = "Site Data Options",
            direction="Input")
        param3=arcpy.Parameter(
            displayName="Select Site Query Field",
            name="site_Field",
            datatype="String",
            parameterType="Required",
            category = "Site Data Options",
            direction="Input")
        param4=arcpy.Parameter(
            displayName="Select Site Query Field Value",
            name="site_Value",
            datatype="String",
            parameterType="Required",
            category = "Site Data Options",
            direction="Input")
        param5=arcpy.Parameter(
            displayName="Input Digital Elevation Model",
            name="dem_In",
            datatype="Raster Layer",
            parameterType="Required",
            category = "DEM Data Options",
            direction="Input")
        param6=arcpy.Parameter(
            displayName="DEM Z-value",
            name="z_Value",
            datatype="Double",
            parameterType="Required",
            category = "DEM Data Options",
            direction="Input")
        param7=arcpy.Parameter(
            displayName="Input Geology Layer",
            name="Geo_Input",
            datatype="Feature Layer",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param8=arcpy.Parameter(
            displayName="Select Geology Query Field",
            name="Geo_Select",
            datatype="string",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param9=arcpy.Parameter(
            displayName="Input Soils Layer",
            name="Soil_Input",
            datatype="Feature Layer",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param10=arcpy.Parameter(
            displayName="Select Soils Query Field",
            name="Soil_Select",
            datatype="string",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param11=arcpy.Parameter(
            displayName="Input Vegetation Layer",
            name="Veg_Input",
            datatype="Feature Layer",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param12=arcpy.Parameter(
            displayName="Select Vegetation Query Field",
            name="Veg_Select",
            datatype="string",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param13=arcpy.Parameter(
            displayName="Input Stream Layer",
            name="Stream_Input",
            datatype="Feature Layer",
            parameterType="Required",
            category = "Environmental Data Options",
            direction="Input")
        param14=arcpy.Parameter(
            displayName="Data Capture Proportion",
            name="data_Capture",
            datatype="Double",
            parameterType="Required",
            direction="Input")
        param15=arcpy.Parameter(
            displayName="Calculate Target Layer Overlap (Input polygon must be less than 50,000 acres)",
            name="calc_Overlap",
            datatype="Boolean",
            parameterType="Required",
            direction="Input")
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13, param14, param15]
        return params
    def isLicensed(self):
        return True
    def updateParameters(self, params):
        #Param0 - Input Shape
        params[0].filter.list = ["Polygon"]
        #Param1 - Out Space and naming convention
        #Param2 - Site layer
        params[2].filter.list = ["Polygon"]
        if not params[2].altered:
            params[2].value = r'T:\CO\GIS\giswork\rgfo\development\cultural\z_Data\Sites\Sites_Joined.shp'
        #Param3 - Site Field
        if params[2].value:
            siteDesc = arcpy.Describe(params[2].value)
            siteFields = siteDesc.fields
            featurefieldList = [field.name for field in siteFields]
            params[3].filter.type = "ValueList"
            params[3].filter.list = featurefieldList
        if not params[2].altered:
            params[3].value = "TYPE_"
        #Param4 - Site Value
        if params[3].value:
            field_select = params[3].value
            arcpy.Frequency_analysis(params[2].value, "in_memory\\field_freq", field_select)
            featurevalueList = []
            with arcpy.da.SearchCursor("in_memory\\field_freq", [field_select])as cursor:
                for row in cursor:
                    featurevalueList.append(row[0])
            featurevalueList.sort()
            featurevalueList.insert(0, "ALL SITES")
            params[4].filter.type = "ValueList"
            params[4].filter.list = featurevalueList
            arcpy.Delete_management("in_memory\\field_freq")
            del siteDesc, siteFields, field_select
        if not params[4].altered:
            params[4].value = "ALL SITES"
        #Param5 - DEM
        if not params[5].altered:
            params[5].value = r'T:\ReferenceState\CO\CorporateData\topography\dem\Elevation 10 Meter Zunits Feet.lyr'
        #Param6 - Z-Factor
        if not params[6].altered:
            params[6].value = 0.3048
        #Param7 - Geology Input
        params[7].filter.list = ["Polygon"]
        if not params[7].altered:
            params[7].value = r'T:\CO\GIS\giswork\rgfo\development\cultural\z_Data\Data.gdb\Geology'
        #Param8 - Geology Field
        if not params[7].altered:
            params[8].value = "UNIT_NAME"
        if params[7].value:
            geoDesc = arcpy.Describe(params[7].value)
            geoFields = geoDesc.fields
            geofieldList = [field.name for field in geoFields]
            params[8].filter.type = "ValueList"
            params[8].filter.list = geofieldList
        #Param9 - Soil Input
        params[9].filter.list = ["Polygon"]
        if not params[9].altered:
            params[9].value = r'T:\ReferenceState\CO\CorporateData\soils\NRCS STATSGO Soils.lyr'
        #Param10 - Soil Field
        if not params[9].altered:
            params[10].value = "MUKEY"   
        if params[9].value:
            soilDesc = arcpy.Describe(params[9].value)
            soilFields = soilDesc.fields
            soilfieldList = [field.name for field in soilFields]
            params[10].filter.type = "ValueList"
            params[10].filter.list = soilfieldList
        #Param11 - Veg Input
        params[11].filter.list = ["Polygon"]
        if not params[11].altered:
            params[11].value = r'T:\ReferenceState\CO\CorporateData\vegetation\Colorado GAP ReGAP 2004.lyr'
        #Param12 - Veg Field
        if not params[11].altered:
            params[12].value = "DESCRIPTIO"
        if params[11].value:
            vegDesc = arcpy.Describe(params[11].value)
            soilFields = vegDesc.fields
            soilFieldList = [field.name for field in soilFields]
            params[12].filter.type = "ValueList"
            params[12].filter.list = soilFieldList
        #Param13 - Stream Input
        if not params[13].altered:
            params[13].value = r'T:\CO\GIS\giswork\rgfo\development\cultural\z_Data\Data.gdb\Streams'
        #Param14 - Data Capture
        if not params[14].altered:
            params[14].value = 0.66
        #Param15 - Calculate Overlap
        if not params[15].altered:
            params[15].value = 1  
        return
    def updateMessages(self, params):      
        warningLoc = 'My Documents'
        string = str(params[1].valueAsText)
        if warningLoc in string:
            params[1].setErrorMessage("This file location is not secure and should NOT be used to store sensitive cultural data")
        if params[14].value > 1 or params[14] < 0:
            params[14].setErrorMessage("Must be a number between 0 and 1")
        return
    def execute(self, params, messages):
        deleteInMemory()
        Limit = params[14].value
        strLimit = params[14].ValueAsText
        arcpy.AddMessage("Target Data Capture = "+strLimit)
        rawPath = os.path.dirname(params[1].valueAsText)+"\\"+os.path.basename(params[1].valueAsText)+"_Raw_Data"
        finalPath = os.path.dirname(params[1].valueAsText)+"\\"+os.path.basename(params[1].valueAsText)+"_Final_Data"
        if not os.path.exists(rawPath):
            os.mkdir(rawPath)
        if not os.path.exists(finalPath):
            os.mkdir(finalPath)
        poly = arcpy.MakeFeatureLayer_management(params[0].valueAsText)
        outRaw = rawPath+"\\"+os.path.basename(params[1].valueAsText)
        outFinal = finalPath+"\\"+os.path.basename(params[1].valueAsText)
        outMain = params[1].valueAsText
        arcpy.env.workspace = os.path.dirname(params[1].valueAsText)
        arcpy.env.scratchWorkspace = os.path.dirname(params[1].valueAsText)
        DEM = params[5].valueAsText
        Geology  = arcpy.MakeFeatureLayer_management(params[7].valueAsText)
        geoField = params[8].valueAsText
        Soils = arcpy.MakeFeatureLayer_management(params[9].valueAsText)
        soilField = params[10].valueAsText
        Vegetation = arcpy.MakeFeatureLayer_management(params[11].valueAsText)
        vegField = params[12].valueAsText
        Streams = arcpy.MakeFeatureLayer_management(params[13].valueAsText)
        Sites = arcpy.MakeFeatureLayer_management(params[2].valueAsText)  
        zFactor = params[6].value
        try:
            #Multipart Handling
            lyr = finalPath+"\\"+os.path.basename(params[1].valueAsText)+"_Poly.shp"
            polyParts=int(arcpy.GetCount_management(poly).getOutput(0))
            if polyParts >1:
                arcpy.Dissolve_management(poly, lyr)    
            else:
                arcpy.CopyFeatures_management(poly, lyr)
            #Create and calcualte POLY_ACRES
            arcpy.AddField_management(lyr, "POLY_ACRES", 'DOUBLE', 12, 8)
            arcpy.CalculateField_management(lyr, "POLY_ACRES", "!shape.area@ACRES!", "PYTHON_9.3", "")
            Desc = arcpy.Describe(lyr)
            polyAcres = ([row[0] for row in arcpy.da.SearchCursor(lyr,["POLY_ACRES"])][0])
            arcpy.AddMessage("Analysis area = "+str(polyAcres)+" acres")
            if polyAcres > 50000:
                arcpy.AddMessage("Target layer overlap will not be calculated")
            #Clip Sites
            siteField = params[3].valueAsText
            siteValue = params[4].valueAsText
            outPoints = outFinal+"_Data_Points.shp"
            outSites = outRaw+"_Sites"
            if siteValue == "ALL SITES":
                arcpy.MakeFeatureLayer_management(Sites, outSites)
            else:
                siteQuery = '"'+siteField+'"'+" = "+"'"+siteValue+"'"
                arcpy.MakeFeatureLayer_management(Sites, outSites, siteQuery)
            arcpy.SelectLayerByLocation_management(outSites, "INTERSECT", lyr)
            siteResult = int(arcpy.GetCount_management(outSites).getOutput(0))
            arcpy.AddMessage(siteValue+" Site Count = "+str(siteResult))
            if siteResult < 10:
                arcpy.AddMessage("There are insufficient site data for analysis")
                deleteInMemory()
                SystemExit(0)
            siteDensity = str(siteResult/polyAcres)
            arcpy.AddMessage("Site density = "+siteDensity[0:5]+" sites/acre")
            if siteResult/polyAcres < 0.01:
                arcpy.AddMessage("Site density is too low for reliable analysis (0.010 sites/acre minimum), use discretion when interpreting results")          
            arcpy.FeatureToPoint_management(outSites, outPoints, "CENTROID")        
            #Clip DEM, Calculate Slope and Aspect, Reclassify
            outDEM = outRaw+"_Dem"
            outSlope = outRaw+"_Slp"
            outAspect = outRaw+"_Asp"
            arcpy.AddMessage("Clipping DEM") 
            arcpy.Clip_management(DEM, "#", "in_memory\\DEMClip", lyr, "#", "ClippingGeometry")
            arcpy.Reclassify_3d("in_memory\\DEMClip", "VALUE", "0 100 100;100 200 200;200 300 300;300 400 400;400 500 500;500 600 600;600 700 700;700 800 800;800 900 900;900 1000 1000;1000 1100 1100;1100 1200 1200;1200 1300 1300;1300 1400 1400;1400 1500 1500;1500 1600 1600;1600 1700 1700;1700 1800 1800;1800 1900 1900;1900 2000 2000;2000 2100 2100;2100 2200 2200;2200 2300 2300;2300 2400 2400;2400 2500 2500;2500 2600 2600;2600 2700 2700;2700 2800 2800;2800 2900 2900;2900 3000 3000;3000 3100 3100;3100 3200 3200;3200 3300 3300;3300 3400 3400;3400 3500 3500;3500 3600 3600;3600 3700 3700;3700 3800 3800;3800 3900 3900;3900 4000 4000;4000 4100 4100;4100 4200 4200;4200 4300 4300;4300 4400 4400;4400 4500 4500;4500 4600 4600;4600 4700 4700;4700 4800 4800;4800 4900 4900;4900 5000 5000;5000 5100 5100;5100 5200 5200;5200 5300 5300;5300 5400 5400;5400 5500 5500;5500 5600 5600;5600 5700 5700;5700 5800 5800;5800 5900 5900;5900 6000 6000;6000 6100 6100;6100 6200 6200;6200 6300 6300;6300 6400 6400;6400 6500 6500;6500 6600 6600;6600 6700 6700;6700 6800 6800;6800 6900 6900;6900 7000 7000;7000 7100 7100;7100 7200 7200;7200 7300 7300;7300 7400 7400;7400 7500 7500;7500 7600 7600;7600 7700 7700;7700 7800 7800;7800 7900 7900;7900 8000 8000;8000 8100 8100;8100 8200 8200;8200 8300 8300;8300 8400 8400;8400 8500 8500;8500 8600 8600;8600 8700 8700;8700 8800 8800;8800 8900 8900;8900 9000 9000;9000 9100 9100;9100 9200 9200;9200 9300 9300;9300 9400 9400;9400 9500 9500;9500 9600 9600;9600 9700 9700;9700 9800 9800;9800 9900 9900;9900 10000 10000;10000 10100 10100;10100 10200 10200;10200 10300 10300;10300 10400 10400;10400 10500 10500;10500 10600 10600;10600 10700 10700;10700 10800 10800;10800 10900 10900;10900 11000 11000;11000 11100 11100;11100 11200 11200;11200 11300 11300;11300 11400 11400;11400 11500 11500;11500 11600 11600;11600 11700 11700;11700 11800 11800;11800 11900 11900;11900 12000 12000;12000 12100 12100;12100 12200 12200;12200 12300 12300;12300 12400 12400;12400 12500 12500;12500 12600 12600;12600 12700 12700;12700 12800 12800;12800 12900 12900;12900 13000 13000;13000 13100 13100;13100 13200 13200;13200 13300 13300;13300 13400 13400;13400 13500 13500;13500 13600 13600;13600 13700 13700;13700 13800 13800;13800 13900 13900;13900 14000 14000;14000 14100 14100;14100 14200 14200;14200 14300 14300;14300 14400 14400;14400 14500 14500;14500 14600 14600;14600 14700 14700;14700 14800 14800;14800 14900 14900;14900 15000 15000", outDEM)
            arcpy.AddMessage("Calculating Slope")
            arcpy.Slope_3d("in_memory\\DEMClip", "in_memory\\outSlope", "DEGREE", zFactor)
            arcpy.Reclassify_3d("in_memory\\outSlope", "VALUE", "0 5 5;5 10 10;10 15 15;15 20 20;20 25 25;25 30 30;30 35 35;35 40 40;40 45 45;45 90 90", outSlope)            
            arcpy.AddMessage("Calculating Aspect")
            arcpy.Aspect_3d("in_memory\\DEMClip", "in_memory\\outAspect")
            arcpy.Reclassify_3d("in_memory\\outAspect", "VALUE", "-1 22.5 0;22.5 67.5 1;67.5 112.5 2;112.5 157.5 3;157.5 202.5 4;202.5 247.5 5;247.5 292.5 6;292.5 337.5 7;337.5 360 0", outAspect)
            #Clip Geology
            arcpy.AddMessage("Clipping Geology")
            outGeo = outRaw+"_Geo.shp"
            arcpy.Clip_analysis(Geology, lyr, "in_memory\\outGeo")
            arcpy.Dissolve_management("in_memory\\outGeo", outGeo, geoField)
            #Clip Soils
            arcpy.AddMessage("Clipping Soils")
            outSoils = outRaw+"_Soil.shp"
            arcpy.Clip_analysis(Soils, lyr, "in_memory\\outSoil")
            arcpy.Dissolve_management("in_memory\\outSoil", outSoils, soilField)
            #Clip Vegetation
            arcpy.AddMessage("Clipping Vegetation")
            outVeg = outRaw+"_Veg.shp"
            arcpy.Clip_analysis(Vegetation, lyr, "in_memory\\outVeg")
            arcpy.Dissolve_management("in_memory\\outVeg", outVeg, vegField)
            #Clip Streams
            arcpy.AddMessage("Clipping and Buffering Streams")
            outStr = outRaw+"_Str.shp"
            strLayer = arcpy.MakeFeatureLayer_management(Streams, "in_memory\\streams")
            arcpy.SelectLayerByLocation_management("in_memory\\streams", "INTERSECT", lyr, "", "NEW_SELECTION")
            streamResult = int(arcpy.GetCount_management("in_memory\\streams").getOutput(0))           
            if streamResult == 0:
                arcpy.AddMessage("There Are No Streams Within This Polygon")
            else:
                outStreams = outRaw+"_Str.shp"
                arcpy.Clip_analysis(Streams, lyr, "in_memory\\outStreams")
                arcpy.MultipleRingBuffer_analysis("in_memory\\outStreams", outStr, [200, 400, 600, 800, 1000], "meters")       
            deleteInMemory()
            #DEM
            demTarget = outFinal+"_Elevation_Target.shp"
            demFinal = outRaw+"_DEM.shp"
            arcpy.AddMessage("Processing DEM")
            ExtractValuesToPoints(outPoints, outDEM, "in_memory\\pointDEM")
            arcpy.Frequency_analysis("in_memory\\pointDEM", "in_memory\\DEM_Table", "RASTERVALU")
            arcpy.Sort_management("in_memory\\DEM_Table", "in_memory\\DEM_Sort", [["FREQUENCY", "DESCENDING"]])
            Vdem = 0
            Xdem = 0
            demList = []
            with arcpy.da.SearchCursor("in_memory\\DEM_Sort", ["RASTERVALU", "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xdem == 0:
                        Vdem = row[1]
                        demList.append(row[0]) 
                    else:
                        Vdem = Vdem + row[1]
                        demList.append(row[0]) 
                    if float(Vdem) / float(siteResult) < Limit:
                        Xdem = Xdem + 1
                    else:
                        break
            arcpy.RasterToPolygon_conversion(outDEM, demFinal, "SIMPLIFY", "VALUE")
            DEMdesc = arcpy.Describe(demFinal)
            fields = DEMdesc.fields
            for field in fields:
                if field.name == "GRIDCODE":
                    arcpy.AddField_management(demFinal, "ELEV", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor(demFinal, ["GRIDCODE", "ELEV"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
                    arcpy.DeleteField_management(demFinal, "GRIDCODE")
            qryList = [str(dem) for dem in demList]
            expr = "ELEV IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(demFinal, "in_memory\\demTarget", expr)
            arcpy.Dissolve_management("in_memory\\demTarget", demTarget, "ELEV")
            #arcpy.Delete_management(outDEM)
            #SLOPE
            slopeTarget = outFinal+"_Slope_Target.shp"
            slopeFinal = outRaw+"_Slope.shp"
            arcpy.AddMessage("Processing Slope")
            ExtractValuesToPoints(outPoints, outSlope, "in_memory\\pointSlope")
            arcpy.Frequency_analysis("in_memory\\pointSlope", "in_memory\\Slope_Table", "RASTERVALU")
            arcpy.Sort_management("in_memory\\Slope_Table", "in_memory\\Slope_Sort", [["FREQUENCY", "DESCENDING"]])
            Vslp = 0
            Xslp = 0
            slpList = []
            with arcpy.da.SearchCursor("in_memory\\Slope_Sort", ["RASTERVALU", "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xslp == 0:
                        Vslp = row[1]
                        slpList.append(row[0]) 
                    else:
                        Vslp = Vslp + row[1]
                        slpList.append(row[0]) 
                    if float(Vslp) / float(siteResult) < Limit:
                        Xslp = Xslp + 1
                    else:
                        break
            arcpy.RasterToPolygon_conversion(outSlope, slopeFinal, "SIMPLIFY", "VALUE")
            Slpdesc = arcpy.Describe(slopeFinal)
            fields = Slpdesc.fields
            for field in fields:
                if field.name == "GRIDCODE":
                    arcpy.AddField_management(slopeFinal, "SLOPE", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor(slopeFinal, ["GRIDCODE", "SLOPE"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
                    arcpy.DeleteField_management(slopeFinal, "GRIDCODE")
            qryList = [str(slp) for slp in slpList]
            expr = "SLOPE IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(slopeFinal, "in_memory\\slopeTarget", expr)
            arcpy.Dissolve_management("in_memory\\slopeTarget", slopeTarget, "SLOPE")
            #arcpy.Delete_management(outSlope)
            #ASPECT
            aspectTarget = outFinal+"_Aspect_Target.shp"
            aspectFinal = outRaw+"_Aspect.shp"
            arcpy.AddMessage("Processing Aspect")
            ExtractValuesToPoints(outPoints, outAspect, "in_memory\\pointAspect")
            arcpy.Frequency_analysis("in_memory\\pointAspect", "in_memory\\aspect_Table", "RASTERVALU")
            arcpy.Sort_management("in_memory\\aspect_Table", "in_memory\\aspect_Sort", [["FREQUENCY", "DESCENDING"]])
            Vasp = 0
            Xasp = 0
            aspList = []
            with arcpy.da.SearchCursor("in_memory\\aspect_Sort", ["RASTERVALU", "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xasp == 0:
                        Vasp = row[1]
                        aspList.append(row[0]) 
                    else:
                        Vasp = Vasp + row[1]
                        aspList.append(row[0]) 
                    if float(Vasp) / float(siteResult) < Limit:
                        Xasp = Xasp + 1
                    else:
                        break
            arcpy.RasterToPolygon_conversion(outAspect, aspectFinal, "SIMPLIFY", "VALUE")
            Aspdesc = arcpy.Describe(aspectFinal)
            fields = Aspdesc.fields
            for field in fields:
                if field.name == "GRIDCODE":
                    arcpy.AddField_management(aspectFinal, "ASPECT", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor(aspectFinal, ["GRIDCODE", "ASPECT"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
                    arcpy.DeleteField_management(aspectFinal, "GRIDCODE")
            qryList = [str(asp) for asp in aspList]
            expr = "ASPECT IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(aspectFinal, "in_memory\\aspectTarget", expr)
            arcpy.Dissolve_management("in_memory\\aspectTarget", aspectTarget, "ASPECT")
            #arcpy.Delete_management(outAspect)
            #GEOLOGY
            GeoTarget = outFinal+"_Geology_Target.shp"
            arcpy.AddMessage("Processing Geology")
            arcpy.SpatialJoin_analysis(outPoints, outGeo, "in_memory\\pointGeo")
            arcpy.Frequency_analysis("in_memory\\pointGeo", "in_memory\\geo_Table", geoField)
            arcpy.Sort_management("in_memory\\geo_Table", "in_memory\\geo_Sort", [["FREQUENCY", "DESCENDING"]])
            Vgeo = 0 
            Xgeo = 0
            geoList = []
            with arcpy.da.SearchCursor("in_memory\\geo_Sort", [geoField, "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xgeo == 0:
                        Vgeo = row[1]
                        geoList.append(row[0]) 
                    else:
                        Vgeo = Vgeo + row[1]
                        geoList.append(row[0]) 
                    if float(Vgeo) / float(siteResult) < Limit:
                        Xgeo = Xgeo + 1
                    else:
                        break
            qryList = ["'"+geo+"'" for geo in geoList]
            expr = '"'+geoField+'"'+" IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(outGeo, "in_memory\\geoTarget", expr)
            GEOdesc = arcpy.Describe("in_memory\\geoTarget")
            fields = GEOdesc.fields
            for field in fields:
                if field.name == geoField:
                    arcpy.AddField_management("in_memory\\geoTarget", "GEO_TYPE", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor("in_memory\\geoTarget", [geoField, "GEO_TYPE"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
            arcpy.Dissolve_management("in_memory\\geoTarget", GeoTarget, "GEO_TYPE")
            #SOILS
            SoilTarget = outFinal+"_Soil_Target.shp"
            arcpy.AddMessage("Processing Soils")
            arcpy.SpatialJoin_analysis(outPoints, outSoils, "in_memory\\pointSoil")
            arcpy.Frequency_analysis("in_memory\\pointSoil", "in_memory\\soil_Table", soilField)
            arcpy.Sort_management("in_memory\\soil_Table", "in_memory\\soil_Sort", [["FREQUENCY", "DESCENDING"]])
            Vsoil = 0
            Xsoil= 0
            soilList = []
            with arcpy.da.SearchCursor("in_memory\\soil_Sort", [soilField, "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xsoil == 0:
                        Vsoil = row[1]
                        soilList.append(row[0]) 
                    else:
                        Vsoil = Vsoil + row[1]
                        soilList.append(row[0]) 
                    if float(Vsoil) / float(siteResult) < Limit:
                        Xsoil = Xsoil + 1
                    else:
                        break
            qryList = ["'"+soil+"'" for soil in soilList]
            expr = '"'+soilField+'"'+" IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(outSoils, "in_memory\\soilTarget", expr)
            SOILdesc = arcpy.Describe("in_memory\\soilTarget")
            fields = SOILdesc.fields
            for field in fields:
                if field.name == soilField:
                    arcpy.AddField_management("in_memory\\soilTarget", "SOIL_TYPE", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor("in_memory\\soilTarget", [soilField, "SOIL_TYPE"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
            arcpy.Dissolve_management("in_memory\\soilTarget", SoilTarget, "SOIL_TYPE")
            #VEGETATION
            VegTarget = outFinal+"_Veg_Target.shp"
            arcpy.AddMessage("Processing Vegetation")
            arcpy.SpatialJoin_analysis(outPoints, outVeg, "in_memory\\pointVeg")
            arcpy.Frequency_analysis("in_memory\\pointVeg", "in_memory\\veg_Table", vegField)
            arcpy.Sort_management("in_memory\\veg_Table", "in_memory\\veg_Sort", [["FREQUENCY", "DESCENDING"]])
            Vveg = 0
            Xveg= 0
            vegList = []
            with arcpy.da.SearchCursor("in_memory\\veg_Sort", [vegField, "FREQUENCY"]) as cursor:
                for row in cursor:
                    if Xveg == 0:
                        Vveg = row[1]
                        vegList.append(row[0]) 
                    else:
                        Vveg = Vveg + row[1]
                        vegList.append(row[0]) 
                    if float(Vveg) / float(siteResult) < Limit:
                        Xveg = Xveg + 1
                    else:
                        break
            qryList = ["'"+veg+"'" for veg in vegList]
            expr = '"'+vegField+'"'+" IN ("+",".join(qryList)+")"
            arcpy.MakeFeatureLayer_management(outVeg, "in_memory\\vegTarget", expr)
            VEGdesc = arcpy.Describe("in_memory\\vegTarget")
            fields = VEGdesc.fields
            for field in fields:
                if field.name == vegField:
                    arcpy.AddField_management("in_memory\\vegTarget", "VEG_TYPE", field.type, field.precision, field.scale, field.length, "", "", "", "")
                    with arcpy.da.UpdateCursor("in_memory\\vegTarget", [vegField, "VEG_TYPE"]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)
            arcpy.Dissolve_management("in_memory\\vegTarget", VegTarget, "VEG_TYPE")
            #WATER
            StreamTarget = outFinal+"_Water_Dist_Target.shp"
            arcpy.AddMessage("Processing Streams")
            if not streamResult == 0:
                arcpy.SpatialJoin_analysis(outPoints, outStreams, "in_memory\\pointStream")
                arcpy.Frequency_analysis("in_memory\\pointStream", "in_memory\\stream_Table", "distance")
                arcpy.Sort_management("in_memory\\stream_Table", "in_memory\\stream_Sort", [["FREQUENCY", "DESCENDING"]])
                Vstr = 0
                Xstr = 0
                streamList = []
                with arcpy.da.SearchCursor("in_memory\\stream_Sort", ["distance", "FREQUENCY"]) as cursor:
                    for row in cursor:
                        if Xstr == 0:
                            Vstr = row[1]
                            streamList.append(row[0]) 
                        else:
                            Vstr = Vstr + row[1]
                            streamList.append(row[0]) 
                        if float(Vstr) / float(siteResult) < Limit:
                            Xstr = Xstr + 1
                        else:
                            break
                qryList = [str(stream) for stream in streamList]
                expr = "distance IN ("+",".join(qryList)+")"
                arcpy.MakeFeatureLayer_management(outStreams, "in_memory\\streamTarget", expr)
                strDesc = arcpy.Describe("in_memory\\streamTarget")
                fields = strDesc.fields
                for field in fields:
                    if field.name == "distance":
                        arcpy.AddField_management("in_memory\\streamTarget", "WAT_DIST", field.type, field.precision, field.scale, field.length, "", "", "", "")
                        with arcpy.da.UpdateCursor("in_memory\\streamTarget", ["distance", "WAT_DIST"]) as cursor:
                            for row in cursor:
                                row[1] = row[0]
                                cursor.updateRow(row)
                arcpy.Dissolve_management("in_memory\\streamTarget", StreamTarget, "WAT_DIST")
            #Overlay and count overlaps
            if params[15].value == 1 and polyAcres < 50000:
                arcpy.AddMessage("Calculating target layer overlap")
                layerList = [demTarget, slopeTarget, aspectTarget, GeoTarget, SoilTarget, VegTarget, StreamTarget]
                existsList = []
                for layer in layerList:
                      if arcpy.Exists(layer):
                           existsList.append(layer)
                outMerge = outFinal+"_Merge.shp"
                outFtoLine = outFinal+"_FtoLine.shp"
                outFtoPoly = outFinal+"_FtoPoly.shp"
                outFtoPoint = outFinal+"_FtoPoint.shp"
                outJoin1 = outFinal+"_Join1.shp"
                outDiss1 = outFinal+"_Diss1.shp"
                outJoin2 = outFinal+"_Join2.shp"
                outDiss2 = outFinal+"_Diss2.shp"
                rankPoly = outFinal+"_Rank_Poly.shp"
                arcpy.Merge_management(existsList, outMerge)
                arcpy.FeatureToLine_management(outMerge, outFtoLine)
                arcpy.FeatureToPolygon_management(outFtoLine, outFtoPoly, "#", "NO_ATTRIBUTES", "#")
                arcpy.FeatureToPoint_management(outFtoPoly, outFtoPoint, "INSIDE")
                arcpy.SpatialJoin_analysis(outFtoPoint, outMerge, outJoin1, "JOIN_ONE_TO_MANY", "KEEP_ALL", "#", "INTERSECT", "#", "#")
                arcpy.Dissolve_management(outJoin1, outDiss1, "TARGET_FID", "Join_Count SUM", "MULTI_PART", "DISSOLVE_LINES")
                arcpy.SpatialJoin_analysis(outFtoPoly, outDiss1, outJoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "INTERSECT", "#", "#")
                rankDesc = arcpy.Describe(outJoin2)
                fields = rankDesc.fields
                for field in fields:
                    if field.name == "SUM_Join_C":
                        arcpy.AddField_management(outJoin2, "OVERLAP", field.type, field.precision, field.scale, field.length, "", "", "", "")
                        with arcpy.da.UpdateCursor(outJoin2, ["SUM_Join_C", "OVERLAP"]) as cursor:
                            for row in cursor:
                                row[1] = row[0]
                                cursor.updateRow(row)
                arcpy.Dissolve_management(outJoin2, outDiss2, "OVERLAP", "#", "MULTI_PART", "DISSOLVE_LINES")
                arcpy.Clip_analysis(outDiss2, lyr, rankPoly)
                delList = [outMerge, outFtoLine, outFtoPoly, outFtoPoint, outJoin1, outDiss1, outJoin2, outDiss2]
                for item in delList:
                    arcpy.Delete_management(item)
        finally:
            delList2 = []
            for item in delList2:
                    arcpy.Delete_management(item)
            deleteInMemory()
        return
