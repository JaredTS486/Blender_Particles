import bpy
from bpy import props
from bpy.props import *
import math
import sys
import mathutils
from mathutils import *
import random
from random import *
import decimal
import time
import gc
import traceback
from bpy.types import Panel
from bpy.types import AnyType
from rna_prop_ui import PropertyPanel
from decimal import *
import threading
#import code
#namespace = globals().copy()
#namespace.update(locals())
#code.interact(local=namespace)

gc.enable()

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT' 
    mat.diffuse_intensity = 1.0 
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

red = makeMaterial('Red',      (1,0,0), (1  ,1  ,1), 1)
yellow = makeMaterial('Yellow',(1,1,0), (1  ,1  ,1), 1)
blue = makeMaterial('Blue',    (0,0,1), (1  ,1  ,1), 1)
green = makeMaterial('Green',  (0,1,0), (0.5,0.5,0), 0.5)
white = makeMaterial('White',  (1,1,1), (0.5,0.5,0), 0.5)
black = makeMaterial('Black',  (0,0,0), (0.5,0.5,0), 0.5)

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)
    
def getColor(color):
    if color == 'Red':
       return red
    if color == 'Blue':
       return blue
    if color == 'Yellow':
       return yellow
    if color == 'Green':
       return green
    if color == 'White':
       return white
    if color == 'Black':
       return black
    else:
       return black

def hideObject(ob, C, Instant):
    T = bpy.context.scene.Frames
    ob.Hidden = True
    #ob.hide = False
    pl = bpy.data.objects['Velocity('+str(ob.Num)+')']
    pl.location = (0,0,0) #Move vector to center of object
    ob.location = (0,0,10000) #Move far away from view
    X = C + 120
    if X > T: X = T
    if Instant == False:    
        pl.keyframe_insert(data_path="location", index=-1, frame=C)
        ob.keyframe_insert(data_path="location", index=-1, frame=X)
        ob.keyframe_insert(data_path="location", index=-1, frame=T)
    else:
        pl.keyframe_insert(data_path="location", index=-1, frame=C)
        pl.keyframe_insert(data_path="location", index=-1, frame=T)
        ob.keyframe_insert(data_path="location", index=-1, frame=C)
        ob.keyframe_insert(data_path="location", index=-1, frame=T)

def accel(x, v, dt):
    """Some function that determines acceleration from current 
    position, velocity, and timestep."""
    return v

def rk4(x, v, a, dt):
    """This should return (position, velocity) tuple object 
    after time dt has passed? Done in replacement of rambogogogo()
    x: initial position (number-like object)
    v: initial velocity (number-like object)
    accel: acceleration function accel(x,v,dt) (created above)
    dt: timestep (number)"""
    x1 = x
    v1 = v
    a1 = accel(x1, v1, 0)

    x2 = x + 0.5*v1*dt
    v2 = v + 0.5*a1*dt
    a2 = accel(x2, v2, dt/2.0)

    x3 = x + 0.5*v2*dt
    v3 = v + 0.5*a2*dt
    a3 = accel(x3, v3, dt/2.0)

    x4 = x + v3*dt
    v4 = v + a3*dt
    a4 = accel(x4, v4, dt)

    xf = x + (dt/6.0)*(v1 + 2*v2 + 2*v3 + v4)
    vf = v + (dt/6.0)*(a1 + 2*a2 + 2*a3 + a4)

    return xf, vf

def rambogogogo(ob,i):
    dt = bpy.context.scene.dt
    G = bpy.context.scene.G
    scn = bpy.context.scene
    pl = bpy.data.objects['Velocity('+str(ob.Num)+')']
    Vv = (pl.location * 25.0)
    ob.select = True
    ob.keyframe_insert(data_path="location", index=-1)
    obsize = (ob.dimensions[0] + ob.dimensions[1] + ob.dimensions[2]) / 6
    for a in bpy.data.objects:
        if a.name != ob.name:
            if a.Hidden == False and ob.Hidden == False:
                d = distance(ob,a)
                r = ob.location - a.location
                Fv = -((G*ob.Mass*a.Mass)/(d**2))*r
                Vv += (Fv*dt)/ob.Mass
                if (d < obsize):
                    if ob.Hidden == False:
                        if scn.Inelastic == True:
                            collision(ob,a,0,i)
                        if scn.Elastic == True:
                            collision(ob,a,1,i)
    bpy.ops.transform.translate(value = Vv*dt)
    ob.select = False #Done working with the particle
    pl.select = True
    pl.location = Vv / 25.0
    pl.keyframe_insert(data_path="location", index=-1)
    pl.select = False
    if ob.location.magnitude > 5000: hideObject(ob,i,False)
    return

