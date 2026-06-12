Web VPython 3.2
scene.userzoom = False


c6_time   = [0.0, 0.014, 0.026, 0.067, 0.099, 0.15, 0.183, 0.207, 0.219, 0.262,
             0.333, 0.349, 0.392, 0.475, 0.653, 0.913, 1.366, 1.607, 1.745, 1.978,
             2.023, 2.024]
c6_thrust = [0.0, 0.633, 1.533, 2.726, 5.136, 9.103, 11.465, 11.635, 11.391, 6.377,
             5.014, 5.209, 4.722, 4.771, 4.746, 4.673, 4.625, 4.625, 4.868, 4.795,
             0.828, 0.0]

d12_time   = [0.0, 0.049, 0.116, 0.184, 0.237, 0.282, 0.297, 0.311, 0.322, 0.348,
              0.386, 0.442, 0.546, 0.718, 0.879, 1.066, 1.257, 1.436, 1.59, 1.612,
              1.65]
d12_thrust = [0.0, 2.569, 9.369, 17.275, 24.258, 29.73, 27.01, 22.589, 17.99, 14.126,
              12.099, 10.808, 9.876, 9.306, 9.105, 8.901, 8.698, 8.31, 8.294, 4.613,
              0.0]

f15_time   = [0.0, 0.148, 0.228, 0.294, 0.353, 0.382, 0.419, 0.477, 0.52, 0.593,
              0.688, 0.855, 1.037, 1.205, 1.423, 1.452, 1.503, 1.736, 1.955, 2.21,
              2.494, 2.763, 3.12, 3.382, 3.404, 3.418, 3.45]
f15_thrust = [0.0, 7.638, 12.253, 16.391, 20.21, 22.756, 25.26, 23.074, 20.845, 19.093,
              17.5, 16.225, 15.427, 14.948, 14.627, 15.741, 14.785, 14.623, 14.303, 14.141,
              13.819, 13.338, 13.334, 13.013, 9.352, 4.895, 0.0]

def interp(x, xs, ys):
    n = xs.length
    if x <= xs[0]:     return ys[0]
    if x >= xs[n - 1]: return ys[n - 1]
    for i in range(n - 1):
        if xs[i] <= x <= xs[i+1]:
            t = (x - xs[i]) / (xs[i+1] - xs[i])
            return ys[i] + t * (ys[i+1] - ys[i])
    return ys[n - 1]

def trapz(ys, xs):
    total = 0.0
    n = xs.length
    for i in range(1, n):
        total += (ys[i] + ys[i-1]) / 2.0 * (xs[i] - xs[i-1])
    return total

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

TABS = ["Nosecone", "Body Tube", "Fins", "Motor", "Parachute", "Wind", "Graphs"]
GRAPH_VARS = ["Flight time", "Height", "Vertical velocity",
              "Total velocity", "Pitch", "Pitch angular velocity"]
DEFAULTS = dict(
    tab="Nosecone",
    nc_length=0.13,  nc_type="Parabolic",
    bt_length=0.40,  bt_diameter=0.056,
    fin_a=0.095, fin_b=0.060, fin_s=0.080, fin_n=4, fin_m=0.030,
    motor_type="C6", motor_delay=4.0,
    para_shroud=0.457, para_canopy=0.456,
    wind_angle = 30, wind_mag = 3.0,
    g1_x="Flight time", g1_y="Height",
    g2_x="Flight time", g2_y="Total velocity",
    g3_x="Flight time", g3_y="Pitch",
    g4_x="Height",      g4_y="Vertical velocity",
)
state = dict(DEFAULTS)
slider_labels = {}
mode = "design"
flight = {}
height_lbl = None
time_lbl   = None
metric_lbl = None

def build_motor(time_arr, thrust_arr, mass_prop, mass_dry, name, motor_length):
    impulse = trapz(thrust_arr, time_arr)
    v_e = round(impulse / mass_prop, 4)
    n_arr = time_arr.length
    burn_time = time_arr[n_arr - 1]

    dm_dt_arr = []
    for _i in range(n_arr):
        dm_dt_arr.append(thrust_arr[_i] / v_e)

    cum_lost = []
    for _k in range(n_arr):
        cum_lost.append(0.0)
    for i in range(1, n_arr):
        avg = (dm_dt_arr[i] + dm_dt_arr[i-1]) / 2.0
        cum_lost[i] = cum_lost[i-1] + avg * (time_arr[i] - time_arr[i-1])

    return {
        'name': name, 'v_e': v_e, 'burn_time': burn_time,
        'time_arr': time_arr, 'thrust_arr': thrust_arr, 'cum_lost': cum_lost,
        'mass': mass_dry + mass_prop, 'length': motor_length,
    }

def motor_thrust(motor, t):
    if t < 0 or t > motor['burn_time']: return 0.0
    return interp(t, motor['time_arr'], motor['thrust_arr'])

def motor_dm(motor, t):
    cl = motor['cum_lost']
    n = cl.length
    if t <= 0:                  return 0.0
    if t >= motor['burn_time']: return cl[n - 1]
    return interp(t, motor['time_arr'], cl)

