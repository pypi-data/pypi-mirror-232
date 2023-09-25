import random
from itertools import (permutations, product, combinations,
                       combinations_with_replacement)
from multiprocessing import Pool
from . import constants as c
from .utils import repeatPattern, countUniqueElements, checkInput
from .contour import Segclass, Segment, primeForm, normalForm
from .pspace import Pseg

__all__ = ["CAS",
           "CASV",
           "CIS",
           "CIA",
           "CCV1",
           "CCV2",
           "Csegclass",
           "Cseg"]


class CAS:
    """Contour Adjacency Series"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, cas):
        """
        Constructor method.

        The input cas is an n-element array whose elements +1 and -1 represent
        positive and negative contour moves respectively.

        >>> CAS([1, 1, -1, 1])
        CAS([1, 1, -1, 1])

        :param cas: contour adjacency series.
        :type cas: cas
        """
        self._cas = list(cas)

    def __iter__(self):
        """
        Return a generator object comprising the current CAS elements.

        >>> for i in CAS([1, 1, -1, 1]):
        ...     print(i, end=" ")
        1 1 -1 1
        """
        for element in self._cas:
            yield element

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CAS([1, 1, 1, -1, -1])
        CAS([1, 1, 1, -1, -1])
        """
        return "CAS({})".format(self._cas)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return CAS(self._cas)

    # Property methods --------------------------------------------------------

    @property
    def cas(self):
        """
        Return the current CAS.

        >>> s = CAS([1, 1, 1, -1, -1])
        >>> s.cas
        [1, 1, 1, -1, -1]

        :return: current CAS.
        :rtype: list
        """
        return self._cas

    @cas.setter
    def cas(self, cas_):
        """
        Set the current CAS to the input CAS.

        >>> s = CAS([1, 1, 1, -1, -1])
        >>> s.cas = [-1, -1, 1, 1, 1]
        >>> s.cas
        [-1, -1, 1, 1, 1]

        :param cas_: contour adjacency series.
        :type cas_: cas
        """
        self._cas = list(cas_)

    # Mutator methods ---------------------------------------------------------

    def invert(self):
        """
        Invert the current CAS.

        >>> CAS([1, 1, -1, 1]).invert()
        [-1, -1, 1, -1]

        :return: inversion of the current CAS.
        :rtype: CAS object
        """
        self._cas = [-i for i in self._cas]
        return self

    def retrograde(self):
        """
        Retrograde the current CAS.

        >>> CAS([1, 1, -1, 1]).retrograde()
        [1, -1, 1, 1]

        :return: retrograde of the current CAS.
        :rtype: CAS object
        """
        self._cas.reverse()
        return self

    def rotate(self, n):
        """
        Rotate the current CAS by n positions.

        >>> s = [1, 1, 1, -1, -1]
        >>> CAS(s).rotate(0)
        [1, 1, 1, -1, -1]
        >>> CAS(s).rotate(1)
        [1, 1, -1, -1, 1]
        >>> CAS(s).rotate(2)
        [1, -1, -1, 1, 1]
        >>> CAS(s).rotate(3)
        [-1, -1, 1, 1, 1]
        >>> CAS(s).rotate(4)
        [-1, 1, 1, 1, -1]

        :param n: rotation index: the number of positions the CAS elements are
            rotated. The index is calculated as n % cardinality, so n may be
            arbitrary int.
        :type n: int
        :return: rotation of the CAS.
        :rtype: CAS object
        """
        n = n % len(self._cas)
        self._cas = self._cas[n:] + self._cas[:n]
        return self

    def opI(self):
        """Shorthand for invert()."""
        self.invert()
        return self

    def opR(self):
        """Shorthand for retrograde()."""
        self.retrograde()
        return self

    def opRI(self):
        """Shorthand for invert().retrograde()"""
        self.invert().retrograde()
        return self

    def rot(self, n):
        """Shorthand for rotate()"""
        self.rotate(n)
        return self

    # Analysis methods --------------------------------------------------------

    def casv(self):
        """
        Return the CASV of the current CAS.

        >>> CAS([1, 1, -1, 1]).casv()
        [3, 1]

        :return: CASV of the current CAS.
        :rtype: list
        """
        pos = self._cas.count(1)
        neg = len(self._cas) - pos
        return [pos, neg]

    def transformationMembers(self):
        """
        Return the CASs transformationally related to the current cas.

        Note that both the rot and rotI both have identity at index=0.
        (i.e., rot[0] = P and rotI[0] = I)

        >>> CAS([1, 1, 1, -1, -1]).transformationMembers()
        {'I': [-1, -1, -1, 1, 1],
         'P': [1, 1, 1, -1, -1],
         'R': [-1, -1, 1, 1, 1],
         'RI': [1, 1, -1, -1, -1],
         'rot': [[1, 1, 1, -1, -1],
                 [1, 1, -1, -1, 1],
                 [1, -1, -1, 1, 1],
                 [-1, -1, 1, 1, 1],
                 [-1, 1, 1, 1, -1]],
         'rotI': [[-1, -1, -1, 1, 1],
                  [-1, -1, 1, 1, -1],
                  [-1, 1, 1, -1, -1],
                  [1, 1, -1, -1, -1],
                  [1, -1, -1, -1, 1]]}

        :return: Transformationally related CASs to the current CAS.
        :rtype: dict
        """
        identity = self.copy()
        inversion = self.copy().opI()
        members = {"P": list(identity),
                   "I": list(inversion),
                   "R": list(identity.copy().opR()),
                   "RI": list(inversion.copy().opR())}
        rot, rotI = [list(identity)], [list(inversion)]
        for j in range(len(self._cas)-1):
            rot.append(list(identity.rot(1)))
            rotI.append(list(inversion.rot(1)))
        members["rot"] = rot
        members["rotI"] = rotI
        return members

    # Relation methods --------------------------------------------------------

    def sim(self, cas, norm=True):
        """
        Return the CAS similarity value between the current and input CASs.

        The input ``cas`` could be CAS of arbitrary csegs of the same
        cardinality (i.e., the same number of contour moves). This CAS
        similarity measurement works for CASs of csegs both with and
        without repeated cps.

        If the contour to measure similarity is cseg, convert it to CAS
        before input by using ``cspace.Cseg().cas()``.

        In case of computing the similarity between two csegs (neither the
        two contours is CAS), use ``cspace.Cseg.simCAS()``.

        >>> cas1 = [1, 1, 1, -1, -1]
        >>> cas2 = [1, -1, 1, -1, -1]
        >>> cas3 = [-1, -1, 1, 1, 1]
        >>> CAS(cas1).sim(cas2, norm=False)
        4
        >>> CAS(cas1).sim(cas3, norm=True)
        0.2

        :param cas: contour adjacency series.
        :param norm: if True (default), output the normalized similarity value,
            otherwise the raw value.
        :type cas: cas
        :type norm: bool
        :return: CAS similarity value.
        :rtype: int (norm=False) or float (norm=True)
        """
        cas1, cas2 = self._cas, cas
        card = len(cas1)
        # Pretest
        if card != len(cas2):
            return
        # Measure similarity
        count = 0
        for i in range(card):
            if cas1[i] == cas2[i]:
                count += 1
        if norm:
            return count / card
        else:
            return count

    def relation(self, cas):
        """
        Return the transformational relation status to the current CAS.

        The relation is indicated by the labels: P (identity),
        I, R, RI, rotn, and rotIn, (i.e., rotation of inversion). For rotn
        and rotIn, n is the rotation index.

        >>> cas = [1, 1, 1, -1, -1]
        >>> CAS(cas).relation([1, 1, 1, -1, -1])
        ['P', 'rot0']
        >>> CAS(cas).relation([-1, -1, 1, 1, 1])
        ['R', 'rot3']
        >>> CAS(cas).relation([1, -1, -1, -1, 1])
        ['rotI4']
        >>> CAS(cas).relation([-1, 1, -1, -1, 1])
        []

        :param cas: contour adjacency series.
        :type cas: cas
        :return: list of labels for the transformational relation status.
        :rtype: list
        """
        cas = list(cas)
        relation = []

        # Pretest: for the input CAS to be related to the current CAS by
        #   some transformation, the CASV of the input CAS must at least be
        #   the same as the CASV of the current CAS or its inversion.
        casv = CAS(cas).casv()
        if (casv != self.casv()) and (casv != self.copy().invert().casv()):
            return relation

        members = self.transformationMembers()
        for rel in ("P", "I", "R", "RI"):
            if cas == members[rel]:
                relation.append(rel)
        for i in range(len(cas)):
            if cas == members["rot"][i]:
                relation.append("rot" + str(i))
            elif cas == members["rotI"][i]:
                relation.append("rotI" + str(i))

        return relation


