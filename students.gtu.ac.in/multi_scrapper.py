# import dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageCms, ImageFilter
import numpy as np
import pytesseract
import cv2
import time

# initiate webdriver and configure options
co = webdriver.ChromeOptions()
co.headless = True # for headless window (not visible in desktop)
co.add_argument("--incognito") # for incognito mode

# initiate chromedriver service by defining path (Choose chromedriver according to your chrome version)
ser = Service("G:\\My Drive\\projects\\captcha_solver\\chromedriver.exe")
driver = webdriver.Chrome(service=ser,options=co) # start webdriver

# define url and filename for download captcha_temp
URL = "https://www.students.gtu.ac.in/"
path="cap.jpg"

## Helper Functions

def step1():
	# open webpage
	driver.get(URL)

	# save captcha
	imdata = driver.find_element(By.ID,"imgCaptcha")
	with open(path, 'wb') as file:
	    file.write(imdata.screenshot_as_png)

def step2():
	# convert to inverted mask and save img_temp
	im = cv2.imread(path)
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
	horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
	Mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,horizontal_kernel, iterations=2)
	#Mask = cv2.bitwise_not(Mask)
	cv2.imwrite("old.png", Mask)

	# open img_temp and reinvert mask
	img = Image.open("old.png")
	img = img.convert("RGBA")
	datas = img.getdata()
	newData = []
	for item in datas:
	    if item[0] == 0 and item[1] == 0 and item[2] == 0:
	        newData.append((255, 255, 255, 0))
	    else:
	        newData.append(item)
	img.putdata(newData)

	# paste mask on img and save new_temp_img
	background = Image.open(path)
	background = background.convert("RGBA")
	background.paste(img,mask=img)
	background.save("new.png","PNG")

def step3(im):
	im = Image.open(im) # open last saved img
	im = im.crop((5,5,115,35)) # crop it
	# conver image to extractable form elements (deffer captcha styles)
	rgb = ImageCms.createProfile(colorSpace='sRGB')
	lab = ImageCms.createProfile(colorSpace='LAB')
	transform = ImageCms.buildTransform(inputProfile=rgb, outputProfile=lab, inMode='RGB', outMode='LAB')
	lab_im = ImageCms.applyTransform(im=im, transform=transform)
	l, a, b = lab_im.split()
	im=l # select an element which is most extractable
	im = im.filter(ImageFilter.MinFilter(3)) # filter it
	result = pytesseract.image_to_string(im) # send it to ocr and save results to a variable
	l=[]
	l.append(result.strip())
	if l[0]==" " or l[0]=="" : # if result will be empty then it will do above steps again untill it gets the result
		step1()
		step2()
		l[0]=step3("new.png")
	return l[0] # return final result (maybe right or wrong)

def step4(enroll,fname):
	# site automation 
	enr = driver.find_element(By.ID,"txtEnrollNo") # get enrollment no. text box
	captex = driver.find_element(By.ID,"CodeNumberTextBox") # get captcha text box
	enr.send_keys(enroll) # send (type) given enrollment number to text box
	captex.send_keys(ans) # send (type) extracted captcha text to text box
	captex.send_keys(Keys.RETURN) # return (ENTER)
	# resize the page for full view
	S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
	driver.set_window_size(S('Width'),S('Height'))                                                                                                              
	driver.find_element(By.TAG_NAME,"body").screenshot(fname) # take a screenshot and save it to given filename

# main driver programm
# just a loop through different enrollment numbers
# you can provide a list of specific numbers too like l=[13,54,66,46]
for i in range(31,33+1): # 31 to 33 (for demo purpose only 3 enrollments taken)
	enroll = "1902801110{}".format(i)
	fname = "./outputs/1902801110{}.png".format(i)
	step1()
	step2()
	ans=step3("new.png")
	step4(enroll,fname)

driver.close() # close the window
driver.quit() # stop the driver