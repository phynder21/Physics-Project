import pandas as pd
import numpy as np
from vpython import *

t= 0.00
dt =0.01
m_first = 0.1 #start here change later when we calculate mass
dm =0

df_c6 = pd.read_csv('C6.csv')
df_d12 = pd.read_csv('D12.csv')
df_f15 = pd.read_csv('F15.csv')

motors = [df_c6, df_d12, df_f15]
labels = ['C6', 'D12', 'F15']
prop_masses = [0.011,0.021,0.06]
dry_masses = [0.013, 0.023,0.042 ]
dt =0.01

def build_motor(df, mass_prop, mass_dry,name):
    time_arr = np.insert(thrust_curve['Time'].to_numpy(), 0, 0.0)
    Thrust_arr = np.insert(thrust_curve['Thrust'].to_numpy(), 0,0.0)

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
    def mass(time):
        if time <= 0:
            return mass_dry +mass_prop
        elif time >= burn_time:
            return mass_dry
        else:
            burnt = float(np.interp(time, time_arr, cumalative_mass_lost))
            return mass_dry + mass_prop - burnt
    
    return {'name': name, 'v_e': v_e, 'burn_time': burn_time, 'thrust': thrust, 'mass': mass}

motor_date = [ build_motor(df, mass_prop, mass_dry,name) for df,mass_prop, mass_dry, name in zip(motors, prop_masses, dry_masses, labels)]
# v_es =[]
# Thrust_dict = {}
# count =0
# for thrust_curve in motors: 
 

#     impulse = np.trapezoid(y_arr, x = x_arr)
#     v_e = impulse/masses[count]
#     v_e = round(v_e, 4)
#     v_es.append(v_e)
#     def Thurst(time,):
#         #ill come back to this
#     count += 1

# print(v_es)


