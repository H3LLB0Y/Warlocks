from direct.showbase.ShowBase import Plane, ShowBase, Vec3, Point3, CardMaker

class YourClass(ShowBase):
  def __init__(self):
    ShowBase.__init__(self)
    self.disableMouse()
    self.camera.setPos(0, 60, 25)
    self.camera.lookAt(0, 0, 0)
    z = 0
    self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, z))
    self.model = loader.loadModel("jack")
    self.model.reparentTo(render)
    cm = CardMaker("blah")
    cm.setFrame(-100, 100, -100, 100)
    render.attachNewNode(cm.generate()).lookAt(0, 0, -1)
    taskMgr.add(self.__getMousePos, "_YourClass__getMousePos")
 
  def __getMousePos(self, task):
    if base.mouseWatcherNode.hasMouse():
      mpos = base.mouseWatcherNode.getMouse()
      pos3d = Point3()
      nearPoint = Point3()
      farPoint = Point3()
      base.camLens.extrude(mpos, nearPoint, farPoint)
      if self.plane.intersectsLine(pos3d,
          render.getRelativePoint(camera, nearPoint),
          render.getRelativePoint(camera, farPoint)):
        print "Mouse ray intersects ground plane at ", pos3d
        self.model.setPos(render, pos3d)
    return task.again

YourClass();base.taskMgr.run()
