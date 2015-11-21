from xml.dom import minidom
from PIL import Image, ImageDraw
import random
import os
import time
import math

class Hama:

	def __init__(self,code,r,g,b):
		self.code = code
		self.red = r
		self.green = g
		self.blue = b

colorchartRGB = []
colorchartLab = []
nbead = 0

def RGBtoXYZ(r,g,b):

	conv = []

	var_R = (r/255)
	var_G = (g/255)
	var_B = (b/255)

	if (var_R > 0.04045): var_R = math.pow(((var_R + 0.055)/1.055),2.4)
	else: var_R = var_R / 12.92
	if (var_G > 0.04045): var_G = math.pow(((var_G + 0.055)/1.055),2.4)
	else: var_G = var_G / 12.92
	if (var_B > 0.04045): var_B = math.pow(((var_B + 0.055)/1.055),2.4)
	else: var_B = var_B / 12.92

	var_R = var_R * 100
	var_G = var_G * 100
	var_B = var_B * 100

	#Observer. = 2°, Illuminant = D65
	x = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
	y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
	z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

	conv.append(x)
	conv.append(y)
	conv.append(z)

	return conv

def XYZtoCIEL(x,y,z):

	ref_X =  95.047   #Observer= 2°, Illuminant= D65
	ref_Y = 100.000
	ref_Z = 108.883

	conv = []

	var_X = x / ref_X
	var_Y = y / ref_Y
	var_Z = z / ref_Z

	if (var_X > 0.008856): var_X = math.pow(var_X,(1/3))
	else: var_X = (7.787 * var_X) + (16 / 116)
	if (var_Y > 0.008856): var_Y = math.pow(var_Y,(1/3))
	else: var_Y = (7.787 * var_Y) + (16 / 116)
	if (var_Z > 0.008856): var_Z = math.pow(var_Z,(1/3))
	else: var_Z = (7.787 * var_Z) + (16 / 116)

	l = ( 116 * var_Y ) - 16
	a = 500 * ( var_X - var_Y )
	b = 200 * ( var_Y - var_Z )

	conv.append(l)
	conv.append(a)
	conv.append(b)

	return conv

def deltaE(l1,a1,b1,l2,a2,b2):

	ab = (math.pow((l1-l2),2)+math.pow((a1-a2),2)+math.pow((b1-b2),2))
	delta = math.sqrt(ab)
	return delta


def bestMatch(r,g,b):

	mini = 5000 #Max(R+G+B+1)
	temp = []

	tempp1 = []
	tempp2 = []

	for x in range(0,nbead):
		code = colorchartLab[x].code
		L_chart = colorchartLab[x].red #valeur de L
		a_chart = colorchartLab[x].green #valeur de a
		b_chart = colorchartLab[x].blue #valeur de b

		tempp1 = RGBtoXYZ(r,g,b)
		tempp2 = XYZtoCIEL(tempp1[0],tempp1[1],tempp1[2])

		delta = deltaE(L_chart,a_chart,b_chart,tempp2[0],tempp2[1],tempp2[2])

		#print ("Mini : ",mini)
		#print ("Delta : ",delta)

		if delta < mini:
			mini = delta
			del(temp[:])
			temp.append(code)
			temp.append(colorchartRGB[x].red)
			temp.append(colorchartRGB[x].green)
			temp.append(colorchartRGB[x].blue)

	return temp


def createImage(op,res):

	debut = time.time()
	im = Image.open(op)
	rgb_im = im.convert('RGB')
	width,height = im.size

	result = []
	im_res = Image.new('RGB',(width,height))
	pixels = im_res.load()

	for y in range(0, height):
		for x in range(0, width):
			xy = (x,y)
			r,g,b = rgb_im.getpixel(xy)
			result = bestMatch(r,g,b)
			pixels[x,y] = (result[1],result[2],result[3])
			#print("R1 : %d | G1 : %d | B1 : %d" % (r,g,b))
			#print("R2 : %d | G2 : %d | B2 : %d" % (result[1],result[2],result[3]))

	im_res.save(res)
	fin = time.time()
	print("Image ",res," est crée en ",fin-debut," secondes")

def createImageBeads(op,resbead):

	debut = time.time()

	im = Image.open(op)
	rgb_im = im.convert('RGB')
	width,height = im.size

	size = 20
	sizeint = 10

	r_back = 245
	g_back = 245
	b_back = 245

	fwidth = width * (size+2)
	fheight = height * (size+2)

	result = []
	im_res = Image.new("RGB",(fwidth,fheight),(r_back,g_back,b_back))
	draw = ImageDraw.Draw(im_res)

	n = 0
	m = 0

	for y in range(0, height):
		for x in range(0, width):
			xy = (x,y)
			r,g,b = rgb_im.getpixel(xy)
			result = bestMatch(r,g,b)

			if result[1] + result[2] + result[3] >= 750:
				draw.ellipse((n,m,n+size,m+size),fill = (result[1],result[2],result[3]),outline =(200,200,200))
				draw.ellipse((n+5,m+5,n+sizeint+5,m+sizeint+5),fill = (r_back,g_back,b_back),outline =(200,200,200))
			else:
				draw.ellipse((n,m,n+size,m+size),fill = (result[1],result[2],result[3]))
				draw.ellipse((n+5,m+5,n+sizeint+5,m+sizeint+5),fill = (r_back,g_back,b_back),outline =(result[1],result[2],result[3]))
			n = n + (size+2)
		m = m + (size+2)
		n = 0

	del draw
	im_res.save(resbead)
	fin = time.time()
	print("Image ",resbead," est crée en ",fin-debut," secondes")


def importXML(filename):

	debut = time.time()

	doc = minidom.parse(filename)
	hamas = doc.getElementsByTagName("Hama")

	tempC1 = []
	tempC2 = []

	global nbead

	#print(type(hamas))

	#colorchart = [] #liste temporaire

	for hama in hamas:
		code = hama.getElementsByTagName("Code")[0].childNodes[0].nodeValue
		r_chart = int(hama.getElementsByTagName("R")[0].childNodes[0].nodeValue)
		g_chart = int(hama.getElementsByTagName("G")[0].childNodes[0].nodeValue)
		b_chart = int(hama.getElementsByTagName("B")[0].childNodes[0].nodeValue)
		#print("CODE : %s | R : %d | G : %d | B : %d" % (code,r_chart,g_chart,b_chart))

		tempC1 = RGBtoXYZ(r_chart,g_chart,b_chart)
		tempC2 = XYZtoCIEL(tempC1[0],tempC1[1],tempC1[2])

		bead = Hama(code,r_chart,g_chart,b_chart)
		bead2 = Hama(code,tempC2[0],tempC2[1],tempC2[2])

		"""print("CODE : %s | R : %d | G : %d | B : %d" % (bead.code,bead.red,bead.green,bead.blue))
		print("L : ",bead2.red," | a : ",bead2.green," | b : ",bead2.blue)"""

		colorchartRGB.append(bead)
		colorchartLab.append(bead2)
		nbead = nbead + 1

	fin = time.time()
	print("Le fichier XML est importé en ",fin-debut," secondes")

s = 'Daredevil'

op = ('images\%s.png' % (s))
res = ('images\%s_Res.png' % (s))
resbead = ('images\%s_ResBead.png' % (s))

importXML('colorchart2.xml')
createImage(op,res)
createImageBeads(op,resbead)
