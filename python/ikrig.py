# -*- coding: utf-8 -*-
'''FK 2 IKRig Encoding

This Maya Plug-in implements a real-time scheme to encode
parameters of FK skeletons into parameters of an IKRig
as described by Bereznyak, 2016.

Author: Gustavo E Boehs
Published @ http://3deeplearner.com
March, 2019
'''

import maya.api.OpenMaya as om
import math

# Inform Maya we are using OpenMaya2
def maya_useNewAPI():
    pass

# Declare global node params and other global vars
encode_nodeName = 'ikrig_encode'
encode_nodeTypeID = om.MTypeId(0x1E240)
decode_nodeName = 'ikrig_decode'
decode_nodeTypeID = om.MTypeId(0x1E241)
float_attrs = ['height_hips',
                'length_spine',
                'length_neck',
                'length_leg_L',
                'length_leg_R',
                'length_arm_L',
                'length_arm_R']
vector_attrs = ['root_offset_neck',
                'root_offset_leg_L',
                'root_offset_leg_R',
                'root_offset_arm_L',
                'root_offset_arm_R']
mat_attrs = ['mat_hips_rest',
             'mat_hips',
             'mat_spine',
             'mat_chest',
             'mat_neck',
             'mat_neck_mid',
             'mat_head',
             'mat_leg_L',
             'mat_shin_L',
             'mat_foot_L',
             'mat_shoulder_L',
             'mat_elbow_L',
             'mat_hand_L',
             'mat_leg_R',
             'mat_shin_R',
             'mat_foot_R',
             'mat_shoulder_R',
             'mat_elbow_R',
             'mat_hand_R']
out_float3_attrs = ['ik_Spine_root',
                    'ik_Spine_dir',
                    'ik_Spine_eff',
                    'ik_Neck_root',
                    'ik_Neck_dir',
                    'ik_Neck_eff',
                    'ik_Leg_root_L',
                    'ik_Leg_dir_L',
                    'ik_Leg_eff_L',
                    'ik_Arm_root_L',
                    'ik_Arm_dir_L',
                    'ik_Arm_eff_L',
                    'ik_Leg_root_R',
                    'ik_Leg_dir_R',
                    'ik_Leg_eff_R',
                    'ik_Arm_root_R',
                    'ik_Arm_dir_R',
                    'ik_Arm_eff_R',
                    'ik_Spine_eff_rot',
                    'ik_Neck_eff_rot',
                    'ik_Leg_eff_rot_L',
                    'ik_Leg_eff_rot_R',
                    'ik_Arm_eff_rot_L',
                    'ik_Arm_eff_rot_R']

def MMat2Trans(mat):
    return om.MVector(mat[12],mat[13],mat[14])

def FK2encoded_root_positionOffset(g_mat, root_jnt):
    # Get normalized IK root position
    l_root_jnt = root_jnt * g_mat.inverse()
    ik_root = MMat2Trans(l_root_jnt)
    return ik_root

def FK2encoded_root_rotationOffset(g_mat, root_offset, root_jnt):
    # Get rotational offset
    l_root_jnt = root_jnt * g_mat.inverse()
    vec_root = MMat2Trans(l_root_jnt)
    vec_root.normalize()
    root_offset.normalize()
    axis = root_offset^vec_root
    angle = math.acos(root_offset*vec_root)
    ik_root = om.MQuaternion().setValue(axis, angle)
    return ik_root

def FK2encoded(g_mat, root_offset, root_jnt, dir_jnt, eff_jnt, chain_length):
    if type(root_offset) == bool:
        ik_root = FK2encoded_root_positionOffset(g_mat, root_jnt)
    else:
        ik_root = FK2encoded_root_rotationOffset(g_mat, root_offset, root_jnt)

    # Get normalized effector position
    vec_root = MMat2Trans(root_jnt)
    vec_eff = MMat2Trans(eff_jnt)
    l_vec_eff = vec_eff - vec_root
    ik_eff = l_vec_eff * g_mat.homogenize().inverse()
    ik_eff /= chain_length

    # Get IK direction
    vec_dir = MMat2Trans(dir_jnt)
    l_vec_dir = vec_root - vec_dir
    ik_upv = (l_vec_dir ^ l_vec_eff) ^ l_vec_eff
        # localize direction to g_mat orientation
    ik_upv *= g_mat.inverse()
    ik_upv = ik_upv.normal()

    # Localize eff rotation
    ik_eff_rot = om.MQuaternion()
    mat = eff_jnt * g_mat.inverse()
    ik_eff_rot.setValue(mat.homogenize())

    return ik_root, ik_eff, ik_upv, ik_eff_rot

