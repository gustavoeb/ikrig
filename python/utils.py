import maya.api.OpenMaya as om
import numpy as np
import os

# inform maya we are using OM2
def maya_useNewAPI():
    pass


class DataCache:
    '''A interface for loading and caching data from csv files'''
    filePath = ''
    data = None

    def getOrLoad(self, filePath):
        if filePath == self.filePath:
            return self.data
        self.filePath = filePath
        self.data = np.loadtxt(filePath)

# global node params
nodeName = 'csvToScalarArray'
nodeTypeID = om.MTypeId(0x1E243)
data_cache = DataCache()

class csvToScalarArray(om.MPxNode):
    '''Node for loading CSV values into scalar arrays.'''

    def compute(self, plug, data):
        # (1) Get handles from data stream
        fpHandle = data.inputValue(csvToScalarArray.filePath)
        filePath = fpHandle.asString()
        frHandle = data.inputValue(csvToScalarArray.frame)
        frame = int(np.float32(frHandle.asFloat()))
        result_handle = data.outputValue(csvToScalarArray.result)

        # (2) Get CSV data
        data_cache.getOrLoad(filePath)

        # (3) Load data based on frame
        frame = max(0, frame)
        frame = min(frame, data_cache.data.shape[0]-1)
        frame_data = data_cache.data[frame,:]
        
        # (4) Output
        output_array = om.MFnDoubleArrayData(result_handle.data())
        output_values = []
        for component in frame_data:
            output_values.append(component)        
        output_array.set(output_values)
        result_handle.setClean()

def create():
    return csvToScalarArray()


def init():
    pass
    # (1) Get Maya data types and attributes
    kString = om.MFnData.kString
    kFloat = om.MFnNumericData.kFloat
    tAttr = om.MFnTypedAttribute()
    nAttr = om.MFnNumericAttribute()
    kDoubleArray = om.MFnNumericData.kDoubleArray

    # (2) Setup attributes
    csvToScalarArray.filePath = tAttr.create('filePath', 'fp', kString)
    tAttr.usedAsFilename = True
    csvToScalarArray.frame = nAttr.create('frame','fr', kFloat, 0.0)
    nAttr.hidden = False
    nAttr.keyable = True
    csvToScalarArray.result = tAttr.create('result', 'r', kDoubleArray, om.MFnDoubleArrayData().create())
    tAttr.writable = False
    tAttr.storable = False
    tAttr.readable = True

    # (3) Add the attributes to the node
    csvToScalarArray.addAttribute(csvToScalarArray.filePath)
    csvToScalarArray.addAttribute(csvToScalarArray.frame)
    csvToScalarArray.addAttribute(csvToScalarArray.result)

    # (4) Set the attribute dependencies
    csvToScalarArray.attributeAffects(csvToScalarArray.filePath, csvToScalarArray.result)
    csvToScalarArray.attributeAffects(csvToScalarArray.frame, csvToScalarArray.result)

def _toplugin(mobject):
    return om.MFnPlugin(
        mobject, 'Gustavo E. Boehs', '1.00')


def initializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.registerNode(nodeName, nodeTypeID, create, init)


def uninitializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.deregisterNode(nodeTypeID)