motors_by_name = {}
motors_by_name['C6']  = build_motor(c6_time,  c6_thrust,  0.011, 0.013, 'C6',  0.07)
motors_by_name['D12'] = build_motor(d12_time, d12_thrust, 0.021, 0.023, 'D12', 0.07)
motors_by_name['F15'] = build_motor(f15_time, f15_thrust, 0.060, 0.042, 'F15', 0.114)

motor_descriptions = {
    'C6':  "\t A C class motor has a total Impulse between <b> 5 and 10 Newton Seconds </b> \n \n \t The average thrust number of 6 implies it outputs an average of <b> 6 Newtons of thrust </b>\n \n \t Typically, a rocket launched on this motor should be between <b> 113 and 142 grams </b> \n \n \t Note that the delay charge is the amount of seconds after main fuel burnout that the ejection charge ejects the parachute",
    'D12': "\t A D class motor has a total Impulse between <b> 10 and 20 Newton Seconds </b> \n \n \t The average thrust number of 12 implies it outputs an average of <b>12 Newtons of thrust </b>\n \n \t Typically, a rocket launched on this motor should be between <b> 150 and 450 grams </b> \n \n \t Note that the delay charge is the amount of seconds after main fuel burnout that the ejection charge ejects the parachute",
    'F15': "\t A F class motor has a total Impulse between <b>40 and 80 Newton Seconds </b> \n \n \t The average thrust number of 15 implies it outputs an average of <b>15 Newtons of thrust </b>\n \n \t Typically, a rocket launched on this motor should be between <b> 800 and 1500 grams </b> \n \n \t Note that the delay charge is the amount of seconds after main fuel burnout that the ejection charge ejects the parachute",
}

def build_thrust_svg(motor_name):
    m = motors_by_name[motor_name]
    time_arr   = m['time_arr']
    thrust_arr = m['thrust_arr']
    w = 200; h = 130
    pad_l = 30; pad_r = 10; pad_t = 12; pad_b = 26
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    n = time_arr.length
    t_max = time_arr[n-1]
    th_max = 0.0
    for v in thrust_arr:
        if v > th_max: th_max = v
    if t_max  <= 0: t_max  = 1.0
    if th_max <= 0: th_max = 1.0

    x0 = pad_l
    y0 = pad_t + plot_h
    x1 = pad_l + plot_w

    pts = ""
    for i in range(n):
        x = pad_l + (time_arr[i]/t_max) * plot_w
        y = pad_t + plot_h - (thrust_arr[i]/th_max) * plot_h
        pts += "{:.1f},{:.1f} ".format(x, y)

    svg  = "<svg width='{}' height='{}' xmlns='http://www.w3.org/2000/svg' style='background:#fff;'>".format(w, h)
    svg += "<line x1='{:.1f}' y1='{:.1f}' x2='{:.1f}' y2='{:.1f}' stroke='#000' stroke-width='1'/>".format(x0, pad_t, x0, y0)
    svg += "<line x1='{:.1f}' y1='{:.1f}' x2='{:.1f}' y2='{:.1f}' stroke='#000' stroke-width='1'/>".format(x0, y0, x1, y0)
    svg += "<polyline points='{}' fill='none' stroke='#c00' stroke-width='1.5'/>".format(pts)
    svg += "<text x='{:.1f}' y='{:.1f}' font-size='8' text-anchor='end'>{:.0f}</text>".format(x0-3, pad_t+4, th_max)
    svg += "<text x='{:.1f}' y='{:.1f}' font-size='8' text-anchor='end'>0</text>".format(x0-3, y0)
    svg += "<text x='{:.1f}' y='{:.1f}' font-size='8' text-anchor='middle'>{:.1f}</text>".format(x1, y0+11, t_max)
    svg += "<text x='{:.1f}' y='{:.1f}' font-size='9' text-anchor='middle'>Time (s)</text>".format((x0+x1)/2, h-4)
    svg += "<text x='8' y='{:.1f}' font-size='9' text-anchor='middle' transform='rotate(-90 8 {:.1f})'>Thrust (N)</text>".format((pad_t+y0)/2, (pad_t+y0)/2)
    svg += "</svg>"
    return svg

geom = {}

