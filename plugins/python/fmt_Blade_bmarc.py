#By Minmode

from inc_noesis import *
from vmd import Vmd
import os

#Options
printMatInfo = False #Print extra material info
exportVmd = True
pmxScale = 12.5

def registerNoesisTypes():
    handle = noesis.register("Blade Animation", ".bmarc")
    noesis.setHandlerTypeCheck(handle, bmarcAnimCheckType)
    noesis.setHandlerLoadModel(handle, bmarcAnimLoadModel)

    handle = noesis.register("Blade Model", ".bmarc")
    noesis.setHandlerTypeCheck(handle, bmarcCheckType)
    noesis.setHandlerLoadModel(handle, bmarcLoadModel)

    handle = noesis.register("Blade Camera", ".bscam")
    noesis.setHandlerTypeCheck(handle, bscamCheckType)
    noesis.setHandlerLoadModel(handle, bscamLoadModel)

    handle = noesis.register("Blade Texture", ".btx")
    noesis.setHandlerTypeCheck(handle, btxCheckType)
    noesis.setHandlerLoadRGBA(handle, btxLoadRGBA)

    handle = noesis.register("Blade Texture Pack", ".pac")
    noesis.setHandlerTypeCheck(handle, pacCheckType)
    noesis.setHandlerLoadRGBA(handle, pacLoadRGBA)
    return 1

def bmarcAnimCheckType(data):
    if not rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName())).startswith("mot_") and not rapi.getDirForFilePath(rapi.getLastCheckedName()).endswith("motion\\"):
        return 0
    bs = NoeBitStream(data)
    if len(data) < 0x08:
        return 0
    magic = bs.readBytes(0x08).decode("ASCII").rstrip("\0")
    if magic != "BMAR104":
        return 0
    return 1

def bmarcCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 0x08:
        return 0
    magic = bs.readBytes(0x08).decode("ASCII").rstrip("\0")
    if magic != "BMAR104":
        return 0
    return 1

def btxCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 0x04:
        return 0
    magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
    if magic != "btx":
        return 0
    return 1

def pacCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 0x04:
        return 0
    magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
    if magic != "ARC":
        return 0
    return 1

def bscamCheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 0x04:
        return 0
    magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
    if magic != "BSCM":
        return 0
    return 1

def bmarcLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    fileDir = rapi.getDirForFilePath(rapi.getLastCheckedName())
    bmarc = Arc(fileDir, [], {})
    pacData = getFileData(fileDir, "texture.pac")
    if pacData:
        test = pacCheckType(pacData)
        if test == 0:
            noesis.messagePrompt("Invalid texture file.")
            return 0
        pac = Arc(None, [], {})
        pac.readArc(NoeBitStream(pacData))
        bmarc.texList = pac.texList
        bmarc.texDict = bmarc.texDict
    bmarc.readArc(NoeBitStream(data[0x08:]))
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(bmarc.texList, bmarc.matList))
    mdlList.append(mdl); mdl.setBones(bmarc.boneList)
    return 1
    
def bmarcAnimLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    modelDir = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Model File", "Select a bmarc model file to open.", noesis.getSelectedFile(), None)
    if isinstance(modelDir, str):
        fileDir = rapi.getDirForFilePath(modelDir)
        test = bmarcCheckType(rapi.loadIntoByteArray(modelDir))
        if test == 0:
            noesis.messagePrompt("Invalid model file.")
            return 0
        bmarc = Arc(fileDir, [], {})
        pacData = getFileData(fileDir, "texture.pac")
        if pacData:
            test = pacCheckType(pacData)
            if test == 0:
                noesis.messagePrompt("Invalid texture file.")
                return 0
            pac = Arc(None, [], {})
            pac.readArc(NoeBitStream(pacData))
            bmarc.texList = pac.texList
            bmarc.texDict = bmarc.texDict
        bmarc.readArc(NoeBitStream(rapi.loadIntoByteArray(modelDir)[0x08:]))
    else:
        noesis.messagePrompt("Invalid input.")
        return 0
    bma = Arc(None, bmarc.boneList, bmarc.boneDict)
    bma.readArc(NoeBitStream(data[0x08:]))
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(bmarc.texList, bmarc.matList))
    if bma.animList != []:
        mdl.setAnims(bma.animList)
        rapi.setPreviewOption("setAnimSpeed", "60")
        if exportVmd:
            vmdExport(bma.animNameList, [bma.endFrame + 1], bma.animList, [], "SIFAC.bone", None)
    mdlList.append(mdl); mdl.setBones(bmarc.boneList)
    return 1

def bscamLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    fileName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
    bscam = Bscm()
    bscam.readBscm(NoeBitStream(data), fileName)
    mdl = NoeModel()
    if bscam.animList != []:
        mdl.setAnims(bscam.animList)
        rapi.setPreviewOption("setAnimSpeed", "60")
        if exportVmd:
            vmdExport([fileName], [bscam.endFrame + 1], bscam.animList, [], "SIFAC.bone", None)
    mdlList.append(mdl); mdl.setBones(bscam.boneList)
    return 1

def btxLoadRGBA(data, texList):
    btx = Btx(texList, {})
    btx.readBtx(NoeBitStream(data))
    return 1

def pacLoadRGBA(data, texList):
    pac = Arc(None, [], {})
    pac.readArc(NoeBitStream(data))
    texList.extend(pac.texList)
    return 1