def collision(A,B,C,i):
    Ma = A.Mass
    Mb = B.Mass
    La = A.location
    Lb = B.location
    plA = bpy.data.objects['Velocity('+str(A.Num)+')']
    plB = bpy.data.objects['Velocity('+str(B.Num)+')']
  
    Va = plA.location
    Vb = plB.location
    vfA = ((C * Mb) * ((Vb-Va) + (Ma*Va) + (Mb*Vb))) / (Ma+Mb)
    vfB = ((C * Ma) * ((Va-Vb) + (Ma*Va) + (Mb*Vb))) / (Ma+Mb)
    VNew = vfA + vfB
    MNew = Ma + Mb
    LNew = (La + Lb) / 2
    if Ma > Mb:
        B.select = True
        scale = Ma/Mb
        B.location = A.location
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type="VERT")
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        B.select = False
        A.select = True
    if Ma < Mb:
        A.select = True
        scale = Mb/Ma
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type="VERT")
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        A.select = False
        B.select = True
    
def createObject():
    num = bpy.context.scene.Number
    for n in range(num):
        origin = Vector((0,0,0))
        loc = bpy.context.scene
        count = loc.objCounter
        if loc.RandL == True:
            origin = Vector((
            randint(loc.minL, loc.maxL),
            randint(loc.minL, loc.maxL),
            randint(loc.minL, loc.maxL)))
        else:
            origin = loc.Location
        if  loc.AutoS == True:
            object_size = round(uniform(loc.minS, loc.maxS),1)
        else:
            object_size = loc.Size
        
        bpy.ops.mesh.primitive_uv_sphere_add(
        segments=loc.Segments,
        ring_count=loc.Rings,
        size= object_size,
        location = origin)
        ob = bpy.context.object
        #bpy.types.Object.Size to add custom variables to active object
        #variable can be accessed by bpy.context.object.Size = 1 (READ ONLY)
        #to make writeable variable use bpy.types.Object.Size = MyClass()
        
        bpy.types.Object.Num = IntProperty()
        bpy.types.Object.Hidden = BoolProperty(name = "Is Hidden")
        bpy.types.Object.Mass = IntProperty()
        bpy.types.Object.Velocity = FloatVectorProperty()
        bpy.types.Object.Saved_Velocity = FloatVectorProperty()
        bpy.types.Object.Saved_Location = FloatVectorProperty()
        bpy.types.Object.Type = StringProperty()
        bpy.types.Object.Size = FloatProperty()
        
        ob.show_name = False
        ob.Hidden = False #notice from delcaration above
        ob.name = loc.Name + '(' + str(loc.objCounter) + ')'
        ob.data.name = 'Mesh(' + str(loc.objCounter) + ')'
        ob.Num = loc.objCounter
        ob.Size = object_size
        
        setMaterial(bpy.context.object, getColor(loc.Color))
        
        T = ob.dimensions[0] + ob.dimensions[1] + ob.dimensions[2]
        base = T / 3 #Average of the objects Three Dimensions
        if loc.AutoM == True: ob.Mass = round(base*(loc.Multiple**loc.Power),0)
        else: ob.Mass = loc.Mass * (loc.Multiple ** loc.Power)

        ob['Saved_Location'] = ob.location    #Default location is saved
        ob['Type'] = 'Particle'
        
        bpy.ops.mesh.primitive_plane_add()
        pl = bpy.context.object
        pl.name = 'Velocity(' + str(ob.Num) + ')'
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type="VERT")
        pl.parent = ob
        pl.Hidden = True
        if loc.RandV == True:
            pl.location[0] = randint(loc.minV, loc.maxV)
            pl.location[1] = randint(loc.minV, loc.maxV)
            pl.location[2] = randint(loc.minV, loc.maxV)
        else: pl.location = loc.Velocity
        pl['Saved_Location'] = pl.location
        pl['Type'] = 'Velocity'
        pl.Num = loc.objCounter
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        loc.objCounter += 1
    return
        