def compute_geom():
    BT_length = state["bt_length"]
    BT_dia    = state["bt_diameter"]
    BT_density   = 0.68 * 1000
    BT_thickness = 0.003
    BT_mass = pi * BT_dia * BT_length * BT_density * BT_thickness

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
        slant = sqrt(NC_length**2 + (BT_dia/2)**2)
        NC_area = pi * (BT_dia/2) * slant
    elif NC_shape == "Ogive":
        rho_o = ((BT_dia/2)**2 + NC_length**2) / (2 * BT_dia/2)
        NC_area = 2 * pi * rho_o * (rho_o - sqrt(rho_o**2 - (BT_dia/2)**2))
    else:
        n = 500
        area = 0.0
        for i in range(1, n+1):
            x_prev = NC_length * (i-1)/n
            x      = NC_length *  i   /n
            x_mid  = (x + x_prev) / 2
            r_mid = BT_dia/2 * (1 - (x_mid/NC_length)**2)
            dydx  = -2 * BT_dia/2 * x_mid / NC_length**2
            area += 2 * pi * r_mid * sqrt(1 + dydx**2) * (x - x_prev)
        NC_area = area
    NC_mass = NC_area * NC_thickness * NC_density

    PC_diam = state["para_canopy"]
    PC_density = 0.06
    PC_mass = pi * (PC_diam/2)**2 * PC_density

    motor = motors_by_name[state["motor_type"]]

    geom.clear()
    geom.update(
        BT_length=BT_length, BT_dia=BT_dia, BT_mass=BT_mass,
        F_root=F_root, F_tip=F_tip, F_span=F_span, F_sweep=F_sweep,
        F_num=F_num, F_mass=F_mass,
        NC_shape=NC_shape, NC_length=NC_length, NC_mass=NC_mass,
        PC_mass=PC_mass, motor=motor,
        total_length=NC_length + BT_length,
        A_ref=pi * (BT_dia/2)**2,
    )

def calc_CG(t):
    G = geom
    x_CG_tube  = G['NC_length'] + G['BT_length']/2
    x_CG_fins  = G['NC_length'] + G['BT_length'] - G['F_root'] + G['F_sweep']/2 + G['F_root']/2
    x_CG_motor = G['NC_length'] + G['BT_length'] - G['motor']['length']/2
    x_CG_NC    = (3/4) * G['NC_length']
    x_CG_PC    = G['NC_length']

    mass_motor = G['motor']['mass'] - motor_dm(G['motor'], t)
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
    if F_num == 3 or F_num == 4:
        K = 1 + (G['BT_dia']/2) / (G['F_span'] + G['BT_dia']/2)
    else:
        K = 1 + (G['BT_dia']/4) / (G['F_span'] + G['BT_dia']/2)
    l = sqrt(G['F_sweep']**2 + ((G['F_root']-G['F_tip'])/2 + G['F_sweep'])**2)
    C_N_finbefore = (4*F_num*(G['F_span']/G['BT_dia'])**2) / (1 + sqrt(1 + ((2*l)/(G['F_root']+G['F_tip']))**2))
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
    A_wet = pi * G['BT_dia'] * G['total_length'] + 2 * G['F_num'] * fin_base
    fineness = G['total_length'] / G['BT_dia']
    CD_frict = Cf * (1 + 1/(2*fineness)) * (A_wet / G['A_ref'])
    half_angle = atan((G['BT_dia']/2) / G['NC_length'])
    if   G['NC_shape'] == "Ogive":     CD_nose = 0.7 * sin(half_angle)**2
    elif G['NC_shape'] == "Parabolic": CD_nose = 0.6 * sin(half_angle)**2
    else:                              CD_nose = 0.8 * sin(half_angle)**2
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
    rocket_ax = sin(theta); rocket_ay = cos(theta)
    perp_x = cos(theta);    perp_y = -sin(theta)
    wind_V = state['wind_mag']
    wind_angle = state['wind_angle']
    wind_VX = wind_V * cos(radians(wind_angle))
    wind_VY = wind_V * sin(radians(wind_angle))
    vfs_x = vx - wind_VX
    vfs_y = vy - wind_VY
    vfs_mag = sqrt(vfs_x**2 + vfs_y**2)
    if vfs_mag < 0.1:
        return 0.0, 0.0, 0.0
    vfs_along = vfs_x*rocket_ax + vfs_y*rocket_ay
    vfs_perp  = vfs_x*perp_x   + vfs_y*perp_y
    alpha = atan2(vfs_perp, vfs_along)
    alpha = max(-0.35, min(0.35, alpha))
    _, C_N_total = calc_CP()
    F_N_signed = -0.5 * rho_air * vfs_mag**2 * C_N_total * alpha * geom['A_ref']
    return F_N_signed * perp_x, F_N_signed * perp_y, F_N_signed

def calc_IN(t):
    G = geom
    x_CG, _a, x_CG_tube, x_CG_fins, x_CG_motor, x_CG_NC = calc_CG(t)
    BT_I = G['BT_mass'] * (3*(G['BT_dia']/2)**2 + G['BT_length']**2)/12 + G['BT_mass']*(x_CG_tube-x_CG)**2
    NC_I = G['NC_mass'] * (3*(G['BT_dia']/2)**2/20 + G['NC_length']**2/10) + G['NC_mass']*(x_CG_NC-x_CG)**2
    F_I  = G['F_mass']  * (G['F_root']**2 + G['F_span']**2)/12 + G['F_mass']*(x_CG_fins-x_CG)**2
    motor_I = G['motor']['mass'] * ((G['BT_dia']/2)**2/4 + (G['motor']['length']**2)/12) \
              + G['motor']['mass']*(x_CG_motor-x_CG)**2
    return BT_I + NC_I + F_I + motor_I

PARA_CD = 1.5