class Arc:
    
    def __init__(self, fileDir, boneList, boneDict):
        self.fileDir = fileDir
        self.boneList = boneList
        self.boneDict = boneDict
        self.texList = []
        self.texDict = {}
        self.matList = []
        self.matDict = {}
        self.matInfo = []
        self.morphList = []
        self.animList = []
        self.animNameList = []
        self.endFrame = 0
        
    def readArc(self, bs):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        unk1 = bs.readUShort()
        unk2 = bs.readUShort()
        fileCount = bs.readInt()
        unk3 = bs.readUInt()
        fileName = bs.readBytes(0x20).decode("ASCII").rstrip("\0")
        fileOff = []
        fileType = []
        for i in range(fileCount):
            fileOff.append(bs.readUInt())
        padding(bs, 0x20)
        for i in range(fileCount):
            fileType.append(bs.readBytes(0x04).decode("ASCII").rstrip("\0"))
            unk1 = bs.readUShort()
            idx = bs.readUShort()
            fileHash = bs.readUInt()
            unk2 = bs.readUShort()
            nameSize = bs.readUShort()
            unk3 = bs.readUInt()
            name = bs.readBytes(nameSize).decode("ASCII").rstrip("\0")
            padding(bs, 0x20)
        for i in range(fileCount):
            self.loadFiles(bs, fileOff[i], fileType[i], [fileOff, fileType], name)

    def loadFiles(self, bs, fileOff, fileType, fileList, name):
        bs.seek(fileOff, NOESEEK_ABS)
        dataSize = bs.readUInt()
        dataOff = bs.readUShort()
        cmpFlag = bs.readUByte()
        bs.seek(fileOff + dataOff, NOESEEK_ABS)
        data = bs.readBytes(dataSize)
        if cmpFlag:
            cs = NoeBitStream(data)
            magic = cs.readBytes(0x04).decode("ASCII").rstrip("\0")
            if magic == "cmp":
                cmpType = cs.readBytes(0x04).decode("ASCII").rstrip("\0")
                zsize = cs.readUInt()
                size = cs.readUInt()
                cmpData = cs.readBytes(zsize)
                if cmpType == "zlib":
                    data = rapi.decompInflate(cmpData, size)
        if fileType == "BML":
            if "BMT" in fileList[1]:
                bmtIdx = fileList[1].index("BMT")
                self.loadFiles(bs, fileList[0][bmtIdx], "morph", None, name)
            bml = Bml(self.fileDir, name, self.texList, self.texDict, self.matList, self.matDict, self.matInfo, self.morphList)
            bml.readBml(NoeBitStream(data))
            self.boneList = bml.boneList
            self.boneDict = bml.boneDict
        elif fileType == "BMD":
            bmd = Bmd(self.matList, self.matDict, self.matInfo)
            bmd.readBmd(NoeBitStream(data))
        elif fileType == "BMA":
            bma = Bma(self.boneList, self.boneDict)
            bma.readBma(NoeBitStream(data))
            if bma.kfBoneList != []:
                self.animList.append(NoeKeyFramedAnim(name, self.boneList, bma.kfBoneList, 1.0))
                self.animNameList.append(name)
                self.endFrame = bma.endFrame
        elif fileType == "morph":
            bmt = Bmt(self.morphList)
            bmt.readBmt(NoeBitStream(data[0x0C:]))
        elif fileType == "tex":
            tex = Btx(self.texList, self.texDict)
            tex.readBtx(NoeBitStream(data))

