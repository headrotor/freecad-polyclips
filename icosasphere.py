#import Part
#myPart = FreeCAD.ActiveDocument.addObject("Part::Feature","myPartName")
#cube = Part.makeBox(2,2,2)
#myPart.Shape = cube
import FreeCAD as App
import FreeCADGui as Gui
import Part,PartGui
import math


######## size constants, in mm

# inner sphere diameter
sphere_diam = 40.0
icosa_pad = 8.0   # add this to sphere diameter to get (rough?) icosa "diam"
drill_diam = 1.8   # radius of drill holes
drill_depth = 2*icosa_pad

# icosa ratio: multiply scale by this to get outside dimension
icosa_ratio = 48.53/25.0

########



# make triangular face from three corner vertexes
def make_tri_face(v1, v2, v3, vlist):
    face_wire = Part.makePolygon([vlist[v1],vlist[v2],vlist[v3],vlist[v1]])
    return Part.Face(face_wire)

def make_edges(a, b, c):
    # return sorted pairwise permutations of vertex indexes
    elist = []
    elist.append((b, a) if b < a else (a, b))
    elist.append((c, b) if c < b else (b, c))
    elist.append((a, c) if a < c else (c, a))
    return elist

doc = App.newDocument()


obj = App.ActiveDocument.addObject("PartDesign::Body", "Body")
obj.Label = "dodeca body"

#obj.addProperty("App::PropertyLinkGlobal","Base","Draft","App::Property","The base object that must be duplicated")

vtex =[]
phi = (math.sqrt(5.) + 1.) / 2.0
scale = 1.0

# need to scale phi if scale is not 1.0

scale = (sphere_diam/2 + icosa_pad)/icosa_ratio
phi = phi*scale


vtex.append(FreeCAD.Vector(-scale, phi, 0))
vtex.append(FreeCAD.Vector(scale, phi, 0))
vtex.append(FreeCAD.Vector(-scale, -phi, 0))
vtex.append(FreeCAD.Vector(scale, -phi, 0))


vtex.append(FreeCAD.Vector(0, -scale, phi))
vtex.append(FreeCAD.Vector(0, scale, phi))
vtex.append(FreeCAD.Vector(0, -scale, -phi))
vtex.append(FreeCAD.Vector(0, scale, -phi))

vtex.append(FreeCAD.Vector(phi, 0, -scale))
vtex.append(FreeCAD.Vector(phi, 0, scale))
vtex.append(FreeCAD.Vector(-phi, 0, -scale))
vtex.append(FreeCAD.Vector(-phi, 0, scale))

# for rectangle "skeleton"
# test_wire = Part.makePolygon([vtex[0],vtex[1],vtex[2], vtex[3], vtex[0]])
# Part.show(test_wire)
# test_wire = Part.makePolygon([vtex[4],vtex[5],vtex[6], vtex[7], vtex[4]])
# Part.show(test_wire)
# test_wire = Part.makePolygon([vtex[8],vtex[9],vtex[10], vtex[11], vtex[8]])
# Part.show(test_wire)


# for i in range(len(vtex) - 1):
#     l=Part.LineSegment()
#     l.StartPoint=vtex[i]
#     l.EndPoint=vtex[i+1]

#     doc.addObject("Part::Feature","Line").Shape=l.toShape() 


# make list of faces, three vertex indexes per face
facelist = []

# 5 faces around point 0
facelist.append((0, 11, 5))
facelist.append((0, 5, 1))
facelist.append((0, 1, 7))
facelist.append((0, 7, 10))
facelist.append((0, 10, 11))

# 5 adjacent faces
facelist.append((5, 11, 4))
facelist.append((1, 5, 9))
facelist.append((7, 1, 8))
facelist.append((11, 10, 2))
facelist.append((10, 7, 6))

# 5 faces around point 3
facelist.append((3, 9, 4))
facelist.append((3, 4, 2))
facelist.append((3, 2, 6))
facelist.append((3, 6, 8))
facelist.append((3, 8, 9))

# 5 adjacent faces
facelist.append((4, 9, 5))
facelist.append((2, 4, 11))
facelist.append((6, 2, 10))
facelist.append((8, 6, 7))
facelist.append((9, 8, 1))

faces = []
edgelist = []

for f in facelist:
    faces.append(make_tri_face(f[0], f[1], f[2], vtex))
    for e in make_edges(f[0], f[1], f[2]):
        if e not in edgelist:
            edgelist.append(e)

myShell = Part.makeShell(faces)   
mySolid = Part.makeSolid(myShell)


myPart = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature','dodeca')
myPart.Shape = mySolid

App.ActiveDocument.recompute()

# now have a list of edge vertexes in edgelist -- a list of two-vertex tuples for each edge.
# make a list  of vectors that are edge midpoints

midpts = []
for edge in edgelist:
   midpts.append((vtex[edge[0]] + vtex[edge[1]])/2) 

#feature = App.ActiveDocument.addObject('PartDesign::SubtractiveSphere', 'ball')
#feature.Radius= 1.5
#feature.Placement.Base = FreeCAD.Vector(0., 0., 0.)
#App.ActiveDocument.Body.Group = App.ActiveDocument.Body.Group + [feature]
#the workaround by directly altering the property

Gui.runCommand('PartDesign_MoveTip',0)

feature = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::SubtractiveSphere','sball')

feature = App.ActiveDocument.addObject('PartDesign::SubtractiveSphere', 'sball')

feature.Radius= sphere_diam/2
feature.Placement.Base = FreeCAD.Vector(0., 0., 0.)

#obj.addObject(feature)
App.ActiveDocument.Body.Group = App.ActiveDocument.Body.Group + [feature] #the workaround by directly altering the property
#Part.show(mySolid)

App.ActiveDocument.recompute()


# make drill circles for each vertex
dcircles = []
#for i, v in enumerate(vtex):
for i, v in enumerate(midpts):
    vname = "circle{}".format(i)
    myPart = App.ActiveDocument.addObject("Part::Feature", vname)
    myPart.Shape = Part.makeCircle(0.1,1.1*v, v)
    #the workaround by directly altering the property
    dcircles.append(myPart)

App.ActiveDocument.Body.Group = App.ActiveDocument.Body.Group + dcircles

# drill holes

#>>> App.getDocument('Unnamed').getObject('Hole').Profile = App.getDocument('Unnamed').getObject('vertex11')
#>>> App.ActiveDocument.recompute()

holes = []
for i, d  in enumerate(dcircles):
    hname = "hole{}".format(i)
    hole  = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Hole',hname)
    #hole = App.ActiveDocument.addObject('PartDesign::Hole','Hole')
    hole.Profile = d
    hole.Diameter = drill_diam
    hole.Depth = drill_depth
    holes.append(hole)
    

App.ActiveDocument.recompute()

#Gui.Selection.addSelection('Unnamed','Body','dodeca.')
#Gui.runCommand('Std_ToggleVisibility',0)


#for c in dcircles:
#    Part.show(c)
    
#doc.addObject("Part::Feature","Line").Shape=l.toShape() 
# edge1 = Part.makeLine((0.,0.,0), (10.,0.,0))
# edge2 = Part.makeLine((10.,0.,0), (10.,10.,0))
# wire1 = Part.Wire([edge1,edge2]) 
# edge3 = Part.makeLine((10.,10.,0), (0.,10.,0))
# edge4 = Part.makeLine((0.,10.,0), (0.,0.,0))
# wire2 = Part.Wire([edge3,edge4])
# wire3 = Part.Wire([wire1,wire2])
# Part.show(wire3) 
#doc.addObject("Part::Feature","Line").Shape=wire3.toShape() 


