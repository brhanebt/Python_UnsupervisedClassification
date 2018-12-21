from pci.kclus import kclus
from pci.fmo import fmo
from pci.sieve import sieve
from pci.ras2poly import ras2poly
from pci.pcimod import *
from pci.api import datasource as ds
from pci.mlr import mlr
from pci.nspio import Report, enableDefaultReport
from pci.exceptions import *
import os, errno
#Delete previous Intermediate Result files
def deletePreviousResultFiles(Path):
    try:
        if os.path.exists(Path+r"my_CastellonShp.shp"): #If file exists
            os.remove(Path+r"my_CastellonShp.shp") #Remove it
        if os.path.exists(Path+r"my_CastellonShp.dbf"): #If file exists
            os.remove(Path+r"my_CastellonShp.dbf") #Remove it
        if os.path.exists(Path+r"my_CastellonShp.shp.pox"): #If file exists
            os.remove(Path+r"my_CastellonShp.shp.pox") #Remove it
        if os.path.exists(Path+r"my_CastellonShp.shx"): #If file exists
            os.remove(Path+r"my_CastellonShp.shx") #Remove it
        if os.path.exists(Path+r"my_CastellonShp.prj"): #If file exists
            os.remove(Path+r"my_CastellonShp.prj") #Remove it
        if os.path.exists(Path+r"my_CastellonPoly.pix"): #If file exists
            os.remove(Path+r"my_CastellonPoly.pix") #Remove it
    except OSError:
        print OSError
	print "Previous result files deleted"

#Remove previously created result channels
def removePreviousResultChannels(fileInput,defNumChannels):
    try:
        with ds.open_dataset(fileInput, ds.eAM_READ) as pix: 
            # Get channel count
            numberOfChannels = pix.chan_count
            channelOperationType  =  'DEL'
            while numberOfChannels > defNumChannels: #While the number of channels in the image are greater than the default number of channels in Landsat 8
                channelsToDelete = [numberOfChannels]
                pcimod(fileInput,channelOperationType,channelsToDelete) #remove
                numberOfChannels = numberOfChannels - 1
    except Exception as e:
        print e
	print "Previous channels deleted"

#Add new channels
def addChannels(fileInput):
    try:
        channelOperationType        =   'ADD' # Channel operation type
        channelsToADD       =   [0,0,3,0] #three channels of 16 bit each
        pcimod(fileInput, channelOperationType, channelsToADD) #Add channels
    except PCIException, e:
        print e
    except Exception, e:
        print e
	print "New channels added"

def kMeansClustering(fileInput, inputChannels,outputChannel):
    mask = []      # Area or window in the input image to process
    numberOfClasses = [5]      # Number of classes
    seedfile = ""
    maximumIterations = [5]      # Number of Iterations for calculating the mean positions
    movethrs = [0.01]     # Movement threshold
    siggen = ""
    backval = []     # Background gray level value to be ignored during classification
    nsam = []      # Number of samples to collect on which to perform the iterative clustering

    try:
        kclus(fileInput, inputChannels, outputChannel, mask, numberOfClasses, seedfile, maximumIterations, movethrs, siggen, backval, nsam)
        print "K means clustering finished"
    except PCIException, e:
        print e
    except Exception, e:
        print e
#Mode filter
def modeFilter(fileInput,inputChannel,outputChannel):
    filterSize = []      # Size of the filter window defualt 7X7
    mask = []      
    thinline = "ON" # Ensures that thin classes are not removed when cleaning up thematic images.
    keepvalu = []     # Pixel values that are not filtered
    bgzero = ""

    try:
        fmo(fileInput, inputChannel, outputChannel, filterSize, mask, thinline, keepvalu, bgzero)
        print "Mode filter finished"
    except PCIException, e:
        print e
    except Exception, e:
        print e
#sieve filter
def sieveFilter(fileInput,inputChannel,outputChannel):
    sthresh = [6]      # Size of the smallest polygon not to be merged into a neighbor
    keepvalu = []      # 
    connect = []      # 

    try:
        sieve(fileInput, inputChannel, outputChannel, sthresh, keepvalu, connect)
        print "Sieve filter finished"
    except PCIException, e:
        print e
    except Exception, e:
        print e

#raster to poly
def rasterToPoly(fileInput,Path,inputChannel):
    outputFile = r"my_CastellonPoly.pix"
    smoothv = "" #Whether to smooth the vector lines or not
    outputDesription = "" #Desciption origin of the output data
    fileType = ""
    foptions = ""

    try:
        ras2poly(fileInput, inputChannel, Path+outputFile, smoothv, outputDesription, fileType, foptions)
        print "Exporting to polygons finished"
    except PCIException, e:
        print e
    except Exception, e:
        print e
#raster to shape file
def rasterToShapeFile(fileInput,Path,inputChannel):
    outputFile = r"my_CastellonShp.shp"
    smoothv = ""
    outputDesription = ""
    fileType = "SHP"
    foptions = ""

    try:
        ras2poly(fileInput, inputChannel, Path+outputFile, smoothv, outputDesription, fileType, foptions)
        print "Export to shape file finished"
    except PCIException, e:
        print e
    except Exception, e:
        print e

directoryPath = r"F:/Master Course Materials/Remote Sensing/Final Project/DataSets/"
filePath = directoryPath + r"castellon.pix"
inputChannels = [2,3,4,5,6,7]      # Input channels
numChannels = 9

removePreviousResultChannels(filePath,numChannels)
deletePreviousResultFiles(directoryPath);
addChannels(filePath)
kMeansClustering(filePath,inputChannels,[numChannels+1])
modeFilter(filePath,[numChannels+1],[numChannels+2])
sieveFilter(filePath,[numChannels+1],[numChannels+3])
rasterToPoly(filePath,directoryPath,[numChannels+3])
rasterToShapeFile(filePath,directoryPath,[numChannels+3])