class Bml:
    
    def __init__(self, fileDir, fileName, texList, texDict, matList, matDict, matInfo, morphList):
        self.fileDir = fileDir
        self.fileName = fileName
        self.texList = texList
        self.texDict = texDict
        self.matList = matList
        self.matDict = matDict
        self.matInfo = matInfo
        self.morphList = morphList
        self.boneList = []
        self.boneMap = []
        self.boneDict = {}
        self.meshList = []
        self.gbl = False
        self.mtxList = []
        
    def readBml(self, bs):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        chunkSize = bs.readUInt()
        unk = bs.readUInt()
        meshCount = bs.readShort()
        nodeCount = bs.readShort()
        mateCount = bs.readShort()
        mtxpCount = bs.readShort()
        drawCount = bs.readShort()
        txtrCount = bs.readShort()
        unk1Count = bs.readShort()
        unk2Count = bs.readShort()
        self.readChunk(bs)

    def readChunk(self, bs):
        while True:
            magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
            if magic == "":
                break
            chunkSize = bs.readUInt()
            unk = bs.readUInt()
            if magic == "NODE":
                self.readNode(bs)
            elif magic == "MATE":
                self.readMate(bs)
            elif magic == "MESH":
                self.readMesh(bs)
            elif magic == "MTXP":
                self.readMtxp(bs)
            elif magic == "DRAW":
                self.readDraw(bs)
            elif magic == "TXTR":
                self.readTxtr(bs)
            else:
                bs.seek(chunkSize, NOESEEK_REL)
            padding(bs, 0x04)

    def readNode(self, bs):
        nodeName = getOffString(bs, bs.readUInt64())
        if nodeName in self.boneDict:
            nodeName += "_dup"
        parentName = getOffString(bs, bs.readUInt64())
        boneMtx = NoeMat43()
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        boneMtx = NoeAngles((bs.readFloat(), bs.readFloat(), bs.readFloat())).toDegrees().toMat43_XYZ()
        boneMtx[0] *= scl[0]
        boneMtx[1] *= scl[1]
        boneMtx[2] *= scl[2]
        boneMtx[3] = pos
        bs.seek(0x34, NOESEEK_REL)
        if nodeName.startswith("Bip001_"):
            nodeName = nodeName[7:]
        if parentName.startswith("Bip001_"):
            parentName = parentName[7:]
        newBone = NoeBone(len(self.boneList), nodeName, boneMtx, parentName, None)
        self.boneList.append(newBone)
        self.boneDict[nodeName] = newBone.index

    def readMate(self, bs):
        matName = getOffString(bs, bs.readUInt64())
        texName = getOffString(bs, bs.readUInt64()).rsplit('.', 1)[0]
        unkColor = NoeVec4((bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255))
        modifier = NoeVec4((bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255))
        ambient = NoeVec4((bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255))
        emission = NoeVec4((bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255))
        unkColor = NoeVec4((bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255, bs.readUByte() / 255))
        specParam = bs.readFloat()
        uvOff = NoeVec3((bs.readFloat(), bs.readFloat(), 0.0))
        uvScale = NoeVec3((bs.readFloat(), bs.readFloat(), 1.0))
        if uvOff != NoeVec3((0.0, 0.0, 0.0)) or uvScale != NoeVec3((1.0, 1.0, 1.0)):
            print(uvOff)
            print(uvScale)
        bs.seek(0x10, NOESEEK_REL)
        material = NoeMaterial(matName, "")
        material.setTexture(texName)
        material.setAmbientColor(ambient)
        self.matDict[material.name] = len(self.matList)
        self.matList.append(material)
        self.matInfo.append([modifier, emission])

    def readMesh(self, bs):
        mesh = Mesh()
        mesh.name = getOffString(bs, bs.readUInt64())
        vertBuffOff = bs.readUInt64()
        faceBuffOff = bs.readUInt64()
        faceInfoOff = bs.readUInt64()
        morphOff = bs.readUInt64()
        bs.seek(0x20, NOESEEK_REL)
        unkTypeFlag1 = bs.readUByte()
        mesh.uvFlag = bs.readUByte()
        mesh.tbFlag = bs.readUByte()
        unkTypeFlag2 = bs.readUByte()
        unk = bs.readUInt()
        mesh.faceCount = bs.readUInt()
        vertCount = bs.readInt()
        mesh.faceSize = bs.readUShort()
        mesh.stride = bs.readUShort()
        unkCount1 = bs.readByte()
        mesh.weightCount = bs.readByte()
        unkCount2 = bs.readByte()
        unkCount3 = bs.readByte()
        mesh.morphCount = bs.readUByte()
        mesh.buffFlag = bs.readUByte()
        bs.seek(vertBuffOff - 0x08, NOESEEK_ABS)
        vertBuffSize = bs.readUInt()
        unk = bs.readUInt()
        mesh.vertBuff = bs.readBytes(vertBuffSize)
        mesh.vertCount = vertBuffSize // mesh.stride
        bs.seek(faceBuffOff - 0x08, NOESEEK_ABS)
        faceBuffSize = bs.readUInt()
        unk = bs.readUInt()
        mesh.faceBuff = bs.readBytes(faceBuffSize)
        bs.seek(faceInfoOff, NOESEEK_ABS)
        bs.seek(0x10, NOESEEK_REL)
        mesh.boneMapIdx = bs.readUInt()
        if mesh.morphCount:
            bs.seek(morphOff, NOESEEK_ABS)
            basePosBuff = noesis.deinterleaveBytes(mesh.vertBuff, 0x00, 0x0C, mesh.stride)
            if mesh.buffFlag & 0x01:
                baseNormBuff = noesis.deinterleaveBytes(mesh.vertBuff, 0x34, 0x06, mesh.stride)
            else:
                baseNormBuff = noesis.deinterleaveBytes(mesh.vertBuff, 0x0C, 0x06, mesh.stride)
            basePos = struct.unpack_from("f" * mesh.vertCount * 3, basePosBuff, 0)
            baseNorm = struct.unpack_from("H" * mesh.vertCount * 3, baseNormBuff, 0)
            newBasePos = []
            newBaseNorm = []
            for i in range(mesh.morphCount):
                name = getOffString(bs, bs.readUInt64())
                bs.seek(0x08, NOESEEK_REL)
                posBuff = bytearray()
                normBuff = bytearray()
                morphPosBuff = noesis.deinterleaveBytes(self.morphList[i][0], 0x00, 0x06, 0x08)
                morphNormBuff = noesis.deinterleaveBytes(self.morphList[i][1], 0x00, 0x06, 0x08)
                morphPos = struct.unpack_from("H" * mesh.vertCount * 3, morphPosBuff, 0)
                morphNorm = struct.unpack_from("H" * mesh.vertCount * 3, morphNormBuff, 0)
                if i == 0:
                    for a in range(mesh.vertCount * 3):
                        p = basePos[a] + noesis.getFloat16(morphPos[a])
                        n = noesis.getFloat16(baseNorm[a]) + noesis.getFloat16(morphNorm[a])
                        posBuff += struct.pack("f", p)
                        normBuff += struct.pack("f", n)
                        newBasePos.append(p)
                        newBaseNorm.append(n)
                    mesh.morphBaseBuff = [posBuff, normBuff]
                else:
                    print(name)
                    if "_eye_" in name or "_eyebrow_" in name:
                        for a in range(mesh.vertCount * 3):
                            posBuff += struct.pack("f", newBasePos[a] + noesis.getFloat16(morphPos[a]))
                            normBuff += struct.pack("f", newBaseNorm[a] + noesis.getFloat16(morphNorm[a]))
                    else:
                        for a in range(mesh.vertCount * 3):
                            posBuff += struct.pack("f", basePos[a] + noesis.getFloat16(morphPos[a]))
                            normBuff += struct.pack("f", noesis.getFloat16(baseNorm[a]) + noesis.getFloat16(morphNorm[a]))
                    mesh.morphBuffList.append([posBuff, normBuff])
        self.meshList.append(mesh)

    def readMtxp(self, bs):
        if not self.gbl:
            self.gbl = True
            self.boneList = rapi.multiplyBones(self.boneList)
        indexOff = bs.readUInt64()
        matrixOff = bs.readUInt64()
        unk = bs.readUShort()
        boneCount = bs.readShort()
        bs.seek(indexOff, NOESEEK_ABS)
        bm = []
        for i in range(boneCount):
            bm.append(bs.readUInt())
        bs.seek(matrixOff, NOESEEK_ABS)
        boneMtx = []
        for i in range(boneCount):
            m01, m02, m03, m04 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m11, m12, m13, m14 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m21, m22, m23, m24 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            m31, m32, m33, m34 = [bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()]
            boneMtx.append(NoeMat44([NoeVec4((m01, m02, m03, m04)), NoeVec4((m11, m12, m13, m14)), NoeVec4((m21, m22, m23, m24)), NoeVec4((m31, m32, m33, m34))]).toMat43() * self.boneList[bm[i]]._matrix)
        self.boneMap.append(bm)
        self.mtxList.append(boneMtx)

    def readDraw(self, bs):
        nodeIdx = bs.readUInt()
        meshIdx = bs.readUInt()
        matIdx = bs.readUInt()
        unk2 = bs.readUInt()
        mesh = self.meshList[meshIdx]
        if mesh.name == "unified_mesh":
            return
        rapi.rpgSetName(mesh.name)
        rapi.rpgSetMaterial(self.matList[matIdx].name)
        if mesh.buffFlag & 0x01 and self.fileName.startswith("mod_"):
            rapi.rpgSetTransform(self.boneList[0]._matrix)
        elif mesh.buffFlag & 0x01:
            idxBuff = noesis.deinterleaveBytes(mesh.vertBuff, 0x1C, 0x04, mesh.stride)
            idx = struct.unpack_from("B", idxBuff, 0)[0]
            rapi.rpgSetTransform(self.mtxList[mesh.boneMapIdx][idx])
        else:
            rapi.rpgSetTransform(self.boneList[nodeIdx]._matrix)
        if mesh.morphCount:
            for morph in mesh.morphBuffList:
                rapi.rpgFeedMorphTargetPositions(morph[0], noesis.RPGEODATA_FLOAT, 0x0C)
                rapi.rpgFeedMorphTargetNormals(morph[1], noesis.RPGEODATA_FLOAT, 0x0C)
                rapi.rpgCommitMorphFrame(mesh.vertCount)
            rapi.rpgCommitMorphFrameSet()
        if mesh.morphCount:
            rapi.rpgBindPositionBuffer(mesh.morphBaseBuff[0], noesis.RPGEODATA_FLOAT, 0x0C)
        else:
            rapi.rpgBindPositionBufferOfs(mesh.vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, 0x00)
        off = 0x0C
        if mesh.buffFlag & 0x01:
            rapi.rpgSetBoneMap(self.boneMap[mesh.boneMapIdx])
            if mesh.weightCount <= 0x04:
                rapi.rpgBindBoneWeightBufferOfs(mesh.vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, off, 4)
                rapi.rpgBindBoneIndexBufferOfs(mesh.vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off + 0x10, 4)
            else:
                w1 = noesis.deinterleaveBytes(mesh.vertBuff, off, 0x10, mesh.stride)
                i1 = noesis.deinterleaveBytes(mesh.vertBuff, off + 0x10, 0x04, mesh.stride)
                w2 = noesis.deinterleaveBytes(mesh.vertBuff, off + 0x14, 0x10, mesh.stride)
                i2 = noesis.deinterleaveBytes(mesh.vertBuff, off + 0x24, 0x04, mesh.stride)
                w1 = [w1[i:i+0x10] for i in range(0, len(w1), 0x10)]
                w2 = [w2[i:i+0x10] for i in range(0, len(w2), 0x10)]
                i1 = [i1[i:i+0x04] for i in range(0, len(i1), 0x04)]
                i2 = [i2[i:i+0x04] for i in range(0, len(i2), 0x04)]
                weightBuff = bytearray()
                indexBuff = bytearray()
                for i in range(mesh.vertCount):
                    weightBuff += w1[i]
                    weightBuff += w2[i]
                    indexBuff += i1[i]
                    indexBuff += i2[i]
                rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 0x20, 8)
                rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_UBYTE, 0x08, 8)
            off += 0x28
        else:
            rapi.rpgSetBoneMap([nodeIdx])
            weightBuff = struct.pack("f" * mesh.vertCount, * [1.0] * mesh.vertCount)
            indexBuff = struct.pack("B" * mesh.vertCount, * [0] * mesh.vertCount)
            rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 0x04, 1)
            rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_UBYTE, 0x01, 1)
        if mesh.morphCount:
            rapi.rpgBindNormalBuffer(mesh.morphBaseBuff[1], noesis.RPGEODATA_FLOAT, 0x0C)
            normBuff = mesh.morphBaseBuff[1]
        else:
            rapi.rpgBindNormalBufferOfs(mesh.vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.stride, off)
            normBuff = noesis.deinterleaveBytes(mesh.vertBuff, off, 0x06, mesh.stride)
        off += 0x08
        rapi.rpgBindColorBufferOfs(mesh.vertBuff, noesis.RPGEODATA_UBYTE, mesh.stride, off, 4)
        off += 0x04
        if mesh.uvFlag & 0x01:
            rapi.rpgBindUV1BufferOfs(mesh.vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, off)
            off += 0x08
        elif mesh.uvFlag & 0x04:
            rapi.rpgBindUV1BufferOfs(mesh.vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.stride, off)
            off += 0x04
        if mesh.buffFlag & 0x04:
            if mesh.uvFlag & 0x10:
                rapi.rpgBindUV2BufferOfs(mesh.vertBuff, noesis.RPGEODATA_FLOAT, mesh.stride, off)
                off += 0x08
            elif mesh.uvFlag & 0x40:
                rapi.rpgBindUV2BufferOfs(mesh.vertBuff, noesis.RPGEODATA_HALFFLOAT, mesh.stride, off)
                off += 0x04
        if mesh.tbFlag & 0x04:
            tanBuff = noesis.deinterleaveBytes(mesh.vertBuff, off, 0x0C, mesh.stride)
            biNormBuff = noesis.deinterleaveBytes(mesh.vertBuff, off + 0x0C, 0x0C, mesh.stride)
            if mesh.morphCount:
                rapi.rpgBindTangentBuffer(rapi.tangentMatricesToTan4(mesh.vertCount, normBuff, noesis.RPGEODATA_FLOAT, 0x0C, tanBuff, noesis.RPGEODATA_FLOAT, 0x0C, biNormBuff, noesis.RPGEODATA_FLOAT, 0x0C), noesis.RPGEODATA_FLOAT, 0x10)
            else:
                rapi.rpgBindTangentBuffer(rapi.tangentMatricesToTan4(mesh.vertCount, normBuff, noesis.RPGEODATA_HALFFLOAT, 0x06, tanBuff, noesis.RPGEODATA_FLOAT, 0x0C, biNormBuff, noesis.RPGEODATA_FLOAT, 0x0C), noesis.RPGEODATA_FLOAT, 0x10)
        elif mesh.tbFlag & 0x08:
            tanBuff = noesis.deinterleaveBytes(mesh.vertBuff, off, 0x06, mesh.stride)
            biNormBuff = noesis.deinterleaveBytes(mesh.vertBuff, off + 0x08, 0x06, mesh.stride)
            if mesh.morphCount:
                rapi.rpgBindTangentBuffer(rapi.tangentMatricesToTan4(mesh.vertCount, normBuff, noesis.RPGEODATA_FLOAT, 0x0C, tanBuff, noesis.RPGEODATA_HALFFLOAT, 0x06, biNormBuff, noesis.RPGEODATA_HALFFLOAT, 0x06), noesis.RPGEODATA_FLOAT, 0x10)
            else:
                rapi.rpgBindTangentBuffer(rapi.tangentMatricesToTan4(mesh.vertCount, normBuff, noesis.RPGEODATA_HALFFLOAT, 0x06, tanBuff, noesis.RPGEODATA_HALFFLOAT, 0x06, biNormBuff, noesis.RPGEODATA_HALFFLOAT, 0x06), noesis.RPGEODATA_FLOAT, 0x10)
        if mesh.faceSize == 0x02:
            rapi.rpgCommitTriangles(mesh.faceBuff, noesis.RPGEODATA_USHORT, mesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
        elif mesh.faceSize == 0x01:
            rapi.rpgCommitTriangles(mesh.faceBuff, noesis.RPGEODATA_UBYTE, mesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
        elif mesh.faceSize == 0x04:
            rapi.rpgCommitTriangles(mesh.faceBuff, noesis.RPGEODATA_UINT, mesh.faceCount, noesis.RPGEO_TRIANGLE, 1)
        rapi.rpgClearBufferBinds()
    
    def readTxtr(self, bs):
        texName = getOffString(bs, bs.readUInt64()).rsplit('.', 1)[0]
        if texName not in self.texDict and rapi.checkFileExists(self.fileDir + texName + ".btx"):
            tex = rapi.loadExternalTex(texName + ".btx")
            self.texDict[texName] = len(self.texList)
            self.texList.append(tex)

class Mesh:
    
    def __init__(self):
        self.name = ""
        self.uvFlag = 0
        self.tbFlag = 0
        self.vertCount = 0
        self.faceCount = 0
        self.faceSize = 0
        self.stride = 0
        self.weightCount = 0
        self.morphCount = 0
        self.buffFlag = 0
        self.vertBuff = bytearray()
        self.boneMapIdx = 0
        self.faceBuff = bytearray()
        self.morphBaseBuff = []
        self.morphBuffList = []

class Bmd:
    
    def __init__(self, matList, matDict, matInfo):
        self.matList = matList
        self.matDict = matDict
        self.matInfo = matInfo
        
    def readBmd(self, bs):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        version = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        unk = bs.readUShort()
        matCount = bs.readShort()
        unk = bs.readUInt()
        unk = bs.readUInt()
        unk = bs.readUInt()
        matOff = bs.readUInt()
        stringOff = bs.readUInt()
        unk = bs.readUInt()
        unk = bs.readUInt()
        texPropCount = bs.readShort()
        shaderPropCount = bs.readShort()
        matPropCount = bs.readShort()
        unk = bs.readUShort()
        texPropOff = bs.readUInt()
        shaderPropOff = bs.readUInt()
        matPropOff = bs.readUInt()
        bs.seek(texPropOff, NOESEEK_ABS)
        texProp = self.texProp(bs, texPropCount)
        bs.seek(shaderPropOff, NOESEEK_ABS)
        shaderProp = self.shaderProp(bs, shaderPropCount)
        bs.seek(matPropOff, NOESEEK_ABS)
        matProp = self.matProp(bs, matPropCount)
        bs.seek(matOff, NOESEEK_ABS)
        self.mat(bs, matCount, shaderProp, matProp, texProp)

    def texProp(self, bs, texPropCount):
        data = []
        for i in range(texPropCount):
            texHash = bs.readUInt()
            if texHash:
                texName = getOffString(bs, bs.readUInt()).rsplit('.', 1)[0]
            else:
                bs.seek(0x04, NOESEEK_REL)
                texName = ""
            texTypeHash = bs.readUInt()
            texType = getOffString(bs, bs.readUInt())
            bs.seek(0x20, NOESEEK_REL)
            data.append([texType, texName])
        return data


    def shaderProp(self, bs, shaderPropCount):
        data = []
        for i in range(shaderPropCount):
            shaderHash = bs.readUInt()
            shaderName = getOffString(bs, bs.readUInt())
            bs.seek(0x08, NOESEEK_REL)
            matPropIdx = bs.readShort()
            texPropIdx = bs.readShort()
            unk = bs.readByte()
            matPropCnt = bs.readByte()
            texPropCnt = bs.readByte()
            bs.seek(0x19, NOESEEK_REL)
            data.append([shaderName, matPropIdx, matPropCnt, texPropIdx, texPropCnt])
        return data

    def matProp(self, bs, matPropCount):
        data = []
        for i in range(matPropCount):
            matPropName = getOffString(bs, bs.readUInt())
            unk = bs.readUInt()
            dataSize = bs.readUShort()
            bs.seek(0x06, NOESEEK_REL)
            vec4 = NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat()))
            data.append([matPropName, vec4])
        return data

    def mat(self, bs, matCount, shaderProp, matProp, texProp):
        for i in range(matCount):
            matHash = bs.readUInt()
            matName = getOffString(bs, bs.readUInt())
            bs.seek(0x1C, NOESEEK_REL)
            shaderIdx = bs.readUShort() + 1
            shaderCnt = bs.readByte()
            bs.seek(0x39, NOESEEK_REL)
            if matName in self.matDict:
                matIdx = self.matDict[matName]
                if printMatInfo:
                    print(matName)
                if shaderCnt == 2:
                    if printMatInfo:
                        print(shaderProp[shaderIdx - 1][0])
                        print(shaderProp[shaderIdx][0])
                        print("vModifierColor " + str(self.matInfo[matIdx][0]))
                        print("vEmissionColor " + str(self.matInfo[matIdx][1]))
                    for a in range(shaderProp[shaderIdx][1], shaderProp[shaderIdx][1] + shaderProp[shaderIdx][2]):
                        if matProp[a][0] == "vSpecularParamFs":
                            self.matList[matIdx].setSpecularColor(matProp[a][1])
                        if printMatInfo:
                            print(matProp[a][0] + " " + str(matProp[a][1]))
                    for a in range(shaderProp[shaderIdx][3], shaderProp[shaderIdx][3] + shaderProp[shaderIdx][4]):
                        if texProp[a][0] == "tSpecularMap" and texProp[a][1] != "":
                            self.matList[matIdx].setSpecularTexture(texProp[a][1])
                        elif texProp[a][0] == "tNormalMap" and texProp[a][1] != "":
                            self.matList[matIdx].setNormalTexture(texProp[a][1])
                        elif texProp[a][0] == "tLightMap" and texProp[a][1] != "":
                            self.matList[matIdx].setOcclTexture(texProp[a][1])
                        elif texProp[a][0] == "tEnvMap" and texProp[a][1] != "":
                            self.matList[matIdx].setEnvTexture(texProp[a][1])
                        if printMatInfo:
                            print(texProp[a][0] + " " + str(texProp[a][1]))
                if printMatInfo:
                    print()