def launch_accels(vx, vy, theta, t):
    speed = sqrt(vx**2 + vy**2)
    x_CG, total_mass, _a, _b, _c, _d = calc_CG(t)
    F_drag_x, F_drag_y = drag_force(vx, vy, speed, t)
    thrust_mag = motor_thrust(geom['motor'], t)
    Thrust_x = thrust_mag * sin(theta)
    Thrust_y = thrust_mag * cos(theta)
    Fg_y = -total_mass * g

    if flight['chute']:
        A_chute = pi * (state['para_canopy']/2)**2
        if speed > 0.01:
            F_p  = 0.5 * rho_air * speed**2 * PARA_CD * A_chute
            F_p  = min(F_p, 0.9 * total_mass * speed / dt)
            Fp_x = -F_p * (vx/speed)
            Fp_y = -F_p * (vy/speed)
        else:
            Fp_x = 0.0; Fp_y = 0.0
        ax = (Thrust_x + F_drag_x + Fp_x) / total_mass
        ay = (Thrust_y + F_drag_y + Fp_y + Fg_y) / total_mass
        a_roll = -18.0 * theta - 9.0 * flight['omega']
        return ax, ay, a_roll

    x_CP, _e = calc_CP()
    F_N_x, F_N_y, F_N_signed = normal_force(vx, vy, theta)
    ax = (Thrust_x + F_drag_x + F_N_x) / total_mass
    ay = (Thrust_y + F_drag_y + F_N_y + Fg_y) / total_mass
    torque = -F_N_signed * (x_CP - x_CG)
    a_roll = torque / calc_IN(t)
    return ax, ay, a_roll

def step_sim():
    if flight['done']:
        return
    t = flight['t'] + dt
    if not flight['chute'] and flight['launched']:
        if t >= geom['motor']['burn_time'] + state['motor_delay']:
            flight['chute'] = True
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

def recommend_delay():
    compute_geom()
    motor = geom['motor']
    t = 0.0; vy = 0.0; y = 0.0
    launched = False
    guard = 0
    while guard < 30000:
        guard += 1
        thrust = motor_thrust(motor, t)
        _x, total_mass, _a, _b, _c, _d = calc_CG(t)
        Fd_y = 0.0
        if abs(vy) > 0.01:
            Fd = 0.5 * rho_air * vy**2 * calc_CD(abs(vy), t) * geom['A_ref']
            Fd_y = -Fd * (vy/abs(vy))
        ay = (thrust + Fd_y - total_mass*g) / total_mass
        vy += ay*dt
        y  += vy*dt
        t  += dt
        if not launched:
            if y > 0:
                launched = True
            else:
                y = 0.0; vy = 0.0
        elif vy <= 0:
            break
    delay = t - motor['burn_time']
    return max(0.0, delay)

def on_tab_click(b):
    state["tab"] = b.tab_name
    draw_ui()

def on_slider_change(s):
    state[s.key_name] = s.value
    if s.key_name in slider_labels:
        lbl = slider_labels[s.key_name]
        val = state[s.key_name]
        if s.key_name in ("nc_length","bt_length","bt_diameter","fin_a","fin_b","fin_s","fin_m","para_shroud","para_canopy"):
            lbl.text = '  {:.3f} m'.format(val)
        elif s.key_name == "motor_delay":
            lbl.text = '  {:.1f} s'.format(val)
        elif s.key_name == "wind_mag":
            lbl.text = '  {:.3f} m/s'.format(val)
        elif s.key_name == "wind_angle":
            lbl.text = '  {:.3f} deg'.format(val)

def on_option_click(b):
    state[b.key_name] = b.opt_value
    draw_ui()

def on_menu_change(m):
    state[m.key_name] = m.selected

def on_launch(b):
    global mode
    compute_geom()
    flight.clear()
    flight.update(t=0.0, x=0.0, y=0.0, vx=0.0, vy=0.0,
                  theta=0.0, omega=0.0, apogee=0.0,
                  launched=False, done=False, chute=False)
    scene.range = 0.4
    mode = "launch"
    draw_ui()
    make_flight_graphs()

def on_back_to_design(b):
    global mode
    mode = "design"
    scene.range = 0.4
    clear_flight_graphs()
    draw_ui()

def on_skip_to_end(b):
    guard = 0
    while not flight['done'] and guard < 200000:
        guard += 1
        step_sim()
        update_graphs()
    redraw_launch()
    update_background()
    if height_lbl is not None:
        height_lbl.text = "Height: {:.3f} m  (apogee {:.3f} m)\n".format(flight['y'], flight['apogee'])
    if time_lbl is not None:
        time_lbl.text   = "Time:   {:.3f} s\n".format(flight['t'])

def on_reset(b):
    global mode
    state.update(DEFAULTS)
    mode = "design"
    scene.range = 0.4
    randomize_background()
    clear_flight_graphs()
    draw_ui()

