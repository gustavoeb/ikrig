from maya import cmds
import maya.api.OpenMaya as om

def print_named_values(node_name):
    encoded = cmds.getAttr(node_name +'.result')
    s = "Global pos (x,z): {0:4.2f},{1:4.2f} \n" \
        "Global rotation (y): {2:4.2f} \n" \
        "Spine position offset to hips rest: {3:4.2f},{4:4.2f},{5:4.2f}\n" \
        "Spine effector: {6:4.2f},{7:4.2f},{8:4.2f}\n" \
        "Spine pole vector: {9:4.2f},{10:4.2f},{11:4.2f}\n" \
        "Spine effector rotation: {12:4.2f},{13:4.2f},{14:4.2f},{15:4.2f}\n" \
        "Neck rotation offset to spine effector: {16:4.2f},{17:4.2f},{18:4.2f},{19:4.2f}\n" \
        "Neck effector: {20:4.2f},{21:4.2f},{22:4.2f}\n" \
        "Neck pole vector: {23:4.2f},{24:4.2f},{25:4.2f}\n" \
        "Neck effector rotation: {26:4.2f},{27:4.2f},{28:4.2f},{29:4.2f}\n" \
        "Leg (L) rotation offset to spine root: {30:4.2f},{31:4.2f},{32:4.2f},{33:4.2f}\n" \
        "Leg (L) effector: {34:4.2f},{35:4.2f},{36:4.2f}\n" \
        "Leg (L) pole vector: {37:4.2f},{38:4.2f},{39:4.2f}\n" \
        "Leg (L) effector rotation: {40:4.2f},{41:4.2f},{42:4.2f},{43:4.2f}\n" \
        "Leg (R) rotation offset to spine root: {44:4.2f},{45:4.2f},{46:4.2f},{47:4.2f}\n" \
        "Leg (R) effector: {48:4.2f},{49:4.2f},{50:4.2f}\n" \
        "Leg (R) pole vector: {51:4.2f},{52:4.2f},{53:4.2f}\n" \
        "Leg (R) effector rotation: {54:4.2f},{55:4.2f},{56:4.2f},{57:4.2f}\n" \
        "Arm (L) rotation offset to spine effector: {58:4.2f},{59:4.2f},{60:4.2f},{61:4.2f}\n" \
        "Arm (L) effector: {62:4.2f},{63:4.2f},{64:4.2f}\n" \
        "Arm (L) pole vector: {65:4.2f},{66:4.2f},{67:4.2f}\n" \
        "Arm (L) effector rotation: {68:4.2f},{69:4.2f},{70:4.2f},{71:4.2f}\n" \
        "Arm (R) rotation offset to spine effector: {72:4.2f},{73:4.2f},{74:4.2f},{75:4.2f}\n" \
        "Arm (R) effector: {76:4.2f},{77:4.2f},{78:4.2f}\n" \
        "Arm (R) pole vector: {79:4.2f},{80:4.2f},{81:4.2f}\n" \
        "Arm (R) effector rotation: {82:4.2f},{83:4.2f},{84:4.2f},{85:4.2f}\n"
    print s.format(*encoded)

def directionBetweenMats(mat1,mat2):
    vec1 = om.MVector(mat1[3][0:3])
    vec2 = om.MVector(mat2[3][0:3])
    result = vec2-vec1
    return result
    
def lengthBetweenMats(mat1,mat2):
    vec1 = om.MVector(mat1[3][0:3])
    vec2 = om.MVector(mat2[3][0:3])
    result = vec2-vec1
    return result.length()

def wire_FK_to_IKRig(name_mapping):
    ikrig_node = pmc.createNode('ikrig_encode')
    ikrig_name = ikrig_node.name()

    for in_attr, out_attr in name_mapping.iteritems():
        pmc.connectAttr(out_attr + '.worldMatrix', ikrig_name + '.' + in_attr)

    # setup static attributes
    mat_hips = pmc.getAttr(name_mapping.get('mat_hips') + '.worldMatrix')
    mat_chest = pmc.getAttr(name_mapping.get('mat_chest') + '.worldMatrix')
    mat_neck = pmc.getAttr(name_mapping.get('mat_neck') + '.worldMatrix')
    mat_head = pmc.getAttr(name_mapping.get('mat_head') + '.worldMatrix')
    mat_leg_L = pmc.getAttr(name_mapping.get('mat_leg_L') + '.worldMatrix')
    mat_foot_L = pmc.getAttr(name_mapping.get('mat_foot_L') + '.worldMatrix')
    mat_leg_R = pmc.getAttr(name_mapping.get('mat_leg_R') + '.worldMatrix')
    mat_foot_R = pmc.getAttr(name_mapping.get('mat_foot_R') + '.worldMatrix')
    mat_shoulder_L = pmc.getAttr(name_mapping.get('mat_shoulder_L') + '.worldMatrix')
    mat_hand_L = pmc.getAttr(name_mapping.get('mat_hand_L') + '.worldMatrix')
    mat_shoulder_R = pmc.getAttr(name_mapping.get('mat_shoulder_R') + '.worldMatrix')
    mat_hand_R = pmc.getAttr(name_mapping.get('mat_hand_R') + '.worldMatrix')

    pmc.setAttr(ikrig_name + '.mat_hips_rest', mat_hips) 
    pmc.setAttr(ikrig_name + '.height_hips', mat_hips[3][1]) # y value of mat hips
    pmc.setAttr(ikrig_name + '.length_spine', lengthBetweenMats(mat_hips, mat_chest))
    pmc.setAttr(ikrig_name + '.length_neck', lengthBetweenMats(mat_neck, mat_head))
    pmc.setAttr(ikrig_name + '.length_leg_L', lengthBetweenMats(mat_leg_L, mat_foot_L))
    pmc.setAttr(ikrig_name + '.length_leg_R', lengthBetweenMats(mat_leg_R, mat_foot_R))
    pmc.setAttr(ikrig_name + '.length_arm_L', lengthBetweenMats(mat_shoulder_L, mat_hand_L))
    pmc.setAttr(ikrig_name + '.length_arm_R', lengthBetweenMats(mat_shoulder_R, mat_hand_R))
    pmc.setAttr(ikrig_name + '.root_offset_neck', directionBetweenMats(mat_chest, mat_neck))
    pmc.setAttr(ikrig_name + '.root_offset_leg_L', directionBetweenMats(mat_hips, mat_leg_L))
    pmc.setAttr(ikrig_name + '.root_offset_leg_R', directionBetweenMats(mat_hips, mat_leg_R))
    pmc.setAttr(ikrig_name + '.root_offset_arm_L', directionBetweenMats(mat_chest, mat_shoulder_L))
    pmc.setAttr(ikrig_name + '.root_offset_arm_R', directionBetweenMats(mat_chest, mat_shoulder_R))

