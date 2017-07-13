import maya.cmds as cmds
import random
import pymel.core as pm
import maya.mel as mel
import maya.api.OpenMaya as OpenMaya

class UI:
    selBuffer = []

    def __init__(self):
        self.scanFunc = False

        if pm.window('mainWindow', exists=True):
            pm.deleteUI('mainWindow', window=True)
        pm.window('mainWindow')
        pm.window('mainWindow', edit=True, width=364, height=237, exists=False,
                  mxb=False, s=False, rtf=True, mb=True, mbv=True, title="vFracture v0.31")
        pm.showWindow('mainWindow')

        # layout A
        pm.tabLayout()
        pm.formLayout('FAST shatter (SOuP)')
        pm.frameLayout(label="SOuP Voronoi shattering", w=358)
        pm.columnLayout('cl1', adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(h=10, st="in")
        pm.checkBox('chBxA', label="Create inside-outside material (experemental)")
        pm.checkBox('chBxB', label="Transfer vertexNormal from main object")
        pm.checkBox('chBxD', label="Remember main object: - - - ", vis=True)
        pm.separator(h=5, st="in")
        pm.button('buttD', w=30, h=15, label='reset', c=lambda x: fr.resetButtD(), vis=True)
        pm.separator(h=5, st="in")
        pm.rowLayout('rowL', nc=3, cw3=(132, 50, 100), adj=2, columnAlign=(2, "center"),
                     columnAttach3=("both", "both", "both"), vis=True)
        pm.text(label="shards amount:")
        pm.intFieldGrp('fieldGrp', cal=(1, 'center'), v1=25, vis=True)
        pm.text(label="test...", vis=False)
        pm.setParent('..')
        pm.separator(h=2, st="none")
        pm.separator(h=5, st="in")
        pm.button('shatterButt', label="SHATTER OBJECT", bgc=(0.0, 0.5, 0.0), c=lambda x: Common.startCheckSouP(), h=30)

        pm.text('textA', label="Select a single polygonal object!", vis=False, bgc=(1.0, 0.3, 0.0))
        pm.separator(h=5, st="in")

        pm.button('crChButt', label="CREATE SHARDS", c=lambda x: fr.sepsShard(), h=30, vis=False, bgc=(0.0, 0.5, 0.0))
        pm.text('textC', vis=False, bgc=(1.0, 0.3, 0.0))
        pm.button('cancelButt', label="CANCEL", bgc=(1.0, 0.4, 0.0),
                  c=lambda x: fr.clCommandA('crChButt', 'cancelButt', 'prgsA'), vis=False, h=30)
        pm.separator('sepB1', h=5, st="in", vis=False)
        pm.button('cancelButtB', label="CANCEL", bgc=(1.0, 0.4, 0.0), c=lambda x: fr.clCommandB(), vis=False, h=30)
        pm.separator('sepB2', h=5, st="in", vis=False)
        pm.separator(h=10, st="none")
        pm.progressBar('prgsA', isInterruptable=True, vis=False)
        pm.separator(h=10, st="none")
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

        # layout B
        pm.formLayout('SLOW shatter (VFR)')
        pm.frameLayout(label="Voronoi shattering scrypt", w=358)
        pm.columnLayout(adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(h=5, st="in")
        pm.separator(h=2, st="none")
        pm.checkBox('chBxC', label="Transfer vertexNormal from main object")
        pm.separator(h=2, st="none")
        pm.separator(h=5, st="in")
        pm.intFieldGrp('shField', label="number of pieces:", v1=25, cw2=(130, 90), ct2=("both", "both"),
                       co2=(15, 5),  vis=True)
        pm.separator(h=2, st="none")
        pm.separator(h=5, st="in")
        pm.button('shButt', label="SHATTER OBJECT", bgc=(0.0, 0.5, 0.0), c=lambda x: vs.selInfCheck(), vis=True, h=30)
        pm.text('textF', label="Select a polygonal object!", vis=False, bgc=(1.0, 0.3, 0.0))
        pm.button('clButt', label="CANCEL", bgc=(1.0, 0.4, 0.0), c=lambda x: vs.clCommand('shButt', 'clButt', 'prgs'),
                  vis=False, h=30)
        pm.separator(h=5, st="in")
        pm.separator(h=5, st="none")
        pm.progressBar('prgs', isInterruptable=True, progress=0, vis=False)
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

        # layout C
        pm.formLayout('BONUS command')
        pm.frameLayout(label="Bonus command", w=358)
        pm.columnLayout(adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(h=75, st="none")
        pm.text('COMING SOON...')
        pm.separator(h=10, st="none")
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')


# common functions
class Common(UI):

    @staticmethod
    def shaderInit(sel, R, G, B, nameMat):
        mel.eval('MLdeleteUnused;')
        _name = (nameMat + sel)
        if cmds.objExists(_name):
            print 'WARRING! Duplicate material or shader group... clearing'
        else:
            cmds.shadingNode('lambert', asShader=True, name=_name)
            cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=(_name + 'SG'))
            cmds.connectAttr((_name + '.outColor'), (_name + 'SG.surfaceShader'), force=True)
            cmds.setAttr((_name + '.color'), R, G, B, type="double3")
        return _name

    @staticmethod
    def fixInNormal(obj, mainObj, SG):
        pm.select(obj)
        evalList = pm.ls(sl=True)
        pm.delete(evalList, ch=True)
        evalList = pm.ls(sl=True, o=True, dag=True, exactType="mesh")
        connList = pm.listConnections(evalList, type='shadingEngine')
        res = [('inMat_' + mainObj + SG) for i in connList]
        pss = pm.filterExpand(res, sm=34, ex=True)
        pm.select(pss, r=True)
        pm.polySetToFaceNormal(setUserNormal=True)
        pm.select(cl=True)

    @staticmethod
    def startCheckSouP():  # start func
        if pm.ls(sl=True):
            selObj = pm.ls(sl=True)[0]
            polyChk = pm.filterExpand(selObj, ex=True, sm=12)
            if pm.nodeType(polyChk) == 'transform':
                UI.selBuffer.append(selObj)
                fr.start()
        else:
            pm.text('textA', e=True, vis=True)


# SoUP
class SouPVoronoi(UI):
    def __init__(self):
        UI.__init__(self)
        self.scanFunc = True

    def start(self):
        pm.makeIdentity(apply=True, t=True, r=True, s=True, n=1, pn=True)
        self.scanFunc = True
        self.selArr = pm.ls(sl=True)
        self.vSize = pm.intFieldGrp('fieldGrp', q=True, value1=True)
        self.mesh = pm.createNode('mesh', name=(self.selArr[0] + "_meshShape"))
        self.shatterNode = pm.createNode('shatter', name=(self.selArr[0] + '_shatterShape'), ss=True)
        self.scatterNode = pm.createNode('scatter', name=(self.selArr[0] + '_scatterShape'))
        self.shapeArr = self.selArr[0].getShape()
        self.arrShards = []
        self.chBxCfoo()
        pm.refresh()

        pm.intFieldGrp('fieldGrp', e=True, m=True, en=False)
        pm.checkBox('chBxD', e=True, vis=True, label="Remember main object: %s" % (UI.selBuffer[0]))
        pm.separator('sepB1', e=True, vis=True)
        pm.button('cancelButtB', e=True, vis=True)
        pm.separator('sepB2', e=True, vis=True)

        pm.button('crChButt', e=True, vis=True)
        pm.rowLayout('rowL', e=True, vis=True)
        pm.button('shatterButt', e=True, vis=False)
        pm.text('textA', edit=True, vis=False)

        # connect attribute
        pm.setAttr((self.selArr[0] + ".visibility"), 1)
        pm.connectAttr((self.selArr[0] + ".worldMatrix"), (self.scatterNode + ".inWorldMatrix"))
        pm.connectAttr((self.shapeArr + ".worldMesh"), (self.scatterNode + ".inGeometry"))
        pm.setAttr(self.scatterNode + ".scatterMode", 0)
        pm.setAttr(self.scatterNode + ".pointDensity", 100000)
        pm.setAttr((self.scatterNode + ".maxNumberOfPoints"), self.vSize)
        pm.connectAttr((self.scatterNode + ".outGeometry"), (self.shatterNode + ".inGeometry"))
        pm.connectAttr((self.scatterNode + ".outPositionPP"), (self.shatterNode + ".inPositionPP"))
        pm.connectAttr((self.shatterNode + ".outGeometry"), (self.mesh + ".inMesh"))
        # refresh(update) before create shards
        pm.refresh()
        self.createShards()

    def clCommandA(self, crButton, clButton, prgBar):  # cancel command A
        if not self.scanFunc:
            self.scanFunc = True
        pm.button(crButton, e=True, vis=True)
        pm.button(clButton, e=True, vis=False)
        pm.progressBar(prgBar, edit=True, vis=False)

    def clCommandB(self):
        pm.separator('sepB1', e=True, vis=False)
        pm.button('cancelButtB', e=True, vis=False)
        pm.separator('sepB2', e=True, vis=False)

        pm.button('shatterButt', e=True, vis=True)
        pm.button('crChButt', e=True, vis=False)
        pm.rowLayout('rowL', e=True, vis=True)
        pm.text('textC', e=True, vis=False)
        pm.intFieldGrp('fieldGrp', e=True, m=True, en=True)
        pm.checkBox('chBxD', e=True, vis=True, v=False, label="Remember main object: - - - ")
        del UI.selBuffer[:]

        pm.delete(self.selArr[0] + '_scatter')
        pm.delete(ch=True)

    def chBxOutMat(self):  # check box
        if pm.checkBox('chBxA', q=True, v=True):
            self.setInsMat()

    @staticmethod
    def chBxTrVtx(obj, shMesh):
        if pm.checkBox('chBxB', q=True, v=True):
            pm.transferAttributes(obj, shMesh, transferNormals=1, sampleSpace=1)

    @staticmethod
    def resetButtD():
        del UI.selBuffer[:]
        pm.checkBox('chBxD', e=True, vis=True, v=False, label="Remember main object: - - - ")
        pm.checkBox('chBxA', e=True, v=False)
        pm.checkBox('chBxB', e=True, v=False)

    def createShards(self):
        pm.text('textC', edit=True, vis=False)

        pm.setAttr((self.shatterNode + ".autoEvaluate"), 1)
        pm.setAttr((self.selArr[0] + ".visibility"), 0)
        pm.select(self.selArr[0] + '_mesh', r=True)
        pss = pm.ls(sl=True)
        inSM = Common.shaderInit(pss[0], 1.0, 0.583, 0.583, 'inMat_')
        pm.select(self.mesh)
        pm.hyperShade(assign=inSM)
        self.chBxTrVtx(self.selArr[0], self.mesh)
        pm.cycleCheck(e=False)

    def setIntVolume(self):
        self.vSize = pm.intFieldGrp('fieldGrp', q=True, value1=True)
        pm.setAttr((self.scatterNode + ".maxNumberOfPoints"), self.vSize)
        print "New shards amount: " + str(self.vSize) + ', please wait...'

    def sepsShard(self):
        sel = pm.ls(sl=True)
        if not sel:
            pm.text('textC', label='select %s and press button' % (self.selArr[0] + '_mesh'), edit=True, vis=True)
        else:
            pm.text('textC', edit=True, vis=False)
            pm.separator('sepB1', e=True, vis=False)
            pm.button('cancelButtB', e=True, vis=False)
            pm.separator('sepB2', e=True, vis=False)
            #
            pm.select(self.mesh)
            pm.polySeparate(ch=False)
            self.arrShards = pm.ls(sl=True)
            i = 0
            for shard in self.arrShards:
                pm.rename(shard, self.selArr[0] + "_shard_" + str(i))
                pm.xform(cp=True)
                i += 1
            pm.rename((self.selArr[0] + '_mesh'), (self.selArr[0] + '_shards'))
            pm.refresh()
            self.chBxOutMat()
            #
            pm.button('crChButt', e=True, vis=False)
            pm.button('shatterButt', e=True, vis=True)
            pm.rowLayout('rowL', e=True, vis=True)
            pm.intFieldGrp('fieldGrp', e=True, m=True, en=True)

    @staticmethod
    def nNormalCheck(obj):
        faces = pm.MeshFace(obj)
        numNormal = [i for i in range(len(faces))]
        nxNormal = [i.getNormal() for i in faces]
        nNormal = [[round(x, 2) for x in i] for i in nxNormal]
        return nNormal, numNormal

    def chBxCfoo(self):
        if pm.checkBox('chBxD', q=True, v=True):
            xSel = UI.selBuffer[0]
        else:
            xSel = self.selArr[0]
        return xSel

    def setInsMat(self):  # apply outside shader
        pm.button('crChButt', e=True, vis=False)
        pm.button('cancelButt', e=True, vis=True)

        selObj = SouPVoronoi.chBxCfoo(self)
        pm.select(selObj)
        setA = SouPVoronoi.nNormalCheck(selObj)
        self.scanFunc = False
        sMat = Common.shaderInit(selObj, 0.78, 0.78, 0.78, 'outMat_')

        pm.select(self.arrShards)
        selB = pm.ls(sl=True)
        inc = 0
        for shard in selB:
            if self.scanFunc:
                pm.progressBar('prgsA', q=True, endProgress=True)
                break
            pm.progressBar('prgsA', e=True, progress=inc, vis=True, maxValue=len(selB) - 1)
            pm.select(shard, r=True)
            setB = SouPVoronoi.nNormalCheck(shard)
            inc += 1
            pm.refresh()
            for i in setA[1]:
                for x in setB[1]:
                    if setA[0][i] == setB[0][x]:
                        sFaces = (shard + '.f[' + str(x) + ']')
                        cmds.sets(sFaces, forceElement=(sMat + 'SG'), e=True)
                        if self.scanFunc:
                            pm.progressBar('prgsA', q=True, endProgress=True)
                            break
        Common.fixInNormal(self.arrShards, self.selArr[0], '_meshSG')

        pm.progressBar('prgsA', edit=True, vis=False)
        pm.button('crChButt', e=True, vis=False)
        pm.button('cancelButt', e=True, vis=False)


class vShatter:
    def __init__(self):
        self.scanFunc = True

    @staticmethod
    def material(obj, R, G, B):
        _name = obj + '_shardMaterial'
        if not cmds.objExists(_name):
            cmds.shadingNode('lambert', asShader=True, name=_name)
            cmds.sets(r=True, nss=True, em=True, name=_name + 'SG')
            cmds.connectAttr((_name + '.outColor'), (_name + 'SG.surfaceShader'), force=True)
            cmds.setAttr((_name + '.color'), R, G, B, type="double3")
        return _name

    @staticmethod
    def chBxTrVtxC(obj, shMesh):
        if pm.checkBox('chBxC', q=True, v=True):
            pm.transferAttributes(obj, shMesh, transferNormals=1, sampleSpace=1)

    def clCommand(self, crButton, clButton, prgBar):
        if not self.scanFunc:
            self.scanFunc = True
        pm.button(crButton, q=True, e=True, vis=True)
        pm.button(clButton, q=True, e=True, vis=False)
        pm.progressBar(prgBar, edit=True, vis=False)

    def selInfCheck(self):
        selObj = cmds.ls(sl=True)
        polyChk = cmds.filterExpand(selObj, ex=True, sm=12)
        if pm.nodeType(polyChk) == 'transform':
            self.vShatter()
        else:
            pm.text('textF', q=True, edit=True, vis=True)

    @staticmethod
    def fill_hole_plus(obj):
        nSelList = OpenMaya.MGlobal.getActiveSelectionList()
        itrMesh = nSelList.getDependNode(0)
        nDagPath = nSelList.getDagPath(0)
        nShape = nDagPath.getPath()
        sMesh = OpenMaya.MFnMesh(nShape)

        itrVtx = OpenMaya.MItMeshEdge(itrMesh)
        nEdge = []
        while not itrVtx.isDone():
            if itrVtx.numConnectedFaces() == 1:
                nEdge.append(itrVtx.index())
            itrVtx.next()

        if nEdge:
            edges = pm.polySelect(obj, eb=nEdge[0], ns=True)
            edges.pop(len(edges) - 1)
            sVert = [sMesh.getEdgeVertices(i) for i in edges]
            sVtx = []
            for i in range(len(edges) - 1):
                for x in sVert[i]:
                    if x in sVert[i + 1] and x not in sVtx:
                        sVtx.append(x)
            for i in sVert:
                for x in i:
                    if x not in sVtx:
                        sVtx.append(x)

            vtxPoint = [sMesh.getPoint(i) for i in sVtx]
            mergeVertices = True
            pointTolerance = 0.0000000001
            sMesh.checkSamePointTwice = True
            sMesh.addPolygon(vtxPoint, mergeVertices, pointTolerance)
            cmds.polyNormal(obj, normalMode=2, userNormalMode=False, ch=False)

    @staticmethod
    def int_point_generator(num, obj):

        """ Generate points inside object mesh """

        cmds.select(obj)
        sel_list = OpenMaya.MGlobal.getActiveSelectionList()
        sel_dag = sel_list.getDagPath(0)
        mesh_obj = OpenMaya.MFnMesh(sel_dag)
        bbPts = mesh_obj.boundingBox

        xPts = 10000 #BBox point
        vX = [random.uniform(bbPts.max[0], bbPts.min[0]) for i in xrange(xPts)]
        vY = [random.uniform(bbPts.max[1], bbPts.min[1]) for i in xrange(xPts)]
        vZ = [random.uniform(bbPts.max[2], bbPts.min[2]) for i in xrange(xPts)]
        vZip = zip(vX, vY, vZ)

        ray_point = OpenMaya.MFloatPointArray()
        [ray_point.append(i) for i in vZip]
        rayDirection = OpenMaya.MFloatVector((bbPts.max[0]*2, bbPts.max[1]*2, bbPts.max[2]*2))
        space = OpenMaya.MSpace.kWorld
        maxParam = 9999999
        testBothDirections = False
        hitPoints = OpenMaya.MFloatPointArray()

        for raySource in ray_point:
            x = mesh_obj.allIntersections(raySource,
                                          rayDirection,
                                          space,
                                          maxParam,
                                          testBothDirections)
            if len(x[0]) % 2 == 1 and len(hitPoints) < num:
                hitPoints.append(raySource)

        targetPoints = [(i.x, i.y, i.z) for i in hitPoints]
        return targetPoints

    @staticmethod
    def copyrator(shapeObj):
        obj = cmds.listRelatives(shapeObj)
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(obj[0])
        shape = selection_list.getDependNode(0)
        prt = OpenMaya.MObject.kNullObj
        mesh_fn = OpenMaya.MFnMesh()
        mesh_fn.copy(shape, prt)
        _name = cmds.rename('polySurface1', shapeObj[0] + '_copy')
        return _name

    def inMat(self, workingObj, surfaceMat):
        aFaces = cmds.polyEvaluate(workingObj, face=True)

        self.fill_hole_plus(workingObj)

        bFaces = cmds.polyEvaluate(workingObj, face=True)
        newFaces = bFaces - aFaces
        cFaces = ('%s.f[ %d ]' % (workingObj, (bFaces + newFaces - 1)))
        cmds.sets(cFaces, forceElement=(surfaceMat + 'SG'), e=True)

    @staticmethod
    def creator(vOut, vIn, shardObj):
        target = [(trg1 - trg2) for (trg1, trg2) in zip(vOut, vIn)]
        trgetCenter = [(trg1 + trg2) / 2 for (trg1, trg2) in zip(vIn, vOut)]
        targetAngle = cmds.angleBetween(euler=True, v1=[0, 0, 1], v2=target, ch=False)
        cmds.polyCut(shardObj, df=True, cutPlaneCenter=trgetCenter, cutPlaneRotate=targetAngle, ch=False)

    def vShatter(self):
        pm.text('textF', edit=True, vis=False)
        num = pm.intFieldGrp('shField', q=True, value1=True)

        sel = cmds.ls(sl=True)
        cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=1, pn=True)
        surfaceMat = Common.shaderInit(sel[0], 1.0, 0.583, 0.583, 'inMat_')
        outMat = self.material(sel[0], 0.78, 0.78, 0.78)
        bbPts = self.int_point_generator(num, sel)

        cmds.setAttr(sel[0] + '.visibility', 0)
        shardGroup = cmds.group(em=True, name=sel[0] + '_shards')

        cmds.undoInfo(state=False)
        cmds.setAttr(sel[0] + '.visibility', 0)
        step = 0
        pm.button('shButt', e=True, vis=False)
        pm.button('clButt', e=True, vis=True)
        self.scanFunc = False

        for vOut in bbPts:
            if self.scanFunc:
                pm.progressBar('prgs', q=True, endProgress=True)
                break
            step += 1
            pm.progressBar('prgs', edit=True, progress=step, vis=True, maxValue=num)
            shardObj = self.copyrator(sel)
            cmds.sets(shardObj, forceElement=(outMat + 'SG'), e=True)

            cmds.setAttr(shardObj + '.visibility', 1)
            cmds.parent(shardObj, shardGroup)
            for vIn in bbPts:
                if vOut != vIn:
                    self.creator(vOut, vIn, shardObj)
                    self.inMat(shardObj, surfaceMat)
            cmds.xform(shardObj, cp=True)
            pm.rename(shardObj, (sel[0] + '_shard_' + str(step)))
            pm.refresh(cv=True)
        self.chBxTrVtxC(sel[0], shardGroup)
        Common.fixInNormal(shardGroup, sel[0], 'SG')

        cmds.xform(shardGroup, cp=True)
        pm.progressBar('prgs', edit=True, vis=False)
        pm.button('shButt', e=True, vis=True)
        pm.button('clButt', e=True, vis=False)
        cmds.undoInfo(state=True)


def initUI():
    UI()

vs = vShatter()
fr = SouPVoronoi()
Common = Common()