def encoded2IK_root_positionOffset(encoded_pose_array, char_scale):
    ik_chain_root = om.MVector(encoded_pose_array[0] * char_scale,
                               encoded_pose_array[1] * char_scale,
                               encoded_pose_array[2] * char_scale)
    return ik_chain_root
def encoded2IK_root_rotationOffset(encoded_pose_array, root_offset):
    rotation_offset = om.MQuaternion(encoded_pose_array[0],
                                    encoded_pose_array[1],
                                    encoded_pose_array[2],
                                    encoded_pose_array[3])
    # print('Quaternion = ', rotation_offset)
    # print('Root offset = ', root_offset)
    ik_chain_root = root_offset * rotation_offset.asMatrix()
    # print('IK chain root = ', ik_chain_root)
    # ik_chain_root = root_offset
    return ik_chain_root

def encoded2IK(encoded_pose_array, root_offset, char_scale, chain_scale):
    if type(root_offset) == bool:
        ik_chain_root = encoded2IK_root_positionOffset(encoded_pose_array, char_scale)
        i=3
    else:
        ik_chain_root = encoded2IK_root_rotationOffset(encoded_pose_array, root_offset)
        i=4
    ik_chain_eff = om.MVector(encoded_pose_array[i] * chain_scale,
                              encoded_pose_array[i+1] * chain_scale,
                              encoded_pose_array[i+2] * chain_scale)
    ik_chain_upv = om.MVector(encoded_pose_array[i+3],
                              encoded_pose_array[i+4],
                              encoded_pose_array[i+5])
    quat = om.MQuaternion(encoded_pose_array[i+6],
                          encoded_pose_array[i+7],
                          encoded_pose_array[i+8],
                          encoded_pose_array[i+9])
    ik_chain_eff_rot = quat.asEulerRotation()
    return ik_chain_root, ik_chain_eff, ik_chain_upv, ik_chain_eff_rot

