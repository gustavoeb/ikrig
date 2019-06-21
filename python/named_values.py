from maya import cmds

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