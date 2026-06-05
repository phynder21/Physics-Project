import pandas as pd
import numpy as np
import math
from vpython import *

scene.align = "left"
scene.width  = 450
scene.height = 550
scene.background = color.white
scene.title  = "Rocket Simulator\n"
scene.range  = 0.4

g = 9.81
rho_air = 1.225
mu = 1.81e-5
dt = 0.01

wind_V = 3.0
wind_angle = 30
wind_VX = wind_V * math.cos(math.radians(wind_angle))
wind_VY = wind_V * math.sin(math.radians(wind_angle))

TABS = ["Nosecone", "Body Tube", "Fins", "Motor", "Parachute"]
DEFAULTS = dict(
    tab="Nosecone",
    nc_length=0.13,  nc_type="Parabolic",
    bt_length=0.40,  bt_diameter=0.056,
    fin_a=0.095, fin_b=0.060, fin_s=0.080, fin_n=4, fin_m=0.036,
    motor_type="C6", motor_delay=4.0,
    para_shroud=0.457, para_canopy=0.456,
)
state = dict(DEFAULTS)
mode = "design" #"design" "launch"
flight = {}              
height_lbl = None
time_lbl   = None

df_c6  = pd.read_csv('C6.csv')
df_d12 = pd.read_csv('D12.csv')
df_f15 = pd.read_csv('F15.csv')

_motors_raw    = [df_c6, df_d12, df_f15]
_motor_names   = ['C6', 'D12', 'F15']
_motor_lengths = [0.07, 0.07, 0.114]
_prop_masses   = [0.011, 0.021, 0.060]
_dry_masses    = [0.013, 0.023, 0.042]

def build_motor(df, mass_prop, mass_dry, name, motor_length):
    time_arr   = np.insert(df['Time'].to_numpy(),   0, 0.0)
    thrust_arr = np.insert(df['Thrust'].to_numpy(), 0, 0.0)
    impulse = np.trapezoid(thrust_arr, x=time_arr)
    v_e = round(impulse / mass_prop, 4)
    burn_time = time_arr[-1]
    dm_dt_arr = thrust_arr / v_e
    cum_lost = np.zeros_like(time_arr)
    for i in range(1, len(time_arr)):
        avg = (dm_dt_arr[i] + dm_dt_arr[i-1]) / 2
        cum_lost[i] = cum_lost[i-1] + avg * (time_arr[i] - time_arr[i-1])

    def thrust(t):
        if t < 0 or t > burn_time:
            return 0.0
        return float(np.interp(t, time_arr, thrust_arr))

    def dm(t):
        if t <= 0:
            return 0.0
        if t >= burn_time:
            return float(cum_lost[-1])
        return float(np.interp(t, time_arr, cum_lost))

    return {
        'name': name, 'v_e': v_e, 'burn_time': burn_time,
        'thrust': thrust, 'dm': dm,
        'mass': mass_dry + mass_prop, 'length': motor_length,
    }

_motor_data = [build_motor(d, mp, md, nm, ln)
               for d, mp, md, nm, ln in zip(_motors_raw, _prop_masses, _dry_masses,
                                            _motor_names, _motor_lengths)]
motors_by_name = {m['name']: m for m in _motor_data}

geom = {}