def distance (A,B):
    (x1,y1,z1) = A.location
    (x2,y2,z2) = B.location
    dist = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    return dist

def run(origin):
    global n
    scn = bpy.context.scene
    t = scn.FrameKeys
    scn.frame_start = 0
    scn.frame_end = scn.Frames
    n = scn.frame_end
    base = int(round(n/60))
    for ob in bpy.data.objects:
        if ob.Type == 'Particle':
            Px = ob.location[0] #Location
            Py = ob.location[1] #Location
            Pz = ob.location[2] #Location
        if ob.Type == 'Velocity':
            Vx = ob.location[0] #Velocity
            Vy = ob.location[1] #Velocity
            Vz = ob.location[2] #Velocity
        Ax = [0.0] #Acceleration
        Ay = [0.0] #Acceleration
        Az = [0.0] #Acceleration
        
    for i in range(n+1):
        X = int(round(i/base))
        bpy.context.scene.Status = ('%3s%% Complete' % (round(i/n*100,1)))
        sys.stdout.write('\r%3s%% [%s>%s]' % (round(i/n*100,1), '='*X, ' '*(60-X)))
        sys.stdout.flush()
        for object in bpy.data.objects:
           if object.Hidden == False:
               rambogogogo(object,t)
        bpy.ops.anim.change_frame(frame = t)
        t += 1
    gc.collect()
      
def initGlobalProperties(scn):
    bpy.types.Scene.G = FloatProperty(
        name = "", 
        description = "Gravitational Constant",
        default = 0.60,
        step = 1,
        min = 0,
        max = 2000)
    bpy.types.Scene.dt = FloatProperty(
        name = "", 
        description = "Delta Time Constant",
        default = 0.0010,
        step = 0.01,
        subtype = 'TIME',
        unit = 'TIME',
        min = 0.0001,
        max = 10,
        precision=3)
    bpy.types.Scene.Frames = IntProperty(
        description = "How far apart should key frames be? Larger number slows movement speed down without changing the Delta Time Constant.",
        name = "",
        default = 1000,
        min = 60,
        max = 999999999)
    bpy.types.Scene.FrameKeys = IntProperty(
        description = "How far apart should key frames be? Larger number slows movement speed down without changing the Delta Time Constant.",
        name = "",
        default = 1,
        min = 0,
        max = 50)
    bpy.types.Scene.Status = StringProperty(
        name = "Status")
    return

initGlobalProperties(bpy.context.scene)

