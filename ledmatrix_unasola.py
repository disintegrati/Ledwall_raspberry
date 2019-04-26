# ledmatrix-scroll by Andrew Oakley www.aoakley.com Public Domain 2015-10-18
#
# Takes an image file (e.g. PNG) as command line argument and scrolls it
# across a grid of WS2811 addressable LEDs, repeated in a loop until CTRL-C
#
# Use a very wide image for good scrolling effect.
#
# If you have a low resolution matrix (like mine, 12x8 LEDs) then you will
# probably need to create your image height equal to your matrix height
# and draw lettering pixel by pixel (e..g in GIMP or mtpaint) if you want
# words or detail to be legible.

import time, sys, os, re
from neopixel import * # See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
from PIL import Image  # Use apt-get install python-imaging to install this

# LED strip configuration:
LED_COUNT      = 675      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 125     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Speed of movement, in seconds (recommend 0.1-0.3)
SPEED=0
# SPEED=0.08

# Size of your matrix
MATRIX_WIDTH=45
MATRIX_HEIGHT=15

# LED matrix layout
# A list converting LED string number to physical grid layout
# Start with top right and continue right then down
# For example, my string starts bottom right and has horizontal batons
# which loop on alternate rows.
#
# Mine ends at the top right here:     -----------\
# My last LED is number 95                        |
#                                      /----------/
#                                      |
#                                      \----------\
# The first LED is number 0                       |
# Mine starts at the bottom left here: -----------/ 

#myMatrix=[95,94,93,92,91,90,89,88,87,86,85,84,
#          72,73,74,75,76,77,78,79,80,81,82,83,
#          71,70,69,68,67,66,65,64,63,62,61,60,
#          48,49,50,51,52,53,54,55,56,57,58,59,
#          47,46,45,44,43,42,41,40,39,38,37,36,
#          24,25,26,27,28,29,30,31,32,33,34,35,
#          23,22,21,20,19,18,17,16,15,14,13,12,
#           0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11]


myMatrix=[
0,29,30,59,60,89,90,119,120,149,150,179,180,209,210,239,240,269,270,299,300,329,330,359,360,389,390,419,420,449,450,479,480,509,510,539,540,569,570,599,600,629,630,659,660,
1,28,31,58,61,88,91,118,121,148,151,178,181,208,211,238,241,268,271,298,301,328,331,358,361,388,391,418,421,448,451,478,481,508,511,538,541,568,571,598,601,628,631,658,661,
2,27,32,57,62,87,92,117,122,147,152,177,182,207,212,237,242,267,272,297,302,327,332,357,362,387,392,417,422,447,452,477,482,507,512,537,542,567,572,597,602,627,632,657,662,
3,26,33,56,63,86,93,116,123,146,153,176,183,206,213,236,243,266,273,296,303,326,333,356,363,386,393,416,423,446,453,476,483,506,513,536,543,566,573,596,603,626,633,656,663,
4,25,34,55,64,85,94,115,124,145,154,175,184,205,214,235,244,265,274,295,304,325,334,355,364,385,394,415,424,445,454,475,484,505,514,535,544,565,574,595,604,625,634,655,664,
5,24,35,54,65,84,95,114,125,144,155,174,185,204,215,234,245,264,275,294,305,324,335,354,365,384,395,414,425,444,455,474,485,504,515,534,545,564,575,594,605,624,635,654,665,
6,23,36,53,66,83,96,113,126,143,156,173,186,203,216,233,246,263,276,293,306,323,336,353,366,383,396,413,426,443,456,473,486,503,516,533,546,563,576,593,606,623,636,653,666,
7,22,37,52,67,82,97,112,127,142,157,172,187,202,217,232,247,262,277,292,307,322,337,352,367,382,397,412,427,442,457,472,487,502,517,532,547,562,577,592,607,622,637,652,667,
8,21,38,51,68,81,98,111,128,141,158,171,188,201,218,231,248,261,278,291,308,321,338,351,368,381,398,411,428,441,458,471,488,501,518,531,548,561,578,591,608,621,638,651,668,
9,20,39,50,69,80,99,110,129,140,159,170,189,200,219,230,249,260,279,290,309,320,339,350,369,380,399,410,429,440,459,470,489,500,519,530,549,560,579,590,609,620,639,650,669,
10,19,40,49,70,79,100,109,130,139,160,169,190,199,220,229,250,259,280,289,310,319,340,349,370,379,400,409,430,439,460,469,490,499,520,529,550,559,580,589,610,619,640,649,670,
11,18,41,48,71,78,101,108,131,138,161,168,191,198,221,228,251,258,281,288,311,318,341,348,371,378,401,408,431,438,461,468,491,498,521,528,551,558,581,588,611,618,641,648,671,
12,17,42,47,72,77,102,107,132,137,162,167,192,197,222,227,252,257,282,287,312,317,342,347,372,377,402,407,432,437,462,467,492,497,522,527,552,557,582,587,612,617,642,647,672,
13,16,43,46,73,76,103,106,133,136,163,166,193,196,223,226,253,256,283,286,313,316,343,346,373,376,403,406,433,436,463,466,493,496,523,526,553,556,583,586,613,616,643,646,673,
14,15,44,45,74,75,104,105,134,135,164,165,194,195,224,225,254,255,284,285,314,315,344,345,374,375,404,405,434,435,464,465,494,495,524,525,554,555,584,585,614,615,644,645,674
]
# if you have a really big display! I used two cheap strings of
# 50 LEDs, so I just have a 12x8 grid = 96 LEDs
# I got mine from: http://www.amazon.co.uk/gp/product/B00MXW054Y
# I also used an 74AHCT125 level shifter & 10 amp 5V PSU
# Good build tutorial here:
# https://learn.adafruit.com/neopixels-on-raspberry-pi?view=all