def compute_geom():
    BT_length = state["bt_length"]
    BT_dia    = state["bt_diameter"]
    BT_density   = 0.68 * 1000
    BT_thickness = 0.003
    BT_mass = math.pi * BT_dia * BT_length * BT_density * BT_thickness

    F_root = state["fin_a"]
    F_tip  = state["fin_b"]
    F_span = state["fin_s"]
    F_sweep = state["fin_m"]
    F_num  = state["fin_n"]
    F_density   = 1.25 * 1000
    F_thickness = 0.003
    F_mass = F_num * 0.5 * (F_root + F_tip) * F_span * F_thickness * F_density

    NC_shape  = state["nc_type"]
    NC_length = state["nc_length"]
    NC_density   = 1.25 * 1000
    NC_thickness = 0.003

    if NC_shape == "Conical":
        slant = math.sqrt(NC_length**2 + (BT_dia/2)**2)
        NC_area = math.pi * (BT_dia/2) * slant
    elif NC_shape == "Ogive":
        rho_o = ((BT_dia/2)**2 + NC_length**2) / (2 * BT_dia/2)
        NC_area = 2 * math.pi * rho_o * (rho_o - math.sqrt(rho_o**2 - (BT_dia/2)**2))
    else:  # Parabolic
        n = 500
        area = 0.0
        for i in range(1, n+1):
            x_prev = NC_length * (i-1)/n
            x      = NC_length *  i   /n
            x_mid  = (x + x_prev) / 2
            r_mid = BT_dia/2 * (1 - (x_mid/NC_length)**2)
            dydx  = -2 * BT_dia/2 * x_mid / NC_length**2
            area += 2 * math.pi * r_mid * math.sqrt(1 + dydx**2) * (x - x_prev)
        NC_area = area
    NC_mass = NC_area * NC_thickness * NC_density

    PC_diam = state["para_canopy"]
    PC_density = 0.06
    PC_mass = math.pi * (PC_diam/2)**2 * PC_density

    motor = motors_by_name[state["motor_type"]]

    geom.clear()
    geom.update(
        BT_length=BT_length, BT_dia=BT_dia, BT_mass=BT_mass,
        F_root=F_root, F_tip=F_tip, F_span=F_span, F_sweep=F_sweep,
        F_num=F_num, F_mass=F_mass,
        NC_shape=NC_shape, NC_length=NC_length, NC_mass=NC_mass,
        PC_mass=PC_mass, motor=motor,
        total_length=NC_length + BT_length,
        A_ref=math.pi * (BT_dia/2)**2,
    )

# super sim Calc fulls
def calc_CG(t):
    G = geom
    x_CG_tube  = G['NC_length'] + G['BT_length']/2
    x_CG_fins  = G['NC_length'] + G['BT_length'] - G['F_root'] + G['F_sweep']/2 + G['F_root']/2
    x_CG_motor = G['NC_length'] + G['BT_length'] - G['motor']['length']/2
    x_CG_NC    = (3/4) * G['NC_length']
    x_CG_PC    = G['NC_length']

    mass_motor = G['motor']['mass'] - G['motor']['dm'](t)
    total_mass = mass_motor + G['BT_mass'] + G['F_mass'] + G['NC_mass'] + G['PC_mass']
    x_CG = (x_CG_tube*G['BT_mass'] + x_CG_fins*G['F_mass']
            + x_CG_motor*mass_motor + x_CG_NC*G['NC_mass'] + x_CG_PC*G['PC_mass']) / total_mass
    return x_CG, total_mass, x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC

def calc_CP():
    G = geom
    if   G['NC_shape'] == "Ogive":     X_CP_NC = (2/3) * G['NC_length']
    elif G['NC_shape'] == "Parabolic": X_CP_NC = 0.466 * G['NC_length']
    else:                              X_CP_NC = 0.5   * G['NC_length']
    CN_NC = 2

    F_num = G['F_num']
    if F_num in (3, 4):
        K = 1 + (G['BT_dia']/2) / (G['F_span'] + G['BT_dia']/2)
    else:
        K = 1 + (G['BT_dia']/4) / (G['F_span'] + G['BT_dia']/2)
    l = math.sqrt(G['F_sweep']**2 + ((G['F_root']-G['F_tip'])/2 + G['F_sweep'])**2)
    C_N_finbefore = (4*F_num*(G['F_span']/G['BT_dia'])**2) / (1 + math.sqrt(1 + ((2*l)/(G['F_root']+G['F_tip']))**2))
    CN_F = K * C_N_finbefore
    X_CP_F = (G['NC_length'] + G['BT_length'] - G['F_root']
              + (G['F_sweep']*(G['F_root']+G['F_tip']))/(3*(G['F_root']+G['F_tip']))
              + (1/6)*(G['F_root']+G['F_tip'] - G['F_root']*G['F_tip']/(G['F_root']+G['F_tip'])))
    CN_total = CN_NC + CN_F
    X_CP = (CN_NC*X_CP_NC + CN_F*X_CP_F) / CN_total
    return X_CP, CN_total

