#AcrylicTK

This package will add acrylic/transparency support
to tkinter.

##How to use

###Installing
First thing, you have to install it!
use this command to install
```
pip install acrylictk
```
###Making the window
Making a window is almost the same as tkinter. But
to use widgets or tkinter methods you will need access it by 
using the atk variable.
here is how to make a new window
```
from AcrylicTK import *

win = ATK()

win.atk.mainloop()
```
You need to refrence the window like this
###Adding widgets
Adding widgets is pretty easy. We will
add a simple label that says hello
```
from AcrylicTK import *


win = ATK()

lbl = Label(win.atk, text="Hello", font="arial 10")
lbl.place(x=0, y=0)

win.atk.mainloop()
```
#Making a transparent spot
Now for the whole point of the libary. 
To make a transparent spot use the widget that
AcrylicTK adds called transparency.
Here is how you use it.
```
from AcrylicTK import *


win = ATK()

tsp = transparency(win.atk, 10000, hieght=100)
tsp.place(x=0, y=0)
lbl = Label(win.atk, text="Hello", font="arial 10")
lbl.place(x=0, y=0)

win.atk.mainloop()
```
There, now we have a transparent spot
The effects will only work on an ATK window
To make the background of the text transparent
I added a variable called acrylic use it in the bg
argument of the label like this.
```
from AcrylicTK import *


win = ATK()

tsp = transparency(win.atk, 10000, hieght=100)
tsp.place(x=0, y=0)
lbl = Label(win.atk, text="Hello", font="arial 10", bg=acrylic)
lbl.place(x=0, y=0)

win.atk.mainloop()
```
#ATK Methods
Here are all the useful methods that acrylicTK adds
##ATK()
ATK is the class that makes the window
Arguments:
darkMode - enables dark title bar
##ATK.config()
Change settings for the window
```
from AcrylicTK import *


win = ATK()

win.config(windowPosX=100, windowPosY=100, windowWidth=500, windowHieght=400, acrylic=False)

tsp = transparency(win.atk, 10000, hieght=100)
tsp.place(x=0, y=0)
lbl = Label(win.atk, text="Hello", font="arial 10", bg=acrylic)
lbl.place(x=0, y=0)

win.atk.mainloop()
```
You can guess what the first four aguments are
but the last argument if True will enable the acrylic effect
like seen in the windows 10 start menu
if False, It will just be a simple blur

##ATK.update()
This updates the window. use this NOT
ATK.atk.update()