class CASV:
    """Contour Adjacency Series Vector"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, casv):
        """
        Constructor method.

        The input casv is a 2-element array whose integer elements represent
        the summation of positive and negative contour moves respectively.

        >>> CASV([3, 2])
        CASV([3, 2])

        :param casv: contour adjacency series vector.
        :type casv: casv
        """
        self._casv = list(casv)

    def __iter__(self):
        """
        Return a generator object comprising the current CASV elements.

        >>> for i in CASV([3, 2]):
        ...     print(i, end=" ")
        3 2
        """
        for element in self._casv:
            yield element

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CASV([3, 2])
        CASV([3, 2])
        """
        return "CASV({})".format(self._casv)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return CASV(self._casv)

    # Property methods --------------------------------------------------------

    @property
    def casv(self):
        """
        Return the current CASV.

        >>> s = CASV([3, 2])
        >>> s.casv
        [3, 2]

        :return: current CASV.
        :rtype: list
        """
        return self._casv

    @casv.setter
    def casv(self, casv_):
        """
        Set the current CASV to the input CASV.

        >>> s = CASV([3, 2])
        >>> s.casv = [1, 4]
        >>> s.casv
        [1, 4]

        :param casv_: contour adjacency series vector.
        :type casv_: casv
        """
        self._casv = list(casv_)

    # Mutator methods ---------------------------------------------------------

    def inc(self, n):
        """
        Increase n-number of positive contour moves in the current CASV.

        Note that this method does not change the total number of contour
        moves. So from CASV [a, b] results [a+n, b-n]. In case n > b,
        b represents n.

        >>> CASV([3, 2]).inc(1)
        [4, 1]
        >>> CASV([3, 2]).inc(3)  # n = 2 as 3 > 2
        [5, 0]

        :param n: the number of positive moves to increase.
        :type n: int
        :return: CASV with positive moves increased.
        :rtype: CASV object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._casv[1])
            else:
                n = max(n, -self._casv[0])
            self._casv[0] += n
            self._casv[1] -= n
            return self

    def dec(self, n):
        """
        Decrease n-number of positive contour moves in the current CASV.

        Note that this method does not change the total number of contour
        moves. So from CASV [a, b] results [a-n, b+n]. In case n > a,
        a represents n.

        >>> CASV([3, 2]).dec(1)
        [2, 3]
        >>> CASV([3, 2]).dec(4)  # n = 3 as 4 > 2
        [0, 5]

        :param n: the number of positive moves to decrease.
        :type n: int
        :return: CASV with positive moves decreased.
        :rtype: CASV object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._casv[0])
            else:
                n = max(n, -self._casv[1])
            self._casv[0] -= n
            self._casv[1] += n
            return self

    # Relation methods ------------------------------------------------------

    def sim(self, casv, norm=True):
        """
        Return the CAS similarity value between the current and input CASVs.

        The input ``casv`` could be CASV of arbitrary csegs of the
        same cardinality (i.e., the same number of contour moves). This CASV
        similarity measurement works for CASVs of csegs both with and
        without repeated cps.

        If the contour to measure similarity is cseg, convert it to CASV
        before input by using ``cspace.Cseg().casv()``.

        In case of computing the similarity between two csegs (neither the
        two contours is CASV), use ``cspace.Cseg.simCASV()``.

        >>> casv1 = [3, 2]
        >>> casv2 = [1, 4]
        >>> casv3 = [5, 0]
        >>> CASV(casv1).sim(casv2, norm=False)
        3
        >>> CASV(casv1).sim(casv3, norm=True)
        0.6

        :param casv: contour adjacency series vector.
        :param norm: if True (default), output the normalized similarity value,
            otherwise the raw value.
        :type casv: casv
        :type norm: bool
        :return: CASV similarity value [0, 1].
        :rtype: float
        """
        total = sum(self._casv)
        # Pretest
        if total != sum(casv):
            return
        # Measure similarity
        sim = total - abs(self._casv[0] - casv[0])
        if norm:
            return sim / total
        else:
            return sim


class CIS:
    """Contour Interval Succession"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, cseg):
        """
        Constructor method.

        The input cseg is assumed to be normalized and may include repeated
        elements. However, as being a cseg, the input must not have
        consecutively repeated elements.

        >>> CIS([1, 2, 3, 5, 4, 0])
        CIS([1, 2, 3, 5, 4, 0])

        :param cseg: c-segment.
        :type cseg: segment
        """
        checkInput(cseg, checkRep=True)
        cis = []
        for i in range(len(cseg)-1):
            ci = cseg[i+1] - cseg[i]
            cis.append(ci)
        self._cis = cis

    def __iter__(self):
        """
        Return a generator object comprising the current CIS elements.

        >>> for i in CIS([1, 2, 3, 5, 4, 0]):
        ...     print(i, end=" ")
        1 1 2 -1 -4
        """
        for element in self._cis:
            yield element

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CIS([1, 2, 3, 5, 4, 0])
        [1, 1, 2, -1, -4]
        """
        return "CIS({})".format(self.cseg())

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return CIS(self._cis)

    # Property methods --------------------------------------------------------

    @property
    def cis(self):
        """
        Return the current CIS.

        >>> s = CIS([1, 2, 3, 5, 4, 0])
        >>> s.cis
        [1, 1, 2, -1, -4]

        :return: current CIS.
        :rtype: list
        """
        return self._cis

    @cis.setter
    def cis(self, cseg):
        """
        Set the current CIS to the input CIS.

        >>> s = CIS([1, 2, 3, 5, 4, 0])  # cis = [1, 1, 2, -1, -4]
        >>> s.cis = [4, 5, 1, 3, 2, 0]   # input is cseg
        >>> s.cis
        [1, -4, 2, -1, -2]

        :param cseg: c-segment.
        :type cseg: segment
        """
        self._cis = CIS(cseg).cis

    # Analysis methods --------------------------------------------------------

    def cas(self):
        """
        Return the CAS of the current CIS.

        >>> CIS([1, 2, 3, 5, 4, 0]).cas()
        [1, 1, 1, -1, -1]

        :return: the CAS of the current CIS.
        :rtype: list
        """
        return [1 if i > 0 else -1 for i in self._cis]

    def casv(self):
        """
        Return the CASV of the current CIS.

        >>> CIS([1, 2, 3, 5, 4, 0]).casv()
        [3, 2]

        :return: the CASV of the current CIS.
        :rtype: list
        """
        cas = self.cas()
        pos = cas.count(1)
        neg = len(cas) - pos
        return [pos, neg]

    def cseg(self):
        """
        return the cseg of the current CIS.

        >>> CIS([1, 2, 3, 5, 4, 0]).cseg()
        [1, 2, 3, 5, 4, 0]

        :return: the cseg of the current CIS.
        :rtype: list
        """
        cseg = []
        cp = 0  # Set contour pitch 0 to the initial element.
        for i in self._cis:
            cseg.append(cp)
            cp += i
        cseg.append(cp)
        return normalForm(cseg)


class CIA:
    """Contour Interval Array"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, cseg):
        """
        Constructor method.

        The input cseg may include repeated cps. However, as being a cseg,
        the input must not have consecutively repeated cps.

        >>> CIA([1, 2, 3, 5, 4, 0])
        [[3, 3, 2, 1, 0], [2, 1, 1, 1, 1]]

        :param cseg: c-segment.
        :type cseg: segment
        """
        checkInput(cseg, checkRep=True)
        self._cia = self.__tabulateCIs(normalForm(cseg))

    def __iter__(self):
        """
        Return a generator object comprising the current CIA rows.

        >>> for row in CIA([1, 2, 3, 5, 4, 0]):
        ...     print(row)
        [3, 3, 2, 1, 0]
        [2, 1, 1, 1, 1]
        """
        for row in self._cia:
            yield row

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CIA([1, 2, 3, 5, 4, 0])
        [[3, 3, 2, 1, 0], [2, 1, 1, 1, 1]]
        """
        return str(self._cia)

    # Property methods --------------------------------------------------------

    @property
    def cia(self):
        """
        Return the current CIA.

        >>> s = CIA([1, 2, 3, 5, 4, 0])
        >>> s.cia
        [[3, 3, 2, 1, 0], [2, 1, 1, 1, 1]]

        :return: current CIA.
        :rtype: list
        """
        return self._cia

    @cia.setter
    def cia(self, cseg):
        """
        Set the current CIA to the input CIA.

        >>> s = CIA([1, 2, 3, 5, 4, 0])
        >>> s.cia = [4, 5, 1, 3, 2, 0]  # input is cseg
        >>> s.cia
        [[2, 1, 0, 0, 0], [3, 3, 3, 2, 1]]

        :param cseg: c-segment.
        :type cseg: segment
        """
        self._cia = CIA(cseg).cia

    # Analysis methods --------------------------------------------------------

    def ccv1(self):
        """
        Return the CCV1 of the current CIA.

        >>> CIA([1, 2, 3, 5, 4, 0]).ccv1()
        [19, 16]

        :return: the CCV1 of the current CIA.
        :rtype: list
        """
        return [self.__totalCIFreqProducts(self._cia[0]),
                self.__totalCIFreqProducts(self._cia[1])]

    def ccv2(self):
        """
        Return the CCV2 of the current CIA.

        >>> CIA([1, 2, 3, 5, 4, 0]).ccv2()
        [9, 6]

        :return: the CCV1 of the current CIA.
        :rtype: list
        """
        return [sum(self._cia[0]), sum(self._cia[1])]

    # Helper methods ----------------------------------------------------------

    def __tabulateCIs(self, cseg):
        """
        Return the CIA of the input cseg.

        :param cseg: c-segment.
        :type cseg: segment
        :return: CIA
        :rtype: list
        """
        # Initialize CIA
        card = len(cseg)
        cia = [[0] * (card - 1), [0] * (card - 1)]

        # Measure CIs and count them in the array.
        for i in range(card):
            for j in range(i + 1, card):
                ci = cseg[j] - cseg[i]
                if ci > 0:
                    cia[0][ci - 1] += 1
                elif ci < 0:
                    cia[1][-ci - 1] += 1

        return cia

    def __totalCIFreqProducts(self, CIARow):
        """
        Return the total of the products of the frequency and CI types.

        :param CIARow: a row of CIA of either ascending or descending
            contour moves.
        :type CIARow: list
        :return: total of the products of the frequency and CI types.
        :rtype: int
        """
        total = 0
        i = 1
        for ci in CIARow:
            total += ci * i
            i += 1
        return total


