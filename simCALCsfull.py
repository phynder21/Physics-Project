#imports
import pandas as pd
import numpy as np
import math
from vpython import *
#world vars (set by sliders)
wind_V = 3.0
wind_angle = 30

wind_VX = wind_V  * math.cos(math.radians(wind_angle))
wind_VY = wind_V  * math.sin(math.radians(wind_angle))

#BODY TUBE
BT_length = 15.0
BT_dia = 4.0
BT_density = 2.0
BT_mass = math.pi * 2 * BT_dia/2 * BT_length* BT_density * 0.003

#FINS
F_root = 4.0
F_tip = 5.0
F_span = 2.0
F_sweep = 3.0
F_num = 4
F_density =2.0
F_thickness = 0.003

F_mass = F_num * (((0.5) * (F_root +F_tip)*F_span) *F_thickness *F_density)

#F_mass 
#NOSE
NC_shape = "Parabolic" #("Ogive", "Parabolic", "Conical")
NC_length = 3.0
NC_density = 2.0
NC_thickness =0.003

if NC_shape == "Conical":
    slant = math.sqrt(NC_length**2 + (BT_dia/2)**2)
    NC_area = math.pi * (BT_dia/2) * slant
if NC_shape == "Ogive":
    rho_ogive = ((BT_dia/2)**2 + NC_length**2) / (2*BT_dia/2)
    NC_area = 2 * math.pi * rho_ogive * (rho_ogive - math.sqrt(rho_ogive**2 - (BT_dia/2)**2))
if NC_shape == "Parabolic":
    n = 1000
    xs = [NC_length * i/n for i in range(n+1)]
    area = 0
    for i in range(1, len(xs)):
        x_mid = (xs[i] + xs[i-1]) / 2
        r_mid = BT_dia/2 * (1 - (x_mid/NC_length)**2)
        dydx  = -2 * BT_dia/2 * x_mid / NC_length**2
        area += 2 * math.pi * r_mid * math.sqrt(1 + dydx**2) * (xs[i] - xs[i-1])
    NC_area = area

NC_mass = NC_area * NC_thickness * NC_density

#PARACHUTE 
PC_line = 6.0
PC_diam = 15 
PC_density = 0.06
PC_mass = (math.pi * (PC_diam/2)**2) * PC_density

#MOTOR 
motor_sel = "C6"
motor_dc = 4.0

#general constants 
total_length = NC_length + BT_length
A_ref = math.pi * (BT_dia/2)**2

#more general constants
g=9.81
rho = 1.225
mu = 1.81e-5
dt =0.01
sim_mode = False
t=0
vx = 0
vy = 0

#motor data

df_c6 = pd.read_csv('C6.csv')
df_d12 = pd.read_csv('D12.csv')
df_f15 = pd.read_csv('F15.csv')

motors = [df_c6, df_d12, df_f15]
labels = ['C6', 'D12', 'F15']
motor_lengths = [0.07, 0.07,0.114]
prop_masses = [0.011,0.021,0.06]
dry_masses = [0.013, 0.023,0.042 ]

def build_motor(df, mass_prop, mass_dry,name,motor_length):
    time_arr = np.insert(df['Time'].to_numpy(), 0, 0.0)
    Thrust_arr = np.insert(df['Thrust'].to_numpy(), 0,0.0)

    impulse = np.trapezoid(Thrust_arr, x = time_arr)
    v_e = impulse/mass_prop
    v_e = round(v_e, 4)
    burn_time = time_arr[-1]
    dm_dt_arr = Thrust_arr/v_e
    cumalative_mass_lost = np.zeros_like(time_arr)
    for i in range(1, len(time_arr)):
        avg= (dm_dt_arr[i] +dm_dt_arr[i-1])/2
        cumalative_mass_lost[i] = cumalative_mass_lost[i-1] + (avg)*(time_arr[i] -time_arr[i-1])
    
    def thrust(time):
        return float(np.interp(time, time_arr, Thrust_arr))
    def dm(time):
        if time <= 0 or time >= burn_time:
            return 0
        else:
            return float(np.interp(time, time_arr, cumalative_mass_lost))
    mass = mass_dry +mass_prop

    return {'name': name, 'v_e': v_e, 'burn_time': burn_time, 'thrust': thrust, 'dm': dm ,'mass': mass, 'length': motor_length}

motor_data = [ build_motor(df, mass_prop, mass_dry,name) for df,mass_prop, mass_dry, name, length in zip(motors, prop_masses, dry_masses, labels, motor_lengths)]

if motor_sel == "C6": motor =motor_data[0]
elif motor_sel == "D12": motor =motor_data[1]
elif motor_sel == "F15": motor =motor_data[2]

#center of pressure and center of gravity locations and force
def calc_CG(time):
    x_CG_tube = NC_length + BT_length/2
    x_CG_fins = NC_length + BT_length - F_root +F_sweep/2 +F_root/2
    x_CG_motor = NC_length + BT_length - motor['length']/2
    x_CG_NC = (3/4) * (NC_length)
    x_CG_PC = NC_length

    mass_motor = motor['mass'] - motor['dm'](time) 

    total_mass = mass_motor + BT_mass + F_mass + NC_mass +PC_mass
    x_CG = (x_CG_tube * BT_mass + x_CG_fins * F_mass + x_CG_motor * mass_motor + x_CG_NC * NC_mass + x_CG_PC * PC_mass)/ total_mass 

    return x_CG, total_mass , x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC

