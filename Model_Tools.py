import arcpy, os, datetime, sys, random
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
        self.label = "Model_Builder"
        self.alias = "Model_Builder"
        self.tools = [Model_Builder]
class Model_Builder(object):
    def __init__(self):
        self.label = "Model_Builder"
        self.description = ""
        self.canRunInBackground = False  
    def getParameterInfo(self):
        param0=arcpy.Parameter(
            displayName="Input Analysis Area Shapefile",
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
            direction="Input")
        param3=arcpy.Parameter(
            displayName="Site SQL Query",
            name="site_Query",
            datatype="String",
            parameterType="Required",
            direction="Input")
        param4=arcpy.Parameter(
            displayName="Input Digital Elevation Model",
            name="dem_In",
            datatype="Raster Layer",
            parameterType="Required",
            direction="Input")
        param5=arcpy.Parameter(
            displayName="DEM Z-value",
            name="z_Value",
            datatype="Double",
            parameterType="Required",
            direction="Input")
        param6=arcpy.Parameter(
            displayName="Input Stream Layer",
            name="Stream_Input",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input")
        params = [param0, param1, param2, param3, param4, param5, param6]
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
        #Param3 - Site SQL Query
        if not params[3].altered:
            params[3].value = "Use All Sites"
        #Param4 - DEM
        if not params[4].altered:
            params[4].value = r'T:\ReferenceState\CO\CorporateData\topography\dem\Elevation 10 Meter Zunits Feet.lyr'
        #Param5 - Z-Factor
        if not params[5].altered:
            params[5].value = 0.3048
        #Param6 - Stream Input
        if not params[6].altered:
            params[6].value = r'T:\CO\GIS\giswork\rgfo\development\cultural\z_Data\Data.gdb\Streams'
        return
    def updateMessages(self, params):      
        warningLoc = 'My Documents'
        string = str(params[1].valueAsText)
        if warningLoc in string:
            params[1].setErrorMessage("This file location is not secure and should NOT be used to store sensitive cultural data")
        return
    def execute(self, params, messages):
        deleteInMemory()
        rawPath = os.path.dirname(params[1].valueAsText)+"\\"+os.path.basename(params[1].valueAsText)+"_Raw_Data"
        finalPath = os.path.dirname(params[1].valueAsText)+"\\"+os.path.basename(params[1].valueAsText)+"_Final_Data"
        testPath = os.path.dirname(params[1].valueAsText)+"\\"+os.path.basename(params[1].valueAsText)+"_Test_Data"
        if not os.path.exists(rawPath):
            os.mkdir(rawPath)
        if not os.path.exists(finalPath):
            os.mkdir(finalPath)
        if not os.path.exists(testPath):
            os.mkdir(testPath)
        poly = arcpy.MakeFeatureLayer_management(params[0].valueAsText)
        outMain = params[1].valueAsText
        outRaw = rawPath+"\\"+os.path.basename(params[1].valueAsText)
        outFinal = finalPath+"\\"+os.path.basename(params[1].valueAsText)
        outTest = testPath+"\\"+os.path.basename(params[1].valueAsText)
        arcpy.env.workspace = os.path.dirname(params[1].valueAsText)
        arcpy.env.scratchWorkspace = os.path.dirname(params[1].valueAsText)
        Sites = arcpy.MakeFeatureLayer_management(params[2].valueAsText)
        DEM = params[4].valueAsText
        zFactor = params[5].value
        Streams = arcpy.MakeFeatureLayer_management(params[6].valueAsText)
        #Process Input Polygon
        lyr = finalPath+"\\"+os.path.basename(params[1].valueAsText)+"_Poly.shp"
        polyParts=int(arcpy.GetCount_management(poly).getOutput(0))
        if polyParts >1:
            arcpy.Dissolve_management(poly, lyr)    
        else:
            arcpy.CopyFeatures_management(poly, lyr)
        lyrDesc = arcpy.Describe(lyr)
        lyrFields = lyrDesc.fields
        lyrExtent = lyrDesc.extent
        arcpy.env.extent = lyrExtent
        fieldx = 0
        for field in lyrFields:
            if field.name == "POLY_ACRES":
                fieldx = 1
        if fieldx == 0:    
            arcpy.AddField_management(lyr, "POLY_ACRES", 'DOUBLE', 12, 8)
        arcpy.CalculateField_management(lyr, "POLY_ACRES", "!shape.area@ACRES!", "PYTHON_9.3", "")
        Desc = arcpy.Describe(lyr)
        polyAcres = ([row[0] for row in arcpy.da.SearchCursor(lyr,["POLY_ACRES"])][0])
        arcpy.AddMessage("Polygon acreage = %d" % polyAcres)
        #Clip Sites
        siteQuery = params[3].ValueAsText
        outPoints = outFinal+"_Data_Points.shp"
        outSites = outRaw+"_Sites"
        if siteQuery == "Use All Sites":
            arcpy.MakeFeatureLayer_management(Sites, outSites)
        else:
            arcpy.MakeFeatureLayer_management(Sites, outSites, siteQuery)
        arcpy.SelectLayerByLocation_management(outSites, "INTERSECT", lyr)
        siteResult = int(arcpy.GetCount_management(outSites).getOutput(0))
        arcpy.AddMessage(siteQuery)
        arcpy.AddMessage("Site Count = "+str(siteResult))
        if siteResult < 10:
            arcpy.AddMessage("There are insufficient site data for analysis")
            systemExit(0)
        arcpy.FeatureToPoint_management(outSites, outPoints, "CENTROID")
        #Add Random field to extract build and test points
        arcpy.AddField_management(outPoints, "Test_Hold", "Double")
        with arcpy.da.UpdateCursor(outPoints, "Test_Hold") as cursor:
            for row in cursor:
                row[0] = random.random()
                cursor.updateRow(row)        
        buildPoints = outTest+"_Build_Sites.shp"
        testPoints = outTest+"_Test_Sites.shp"
        arcpy.MakeFeatureLayer_management(outPoints, "in_memory\\test", """ "Test_Hold" <= 0.2 """)
        arcpy.CopyFeatures_management("in_memory\\test", testPoints)
        arcpy.MakeFeatureLayer_management(outPoints, "in_memory\\build", """ "Test_Hold" > 0.2 """)
        arcpy.CopyFeatures_management("in_memory\\build", buildPoints)
        #These are the raw layers of interest
        outSlope = outRaw+"_slp"
        outTopoProm = outRaw+"_pro"
        outHHODist = outRaw+"_dtw"
        outEleHHO = outRaw+"_eaw"
        outConfDist = outRaw+"_dtc"
        outEaConf = outRaw+"_eac"
        #DEM-based analysis
        outDEM = outRaw+"_dem"
        arcpy.Clip_management(DEM, "#", outDEM, lyr, "#", "ClippingGeometry")           
        arcpy.Slope_3d(outDEM, outSlope, "DEGREE", zFactor)
        outBlk = BlockStatistics(outDEM, NbrCircle(3, "CELL"), "RANGE", "DATA")
        outBlk.save(outTopoProm)
        #Stream-based analysis - rubs only if streams are within input polygon
        outStreams = outFinal+"_str.shp"
        outVPts = outRaw+"_vpt.shp"
        vPtsEle = outRaw+"_vpe.shp"
        vPtsCor = outRaw+"_vpc.shp"
        outCPts = outRaw+"_cpt.shp"
        outCPsC = outRaw+"_cpc.shp"
        outBuff = outRaw+"_buff.shp"
        outDiss = outRaw+"_diss.shp"
        outConPts = outRaw+"_con.shp"
        cPtsEle = outRaw+"_cpe.shp"
        arcpy.Clip_analysis(Streams, lyr, outStreams)
        streamCount = arcpy.GetCount_management(outStreams)
        if not streamCount == 0:
            arcpy.FeatureVerticesToPoints_management(outStreams, outVPts, "ALL")
            arcpy.gp.ExtractValuesToPoints_sa(outVPts, outDEM, vPtsEle, "NONE", "VALUE_ONLY")
            arcpy.MakeFeatureLayer_management(vPtsEle, "in_memory\\vPtsCor", """"RASTERVALU" > 0""")
            arcpy.CopyFeatures_management("in_memory\\vPtsCor", vPtsCor)
            arcpy.AddField_management(vPtsCor, "WAT_ELEV", "SHORT")
            arcpy.CalculateField_management(vPtsCor, "WAT_ELEV", "[RASTERVALU]", "VB", "#")
            arcpy.gp.EucAllocation_sa(vPtsCor, "in_memory\\outAllo", "#", "#", "10", "WAT_ELEV", outHHODist,"#")
            arcpy.Minus_3d(outDEM, "in_memory\\outAllo", outEleHHO)
            deleteList = [outVPts, vPtsEle, vPtsCor]
            #Confluence-based analysis
            arcpy.FeatureVerticesToPoints_management(outStreams, "in_memory\\outCPts", "BOTH_ENDS")
            arcpy.MakeFeatureLayer_management("in_memory\\outCPts", outCPts)
            arcpy.FeatureToLine_management(lyr, "in_memory\\lyrLine","#","ATTRIBUTES")
            arcpy.SelectLayerByLocation_management(outCPts, "WITHIN_A_DISTANCE", "in_memory\\lyrLine", "100 Meters", "NEW_SELECTION")
            arcpy.SelectLayerByLocation_management(outCPts, "#", "#", "#", "SWITCH_SELECTION")
            arcpy.CopyFeatures_management(outCPts, outCPsC)
            arcpy.Buffer_analysis(outCPsC, outBuff, "10 METERS", "#", "#", "NONE", "#")
            arcpy.Dissolve_management(outBuff, outDiss, "#", "#", "SINGLE_PART", "#")
            arcpy.SpatialJoin_analysis(outDiss, outCPsC, "in_memory\\outJoin") 
            arcpy.MakeFeatureLayer_management("in_memory\\outJoin", "in_memory\\joinLayer", """"Join_Count" >= 3""")
            arcpy.FeatureToPoint_management("in_memory\\joinLayer", outConPts, "CENTROID")
            arcpy.gp.ExtractValuesToPoints_sa(outConPts, outDEM, cPtsEle, "NONE", "VALUE_ONLY")
            arcpy.AddField_management(cPtsEle, "CONF_ELEV", "SHORT")
            arcpy.CalculateField_management(cPtsEle, "CONF_ELEV", "[RASTERVALU]", "VB", "#")       
            arcpy.gp.EucAllocation_sa(cPtsEle, "in_memory\\outConfAllo", "#", "#", "10", "CONF_ELEV", outConfDist,"#")
            arcpy.Minus_3d(outDEM, "in_memory\\outConfAllo", outEaConf)
        deleteList = [outCPts, outCPsC, outBuff, outDiss, outConPts, cPtsEle, outVPts, vPtsEle, vPtsCor]
        for delete in deleteList:
            arcpy.Delete_management(delete)
        #Extract values to seperate tables and rename fields    
        def extractValues(pointLayer, raster, outPoints, renameField):
            arcpy.gp.ExtractValuesToPoints_sa(pointLayer, raster, outPoints, "NONE", "ALL")
            arcpy.AddField_management(outPoints, renameField, "SHORT")
            arcpy.CalculateField_management(outPoints, renameField, "[RASTERVALU]", "VB", "#")
            return
        slopeTable = outRaw+"_slopePts.shp"
        promTable = outRaw+"_promPts.shp"
        distTHOtable = outRaw+"_distTHOPts.shp"
        distAHOtable = outRaw+"_distAHOPts.shp"
        distTCOtable = outRaw+"_distTCOPts.shp"
        distACOtable = outRaw+"_distACOPts.shp"
        extractValues(buildPoints, outSlope, slopeTable, "Slope")
        extractValues(buildPoints, outTopoProm, promTable, "Relief")
        if not streamCount == 0:
            extractValues(buildPoints, outHHODist, distTHOtable, "DTo_Water")
            extractValues(buildPoints, outEleHHO, distAHOtable, "DAbo_Water")
            extractValues(buildPoints, outConfDist, distTCOtable, "DTo_Conf")
            extractValues(buildPoints, outEaConf, distACOtable, "DAbo_Conf")
        #Get range of values for each layer and populate lists - reject null values 
        def getValues(layer, fieldName):
            vList = []
            with arcpy.da.SearchCursor(layer, [fieldName]) as cursor:
                    for row in cursor:
                        if row[0] != -999 and row[0] != -9999:
                            vList.append(row[0])                
            return vList
        slopeList = getValues(slopeTable, "Slope")
        promList = getValues(promTable, "Relief")
        if not streamCount == 0:
            dtwList = getValues(distTHOtable, "DTo_Water")
            dawList = getValues(distAHOtable, "DAbo_Water")
            dtcList = getValues(distTCOtable, "DTo_Conf")
            dacList = getValues(distACOtable, "DAbo_Conf")
        deleteList = [slopeTable, promTable, distTHOtable, distAHOtable, distTCOtable, distACOtable]
        for item in deleteList:
            if arcpy.Exists(item):
                arcpy.Delete_management(item)
        #Get statistics for range of values 
        def meanstdv(xlist):
            from math import sqrt
            n, total, std1 = len(xlist), 0, 0
            for x in xlist:
                total = total + x
                mean = total / float(n)
            for x in xlist:
                std1 = std1 + (x - mean)**2
                std = sqrt(std1 / float(n-1))
            return mean, std
        slopeStats = meanstdv(slopeList)
        promStats = meanstdv(promList)
        if not streamCount == 0:
            dtwStats = meanstdv(dtwList)
            dawStats = meanstdv(dawList)
            dtcStats = meanstdv(dtcList)
            dacStats = meanstdv(dacList)
        #Remap rasters according to 1-sigma range        
        def remapRaster(inRaster, outRaster, recField, statList):
            R1 = statList[0] - statList[1]
            R2 = statList[0] + statList[1]
            rasterMin = arcpy.GetRasterProperties_management(inRaster, "MINIMUM")
            rasterMax = arcpy.GetRasterProperties_management(inRaster, "MAXIMUM")
            if R1 < rasterMin:
                R1 = rasterMin
            if R2 > rasterMax:
                R2 = rasterMax    
            remap = str(rasterMin)+" "+str(R1)+" 0;"+str(R1)+" "+str(R2)+" 1;"+str(R2)+" "+str(rasterMax)+" 0"
            arcpy.Reclassify_3d(inRaster, recField, remap, outRaster, "NODATA")
            return outRaster
        targetSlope = outTest+"_slp"       
        targetTopoProm = outTest+"_pro"     
        targetHHODist = outTest+"_dtw"      
        targetConfDist = outTest+"_dtc"       
        targetEleHHO = outTest+"_eaw"      
        targetEaConf = outTest+"_eac"       
        remapRaster(outSlope, targetSlope, "Value", slopeStats)
        remapRaster(outTopoProm, targetTopoProm, "Value", promStats)
        if not streamCount == 0:
            remapRaster(outHHODist, targetHHODist, "Value", dtwStats)
            remapRaster(outEleHHO, targetEleHHO, "Value", dawStats)
            remapRaster(outConfDist, targetConfDist, "Value", dtcStats)
            remapRaster(outEaConf, targetEaConf, "Value", dacStats)

        #Test against test points
        def AreaAndAccuracy(inRaster, inPoly):
            rasterPoly = outRaw+"_poly.shp"
            rasterPolyarea = 0
            lyrPolyarea = 0
            testCount = arcpy.GetCount_management(testPoints)
            arcpy.RasterToPolygon_conversion (inRaster, rasterPoly, "SIMPLIFY", "Value")
            with arcpy.da.SearchCursor(rasterPoly, ("GRIDCODE", "SHAPE@AREA")) as cursor:
                for row in cursor:
                    if row[0] == 1: 
                        rasterPolyarea += row[1]
            with arcpy.da.SearchCursor(inPoly, "SHAPE@AREA") as cursor:
                for row in cursor:
                    lyrPolyarea += row[0]
            targetAcres = rasterPolyarea/lyrPolyarea
            arcpy.MakeFeatureLayer_management(rasterPoly, "in_memory\\rasterPoly", """ "GRIDCODE" = '1' """)
            arcpy.MakeFeatureLayer_management(testPoints, "in_memory\\testPoints")
            arcpy.AddMessage("selecting")
            arcpy.SelectLayerByLocation_management ("in_memory\\testPoints", "WITHIN", "in_memory\\rasterPoly")
            selectCount = arcpy.GetCount_management("in_memory\\testPoints")
            Accuracy = selectCount/testCount
            indexValue = Accuracy/targetAcres
            arcpy.AddMessage(os.path.basename(inRaster)+": Accuracy = "+str(Accuracy)+", Target Area Proportion = "+str(targetAcres)+", Index = "+str(indexValue))
            return targetAcres, Accuracy, indexValue
        #Evaluate accuracy and target area proprtion - generate accuracy/area index - eliminate where index < 1
        assessList = [targetSlope, targetTopoProm, targetHHODist, targetEleHHO, targetConfDist, targetEaConf]
        sumDict = {}
        for item in assessList:
            if arcpy.Exists(item):
                testX = AreaAndAccuracy(item, lyr)
                if testX[2] >= 1:
                    sumDict[item] = testX
        arcpy.AddMessage(sumDict)
        nameList = sumList.keys()        
        deleteInMemory()
        return