class CCV1:
    """Contour Class Vector I"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, ccv1):
        """
        Constructor method.

        The input ccv1 is a 2-element array whose integer elements represent
        the summation of the degrees of ascent and descent expressed in a
        CIA respectively.

        >>> CCV1([9, 1])
        CCV1([9, 1])

        :param ccv1: contour class vector I.
        :type ccv1: ccv1
        """
        self._ccv1 = list(ccv1)

    def __iter__(self):
        """
        Return a generator object comprising the current CCV1 elements.

        >>> for i in CCV1([9, 1]):
        ...     print(i, end=" ")
        9 1
        """
        for element in self._ccv1:
            yield element

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CCV1([9, 1])
        CCV1([9, 1])
        """
        return "CCV1({})".format(self._ccv1)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return CCV1(self._ccv1)

    # Property methods --------------------------------------------------------

    @property
    def ccv1(self):
        """
        Return the current CCV1.

        >>> s = CCV1([9, 1])
        >>> s.ccv1
        [9, 1]

        :return: current CCV1.
        :rtype: list
        """
        return self._ccv1

    @ccv1.setter
    def ccv1(self, ccv1_):
        """
        Set the current CCV1 to the input CCV1.

        >>> s = CCV1([9, 1])
        >>> s.ccv1 = [4, 6]
        >>> s.ccv1
        [4, 6]

        :param ccv1_: contour class vector I.
        :type ccv1_: ccv1
        """
        self._ccv1 = list(ccv1_)

    # Mutator methods ---------------------------------------------------------

    def inc(self, n):
        """
        Increase n-number of positive CI digit in the current CCV1.

        Note that this method does not change the total number of CI digits.
        So from CCV1 [a,b] results [a+n, b-n]. In case n > b, b represents n.

        >>> CCV1([9, 1]).inc(1)
        [10, 0]
        >>> CCV1([9, 1]).inc(2)  # n = 1 as 2 > 1
        [10, 0]

        :param n: the number of positive CI digit to increase.
        :type n: int
        :return: CCV1 with positive CI digit increased.
        :rtype: CCV1 object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._ccv1[1])
            else:
                n = max(n, -self._ccv1[0])
            self._ccv1[0] += n
            self._ccv1[1] -= n
            return self

    def dec(self, n):
        """
        Decrease n-number of positive CI digit in the current CCV1.

        Note that this method does not change the total number of CI digits.
        So from CCV1 [a, b] results [a-n, b+n]. In case n > a, a represents n.

        >>> CCV1([9, 1]).dec(1)
        [8, 2]
        >>> CASV([9, 1]).dec(10)  # n = 10 as 10 > 9
        [0, 10]

        :param n: the number of positive CI digit to decrease.
        :type n: int
        :return: CCV1 with positive CI digit decreased.
        :rtype: CCV1 object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._ccv1[0])
            else:
                n = max(n, -self._ccv1[1])
            self._ccv1[0] -= n
            self._ccv1[1] += n
            return self

    # Relation methods ------------------------------------------------------

    def sim(self, ccv1, card, norm=True):
        """
        Return the CCV1 similarity value between the current and input CCV1s.

        The input ``ccv1`` could be CCV1 of arbitrary csegs of the
        same cardinality. This CCV1 similarity measurement works for CCV1s
        of csegs both with and without repeated cps.

        .. Note::
            ``card`` parameter is required, because the cardinality of the
            cseg from which the input ccv1 is derived cannot be deduced from
            the summation of the CCV1 digits. It is deducible only if the
            CCV1s are derived from csegs without repeated cps exclusively.
            Recall that csegs with repeated cps yield CI = 0 which does not
            affect the digits.

        If the contour to measure similarity is cseg, convert it to CCV1
        before input by using ``cspace.Cseg().ccv1()`` or
        ``cspace.CIA(cseg).ccv1()``.

        In case of computing the similarity between two csegs (neither the
        two contours is CASV), use ``cspace.Cseg.simCCV1()``. In this case,
        the cardinality is known from the input cseg.

        >>> x = [3, 2, 0, 1]  # cseg x
        >>> y = [1, 3, 0, 2]  # cseg y
        >>> z = [0, 2, 0, 1]  # cseg z
        >>> ccv1X = CIA(x).ccv1()  # CCV1(X)
        >>> ccv1Y = CIA(y).ccv1()  # CCV1(Y)
        >>> ccv1Z = CIA(z).ccv1()  # CCV1(Z)
        >>> CCV1(ccv1X).sim(ccv1Y, len(y), norm=False)  # simCCV1(X,Y)
        12
        >>> CCV1(ccv1X).sim(ccv1Y, len(y), norm=True)   # normSimCCV1(X,Y)
        0.6
        >>> CCV1(ccv1X).sim(ccv1Z, len(z), norm=False)  # simCCV1(X,Z)
        11
        >>> CCV1(ccv1X).sim(ccv1Z, len(z), norm=True)   # normSimCCV1(X,Z)
        0.55

        :param ccv1: contour class vector I.
        :param norm: if True, output the normalized similarity value,
            otherwise the raw value.
        :param card: cardinality of the cseg from which the input ccv1 is
            derived.
        :type ccv1: ccv1
        :type norm: bool
        :type card: int
        :return: CCV1 similarity value [0, 1]
        :rtype: float
        """
        sumDiff = abs(self._ccv1[0] - ccv1[0]) + abs(self._ccv1[1] - ccv1[1])
        maxDiff = c.MAX_DIFF_CCV1[card]
        if norm:
            return (maxDiff - sumDiff) / maxDiff
        else:
            return maxDiff - sumDiff