class ikrig_encode(om.MPxNode):
    '''Encode parameters of an FK rig into
    parameters of an IKRig as described by
    Bereznyak, 2016.'''

    def compute(self, plug, datablock): #(1)
        # (1) Get handles from MPxNode's data block
        for attr in float_attrs:
            handle = datablock.inputValue(getattr(ikrig_encode,attr))
            exec(attr + "= handle.asFloat()")
        for attr in vector_attrs:
            handle = datablock.inputValue(getattr(ikrig_encode,attr))
            vec = handle.asFloatVector()
            exec(attr + "= om.MVector(vec.x, vec.y, vec.z)")
        for attr in mat_attrs:
            handle = datablock.inputValue(getattr(ikrig_encode,attr))
            exec(attr + "= handle.asMatrix()")
        mirrorHandle = datablock.inputValue(ikrig_encode.mirror)
        mirror = mirrorHandle.asBool()
        normalize_global_xfoHandle = datablock.inputValue(ikrig_encode.normalize_global_xfo)
        normalize_global_xfo = normalize_global_xfoHandle.asBool()

        # Global xfo with default hips height and 2d orientation
            # get xfo from rest pose 
        mat_hips_delta = mat_hips_rest.inverse() * mat_hips
            # use xfo to transform direction vector
        direction = om.MVector([.0,.0,1.])*mat_hips_delta
            # constraint direction to xz plane
        direction.y = 0
            # get all vectors
        zaxis = direction.normal()
        yaxis = om.MVector([.0,1.,.0])
        xaxis = yaxis^zaxis.normal()
            # build global matrix
        g_tr_x = mat_hips[12]
        g_tr_y = height_hips
        g_tr_z = mat_hips[14]
            # scale to normalize for height
        zaxis *= height_hips
        yaxis *= height_hips
        xaxis *= height_hips
        g_mat = om.MMatrix([[xaxis[0],xaxis[1],xaxis[2],0],
                    [yaxis[0],yaxis[1],yaxis[2],0],
                    [zaxis[0],zaxis[1],zaxis[2],0],
                    [g_tr_x, g_tr_y, g_tr_z, 1]])
        g_ori = om.MEulerRotation()
        g_ori = g_ori.setValue(g_mat.homogenize())

        # chains
        ik_spine_root, ik_spine_eff, ik_spine_upv, ik_spine_eff_rot = FK2encoded(g_mat, False, mat_hips, mat_spine, mat_chest, length_spine)
            # lower body roots are offsets to hips
        lower_body_mat = om.MMatrix(g_mat)
        lower_body_mat[12] = mat_hips[12]
        lower_body_mat[13] = mat_hips[13]
        lower_body_mat[14] = mat_hips[14]
        ik_leg_root_L, ik_leg_eff_L, ik_leg_upv_L, ik_leg_eff_rot_L = FK2encoded(lower_body_mat, root_offset_leg_L, mat_leg_L, mat_shin_L, mat_foot_L, length_leg_L)
        ik_leg_root_R, ik_leg_eff_R, ik_leg_upv_R, ik_leg_eff_rot_R = FK2encoded(lower_body_mat, root_offset_leg_R, mat_leg_R, mat_shin_R, mat_foot_R, length_leg_R)
            # upper body roots are offsets to neck
        upper_body_mat = om.MMatrix(g_mat)
        upper_body_mat[12] = mat_chest[12]
        upper_body_mat[13] = mat_chest[13]
        upper_body_mat[14] = mat_chest[14]
        ik_arm_root_L, ik_arm_eff_L, ik_arm_upv_L, ik_arm_eff_rot_L = FK2encoded(upper_body_mat, root_offset_arm_L, mat_shoulder_L, mat_elbow_L, mat_hand_L, length_arm_L)
        ik_arm_root_R, ik_arm_eff_R, ik_arm_upv_R, ik_arm_eff_rot_R = FK2encoded(upper_body_mat, root_offset_arm_R, mat_shoulder_R, mat_elbow_R, mat_hand_R, length_arm_R)
        ik_neck_root, ik_neck_eff, ik_neck_upv, ik_neck_eff_rot = FK2encoded(upper_body_mat, root_offset_neck, mat_neck, mat_neck_mid, mat_head, length_neck)

        if normalize_global_xfo:
            g_tr_x /= height_hips
            g_tr_z /= height_hips
        
        if g_ori.y < 0: # avoid flips on y rotation
            g_ori.y += math.radians(360)

        global_components = (g_tr_x, g_tr_z, g_ori.y)
        pos_components = [ik_spine_root, ik_spine_eff, ik_spine_upv, 
                          ik_neck_eff, ik_neck_upv,
                          ik_leg_eff_L, ik_leg_upv_L, 
                          ik_leg_eff_R, ik_leg_upv_R, 
                          ik_arm_eff_L, ik_arm_upv_L, 
                          ik_arm_eff_R, ik_arm_upv_R]
        
        rot_components = [ik_spine_eff_rot,
                         ik_neck_root, ik_neck_eff_rot,
                         ik_leg_root_L, ik_leg_eff_rot_L,
                         ik_leg_root_R, ik_leg_eff_rot_R,
                         ik_arm_root_L, ik_arm_eff_rot_L,
                         ik_arm_root_R, ik_arm_eff_rot_R]
        
        if mirror:
            global_components = (-g_tr_x, g_tr_z, -g_ori.y)
            for component in pos_components:
                component[0] *= -1
            for component in rot_components:
                component[0] *= -1
                component[3] *= -1
            out_components = [global_components,
                pos_components[0], pos_components[1], pos_components[2], rot_components[0],
                rot_components[1], pos_components[3], pos_components[4], rot_components[2],
                rot_components[5], pos_components[7], pos_components[8], rot_components[6],
                rot_components[3], pos_components[5], pos_components[6], rot_components[4],
                rot_components[9], pos_components[11], pos_components[12], rot_components[10],
                rot_components[7], pos_components[9], pos_components[10], rot_components[8]]
        else:
            out_components = [global_components,
                pos_components[0], pos_components[1], pos_components[2], rot_components[0],
                rot_components[1], pos_components[3], pos_components[4], rot_components[2],
                rot_components[3], pos_components[5], pos_components[6], rot_components[4],
                rot_components[5], pos_components[7], pos_components[8], rot_components[6],
                rot_components[7], pos_components[9], pos_components[10], rot_components[8],
                rot_components[9], pos_components[11], pos_components[12], rot_components[10]]
                          

        result_handle = datablock.outputValue(ikrig_encode.result)
        output_array = om.MFnDoubleArrayData(result_handle.data())
        output_values = []
        for component in out_components:
            for i in range(len(component)):
                output_values.append(component[i])        
        output_array.set(output_values)
        result_handle.setClean()