class Bmt:
    
    def __init__(self, morphList):
        self.morphList = morphList
        
    def readBmt(self, bs):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        unk1 = bs.readUShort()
        unk2 = bs.readUShort()
        fileCount = bs.readInt()
        unk3 = bs.readUInt()
        fileName = bs.readBytes(0x20).decode("ASCII").rstrip("\0")
        fileOff = []
        fileType = []
        for i in range(fileCount):
            fileOff.append(bs.readUInt())
        padding(bs, 0x20)
        for i in range(fileCount):
            fileType.append(bs.readBytes(0x04).decode("ASCII").rstrip("\0"))
            unk1 = bs.readUShort()
            idx = bs.readUShort()
            fileHash = bs.readUInt()
            unk2 = bs.readUShort()
            nameSize = bs.readUShort()
            unk3 = bs.readUInt()
            name = bs.readBytes(nameSize).decode("ASCII").rstrip("\0")
            padding(bs, 0x20)
        for i in range(fileCount):
            self.loadFiles(bs, fileOff[i], fileType[i])

    def loadFiles(self, bs, fileOff, fileType):
        bs.seek(fileOff, NOESEEK_ABS)
        dataSize = bs.readUInt()
        dataOff = bs.readUShort()
        cmpFlag = bs.readUByte()
        bs.seek(fileOff + dataOff, NOESEEK_ABS)
        data = bs.readBytes(dataSize)
        if cmpFlag:
            cs = NoeBitStream(data)
            magic = cs.readBytes(0x04).decode("ASCII").rstrip("\0")
            if magic == "cmp":
                cmpType = cs.readBytes(0x04).decode("ASCII").rstrip("\0")
                zsize = cs.readUInt()
                size = cs.readUInt()
                cmpData = cs.readBytes(zsize)
                if cmpType == "zlib":
                    data = rapi.decompInflate(cmpData, size)
        if fileType == "tex":
            self.readMorph(NoeBitStream(data))

    def readMorph(self, bs):
        bs.seek(0x08, NOESEEK_REL)
        width = bs.readUShort()
        height = bs.readUShort()
        unk2 = bs.readUInt()
        byteFormat = bs.readUByte()
        bs.seek(0x07, NOESEEK_REL)
        dataOff = bs.readUInt()
        bs.seek(dataOff, NOESEEK_ABS)
        if byteFormat == 0x1B:
            posData = bs.readBytes(width * height * 0x04)
            normData = bs.readBytes(width * height * 0x04)
        self.morphList.append([posData, normData])

