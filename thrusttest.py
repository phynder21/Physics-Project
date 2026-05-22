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
masses = [0.011,0.021,0.06]
v_es =[]

for thrust_curve in motors: 
    count =0
    x_arr = thrust_curve['Time'].to_numpy()
    y_arr = thrust_curve['Thrust'].to_numpy()
    x_arr = np.insert(x_arr, 0, 0.0)
    y_arr = np.insert(y_arr, 0, 0.0)


    impulse = np.trapezoid(y_arr, x = x_arr)
    v_e = impulse/masses[count]
    v_e = round(v_e, 4)
    v_es.append(v_e)
    count += 1

dm = 

print(v_es)


