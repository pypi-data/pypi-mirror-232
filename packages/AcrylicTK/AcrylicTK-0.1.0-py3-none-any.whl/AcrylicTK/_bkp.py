from tkinter import *
from ctypes import windll
#source: https://github.com/Opticos/GWSL-Source/blob/master/blur.py , https://www.cnblogs.com/zhiyiYo/p/14659981.html , https://github.com/ifwe/digsby/blob/master/digsby/src/gui/vista.py
import platform
import ctypes

if platform.system() == 'Darwin':
    from AppKit import *

    def MacBlur(QWidget,Material=NSVisualEffectMaterialPopover,TitleBar:bool=True):
        #WIP, trying to implement CGSSetWindowBackgroundBlurRadius too
        frame = NSMakeRect(0, 0, QWidget.width(), QWidget.height())
        view = objc.objc_object(c_void_p=QWidget.winId().__int__())

        visualEffectView = NSVisualEffectView.new()
        visualEffectView.setAutoresizingMask_(NSViewWidthSizable|NSViewHeightSizable) #window resizable
        #visualEffectView.setWantsLayer_(True)
        visualEffectView.setFrame_(frame)
        visualEffectView.setState_(NSVisualEffectStateActive)
        visualEffectView.setMaterial_(Material) #https://developer.apple.com/documentation/appkit/nsvisualeffectmaterial
        visualEffectView.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)

        window = view.window()
        content = window.contentView()

        try:
            from PyQt5.QtWidgets import QMacCocoaViewContainer
            
        except:
            print('You need PyQt5')
            exit()
            
        container = QMacCocoaViewContainer(0,QWidget)
        content.addSubview_positioned_relativeTo_(visualEffectView, NSWindowBelow, container)  

        if TitleBar:
            #TitleBar with blur
            window.setTitlebarAppearsTransparent_(True)
            window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)

        #appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        #window.setAppearance_(appearance)


if platform.system() == 'Windows':
    from ctypes.wintypes import  DWORD, BOOL, HRGN, HWND
    user32 = ctypes.windll.user32
    dwm = ctypes.windll.dwmapi


    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_uint),
            ("AccentFlags", ctypes.c_uint),
            ("GradientColor", ctypes.c_uint),
            ("AnimationId", ctypes.c_uint)
        ]


    class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.POINTER(ctypes.c_int)),
            ("SizeOfData", ctypes.c_size_t)
        ]


    class DWM_BLURBEHIND(ctypes.Structure):
        _fields_ = [
            ('dwFlags', DWORD), 
            ('fEnable', BOOL),  
            ('hRgnBlur', HRGN), 
            ('fTransitionOnMaximized', BOOL) 
        ]


    class MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                    ]


    SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
    SetWindowCompositionAttribute.argtypes = (HWND, WINDOWCOMPOSITIONATTRIBDATA)
    SetWindowCompositionAttribute.restype = ctypes.c_int


def ExtendFrameIntoClientArea(HWND):
    margins = MARGINS(-1, -1, -1, -1)
    dwm.DwmExtendFrameIntoClientArea(HWND, ctypes.byref(margins))


def Win7Blur(HWND,Acrylic):
    if Acrylic == False:
        DWM_BB_ENABLE = 0x01
        bb = DWM_BLURBEHIND()
        bb.dwFlags = DWM_BB_ENABLE
        bb.fEnable = 1
        bb.hRgnBlur = 1
        dwm.DwmEnableBlurBehindWindow(HWND, ctypes.byref(bb))
    else:
        ExtendFrameIntoClientArea(HWND)


def HEXtoRGBAint(HEX:str):
    alpha = HEX[7:]
    blue = HEX[5:7]
    green = HEX[3:5]
    red = HEX[1:3]

    gradientColor = alpha + blue + green + red
    return int(gradientColor, base=16)


def blur(hwnd, hexColor=False, Acrylic=False, Dark=False):
    accent = ACCENTPOLICY()
    accent.AccentState = 3 #Default window Blur #ACCENT_ENABLE_BLURBEHIND

    gradientColor = 0
    
    if hexColor != False:
        gradientColor = HEXtoRGBAint(hexColor)
        accent.AccentFlags = 2 #Window Blur With Accent Color #ACCENT_ENABLE_TRANSPARENTGRADIENT
    
    if Acrylic:
        accent.AccentState = 4 #UWP but LAG #ACCENT_ENABLE_ACRYLICBLURBEHIND
        if hexColor == False: #UWP without color is translucent
            accent.AccentFlags = 2
            gradientColor = HEXtoRGBAint('#12121240') #placeholder color
    
    accent.GradientColor = gradientColor
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19 #WCA_ACCENT_POLICY
    data.SizeOfData = ctypes.sizeof(accent)
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))
    
    SetWindowCompositionAttribute(int(hwnd), data)
    
    if Dark: 
        data.Attribute = 26 #WCA_USEDARKMODECOLORS
        SetWindowCompositionAttribute(int(hwnd), data)


def BlurLinux(WID): #may not work in all distros (working in Deepin)
    import os

    c = "xprop -f _KDE_NET_WM_BLUR_BEHIND_REGION 32c -set _KDE_NET_WM_BLUR_BEHIND_REGION 0 -id " + str(WID)
    os.system(c)