def draw_ui():
    global height_lbl, time_lbl, metric_lbl
    scene.caption = ""
    scene.append_to_caption("<div style='margin-left: 30px; display: inline-block; vertical-align: top; font-family: sans-serif;'>")

    if mode == "launch":
        scene.append_to_caption("<div><h2 style='margin: 0;'>Flight</h2></div><br>")
        height_lbl = wtext(text="Height: 0.000 m\n")
        scene.append_to_caption("\n")
        time_lbl   = wtext(text="Time:   0.000 s\n")
        scene.append_to_caption("\n\n")
        scene.append_to_caption("<hr style='margin: 15px 0;'>")
        b = button(text="Skip to end", bind=on_skip_to_end)
        scene.append_to_caption("   ")
        b = button(text="Back to design", bind=on_back_to_design)
        scene.append_to_caption("</div>")
        return

    scene.append_to_caption("<div><h2 style='margin: 0;'>Design Workbench</h2></div><br>")
    for i in TABS:
        b = button(text="  " + i + "  ", bind=on_tab_click)
        b.tab_name = i
        if state["tab"] == i:
            b.background = color.gray(0.4)
            b.color = color.white
        else:
            b.background = color.white
            b.color = color.black
    scene.append_to_caption("<hr style='margin: 15px 0;'>")

    active = state["tab"]

    if active == "Nosecone":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min=0.05, max=0.3, value=state["nc_length"], bind=on_slider_change)
        s.key_name = "nc_length"
        slider_labels["nc_length"] = wtext(text='  {:.3f} m'.format(state["nc_length"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Type</b>  ")
        for opt in ["Parabolic", "Ogive", "Conical"]:
            b = button(text="  " + opt + "  ", bind=on_option_click)
            b.key_name = "nc_type"
            b.opt_value = opt
            if state["nc_type"] == opt:
                b.background = color.gray(0.4)
                b.color = color.white
            else:
                b.background = color.white
                b.color = color.black
        scene.append_to_caption("\n")

    elif active == "Body Tube":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min=0.1, max=1.0, value=state["bt_length"], bind=on_slider_change)
        s.key_name = "bt_length"
        slider_labels["bt_length"] = wtext(text='  {:.3f} m'.format(state["bt_length"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Diameter</b>  ")
        s = slider(min=0.02, max=0.15, value=state["bt_diameter"], bind=on_slider_change)
        s.key_name = "bt_diameter"
        slider_labels["bt_diameter"] = wtext(text='  {:.3f} m'.format(state["bt_diameter"]))
        scene.append_to_caption("\n")

    elif active == "Fins":
        scene.append_to_caption("  <b>root chord</b>  ")
        s = slider(min=0.03, max=0.20, value=state["fin_a"], bind=on_slider_change)
        s.key_name = "fin_a"
        slider_labels["fin_a"] = wtext(text='  {:.3f} m'.format(state["fin_a"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>tip chord</b>  ")
        s = slider(min=0.005, max=0.20, value=state["fin_b"], bind=on_slider_change)
        s.key_name = "fin_b"
        slider_labels["fin_b"] = wtext(text='  {:.3f} m'.format(state["fin_b"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>semi-span</b>  ")
        s = slider(min=0.01, max=0.15, value=state["fin_s"], bind=on_slider_change)
        s.key_name = "fin_s"
        slider_labels["fin_s"] = wtext(text='  {:.3f} m'.format(state["fin_s"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>sweep offset</b>  ")
        s = slider(min=0.0, max=0.15, value=state["fin_m"], bind=on_slider_change)
        s.key_name = "fin_m"
        slider_labels["fin_m"] = wtext(text='  {:.3f} m'.format(state["fin_m"]))
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>Number of Fins</b>  ")
        for opt in [3, 4, 6]:
            b = button(text="  " + str(opt) + "  ", bind=on_option_click)
            b.key_name = "fin_n"
            b.opt_value = opt
            if state["fin_n"] == opt:
                b.background = color.gray(0.4)
                b.color = color.white
            else:
                b.background = color.white
                b.color = color.black
        scene.append_to_caption("\n")

    elif active == "Motor":
        scene.append_to_caption("  <b>Motor type</b>  ")
        for opt in ["C6", "D12", "F15"]:
            b = button(text="  " + opt + "  ", bind=on_option_click)
            b.key_name = "motor_type"
            b.opt_value = opt
            if state["motor_type"] == opt:
                b.background = color.gray(0.4)
                b.color = color.white
            else:
                b.background = color.white
                b.color = color.black
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Delay Charge</b>  ")
        s = slider(min=0, max=15, value=state["motor_delay"], bind=on_slider_change)
        s.key_name = "motor_delay"
        slider_labels["motor_delay"] = wtext(text='  {:.1f} s'.format(state["motor_delay"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption(
            "<div style='display: flex; gap: 10px; margin: 5px 0 5px 30px; align-items: stretch;'>"
            "<div style='flex: 1; padding: 8px; border: 1px solid #ccc; "
            "background: #f5f5f5; font-size: 13px; white-space: pre-wrap;'>"
            + motor_descriptions[state["motor_type"]]
            + "</div>"
            "<div style='padding: 4px; border: 1px solid #ccc; background: #fff; "
            "display: flex; align-items: center;'>"
            + build_thrust_svg(state["motor_type"])
            + "</div>"
            "</div>")
        scene.append_to_caption("\n")

    elif active == "Parachute":
        scene.append_to_caption("  <b>Shroud line length</b>  ")
        s1 = slider(min=0.1, max=1.0, value=state["para_shroud"], bind=on_slider_change)
        s1.key_name = "para_shroud"
        slider_labels["para_shroud"] = wtext(text='  {:.3f} m'.format(state["para_shroud"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Canopy diameter</b>  ")
        s2 = slider(min=0.1, max=1.0, value=state["para_canopy"], bind=on_slider_change)
        s2.key_name = "para_canopy"
        slider_labels["para_canopy"] = wtext(text='  {:.3f} m'.format(state["para_canopy"]))
        scene.append_to_caption("\n\n")
        rec_delay = recommend_delay()
        scene.append_to_caption(
            "<div style='margin: 5px 0 5px 30px; padding: 8px; border: 1px solid #ccc; "
            "background: #f5f5f5; font-size: 13px;'>"
            + f'\t For this parachute to deploy, set the <b>Delay Charge</b> (in the Motor tab) to about <b>{round(rec_delay,3)} s</b>.'
            + "</div>")
        scene.append_to_caption("\n")

    elif active == "Wind":
        scene.append_to_caption("  <b>Wind Magnitude</b>  ")
        s1 = slider(min=0.1, max=20.0, value=state["wind_mag"], bind=on_slider_change)
        s1.key_name = "wind_mag"
        slider_labels["wind_mag"] = wtext(text='  {:.3f} m/s'.format(state["wind_mag"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Wind Angle</b>  ")
        s2 = slider(min=-90.0, max=90.0, value=state["wind_angle"], bind=on_slider_change)
        s2.key_name = "wind_angle"
        slider_labels["wind_angle"] = wtext(text='  {:.3f} deg'.format(state["wind_angle"]))
        scene.append_to_caption("\n\n")
        scene.append_to_caption(
            "<div style='margin: 5px 0 5px 30px; padding: 8px; border: 1px solid #ccc; "
            "background: #f5f5f5; font-size: 13px;'>"
            + "\tThe <b>wind angle is measured from the horizontal</b>: 0&deg; is wind blowing straight "
            + "sideways, +90&deg; is straight up, and -90&deg; is straight down."
            + "</div>")
        scene.append_to_caption("\n")

    elif active == "Graphs":
        scene.append_to_caption("  <b>Customize the X and Y axis for each flight graph</b>\n\n")
        for gi in [1, 2, 3, 4]:
            scene.append_to_caption("  <b>Graph {}</b>   X: ".format(gi))
            mx = menu(choices=GRAPH_VARS, selected=state["g{}_x".format(gi)], bind=on_menu_change)
            mx.key_name = "g{}_x".format(gi)
            scene.append_to_caption("   Y: ")
            my = menu(choices=GRAPH_VARS, selected=state["g{}_y".format(gi)], bind=on_menu_change)
            my.key_name = "g{}_y".format(gi)
            scene.append_to_caption("\n\n")

    scene.append_to_caption("<hr style='margin: 15px 0;'>")
    metric_lbl = wtext(text="<b>Stability margin:</b> --    <b>Mass:</b> -- g\n")
    scene.append_to_caption("\n\n")
    scene.append_to_caption(
    "<div style='display: flex; gap: 10px; margin: 5px 0 5px 30px; align-items: stretch;'>"
    "<div style='flex: 1; padding: 8px; border: 1px solid #ccc; "
    "background: #f5f5f5; font-size: 13px; white-space: pre-wrap;'>"
    + "In Model Rocketry, we aim to have the Stability Margin(dist(CoG,CoP)/body tube diameter) between <b>1.5 and 2.5 cal</b>. Also, note that we want the CoP to be below the CoG to be stable."
    + "</div>")
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
        elif nc_type == "Ogive":     x = r * sqrt(max(0.0, 1 - tt**2))
        else:                        x = r * (1 - tt)
        points.append(vector(x, y, 0))
    for i in range(steps, -1, -1):
        tt = i/steps
        y = bt_top + tt * length
        if   nc_type == "Parabolic": x = r * (1 - tt**2)
        elif nc_type == "Ogive":     x = r * sqrt(max(0.0, 1 - tt**2))
        else:                        x = r * (1 - tt)
        points.append(vector(-x, y, 0))
    return points

def makeFin(side):
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
    dx = pt.x - pivot.x
    dy = pt.y - pivot.y
    c = cos(theta_cw); s = sin(theta_cw)
    return vector(pivot.x + dx*c + dy*s, pivot.y - dx*s + dy*c, pt.z)

def cg_visual_y(x_CG):
    nose_y = state["bt_length"]/2 + state["nc_length"]
    return nose_y - x_CG

body_curve   = curve(color=color.black)
nose_curve   = curve(color=color.black)
fin_curve_l  = curve(color=color.black)
fin_curve_r  = curve(color=color.black)
chute_canopy = curve(color=color.red,       visible=False)
chute_shroud = curve(color=color.gray(0.4), visible=False)

cg_marker = sphere(pos=vector(0,0,0), radius=0.008, color=color.red,  visible=False)
cp_marker = sphere(pos=vector(0,0,0), radius=0.008, color=color.blue, visible=False)
cg_label  = label(pos=vector(0,0,0), text="CG", color=color.red,  box=False, opacity=0, height=10, visible=False)
cp_label  = label(pos=vector(0,0,0), text="CP", color=color.blue, box=False, opacity=0, height=10, visible=False)

BG_BASE       = "https://raw.githubusercontent.com/phynder21/Physics-Project/main/"
BG_IMAGES = [
    {"url": BG_BASE + "sky.jpg",    "aspect": 5304/7952},
    {"url": BG_BASE + "sunset.jpg", "aspect": 4000/6000},
    {"url": BG_BASE + "night.jpg",  "aspect": 1000/1000},
]
GROUND_LEVEL  = -0.22
IMG_W         = 1.4
NTILES        = 3
BG_Z          = -0.6
ALT_PER_IMAGE = 120.0
TILE_H        = IMG_W * BG_IMAGES[0]["aspect"]
BG_SCALE      = TILE_H / ALT_PER_IMAGE

sky_tiles = []
for _t in range(NTILES):
    sky_tiles.append(box(pos=vector(0, GROUND_LEVEL + (_t + 0.5)*TILE_H, BG_Z),
                         size=vector(IMG_W, TILE_H, 0.005),
                         texture={'file': BG_IMAGES[0]["url"], 'mapping': 'sign'},
                         emissive = True, visible=False))

GROUND_BOX_H = 4.0
ground_box = box(pos=vector(0, GROUND_LEVEL - GROUND_BOX_H/2, BG_Z + 0.02),
                 size=vector(IMG_W*1.2, GROUND_BOX_H, 0.005),
                 color=vector(0.20, 0.55, 0.18), emissive = True, visible=False)

def set_bg_visible(v):
    for _s in sky_tiles:
        _s.visible = v
    ground_box.visible = v

def update_background():
    scroll = flight['y'] * BG_SCALE
    if scroll < 0:
        scroll = 0
    center_idx = int((scroll - GROUND_LEVEL) / TILE_H)
    i0 = center_idx - 1
    for j in range(NTILES):
        ci = i0 + j
        if ci < 0:
            sky_tiles[j].visible = False
        else:
            sky_tiles[j].visible = True
            sky_tiles[j].pos = vector(0, GROUND_LEVEL + (ci + 0.5)*TILE_H - scroll, BG_Z)
    ground_box.pos = vector(0, (GROUND_LEVEL - GROUND_BOX_H/2) - scroll, BG_Z + 0.02)

def randomize_background():
    global TILE_H, BG_SCALE
    choice   = BG_IMAGES[int(random() * len(BG_IMAGES))]
    TILE_H   = IMG_W * choice["aspect"]
    BG_SCALE = TILE_H / ALT_PER_IMAGE
    for _t in range(NTILES):
        sky_tiles[_t].texture = {'file': choice["url"], 'mapping': 'sign'}
        sky_tiles[_t].size    = vector(IMG_W, TILE_H, 0.005)
        sky_tiles[_t].pos     = vector(0, GROUND_LEVEL + (_t + 0.5)*TILE_H, BG_Z)

Z_FILL        = -0.005
NC_FILL_STEPS = 24

def vert():
    return vertex(pos=vector(0, 0, Z_FILL), color=color.white, normal=vector(0, 0, 1))

vb_body  = []
vb_fin_l = []
vb_fin_r = []
vb_nose  = []
for _q in range(4):
    vb_body.append(vert())
    vb_fin_l.append(vert())
    vb_fin_r.append(vert())
for _q in range(2*(NC_FILL_STEPS + 1)):
    vb_nose.append(vert())

quad(vs=vb_body)
quad(vs=vb_fin_l)
quad(vs=vb_fin_r)
for _i in range(NC_FILL_STEPS):
    quad(vs=[vb_nose[2*_i], vb_nose[2*_i+1], vb_nose[2*_i+3], vb_nose[2*_i+2]])

def nose_fill_pairs():
    r       = state["bt_diameter"] / 2
    length  = state["nc_length"]
    bt_top  = state["bt_length"] / 2
    nc_type = state["nc_type"]
    pairs = []
    for i in range(NC_FILL_STEPS + 1):
        tt = i / NC_FILL_STEPS
        y  = bt_top + tt * length
        if   nc_type == "Parabolic": x = r * (1 - tt**2)
        elif nc_type == "Ogive":     x = r * sqrt(max(0.0, 1 - tt**2))
        else:                        x = r * (1 - tt)
        pairs.append((vector(x, y, 0), vector(-x, y, 0)))
    return pairs

def _place(vlist, pts, pivot, th, do_rot):
    for k in range(len(pts)):
        p = pts[k]
        if do_rot:
            q = rotate_about(p, pivot, th)
        else:
            q = p
        vlist[k].pos = vector(q.x, q.y, Z_FILL)

def update_fill(pivot, th, do_rot):
    bc = makeRect(state["bt_diameter"], state["bt_length"])
    _place(vb_body, [bc[0], bc[1], bc[2], bc[3]], pivot, th, do_rot)
    fl = makeFin(+1); fr = makeFin(-1)
    _place(vb_fin_l, [fl[0], fl[1], fl[2], fl[3]], pivot, th, do_rot)
    _place(vb_fin_r, [fr[0], fr[1], fr[2], fr[3]], pivot, th, do_rot)
    pairs = nose_fill_pairs()
    npts = []
    for i in range(NC_FILL_STEPS + 1):
        npts.append(pairs[i][0])
        npts.append(pairs[i][1])
    _place(vb_nose, npts, vector(0, 0, 0) if not do_rot else pivot, th, do_rot)

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

    update_fill(vector(0, 0, 0), 0.0, False)
    chute_canopy.visible = False
    chute_shroud.visible = False

    compute_geom()
    x_CG, total_mass, _b, _c, _d, _e = calc_CG(0.0)
    x_CP, _f  = calc_CP()
    margin = abs(x_CG - x_CP) / state["bt_diameter"]
    if metric_lbl is not None:
        metric_lbl.text = f'<b>Stability margin:</b> {round(margin,3)} cal    <b>Mass:</b> {round(total_mass *1000,3)} g'
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
    cg_marker.visible = True; cg_label.visible = True
    cp_marker.visible = True; cp_label.visible = True

    x_CG, _a, _b, _c, _d, _e = calc_CG(flight['t'])
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

    update_fill(pivot, th, True)

    x_CP, _f = calc_CP()
    cp_unrot = vector(0, cg_visual_y(x_CP), 0)
    cp_pos = rotate_about(cp_unrot, pivot, th)
    cg_marker.pos = pivot
    cp_marker.pos = cp_pos
    r = state["bt_diameter"] / 2
    cg_label.pos = vector(pivot.x + r + 0.03, pivot.y, 0)
    cp_label.pos = vector(cp_pos.x + r + 0.03, cp_pos.y, 0)

    if flight['chute']:
        nose_y = state["bt_length"]/2 + state["nc_length"]
        room   = max(0.05, 0.39 - nose_y)
        rim_y  = nose_y + room*0.4
        dome_h = room*0.6
        rc     = min(state["para_canopy"]/2, 0.20)
        chute_canopy.clear()
        for k in range(25):
            ang = pi * (1 - k/24.0)
            chute_canopy.append(rotate_about(vector(rc*cos(ang), rim_y + dome_h*sin(ang), 0), pivot, th))
        chute_shroud.clear()
        for p in [vector(-rc, rim_y, 0), vector(0, nose_y, 0), vector(rc, rim_y, 0)]:
            chute_shroud.append(rotate_about(p, pivot, th))
        chute_canopy.visible = True
        chute_shroud.visible = True
    else:
        chute_canopy.visible = False
        chute_shroud.visible = False

GRAPH_COLORS = [color.blue, color.red, color.green, color.magenta]
flight_graphs = []
flight_curves = []
flight_axes   = []

def graph_value(name):
    if   name == "Flight time":             return flight['t']
    elif name == "Height":                  return flight['y']
    elif name == "Vertical velocity":       return flight['vy']
    elif name == "Total velocity":          return sqrt(flight['vx']**2 + flight['vy']**2)
    elif name == "Pitch":                   return flight['theta'] * (180/pi)
    elif name == "Pitch angular velocity":  return flight['omega'] * (180/pi)
    return 0.0

def clear_flight_graphs():
    global flight_graphs, flight_curves, flight_axes
    for c in flight_curves:
        c.delete()
    for gph in flight_graphs:
        gph.delete()
    flight_graphs = []
    flight_curves = []
    flight_axes   = []

def make_flight_graphs():
    global flight_graphs, flight_curves, flight_axes
    clear_flight_graphs()
    for gi in [1, 2, 3, 4]:
        xname = state["g{}_x".format(gi)]
        yname = state["g{}_y".format(gi)]
        gph = graph(width=340, height=240, align="left", fast=True,
                    title="<b>{} vs {}</b>".format(yname, xname),
                    xtitle=xname, ytitle=yname)
        c = gcurve(graph=gph, color=GRAPH_COLORS[gi-1])
        flight_graphs.append(gph)
        flight_curves.append(c)
        flight_axes.append([xname, yname])

def update_graphs():
    for gi in range(len(flight_curves)):
        xname = flight_axes[gi][0]
        yname = flight_axes[gi][1]
        flight_curves[gi].plot(graph_value(xname), graph_value(yname))

randomize_background()
draw_ui()
redraw_design()

steps_per_frame = 4

while True:
    rate(25)
    if mode == "design":
        set_bg_visible(True)
        redraw_design()
    else:
        set_bg_visible(True)
        for _ in range(steps_per_frame):
            step_sim()
            if flight['done']:
                break
        redraw_launch()
        update_background()
        if height_lbl is not None:
            height_lbl.text = "Height: {:.3f} m  (apogee {:.3f} m)\n".format(flight['y'], flight['apogee'])
        if time_lbl is not None:
            time_lbl.text   = "Time:   {:.3f} s\n".format(flight['t'])
        if not flight['done']:
            update_graphs()