class Bma:
    
    def __init__(self, boneList, boneDict):
        self.boneList = boneList
        self.boneDict = boneDict
        self.kfBoneList = []
        self.frameRate = 0
        self.endFrame = 0
        
    def readBma(self, bs):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        chunkSize = bs.readUInt()
        unk = bs.readUInt()
        version = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        self.frameRate = int(bs.readFloat())
        self.endFrame = int(bs.readFloat())
        if self.endFrame != 0:
            magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
            chunkSize = bs.readUInt()
            unk = bs.readUInt()
            if magic == "ANSK":
                self.readAnsk(bs)

    def readAnsk(self, bs):
        boneOff = bs.readUInt64()
        boneCount = bs.readUShort()
        unkCount = bs.readUShort()
        unk = bs.readUInt()
        bs.seek(boneOff, NOESEEK_ABS)
        for i in range(boneCount):
            name = getOffString(bs, bs.readUInt64())
            if name.startswith("Bip001_"):
                name = name[7:]
            animDataOff = bs.readUInt64()
            animHash = bs.readUInt()
            dataCount = bs.readUShort()
            facialId = bs.readUShort()
            if name in self.boneDict:
                pos = bs.tell()
                bs.seek(animDataOff, NOESEEK_ABS)
                kfBone = NoeKeyFramedBone(self.boneDict[name])
                self.readAnimData(bs, kfBone, dataCount)
                self.kfBoneList.append(kfBone)
                bs.seek(pos, NOESEEK_ABS)

    def readAnimData(self, bs, kfBone, dataCount):
        for i in range(dataCount):
            frameOff = bs.readUInt64()
            keyOff = bs.readUInt64()
            frameCount = bs.readUInt()
            dataType = bs.readUInt()
            pos = bs.tell()
            bs.seek(frameOff, NOESEEK_ABS)
            frames = self.readFrames(bs, frameCount)
            if dataType == 0x00:
                bs.seek(keyOff, NOESEEK_ABS)
                keyFrames = self.readTranKeys(bs, frameCount, frames)
                kfBone.setTranslation(keyFrames, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            elif dataType == 0x02:
                bs.seek(keyOff, NOESEEK_ABS)
                keyFrames = self.readSclKeys(bs, frameCount, frames)
                kfBone.setScale(keyFrames, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
            elif dataType == 0x03:
                bs.seek(keyOff, NOESEEK_ABS)
                keyFrames = self.readRotKeys(bs, frameCount, frames)
                kfBone.setRotation(keyFrames, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
            bs.seek(pos, NOESEEK_ABS)

    def readFrames(self, bs, frameCount):
        frames = []
        for i in range(frameCount):
            frames.append(int(bs.readFloat()))
            keyDataOff = bs.readUInt64()
        return frames

    def readTranKeys(self, bs, frameCount, frames):
        keyFrames = []
        for i in range(frameCount):
            key = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
            keyFrames.append(NoeKeyFramedValue(frames[i], key))
        return keyFrames

    def readSclKeys(self, bs, frameCount, frames):
        keyFrames = []
        for i in range(frameCount):
            key = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
            keyFrames.append(NoeKeyFramedValue(frames[i], key))
        return keyFrames

    def readRotKeys(self, bs, frameCount, frames):
        keyFrames = []
        for i in range(frameCount):
            key = NoeQuat((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat() *-1))
            keyFrames.append(NoeKeyFramedValue(frames[i], key))
        return keyFrames

class Bscm:
    
    def __init__(self):
        self.boneList = []
        self.animList = []
        self.frameRate = 0
        self.endFrame = 0
        
    def readBscm(self, bs, name):
        magic = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        chunkSize = bs.readUInt()
        unk = bs.readUInt()
        version = bs.readBytes(0x04).decode("ASCII").rstrip("\0")
        self.frameRate = int(bs.readFloat())
        self.endFrame = int(bs.readFloat())
        tranCount = bs.readInt()
        rotCount = bs.readInt()
        sclCount = bs.readInt()
        fovCount = bs.readInt()
        pos = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        rot = NoeAngles((bs.readFloat(), bs.readFloat(), bs.readFloat())).toDegrees().toQuat()
        scl = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
        fov = bs.readFloat()
        unk = bs.readUInt()
        tranOff = bs.readUInt64()
        rotOff = bs.readUInt64()
        sclOff = bs.readUInt64()
        fovOff = bs.readUInt64()
        boneMtx = NoeMat43()
        self.boneList.append(NoeBone(0, "Camera", boneMtx, None, -1))
        self.boneList.append(NoeBone(1, "Camera_Fov", boneMtx, None, -1))
        kfBoneList = []
        if self.endFrame != 0:
            kfBone = NoeKeyFramedBone(0)
            bs.seek(tranOff, NOESEEK_ABS)
            self.readTranKeys(bs, tranCount, kfBone, pos)
            bs.seek(rotOff, NOESEEK_ABS)
            self.readRotKeys(bs, rotCount, kfBone, rot)
            bs.seek(sclOff, NOESEEK_ABS)
            self.readSclKeys(bs, sclCount, kfBone, scl)
            kfBoneList.append(kfBone)
            kfBone = NoeKeyFramedBone(1)
            bs.seek(fovOff, NOESEEK_ABS)
            self.readFovKeys(bs, fovCount, kfBone, fov)
            kfBoneList.append(kfBone)
            self.animList.append(NoeKeyFramedAnim(name, self.boneList, kfBoneList, 1.0))

    def readTranKeys(self, bs, tranCount, kfBone, pos):
        if tranCount:
            keyFrames = []
            for i in range(tranCount):
                idx = bs.readUInt()
                unk = bs.readUInt()
                key = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
                keyFrames.append(NoeKeyFramedValue(idx, key))
            kfBone.setTranslation(keyFrames, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            kfBone.setTranslation([NoeKeyFramedValue(0, pos)], noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)

    def readRotKeys(self, bs, rotCount, kfBone, rot):
        if rotCount:
            keyFrames = []
            for i in range(rotCount):
                idx = bs.readUInt()
                unk = bs.readUInt()
                key = NoeQuat((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat() *-1))
                keyFrames.append(NoeKeyFramedValue(idx, key))
            kfBone.setRotation(keyFrames, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            kfBone.setRotation([NoeKeyFramedValue(0, rot)], noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)

    def readSclKeys(self, bs, sclCount, kfBone, scl):
        if sclCount:
            keyFrames = []
            for i in range(sclCount):
                idx = bs.readUInt()
                unk = bs.readUInt()
                key = NoeVec3((bs.readFloat(), bs.readFloat(), bs.readFloat()))
                keyFrames.append(NoeKeyFramedValue(idx, key))
            kfBone.setScale(keyFrames, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            kfBone.setScale([NoeKeyFramedValue(0, scl)], noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)

    def readFovKeys(self, bs, fovCount, kfBone, fov):
        if fovCount:
            keyFrames = []
            for i in range(fovCount):
                idx = bs.readUInt()
                unk = bs.readUInt()
                key = NoeVec3((bs.readFloat(), 0.0, 0.0))
                keyFrames.append(NoeKeyFramedValue(idx, key))
            kfBone.setTranslation(keyFrames, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
        else:
            kfBone.setTranslation(keyFrames, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)

class Btx:
    
    def __init__(self, texList, texDict):
        self.texList = texList
        self.texDict = texDict
        
    def readBtx(self, bs):
        magic = bs.readBytes(4).decode("ASCII").rstrip("\0")
        unk1 = bs.readUInt()
        width = bs.readUShort()
        height = bs.readUShort()
        unk2 = bs.readUInt()
        texFormat = bs.readUByte()
        unkFlag2 = bs.readUByte()
        mipCount = bs.readByte()
        unkFlag3 = bs.readUByte()
        unkFlag4 = bs.readUByte()
        unkFlag5 = bs.readUByte()
        unkFlag6 = bs.readUByte()
        cubeFlag = bs.readUByte()
        dataOff = bs.readUInt()
        unk = bs.readUInt()
        unk3 = bs.readUInt()
        name = getOffString(bs, bs.readUInt())
        bs.seek(dataOff, NOESEEK_ABS)
        if cubeFlag:
            faceSize = width * height
            prevFaceSize = width * height
            for i in range(mipCount):
                prevFaceSize = max(0x10, prevFaceSize // 4)
                faceSize += prevFaceSize
            texData = bytearray()
            for i in range(6):
                bs.seek(dataOff + (faceSize * i), NOESEEK_ABS)
                data = bs.readBytes(width * height)
                texData += rapi.imageDecodeDXT(data, width, height, noesis.FOURCC_BC7)
            tex = NoeTexture(name, width, height, texData, noesis.NOESISTEX_RGBA32)
            tex.setFlags(noesis.NTEXFLAG_CUBEMAP)
        else:
            texFmt = noesis.NOESISTEX_RGBA32
            if texFormat == 0x00:
                texData = bs.readBytes(width * height * 0x04)
                texData = rapi.imageDecodeRaw(texData, width, height, "b8g8r8a8")
            elif texFormat == 0x01:
                texData = bs.readBytes(width * height * 0x03)
                texData = rapi.imageDecodeRaw(texData, width, height, "b8g8r8")
            elif texFormat == 0x02:
                texData = bs.readBytes(width * height * 0x02)
                texData = rapi.imageDecodeRaw(texData, width, height, "b5g6r5")
            elif texFormat == 0x03:
                texData = bs.readBytes(width * height * 0x02)
                texData = rapi.imageDecodeRaw(texData, width, height, "rbg5r5a1")
            elif texFormat == 0x04:
                texData = bs.readBytes(width * height * 0x02)
                texData = rapi.imageDecodeRaw(texData, width, height, "b4g4r4a4")
            elif texFormat == 0x07:
                texFmt = noesis.NOESISTEX_DXT1
                texData = bs.readBytes((width * height) // 2)
            elif texFormat == 0x08:
                texFmt = noesis.NOESISTEX_DXT3
                texData = bs.readBytes(width * height)
            elif texFormat == 0x09:
                texFmt = noesis.NOESISTEX_DXT5
                texData = bs.readBytes(width * height)
            elif texFormat == 0x0A:
                texData = bs.readBytes(width * height)
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
            elif texFormat == 0x0B:
                texData = bs.readBytes(width * height)
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
            elif texFormat == 0x0C:
                texData = bs.readBytes(width * height)
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC6H)
            elif texFormat == 0x0D:
                texData = bs.readBytes(width * height)
                texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
            elif texFormat == 0x10:
                texData = bs.readBytes(width * height)
                texData = rapi.imageDecodeRaw(texData, width, height, "r8")
            tex = NoeTexture(name, width, height, texData, texFmt)
        self.texDict[tex.name] = len(self.texList)
        self.texList.append(tex)

def getFileData(path, name):
    parentDir = os.path.dirname(os.path.dirname(path))
    if rapi.checkFileExists(path + name):
        fileDir = path + name
    elif rapi.checkFileExists(parentDir + "/" + name):
        fileDir = parentDir + "/" + name
    else:
        return
    data = rapi.loadIntoByteArray(fileDir)
    return data

def getOffString(bs, off):
    pos = bs.tell()
    bs.seek(off, NOESEEK_ABS)
    string = bs.readString()
    bs.seek(pos, NOESEEK_ABS)
    return string

def padding(bs, pad):
    offFix = bs.tell()
    while offFix%pad != 0:
        bs.seek(0x01, NOESEEK_REL)
        offFix = bs.tell()

def vmdExport(nameList, frameCountList, animList, morphList, boneDictName, morphDictName):
    outDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Choose a output directory.", "Choose a directory to output your vmd files.", rapi.getDirForFilePath(rapi.getLastCheckedName()), isFolder)
    if outDir == None:
        print("Write vmd failed.")
        return 0
    if not outDir.endswith("\\"):
        outDir += "\\"
    for i in range(len(animList)):
        vmd = Vmd(nameList[i], frameCountList[i], animList[i], [], boneDictName, morphDictName, pmxScale, ["Camera_Fov"])
        vmd.wrtieVmd(outDir)

def isFolder(path):
    if os.path.isdir(path):
        return None
    else:
        return "Directory does not exists."