def setup_IKRig_decode(name_mapping):
    ikrig_node = pmc.createNode('ikrig_decode')
    ikrig_name = ikrig_node.name()
    # setup static attributes
    mat_hips = pmc.getAttr(name_mapping.get('mat_hips') + '.worldMatrix')
    mat_chest = pmc.getAttr(name_mapping.get('mat_chest') + '.worldMatrix')
    mat_neck = pmc.getAttr(name_mapping.get('mat_neck') + '.worldMatrix')
    mat_head = pmc.getAttr(name_mapping.get('mat_head') + '.worldMatrix')
    mat_leg_L = pmc.getAttr(name_mapping.get('mat_leg_L') + '.worldMatrix')
    mat_foot_L = pmc.getAttr(name_mapping.get('mat_foot_L') + '.worldMatrix')
    mat_leg_R = pmc.getAttr(name_mapping.get('mat_leg_R') + '.worldMatrix')
    mat_foot_R = pmc.getAttr(name_mapping.get('mat_foot_R') + '.worldMatrix')
    mat_shoulder_L = pmc.getAttr(name_mapping.get('mat_shoulder_L') + '.worldMatrix')
    mat_hand_L = pmc.getAttr(name_mapping.get('mat_hand_L') + '.worldMatrix')
    mat_shoulder_R = pmc.getAttr(name_mapping.get('mat_shoulder_R') + '.worldMatrix')
    mat_hand_R = pmc.getAttr(name_mapping.get('mat_hand_R') + '.worldMatrix')
    pmc.setAttr(ikrig_name + '.height_hips', mat_hips[3][1]) # y value of mat hips
    pmc.setAttr(ikrig_name + '.length_spine', lengthBetweenMats(mat_hips, mat_chest))
    pmc.setAttr(ikrig_name + '.length_neck', lengthBetweenMats(mat_neck, mat_head))
    pmc.setAttr(ikrig_name + '.length_leg_L', lengthBetweenMats(mat_leg_L, mat_foot_L))
    pmc.setAttr(ikrig_name + '.length_leg_R', lengthBetweenMats(mat_leg_R, mat_foot_R))
    pmc.setAttr(ikrig_name + '.length_arm_L', lengthBetweenMats(mat_shoulder_L, mat_hand_L))
    pmc.setAttr(ikrig_name + '.length_arm_R', lengthBetweenMats(mat_shoulder_R, mat_hand_R))
    pmc.setAttr(ikrig_name + '.root_offset_neck', directionBetweenMats(mat_chest, mat_neck))
    pmc.setAttr(ikrig_name + '.root_offset_leg_L', directionBetweenMats(mat_hips, mat_leg_L))
    pmc.setAttr(ikrig_name + '.root_offset_leg_R', directionBetweenMats(mat_hips, mat_leg_R))
    pmc.setAttr(ikrig_name + '.root_offset_arm_L', directionBetweenMats(mat_chest, mat_shoulder_L))
    pmc.setAttr(ikrig_name + '.root_offset_arm_R', directionBetweenMats(mat_chest, mat_shoulder_R))

cmu_name_mapping = {'mat_hips':'Hips',
                    'mat_spine':'Spine',
                    'mat_chest':'Spine1',
                    'mat_neck':'Neck',
                    'mat_neck_mid':'Neck1',
                    'mat_head':'Head',
                    'mat_leg_L':'LeftUpLeg',
                    'mat_shin_L':'LeftLeg',
                    'mat_foot_L':'LeftFoot',
                    'mat_leg_R':'RightUpLeg',
                    'mat_shin_R':'RightLeg',
                    'mat_foot_R':'RightFoot',
                    'mat_shoulder_L':'LeftArm',
                    'mat_elbow_L':'LeftForeArm',
                    'mat_hand_L':'LeftHand',
                    'mat_shoulder_R':'RightArm',
                    'mat_elbow_R':'RightForeArm',
                    'mat_hand_R':'RightHand'}