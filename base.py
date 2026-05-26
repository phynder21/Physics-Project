from vpython import *

scene.background = color.white
scene.range = 6
scene.title = "\n Title \n\n"

initLength = 4
initHeight = 2

def makeRect(L, H):
    return [
        vector(-L/2, -H/2, 0),
        vector( L/2, -H/2, 0),
        vector( L/2,  H/2, 0),
        vector(-L/2,  H/2, 0),
        vector(-L/2, -H/2, 0),
    ]

rect = curve(pos=makeRect(initLength, initHeight), color=color.black)


def onLength(evt):
    lengthText.text = '{:1.2f}'.format(evt.value)

def onHeight(evt):
    heightText.text = '{:1.2f}'.format(evt.value)

scene.append_to_caption("\n Length: ")
lengthSlider = slider(bind=onLength, min=0.1, max=10, value=initLength)
lengthText = wtext(text='{:1.2f}'.format(initLength))
scene.append_to_caption(" meters\n")

scene.append_to_caption("\n Height: ")
heightSlider = slider(bind=onHeight, min=0.1, max=10, value=initHeight)
heightText = wtext(text='{:1.2f}'.format(initHeight))
scene.append_to_caption(" meters\n")

while True:
    rate(20)
    rect.clear()
    for p in makeRect(lengthSlider.value, heightSlider.value):
        rect.append(p)