def calc_CD(speed, t):
    G = geom
    Re = max(rho_air * speed * G['total_length'] / mu, 1e4)
    Cf = 0.074 / Re**0.2
    fin_base = 0.5 * (G['F_root'] + G['F_tip']) * G['F_span']
    A_wet = math.pi * G['BT_dia'] * G['total_length'] + 2 * G['F_num'] * fin_base
    fineness = G['total_length'] / G['BT_dia']
    CD_frict = Cf * (1 + 1/(2*fineness)) * (A_wet / G['A_ref'])
    half_angle = math.atan((G['BT_dia']/2) / G['NC_length'])
    if   G['NC_shape'] == "Ogive":     CD_nose = 0.7 * math.sin(half_angle)**2
    elif G['NC_shape'] == "Parabolic": CD_nose = 0.6 * math.sin(half_angle)**2
    else:                              CD_nose = 0.8 * math.sin(half_angle)**2
    CD_base = 0.12 if t < G['motor']['burn_time'] else 0.25
    t_fin = 0.002
    CD_interference = 0.04 * G['F_num'] * (t_fin / G['BT_dia'])
    return CD_frict + CD_nose + CD_base + CD_interference

def drag_force(vx, vy, speed, t):
    if speed < 0.01:
        return 0.0, 0.0
    CD = calc_CD(speed, t)
    F = 0.5 * rho_air * speed**2 * CD * geom['A_ref']
    return -F * (vx/speed), -F * (vy/speed)

def normal_force(vx, vy, theta):
    rocket_ax = math.sin(theta); rocket_ay = math.cos(theta)
    perp_x = math.cos(theta);    perp_y = -math.sin(theta)
    vfs_x = vx - wind_VX
    vfs_y = vy - wind_VY
    vfs_mag = math.sqrt(vfs_x**2 + vfs_y**2)
    if vfs_mag < 0.1:
        return 0.0, 0.0, 0.0
    vfs_along = vfs_x*rocket_ax + vfs_y*rocket_ay
    vfs_perp  = vfs_x*perp_x   + vfs_y*perp_y
    alpha = math.atan2(vfs_perp, vfs_along)
    alpha = max(-0.35, min(0.35, alpha))
    _, C_N_total = calc_CP()
    F_N_signed = -0.5 * rho_air * vfs_mag**2 * C_N_total * alpha * geom['A_ref']
    return F_N_signed * perp_x, F_N_signed * perp_y, F_N_signed

def calc_IN(t):
    G = geom
    x_CG, _, x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC = calc_CG(t)
    BT_I = G['BT_mass'] * (3*(G['BT_dia']/2)**2 + G['BT_length']**2)/12 + G['BT_mass']*(x_CG_tube-x_CG)**2
    NC_I = G['NC_mass'] * (3*(G['BT_dia']/2)**2/20 + G['NC_length']**2/10) + G['NC_mass']*(x_CG_NC-x_CG)**2
    F_I  = G['F_mass']  * (G['F_root']**2 + G['F_span']**2)/12 + G['F_mass']*(x_CG_fins-x_CG)**2
    motor_I = G['motor']['mass'] * ((G['BT_dia']/2)**2/4 + (G['motor']['length']**2)/12) \
              + G['motor']['mass']*(x_CG_motor-x_CG)**2
    return BT_I + NC_I + F_I + motor_I

def launch_accels(vx, vy, theta, t):
    speed = math.sqrt(vx**2 + vy**2)
    x_CG, total_mass, *_ = calc_CG(t)
    x_CP, _ = calc_CP()
    F_N_x, F_N_y, F_N_signed = normal_force(vx, vy, theta)
    F_drag_x, F_drag_y = drag_force(vx, vy, speed, t)
    thrust_mag = geom['motor']['thrust'](t)
    Thrust_x = thrust_mag * math.sin(theta)
    Thrust_y = thrust_mag * math.cos(theta)
    Fg_y = -total_mass * g
    ax = (Thrust_x + F_drag_x + F_N_x) / total_mass
    ay = (Thrust_y + F_drag_y + F_N_y + Fg_y) / total_mass
    torque = -F_N_signed * (x_CP - x_CG)
    a_roll = torque / calc_IN(t)
    return ax, ay, a_roll