def calc_CP(t):
    if NC_shape == "Ogive":
        X_CP_NC = (2/3)*(NC_length)
    elif NC_shape == "Parabolic":
        X_CP_NC = (0.466)*(NC_length)
    elif NC_shape =="Conical":
        X_CP_NC = (0.5)*(NC_length)
    CN_NC= 2

    if (F_num == 4) or (F_num ==3):
        K = 1 + (BT_dia/2)/( F_span + BT_dia/2)
    elif (F_num == 6):
        K = 1 + (BT_dia/4)/( F_span + BT_dia/2)
    l = math.sqrt(F_sweep**2 +((F_root-F_tip)/2 + F_sweep)**2)
    C_N_finbefore = ((4)*(F_num)*(F_span/BT_dia)**2)/(1+ math.sqrt(1+ ((2*l)/(F_root+F_tip))**2))
    CN_F = K * C_N_finbefore
    X_CP_F = NC_length + BT_length - F_root + (F_sweep*(F_root+F_tip))/(3*(F_root+F_tip)) + (1/6)*(F_root+F_tip-( F_root * F_tip)/(F_root+F_tip) )

    CN_total = CN_NC + CN_F
    X_CP = (CN_NC * X_CP_NC + CN_F * X_CP_F)/CN_total

    return X_CP, CN_total

#drag force and coeff
def calc_CD(speed, t):
    Re = max(rho * speed * total_length/ mu , 1e4 )
    Cf = 0.074/Re**2


    fin_base = 0.5 * (F_root + F_tip) * F_span
    A_wet = math.pi * BT_dia * total_length * F_num * fin_base
    fineness = total_length/ BT_dia
    CD_frict = Cf * (1+1/(2 *fineness)) * (A_wet/ A_ref)

    half_angle = math.atan((BT_dia/2)/ NC_length)
    if NC_shape == "Ogive":
        CD_nose = (0.7) * math.sin(half_angle)**2
    if NC_shape == "Parabolic":
        CD_nose = (0.6) * math.sin(half_angle)**2
    if NC_shape == "Conical":
        CD_nose = (0.8) * math.sin(half_angle)**2

    if t < motor['burn_time']: CD_base =0.12 
    else: CD_base =0.25

    t_fin =0.002
    CD_interference = 0.04 * F_num * (t_fin/ BT_dia) #whaaaaaatidk where i got this

    return CD_frict + CD_nose + CD_base + CD_interference

def drag_force(vx,vy, speed,time):
    if speed< 0.01: 
        return 0.0 ,0.0
    else: 
        CD = calc_CD(speed,time)
        F = 0.5 * rho * speed**2 *CD * A_ref
        return -F * (vx/speed), -F *(vy/speed)

#normal force 
def normal_force(vx,vy,speed,theta):
        rocket_ax = math.sin(theta)
        rocket_ay = math.cos(theta)
        perp_x = math.cos(theta)
        perp_y = -math.sin(theta)

        vrel_x = wind_VX - vx
        vrel_y = wind_VY -vy
        vrel_along = vrel_x*rocket_ax + vrel_y*rocket_ay
        vrel_perp  = vrel_x*perp_x   + vrel_y*perp_y
        vrel_mag   = math.sqrt(vrel_x**2 + vrel_y**2)

        alpha = math.atan2(vrel_perp, vrel_along)

        x_CP, C_N_total = calc_CP()
        F_N = 0.5 * rho * vrel_mag**2 * C_N_total * alpha * A_ref

        return F_N * perp_x, F_N * perp_y

#moment of inertia about the CG
def calc_IN(t):
    x_CG, total_mass , x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC = calc_CG(t)
    BT_I_self = BT_mass * (3*(BT_dia/2)**2 + BT_length**2)/12
    BT_I = BT_I_self + BT_mass * (x_CG_tube -x_CG)**2 #look at that super cool parrallel axis theorem magic

    NC_I_self = NC_mass * (3*(BT_dia/2)**2/20 + NC_length**2/10)
    NC_I = NC_I_self + NC_mass * (x_CG_NC - x_CG)**2

    F_I_self = F_mass * #ill do ltr

    # I_fin_own = m_f * (state["fin_a"]**2 + state["fin_s"]**2) / 12
    # I_fins = I_fin_own + m_f * (x_f - x_CG)**2

    motor_I = motor['mass'] * ((BT_dia/2)**2/4+(0.07**2)/12) + motor['mass'] * (x_CG_motor-x_CG)**2

    return motor_I + BT_I +NC_I + F_I_self

#wind force 

#UPDATES IN SIM
#rk4 --> updating acceleration --> updating velcity, height, pitch, vertical velocity, roll, horizontal dist)
#

while sim_mode:
    rate(1/dt)

    #rereunning functions 
    
    #recalculating constants
    speed = math.sqrt(vx**2 +vy**2)
    F_drag_x, F_drag_y = drag_force(vx,vy,speed,t)
    Thrust_x = motor['Thrust'](t) * vx/speed
    Thrust_y = motor['Thrust'](t) *vy/speed
    x_CG, total_mass , x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC = calc_CG(t)
    Fg_y = -total_mass * g

    FX_tot = F_drag_x + Thrust_x
    FY_tot = F_drag_y +Thrust_y + Fg_y
    t = t + dt

F_tot

#after burn time+delay charge jsut model a lump of mass and a parachute since nothing else really matters