def create_encode():
    return ikrig_encode()
    
def init_encode():
    # (1) Setup attributes
    nAttr = om.MFnNumericAttribute()
    mAttr = om.MFnMatrixAttribute()
    tAttr = om.MFnTypedAttribute()
    kDoubleArray = om.MFnNumericData.kDoubleArray
    kFloat = om.MFnNumericData.kFloat
    k3Float = om.MFnNumericData.k3Float
    kBool = om.MFnNumericData.kBoolean

    def add_nAttr(params):
        setattr(ikrig_encode,
                params[0],
                nAttr.create(params[0], params[1], params[2]))
        nAttr.hidden = False
        nAttr.keyable = True
        return getattr(ikrig_encode, params[0])

    def add_mAttr(params):
        setattr(ikrig_encode,
                params[0],
                mAttr.create(params[0], params[1]))
        mAttr.writable = True
        mAttr.storable = True
        mAttr.connectable = True
        mAttr.hidden = False
        return getattr(ikrig_encode, params[0])

    ikrig_encode.mirror = nAttr.create('mirror', 'mi', kBool, 0)
    nAttr.hidden = False
    nAttr.keyable = True
    ikrig_encode.normalize_global_xfo = nAttr.create('normalize_global_xfo', 'nx', kBool, 1)
    nAttr.hidden = False
    nAttr.keyable = True

    in_attributes = []

    # Character size attr.
    in_attributes.append(add_nAttr(('height_hips','hh',kFloat)))
    in_attributes.append(add_nAttr(('root_offset_neck','o0', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_leg_L','o1', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_leg_R','o2', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_arm_L','o3', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_arm_R','o4', k3Float)))
    in_attributes.append(add_nAttr(('length_spine','l0', kFloat)))
    in_attributes.append(add_nAttr(('length_neck','l1', kFloat)))
    in_attributes.append(add_nAttr(('length_leg_L','l2', kFloat)))
    in_attributes.append(add_nAttr(('length_leg_R','l3', kFloat)))
    in_attributes.append(add_nAttr(('length_arm_L','l4', kFloat)))
    in_attributes.append(add_nAttr(('length_arm_R','l5', kFloat)))

    # Character positional attr.
    in_attributes.append(add_mAttr(('mat_hips_rest','hr')))
    in_attributes.append(add_mAttr(('mat_hips','h')))
    in_attributes.append(add_mAttr(('mat_spine','s')))
    in_attributes.append(add_mAttr(('mat_chest','c')))
    in_attributes.append(add_mAttr(('mat_neck','n')))
    in_attributes.append(add_mAttr(('mat_neck_mid','nm')))
    in_attributes.append(add_mAttr(('mat_head','e')))
    in_attributes.append(add_mAttr(('mat_leg_L','ll')))
    in_attributes.append(add_mAttr(('mat_shin_L','sl')))
    in_attributes.append(add_mAttr(('mat_foot_L','fl')))
    in_attributes.append(add_mAttr(('mat_leg_R','lr')))
    in_attributes.append(add_mAttr(('mat_shin_R','sr')))
    in_attributes.append(add_mAttr(('mat_foot_R','fr')))
    in_attributes.append(add_mAttr(('mat_shoulder_L','ol')))
    in_attributes.append(add_mAttr(('mat_elbow_L','el')))
    in_attributes.append(add_mAttr(('mat_hand_L','al')))
    in_attributes.append(add_mAttr(('mat_shoulder_R','or')))
    in_attributes.append(add_mAttr(('mat_elbow_R','er')))
    in_attributes.append(add_mAttr(('mat_hand_R','ar')))

    #(2) Setup the output attributes
    ikrig_encode.result = tAttr.create('result', 'r', kDoubleArray, om.MFnDoubleArrayData().create())
    tAttr.writable = False
    tAttr.storable = False
    tAttr.readable = True

    # (3) Add the attributes to the node
    for attribute in in_attributes:
        ikrig_encode.addAttribute(attribute)
    ikrig_encode.addAttribute(ikrig_encode.mirror)
    ikrig_encode.addAttribute(ikrig_encode.normalize_global_xfo)
    ikrig_encode.addAttribute(ikrig_encode.result)

    # (4) Set the attribute dependencies
    for attribute in in_attributes:
        ikrig_encode.attributeAffects(attribute, ikrig_encode.result)
    ikrig_encode.attributeAffects(ikrig_encode.mirror, ikrig_encode.result)
    ikrig_encode.attributeAffects(ikrig_encode.normalize_global_xfo, ikrig_encode.result)