# Check that we have sensible width & height
if MATRIX_WIDTH * MATRIX_HEIGHT != len(myMatrix):
  raise Exception("Matrix width x height does not equal length of myMatrix")

def allonecolour(strip,colour):
  # Paint the entire matrix one colour
  for i in range(strip.numPixels()):
    strip.setPixelColor(i,colour)
  strip.show()

def colour(r,g,b):
  # Fix for Neopixel RGB->GRB, also British spelling
  return Color(g,r,b)

def colourTuple(rgbTuple):
  return Color(rgbTuple[0],rgbTuple[1],rgbTuple[2])

def initLeds(strip):
  # Intialize the library (must be called once before other functions).
  strip.begin()
  # Wake up the LEDs by briefly setting them all to white
  allonecolour(strip,colour(255,255,255))
  time.sleep(0.01)

# Open the image file given as the command line parameter
try:
  loadIm=Image.open(sys.argv[1])
except:
  if len(sys.argv)==0:
    raise Exception("Please provide an image filename as a parameter.")
  else:
    raise Exception("Image file %s could not be loaded" % sys.argv[1])

# If the image height doesn't match the matrix, resize it
if loadIm.size[1] != MATRIX_HEIGHT:
  origIm=loadIm.resize((loadIm.size[0]/(loadIm.size[1]//MATRIX_HEIGHT),MATRIX_HEIGHT),Image.BICUBIC)
else:
  origIm=loadIm.copy()
# If the input is a very small portrait image, then no amount of resizing will save us
if origIm.size[0] < MATRIX_WIDTH:
  raise Exception("Picture is too narrow. Must be at least %s pixels wide" % MATRIX_WIDTH)

# Check if there's an accompanying .txt file which tells us
# how the user wants the image animated
# Commands available are:
# NNNN speed S.SSS
#   Set the scroll speed (in seconds)
#   Example: 0000 speed 0.150
#   At position zero (first position), set the speed to 150ms
# NNNN hold S.SSS
#   Hold the frame still (in seconds)
#   Example: 0011 hold 2.300
#   At position 11, keep the image still for 2.3 seconds
# NNNN-PPPP flip S.SSS
#   Animate MATRIX_WIDTH frames, like a flipbook
#   with a speed of S.SSS seconds between each frame
#   Example: 0014-0049 flip 0.100
#   From position 14, animate with 100ms between frames
#   until you reach or go past position 49
#   Note that this will jump positions MATRIX_WIDTH at a time
#   Takes a bit of getting used to - experiment
# NNNN jump PPPP
#   Jump to position PPPP
#   Example: 0001 jump 0200
#   At position 1, jump to position 200
#   Useful for debugging only - the image will loop anyway
txtlines=[]
match=re.search( r'^(?P<base>.*)\.[^\.]+$', sys.argv[1], re.M|re.I)
if match:
  txtfile=match.group('base')+'.txt'
  if os.path.isfile(txtfile):
    print "Found text file %s" % (txtfile)
    f=open(txtfile,'r')
    txtlines=f.readlines()
    f.close()

# Add a copy of the start of the image, to the end of the image,
# so that it loops smoothly at the end of the image
im=Image.new('RGB',(origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))
im.paste(origIm,(0,0,origIm.size[0],MATRIX_HEIGHT))
im.paste(origIm.crop((0,0,MATRIX_WIDTH,MATRIX_HEIGHT)),(origIm.size[0],0,origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
initLeds(strip)

# And here we go.
try:
  while(True):

    # Loop through the image widthways
    # Can't use a for loop because Python is dumb
    # and won't jump values for FLIP command
    x=0
    # Initialise a pointer for the current line in the text file
    tx=0

    while x<im.size[0]-MATRIX_WIDTH:

      # Set the sleep period for this frame
      # This might get changed by a textfile command
      thissleep=SPEED

      # Set the increment for this frame
      # Typically advance 1 pixel at a time but
      # the FLIP command can change this
      thisincrement=1

      rg=im.crop((x,0,x+MATRIX_WIDTH,MATRIX_HEIGHT))
      dots=list(rg.getdata())
  
      for i in range(len(dots)):
        strip.setPixelColor(myMatrix[i],colourTuple(dots[i]))
      strip.show()

      # Check for instructions from the text file
      if tx<len(txtlines):
        match = re.search( r'^(?P<start>\s*\d+)(-(?P<finish>\d+))?\s+((?P<command>\S+)(\s+(?P<param>\d+(\.\d+)?))?)$', txtlines[tx], re.M|re.I)
        if match:
          print "Found valid command line %d:\n%s" % (tx,txtlines[tx])
          st=int(match.group('start'))
          fi=st
          print "Current pixel %05d start %05d finish %05d" % (x,st,fi)
          if match.group('finish'):
            fi=int(match.group('finish'))
          if x>=st and tx<=fi:
            if match.group('command').lower()=='speed':
              SPEED=float(match.group('param'))
              thissleep=SPEED
              print "Position %d : Set speed to %.3f secs per frame" % (x,thissleep)
            elif match.group('command').lower()=='flip':
              thissleep=float(match.group('param'))
              thisincrement=MATRIX_WIDTH
              print "Position %d: Flip for %.3f secs" % (x,thissleep)
            elif match.group('command').lower()=='hold':
              thissleep=float(match.group('param'))
              print "Position %d: Hold for %.3f secs" % (x,thissleep)
            elif match.group('command').lower()=='jump':
              print "Position %d: Jump to position %s" % (x,match.group('param'))
              x=int(match.group('param'))
              thisincrement=0
          # Move to the next line of the text file
          # only if we have completed all pixels in range
          if x>=fi:
            tx=tx+1
        else:
          print "Found INVALID command line %d:\n%s" % (tx,txtlines[tx])
          tx=tx+1

      x=x+thisincrement
      time.sleep(thissleep)

except (KeyboardInterrupt, SystemExit):
  print "Stopped"
  allonecolour(strip,colour(0,0,0))
