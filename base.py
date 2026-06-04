from vpython import *

scene.align = "left"
scene.width  = 450
scene.height = 550
scene.background = color.white
scene.title  = "Rocket Simulator\n"

TABS = ["Nosecone", "Body Tube", "Fins", "Motor", "Parachute"]
# Starting configurations for each tab
DEFAULTS = dict(
    tab="Nosecone",
    nc_length = 1.0,  nc_type="Parabolic",
    bt_length = 4.0,  bt_diameter = 0.5,
    fin_a = 0.3,  fin_b = 0.15,  fin_s = 0.3,  fin_n=4,  fin_m=0.1,
    motor_type="D12",  motor_delay = 5.0,
    para_shroud = 1.0,  para_canopy = 0.5,
)
state = dict(DEFAULTS)

# UI event handlers, basically just update the state of each interaction (button press, slider)
def on_tab_click(b):
    state["tab"] = b.tab_name
    draw_ui()

def on_slider_change(s):
    state[s.key_name] = s.value

def on_option_click(b):
    state[b.key_name] = b.opt_value
    draw_ui()

def on_launch():
    pass

def on_reset():
    state.update(DEFAULTS)
    draw_ui()

def draw_ui():
    scene.caption = ""
    #formatting
    scene.append_to_caption("<div style='margin-left: 30px; display: inline-block; vertical-align: top; font-family: sans-serif;'>")
    scene.append_to_caption("<div><h2 style='margin: 0;'>Design Workbench</h2></div>")
    scene.append_to_caption("<br>")
    # highlights with ** for tab selected
    for i in TABS:
        lbl = " * " + i + " * " if state["tab"] == i else "   " + i + "   "
        b = button(text=lbl, bind=on_tab_click)
        b.tab_name = i 
    scene.append_to_caption("<hr style='margin: 15px 0;'>")

    active_tab = state["tab"]

    # nosecone
    if active_tab == "Nosecone":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min = 0.1, max = 5.0, value=state["nc_length"], bind = on_slider_change)
        s.key_name = "nc_length"
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Type</b>  ")
        for opt in ["Parabolic", "Ogive", "Conical"]:
            lbl = " [" + opt + "] " if state["nc_type"] == opt else "  " + opt + "  "
            b = button(text = lbl, bind = on_option_click)
            b.key_name = "nc_type"
            b.opt_value = opt
        scene.append_to_caption("\n")

    # body tube
    elif active_tab == "Body Tube":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min = 0.1, max = 10.0, value = state["bt_length"], bind = on_slider_change)
        s.key_name = "bt_length"
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Diameter</b>  ")
        s = slider(min = 0.1, max = 5.0, value = state["bt_diameter"], bind = on_slider_change)
        s.key_name = "bt_diameter"
        scene.append_to_caption("\n")

    # fins
    elif active_tab == "Fins":

        scene.append_to_caption("  <b>a (root chord)</b>  ")
        wt_a = wtext(text='  {:.2f} m'.format(state["fin_a"]))
        scene.append_to_caption("\n")
        def on_fin_a(s):
            state["fin_a"] = s.value
            wt_a.text = '  {:.2f} m'.format(s.value)
        s = slider(min = 0.1, max = 0.5, value = state["fin_a"], bind = on_fin_a)
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>b (tip chord)</b>  ")
        wt_b = wtext(text='  {:.2f} m'.format(state["fin_b"]))
        scene.append_to_caption("\n")
        def on_fin_b(s):
            state["fin_b"] = s.value
            wt_b.text = '  {:.2f} m'.format(s.value)
        s = slider(min = 0.05, max = 0.5, value = state["fin_b"], bind = on_fin_b)
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>s (semi-span)</b>  ")
        wt_s = wtext(text='  {:.2f} m'.format(state["fin_s"]))
        scene.append_to_caption("\n")
        def on_fin_s(s):
            state["fin_s"] = s.value
            wt_s.text = '  {:.2f} m'.format(s.value)
        sl = slider(min = 0.1, max = 0.5, value = state["fin_s"], bind = on_fin_s)
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>m (sweep offset)</b>  ")
        wt_m = wtext(text='  {:.2f} m'.format(state["fin_m"]))
        scene.append_to_caption("\n")
        def on_fin_m(s):
            state["fin_m"] = s.value
            wt_m.text = '  {:.2f} m'.format(s.value)
        sl = slider(min = 0.0, max = 0.5, value = state["fin_m"], bind = on_fin_m)
        scene.append_to_caption("\n\n")

        scene.append_to_caption("  <b>Number of Fins</b>  ")
        for opt in [3, 4, 6]:
            lbl = " [" + str(opt) + "] " if state["fin_n"] == opt else "  " + str(opt) + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "fin_n"
            b.opt_value = opt
        scene.append_to_caption("\n")

    
    # launch and reset 
    scene.append_to_caption("<hr style='margin: 15px 0;'>")
    launch_btn = button(text="Launch!", bind=on_launch)
    scene.append_to_caption("   ")
    reset_btn = button(text="Reset", bind=on_reset)
    scene.append_to_caption("</div>")

def makeRect(L, H):
    return [
        vector(-L/2, -H/2, 0),
        vector( L/2, -H/2, 0),
        vector( L/2,  H/2, 0),
        vector(-L/2,  H/2, 0),
        vector(-L/2, -H/2, 0),
    ]

rect = curve(color=color.black)

def MakeNosecone(length, diameter):
    points = []
    r = diameter/2
    steps = 50
    bt_top = state["bt_length"] / 2
    nc_type = state["nc_type"]
    for i in range(steps+1):
        t = i/steps
        y = bt_top + t * length
        if nc_type == "Parabolic":
            x = r * (1 - t ** 2)
        elif nc_type == "Ogive":
            x = r * sqrt(1 - t ** 2)
        elif nc_type == "Conical":
            x = r * (1 - t)
        points.append(vector(x, y, 0))
    for i in range (steps, -1, -1):
        t= i / steps
        y = bt_top + t * length
        if nc_type == "Parabolic":
            x = r * (1 - t ** 2)
        elif nc_type == "Ogive":
            x = r * sqrt(1 - t ** 2)
        elif nc_type == "Conical":
            x = r * (1 - t)
        points.append(vector(-x, y, 0))
    return points

nosecone = curve(color=color.black)

def makeFin():
    a = state["fin_a"]
    b = state["fin_b"]
    s = state["fin_s"]
    m = state["fin_m"]
    bt_bottom = -state["bt_length"] / 2
    r = state["bt_diameter"] / 2

    p1 = vector(r,     bt_bottom,           0)
    p2 = vector(r,     bt_bottom + a,       0)
    p3 = vector(r + s, bt_bottom + a - m,   0)
    p4 = vector(r + s, bt_bottom + a - m - b, 0)

    return [p1, p2, p3, p4, p1]

fin = curve(color=color.black)

draw_ui()

while True:
    rate(20)
    rect.clear()
    for p in makeRect(state["bt_diameter"], state["bt_length"]):
        rect.append(p)
    nosecone.clear()
    for p in MakeNosecone(state["nc_length"], state["bt_diameter"]):
        nosecone.append(p)
    fin.clear()
    for p in makeFin():
        fin.append(p)

while True:
    rate(10)