def initLocalProperties(scn):
    bpy.types.Scene.objCounter = bpy.props.IntProperty()
    if scn.objCounter <= 1: scn.objCounter = 1
    bpy.types.Scene.Rings = IntProperty(
        description = "Number of rings, smaller size generates rougher objects.",
        name = "",
        default = 2,
        min = 0,
        max = 25)
    bpy.types.Scene.Segments = IntProperty(
        description = "Number of segments, smaller size generates rougher objects.",
        name = "",
        default = 2,
        min = 0,
        max = 25)
    bpy.types.Scene.Size = FloatProperty(
        description = "Size of the object",
        name = "",
        default = 1.0,
        step=10,
        min = 0.0,
        max = 50.0)
    bpy.types.Scene.Mass = FloatProperty(
        description = "Specific Mass for Each Object",
        name = "",
        default = 3.33,
        step=1,
        min = 0.0,
        max = 500.0)
    bpy.types.Scene.Multiple = IntProperty(
        description = "Multiplier for the mass of each object.",
        name = "",
        default = 10,
        min = -500,
        max = 500)
    bpy.types.Scene.Power = IntProperty(
        description = "Multiplier for the mass of each object.",
        name = "",
        default = 2,
        min = -30,
        max = 30)
    bpy.types.Scene.Number = IntProperty(
        description = "Number of Objects to Generate",
        name = "",
        default = 1,
        step=10,
        min = 0,
        max = 500)
    bpy.types.Scene.minV = IntProperty(
        description = "Minimum Value",
        name = "",
        default = -100,
        min = -5000,
        max = 5000)
    bpy.types.Scene.maxV = IntProperty(
        description = "Maximum Value",
        name = "",
        default = 100,
        min = -5000,
        max = 5000)
    bpy.types.Scene.minL = IntProperty(
        description = "Minimum Value",
        name = "",
        default = -500,
        min = -5000,
        max = 5000)
    bpy.types.Scene.maxL = IntProperty(
        description = "Maximum Value",
        name = "",
        default = 500,
        min = -5000,
        max = 5000)
    bpy.types.Scene.minS = FloatProperty(
        description = "Maximum Value",
        name = "",
        default = 0.1,
        step=1,
        min = 0,
        max = 50.0)
    bpy.types.Scene.maxS = FloatProperty(
        description = "Maximum Value",
        name = "",
        default = 5.0,
        step=1,
        min = 0,
        max = 50.0)
    bpy.types.Scene.Location= IntVectorProperty(
        name="Location", 
        description="Location Vector",
        subtype = 'XYZ',
        default=(0, 0, 0))
    bpy.types.Scene.Name = StringProperty(
        default = "Object",
        name = "")
    bpy.types.Scene.Velocity = IntVectorProperty(
        name="Velocity", 
        description="Velocity Vector",
        subtype = 'XYZ',
        default=(0, 0, 0))
    bpy.types.Scene.AutoS = BoolProperty(
        name = "Random Object Size", 
        description = "If selected, the random range below will be used to generate a random object size between the minimum and maximum values.")
    bpy.types.Scene.Inelastic = BoolProperty(
        name = "Inelastic Collision", 
        description = "If selected, when particles collide collisions will be calculated using inelastic properties.")
    bpy.types.Scene.Elastic = BoolProperty(
        name = "Elastic Collision", 
        description = "If selected, when particles collide collisions will be calculated using elastic properties.")
    bpy.types.Scene.RandV = BoolProperty(
        name = "Random", 
        description = "If selected, the random range below will be used to generate a random vector between the minimum and maximum values.")
    bpy.types.Scene.AutoM = BoolProperty(
        name = "Auto", 
        description = "If selected, the size of each Object will be a variable in their mass.")
    bpy.types.Scene.RandL = BoolProperty(
        name = "Random", 
        description = "If selected, the random range below will be used to generate a random vector between the minimum and maximum values.")
    bpy.types.Scene.Hidden = BoolProperty(
        name = "Hidden", 
        description = "If selected, the script will skip this object in its calculations.")
    bpy.types.Scene.Color = EnumProperty(
        items = [('Red', 'Red', 'One'), 
                 ('Blue', 'Blue', 'Two'),
                 ('Yellow', 'Yellow', 'Three'),
                 ('Green', 'Green', 'Four'),
                 ('White', 'White', 'Five'),
                 ('Black', 'Black', 'Six')],
        name = "Color")
    return

initLocalProperties(bpy.context.scene)

def resetGlobal(scn):
    scn['Status'] = "0% Complete"
    scn['FrameKeys'] = 1
    scn['Frames'] = 1000
    scn['G'] = 0.06
    scn['dt'] = 0.0010
    scn['Inelastic'] = True
    scn['Elastic'] = False
    return

def resetLocal(scn):
    scn['Rings'] = 5
    scn['Segments'] = 10
    scn['Size'] = 1.0
    scn['Color'] = 0
    scn['RandL'] = True
    scn['AutoS'] = True
    scn['AutoM'] = True
    scn['RandV'] = True
    scn['Number'] = 1
    scn['Mass'] = 3.33
    scn['Multiple'] = 10
    scn['Name'] = "Particle"
    scn['Power'] = 5
    scn['minV'] = -100
    scn['maxV'] =  100
    scn['minL'] = -100
    scn['maxL'] =  100
    scn['minS'] =  0.10
    scn['maxS'] =  5.00
    scn['Velocity'] = (0, 0, 0)
    scn['Location'] = (0, 0, 0)
    return

