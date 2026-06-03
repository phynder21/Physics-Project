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
    nc_length=1.0,  nc_type="Parabolic",
    bt_length=4.0,  bt_diameter=0.5,
    fin_a=1.0,  fin_b=0.5,  fin_s=0.8,  fin_n=4,  fin_m=0.2,
    motor_type="D12",  motor_delay=5.0,
    para_shroud=1.0,  para_canopy=0.5,
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
        s = slider(min=0.1, max=5.0, value=state["nc_length"], bind=on_slider_change)
        s.key_name = "nc_length"
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Type</b>  ")
        for opt in ["Parabolic", "Ogive", "Conical"]:
            lbl = " [" + opt + "] " if state["nc_type"] == opt else "  " + opt + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "nc_type"
            b.opt_value = opt
        scene.append_to_caption("\n")

    # body tube
    elif active_tab == "Body Tube":
        scene.append_to_caption("  <b>Length</b>  ")
        s = slider(min=0.1, max=10.0, value=state["bt_length"], bind=on_slider_change)
        s.key_name = "bt_length"
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Diameter</b>  ")
        s = slider(min=0.1, max=5.0, value=state["bt_diameter"], bind=on_slider_change)
        s.key_name = "bt_diameter"
        scene.append_to_caption("\n")

    # fins
    elif active_tab == "Fins":
        fin_params = [
            ("a (root chord)", "fin_a", 0.1, 3.0),
            ("b (tip chord)",  "fin_b", 0.1, 2.0),
            ("s (semi-span)",  "fin_s", 0.1, 3.0),
            ("m (sweep offset)","fin_m", 0.0, 2.0)
        ]
        for lbl, key, lo, hi in fin_params:
            scene.append_to_caption("  <b>" + lbl + "</b>  ")
            s = slider(min=lo, max=hi, value=state[key], bind=on_slider_change)
            s.key_name = key
            scene.append_to_caption("\n\n")
        scene.append_to_caption("  <b>Number of Fins</b>  ")
        for opt in [3, 4, 6]:
            lbl = " [" + str(opt) + "] " if state["fin_n"] == opt else "  " + str(opt) + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "fin_n"
            b.opt_value = opt
        scene.append_to_caption("\n")

    # motor
    elif active_tab == "Motor":
        scene.append_to_caption("  <b>Motor type</b>  ")
        for opt in ["C6", "D12", "F15"]:
            lbl = " [" + opt + "] " if state["motor_type"] == opt else "  " + opt + "  "
            b = button(text=lbl, bind=on_option_click)
            b.key_name = "motor_type"
            b.opt_value = opt
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Delay charge</b>  ")
        s = slider(min=0, max=15, value=state["motor_delay"], bind=on_slider_change)
        s.key_name = "motor_delay"
        scene.append_to_caption("\n")

    # parachute
    elif active_tab == "Parachute":
        scene.append_to_caption("  <b>Shroud line length</b>  ")
        s1 = slider(min=0.1, max=5.0, value=state["para_shroud"], bind=on_slider_change)
        s1.key_name = "para_shroud"
        scene.append_to_caption("\n\n")
        
        scene.append_to_caption("  <b>Canopy diameter</b>  ")
        s2 = slider(min=0.1, max=3.0, value=state["para_canopy"], bind=on_slider_change)
        s2.key_name = "para_canopy"
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

draw_ui()

while True:
    rate(20)
    rect.clear()
    for p in makeRect(state["bt_diameter"], state["bt_length"]):
        rect.append(p)
    nosecone.clear()
    for p in MakeNosecone(state["nc_length"], state["bt_diameter"]):
        nosecone.append(p)

while True:
    rate(10)