def GlobalBlur(HWND,hexColor=False,Acrylic=False,Dark=False,QWidget=None):
    release = platform.release()
    system = platform.system()

    if system == 'Windows':
        if release == 'Vista': 
            Win7Blur(HWND,Acrylic)
        else:
            release = int(float(release))
            if release == 10 or release == 8 or release == 11: #idk what windows 8.1 spits, if is '8.1' int(float(release)) will work...
                blur(HWND,hexColor,Acrylic,Dark)
            else:
                Win7Blur(HWND,Acrylic)
    
    if system == 'Linux':
        BlurLinux(HWND)

    if system == 'Darwin':
        MacBlur(QWidget)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *

    class MainWindow(QWidget):
        def __init__(self):
            super(MainWindow, self).__init__()
            #self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.resize(500, 400)
            
            hWnd = self.winId()
            #print(hWnd)
            l = QLabel('Can you see me?',self)
            GlobalBlur(hWnd,Dark=True,QWidget=self)
            

            self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()

    #blur(mw.winId())
    #ExtendFrameIntoClientArea(mw.winId())

    sys.exit(app.exec_())


AppBG = None
App = None
acrylic = '#010101'


class transparency:
    '''
    This widget will add a transparent spot.
    '''
    ts = None
    def __init__(self, master:Misc, width, hieght):
        self.msr = master
        self.wd:int = width
        self.ht:int = hieght
        global ts
        ts = Frame(self.msr, width=self.wd, height=self.ht, bg="#010101") 
    def place(self, x:int = 0, y:int = 0):
        ts.place(x=x, y=y)
        

#the class to make the window
class ATK():
    '''
    This will create a tkinter window that 
    will have transparency/acrylic support.
    Make the window like you would with a normal tkinter
    window. it will look like this:\n
    root = ATK()\n
    To add widgets or use tkinter functions 
    you will have to acess the atk varible
    that is in the ATK class:\n
    root.atk.mainloop()
    '''
    Dm:bool = None
    def __init__(self, darkMode:bool = False):
        self.Dm:bool = darkMode
    global App
    global AppBG
    
    
    px = 100
    py = 100
    w = 400
    h = 500
    Bg = "#eeeeee"
    Ac = False 
    def config(self, windowPosX:int=None, windowPosY:int=None, windowWidth:int=None, windowHieght:int=None, bg:str=None, acrylic:bool=None):
        global px
        global py
        global w
        global h
        global Bg
        global Ac
        
        px = windowPosX
        py = windowPosY
        w = windowWidth
        h = windowHieght
        Bg = bg
        Ac = acrylic
        self.update()
        print(str(Ac) + ' ' + str(acrylic))

    
    #create the background for the app.
    #the app where all the widgets will
    #be is a top level window that will
    #move, resize, and minimize/maximize with
    #this window.
    
    appBG = Tk()
    AppBG = appBG
    #this geometry method wont
    #change anything yet
    #Dont change this one
    #change the one after this one
    appBG.geometry('0x0+0+0')
    appBG.config(bg='#000000')
    appBG.update()
    #make the background blury.
    
    hWND = windll.user32.GetParent(appBG.winfo_id())
    blur(hWND, '#010101', Ac, Dm)

    def updateBlur(self):
        hWND = windll.user32.GetParent(AppBG.winfo_id())
        blur(hWND, '#010101', Ac, self.Dm)

    #change the geometry here
    #I dont know why but I
    #have to change it here or
    #if dark mode is enabled and
    #I dont do this it does wierd things
    #SO CHANGE IT HERE!
    appBG.geometry(str(w) + 'x' + str(h) + '+' + str(px) + '+' + str(py))
    
    appBG.update()

    #make the toplevel app window where all the widgets will go.
    app = Toplevel(appBG, background=Bg)
    App = app
    #set the geometry to the sane as the background
    #window dont change this at all
    app.geometry(str(appBG.winfo_width()+0) + 'x' + str(appBG.winfo_height()) + '+' + str(appBG.winfo_x()+8) + '+' + str(appBG.winfo_y()+31))
    #remove the title bar for the app window
    app.overrideredirect(True)
    app.update()

    #move the app window with the background window.
    def PairWindows(x):
        global App
        global AppBG
        App.geometry(str(AppBG.winfo_width()+0) + 'x' + str(AppBG.winfo_height()) + '+' + str(AppBG.winfo_x()+8) + '+' + str(AppBG.winfo_y()+31))
        App.update()
    #this handles when the window is un minimized
    def OnMouseEnter(x):
        global App
        App.wm_attributes('-topmost', True)
        App.wm_attributes('-topmost', False)
    def OnMouseExit(x):
        global App
        App.wm_attributes('-topmost', False)

    def Show(x):
        App.wm_deiconify()
    def Hide(x):
        App.wm_withdraw()
        
    def update(self):
        App.update()
        AppBG.update()
        self.updateBlur()
        AppBG.geometry(str(w) + 'x' + str(h) + '+' + str(px) + '+' + str(py))
        App.config(bg=Bg)



    atk = App

    #bind the functions
    app.attributes('-transparentcolor', '#010101')
    appBG.bind("<Configure>", PairWindows)
    appBG.bind("<Enter>", OnMouseEnter)
    appBG.bind("<Leave>", OnMouseExit)
    appBG.bind("<Map>", Show)
    appBG.bind("<Unmap>", Hide)
    