class Calculate(bpy.types.Operator):
    bl_idname = "calc.now"
    bl_label = "Calculate Now"
    bl_description = "Calculate the Current Scene / Objects"
    def execute(self, context):
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: 
            print("Warning: bpy.ops.object.mode_set(mode='OBJECT') Failed...")
            sys.stdout.flush()
        run(Vector((0,0,0)))
        return {'FINISHED'}
    
class Reset_Global(bpy.types.Operator):
    bl_idname = "reset.global"
    bl_label = "Reset Global"
    bl_description = "Reset all of the settings in this Box"
    def execute(self, context):
        resetGlobal(bpy.context.scene)
        return {'FINISHED'}
    
class Delete_All(bpy.types.Operator):
    bl_idname = "delete.all"
    bl_label = "Delete All"
    bl_description = "Delete all of the objects in the scene"
    def execute(self, context):
        try: bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        except: pass #If this causes an error thats ok, we just need to try at least once.
        candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]
        for object_name in candidate_list:
            bpy.data.objects[object_name].select = True
        bpy.ops.object.delete()
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        bpy.context.scene.objCounter = 1
        return {'FINISHED'}
    
class Delete_Selected(bpy.types.Operator):
    bl_idname = "delete.selected"
    bl_label = "Delete Selected"
    bl_description = "Delete the Selected object and its Child objects."
    def execute(self, context):
        bpy.ops.object.delete()
        return {'FINISHED'}
    
class Clear_Keyframes_All(bpy.types.Operator):
    bl_idname = "clear.keyframes_all"
    bl_label = "Clear Keyframes"
    bl_description = "Clear all of the keyframes for every object in the scene."
    def execute(self, context):
        for ob in bpy.data.objects:
            ob['Hidden'] = False
            ob.select = True
            bpy.ops.anim.keyframe_clear_v3d()
            ob.select = False
        return {'FINISHED'}
    
class Reset_Velocity_All(bpy.types.Operator):
    bl_idname = "reset.velocity_all"
    bl_label = "Reset Velocities"
    bl_description = "Reset all of the velocites to the saved state."
    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.Type == 'Velocity': ob.location = ob['Saved_Location']
        return {'FINISHED'}
    
class Save_Velocity_All(bpy.types.Operator):
    bl_idname = "save.velocity_all"
    bl_label = "Save Velocities"
    bl_description = "Saves the velocity vector for all objects."
    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.Type == 'Velocity': ob.location = ob['Saved_Location']
        return {'FINISHED'}
    
class Reset_Location_All(bpy.types.Operator):
    bl_idname = "reset.location_all"
    bl_label = "Reset Locations"
    bl_description = "Reset all of the object locations to the saved state."
    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.Type == 'Particle': ob.location = ob['Saved_Location']
        return {'FINISHED'}

class Save_Location_All(bpy.types.Operator):
    bl_idname = "save.location_all"
    bl_label = "Save Locations"
    bl_description = "Saves the location for all particle objects."
    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.Type == 'Particle': ob.location = ob['Saved_Location']
        return {'FINISHED'}
    
class GlobalUI(bpy.types.Panel):
    bl_label = "Orbital Simulation Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
        
    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        
        row = layout.row()
        box = row.box()
        box.label("Global Settings",icon="WORLD")
        split = box.split(percentage=0.60)
        col = split.column(align=True)
        col.label("Gravitational Constant")
        col.label("Delta Time Constant")
        col.label("Insert Frame Every")
        col.label("Frames / Calculations")
        col = split.column(align=True)
        col.prop(scn, 'G')
        col.prop(scn, 'dt')
        col.prop(scn, 'FrameKeys')
        col.prop(scn, 'Frames')
        
        split = box.split()
        col = split.column(align=True)
        col.prop(scn, 'Inelastic')
        col.prop(scn, 'Elastic')
        
        split = box.split()
        col = split.column(align=True)
        col.operator("calc.now")
        col.operator("reset.global")
        split = box.split(percentage=0.50)
        col = split.column(align=True)
        col.operator("delete.all")
        col.operator("save.velocity_all")
        col.operator("save.location_all")
        col = split.column(align=True)
        col.operator("delete.selected")
        col.operator("reset.velocity_all")
        col.operator("reset.location_all")
        split = box.split()
        split.operator("clear.keyframes_all")
        box.prop(scn, 'Status')
        
