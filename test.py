import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
 
#add some text
bk_text = "DirectDialog- YesNoDialog Demo"
textObject = OnscreenText(text = bk_text, pos = (0.85,0.85), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
#add some text
output = ""
textObject = OnscreenText(text = output, pos = (0.95,-0.95),
 scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
#callback function to set  text 
def itemSel(arg):
	if(arg):
		output = "Button Selected is: Yes"
	else:
		output = "Button Selected is: No"
	textObject.setText(output)
 
#create a frame
dialog = YesNoDialog(dialogName="YesNoCancelDialog", text="Please choose:", command=itemSel)
 
base.camera.setPos(0,-20,0)
#run the tutorial
run()
