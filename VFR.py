import maya.cmds as cmds
import random
import pymel.core as pm
import maya.mel as mel

class UI:
    def __init__(self):
        self.scanFunc = False
        self.numPoints = 25
        self.sel = pm.ls(sl=True)
        
        if pm.window('mainWindow', exists=True):
           pm.deleteUI('mainWindow', window=True)
        pm.window('mainWindow')
        pm.window('mainWindow', edit=True, width=392, height=220, exists=False, 
        mxb=False, s=False, rtf=True, mb=True, mbv=True, title="Voronoi shatter")
        pm.showWindow('mainWindow')
        
        #layout A
        pm.tabLayout() 
        pm.formLayout('FAST shatter (SouP)')
        pm.frameLayout(label = "SouP Voronoi shattering")
        pm.columnLayout(adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(w=380, h=10, st="in")
        pm.checkBox('chBxA', label = "Create inside-outside shader (experemental)")
        pm.checkBox('chBxB', label = "Transfer vertexNormal from object")
        pm.separator(w=380, h=5, st = "none")

        pm.separator(w=380, h=5, st="in")
        pm.button('shatterButt', label="SHATTER OBJECT", bgc=(0.0, 0.5, 0.0), c='fr.startCheck()', h=30)
        pm.intFieldGrp('fieldGrp', label="Shards amount:", cal=(1, 'center'), cc='fr.setIntVolume()', vis=False)
        pm.text('textA',label = "Select polygon object!", vis=False, bgc=(1.0, 0.3, 0.0))
        pm.separator(w=380, h=5, st="in")

        pm.separator(w=380, h=5, st="in")
        pm.button('crChButt', label="CREATE SHARDS", c='fr.sepsShard()', h=30, en=False, bgc=(0.58, 0.58, 0.58))
        pm.text('textC', vis=False, bgc=(1.0, 0.3, 0.0))
        pm.button('cancelButt', label="CANCEL", bgc=(1.0, 0.3, 0.0), c="fr.clCommandA('crChButt', 'cancelButt', 'prgsA')", vis=False, h=30)
        pm.separator(w=380, h=5, st="in")
        pm.separator('sepB1', w=380, h=5, st="in", vis=False)
        pm.button('cancelButtB', label="CANCEL", bgc=(1.0, 0.3, 0.0), c="fr.clCommandB()", vis=False, h=30)
        pm.separator('sepB2', w=380, h=5, st="in", vis=False)
        pm.separator(w=380, h=15, st = "none")
        pm.progressBar('prgsA', width=240, isInterruptable=True, vis=False)
        pm.separator(w=380, h=15, st = "none")
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')
        
        #layout B
        pm.formLayout('SLOW shatter (oceanqiu)')
        pm.frameLayout(label = "Voronoi shattering by Ocean Tian Qiu ")
        pm.columnLayout(adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(w=380, h=10, st="in")
        pm.separator(w=380, h=2, st="none")
        pm.checkBox('chBxC', label = "Transfer vertexNormal from object")
        pm.separator(w=380, h=2, st="none")
        pm.separator(w=380, h=10, st="in")
        pm.intFieldGrp('shField', label="number of pieces:", v1=25, cal=(1, 'center'), vis=True, cc='ov.checkNumPoints()')
        pm.separator(w=380, h=5, st="in")
        pm.button('shButt', label="SHATTER", bgc=(0.0, 0.5, 0.0), c='ov.selInfCheck()', vis=True, h=30)
        pm.button('clButt', label="CANCEL", bgc=(1.0, 0.3, 0.0), c="ov.clCommand('shButt', 'clButt', 'prgs')", vis=False, h=30)
        pm.separator(w=380, h=5, st="in")
        pm.progressBar('prgs', width=240, isInterruptable=True, progress = 0, vis=False)
        pm.text('textF', label = "Select polygon object!", vis=False, bgc=(1.0, 0.3, 0.0))
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')
        
        #layout C
        pm.formLayout('BONUS command')
        pm.frameLayout(label = "Bonus command")
        pm.columnLayout(adjustableColumn=True, columnAlign="center", columnAttach=('both', 2))
        pm.separator(w=380, h=75, st="none")
        pm.text('COMING SOON...')
        pm.separator(w=380, h=10, st="none")
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

#common functions        
class Common:
    def surfaceMaterial(self, sel, R, G, B, nameMat):
        mel.eval('MLdeleteUnused;')
        name = (nameMat + sel)
        if cmds.objExists(name) == True:
           print 'WARRING! Duplicate material or shader group... clearing'
        else:
            cmds.shadingNode('lambert', asShader = True, name = name)
            cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = (name + 'SG'))
            cmds.connectAttr((name + '.outColor'), (name + 'SG.surfaceShader'), force = True)
            cmds.setAttr((name + '.color'), R, G, B, type = "double3")
        return name
        
    def fixInNormal(self, obj, mainObj, SG):
        pm.select(obj)
        evalList = pm.ls(sl=True)
        pm.delete(evalList, ch=True)
        evalList = pm.ls(sl=True, o=True, dag=True, exactType = "mesh")
        connList = pm.listConnections(evalList, type='shadingEngine')
        res = []
        for i in connList:
            res.append('inMat_' + mainObj + SG)
        pss = pm.filterExpand(res, sm=34, ex=True)
        pm.select(pss, r=True)
        pm.polySetToFaceNormal(setUserNormal=True)
        pm.select(cl=True)
    
#SoUP 
class SouP_Voronoi(UI):
    def connectAtr(self):
        pm.makeIdentity(apply=True, t=True, r=True, s=True, n=1, pn=True)
        pm.refresh()
        
        pm.separator('sepB1', e=True, vis=True)
        pm.button('cancelButtB', e=True, vis=True)
        pm.separator('sepB2', e=True, vis=True)
        
        pm.button('crChButt', e=True, m=True, en=True, bgc=(0.0, 0.5, 0.0))
        pm.intFieldGrp('fieldGrp', edit=True, cal=(1, 'center'), v1=25, cc='fr.setIntVolume()', vis=True)
        pm.button('shatterButt', e=True, vis=False)
        pm.text('textA', edit=True, vis=False)
        #create variable
        self.selArr = pm.ls(sl=True, o=True, fl=True, r=True)
        self.shapeArr = pm.listRelatives(shapes=True)
        self.scatterNode = pm.createNode('scatter', name=(self.selArr[0] + '_scatterShape'))
        self.shatterNode = pm.createNode('shatter', name=(self.selArr[0] + '_shatterShape'), ss=True)
        self.mesh = pm.createNode('mesh', name=(self.selArr[0] + "_meshShape"))
        self.vSize = pm.intFieldGrp('fieldGrp', q=True, value1=True)
        #connect attribute 
        pm.setAttr((self.selArr[0] + ".visibility"), 1)
        pm.connectAttr((self.selArr[0] + ".worldMatrix"), (self.scatterNode + ".inWorldMatrix"))
        pm.connectAttr((self.shapeArr[0] + ".worldMesh"), (self.scatterNode + ".inGeometry"))
        pm.setAttr(self.scatterNode + ".scatterMode", 0)
        pm.setAttr(self.scatterNode + ".pointDensity", 100000)
        pm.setAttr((self.scatterNode + ".maxNumberOfPoints"), self.vSize)
        pm.connectAttr((self.scatterNode + ".outGeometry"), (self.shatterNode + ".inGeometry"))
        pm.connectAttr((self.scatterNode + ".outPositionPP"), (self.shatterNode + ".inPositionPP"))
        pm.connectAttr((self.shatterNode + ".outGeometry"), (self.mesh + ".inMesh"))
        #refresh(update) before create shards
        pm.refresh()
        fr.createShards()
        
    def clCommandA(self, crButton, clButton, prgBar): # cancel command A
        if self.scanFunc == False:
           self.scanFunc = True
        pm.button(crButton, e=True, vis=True)
        pm.button(clButton, e=True, vis=False)
        pm.progressBar(prgBar, edit=True, vis=False)
        
    def clCommandB(self):
        pm.separator('sepB1', e=True, vis=False)
        pm.button('cancelButtB', e=True, vis=False)
        pm.separator('sepB2', e=True, vis=False)
        
        pm.button('shatterButt', e=True, vis=True)
        pm.button('crChButt', e=True, m=True, en=False, vis=True, bgc=(0.58, 0.58, 0.58))
        pm.intFieldGrp('fieldGrp', e=True, vis=False)
        pm.text('textC', e=True, vis=False)
        
        pm.delete(self.selArr[0]+'_scatter')
        pm.delete(ch=True) 
        
    def checkPolyObj(self, selObj): #check polygon object
        selObj = pm.ls(sl=True)
        polyChk = pm.filterExpand(selObj, ex=True, sm=12)
        if pm.nodeType(polyChk) == 'transform':
            return True
        else:
            return False

    def startCheck(self): #start func
        obj = pm.ls(sl=True)
        if fr.checkPolyObj(obj) == True:
            fr.connectAtr()
        else:
            pm.text('textA', e=True, vis=True)
      
    def chBxOutMat(self): #check box A for set insaide material
        if pm.checkBox('chBxA', q=True, v=True) == True:
           fr.setInsMat()
           
    def chBxTrVtx(self, obj, shMesh): #transfer attribute from main object
        if pm.checkBox('chBxB', q=True, v=True) == True:
           pm.transferAttributes(obj, shMesh, transferNormals=1, sampleSpace=1)
            
    def createShards(self):
        pm.text('textC', edit=True, vis=False)
        pm.setAttr((self.shatterNode + ".autoEvaluate"), 1)
        pm.setAttr((self.selArr[0] + ".visibility"), 0)
        pm.select(self.selArr[0]+'_mesh', r=True)
        pss = pm.ls(sl=True)
        inSM = cmm.surfaceMaterial(pss[0], 0.056, 0.260, 0.030, 'inMat_')
        pm.select(self.mesh)
        pm.hyperShade(assign = inSM)
        fr.chBxTrVtx(self.selArr[0], self.mesh)
        pm.cycleCheck(e=False)
        
    def setIntVolume(self): #intField 
        self.vSize = pm.intFieldGrp('fieldGrp', q=True, value1=True)
        pm.setAttr((self.scatterNode + ".maxNumberOfPoints"), self.vSize)
        print "New shards amount: " + str(self.vSize) + ', please wait...'
        
    def sepsShard(self): #separate shard & apply outside material
        sel = pm.ls(sl=True)
        if sel == []:
           pm.text('textC', label = ('select %s and press button') % (self.selArr[0]+ '_mesh'), edit=True, vis=True)
        else:
            pm.text('textC', edit=True, vis=False)
            pm.separator('sepB1', e=True, vis=False)
            pm.button('cancelButtB', e=True, vis=False)
            pm.separator('sepB2', e=True, vis=False)
        
            pm.select(self.mesh)
            pm.polySeparate(ch=False)
            self.arrShards = pm.ls(sl=True)
            i = 0
            for shard in self.arrShards:
                pm.rename(shard, self.selArr[0] + "_shard_" + str(i))
                pm.xform(cp=True)
                i = i + 1
            pm.rename((self.selArr[0]+'_mesh'), (self.selArr[0] + '_shards'))
            pm.refresh()
            fr.chBxOutMat()
            pm.button('crChButt', e=True, vis=True, m=True, en=False, bgc=(0.58, 0.58, 0.58))
            pm.button('shatterButt', e=True, vis=True)
            pm.intFieldGrp('fieldGrp', e=True, vis=False)
            
    def nNormalCheck(self, obj): #return info for faceNormal
        obj = pm.ls(fl=True)
        fnlListA = pm.polyInfo(faceNormals=True)
        res = [i.split() for i in fnlListA]
        for i in res:
            i.remove(i[0])
        numNormal = [int(i[0].replace(':', '')) for i in res]
    
        numX = [float(i[1]) for i in res]
        numY = [float(i[2]) for i in res]
        numZ = [float(i[3]) for i in res]
        nNormal = [[round(numX[i], 2), round(numY[i], 2), round(numZ[i], 2)] for i in numNormal]
        return nNormal, numNormal
        
    def setInsMat(self): #apply outside shader
        start = pm.timerX()
        pm.select(self.selArr)
        setA = fr.nNormalCheck(self.selArr)
        pm.button('crChButt', e=True, vis=False)
        pm.button('cancelButt', e=True, vis=True)
        self.scanFunc = False
        sMat = cmm.surfaceMaterial(self.selArr[0], 0.78, 0.78, 0.78, 'outMat_')
        pm.select(self.arrShards)
        selB = pm.ls(sl=True, dag=True, g=True)
        inc = 0
        for shard in selB:
            if self.scanFunc == True:
               pm.progressBar('prgsA', q=True, endProgress=True)
               break
            pm.progressBar('prgsA', e=True, progress = inc, vis=True, maxValue = len(selB))
            pm.select(shard, r=True)
            setB = fr.nNormalCheck(shard)
            inc += 1
            pm.refresh()
            for i in setA[1]:
                for x in setB[1]:
                    if setA[0][i] == setB[0][x]:
                       s = (shard + '.f['+str(x)+']')
                       cmds.sets(s, forceElement = (sMat + 'SG'), e=True)
                       if self.scanFunc == True:
                           pm.progressBar('prgsA', q=True, endProgress=True)
                           break
        cmm.fixInNormal(self.arrShards, self.selArr[0], '_meshSG')
    
        pm.progressBar('prgsA', edit=True, vis=False)
        pm.button('crChButt', e=True, vis=True, m=True, en=False)
        pm.button('cancelButt', e=True, vis=False)
        
        totalTime = pm.timerX(startTime = start)
        print "work time %.2f sec. " % (totalTime)

class Ou_Voronoi(UI):
    
    def chBxTrVtxC(self, obj, shMesh):
        if pm.checkBox('chBxC', q=True, v=True) == True:
            pm.transferAttributes(obj, shMesh, transferNormals=1, sampleSpace=1)
            
    def clCommand(self, crButton, clButton, prgBar):
        if self.scanFunc == False:
           self.scanFunc = True
        pm.button(crButton, q=True, e=True, vis=True)
        pm.button(clButton, q=True, e=True, vis=False)
        pm.progressBar(prgBar, edit=True, vis=False)

    def checkNumPoints(self):
        self.numPoints = pm.intFieldGrp('shField', q=True, value1=True)
        if self.numPoints >= 10 :
            print "Shards %d" % (self.numPoints)
        else:
            print "ALERT"

    def selInfCheck(self):
        if fr.checkPolyObj(self.sel) == True:
            ov.voroShatter(self, self.sel, self.numPoints)
        else:
            pm.text('textF', q=True, edit=True, vis=True)

    def voroShatter(self, sel, object, num):
        start = pm.timerX()
        pm.text('textF', edit=True, vis=False)
        pm.intFieldGrp('shField', edit=True, cal=(1, 'center'), cc='ov.checkNumPoints()', vis=True)
        
        sel = cmds.ls(sl=True)
        surfaceMat = cmm.surfaceMaterial(sel[0], 1.0, 0.9, 0.0, 'inMat_')
        bbPoints = cmds.exactWorldBoundingBox(sel[0]) 
    
        self.numPoints = num
        
        voroX = [random.uniform(bbPoints[0], bbPoints[3]) for i in range(self.numPoints)]
        voroY = [random.uniform(bbPoints[1], bbPoints[4]) for i in range(self.numPoints)]
        voroZ = [random.uniform(bbPoints[2], bbPoints[5]) for i in range(self.numPoints)]
        voroPoints = zip(voroX, voroY, voroZ)
    
        cmds.setAttr(sel[0] + '.visibility', 0)
        chunksGrp = cmds.group( em=True, name = sel[0] + '_chunks' )
    
        cmds.undoInfo(state = False)
        cmds.setAttr(sel[0] + '.visibility' , 0)
        step = 0
        pm.button('shButt', e=True, vis=False)
        pm.button('clButt', e=True, vis=True)    
        self.scanFunc = False
        print "Shattering of %d chunks..." % (self.numPoints)
        
        for voroFrom in voroPoints:
            if self.scanFunc == True:
               pm.progressBar('prgs', q=True, endProgress=True)
               break
            step = step + 1
            pm.progressBar('prgs', edit=True, progress = step, vis=True, maxValue = self.numPoints)
        
            # Duplicate the object to cut as shatters
            workingObj = cmds.duplicate(sel[0])
            cmds.setAttr(workingObj[0] + '.visibility', 1)
            cmds.parent(workingObj[0], chunksGrp)
        
            for voroTo in voroPoints:
                if voroFrom != voroTo:
                    # Calculate the Perpendicular Bisector Plane
                    aim = [(vec1-vec2) for (vec1,vec2) in zip(voroFrom,voroTo)]
                    voroCenter = [(vec1 + vec2)/2 for (vec1,vec2) in zip(voroTo,voroFrom)]
                    planeAngle = cmds.angleBetween( euler=True, v1=[0,0,1], v2=aim )
                    # Bullet Shatter
                    cmds.polyCut(workingObj, df=True, cutPlaneCenter = voroCenter, cutPlaneRotate = planeAngle)
                
                    # Applying the material to the cut faces
                    oriFaces = cmds.polyEvaluate(workingObj, face=True)
                    cmds.polyCloseBorder(workingObj, ch=True)
                    aftFaces = cmds.polyEvaluate(workingObj, face=True)
                    newFaces = aftFaces - oriFaces
               
                    cutFaces = ( '%s.f[ %d ]' % (workingObj[0], (aftFaces + newFaces - 1)))
                    cmds.sets(cutFaces, forceElement = (surfaceMat + 'SG'), e=True)
            cmds.xform(workingObj, cp=True)
            pm.rename(workingObj[0], (sel[0] + '_chunk_' + str(step)))
            pm.refresh(cv=True)
        pm.select(chunksGrp)
        ov.chBxTrVtxC(sel[0], chunksGrp)
        cmm.fixInNormal(chunksGrp, sel[0], 'SG')
        
        cmds.xform(chunksGrp, cp=True)
        pm.progressBar('prgs', edit=True, vis=False)
        pm.button('shButt', e=True, vis=True)
        pm.button('clButt', e=True, vis=False)
        cmds.undoInfo(state = True)
        totalTime = pm.timerX(startTime=start)
        print "Shattering of %d chunks completed in %.2f sec" % (step, totalTime)

fr = SouP_Voronoi()
ov = Ou_Voronoi()
cmm = Common()