# -*- coding: utf8 -*-
# *****************************************************************************
# *                                                                           *
# *    Copyright (c) 2017                                                     *
# *                                                                           *
# *    This program is free software; you can redistribute it and/or modify   *
# *    it under the terms of the GNU Lesser General Public License (LGPL)     *
# *    as published by the Free Software Foundation; either version 2 of      *
# *    the License, or (at your option) any later version.                    *
# *    For detail see the LICENSE text file.                                  *
# *                                                                           *
# *    This program is distributed in the hope that it will be useful,        *
# *    but WITHOUT ANY WARRANTY; without even the implied warranty of         *
# *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                   *
# *    See the  GNU Library General Public License for more details.          *
# *                                                                           *
# *    You should have received a copy of the GNU Library General Public      *
# *    License along with this program; if not, write to the Free Software    *
# *    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
# *    USA                                                                    *
# *                                                                           *
# *****************************************************************************


import Part
from SlopedPlanesPy import _Py


__title__ = "SlopedPlanes Macro"
__author__ = "Damian Caceres Moreno"
__url__ = "http://www.freecadweb.org"
__version__ = ""


class _PyReflex(_Py):

    '''The complementary python object class for reflex corners'''

    def __init__(self):

        ''''''

        self.planes = []
        self.rango = []

    @property
    def planes(self):

        ''''''

        return self._planes

    @planes.setter
    def planes(self, planes):

        ''''''

        self._planes = planes

    @property
    def rango(self):

        ''''''

        return self._rango

    @rango.setter
    def rango(self, rango):

        ''''''

        self._rango = rango

    def virtualizing(self):

        '''virtualizing(self)
        '''

        [pyReflex, pyOppReflex] = self.planes

        pyR = pyReflex.virtualizing()
        pyOppR = pyOppReflex.virtualizing()

        self.planes = [pyR, pyOppR]

    def simulating(self, force=False):

        '''simulating(self, force=False)
        '''

        [pyR, pyOppR] = self.planes

        enormousR = pyR.enormousShape
        enormousOppR = pyOppR.enormousShape

        pyR.simulating([enormousOppR])
        pyOppR.simulating([enormousR])

    def preProcess(self, pyWire):

        '''preProcess(self, pyWire)
        The planes included in a range are cutted between them.
        '''

        # print '### preProcess'

        pyPlaneList = pyWire.planes
        numWire = pyWire.numWire

        for pyReflexPlane in self.planes:
            # print '# pyReflexPlane ', pyReflexPlane.numGeom
            rango = pyReflexPlane.rangoConsolidate
            # print 'rango ', rango
            pyRan = []
            for nG in rango:
                pyPl = pyPlaneList[nG]
                pyRan.append(pyPl)

            for pyPlane in pyRan:
                cList = []
                plane = pyPlane.shape
                if not pyPlane.choped and not pyPlane.aligned:
                    # print 'pyPlane.numGeom ', pyPlane.numGeom

                    control = pyPlane.control
                    rangoPost = pyPlane.rangoConsolidate
                    total = control + rangoPost
                    # print 'total ', total
                    num = -1
                    for nG in rango:
                        num += 1
                        if nG not in total:
                            pyPl = pyRan[num]
                            # print 'pyPl.numGeom ', nG

                            if not pyPl.reflexed:
                                # print 'a'
                                cList.append(pyPl.shape)
                                control.append(nG)

                            elif pyPl.choped:
                                # print 'b'
                                pass

                            elif pyPl.aligned:
                                # print 'c'
                                pyAli =\
                                    self.selectAlignment(numWire, nG)
                                if pyAli:
                                    cList.extend(pyAli.simulatedAlignment)

                            else:
                                # print 'd'
                                if not pyPlane.reflexed or pyPlane.aligned:
                                    # print 'dd'
                                    cList.append(pyPl.simulatedShape)
                                else:
                                    # print 'ddd'
                                    pyReflexList =\
                                        self.selectAllReflex(numWire, nG)
                                    for pyReflex in pyReflexList:
                                        [pyOne, pyTwo] = pyReflex.planes
                                        if pyPlane.numGeom in\
                                           [pyOne.numGeom, pyTwo.numGeom]:
                                            # print 'ddd1'
                                            break
                                    else:
                                        # print 'ddd2'
                                        cList.append(pyPl.simulatedShape)

                if cList:
                    # print 'cList', cList
                    gS = pyPlane.geomShape
                    plane = self.cutting(plane, cList, gS)
                    pyPlane.shape = plane
                    # print 'plane ', plane

    def reflexing(self, pyWire):

        '''reflexing(self, pyWire)
        '''

        pyPlaneList = self.planes
        pyR = pyPlaneList[0]
        pyOppR = pyPlaneList[1]

        direction = "forward"
        print '### direction ', direction
        print(pyR.numGeom, pyOppR.numGeom)
        if not pyR.cutter:
            self.twin(pyWire, pyR, pyOppR, direction)

        direction = "backward"
        print '### direction ', direction
        print(pyOppR.numGeom, pyR.numGeom)
        if not pyOppR.cutter:
            self.twin(pyWire, pyOppR, pyR, direction)

    def twin(self, pyWire, pyR, pyOppR, direction):

        '''twin(self, pyWire, pyR, pyOppR, direction)
        '''

        pyPlaneList = pyWire.planes
        control = pyR.control
        oppReflexEnormous = pyOppR.enormousShape
        numWire = pyWire.numWire

        rear = pyR.rear

        for nGeom in rear:
            if nGeom not in control:

                rearPyPl = pyPlaneList[nGeom]

                if rearPyPl.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    rearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated', (numWire, nGeom)

                elif rearPyPl.choped:
                    # print 'b'
                    rearPl = rearPyPl.simulatedShape  # ???
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated ', (numWire, nGeom)

                elif rearPyPl.reflexed:
                    # print 'c'
                    rearPl = rearPyPl.simulatedShape
                    # # OJO
                    # # rearPl = rearPyPl.bigShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear simulated', (numWire, nGeom)

                else:
                    # print 'd'
                    rearPl = rearPyPl.shape
                    # # OJO
                    # # rearPl = rearPyPl.bigShape
                    pyR.addLink('cutter', rearPl)
                    # print 'included rear ', (numWire, nGeom)
                    control.append(nGeom)

        oppRear = pyOppR.rear

        if len(oppRear) == 1:
            nGeom = oppRear[0]
            if nGeom not in control:
                pyOppRear = pyPlaneList[nGeom]

                if pyOppRear.aligned:
                    # print 'a'
                    pyAlign = self.selectAlignment(numWire, nGeom)
                    oppRearPl = pyAlign.simulatedAlignment
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated', (numWire, nGeom)

                elif pyOppRear.choped:
                    # print 'b'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated', (numWire, nGeom)

                elif pyOppRear.reflexed:
                    # print 'c'
                    oppRearPl = pyOppRear.simulatedShape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear simulated ', (numWire, nGeom)

                else:
                    # print 'd'
                    oppRearPl = pyOppRear.shape
                    pyR.addLink('cutter', oppRearPl)
                    # print 'included oppRear ', (numWire, nGeom)
                    control.append(nGeom)

        elif len(oppRear) == 2:

            self.processOppRear(oppRear, direction, pyWire, pyR,
                                pyOppR, oppReflexEnormous)

        rangoCorner = pyR.rangoConsolidate
        # print 'rangoCorner ', rangoCorner

        for nn in rangoCorner:
            if nn not in control:
                if nn not in oppRear:
                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoCorner', direction)

        rangoNext = pyOppR.rangoConsolidate
        # print 'rangoNext ', rangoNext

        if len(rear) == 1:
            for nn in rangoNext:
                if nn not in control:
                    self.processRango(pyWire, pyR, pyOppR, nn, 'rangoNext', direction)

        rangoInter = self.rango
        # print 'rangoInter ', rangoInter

        for nn in rangoInter:
            if nn not in control:
                self.processRango(pyWire, pyR, pyOppR, nn,  'rangoInter', direction)

    def processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                       oppReflexEnormous):

        '''processOppRear(self, oppRear, direction, pyWire, pyR, pyOppR,
                          oppReflexEnormous)
        '''

        pyPlaneList = pyWire.planes
        tolerance = _Py.tolerance
        control = pyR.control

        if direction == "forward":
            nGeom = oppRear[1]
        else:
            nGeom = oppRear[0]

        if nGeom not in control:
            pyOppRear = pyPlaneList[nGeom]

            oppRearPl = pyOppRear.shape.copy()
            pyR.addLink('cutter', oppRearPl)
            # print 'included oppRear ', (pyWire.numWire, nGeom)
            control.append(nGeom)

        if direction == "forward":
            nGeom = oppRear[0]
        else:
            nGeom = oppRear[1]

        if nGeom not in control:
            pyOppRear = pyPlaneList[nGeom]
            oppRearPl = pyOppRear.shape.copy()
            oppRearPl = oppRearPl.cut([oppReflexEnormous], tolerance)

            pointWire = pyWire.coordinates

            if direction == "forward":
                point = pointWire[nGeom+1]
            else:
                point = pointWire[nGeom]

            # print 'point ', point
            vertex = Part.Vertex(point)

            for ff in oppRearPl.Faces:
                section = vertex.section([ff], tolerance)
                if section.Vertexes:
                    pyR.addLink('cutter', ff)
                    # print 'included oppRear rectified ', (pyWire.numWire, nGeom)
                    break

    def processRango(self, pyWire, pyR, pyOppR, nn, kind, direction):

        ''''''

        tolerance = _Py.tolerance
        numWire = pyWire.numWire
        numGeom = pyR.numGeom
        oppReflexEnormous = pyOppR.enormousShape
        pyPlaneList = pyWire.planes

        pyPl = pyPlaneList[nn]
        gS = pyPl.geomShape

        if pyPl.aligned:
            # print 'A'
            pyAlign = self.selectAlignment(numWire, nn)
            pl = pyAlign.simulatedAlignment
            pyR.addLink('cutter', pl)
            # print 'included rango simulated ', (pl, numWire, nn)

        elif pyPl.choped:
            # print 'B'
            pl = pyPl.simulatedShape
            pyR.addLink('cutter', pl)
            # print 'included rango simulated', (pl, numWire, nn)

        elif pyPl.reflexed:
            # print 'C'
            pl = pyPl.simulatedShape.copy()

            rear = pyPl.rear

            forward = pyR.forward
            forwa = pyOppR.forward
            fo = pyPl.forward

            pyReflexList = self.selectAllReflex(numWire, nn)
            ref = False
            for pyReflex in pyReflexList:
                for pyPlane in pyReflex.planes:
                    if pyPlane != pyPl:
                        if numGeom in pyPlane.rear:
                            # print '0'
                            ref = True
                            break

            if ref:
                if kind == 'rangoCorner':
                    # print '00'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif numGeom in rear:
                # print '1'
                pass

            elif pyOppR.numGeom in rear:
                # print '2'

                pl = pyPl.shape.copy()
                pl = self.cutting(pl, [oppReflexEnormous], gS)
                pyR.addLink('cutter', pl)
                # print 'included rango ', (pl, numWire, nn)

                pl = pyPl.simulatedShape.copy()     # Two faces included
                if kind == 'rangoCorner':
                    # print '22'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoCorner':
                # print '4'

                if forward.section([fo], tolerance).Vertexes:
                    # print '42'
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

                else:
                    # print '43'
                    pl = pyPl.shape.copy()
                    # cList = [oppReflexEnormous]
                    rang = self.rang(pyWire, numGeom, nn, direction)
                    # print 'rang ', rang
                    cList = []
                    for mm in rang:
                        pyP = pyPlaneList[mm]
                        if pyP.reflexed:
                            if forward.section([pyP.forward, pyP.backward], tolerance).Vertexes:
                                cList.append(pyP.enormousShape)
                    pl = self.cutting(pl, cList, gS)

            elif kind == 'rangoNext':
                # print '6'

                if forwa.section([gS], tolerance).Vertexes:
                    # print '61'
                    pass

                else:
                    # print '62'
                    pl = pyPl.shape.copy()
                    pl = self.cutting(pl, [oppReflexEnormous], gS)

            elif kind == 'rangoInter':
                # print '7'
                pass

            else:
                #print 'NEW CASE'
                pass

            pyR.addLink('cutter', pl)
            # print 'included rango simulated', (pl, numWire, nn)

        else:
            # print 'D'
            pl = pyPl.shape.copy()

            if kind == 'rangoCorner':
                # print 'D1'
                pl = self.cutting(pl, [oppReflexEnormous], gS)

            pyR.addLink('cutter', pl)
            # print 'included rango ', (pl, numWire, nn)
            pyR.control.append(nn)

    def solveReflex(self, pyWire):

        '''solveReflex(self)
        '''

        print '### solveReflexs'

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print '# ', (pyR.numGeom, pyOppR.numGeom)
        self.processReflex(reflex, oppReflex,
                           pyR, pyOppR,
                           'forward', pyWire)

        print '# ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflex(oppReflex, reflex,
                           pyOppR, pyR,
                           'backward', pyWire)

    def processReflex(self, reflex, oppReflex, pyR, pyOppR,
                      direction, pyWire):

        '''processReflex(self, reflex, oppReflex, pyR, pyOppR,
                         direction, pyWire)
        '''

        if not pyR.rear:
            pyR.cutter = [pyOppR.enormousShape]

        tolerance = _Py.tolerance
        planeList = pyWire.planes

        if isinstance(reflex, Part.Compound):
            secondaries = reflex.Faces[1:]
        else:
            secondaries = []

        aa = reflex.copy()

        cList = [pyOppR.enormousShape]
        if not pyR.aligned:
            cList.extend(pyR.cutter)
        # print 'pyR.cutter ', pyR.cutter, len(pyR.cutter)

        aa = aa.cut(cList, tolerance)
        print 'aa.Faces ', aa.Faces, len(aa.Faces)
        gS = pyR.geomShape

        if pyR.rear:

            rear = pyR.rear
            if len(rear) == 1:
                rr = planeList[rear[0]]
            else:
                if direction == 'forward':
                    rr = planeList[rear[0]]
                else:
                    rr = planeList[rear[1]]

            rrG = rr.geomShape

        cutterList = []
        for ff in aa.Faces:
            section = ff.section([gS], tolerance)
            if not section.Edges:
                section = ff.section([_Py.face], tolerance)
                if section.Edges:
                    cutterList.append(ff)
                elif section.Vertexes:
                    section = ff.section([rrG], tolerance)
                    if not section.Vertexes:
                        cutterList.append(ff)
        print 'cutterList ', cutterList, len(cutterList)

        if cutterList:
            reflex = reflex.cut(cutterList, tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        if not pyR.aligned:
            reflex = reflex.cut(pyR.cutter, tolerance)
            print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

        aList = []
        for ff in reflex.Faces:
            section = ff.section([gS], tolerance)
            if section.Edges:
                aList.append(ff)
                reflex = reflex.removeShape([ff])
                break
        print 'aList ', aList, len(aList)

        if pyR.rear:

            if not rr.aligned:

                if reflex.Faces:
                    reflex = reflex.cut([pyOppR.enormousShape], tolerance)
                    print 'reflex.Faces ', reflex.Faces, len(reflex.Faces)

                # TODO corregir
                # TODO cambiar a rango con dirección

                corner = []
                for num in pyR.rangoConsolidate:
                    # print 'num ', num
                    pyPl = planeList[num]
                    if pyPl.aligned:
                        # print 'a'
                        pyAlign = self.selectAlignment(pyPl.numWire, num)
                        corner.extend(pyAlign.simulatedAlignment)
                        # print pyAlign.simulatedAlignment
                    elif pyPl.reflexed:
                        # print 'b'
                        corner.append(pyPl.simulatedShape)
                        # print pyPl.simulatedShape
                    else:
                        # print 'c'
                        pl = pyPl.shape.copy()
                        '''gShape = pyPl.geomShape
                        pl = self.cutting(pl, [pyOppR.enormousShape, rr.enormousShape], gShape)'''
                        corner.append(pl)
                        # print pyPl.shape

                bList = []
                for ff in reflex.Faces:
                    # print 'a'
                    section = ff.section(aList, tolerance)
                    if not section.Edges:
                        # print 'b'
                        section = ff.section(cutterList, tolerance)
                        if section.Edges:
                            # print 'c'
                            section = ff.section([pyR.forward], tolerance)
                            if not section.Edges:
                                # print 'd'
                                section = ff.section([pyR.backward], tolerance)
                                if not section.Edges:
                                    # print 'e'
                                    for pp in corner:
                                        section = ff.section([pp], tolerance)
                                        if section.Edges:
                                            # print 'f'
                                            bList.append(ff)
                                            break

                # print 'bList ', bList

                aList.extend(secondaries)
                aList.extend(bList)
                print 'aList ', aList

        compound = Part.makeCompound(aList)
        pyR.shape = compound

    def solveReflexTwo(self, pyWire):

        ''''''

        [pyR, pyOppR] = self.planes

        reflex = pyR.shape.copy()
        oppReflex = pyOppR.shape.copy()

        print '### ', (pyR.numGeom, pyOppR.numGeom), reflex.Faces, oppReflex.Faces
        self.processReflexTwo(reflex, oppReflex, pyR, pyOppR, pyWire)

        print '### ', (pyOppR.numGeom, pyR.numGeom)
        self.processReflexTwo(oppReflex, reflex, pyOppR, pyR, pyWire)

    def processReflexTwo(self,reflex, oppReflex, pyR, pyOppR, pyWire):

        '''
        
        '''

        reflex = reflex.copy()
        gS = pyR.geomShape
        tolerance = _Py.tolerance

        if not oppReflex.section([pyOppR.forward, pyOppR.backward], tolerance).Edges:
            print 'A'

            aList = []

            ff = reflex.Faces[0]
            ff = self.cutting(ff, [oppReflex], gS)
            aList.append(ff)

            if len(reflex.Faces) > 1:
                dList = [pyPlane.shape for pyPlane in pyWire.planes
                         if pyPlane.numGeom is not pyR.numGeom and
                         pyPlane.shape]
                comp = Part.makeCompound(dList)

            brea = False
            for ff in reflex.Faces[1:]:
                if brea:
                    break
                ff = ff.cut([oppReflex], tolerance)
                for f in ff.Faces:
                    if brea:
                        break
                    section = f.section([comp], tolerance)
                    if len(section.Edges) >= len(f.Edges):
                        aList.append(f)
                        brea = True
                        break

            compound = Part.makeCompound(aList)
            pyR.shape = compound

        else:
            if reflex.section([pyR.forward, pyR.backward], tolerance).Edges:
                print 'B'

                reflex = reflex.cut([oppReflex], tolerance)
                gS = pyR.geomShape
                ff = self.selectFace(reflex.Faces, gS)
                fList = [ff]
                reflex = reflex.removeShape([ff])
                for ff in reflex.Faces:
                    section = ff.section([pyR.forward, pyR.backward], tolerance)
                    if not section.Edges:
                        fList.append(ff)
                compound = Part.makeCompound(fList)
                pyR.shape = compound

            else:
                pass
                print 'C'

    def postProcess(self, pyWire):

        ''''''

        # print '### postProcess'

        planeList = self.planes
        tolerance = _Py.tolerance

        forw = planeList[1].forward

        for pyPl in self.planes:
            pl = pyPl.shape

            if len(pl.Faces) == 1:
                # print '# cutted ', pyPl.numGeom

                forward = pyPl.forward
                gS = pyPl.geomShape

                cutterList = []
                for pyReflex in pyWire.reflexs:
                    if pyReflex != self:
                        for pyPlane in pyReflex.planes:
                            if pyPlane not in self.planes:
                                # print pyPlane.numGeom

                                fo = pyPlane.forward
                                ba = pyPlane.backward

                                section = fo.section([forward], tolerance)
                                sect = fo.section([forw], tolerance)

                                if section.Vertexes or sect.Vertexes:
                                    # print 'a'

                                    plane = pyPlane.shape

                                    # subir o invertir
                                    section =\
                                        plane.section([fo, ba], tolerance)

                                    if not section.Edges:
                                        # print 'b'

                                        cutterList.append(plane)
                                        # print '# included cutter ', pyPlane.numGeom
                                        pyPl.control.append(pyPlane.numGeom)

                if cutterList:
                    # print 'cutterList', cutterList

                    ff = pl.Faces[0]
                    ff = self.cutting(ff, cutterList, gS)
                    compound = Part.Compound([ff])
                    pyPl.shape = compound

            forw = planeList[0].forward

    def rearing(self, pyWire, case):

        '''rearing(self, pyWire)
        '''

        direction = "forward"
        for pyPlane in self.planes:
            if not pyPlane.aligned:
                if pyPlane.rear:
                    pyPlane.rearing(pyWire, self, direction, case)
            direction = "backward"

    def rangging(self, pyWire):

        '''rangging(self, pyWire)
        '''

        lenWire = len(pyWire.planes)

        pyR = self.planes[0]
        pyOppR = self.planes[1]
        rear = pyR.rear
        oppRear = pyOppR.rear

        if rear and oppRear:

            rG = rear[0]
            try:
                oG = oppRear[1]
            except IndexError:
                oG = oppRear[0]

            if oG > rG:
                ran = range(rG+1, oG)

            elif oG < rG:
                ranA = range(rG+1, lenWire)
                ranB = range(0, oG)
                ran = ranA + ranB

            else:
                ran = []

            self.rango = ran

    def rang(self, pyWire, g1, g2, direction):

        ''''''

        # print(g1, g2)

        lenWire = len(pyWire.planes)

        if direction == 'forward':
            # print 'forward'
            if g2 > g1:
                # print 'a'
                ran = range(g1+1, g2)
            else:
                # print 'b'
                ranA = range(g1+1, lenWire)
                ranB = range(0, g2)
                ran = ranA + ranB

        else:
            # print 'backward'
            if g1 > g2:
                # print 'aa'
                ran = range(g2+1, g1)
            else:
                # print 'bb'
                ranB = range(0, g2)
                ranA = range(g1+1, lenWire)
                ran = ranA + ranB

        return ran