def step_sim():
    if flight['done']:
        return
    t = flight['t'] + dt
    ax, ay, a_roll = launch_accels(flight['vx'], flight['vy'], flight['theta'], t)
    vx = flight['vx'] + ax*dt
    vy = flight['vy'] + ay*dt
    x  = flight['x']  + vx*dt
    y  = flight['y']  + vy*dt
    omega = flight['omega'] + a_roll*dt
    theta = flight['theta'] + omega*dt

    if not flight['launched']:
        if y <= 0:
            flight.update(t=t, x=0.0, y=0.0, vx=0.0, vy=0.0, theta=0.0, omega=0.0)
            return
        flight['launched'] = True

    if y <= 0:
        flight['done'] = True
        return

    flight.update(t=t, x=x, y=y, vx=vx, vy=vy, theta=theta, omega=omega)
    if y > flight['apogee']:
        flight['apogee'] = y

def on_tab_click(b):
    state["tab"] = b.tab_name
    draw_ui()

def on_slider_change(s):
    state[s.key_name] = s.value

def on_option_click(b):
    state[b.key_name] = b.opt_value
    draw_ui()

def on_launch():
    global mode
    compute_geom()
    flight.clear()
    flight.update(t=0.0, x=0.0, y=0.0, vx=0.0, vy=0.0,
                  theta=0.0, omega=0.0, apogee=0.0,
                  launched=False, done=False)
    mode = "launch"
    draw_ui()

def on_reset():
    global mode
    state.update(DEFAULTS)
    mode = "design"
    draw_ui()