class ikrig_decode(om.MPxNode):
    '''Decode parameters of an IKRig into
    positions and orientations.'''

    def compute(self, plug, datablock): #(1)
        # (1) Get handles from MPxNode's data block
        encoded_pose_handle = datablock.inputValue(ikrig_decode.encoded_pose)
        encoded_pose_marray = om.MFnDoubleArrayData(encoded_pose_handle.data())
        encoded_pose_array = encoded_pose_marray.array()
        offset_mat_Handle = datablock.inputValue(ikrig_decode.offset_mat)
        offset_mat = offset_mat_Handle.asMatrix()
        for attr in float_attrs:
            handle = datablock.inputValue(getattr(ikrig_decode,attr))
            exec(attr + "= handle.asFloat()")
        for attr in vector_attrs:
            handle = datablock.inputValue(getattr(ikrig_decode,attr))
            vec = handle.asFloatVector()
            exec(attr + "= om.MVector(vec.x, vec.y, vec.z)")
        for attr in out_float3_attrs:
            handle = datablock.outputValue(getattr(ikrig_decode,attr))
            exec(attr + "_Handle = handle")
        global_mat_Handle = datablock.outputValue(ikrig_decode.global_mat)
        normalized_global_xfoHandle = datablock.inputValue(ikrig_decode.normalized_global_xfo)
        normalized_global_xfo = normalized_global_xfoHandle.asBool()

        if len(encoded_pose_array) != 86:
            print('Encoded pose with wrong length, expecting 86 dimensions got ' + str(len(encoded_pose_array)))
            return
        
        # Global character transform
        g_tr_x = encoded_pose_array[0]
        g_tr_y = 0
        g_tr_z = encoded_pose_array[1]
        g_ori = om.MEulerRotation(0, encoded_pose_array[2], 0)
        g_mat = g_ori.asMatrix()
        if normalized_global_xfo:
            g_tr_x *= height_hips
            g_tr_z *= height_hips
        g_mat[12] = g_tr_x
        g_mat[13] = g_tr_y
        g_mat[14] = g_tr_z
        g_mat *= offset_mat
        global_mat_Handle.setMMatrix(g_mat)

        ik_spine_root,ik_spine_eff, ik_spine_upv, ik_spine_eff_rot = encoded2IK(encoded_pose_array[3:16],
                                                                                False,
                                                                                height_hips,
                                                                                length_spine)
        ik_spine_root.y += height_hips
        ik_neck_root,ik_neck_eff,ik_neck_upv,ik_neck_eff_rot = encoded2IK(encoded_pose_array[16:30],
                                                                          root_offset_neck,
                                                                          height_hips,
                                                                          length_neck)
        ik_leg_root_L,ik_leg_eff_L,ik_leg_upv_L,ik_leg_eff_rot_L = encoded2IK(encoded_pose_array[30:44],
                                                                              root_offset_leg_L, 
                                                                              height_hips,
                                                                              length_leg_L)
        ik_leg_root_R,ik_leg_eff_R,ik_leg_upv_R,ik_leg_eff_rot_R = encoded2IK(encoded_pose_array[44:58],
                                                                              root_offset_leg_R,
                                                                              height_hips,
                                                                              length_leg_R)
        ik_arm_root_L,ik_arm_eff_L,ik_arm_upv_L,ik_arm_eff_rot_L = encoded2IK(encoded_pose_array[58:72],
                                                                              root_offset_arm_L,
                                                                              height_hips,
                                                                              length_arm_L)
        ik_arm_root_R,ik_arm_eff_R,ik_arm_upv_R,ik_arm_eff_rot_R = encoded2IK(encoded_pose_array[72:86],
                                                                              root_offset_arm_R,
                                                                              height_hips,
                                                                              length_arm_R)
        ik_neck_root = ik_neck_root * ik_spine_eff_rot.asMatrix()
        ik_arm_root_L = ik_arm_root_L * ik_spine_eff_rot.asMatrix()
        ik_arm_root_R = ik_arm_root_R * ik_spine_eff_rot.asMatrix()

        ik_Spine_root_Handle.set3Float(ik_spine_root[0],ik_spine_root[1],ik_spine_root[2])
        ik_Spine_eff_Handle.set3Float(ik_spine_eff[0],ik_spine_eff[1],ik_spine_eff[2])
        ik_Spine_dir_Handle.set3Float(ik_spine_upv[0],ik_spine_upv[1],ik_spine_upv[2])
        ik_Spine_eff_rot_Handle.set3Double(ik_spine_eff_rot[0],ik_spine_eff_rot[1],ik_spine_eff_rot[2])
        ik_Neck_root_Handle.set3Float(ik_neck_root[0],ik_neck_root[1],ik_neck_root[2])
        ik_Neck_eff_Handle.set3Float(ik_neck_eff[0],ik_neck_eff[1],ik_neck_eff[2])
        ik_Neck_dir_Handle.set3Float(ik_neck_upv[0],ik_neck_upv[1],ik_neck_upv[2])
        ik_Neck_eff_rot_Handle.set3Double(ik_neck_eff_rot[0],ik_neck_eff_rot[1],ik_neck_eff_rot[2])
        ik_Leg_root_L_Handle.set3Float(ik_leg_root_L[0],ik_leg_root_L[1],ik_leg_root_L[2])
        ik_Leg_eff_L_Handle.set3Float(ik_leg_eff_L[0],ik_leg_eff_L[1],ik_leg_eff_L[2])
        ik_Leg_dir_L_Handle.set3Float(ik_leg_upv_L[0],ik_leg_upv_L[1],ik_leg_upv_L[2])
        ik_Leg_eff_rot_L_Handle.set3Double(ik_leg_eff_rot_L[0],ik_leg_eff_rot_L[1],ik_leg_eff_rot_L[2])
        ik_Leg_root_R_Handle.set3Float(ik_leg_root_R[0],ik_leg_root_R[1],ik_leg_root_R[2])
        ik_Leg_eff_R_Handle.set3Float(ik_leg_eff_R[0],ik_leg_eff_R[1],ik_leg_eff_R[2])
        ik_Leg_dir_R_Handle.set3Float(ik_leg_upv_R[0],ik_leg_upv_R[1],ik_leg_upv_R[2])
        ik_Leg_eff_rot_R_Handle.set3Double(ik_leg_eff_rot_R[0],ik_leg_eff_rot_R[1],ik_leg_eff_rot_R[2])
        ik_Arm_root_L_Handle.set3Float(ik_arm_root_L[0],ik_arm_root_L[1],ik_arm_root_L[2])
        ik_Arm_eff_L_Handle.set3Float(ik_arm_eff_L[0],ik_arm_eff_L[1],ik_arm_eff_L[2])
        ik_Arm_dir_L_Handle.set3Float(ik_arm_upv_L[0],ik_arm_upv_L[1],ik_arm_upv_L[2])
        ik_Arm_eff_rot_L_Handle.set3Double(ik_arm_eff_rot_L[0],ik_arm_eff_rot_L[1],ik_arm_eff_rot_L[2])
        ik_Arm_root_R_Handle.set3Float(ik_arm_root_R[0],ik_arm_root_R[1],ik_arm_root_R[2])
        ik_Arm_eff_R_Handle.set3Float(ik_arm_eff_R[0],ik_arm_eff_R[1],ik_arm_eff_R[2])   
        ik_Arm_dir_R_Handle.set3Float(ik_arm_upv_R[0],ik_arm_upv_R[1],ik_arm_upv_R[2])
        ik_Arm_eff_rot_R_Handle.set3Double(ik_arm_eff_rot_R[0],ik_arm_eff_rot_R[1],ik_arm_eff_rot_R[2])
        ik_Spine_root_Handle.setClean()
        ik_Spine_eff_Handle.setClean()
        ik_Spine_dir_Handle.setClean()
        ik_Spine_eff_rot_Handle.setClean()
        ik_Neck_root_Handle.setClean()
        ik_Neck_eff_Handle.setClean()
        ik_Neck_dir_Handle.setClean()
        ik_Neck_eff_rot_Handle.setClean()
        ik_Leg_root_L_Handle.setClean()
        ik_Leg_eff_L_Handle.setClean()
        ik_Leg_dir_L_Handle.setClean()
        ik_Leg_eff_rot_L_Handle.setClean()
        ik_Leg_root_R_Handle.setClean()
        ik_Leg_eff_R_Handle.setClean()
        ik_Leg_dir_R_Handle.setClean()
        ik_Leg_eff_rot_R_Handle.setClean()
        ik_Arm_root_L_Handle.setClean()
        ik_Arm_eff_L_Handle.setClean()
        ik_Arm_dir_L_Handle.setClean()
        ik_Arm_eff_rot_L_Handle.setClean()
        ik_Arm_root_R_Handle.setClean()
        ik_Arm_eff_R_Handle.setClean()
        ik_Arm_dir_R_Handle.setClean()
        ik_Arm_eff_rot_R_Handle.setClean()