class LocalUI(bpy.types.Panel):
    bl_label = "Orbital Simulation Panel"
    bl_icon = "WORLD"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self, context):
        layout = self.layout
        self = bpy.context.scene
        row = layout.row()
        box = row.box()
        box.label("Object Settings", icon='OBJECT_DATA')
        
        split = box.split(percentage=0.20)
        col = split.column()
        col.label("Name")
        col = split.column()
        col.prop(self,"Name")
        
        split = box.split(percentage=0.50)
        col = split.column()
        col.label("Number")
        col.label("Object Mass")
        
        col = split.column()
        col.prop(self, 'Number')
        col.prop(self, 'AutoM')
        
        split = box.split(percentage=0.33)
        col = split.column(align=True)
        col.label("Base")
        col.prop(self, 'Mass')
        col = split.column(align=True)
        col.label("Multiple")
        col.prop(self, 'Multiple')
        col = split.column(align=True)
        col.label("Power")
        col.prop(self, 'Power')
        split = box.split()
        col = split.column()
        col.label("Example: 20 * 10 ^ 2")
        
        split = box.split(percentage=0.50)
        col = split.column(align=True)
        col.prop(self, 'Velocity')
        
        col = split.column(align=True)
        col.prop(self, 'RandV')
        col.label("Random Range")
        col.prop(self, 'minV')
        col.prop(self, 'maxV')
        
        split = box.split(percentage=0.50)
        col = split.column(align=True)
        col.prop(self, 'Location')
        
        col = split.column(align=True)
        col.prop(self, 'RandL')
        col.label("Random Range")
        col.prop(self, 'minL')
        col.prop(self, 'maxL')
        box.prop(self, 'Color')
        
        split = box.split(percentage=0.60)
        col = split.column()
        col.label("Size")
        col.label("Ring Count")
        col.label("Segments")
        col.prop(self, 'AutoS')
        
        col = split.column()
        col.prop(self, 'Size')
        col.prop(self, 'Rings')
        col.prop(self, 'Segments')
        col.label("Random Range")
        col.prop(self, 'minS')
        col.prop(self, 'maxS')
        
        split = box.split(percentage=0.50)
        split.alignment = 'EXPAND'
        col = split.column()
        col.operator("local.variables", text="Create Object(s)").number=2
        col = split.column()
        col.operator("local.variables", text="Reset Settings").number=3
        #self.layout.prop(bpy.context.active_object, '["foo"]')

class Local_Variables(bpy.types.Operator):
    bl_idname = "local.variables"
    bl_label = "Print Variables"
    number = bpy.props.IntProperty()
    box = bpy.props.IntProperty()
    error_message = StringProperty(name="Error Message")
    
    def execute(self, context):
        if self.number == 2:
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass #If this causes an error thats ok, we just need to try at least once.
            createObject()
        if self.number == 3:
            resetLocal(bpy.context.scene)
        return{'FINISHED'}
    
def printProp(label, key, scn):
    try:
        val = scn[key]
    except:
        val = 'Undefined'
    print("%s %s %s" % (label, key, val))
    sys.stdout.flush()
 
class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()
    # Below is how to call the above class generating a message box
    # bpy.ops.error.message('INVOKE_DEFAULT', 
    # type = "Error",
    # message = 'Found "return" on line %d' % n)
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
 
    def draw(self, context):
        self.layout.label("A message has arrived")
        row = self.layout.split(0.25)
        row.prop(self, "type")
        row.prop(self, "message")
        row = self.layout.split(0.80)
        row.label("") 
        row.operator("error.ok")

class OkOperator(bpy.types.Operator):
    bl_idname = "error.ok"
    bl_label = "OK"
    def execute(self, context):
        return {'FINISHED'}
 
bpy.utils.register_class(OkOperator)
bpy.utils.register_class(MessageOperator)
bpy.utils.register_module(__name__)
