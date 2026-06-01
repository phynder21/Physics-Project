#imports
import pandas as pd
import numpy as np
import math
from vpython import *
#world vars (set by sliders)
wind_V = 3.0
wind_angle = 30

wind_VX = math.cos(math.radians(wind_angle))
wind_VY = math.sin(math.radians(wind_angle))

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
#PARACHUTE 
PC_line = 6.0
PC_diam = 15 
#MOTOR 
motor_sel = "C6"

#general constants 
g=9.81

#THRUST and dt

df_c6 = pd.read_csv('C6.csv')
df_d12 = pd.read_csv('D12.csv')
df_f15 = pd.read_csv('F15.csv')

motors = [df_c6, df_d12, df_f15]
labels = ['C6', 'D12', 'F15']
prop_masses = [0.011,0.021,0.06]
dry_masses = [0.013, 0.023,0.042 ]
dt =0.01

def build_motor(df, mass_prop, mass_dry,name):
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
    
    return {'name': name, 'v_e': v_e, 'burn_time': burn_time, 'thrust': thrust, 'dm': dm}

motor_data = [ build_motor(df, mass_prop, mass_dry,name) for df,mass_prop, mass_dry, name in zip(motors, prop_masses, dry_masses, labels)]

if motor_sel == "C6": motor =motor_data[1]
elif motor_sel == "D12": motor =motor_data[2]
elif motor_sel == "F15": motor =motor_data[3]

#center of pressure and center of gravity location
def calc_CG(time):

    total_mass = 
    x_CG = #weighted avg
def calc_CP():


#drag force
def calc_CD(speed, t):
    if t > 

#normal force 

#wind force 

#rk4