def draw_ui():
    global height_lbl, time_lbl
    scene.caption = ""
    scene.append_to_caption("<div style='margin-left: 30px; display: inline-block; vertical-align: top; font-family: sans-serif;'>")

    if mode == "launch":
        scene.append_to_caption("<div><h2 style='margin: 0;'>Flight</h2></div><br>")
        height_lbl = wtext(text="Height: 0.000 m\n")
        scene.append_to_caption("\n")
        time_lbl   = wtext(text="Time:   0.000 s\n")
        scene.append_to_caption("\n\n")
        scene.append_to_caption("<hr style='margin: 15px 0;'>")
        b = button(text="Back to design", bind=on_reset)
        scene.append_to_caption("</div>")
        return

    scene.append_to_caption("<div><h2 style='margin: 0;'>Design Workbench</h2></div><br>")
    for i in TABS:
        lbl = " * " + i + " * " if state["tab"] == i else "   " + i + "   "
        b = button(text=lbl, bind=on_tab_click)
        b.tab_name = i
    scene.append_to_caption("<hr style='margin: 15px 0;'>")

    active = state["tab"]

    if active == "Nosecone":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min=0.05, max=0.3, value=state["nc_length"], bind=on_slider_change)
        s.key_name = "nc_length"
        wtext(text='  {:.3f} m'.format(state["nc_length"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Type</b>  ")
        for opt in ["Parabolic", "Ogive", "Conical"]:
            lbl = " [" + opt + "] " if state["nc_type"] == opt else "  " + opt + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "nc_type"
            b.opt_value = opt
        scene.append_to_caption("\n")

    elif active == "Body Tube":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min=0.1, max=1.0, value=state["bt_length"], bind=on_slider_change)
        s.key_name = "bt_length"
        wtext(text='  {:.3f} m'.format(state["bt_length"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Diameter</b>  ")
        s = slider(min=0.02, max=0.15, value=state["bt_diameter"], bind=on_slider_change)
        s.key_name = "bt_diameter"
        wtext(text='  {:.3f} m'.format(state["bt_diameter"]))
        scene.append_to_caption("\n")

    elif active == "Fins":
        a = state["fin_a"]
        b_max = max(0.006, a - state["fin_m"] - 0.005)
        m_max = max(0.001, a - state["fin_b"] - 0.005)
        state["fin_b"] = min(state["fin_b"], b_max)
        state["fin_m"] = min(state["fin_m"], m_max)

        scene.append_to_caption("  <b>a (root chord)</b>  ")
        s = slider(min=0.03, max=0.20, value=state["fin_a"], bind=on_slider_change)
        s.key_name = "fin_a"
        wtext(text='  {:.3f} m'.format(state["fin_a"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>b (tip chord)</b>  ")
        s = slider(min=0.005, max=b_max, value=state["fin_b"], bind=on_slider_change)
        s.key_name = "fin_b"
        wtext(text='  {:.3f} m'.format(state["fin_b"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>s (semi-span)</b>  ")
        s = slider(min=0.01, max=0.15, value=state["fin_s"], bind=on_slider_change)
        s.key_name = "fin_s"
        wtext(text='  {:.3f} m'.format(state["fin_s"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>m (sweep offset)</b>  ")
        s = slider(min=0.0, max=m_max, value=state["fin_m"], bind=on_slider_change)
        s.key_name = "fin_m"
        wtext(text='  {:.3f} m'.format(state["fin_m"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>Number of Fins</b>  ")
        for opt in [3, 4, 6]:
            lbl = " [" + str(opt) + "] " if state["fin_n"] == opt else "  " + str(opt) + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "fin_n"
            b.opt_value = opt
        scene.append_to_caption("\n")

    elif active == "Motor":
        scene.append_to_caption("  <b>Motor type</b>  ")
        for opt in ["C6", "D12", "F15"]:
            lbl = " [" + opt + "] " if state["motor_type"] == opt else "  " + opt + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "motor_type"
            b.opt_value = opt
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Delay Charge</b>  ")
        s = slider(min=0, max=15, value=state["motor_delay"], bind=on_slider_change)
        s.key_name = "motor_delay"
        scene.append_to_caption("\n")

    elif active == "Parachute":
        scene.append_to_caption("  <b>Shroud line length</b>  ")
        s1 = slider(min=0.1, max=1.0, value=state["para_shroud"], bind=on_slider_change)
        s1.key_name = "para_shroud"
        wtext(text='  {:.3f} m'.format(state["para_shroud"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Canopy diameter</b>  ")
        s2 = slider(min=0.1, max=1.0, value=state["para_canopy"], bind=on_slider_change)
        s2.key_name = "para_canopy"
        wtext(text='  {:.3f} m'.format(state["para_canopy"]))
        scene.append_to_caption("\n")

    scene.append_to_caption("<hr style='margin: 15px 0;'>")
    button(text="Launch!", bind=on_launch)
    scene.append_to_caption("   ")
    button(text="Reset", bind=on_reset)
    scene.append_to_caption("</div>")

def makeRect(L, H):
    return [
        vector(-L/2, -H/2, 0),
        vector( L/2, -H/2, 0),
        vector( L/2,  H/2, 0),
        vector(-L/2,  H/2, 0),
        vector(-L/2, -H/2, 0),
    ]

def MakeNosecone(length, diameter):
    points = []
    r = diameter/2
    steps = 50
    bt_top = state["bt_length"] / 2
    nc_type = state["nc_type"]
    for i in range(steps+1):
        tt = i/steps
        y = bt_top + tt * length
        if   nc_type == "Parabolic": x = r * (1 - tt**2)
        elif nc_type == "Ogive":     x = r * math.sqrt(max(0.0, 1 - tt**2))
        else:                        x = r * (1 - tt)
        points.append(vector(x, y, 0))
    for i in range(steps, -1, -1):
        tt = i/steps
        y = bt_top + tt * length
        if   nc_type == "Parabolic": x = r * (1 - tt**2)
        elif nc_type == "Ogive":     x = r * math.sqrt(max(0.0, 1 - tt**2))
        else:                        x = r * (1 - tt)
        points.append(vector(-x, y, 0))
    return points

def makeFin(side=+1):
    a = state["fin_a"]; b = state["fin_b"]; s = state["fin_s"]; m = state["fin_m"]
    bt_bottom = -state["bt_length"] / 2
    r = state["bt_diameter"] / 2 * side
    sgn = 1 if side > 0 else -1
    p1 = vector(r,             bt_bottom,             0)
    p2 = vector(r,             bt_bottom + a,         0)
    p3 = vector(r + sgn*s,     bt_bottom + a - m,     0)
    p4 = vector(r + sgn*s,     bt_bottom + a - m - b, 0)
    return [p1, p2, p3, p4, p1]

def rotate_about(pt, pivot, theta_cw):
    """2D rotate `pt` clockwise (positive angle = clockwise as viewed) about `pivot`."""
    dx = pt.x - pivot.x
    dy = pt.y - pivot.y
    c = math.cos(theta_cw); s = math.sin(theta_cw)
    return vector(pivot.x + dx*c + dy*s, pivot.y - dx*s + dy*c, pt.z)

def cg_visual_y(x_CG):
    """Map axial distance-from-nose-tip into the design visual's y."""
    nose_y = state["bt_length"]/2 + state["nc_length"]
    return nose_y - x_CG

body_curve   = curve(color=color.black)
nose_curve   = curve(color=color.black)
fin_curve_l  = curve(color=color.black)
fin_curve_r  = curve(color=color.black)

cg_marker = sphere(pos=vector(0,0,0), radius=0.008, color=color.red,  visible=False)
cp_marker = sphere(pos=vector(0,0,0), radius=0.008, color=color.blue, visible=False)
cg_label  = label(pos=vector(0,0,0), text="CG", color=color.red,  box=False, opacity=0, height=10, visible=False)
cp_label  = label(pos=vector(0,0,0), text="CP", color=color.blue, box=False, opacity=0, height=10, visible=False)

def redraw_design():
    body_curve.clear()
    for p in makeRect(state["bt_diameter"], state["bt_length"]):
        body_curve.append(p)
    nose_curve.clear()
    for p in MakeNosecone(state["nc_length"], state["bt_diameter"]):
        nose_curve.append(p)
    fin_curve_l.clear()
    for p in makeFin(+1):
        fin_curve_l.append(p)
    fin_curve_r.clear()
    for p in makeFin(-1):
        fin_curve_r.append(p)

    compute_geom()
    x_CG, _, *_ = calc_CG(0.0)
    x_CP, _    = calc_CP()
    cg_y = cg_visual_y(x_CG)
    cp_y = cg_visual_y(x_CP)
    r = state["bt_diameter"] / 2
    marker_r = max(0.004, state["bt_diameter"] * 0.12)
    cg_marker.radius = marker_r
    cp_marker.radius = marker_r
    cg_marker.pos = vector(0, cg_y, 0)
    cp_marker.pos = vector(0, cp_y, 0)
    cg_label.pos  = vector(r + 0.03, cg_y, 0)
    cp_label.pos  = vector(r + 0.03, cp_y, 0)
    cg_marker.visible = True; cg_label.visible = True
    cp_marker.visible = True; cp_label.visible = True

def redraw_launch():
    #can change to false but i lowkey like it
    cg_marker.visible = True; cg_label.visible = True
    cp_marker.visible = True; cp_label.visible = True

    x_CG, _, *_ = calc_CG(flight['t'])
    pivot = vector(0, cg_visual_y(x_CG), 0)
    th = flight['theta']

    body_curve.clear()
    for p in makeRect(state["bt_diameter"], state["bt_length"]):
        body_curve.append(rotate_about(p, pivot, th))
    nose_curve.clear()
    for p in MakeNosecone(state["nc_length"], state["bt_diameter"]):
        nose_curve.append(rotate_about(p, pivot, th))
    fin_curve_l.clear()
    for p in makeFin(+1):
        fin_curve_l.append(rotate_about(p, pivot, th))
    fin_curve_r.clear()
    for p in makeFin(-1):
        fin_curve_r.append(rotate_about(p, pivot, th))

    x_CP, _ = calc_CP()
    cp_unrot = vector(0, cg_visual_y(x_CP), 0)
    cp_pos = rotate_about(cp_unrot, pivot, th)
    cg_marker.pos = pivot
    cp_marker.pos = cp_pos
    r = state["bt_diameter"] / 2
    cg_label.pos = vector(pivot.x + r + 0.03, pivot.y, 0)
    cp_label.pos = vector(cp_pos.x + r + 0.03, cp_pos.y, 0)

draw_ui()
redraw_design()

steps_per_frame = 4   

while True:
    rate(25)
    if mode == "design":
        redraw_design()
    else:
        for _ in range(steps_per_frame):
            step_sim()
            if flight['done']:
                break
        redraw_launch()
        if height_lbl is not None:
            height_lbl.text = "Height: {:.3f} m  (apogee {:.3f} m)\n".format(flight['y'], flight['apogee'])
        if time_lbl is not None:
            time_lbl.text   = "Time:   {:.3f} s\n".format(flight['t'])