def create_decode():
    return ikrig_decode()

def init_decode():
    # (1) Setup attributes
    nAttr = om.MFnNumericAttribute()    # Maya's Numeric Attribute class
    tAttr = om.MFnTypedAttribute()
    mAttr = om.MFnMatrixAttribute()
    uAttr = om.MFnUnitAttribute()
    kFloat = om.MFnNumericData.kFloat   # Maya's float type
    k3Float = om.MFnNumericData.k3Float   # Maya's float type
    kAngle = om.MFnUnitAttribute.kAngle
    kDoubleArray = om.MFnNumericData.kDoubleArray
    kBool = om.MFnNumericData.kBoolean

        # Setup attribute helper functions and classes
    def add_nAttr(params):
        setattr(ikrig_decode,
                params[0],
                nAttr.create(params[0], params[1], params[2]))
        nAttr.hidden = False
        nAttr.keyable = True
        return getattr(ikrig_decode, params[0])

    def add_out_nAttr(params):
        setattr(ikrig_decode,
                params[0],
                nAttr.create(params[0], params[1], params[2]))
        mAttr.writable = False
        mAttr.storable = False
        mAttr.readable = True
        return getattr(ikrig_decode, params[0])
    
    class out_euler_nAttr:
        i=0

        def create(self, params):
            rotX = uAttr.create("rotateX" + str(self.i), "rx" + str(self.i), kAngle)
            uAttr.writable = False
            uAttr.storable = False
            rotY = uAttr.create("rotateY" + str(self.i), "ry" + str(self.i), kAngle)
            uAttr.writable = False
            uAttr.storable = False
            rotZ = uAttr.create("rotateZ" + str(self.i), "rz" + str(self.i), kAngle)
            uAttr.writable = False
            uAttr.storable = False
            setattr(ikrig_decode,
                    params[0],
                    nAttr.create(params[0], params[1], rotX, rotY, rotZ))
            nAttr.writable = False
            nAttr.storable = False
            nAttr.readable = True
            self.i += 1
            return getattr(ikrig_decode, params[0])
    euler_nAttr = out_euler_nAttr()  

        
    # (2) Setup the input attributes
    in_attributes = []
    ikrig_decode.encoded_pose = tAttr.create('encoded_pose', 'ep', kDoubleArray, om.MFnDoubleArrayData().create())
    tAttr.connectable = True
    tAttr.hidden = False
    ikrig_decode.offset_mat = mAttr.create('offset_mat', 'om')
    mAttr.keyable = True
    mAttr.hidden = False
    in_attributes.append(ikrig_decode.encoded_pose)
    in_attributes.append(ikrig_decode.offset_mat)
    in_attributes.append(add_nAttr(('height_hips','hh',kFloat)))
    in_attributes.append(add_nAttr(('root_offset_neck','o0', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_leg_L','o1', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_leg_R','o2', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_arm_L','o3', k3Float)))
    in_attributes.append(add_nAttr(('root_offset_arm_R','o4', k3Float)))
    in_attributes.append(add_nAttr(('length_spine','l0', kFloat)))
    in_attributes.append(add_nAttr(('length_neck','l1', kFloat)))
    in_attributes.append(add_nAttr(('length_leg_L','l2', kFloat)))
    in_attributes.append(add_nAttr(('length_leg_R','l3', kFloat)))
    in_attributes.append(add_nAttr(('length_arm_L','l4', kFloat)))
    in_attributes.append(add_nAttr(('length_arm_R','l5', kFloat)))
    ikrig_decode.normalized_global_xfo = nAttr.create('normalized_global_xfo', 'nx', kBool, 1)
    nAttr.hidden = False
    nAttr.keyable = True

    # (3) Setup the output attributes
    out_attributes = []
    ikrig_decode.global_mat = mAttr.create('global_mat', 'gm')
    mAttr.writable = False
    mAttr.storable = False
    mAttr.connectable = True
    mAttr.readable = True
    out_attributes.append(ikrig_decode.global_mat)
    out_attributes.append(add_out_nAttr(('ik_Spine_root','ikp0', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Spine_dir','ikd0', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Spine_eff','ike0', k3Float)))
    out_attributes.append(euler_nAttr.create(('ik_Spine_eff_rot', 'ikr0')))
    out_attributes.append(add_out_nAttr(('ik_Neck_root','ikp1', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Neck_dir','ikd1', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Neck_eff','ike1', k3Float)))
    out_attributes.append(euler_nAttr.create(('ik_Neck_eff_rot', 'ikr1')))
    out_attributes.append(add_out_nAttr(('ik_Leg_root_L','ikp2', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Leg_dir_L','ikd2', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Leg_eff_L','ike2', k3Float)))
    out_attributes.append(euler_nAttr.create(('ik_Leg_eff_rot_L', 'ikr2')))
    out_attributes.append(add_out_nAttr(('ik_Leg_root_R','ikp3', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Leg_dir_R','ikd3', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Leg_eff_R','ike3', k3Float)))
    out_attributes.append(euler_nAttr.create(('ik_Leg_eff_rot_R', 'ikr3')))
    out_attributes.append(add_out_nAttr(('ik_Arm_root_L','ikp4', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Arm_dir_L','ikd4', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Arm_eff_L','ike4', k3Float)))
    out_attributes.append(euler_nAttr.create(('ik_Arm_eff_rot_L', 'ikr4')))
    out_attributes.append(add_out_nAttr(('ik_Arm_root_R','ikp5', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Arm_dir_R','ikd5', k3Float)))
    out_attributes.append(add_out_nAttr(('ik_Arm_eff_R','ike5', k3Float)))  
    out_attributes.append(euler_nAttr.create(('ik_Arm_eff_rot_R', 'ikr5')))

    # (4) Add the attributes to the node
    for attribute in in_attributes:
        ikrig_decode.addAttribute(attribute)
    for attribute in out_attributes:
        ikrig_decode.addAttribute(attribute)
    ikrig_decode.addAttribute(ikrig_decode.normalized_global_xfo)

    # (5) Set the attribute dependencies
    for out_attribute in out_attributes:
        ikrig_decode.attributeAffects(ikrig_decode.normalized_global_xfo, out_attribute)
        for in_attribute in in_attributes:
            ikrig_decode.attributeAffects(in_attribute, out_attribute)

def _toplugin(mobject):
    return om.MFnPlugin(
        mobject, 'Gustavo E. Boehs', '1.00')
def initializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.registerNode(encode_nodeName, encode_nodeTypeID, create_encode, init_encode)
    plugin.registerNode(decode_nodeName, decode_nodeTypeID, create_decode, init_decode)
def uninitializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.deregisterNode(encode_nodeTypeID)
    plugin.deregisterNode(decode_nodeTypeID)