#coding:utf-8

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.font# text size in pixel
import pygetwindow as gw
import time
import threading #Update the connection status of the printer 
import os
import serial #connection arduino 
import subprocess # Processing 
import pathlib #path extension
import shutil # copy fichier
from reportlab.pdfgen.canvas import Canvas # Creation de pdf
from reportlab.lib.pagesizes import A4, A3, landscape, portrait #dimension page
from tkinter.filedialog import askopenfilename # permet ouverture application
#Backend 
from pathlib import Path
from pdf2image import convert_from_path
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces


#Define
BG= "SkyBlue2" 
TEXT = "White"
BUTTON = "SteelBlue3"  # In the end not used
A4PAPERW = 2480
A4PAPERH = 3508

port = input("Port machine (COMX) : ")

s=serial.Serial(port, 115200)

#Envoi machine 

def Gcode_to_printer():
    """
    Simple g-code streaming script for grbl

    Provided as an illustration of the basic communication interface
    for grbl. When grbl has finished parsing the g-code block, it will
    return an 'ok' or 'error' response. When the planner buffer is full,
    grbl will not send a response until the planner buffer clears space.

    G02/03 arcs are special exceptions, where they inject short line 
    segments directly into the planner. So there may not be a response 
    from grbl for the duration of the arc.

    ---------------------
    The MIT License (MIT)

    Copyright (c) 2012 Sungeun K. Jeon

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    ---------------------
    """
    # Open g-code file
    f = open(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\Gcode.gcode",'r')

    # Wake up grbl
    s.write(b"\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize 
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in f:
        l = line.strip() # Strip all EOL characters for consistency
        print ('Sending: ' + l)
        s.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        print (' : ' + grbl_out.strip().decode())

    # Wait here until grbl is finished to close serial port and file.
    #raw=input("  Press <Enter> to exit and disable grbl.") 

    # Close file and serial port
    f.close()

#Traductions fichier 

def PDF_to_PNG(): 
    image = convert_from_path(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf", poppler_path=r"C:\Python\poppler-24.08.0\Library\bin")
    image[0].save(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PNG.png", 'PNG')

def PNG_to_PNM ():
    #cmd= r"cd C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode && magick PNG.png PNM.pnm "
    cmd = r"magick PNG.png PNM.pnm"
    subprocess.run(cmd, check=True, cwd =r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode")

def PNM_to_SVG ():
    #cmd = r"cd C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode && C:\Python\Protace\protace.exe PNM.pnm -s -o SVG.svg "
    cmd = r"C:\Python\Protace\potrace.exe PNM.pnm -s -o SVG.svg"
    #cwd=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode"
    translation = subprocess.run(cmd,shell=True, capture_output=True, check=True, text=True, cwd=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode")

def SVG_to_gcode():
    curves = parse_file(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\SVG.svg")
    compiler = Compiler(interfaces.Gcode, 0.1, 0.1, 1)
    compiler.append_curves(curves)
    compiler.compile_to_file(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\Gcode.gcode")


def Openfiles(root): 
    file=askopenfilename(filetypes=[('Documents','*')])
    #os.system('"%s"' % file) #Openning the file
 
    # GRBL 
    extension = pathlib.Path(file).suffix
    print(extension)

    if extension==".gcode": 
        shutil.copy(file, r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\Gcode.gcode")
        #sent machine
        Gcode_to_printer()
    elif extension==".svg":
        shutil.copy(file, r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\SVG.svg")
        SVG_to_gcode()
        #sent machine
        Gcode_to_printer()
    elif extension==".pnm":
        shutil.copy(file, r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PNM.pnm")
        PNM_to_SVG()
        SVG_to_gcode()
        #sent machine
        Gcode_to_printer()
    elif extension==".png":
        shutil.copy(file, r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PNG.png")
        PNG_to_PNM()
        PNM_to_SVG()
        SVG_to_gcode()
        #Sent machine
        Gcode_to_printer()
    elif extension==".pdf":
        shutil.copy(file, r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf")
        PDF_to_PNG()
        PNG_to_PNM()
        PNM_to_SVG()
        SVG_to_gcode()
        print("PDF")
        #Sent to machine
        Gcode_to_printer
    else : 
        file = "Extension de fichier non accépté"
    
        #Printing 
    File = Label(root, text = file, bg=BG, foreground='white')
    File.place(x=500, y=700, anchor="center")

def WindowBanner(root, width, imgRet, imgBanner):
    #Banner
    ImageB = Label(root, image=imgBanner, bd=0)
    ImageB.place(x=width/2, y=110, anchor='center')

    #Retour
    Retour=Button(root, image = imgRet, activebackground=BG, bd=0, bg= BG, command= lambda :[root.destroy(), Window1()])
    Retour.place(x=0, y=0)

    if s.is_open : 
        text = "- Imprimante connéctée -"
        color = "White"
    else : 
        text = "- Imprimante déconnéctée -"
        color = "red"

    Status = Label(root, text = text, bg=BG, foreground = color)
    Status.place(x=width/2, y=20, anchor= 'center')

def Doc():
    WindowDoc = Tk()
    width = WindowDoc.winfo_screenwidth()
    height = WindowDoc.winfo_screenheight()
    WindowDoc.geometry("%dx%d" % (width, height))
    WindowDoc.title("Machine that draws - Document")
    WindowDoc.config(bg=BG)

    # Ne fonctionne pas autrement
    imgBanner = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Telechargement.gif")
    imgFiles = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Fichier.gif")
    imgRet = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Retour.gif")
    time.sleep(2)

    #Fichier
    Fichier = Button (WindowDoc, image=imgFiles, bd=0, bg=BG, activebackground=BG, command=lambda :[Openfiles(WindowDoc)])
    Fichier.place(x=width/2, y=height/2, anchor= "center")

    #Status
    #WindowBanner(WindowDoc, width, imgRet)
    Banner = threading.Thread(target = WindowBanner(WindowDoc, width, imgRet, imgBanner), daemon=True) #Suppose to update status... Not working 
    Banner.start()

    WindowDoc.mainloop()

def PDF_Rectangle2(canvas, position, alignement, WidthR, HeightR, width, height): 
    if alignement =='Center': 
        x= int(width/2)-int(int(WidthR)/2)
    elif alignement == 'Right': 
        x= width-WidthR-30
    else : 
        x=30 #Margins
    print (x)
    if position =='Middle': 
        y= int(height/2)-int(int(HeightR)/2)
    elif position == 'Bottom': 
        y=30
    else : 
        y = height - HeightR -30 # 30 = margins
    print (y)
    canvas.rect(x, y, WidthR, HeightR)
    canvas.save()
    PDF_to_PNG()
    PNG_to_PNM()
    PNM_to_SVG()
    SVG_to_gcode() 
    Gcode_to_printer()

def PDF_Rectangle(WindowText, orientation, size, PositionRect, AlignRect, sizeW, sizeH):

    #PDF 
    #folder = "PDFs_Rectangle"
    #os.makedirs(folder, exist_ok=True)
    #filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"  # Custom name for the files, diffrent anytime
    #path = os.path.join(folder, filename)
    path = r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf"
    print(path)
    Ortt=orientation.get()
    sz = size.get()
    print(Ortt, sz)
    if Ortt== 'landscape' : 
        if sz == 'A3':
            canvas = Canvas(path, pagesize=landscape(A3))
            print("Landscape A3")
        else : 
            canvas = Canvas(path, pagesize=landscape(A4))
            print("Landscape A4")
    else : 
        if sz == 'A3': 
            canvas = Canvas(path, pagesize=portrait(A3))
            print ("portrait A3")
        else : 
            canvas = Canvas(path, pagesize=portrait(A4))
            print ("Portrait A4")
    width, height = canvas._pagesize # page dimensions

    position= PositionRect.get()
    alignement = AlignRect.get()
    WidthR = int(sizeW.get())
    HeightR = int(sizeH.get())
    if int(WidthR)>int(width-20) or int(HeightR)>int(height-20) : 
        text = "Dimensions trop grande"
        color = "Red"
    else : 
        PDF_Rectangle2(canvas, position, alignement, WidthR, HeightR, width, height)
        text = "Sauvegarde du PDF"
        color = "white"
    
    Err = Label(WindowText, text = text, font=('Helvetica', 7, 'bold'), foreground=color, background=BG)
    Err.place(x=1000, y=550, anchor='center')

def PDF_Circle2(canvas, position, alignement, size, width, height): 
    if alignement == 'Center': 
        x= width/2
    elif alignement=='Right':
        x= width-size-30
    else : 
        x= 30+size

    if position == 'Middle': 
        y= height/2
    elif position == 'Bottom': 
        y= size +30
    else : 
        y= height -size -30

    canvas.circle(x, y, size, fill=0)
    canvas.save()
    PDF_to_PNG()
    PNG_to_PNM()
    PNM_to_SVG()
    SVG_to_gcode() 
    Gcode_to_printer()

def PDF_Circle(Windowtext, orientation, size, PositionCir, AlignCir, sizeC):
    #PDF 
    #folder = "PDFs_Circle"
    #os.makedirs(folder , exist_ok=True)
    #filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"  # Custom name for the files, diffrent anytime
    #path = os.path.join(folder, filename)
    path = r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf"
    Ortt=orientation.get()
    sz = size.get()
    if Ortt== 'landscape' : 
        if sz == 'A3':
            canvas = Canvas(path, pagesize=landscape(A3))
        else : 
            canvas = Canvas(path, pagesize=landscape(A4))
    else : 
        if sz == 'A3': 
            canvas = Canvas(path, pagesize=portrait(A3))
        else : 
            canvas = Canvas(path, pagesize=portrait(A4))
    width, height = canvas._pagesize # page dimensions

    position = PositionCir.get()
    alignement = AlignCir.get()
    size= int(sizeC.get())

    if size > ((int(width)/2)-20) or size>((int(height)/2)-20):
        text = "Dimensions trop grande"
        color = 'red'
    else : 
        PDF_Circle2(canvas, position, alignement, size, width, height)
        text = "Sauvegarde du PDF"
        color = 'white'
    Err = Label(Windowtext, text = text, font =('Helvetia', 7), foreground=color, background=BG)
    Err.place(x= 1000, y=650, anchor='center')

def PDF_Line2(canvas, position, alignement, orientation, size, width, height):
    print (position, alignement)
    if orientation =='Verticale':
        if alignement == 'Center': 
            x= width/2
        elif alignement=='Right': 
            x= width-30
        else : 
            x=30
        
        if position == 'Middle': 
            y= (height/2)-(size/2)
        elif alignement=='Bottom': 
            y= 30
        else : 
            y=height-30-size
        
        canvas.line(x, y, x, y+size)
    
    else : 
        if alignement == 'Center': 
            x= (width/2)-(size/2)
        elif alignement == 'Right' :
            x=width-30-size
        else : 
            x=30

        if position == 'Middle': 
            y = int(height/2)
        elif position == 'Bottom' :
            y = 30
        else : 
            y = height-30
        print (x, y)
        canvas.line(x, y, x+int(size), y)
     
    canvas.save()
    PDF_to_PNG()
    PNG_to_PNM()
    PNM_to_SVG()
    SVG_to_gcode() 
    Gcode_to_printer()

def PDF_Line(WindowText, orientation, size, PositionLine, AlignLine, OrientaLine, Lenght):
    #PDF 
    #folder = "PDFs_Line"
    #os.makedirs(folder , exist_ok=True)
    #filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"  # Custom name for the files, diffrent anytime
    #path = os.path.join(folder, filename)
    path = r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf"
    Ortt=orientation.get()
    sz = size.get()
    if Ortt== 'landscape' : 
        if sz == 'A3':
            canvas = Canvas(path, pagesize=landscape(A3))
        else : 
            canvas = Canvas(path, pagesize=landscape(A4))
    else : 
        if sz == 'A3': 
            canvas = Canvas(path, pagesize=portrait(A3))
        else : 
            canvas = Canvas(path, pagesize=portrait(A4))
    width, height = canvas._pagesize # page dimensions
    print(width, height)

    position = PositionLine.get()
    alignement = AlignLine.get()
    orientation = OrientaLine.get()
    size = int(Lenght.get())

    if (orientation == 'Horizontale' and size > (width-40)) or (orientation=='Verticale' and size > (height-40)):
        text = "Dimensions trop grande"
        color = 'red'
    else : 
        PDF_Line2(canvas, position, alignement, orientation, size, width, height)
        text = "Sauvegarde du PDF"
        color = 'white'

    Err = Label(WindowText, text = text, font =("Helvetia", 7, 'bold'), foreground=color, background= BG)
    Err.place(x=1000, y= 750, anchor='center') 

def PDF2(NbrLine, text, alignement, position, height, width, canvas, text_width, Size):
    #Nombre de pixel par ligne 
    lineLenght = int(text_width/NbrLine) #Nombre de points par ligne
    if text_width%NbrLine !=0: 
        lineLenght+=1
    print ("lineLenght : ", lineLenght)
    CLenght= text_width/len(text) # dimension en points d'un caractère (en moyenne)
    print ("CLenght : ", CLenght)
    CLine = lineLenght/CLenght # Nombres de caractère par ligne
    print("Cline : ", CLine)
    strlen = len (text) # Nombre de caractère dans le texte
    print (strlen)

    LineText = [] #tableau des différentes lignes à ajouter 
    v=0
    linetot=0
    
    # tant que tout les caractères du texte ne sont pas traité
    for v in range (strlen):
        if (v-linetot)== int(CLine) : 
            LineText.append(text[linetot : v]) # enregistre ligne 
            linetot = v #Update overall position
        v+=v # Passe au caractère suivant 
    LineText.append(text[linetot:strlen]) #Derniére ligne du text 
    i=0
    print(LineText)
    
    if alignement == 'Center' :  # A OPTIMISER --------------------------------------------------------------------------------------------------
        #POSITION
        if position == 'Middle': 
            TextHeight = NbrLine*Size # Hauteur en point du texte
            MiddlePage = height/2
            MiddleText = TextHeight/2
            YText = (MiddlePage-MiddleText) # position en Y de la première ligne
            for i in range(NbrLine):
                canvas.drawCentredString(width/2, (YText+i*Size), LineText[NbrLine-i-1])
                print((YText+i*Size))
        elif position == 'Bottom':
            YText= 30+Size 
            for i in range(NbrLine):
                print("i", NbrLine-i-1)
                canvas.drawCentredString(width/2, (YText+i*Size), LineText[NbrLine-i-1])
        else : #Default settings 
            YText= height -30 -Size #Height - margins -Size
            print (YText)
            for i in range (NbrLine): 
                print (i)
                print(LineText[i])
                canvas.drawCentredString(width/2, (YText-i*Size), LineText[i])
                print(YText+i*Size)

    elif alignement == 'Right': 
        if position =='Middle': 
            TextHeight= NbrLine*Size
            YText= ((height/2)-(TextHeight/2))
            for i in range(NbrLine) : 
                canvas.drawRightString(width-30, YText+i*Size, LineText[NbrLine-i-1])
        elif position == 'Bottom': 
            YText= 30+Size
            for i in range(NbrLine): 
                canvas.drawRightString(width-30, YText+i*Size, LineText[NbrLine-i-1])
        else : #Defaults
            YText = height-30-Size
            for i in range(NbrLine): 
                canvas.drawRightString(width-30, YText-i*Size, LineText[i])

    else : 
        if position=='Middle': 
            TextHeight= NbrLine*Size
            YText= ((height/2)-(TextHeight/2))
            for i in range(NbrLine): 
                canvas.drawString(30, YText+i*Size, LineText[NbrLine-i-1])
        elif position=='Bottom': 
            YText= 30+Size
            for i in range(NbrLine):
                canvas.drawString(30, YText+i*Size, LineText[NbrLine-i-1])
        else : #Default
            YText= height-30-Size
            for i in range(NbrLine): 
                canvas.drawString(30, YText-i*Size, LineText[i])
    
    canvas.save()
    PDF_to_PNG()
    PNG_to_PNM()
    PNM_to_SVG()
    SVG_to_gcode()    
    Gcode_to_printer()

def PDF(WindowText, orientation, size, textPhrase, combobox, Align, Position, Font): # Crée le PDF 
    #PDF 
    #folder = "PDFs"
    #os.makedirs(folder , exist_ok=True)
    #filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"  # Custom name for the files, diffrent anytime
    #path = os.path.join(folder, filename)
    path = r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\PDF.pdf"
    Ortt=orientation.get()
    sz = size.get()
    if Ortt== 'landscape' : 
        if sz == 'A3':
            height, width = A3
            canvas = Canvas(path, pagesize=landscape(A3))
        else : 
            height, width = A4
            canvas = Canvas(path, pagesize=landscape(A4))
    else : 
        if sz == 'A3': 
            width, height = A3
            canvas = Canvas(path, pagesize=portrait(A3))
        else : 
            width, height = A4 #dimension de la page en fonction de la taille et de l'orientation (A SUPPRIMER)
            canvas = Canvas(path, pagesize=portrait(A4))
    width, height = canvas._pagesize
    print (width, height)

    text = textPhrase.get()
    Size = float(combobox.get())
    alignement = Align.get()
    position = Position.get()
    font = str(Font.get())
    
    canvas.setFont(font, Size) #Font variable and position 
    text_width=canvas.stringWidth(text, font, Size) #Longueur du texte en points

    # Nombre de ligne en points
    print(text_width)
    NbrLine =int(text_width/(int(width)-2)) 
    print(NbrLine)
    if text_width%(width-2) != 0 : 
        NbrLine = NbrLine+1
        print ("Adding one")
    print(NbrLine)

    
    if Size*NbrLine >height : 
        text = "Texte trop long"
        color = 'red'
    else : 
        PDF2(NbrLine, text, alignement, position, height, width, canvas, text_width, Size)
        text = "Sauvegarde du PDF"
        color = "white"
    

    SaEr = Label(WindowText, text = text, font= ("Helvetica", 6, "bold"), foreground= color, background=BG)
    SaEr.place(x=1100, y=450, anchor='center')    
    
def text_1(WindowText, orientation, size, imgText, imgRect, imgCercle, imgline): # Récupère les infos à ecrire sur le PDF 
    height = WindowText.winfo_screenheight()
    width = WindowText.winfo_screenwidth()

    #Text

    imageText= Label(WindowText, image=imgText, bd=0, bg=BG)
    imageText.place(x=width/2, y=300, anchor='center')

    textPhrase = Entry(WindowText, width=150, bd=0)
    textPhrase.place(x=600, y=275, anchor='center')

    n=StringVar() #Pixel
    combobox = ttk.Combobox(WindowText, width= 15, textvariable= n) # Definitly a way to do that quicker
    combobox['values'] = ('10', '13', '16', '19', '22', '25', '28', '31', '34', '37', '40', '43', '46', '49', '52', '55', '58', '61', '64', '67', '70', '73', '76', '79', '82', '85', '88', '91', '94', '97', '100')
    combobox.place(x=200, y=310, anchor="center")

        #Alignement 
    m=StringVar() 
    Align = ttk.Combobox(WindowText, width= 30, textvariable=m)
    Align ['values'] = ('Center', 'Right', 'Left')
    Align.place(x=450, y=310, anchor='center')

        #Position 
    w=StringVar()
    Position = ttk.Combobox(WindowText, width=30, textvariable=w)
    Position['values'] = ('Top', 'Middle', 'Bottom')
    Position.place(x= 700, y=310, anchor='center')
    
        #Font 
    x=StringVar()
    Font = ttk.Combobox(WindowText, width=30, textvariable=x )
    Font ['values'] = ('Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman')
    Font.place (x=900, y= 310, anchor='center')


    # IMPRESSION 
    Print = Button (WindowText, text = 'Print', bg= BUTTON, activebackground= "white", bd=0, command= lambda :[PDF(WindowText, orientation, size, textPhrase, combobox, Align, Position, Font)])
    Print.place(x=1100, y= 310 , anchor='center')
    

    #Rectangle

    imageRect= Label(WindowText, image=imgRect, bd=0, bg=BG)
    imageRect.place(x=width/2, y=450, anchor='center')

    p=StringVar()
    PositionRect = ttk.Combobox(WindowText, width=30, textvariable=p)
    PositionRect['values']=('Top', 'Middle', 'Bottom')
    PositionRect.place(x=200, y=4500, anchor='center')

    a=StringVar()
    AlignRect = ttk.Combobox(WindowText, width=30, textvariable=a)
    AlignRect['values']=('Center', 'Right', 'Left')
    AlignRect.place(x=450, y=450, anchor='center')

    sizeW= Entry(WindowText, width=20, bd=0)
    sizeW.place(x=650, y=450, anchor='center')

    sizeH = Entry(WindowText, width=20, bd=0)
    sizeH.place(x=800, y=450, anchor='center')

    Rectangle=Button(WindowText, text = 'Rectangle', bg=BUTTON, activebackground="white", bd=0, command=lambda:[PDF_Rectangle(WindowText, orientation, size, PositionRect, AlignRect, sizeW, sizeH)])
    Rectangle.place(x=1000, y=450, anchor='center')

    
    #CERCLE

    imageCercle= Label(WindowText, image=imgCercle, bd=0, bg=BG)
    imageCercle.place(x=width/2, y=570, anchor='center')

    y=StringVar()
    PositionCir =ttk.Combobox(WindowText, width=30, textvariable=y)
    PositionCir['values']=('Top', 'Middle', 'Bottom')
    PositionCir.place (x=300, y=570, anchor='center')

    z=StringVar()
    AlignCir=ttk.Combobox(WindowText, width=30, textvariable=z)
    AlignCir['values']=('Center', 'Right', 'Left')
    AlignCir.place(x=550, y=570, anchor='center')

    sizeC = Entry(WindowText, width=40, bd=0)
    sizeC.place(x=800, y=570, anchor='center')

    Circle=Button(WindowText, text = 'Cercle', bg=BUTTON, activebackground='white', bd=0, command=lambda :[PDF_Circle(WindowText, orientation, size, PositionCir, AlignCir, sizeC)])
    Circle.place(x=1000, y=570, anchor='cente')


    #Line

    imageLine= Label(WindowText, image=imgline, bd=0, bg=BG)
    imageLine.place(x=width/2, y=height-100, anchor='center')

    lx=StringVar()
    PositionLine = ttk.Combobox(WindowText, width=30, textvariable=lx)
    PositionLine['values']=('Top', 'Middle', 'Bottom')
    PositionLine.place(x=270, y=700, anchor='center')

    ly=StringVar()
    AlignLine= ttk.Combobox(WindowText, width=20, textvariable=ly)
    AlignLine['values']=('Center', 'Right', 'Left')
    AlignLine.place(x=520, y=700, anchor='center')
    
    lL= StringVar()
    OrientaLine = ttk.Combobox(WindowText, width = 20, textvariable=lL)
    OrientaLine['values']= ('Horizontale', 'Verticale')
    OrientaLine.place(x=720, y= 700, anchor='center')

    Lenght= Entry(WindowText, width=10, bd=0)
    Lenght.place(x=920, y=700, anchor='center')

    Line= Button(WindowText, text = 'Line', bg=BUTTON, activebackground='white', bd=0, command=lambda:[PDF_Line(WindowText, orientation, size, PositionLine, AlignLine, OrientaLine, Lenght)])
    Line.place(x=1020, y=700, anchor='center') 
    
def text():
    WindowText = Tk()
    height = WindowText.winfo_screenheight()
    width = WindowText.winfo_screenwidth()
    WindowText.geometry("%dx%d" %(width, height))
    WindowText.title ("Machine that draws - Texte")
    WindowText.config(bg=BG)

    #Banner
    Banner = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Ecrire.gif")
    imgRet = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Retour.gif") #Else not working 
    imgOK = PhotoImage(file= r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\OK.gif")
    imgText= PhotoImage(file= r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Paragraph_texte.gif")
    imgRect= PhotoImage(file= r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Paragraph_rectangle.gif")
    imgCercle = PhotoImage(file= r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Paragraph_cercle.gif")
    imgline = PhotoImage(file= r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Paragraph_line.gif")
    WindowBanner(WindowText, width, imgRet, Banner)

    #Dimensions
    dimension = Label(WindowText, text = "Dimension", background=BG, foreground=TEXT, font=("Helvetica", 12, "bold"))
    dimension.place(x=80, y=150, anchor='center')

    #Page 
    s=StringVar()
    size = ttk.Combobox(WindowText, width =10, textvariable=s)
    size['values'] = ('A4', 'A3')
    size.place(x= 180, y= 150, anchor='center')

    o=StringVar()
    orientation = ttk.Combobox(WindowText, width = 20, textvariable=o)
    orientation['values'] = ('landscape', 'portrait')
    orientation.place(x=330, y=150, anchor='center') 

    #OK
    ok = Button(WindowText, image= imgOK, bg=BG, activebackground=BG, bd=0, command= lambda : [text_1(WindowText, orientation, size, imgText, imgRect, imgCercle, imgline)])
    ok.place (x= 430, y=150, anchor='center')

    WindowText.mainloop()

def processing_to_gcode(GcodeEntry): 
    Gcode = GcodeEntry.get()
    file = open(r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\Gcode.gcode", "w")
    #with open("C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Doc_to_gcode\Gcode.gcode", "w") as file:
    file.write(Gcode)
    Gcode_to_printer()

def processing(): 
    WindowProc = Tk()
    height = WindowProc.winfo_screenheight()
    width = WindowProc.winfo_screenwidth()
    WindowProc.geometry("%dx%d" %(width, height))
    WindowProc.title("Machine that draws - Processing")
    WindowProc.config(bg=BG)

    #Banner 
    imgBanner = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Processing.gif")
    imgRet = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Retour.gif")
    WindowBanner(WindowProc, width, imgRet, imgBanner)

    #Processing 
    os.startfile(r'C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Processing to Gcode\scaffold.pde')

    #Data
    GcodeEntry = Entry(WindowProc, width = 50)
    GcodeEntry.place(x=1000, y= height/2, anchor='center')
    GcodeEntry.focus_set()

    Ok = PhotoImage(file =r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\OK.gif")
    ok= Button(WindowProc, image = Ok, bd= 0, bg=BG)
    ok.place(x=1000, y=height/2+50, anchor='center')

    #Help button 

    WindowProc.mainloop()

def Choices(WindowOne, imgDoc, imgText, imgProc): 
    width = WindowOne.winfo_screenwidth()

    #Button Document
    BtDoc=Button(WindowOne, image=imgDoc, bg=BG, activebackground=BG, bd=0, command=lambda :[WindowOne.destroy(), Doc()])
    BtDoc.place(x=width/5, y=600, anchor= 'center')

    #Button Text
    BtText = Button(WindowOne, image= imgText, bg=BG, activebackground=BG, bd=0, command= lambda:[WindowOne.destroy(), text()])
    BtText.place(x=width/2, y=600, anchor='center')

    #Button Processing 
    BtProcessing= Button(WindowOne, image = imgProc, bg=BG, activebackground= BG, bd=0, command=lambda:[WindowOne.destroy(), processing()])
    BtProcessing.place(x=width * 4/5, y= 600, anchor="center")

def connectArduino(WindowOne, imgDoc, imgText, imgProc):
    # Wake up grbl
    #s.write("\r\n\r\n") # mess up everything ...
    time.sleep(2)   # Wait for grbl to initialize 
    s.flushInput()  # Flush startup text in serial input

        # Variable text
    if s.is_open:           # Connection 
        text= "Connectée"
        color = "White"
        Choices(WindowOne, imgDoc, imgText, imgProc)
    else : 
        text= "Erreur de connection"
        color= "red"
    # Message status
    Status=Label(WindowOne, text= text, foreground=color, background=BG)
    Status.place(x=700, y=435, width=200, anchor= "center")

def Window1():
    WindowOne = Tk()
            #Dimension fenêtre
    height = WindowOne.winfo_screenheight()
    width = WindowOne.winfo_screenwidth()
    WindowOne.geometry("%dx%d" %(width, height))
    WindowOne.title("Machine that draws")
    WindowOne.configure(bg=BG)

        #Image button_choices (ne fonctionne pas autrement)
    imgDoc = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Btt_Document.gif")
    imgText = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Btt_Texte.gif")
    imgProc = PhotoImage(file = r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Btt_Processing.gif")

        #Texte
    imgBienvenue = PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Bienvenue.gif")
    imageBienvenue=Label(WindowOne, image=imgBienvenue, borderwidth=0)
    imageBienvenue.place(x=width/2, y=225, anchor="center")
        
        #   bouton 1
    connection=PhotoImage(file=r"C:\Users\cpier\OneDrive\Documents\Arduino\Program_Arduino\ProjetMakerSpace\Inteface\Connexion.gif")
    buttonChoice1=Button(WindowOne, image=connection, bd=0, bg=BG, activebackground= BG, command= lambda :[connectArduino(WindowOne, imgDoc, imgText, imgProc)]) # or activebackground=BG
    buttonChoice1.place(x=width/2+50, y=400, anchor="center")


    WindowOne.mainloop()
    
Window1()

    # FERMETURE PORT
s.close()