Web VPython 3.2
# Hello. This is Philip and Kiran. This README will explain what we made, how it works, and how to use it!

# We made a model rocket simulator! The setup is quite simple. There are two modes in the simulator: The “Design Workbench” and “Flight”. 

# In “Design Workbench”, there are two main buttons. The first one is the “Launch!” button, which switches the interface into “Flight” mode,
# and the second one is the “Reset” button which resets all the rocket changes you made to a default rocket. 


# In “Flight”, there are also two main buttons. The first one is the “Skip to end” button, 
# which allows the user to skip watching the launch and see the end resulting graphs, height, time, and rocket position. 
# The second button is “Back to design”, which allows the user to go back to the “Design Workbench” with all existing rocket changes intact.


# Now into the actual rocket design. There are seven different tabs that you can select that will change the rocket or information you see. 
# Simply press on the name of the tab you want to go to, and it will be highlighted and the new tab will appear for customization! 
# We will go through each tab one by one and explain what each thing does. 


# The first tab is the “Nosecone”. There are two things you can change with the nosecone. The first is the nosecone length (with a slider), 
# with range 0.05m to 0.3m, and the nosecone type (a button). The base diameter of the nosecone is set by the body tube diameter, 
# which is in another tab. Each nosecone type (Parabolic, Ogive, and Conical) corresponds to a different shape, 
# which you can see updated in the diagram of the rocket as you select a new nosecone type.


# The second tab is the”Body Tube” tab. There are two sliders here which control the body tube length, with range 0.1m to 0.999m, 
# and body tube diameter, with range 0.02m to 0.15m.


# The third tab is the “Fins” tab. This tab has five different customizations. The first four are sliders. These four sliders define different aspects of the fins. 
# The first slider is the root chord, which is the length of the edge of the fin attached to the rocket. This slider has a range from 0.03m to 0.2m. 
# The second slider is the tip chord, this is the length of the outermost edge of the fin that is parallel to the rocket. This slider has a range from 0.005m to 0.06m. 
# The third slider is the semi-span, which is essentially how far the fin extends from the surface of the body tube. This slider has a range from 0.01m to 0.15m. 
# The fourth slider is the sweep offset, which is the vertical distance from the top of the root chord to the top of the tip chord. This slider has a range from 0m to 0.135m. 
# The last is a customization of the number of fins and is a button that allows you to select from 3,4, and 6 fins (nothing else is available for computational purposes). 

#The fourth tab is the “Motor” tab. There is a selection for motor type, as well as a slider for delay charge, with range 0.0s to 15.0s. 
# Simply select a different motor (C6, D12, F15) for a different thrust. There is a little blurb of text that includes the total impulse range of the motor type, 
# the average thrust number implication, a recommended rocket mass for each motor’s rocket class, and a note about the delay charge which is that:
# “the delay charge is the amount of seconds after main fuel burnout that the ejection charge ejects the parachute”. 
# Each motor type's thrust curve is also on display to the right of the blurb of text. 


# The fifth tab is the parachute tab. You can customize the shroud line length, which is the length of the parachute lines, with a slider of range 0.1m to 0.999m. 
# You can also customize the canopy diameter, which is the diameter of the parachute, with a slider of range 0.1m to 0.999m. 
# This tab also includes a tip for delay charge selection that ensures the parachute deploys.

# The sixth tab is the “Wind” tab. There are two sliders here. The first “wind magnitude” slider has a range of 0.1m/s to 20m/s, and simply changes the magnitude of the wind. 
# The second slider changes the angle, from -90° to 90°, at which the wind hits the rocket measured with the horizontal being 0°. A tip about this exists on the tab.

# The final tab is the “Graphs” tab. When you launch the rocket, four graphs appear next to the simulated launch. In this tab, you can select what the X and Y
# should show for each graph. You can select from flight time, height, vertical velocity, total velocity, pitch, and pitch angular velocity. 
# Note that pitch is the angle about the center of gravity and is observed in the rocket’s rotation in “Flight” mode. 

# Constantly displayed throughout the “Design Workbench” is the Stability Margin, which is the distance between the center of gravity and center of pressure divided by 
# the body tube diameter. This is a standard metric used in model rocketry creation to determine how stable the rocket will be in flight, a tip for the Stability Margin 
# (to keep it between 1.5 cal and 2.5 cal exists on the screen). Another metric that exists at all times on the “Design Workbench” screen is the mass of the model rocket, 
# which can be used in conjunction with the blurb in the “Motor” tab to create a stable rocket. 

# Also, a fun tidbit is that everytime you refresh/rest the page a new background will be chosen from a set of three (day, night, and sunset)!

# To learn more about the exact math and physics that was used in this simulation go to the following pdf link (note that you can click on some words as links): 
# https://drive.google.com/file/d/1HNd3ALFwpUoABCPag85L_yI3zDHrxrME/view?usp=sharing