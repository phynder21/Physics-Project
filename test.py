from vpython import *

scene.range = 5 
initX = 0 
cube = box(pos=vector(initX, 0, 0), color=color.blue) 
scene.title = "\n Where is the box? \n\n" 

# 1. Define the function FIRST so the slider can find it
def moveBoxSlide(evt):
    cubePos.text = '{:1.2f}'.format(evt.value)
    cube.pos.x = evt.value  # Update the cube position immediately when slid

# 2. Create the slider and text elements SECOND
moveBox = slider(bind=moveBoxSlide, min=-5, max=5, value=initX) 
scene.append_to_caption("\n The box is at x = ") 
cubePos = wtext(text='{:1.2f}'.format(moveBox.value)) 
scene.append_to_caption(" meters\n") 

# 3. Simple keep-alive loop
while True: 
    rate(20)