class CCV2:
    """Contour Class Vector II"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, ccv2):
        """
        Constructor method.

        The input ccv2 is a 2-element array whose integer elements represent
        the summation of the degrees of ascent and descent expressed in a
        CIA respectively.

        >>> CCV2([5, 1])

        :param ccv2: contour class vector II.
        :type ccv2: ccv2
        """
        self._ccv2 = list(ccv2)

    def __iter__(self):
        """
        Return a generator object comprising the current CCV2 elements.

        >>> for i in CCV2([5, 1]):
        ...     print(i, end=" ")
        5 1
        """
        for element in self._ccv2:
            yield element

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> CCV2([5, 1])
        CCV2([5, 1])
        """
        return "CCV2({})".format(self._ccv2)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return CCV2(self._ccv2)

    # Property methods --------------------------------------------------------

    @property
    def ccv2(self):
        """
        Return the current CCV2.

        >>> s = CCV2([5, 1])
        >>> s.ccv2
        [5, 1]

        :return: current CCV2.
        :rtype: list
        """
        return self._ccv2

    @ccv2.setter
    def ccv2(self, ccv2_):
        """
        Set the current CCV2 to the input CCV2.

        >>> s = CCV2([5, 1])
        >>> s.ccv2 = [2, 4]
        >>> s.ccv2
        [2, 4]

        :param ccv2_: contour class vector II.
        :type ccv2_: ccv2
        """
        self._ccv2 = list(ccv2_)

    # Mutator methods ---------------------------------------------------------

    def inc(self, n):
        """
        Increase n-number of positive CI digit in the current CCV2.

        Note that this method does not change the total number of CI digits.
        So from CCV2 [a,b] results [a+n, b-n]. In case n > b, b represents n.

        >>> CCV2([5, 1]).inc(1)
        [6, 0]
        >>> CCV1([5, 1]).inc(2)  # n = 1 as 2 > 1
        [6, 0]

        :param n: the number of positive CI digit to increase.
        :type n: int
        :return: CCV2 with positive CI digit increased.
        :rtype: CCV2 object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._ccv2[1])
            else:
                n = max(n, -self._ccv2[0])
            self._ccv2[0] += n
            self._ccv2[1] -= n
            return self

    def dec(self, n):
        """
        Decrease n-number of positive CI digit in the current CCV2.

        Note that this method does not change the total number of CI digits.
        So from CCV2 [a, b] results [a-n, b+n]. In case n > a, a represents n.

        >>> CCV1([5, 1]).dec(1)
        [4, 2]
        >>> CASV([5, 1]).dec(6)  # n = 5 as 6 > 5
        [0, 6]

        :param n: the number of positive CI digit to decrease.
        :type n: int
        :return: CCV2 with positive CI digit decreased.
        :rtype: CCV2 object
        """
        if n == 0:
            return self
        else:
            if n > 0:
                n = min(n, self._ccv2[0])
            else:
                n = max(n, -self._ccv2[1])
            self._ccv2[0] -= n
            self._ccv2[1] += n
            return self

    # Relation methods ------------------------------------------------------

    def sim(self, ccv2, card, norm=True):
        """
        Return the CCV2 similarity value between the current and input CCV2s.

        The input ``ccv2`` could be CCV2 of arbitrary csegs of the
        same cardinality. This CCV2 similarity measurement works for CCV2s
        of csegs both with and without repeated cps.

        .. Note::
            ``card`` parameter is required, because the cardinality of the
            cseg from which the input ccv2 is derived cannot be deduced from
            the summation of the CCV2 digits. It is deducible only
            if the CCV2s are derived from csegs without repeated
            cps exclusively. Recall that csegs with repeated cps yield CI =
            0 which does not affect the digits.

        If the contour to measure similarity is cseg, convert it to CCV2
        before input by using ``cspace.Cseg().ccv2()`` or
        ``cspace.CIA(cseg).ccv2()``.

        In case of computing the similarity between two csegs (neither the
        two contours is CASV), use ``cspace.Cseg.simCCV2()``.  In this case,
        the cardinality is known from the input cseg.

        >>> x = [3, 2, 0, 1]  # cseg X
        >>> y = [1, 3, 0, 2]  # cseg Y
        >>> z = [0, 2, 0, 1]  # cseg Z
        >>> ccv2X = CIA(x).ccv2()  # CCV2(X)
        >>> ccv2Y = CIA(y).ccv2()  # CCV2(Y)
        >>> ccv2Z = CIA(z).ccv2()  # CCV2(Z)
        >>> CCV2(ccv2X).sim(ccv2Y, len(y), norm=False)  # simCCV2(X,Y)
        8
        >>> CCV2(ccv2X).sim(ccv2Y, len(y), norm=True)   # normSimCCV2(X,Y)
        0.6666666666666666
        >>> CCV2(ccv2X).sim(ccv2Z, len(z), norm=False)  # simCCV2(X,Z)
        7
        >>> CCV2(ccv2X).sim(ccv2Z, len(z), norm=True)   # normSimCCV2(X,Z)
        0.5833333333333334

        :param ccv2: contour class vector II.
        :param norm: if True, output the normalized similarity value,
            otherwise the raw value.
        :param card: cardinality of the cseg from which the input ccv2 is
            derived from.
        :type ccv2: ccv2
        :type norm: bool
        :type card: int
        :return: CCV2 similarity value [0, 1].
        :rtype: float
        """
        sumDiff = abs(self._ccv2[0] - ccv2[0]) + abs(self._ccv2[1] - ccv2[1])
        maxDiff = c.MAX_DIFF_CCV2[card]
        if norm:
            return (maxDiff - sumDiff) / maxDiff
        else:
            return maxDiff - sumDiff


class Csegclass(Segclass):
    """C-space segment-class"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, cseg):
        """
        Constructor method.

        The csegclass is represented by the prime form of the input cseg.

        >>> Csegclass([0, 2, 3, 1])
        Csegclass([0, 2, 3, 1])
        >>> Csegclass([0, 2, 1, 1])
        ValueError: Cseg cannot have consecutively repeated cps.

        :param cseg: c-segment.
        :type cseg: segment
        """
        Segclass.__init__(self, cseg)

    def __contains__(self, cp):
        """
        Return a bool of the cp membership to the current csegclass.

        >>> s = Csegclass([0, 2, 3, 1])
        >>> 2 in s
        True

        :param cp: cp to test the membership to the current csegclass.
        :type cp: int
        :return: True if the cp is in self, False otherwise.
        :rtype: bool
        """
        return Segclass.__contains__(self, cp)

    def __getitem__(self, index):
        """
        Return the indexed cp of the current csegclass.

        >>> Csegclass([0, 2, 3, 1])[3]
        1

        :param index: index to get a cp.
        :type index: int
        :return: indexed cp.
        :rtype: int
        """
        return Segclass.__getitem__(self, index)

    def __iter__(self):
        """
        Return a generator object comprising the current csegclass's cps.

        >>> for i in Csegclass([0, 2, 3, 1]):
        ...     print(i, end="")
        0231
        """
        return Segclass.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current csegclass.

        >>> len(Csegclass([0, 2, 3, 1]))
        4
        """
        return Segclass.__len__(self)

    def __reversed__(self):
        """
        Return a reverse iterator of the current csegclass's cps.

        >>> list(reversed(Csegclass([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current csegclass's cps in
            reverse order.
        :rtype: iterator
        """
        return Segclass.__reversed__(self)

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Csegclass([0, 2, 3, 1])
        Csegclass([0, 2, 3, 1])
        """
        return "Csegclass({})".format(self._segclass)

    def count(self, cp):
        """
        Return the number of occurrences of the cp.

        >>> Csegclass([0, 2, 3, 1]).count(2)
        1
        >>> Csegclass([0, 2, 3, 1]).count(4)
        0

        :param cp: cp to check the occurrence frequency in the current
            Csegclass.
        :type cp: int
        :return: the number of occurrences of the cp.
        :rtype: int
        """
        return Segclass.count(self, cp)

    def index(self, cp, start=0, stop=None):
        """
        Return the first index of the cp.

        Raise ValueError if the cp is not present.

        >>> Csegclass([0, 2, 3, 1]).index(3)
        2
        >>> Csegclass([0, 2, 3, 1]).index(4)
        ValueError

        :param cp: cp to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type cp: int
        :type start: int
        :type stop: int
        :return: first index of the cp.
        :rtype: int
        """
        return Segclass.index(self, cp, start=start, stop=stop)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Csegclass(self._segclass)

    # Property methods --------------------------------------------------------

    @property
    def csegclass(self):
        """
        Return the current csegclass.

        >>> s = Csegclass([3, 1, 0, 2])
        >>> s.csegclass
        [0, 2, 3, 1]  # csegclass is represented by the prime form.

        :return: current csegclass.
        :rtype: list
        """
        return self._segclass

    @csegclass.setter
    def csegclass(self, cseg):
        """
        Set the current csegclass to that of the input cseg.

        >>> s = Csegclass([3, 1, 0, 2])
        >>> s.csegclass = [1, 3, 0, 2]
        >>> s.csegclass
        [1, 3, 0, 2]
        >>> s.csegclass = [0, 2, 1, 1]
        ValueError: Cseg cannot have consecutively repeated cps.

        :param cseg: c-segment.
        :type cseg: segment
        """
        checkInput(cseg, checkRep=True)
        self._segclass = primeForm(cseg)

    # Analysis methods --------------------------------------------------------

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current csegclass.

        >>> Csegclass([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (numpy=False) or 2D ndarray (numpy=True) of the
            COM-matrix of the current csegclass.
        :rtype: list or ndarray
        """
        return Segclass.comMatrix(self, nparr)

    def csegclassName(self):
        """
        Return the name of the current csegclass.

        >>> Csegclass([0, 2, 3, 1]).csegclassName()
        4-4

        :return: the name of the current csegclass.
        :rtype: str
        """
        return Segclass.segclassName(self)

    def csegclassMembers(self, nparr=False):
        """
        Return the members (P, I, R, and RI) of the current csegclass.

        >>> Csegclass([0, 2, 3, 1]).csegclassMembers()
        {'I': [3, 1, 0, 2],
         'P': [0, 2, 3, 1],
         'R': [1, 3, 2, 0],
         'RI': [2, 0, 1, 3]}

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: the dict keys (P, I, R, and RI) are assigned with their
            corresponding segment as the values. The values are list
            (nparr=False) or numpy array (nparr=True) of normalized cseg.
        :rtype: dict
        """
        return Segclass.segclassMembers(self, nparr)

    def csubsegs(self, normalize=False):
        """
        Return the csubsegs (c-subsegments) of the current csegclass.

        The cardinalities of the csubsegs are 2 to the cardinality of the
        csegclass. Therefore, the returned group of csubsegs includes the
        csegclass itself.

        >>> s = Csegclass([0, 2, 3, 1])
        >>> s.csubsegs()
        {2: [(0, 2), (0, 3), (0, 1), (2, 3), (2, 1), (3, 1)],
         3: [(0, 2, 3), (0, 2, 1), (0, 3, 1), (2, 3, 1)],
         4: [(0, 2, 3, 1)]}
        >>> s.csubsegs(normalize=True)
        {2: [(0, 1), (0, 1), (0, 1), (0, 1), (1, 0), (1, 0)],
         3: [(0, 1, 2), (0, 2, 1), (0, 2, 1), (1, 2, 0)],
         4: [(0, 2, 3, 1)]}

        :param normalize: the output csubsegs are normalized when True,
            otherwise as is.
        :type normalize: bool
        :return: the dict of the csubsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return Segclass.subsegs(self, normalize=normalize, contiguous=False)

    def csegclasses(self, func=1, sim=1.0, card=None):
        """
        Return csegclasses within the similarity range.

        The returned csegclasses are sorted by the lexicographic order and the
        number of repeated cps.

        >>> s = Csegclass([0, 2, 3, 1])
        >>> s.csegclasses(func=0, sim=0.7)  # CSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334),
         ((0, 1, 2, 1), 0.8333333333333334)]
        >>> s.csegclasses(func=1, sim=0.7)  # ACMEMB
        [((0, 1, 3, 2), 0.8636363636363636),
         ((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 3, 2, 1), 0.8181818181818182),
         ((0, 2, 1), 0.8),
         ((1, 3, 0, 2), 0.7727272727272727),
         ((1, 0, 3, 2), 0.7272727272727273),
         ((0, 1, 0, 2), 0.7272727272727273),
         ((0, 1, 2, 1), 0.7272727272727273)]
        >>> s.csegclasses(func=1, sim=0.7, card=3)
        [((0, 2, 1), 0.8)]

        :param func: the function to measure the similarity: CSIM (0),
            ACMEMB (1).
        :param sim: similarity threshold [0, 1]. Measured with the current
            csegclass, those csegclasses which have a similarity value the
            same or higher than sim will be output.
        :param card: when card value is given, the output csegclasses are of
            the specific cardinality.
        :type func: int
        :type sim: float
        :type card: int
        :return: tuples of csegclass and similarity value pairs.
        :rtype: list of tuples
        """
        f = [0, 2][func]
        return Segclass.segclasses(self, func=f, sim=sim, card=card)

    # Relation methods --------------------------------------------------------

    def csim(self, cseg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current csegclass and the
        input cseg.

        The input cseg must have the same cardinality as the current
        csegclass, however, does not have to be preprocessed to be in
        normal form nor prime form--the method computes the similarity with
        its csegclass members accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> Csegclass([0, 2, 3, 1]).csim([3, 1, 0, 2])
        1.0
        >>> Csegclass([1, 0, 4, 3, 2]).csim([1, 2, 4, 0, 3])
        0.8

        :param cseg: c-segment to measure the similarity with.
        :type cseg: segment
        :return: similarity value [0, 1]
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segclass.xsim(self, cseg)

    def cemb(self, cseg):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input cseg does not have to be preprocessed to be in normal form
        nor prime form: the method computes the similarity with its csegclass
        members accordingly.

        .. Note::
            This contour similarity measurement method only works with
            csegs of differing cardinalities: the input cseg must be
            larger than the current csegclass.

        See the description of ``contour.xemb()`` for more detail.

        >>> Csegclass([0, 1, 2]).cemb([3, 1, 4, 2, 0])
        0.3

        :param cseg: c-segment.
        :type cseg: segment
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segclass.xemb(self, cseg, contiguous=False)

    def acmemb(self, cseg):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        This contour similarity measurement method works with csegclasses of
        both equal or unequal cardinalities: the input cseg may or may not be
        the same size as the current csegclass.

        The input cseg does not have to be preprocessed to be in normal form
        nor prime form: the method computes the similarity with its csegclass
        members accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> x = Csegclass([0, 1, 2, 3])
        >>> y = Csegclass([0, 2, 1, 3])
        >>> z = Csegclass([0, 2, 1, 3, 4])
        >>> x.acmemb(y)  # ACMEMB(X_,Y_)
        0.7727272727272727
        >>> x.acmemb(z)  # ACMEMB(X_,Z_)
        0.7837837837837838
        >>> y.acmemb(z)  # ACMEMB(Y_,Z_)
        0.8918918918918919

        :param cseg: c-segment to measure the similarity with.
        :type cseg: segment
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segclass.axmemb(self, cseg, contiguous=False)


class Cseg(Segment):
    """C-space segment"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, cseg):
        """
        Constructor method.

        >>> Cseg([0, 2, 3, 1])
        Cseg([0, 2, 3, 1])
        >>> Cseg([0, 2, 1, 1])
        ValueError: Cseg cannot have consecutively repeated cps.

        :param cseg: c-segment.
        :type cseg: segment
        """
        checkInput(cseg, checkRep=True)
        Segment.__init__(self, cseg)

    def __contains__(self, cp):
        """
        Return a bool of the cp membership to the current cseg.

        >>> s = Cseg([0, 2, 3, 1])
        >>> 2 in s
        True

        :param cp: cp to test the membership to the current cseg.
        :type cp: int
        :return: True if the cp is in self, False otherwise.
        :rtype: bool
        """
        return Segment.__contains__(self, cp)

    def __delitem__(self, index):
        """
        Delete the indexed cp.

        >>> s = Cseg([0, 2, 3, 1])
        >>> del s[2]
        >>> s
        [0, 2, 1]

        :param index: index at which the cp is deleted.
        """
        try:
            s = list(self._seg)
            del s[index]
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def __getitem__(self, index):
        """
        Return the indexed cp of the current cseg.

        >>> Cseg([0, 2, 3, 1])[3]
        1

        :param index: index to get a cp.
        :type index: int
        :return: indexed cp.
        :rtype: int
        """
        return Segment.__getitem__(self, index)

    def __iadd__(self, cps):
        """
        Append the input cps to the current cseg in-place.

        This operation is equivalent to self.extend(cps) but invoked by +=
        operator.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s += [4, 6, 5]
        >>> s
        Cseg([0, 2, 3, 1, 4, 6, 5])

        :param cps: cps to append to the current cseg.
        :type cps: list
        :return: mutated cseg.
        :rtype: Cseg object
        """
        return self.extend(cps)

    def __iter__(self):
        """
        Return a generator object comprising the current cseg's cps.

        >>> for i in Cseg([0, 2, 3, 1]):
        ...     print(i, end="")
        0231

        :return: iterator with the current cseg's elements.
        :rtype: iterator
        """
        return Segment.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the cseg.

        >>> len(Cseg([0, 2, 3, 1]))
        4
        """
        return Segment.__len__(self)

    def __reversed__(self):
        """
        Return a reverse iterator of the current cseg's cps.

        >>> list(reversed(Cseg([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current cseg's cps in
            reverse order.
        :rtype: iterator
        """
        return Segment.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed cp.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s[2] = 0
        >>> s
        Cseg([0, 2, 0, 1])

        :param index: index at which the cp changes the value.
        :param value: value to change the indexed cp.
        :type index: int
        :type value: int
        """
        try:
            s = list(self._seg)
            s[index] = value
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Cseg([0, 2, 3, 1])
        Cseg([0, 2, 3, 1])

        :return: official representation of the object.
        :rtype: str
        """
        return "Cseg({})".format(self._seg)

    def append(self, cp):
        """
        Append a single cp to the end of the current cseg.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.append(4)
        Cseg([0, 2, 3, 1, 4])

        :param cp: cp to append.
        :type cp: int
        :return: mutated cseg.
        :rtype: Cseg object
        """
        try:
            if self._seg[-1] == cp:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        return Segment.append(self, cp)

    def count(self, cp):
        """
        Return the number of occurrences of the cp.

        >>> Cseg([0, 2, 3, 1]).count(2)
        1
        >>> Cseg([0, 2, 3, 1]).count(4)
        0

        :param cp: cp to check the occurrence frequency in the current cseg.
        :type cp: int
        :return: the number of occurrences of the cp.
        :rtype: int
        """
        return Segment.count(self, cp)

    def extend(self, cps):
        """
        Extend the current cseg by appending the input cps.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.extend([4, 6, 5])
        Cseg([0, 2, 3, 1, 4, 6, 5])

        :param cps: cps to append to the current cseg.
        :type cps: list
        :return: mutated cseg.
        :rtype: Cseg object
        """
        try:
            s = self._seg + cps
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def index(self, cp, start=0, stop=None):
        """
        Return the first index of the cp.

        Raise ValueError if the cp is not present.

        >>> Cseg([0, 2, 3, 1]).index(3)
        2
        >>> Cseg([0, 2, 3, 1]).index(4)
        ValueError

        :param cp: cp to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type cp: int
        :type start: int
        :type stop: int
        :return: first index of the cp.
        :rtype: int
        """
        return Segment.index(self, cp, start=start, stop=stop)

    def insert(self, index, cp):
        """
        Insert the cp at the specified index of the cseg.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.insert(3, 2)
        Cseg([0, 2, 3, 2, 1])

        :param index: index at which the cp is inserted.
        :param cp: cp to insert.
        :type index: int
        :type cp: int
        :return: mutated cseg.
        :rtype: Cseg object
        """
        try:
            s = list(self._seg)
            s.insert(index, cp)
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def pop(self, index=-1):
        """
        Remove and return a cp at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.pop()
        1
        >>> s.pop(1)
        2
        >>> s
        [0, 3]

        :param index: index at which the cp is popped.
        :type index: int
        :return: popped cp.
        :rtype: int
        """
        try:
            s = list(self._seg)
            s.pop(index)
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def remove(self, value):
        """
        Remove the first occurrence of a cp with the input value.

        Raise ValueError if the value is not present.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.remove(3)
        Cseg([0, 2, 1])

        :param value: value with which a cp is removed.
        :type value: int
        :return: mutated cseg.
        :rtype: Cseg object
        """
        try:
            s = list(self._seg)
            s.remove(value)
            if repeatPattern(s) == 2:
                raise ValueError("Consecutively repeated cps detected.")
        except ValueError:
            raise
        self._seg = s
        return self

    def reverse(self):
        """
        Reverse the current cseg in place.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.reverse()
        Cseg([1, 3, 2, 0])

        :return: mutated cseg.
        :rtype: Cseg object
        """
        # Do not Segment.reverse(self), as it invokes self.__setitem__ that
        #   raises ValueError("Consecutively repeated cps detected.").
        self._seg.reverse()
        return self

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Cseg(self._seg)

    # Property methods --------------------------------------------------------

    @property
    def cseg(self):
        """
        Return the current cseg.

        >>> s = Cseg([3, 1, 0, 2])
        >>> s.cseg
        [3, 1, 0, 2]

        :return: current cseg.
        :rtype: list
        """
        return self._seg

    @cseg.setter
    def cseg(self, cseg_):
        """
        Set the current cseg to the input cseg.

        >>> s = Cseg([3, 1, 0, 2])
        >>> s.cseg = [1, 3, 0, 2]
        >>> s.cseg
        [1, 3, 0, 2]

        :param cseg_: contour segment.
        :type cseg_: segment
        """
        checkInput(cseg_, checkRep=True)
        self._seg = list(cseg_)

    # Mutator methods ---------------------------------------------------------

    def normalize(self):
        """
        Normalize the current cseg.

        See ``contour.normalForm()`` for more detail.

        >>> Cseg([1, 5, 3, 2]).normalize()
        Cseg([0, 3, 2, 1])

        :return: normal form of the current cseg.
        :rtype: Cseg object
        """
        return Segment.normalize(self)

    def invert(self):
        """
        Invert the current cseg.

        >>> Cseg([0, 2, 3, 1]).invert()
        Cseg([3, 1, 0, 2])

        :return: inversion of the current cseg.
        :rtype: Cseg object
        """
        return Segment.invert(self)

    def retrograde(self):
        """
        Retrograde the current cseg.

        >>> Cseg([0, 2, 3, 1]).retrograde()
        Cseg([1, 3, 2, 0])

        :return: retrograde of the current cseg.
        :rtype: Cseg object
        """
        return Segment.retrograde(self)

    def rotate(self, n, mode=0):
        """
        Cyclically permute the cps of the current cseg.

        >>> s = Cseg([0, 2, 3, 1])
        >>> s.copy().rotate(1, mode=0))
        Cseg([2, 3, 1, 0])
        >>> s.copy().rotate(1, mode=1))
        Cseg([1, 3, 0, 2])

        :param n: rotation index: the number of positions the c-pitches are
            rotated. The index is calculated as n % cardinality, so n may be
            arbitrary int.
        :param mode: rotation mode: temporal order rotation(0),
            c-space registral order rotation (1).
        :type n: int
        :type mode: int
        :return: rotation of the current cseg
        :rtype: Cseg object
        """
        return Segment.rotate(self, n=n, mode=mode)

    def opI(self):
        """Shorthand for invert()."""
        return self.invert()

    def opR(self):
        """Shorthand for retrograde()."""
        return self.retrograde()

    def opRI(self):
        """Return the retrograde inversion of the current cseg."""
        return self.invert().retrograde()

    def simTransform(self, func=1, sim=0, card=None, fixed=None):
        """
        Transform the current cseg based on similarity.

        >>> a = Cseg([0, 2, 3, 1])
        >>> a.csegs(func=1, sim=0.6, card=4, fixed={"-1": 0})  # candidates
        [((1, 2, 3, 0), 0.8181818181818182),
         ((1, 3, 2, 0), 0.8181818181818182),
         ((2, 1, 3, 0), 0.6818181818181818),
         ((2, 3, 1, 0), 0.6818181818181818),
         ((0, 1, 2, 0), 0.6818181818181818),
         ((3, 1, 2, 0), 0.6363636363636364),
         ((0, 2, 1, 0), 0.6363636363636364)]
        >>> a.simTransform(func=1, sim=0.6, card=4, fixed={"-1": 0})
        Cseg([0, 1, 2, 0])

        :param func: the function to measure the similarity:

            * CSIM (0)
            * ACMEMB (1)
            * CAS (2)
            * CASV (3)
            * CCV1 (4)
            * CCV2 (5)

        :param sim: similarity threshold [0.0, 1.0]. Measured with the current
            cseg, those csegs which have a similarity value the same or higher
            than the sim value will be the candidate for transformation.
        :param card: when card value is given, the transformed cseg is of the
            specified cardinality.
        :param fixed: dict keys are the element positions to fix, and values
            are the elements' values.
        :type func: int
        :type sim: float
        :type card: int
        :type fixed: dict
        :return: similarity-transformation of the current cseg.
        :rtype: Cseg object
        """
        candidates = [i[0] for i in
                      self.csegs(func=func, sim=sim, card=card, fixed=fixed)]
        if len(candidates) > 0:
            self._seg = list(random.choice(candidates))
        else:
            self._seg = []
        return self

    # Analysis methods --------------------------------------------------------

    def normalForm(self, nparr=False):
        """
        Return the normal form of the current cseg.

        See ``contour.normalForm()`` for more detail.

        >>> Cseg([-12, 8, 0, -2]).normalForm()
        [0, 3, 2, 1]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or a ndarray (nparr=True) of the
            current cseg.
        :rtype: list or ndarray
        """
        return Segment.normalForm(self, nparr=nparr)

    def primeForm(self, nparr=False):
        """
        Return the prime form of the current cseg.

        >>> Cseg([3, 1, 2, 0]).primeForm()
        [0, 2, 1, 3]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (numpy=False) or ndarray (numpy=True) of the prime
            form of the current cseg.
        :rtype: list or ndarray
        """
        return Segment.primeForm(self, nparr=nparr)

    def isNormalForm(self):
        """
        Return a bool that indicates whether the current cseg is normalized.

        >>> Cseg([0, 1, 4, 2]).isNormalForm()  # NF = [0, 1, 3, 2]
        False

        :return: True if cseg is normalized, False otherwise.
        :rtype: bool
        """
        return Segment.isNormalForm(self)

    def isPrimeForm(self):
        """
        Return a bool that indicates whether the current cseg is the prime
        form.

        >>> Cseg([1, 3, 2, 0]).isPrimeForm()  # PF = [0, 2, 3, 1]
        False

        :return: True if cseg is the prime form, False otherwise.
        :rtype: bool
        """
        return Segment.isPrimeForm(self)

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current cseg.

        >>> Cseg([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (numpy=False) or 2D ndarray (numpy=True) of the
            COM-matrix of the current cseg.
        :rtype: list or ndarray
        """
        return Segment.comMatrix(self, nparr=nparr)

    def csegclassRelation(self):
        """
        Return the relation status of the current cseg to its csegclass.

        See ``contour.segclassRelation`` for more detail.

        >>> Cseg([4, 1, 3, 2]).segclassRelation()  # Unnormalized
        -1
        >>> Cseg([0, 1, 3, 2]).segclassRelation()  # P (identity)
        0
        >>> Cseg([3, 2, 0, 1]).segclassRelation()  # I
        1
        >>> Cseg([2, 3, 1, 0]).segclassRelation()  # R
        2
        >>> Cseg([1, 0, 2, 3]).segclassRelation()  # RI
        3
        >>> Cseg([0, 2, 1, 3]).segclassRelation()  # Both P and RI related
        4
        >>> Cseg([3, 1, 2, 0]).segclassRelation()  # Both I and R related
        5

        :return: the csegclass member relation status:

            * unnormalized (-1)
            * identity (0)
            * inversion (1)
            * retrograde (2)
            * retrograde-inversion (3)
            * both identity and retrograde-inversion (4)
            * both inversion and retrograde (5).

        :rtype: int
        """
        return Segment.segclassRelation(self)

    def cas(self):
        """
        Return the CAS of the current cseg.

        >>> Cseg([0, 2, 3, 1, 5, 4]).cas()
        [1, 1, -1, 1, -1]

        :return: the CAS of the current cseg.
        :rtype: list
        """
        return CIS(self._seg).cas()

    def casv(self):
        """
        Return the CASV of the current cseg.

        >>> Cseg([0, 2, 3, 1, 5, 4]).casv()
        [3, 2]

        :return: the CASV of the current cseg.
        :rtype: list
        """
        return CIS(self._seg).casv()

    def cis(self):
        """
        Return the CIS of the current cseg.

        >>> Cseg([0, 2, 3, 1, 5, 4]).cis()
        [2, 1, -2, 4, -1]

        :return: the CIS of the current cseg.
        :rtype: list
        """
        return CIS(self._seg).cis

    def cia(self):
        """
        Return the CIA of the current cseg.

        >>> Cseg([1, 2, 3, 5, 4, 0]).cia()
        [[3, 3, 2, 1, 0], [2, 1, 1, 1, 1]]

        :return: the CIA of the current cseg.
        :rtype: list
        """
        return CIA(self._seg).cia

    def ccv1(self):
        """
        Return the CCV1 of the current cseg.

        >>> Cseg([1, 2, 3, 5, 4, 0]).ccv1()
        [19, 16]

        :return: the CCV1 of the current cseg.
        :rtype: list
        """
        return CIA(self._seg).ccv1()

    def ccv2(self):
        """
        Return the CCV2 of the current cseg.

        >>> Cseg([1, 2, 3, 5, 4, 0]).ccv2()
        [9, 6]

        :return: the CCV2 of the current cseg.
        :rtype: list
        """
        return CIA(self._seg).ccv2()

    def csubsegs(self, normalize=False):
        """
        Return the csubsegments of the current cseg.

        The cardinalities of the csubsegs are 2 to the cardinality of the
        current cseg. Therefore, the returned group of csubsegments includes
        the current cseg itself.

        >>> a = Cseg([0, 6, 1, -12]).csubsegs(normalize=True)
        >>> b = Cseg([1, 3, 2, 0]).csubsegs(normalize=True)
        >>> a == b
        True
        >>> a
        {2: [(0, 1), (0, 1), (1, 0), (1, 0), (1, 0), (1, 0)],
         3: [(0, 2, 1), (1, 2, 0), (1, 2, 0), (2, 1, 0)],
         4: [(1, 3, 2, 0)]}

        :param normalize: the output csubsegs are normalized when True,
            otherwise as is.
        :type normalize: bool
        :return: the dict of the csubsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return Segment.subsegs(self, normalize=normalize, contiguous=False)

    def csegs(self, func=1, sim=1.0, card=None, fixed=None):
        """
        Return csegs within the similarity range.

        The output list of csegs is in the order of similarity value high to
        low.

        Optional filtering criteria may be given for filtering the csegs (the
        cardinality of and fixed elements in the cseg).

        >>> a = Cseg([0, 2, 3, 1])
        >>> a.csegs(func=0, sim=0.6, fixed={"1": 3})  # CSIM
        [((0, 3, 2, 1), 0.8333333333333334),
         ((0, 3, 1, 2), 0.6666666666666666),
         ((1, 3, 2, 0), 0.6666666666666666)]
        >>> a.csegs(func=1, sim=0.7)  # ACMEMB
        [((0, 1, 3, 2), 0.8636363636363636),
         ((0, 2, 1, 3), 0.8181818181818182),
         ...
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.csegs(func=1, sim=0.7, fixed={"0": 0, "2": 1})
        [((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 2, 1), 0.8),
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.csegs(func=1, sim=0.7, card=4, fixed={"0": 0, "2": 1})
        [((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.csegs(func=2, sim=0.6, fixed={"3": 1})  # CAS
        [((0, 1, 2, 1), 1.0),
         ((0, 3, 2, 1), 0.6666666666666666),
         ...
         ((2, 0, 2, 1), 0.6666666666666666)]
        >>> a.csegs(func=3, sim=0.6, fixed={"2": 3})  # CASV
        [((0, 1, 3, 2), 1.0),
         ((1, 2, 3, 0), 1.0),
         ...
         ((2, 1, 3, 0), 0.6666666666666666)]
        >>> a.csegs(func=4, sim=0.8, fixed={"2": 3})  # CCV1
        [((1, 0, 3, 2), 0.9),
         ((0, 1, 3, 2), 0.8),
         ((2, 0, 3, 1), 0.8)]
        >>> a.csegs(func=5, sim=0.8, fixed={"1": 2})  # CCV2
        [((1, 2, 0, 3), 1.0),
         ((0, 2, 0, 1), 0.9166666666666666),
         ...
         ((1, 2, 3, 0), 0.8333333333333334)]

        :param func: the function to measure the similarity:

            * CSIM (0)
            * ACMEMB (1)
            * CAS (2)
            * CASV (3)
            * CCV1 (4)
            * CCV2 (5)

        :param sim: similarity threshold [0, 1]. Measured with the current
            cseg, those csegs which have a similarity value the same or higher
            than the sim value will be output.
        :param card: when card value is given, the output csegs are of the
            specified cardinality.
        :param fixed: dict keys are the element positions to fix, and the
            values are the elements' values.
        :type func: int
        :type sim: float
        :type card: int
        :type fixed: dict
        :return: pairs of cseg and similarity value.
        :rtype: list of tuples
        """
        f = [0, 2, 4, 5, 6, 7][func]
        return Segment.segs(self, func=f, sim=sim, card=card, fixed=fixed)

    def contourReduction(self, mode=2):
        """

        :param mode: Morris's algorithm (0), Schultz's algorithm (1),
            Mustafa's algorithm (2)
        :return:
        """
        # TODO: implement later
        pass

    # Relation methods---------------------------------------------------------

    def csim(self, cseg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current and the input csegs.

        The input cseg must have the same cardinality as the current cseg,
        however, it does not have to be preprocessed to be in normal form--the
        method computes the similarity with its normal form accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> a = Cseg([2, 0, 1, 3])
        >>> b = [0, 1, 2, 3]
        >>> c = [1, 3, 0, 2]
        >>> d = [0, 2, 3, 1]
        >>> a.csim(b)  # CSIM(A,B)
        0.6666666666666666
        >>> a.csim(c)  # CSIM(A,C)
        0.5
        >>> a.csim(d)  # CSIM(A,D)
        0.3333333333333333

        :param cseg: c-segment to measure the similarity with.
        :type cseg: segment
        :return: similarity value [0.0, 1.0].
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segment.xsim(self, cseg)

    def cemb(self, cseg):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input cseg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        .. Note::
            This contour similarity measurement method only works with
            csegs of differing cardinalities--the input cseg must be
            larger than the current cseg.

        See the description of ``contour.xemb()`` for more detail.

        >>> a = [0, 1, 2]
        >>> b = [0, 2, 1, 3, 4]
        >>> Cseg(a).cemb(b)  # CEMB(A,B)
        0.7

        :param cseg: c-segment to measure the similarity with
        :type cseg: segment
        :return: the contour similarity value [0.0, 1.0].
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segment.xemb(self, cseg, contiguous=False)

    def acmemb(self, cseg):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        This contour similarity measurement method works with csegs of
        both equal or unequal cardinalities--the input cseg may or may not be
        the same size as the current cseg.

        The input cseg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> a = [0, 1, 2, 3]
        >>> b = [0, 2, 1, 3, 4]
        >>> Cseg(a).axmemb(b)  # ACMEMB(A,B)
        0.7837837837837838

        :param cseg: c-segment to measure the similarity with.
        :type cseg: segment
        :return: the contour similarity value [0.0, 1.0].
        :rtype: float
        """
        checkInput(cseg, checkRep=True)
        return Segment.axmemb(self, cseg, contiguous=False)

    def simCAS(self, cseg, norm=True):
        """
        Return the CAS similarity value between the current and input csegs.

        This CAS similarity measurement works for csegs both with and
        without repeated cps. Also, the csegs need not be in normal form,
        because the same CAS value derives from csegs which are normalized
        or not.

        However, the cardinality of the input cseg must be the same as the
        current cseg, resulting in a pair of CASs that represent the same
        number of contour moves (i.e., the total of positive and negative
        moves) to measure the similarity. The maximum similarity value is 1.0,
        and minimum 0.0.

        >>> s1 = [0, 3, 2, 4, 1, 5]  # CAS(s1) = [1, -1, 1, -1, 1]
        >>> s2 = [3, 1, 2, 4, 5, 0]  # CAS(s2) = [-1, 1, 1, 1, -1]
        >>> Cseg(s1).simCAS(s2, norm=True)
        0.2

        :param cseg: c-segment
        :type cseg: segment
        :return: CAS similarity value [0.0, 1.0]
        :rtype: float
        """
        # Pretest
        if self.__len__() != len(cseg):
            return
        else:
            # checkInput is done in the CIS constructors.
            cas1, cas2 = self.cas(), CIS(cseg).cas()
            return CAS(cas1).sim(cas2, norm=norm)

    def simCASV(self, cseg, norm=True):
        """
        Return the CASV similarity value between the current and input csegs.

        This CASV similarity measurement works for csegs both with and
        without repeated cps. Also, the csegs need not be in normal form,
        because the same CASV value derives from csegs which are normalized
        or not.

        However, the cardinality of the input cseg must be the same as the
        current cseg, resulting in a pair of CASVs that represent the same
        number of contour moves (i.e., the total of positive and negative
        moves) to measure the similarity. The maximum similarity value is 1.0,
        and minimum 0.0.

        >>> s1 = [0, 3, 2, 4, 1, 5]  # CASV(s1) = [3, 2]
        >>> s2 = [3, 1, 2, 4, 5, 0]  # CASV(s2) = [3, 2]
        >>> Cseg(s1).simCASV(s2, norm=True)
        1.0

        :param cseg: c-segment
        :type cseg: segment
        :return: CASV similarity value [0.0, 1.0]
        :rtype: float
        """
        # Pretest
        if self.__len__() != len(cseg):
            return
        else:
            # checkInput is done in the CIS constructors.
            casv1, casv2 = self.casv(), CIS(cseg).casv()
            return CASV(casv1).sim(casv2, norm=norm)

    def simCCV1(self, cseg, norm=True):
        """
        Return the CCV1 similarity value between the current and input CCV1s.

        The input cseg must have the same cardinality as the current cseg,
        however, it does not have to be preprocessed to be in normal form--the
        method computes the similarity with its normal form accordingly.

        >>> x = [3, 2, 0, 1]  # cseg X
        >>> y = [1, 3, 0, 2]  # cseg Y
        >>> z = [0, 2, 0, 1]  # cseg Z
        >>> Cseg(x).simCCV1(y, norm=True)  # simCCV1(X,Y)
        0.6
        >>> Cseg(x).simCCV1(z, norm=True)  # simCCV1(X,Z)
        0.55

        :param cseg: c-segment
        :type cseg: segment
        :return: CCV1 similarity value [0.0, 1.0]
        :rtype: float
        """
        # Pretest
        card = self.__len__()
        if card != len(cseg):
            return
        else:
            # cseg is normalized when a CIA object is instantiated with it.
            # checkInput is done in the CIA constructors.
            ccv1_1, ccv1_2 = self.ccv1(), CIA(cseg).ccv1()
            return CCV1(ccv1_1).sim(ccv1_2, card=card, norm=norm)

    def simCCV2(self, cseg, norm=True):
        """
        Return the CCV2 similarity value between the current and input CCV2s.

        The input cseg must have the same cardinality as the current cseg,
        however, it does not have to be preprocessed to be in normal form--the
        method computes the similarity with its normal form accordingly.

        >>> x = [3, 2, 0, 1]  # cseg X
        >>> y = [1, 3, 0, 2]  # cseg Y
        >>> z = [0, 2, 0, 1]  # cseg Z
        >>> Cseg(x).simCCV2(y, norm=True)  # simCCV2(X,Y)
        0.6666666666666666
        >>> Cseg(x).simCCV2(z, norm=True)  # simCCV2(X,Z)
        0.5833333333333334

        :param cseg: c-segment
        :type cseg: segment
        :return: CCV2 similarity value [0.0, 1.0]
        :rtype: float
        """
        # Pretest
        card = self.__len__()
        if card != len(cseg):
            return
        else:
            # cseg is normalized when a CIA object is instantiated with it.
            # checkInput is done in the CIA constructors.
            ccv2_1, ccv2_2 = self.ccv2(), CIA(cseg).ccv2()
            return CCV2(ccv2_1).sim(ccv2_2, card=card, norm=norm)

    # Realization methods------------------------------------------------------

    def realize(self, pcset, tessitura=None, length=None, include=None,
                fixed=None):
        """
        Return a list of psegs possible with the current cseg.

        This method realizes melodic contours in p-space through associating
        the input pcset with the current cseg.

        As an infinite number of instances can be made when realizing a cseg
        in p-space, imposing some limitation factors yields a handful of
        psegs for selection.

        For more information about cseg realization, see Theory section of
        the API document.

        >>> cseg = Cseg([0, 2, 1, 0, 1])
        >>> cseg.realize({0,1,4})  # Long process time: need limitation factors
        [Pseg([24, 28, 25, 24, 25]),
         Pseg([36, 40, 37, 36, 37]),
         ...
         Pseg([25, 108, 100, 25, 100])]
        >>> cseg.realize({0,1,4}, tessitura=(48,72))
        [Pseg([48, 52, 49, 48, 49]),
         Pseg([60, 64, 61, 60, 61]),
         Pseg([49, 60, 52, 49, 52]),
         Pseg([61, 72, 64, 61, 64]),
         Pseg([52, 61, 60, 52, 60]),
         Pseg([48, 61, 52, 48, 52]),
         Pseg([48, 64, 49, 48, 49]),
         Pseg([49, 64, 60, 49, 60]),
         Pseg([48, 64, 61, 48, 61]),
         Pseg([52, 72, 61, 52, 61]),
         Pseg([49, 72, 52, 49, 52]),
         Pseg([49, 72, 64, 49, 64])]
        >>> cseg.realize({0,1,4}, tessitura=(48,72), length=(10,30))
        [Pseg([49, 60, 52, 49, 52]),
         Pseg([61, 72, 64, 61, 64]),
         Pseg([52, 61, 60, 52, 60]),
         Pseg([48, 61, 52, 48, 52])]
        >>> cseg.realize({0,1,4}, include=(76,), fixed={"-1": 61})
        [Pseg([60, 76, 61, 60, 61]),
         Pseg([48, 76, 61, 48, 61]),
         Pseg([36, 76, 61, 36, 61]),
         Pseg([24, 76, 61, 24, 61])]

        :param pcset: pcs to map to the current cseg.
        :param tessitura: (min, max) of the pitch range for the psegs to make.
            Default = (21, 108) that corresponds with the pitch range (A0, C8).
        :param length: (min, max) of the "length" for the pseg to make.
            Unlimited by default.
        :param include: the output psegs include these pitches.
        :param fixed: dict keys are the pitch positions to fix, and the
            values are the pitches.
        :type pcset: iterable
        :type tessitura: list/tuple
        :type length: list/tuple
        :type include: list/tuple
        :type fixed: dict
        :return: a list of Pseg objects which represent the psegs realized
            with the current cseg and the input pcset, and filtered by the
            conditions, tessitura, length, include, and fixed, if given.
            The Pseg objects are sorted by the length from short to long.
        :rtype: list
        """
        checkInput(pcset, checkPc=True, checkDup=True)
        pcset = list(pcset)
        cseg = self.normalForm()
        cardCseg = len(cseg)
        cardPcset = len(pcset)
        ucardCseg = countUniqueElements(cseg)
        minP = c.MIN_PITCH
        maxP = c.MAX_PITCH
        if tessitura is not None:
            minP = max(minP, tessitura[0])
            maxP = min(maxP, tessitura[1])

        # From the input pcset, make the variants to map to the current cseg.
        pcsets = []
        if cardCseg < cardPcset:  # Impossible mapping
            return
        elif cardCseg == cardPcset:
            if ucardCseg == cardPcset:  # No repeated cps
                # one-to-one, onto mapping
                pcsets.append(pcset)  # Single pcset possibility
            elif cardCseg > ucardCseg:  # Repeated cps; impossible mapping
                return
        else:  # #cseg > #pcset, also implied #cseg >= u#cseg
            if ucardCseg < cardPcset:
                return
            else:  # u#cseg >= #pcset
                # Onto (but not one-to-one) mapping
                for combi in combinations_with_replacement(pcset,
                                                           cardCseg-cardPcset):
                    pcsets.append(list(pcset) + list(combi))

        # Prepare all the permutations of the pcsets.
        pcsegs = {p for s in pcsets for p in permutations(s) if
                  repeatPattern(p) != 2}

        # Make a list of psegs possible with the pcsegs and the limitations.
        psegs = []
        pool = Pool(processes=c.MAX_PROCESSES)
        for pcseg in pcsegs:
            pool.apply_async(func=self._workerMakePsegs1,
                             args=(pcseg, minP, maxP, length, include,
                                   fixed, cseg),
                             callback=lambda r: psegs.extend(r))
        pool.close()
        pool.join()

        # Return a list of psegs sorted by the length from short to long.
        return list(sorted(psegs, key=lambda x: x.length()))

    def find(self, pseg, tessitura=None, length=None, include=None,
             fixed=None):
        """
        Return psubsegs that match the current cseg in the input pseg.

        In a large pseg many psubsegs with the current cseg are found;
        imposing some limitation factors yields a handful of psubsegs for
        selection.

        For more information about cseg finding, see Theory section of
        the API document.

        >>> pseg = [38, 46, 56, 57, 63, 65, 71, 78, 79, 84, 88, 97]
        >>> cseg = [0, 2, 1, 0, 3, 4]
        >>> Cseg(cseg).find(pseg) # Long process time: need limitation factors
        [Pseg([56, 63, 57, 56, 65, 71]),
         Pseg([78, 84, 79, 78, 88, 97]),
         ...
         Pseg([38, 84, 79, 38, 88, 97])]
        >>> Cseg(cseg).find(pseg, tessitura=(48, 84), include=(71,),
        ... fixed={"0": 63})
        [Pseg([63, 71, 65, 63, 78, 79]),
         Pseg([63, 71, 65, 63, 78, 84]),
         Pseg([63, 71, 65, 63, 79, 84]),
         Pseg([63, 78, 71, 63, 79, 84])]

        :param pseg: p-segment
        :param tessitura: (min, max) of the pitch range for the psubsegs to
            find. Default = (min(pseg), max(pseg)).
        :param length: (min, max) of the "length" for the psubsegs to find.
            Unlimited by default.
        :param include: the output psegs include these pitches.
        :param fixed: dict keys are the pitch positions to fix, and the
            values are the pitches.
        :type pseg: iterable
        :type tessitura: list/tuple
        :type length: list/tuple
        :type include: list/tuple
        :type fixed: dict
        :return: a list of Pseg objects which represent the psubsegs that
            match the current cseg in the input pseg, filtered by the
            conditions, tessitura, length, include, and fixed, if given. The
            Pseg objects are sorted by the length from short to long.
        :rtype: list
        """
        pseg = list(pseg)
        cseg = self.normalForm()
        cardCseg = len(cseg)
        ucardCseg = countUniqueElements(cseg)
        # Remove pitches outside tessitura.
        if tessitura is not None:
            pseg = [p for p in pseg if tessitura[0] <= p <= tessitura[1]]
        # Pretest: the input pseg needs at least u#cseg pitches.
        if ucardCseg > len(pseg):
            return

        # From the pseg, make a list of psets: #pset = #cseg = u#cseg (if
        #   cseg has no repeated cp), or #pset = #cseg != u#cseg (if cseg
        #   has repeated cp(s)).
        psets = []
        combis = combinations(pseg, ucardCseg)
        if cardCseg == ucardCseg:  # No cp repeats: pitch is unique in pset.
            psets = list(combis)
        else:  # #cseg > u#cseg (i.e., repeated-element cseg)
            # One or more pitches are duplicated in the psets.
            for combi in combis:
                additions = combinations_with_replacement(combi,
                                                          cardCseg-ucardCseg)
                for addition in additions:
                    psets.append(list(combi) + list(addition))

        # Make all the permutations of the psets, filtering them by the
        #   specified limitation factors.
        psegs = []
        pool = Pool(processes=c.MAX_PROCESSES)
        for pset in psets:
            pool.apply_async(func=self._workerMakePsegs2,
                             args=(pset, length, include, fixed, cseg),
                             callback=lambda r: psegs.extend(r))
        pool.close()
        pool.join()

        # Return a list of psegs sorted by the length from short to long.
        return list(sorted(psegs, key=lambda x: x.length()))

    # Private methods ---------------------------------------------------------

    def _workerMakePsegs1(self, pcseg, minPitch, maxPitch, length, include,
                          fixed, cseg):
        """
        Return a list of Pseg objects to accumulate in the main process.

        This is a Worker method used in ``Cseg.realize()``.
        """
        pitchesForPc = []
        for pc in pcseg:
            pitchesForPc.append([p for p in c.PITCHES[pc]
                                 if minPitch <= p <= maxPitch])
        candidates = [Pseg(pseg) for pseg in product(*pitchesForPc)]
        return self._psegFilters(candidates, length, include, fixed, cseg)

    def _workerMakePsegs2(self, pset, length, include, fixed, cseg):
        """
        Return a list of Pseg objects to accumulate in the main process.

        This is a Worker method used in ``Cseg.find()``.
        """
        candidates = [Pseg(pseg) for pseg in set(permutations(pset)) if
                      repeatPattern(pseg) != 2]
        return self._psegFilters(candidates, length, include, fixed, cseg)

    def _psegFilters(self, candidates, length, include, fixed, cseg):
        """Helper function for _workerMakePseg1/2."""
        # Filter the candidates by length.
        if length is not None:
            candidates = [pseg for pseg in candidates
                          if length[0] <= pseg.length() <= length[1]]
        # Filter the candidates by inclusion.
        if include is not None:
            candidates = [pseg for pseg in candidates
                          if set(include).issubset(pseg)]
        # Filter the candidates by fixed positions of pitches.
        if fixed is not None:
            temp = []
            for pseg in candidates:
                try:
                    if all([pseg[int(pos)] == val
                            for pos, val in fixed.items()]):
                        temp.append(pseg)
                except IndexError:
                    continue
            candidates = temp
        # Filter the candidates by cseg.
        psegs = [pseg for pseg in candidates if pseg.cseg() == cseg]

        return psegs
