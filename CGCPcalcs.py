#parameters (all adjustable in simulation)
#BODY TUBE
BT_length = 15.0
BT_dia = 4.0
#FINS
F_root = 4.0
F_tip = 5.0
F_span = 2.0
F_sweep = 3.0
F_num = 4
#NOSE
NC_shape = "Parabolic" #("Ogive", "Parabolic", "Conical")
NC_length = 3.0
#PARACHUTE (later)
#MOTOR (later)

#Center of Pressures and drags
if NC_shape == "Ogive":
    X_NC = (2/3)(NC_length)
elif NC_shape == "Parabolic":
    X_NC = (0.466)(NC_length)
elif NC_shape =="Conical":
    X_NC = (0.5)(NC_length)

#Normal Coeffs
C_N_NC =2
if (F_num == 4) or (F_num ==3):
    K = 1 + (BT_dia/2)/( F_span + BT_dia/2)
elif (F_num == 6):
    K = 1 + (BT_dia/4)/( F_span + BT_dia/2)
C_N_finbefore = 
C_N_F = K

#Center of Gravitys
x_BT = NC_length + (BT_length/2)
x_NC = (0.75)(NC_length)
offset = NC_length + BT_length - F_root
x_F = offset + F_sweep/2 + F_root/2

#Summing Everything