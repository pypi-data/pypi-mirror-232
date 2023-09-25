import random
from itertools import permutations, combinations, combinations_with_replacement
from multiprocessing import Pool
from . import constants as c
from .utils import countUniqueElements
from .contour import Segclass, Segment, primeForm
from .mdspace import Mdseg

__all__ = ["Dsegclass", "Dseg"]


class Dsegclass(Segclass):
    """D-space segment-class"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, dseg):
        """
        Constructor method.

        The dsegclass is represented by the prime form of the input dseg.

        >>> Dsegclass([0, 2, 3, 1])
        Dsegclass([0, 2, 3, 1])

        :param dseg: d-segment.
        :type dseg: segment
        """
        Segclass.__init__(self, dseg)

    def __contains__(self, dur):
        """
        Return a bool of the dur membership to the current dsegclass.

        >>> s = Dsegclass([0, 2, 3, 1])
        >>> 2 in s
        True

        :param dur: dur to test the membership to the current dsegclass.
        :type dur: int
        :return: True if the dur is in self, False otherwise.
        :rtype: bool
        """
        return Segclass.__contains__(self, dur)

    def __getitem__(self, index):
        """
        Return the indexed dur of the current dsegclass.

        >>> Dsegclass([0, 2, 3, 1])[3]
        1

        :param index: index to get a dur.
        :type index: int
        :return: indexed dur.
        :rtype: int
        """
        return Segclass.__getitem__(self, index)

    def __iter__(self):
        """
        Return a generator object comprising the current dsegclass's durs.

        >>> for i in Dsegclass([0, 2, 3, 1]):
        ...     print(i, end="")
        0231
        """
        return Segclass.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current dsegclass.

        >>> len(Dsegclass([0, 2, 3, 1]))
        4
        """
        return Segclass.__len__(self)

    def __reversed__(self):
        """
        Return a reverse iterator of the current dsegclass's durs.

        >>> list(reversed(Dsegclass([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current dsegclass's durs in
            reverse order.
        :rtype: iterator
        """
        return Segclass.__reversed__(self)

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Dsegclass([0, 2, 3, 1])
        Dsegclass([0, 2, 3, 1])
        """
        return "Dsegclass({})".format(self.dsegclass)

    def count(self, dur):
        """
        Return the number of occurrences of the dur.

        >>> Dsegclass([0, 2, 3, 1]).count(2)
        1
        >>> Dsegclass([0, 2, 3, 1]).count(4)
        0

        :param dur: dur to check the occurrence frequency in the current
            Dsegclass.
        :type dur: int
        :return: the number of occurrences of the dur.
        :rtype: int
        """
        return Segclass.count(self, dur)

    def index(self, dur, start=0, stop=None):
        """
        Return the first index of the dur.

        Raise ValueError if the dur is not present.

        >>> Dsegclass([0, 2, 3, 1]).index(3)
        2
        >>> Dsegclass([0, 2, 3, 1]).index(4)
        ValueError

        :param dur: dur to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type dur: int
        :type start: int
        :type stop: int
        :return: first index of the dur.
        :rtype: int
        """
        return Segclass.index(self, dur, start=start, stop=stop)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Dsegclass(self.dsegclass)

    # Property methods --------------------------------------------------------

    @property
    def dsegclass(self):
        """
        Return the current dsegclass.

        >>> s = Dsegclass([3, 1, 0, 2])
        >>> s.dsegclass
        [0, 2, 3, 1]  # dsegclass is represented by the prime form.

        :return: current dsegclass.
        :rtype: list
        """
        return self._segclass

    @dsegclass.setter
    def dsegclass(self, dseg):
        """
        Set the current dsegclass to that of the input dseg.

        >>> s = Dsegclass([3, 1, 0, 2])
        >>> s.dsegclass = [1, 3, 0, 2]
        >>> s.dsegclass
        [1, 3, 0, 2]

        :param dseg: d-segment.
        :type dseg: segment
        """
        self._segclass = primeForm(dseg)

    # Analysis methods --------------------------------------------------------

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current dsegclass.

        >>> Dsegclass([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (numpy=False) or 2D ndarray (numpy=True) of the
            COM-matrix of the current dsegclass.
        :rtype: list or ndarray
        """
        return Segclass.comMatrix(self, nparr)

    def dsegclassName(self):
        """
        Return the name of the current dsegclass.

        >>> Dsegclass([0, 2, 3, 1]).dsegclassName()
        4-4

        :return: the name of the current dsegclass.
        :rtype: str
        """
        return Segclass.segclassName(self)

    def dsegclassMembers(self, nparr=False):
        """
        Return the members (P, I, R, and RI) of the current dsegclass.

        >>> Dsegclass([0, 2, 3, 1]).dsegclassMembers()
        {'I': [3, 1, 0, 2],
         'P': [0, 2, 3, 1],
         'R': [1, 3, 2, 0],
         'RI': [2, 0, 1, 3]}

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: the dict keys (P, I, R, and RI) are assigned with their
            corresponding segment as the values. The values are list
            (nparr=False) or numpy array (nparr=True) of normalized dseg.
        :rtype: dict
        """
        return Segclass.segclassMembers(self, nparr)

    def dsubsegs(self, normalize=False):
        """
        Return the dsubsegs (d-subsegments) of the current dsegclass.

        The cardinalities of the dsubsegs are 2 to the cardinality of the
        dsegclass. Therefore, the returned group of dsubsegs includes the
        dsegclass itself.

        >>> s = Dsegclass([0, 2, 3, 1])
        >>> s.dsubsegs()
        {2: [(0, 2), (2, 3), (3, 1)],
         3: [(0, 2, 3), (2, 3, 1)],
         4: [(0, 2, 3, 1)]}
        >>> s.dsubsegs(normalize=True)
        {2: [(0, 1), (0, 1), (1, 0)],
         3: [(0, 1, 2), (1, 2, 0)],
         4: [(0, 2, 3, 1)]}

        :param normalize: the output dsubsegs are normalized when True,
            otherwise as is.
        :type normalize: bool
        :return: the dict of the dsubsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return Segclass.subsegs(self, normalize=normalize, contiguous=True)

    def dsegclasses(self, func=1, sim=1.0, card=None):
        """
        Return dsegclasses within the similarity range.

        The returned dsegclasses are sorted by the lexicographic order and the
        number of repeated durs.

        >>> s = Dsegclass([0, 2, 3, 1])
        >>> s.dsegclasses(func=0, sim=0.7)  # DSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334),
         ((0, 1, 2, 1), 0.8333333333333334),
         ((0, 2, 2, 1), 0.8333333333333334)]
        >>> s.dsegclasses(func=1, card=4, sim=0.7)  # ADMEMB
        [((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334)]

        :param func: the function to measure the similarity: DSIM (0),
            ADMEMB (1).
        :param sim: similarity threshold [0, 1]. Measured with the current
            dsegclass, those dsegclasses which have a similarity value the
            same or higher than sim will be output.
        :param card: when card value is given, the output dsegclasses are of
            the specific cardinality.
        :type func: int
        :type sim: float
        :type card: int
        :return: tuples of dsegclass and similarity value pairs.
        :rtype: list of tuples
        """
        f = [1, 3][func]
        return Segclass.segclasses(self, func=f, sim=sim, card=card)

    # Relation methods --------------------------------------------------------

    def dsim(self, dseg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current dsegclass and the
        input dseg.

        The input dseg must have the same cardinality as the current
        dsegclass, however, does not have to be preprocessed to be in
        normal form nor prime form--the method computes the similarity with
        its dsegclass members accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> Dsegclass([0, 2, 3, 1]).dsim([3, 1, 0, 2]))
        1.0
        >>> Dsegclass([1, 0, 4, 3, 2]).dsim([1, 2, 4, 0, 3])
        0.8

        :param dseg: d-segment to measure the similarity with.
        :type dseg: segment
        :return: similarity value [0, 1]
        :rtype: float
        """
        return Segclass.xsim(self, dseg)

    def demb(self, dseg):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input dseg does not have to be preprocessed to be in normal form
        nor prime form: the method computes the similarity with its dsegclass
        members accordingly.

        .. Note::
            This contour similarity measurement method only works with
            dsegs of differing cardinalities: the input dseg must be
            larger than the current dsegclass.

        See the description of ``contour.xemb()`` for more detail.

        >>> Dsegclass([0, 1, 2]).demb([3, 1, 4, 2, 0])
        0.3333333333333333

        :param dseg: d-segment.
        :type dseg: segment
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return Segclass.xemb(self, dseg, contiguous=True)

    def admemb(self, dseg, admembOpt=False):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        This contour similarity measurement method works with dsegclasses of
        both equal or unequal cardinalities: the input dseg may or may not be
        the same size as the current dsegclass.

        The input dseg does not have to be preprocessed to be in normal form
        nor prime form: the method computes the similarity with its dsegclass
        members accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> a = Dsegclass([2, 1, 0, 3])
        >>> b = Dsegclass([2, 0, 3, 1])
        >>> c = Dsegclass([3, 5, 2, 0, 6, 4, 1, 7])
        >>> a.admemb(c, admembOpt=True) # ADMEMB(A_,C_)
        0.5588235294117647
        >>> b.admemb(c, admembOpt=True) # ADMEMB(B_,C_)
        0.4411764705882353
        >>> a.admemb(b, admembOpt=True) # ADMEMB(A_,B_)
        0.6666666666666666

        :param dseg: d-segment to measure the similarity with.
        :type dseg: segment
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return Segclass.axmemb(self, dseg, contiguous=True,
                               admembOpt=admembOpt)


class Dseg(Segment):
    """D-space segment"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, dseg):
        """
        Constructor method.

        >>> Dseg([0, 2, 3, 1])
        Dseg([0, 2, 3, 1])

        :param dseg: d-segment.
        :type dseg: segment
        """
        Segment.__init__(self, dseg)

    def __contains__(self, dur):
        """
        Return a bool of the dur membership to the current dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> 2 in s
        True

        :param dur: dur to test the membership to the current dseg.
        :type dur: int
        :return: True if the dur is in self, False otherwise.
        :rtype: bool
        """
        return Segment.__contains__(self, dur)

    def __delitem__(self, index):
        """
        Delete the indexed element.

        >>> s = Dseg([0, 2, 3, 1])
        >>> del s[2]
        >>> s
        [0, 2, 1]

        :param index: index at which the element is deleted.
        """
        del self._seg[index]

    def __getitem__(self, index):
        """
        Return the indexed dur of the current dseg.

        >>> Dseg([0, 2, 3, 1])[3]
        1

        :param index: index to get a dur.
        :type index: int
        :return: indexed dur.
        :rtype: int
        """
        return Segment.__getitem__(self, index)

    def __iadd__(self, dseg):
        """
        Append the input dseg to the current dseg in-place.

        This operation is equivalent to self.extend(dseg) but invoked by +=
        operator.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s += [4, 6, 5]
        Dseg([0, 2, 3, 1, 4, 6, 5])

        :param dseg: dseg to append to the current dseg.
        :type dseg: segment
        :return: mutated dseg.
        :rtype: Dseg object
        """
        Segment.__iadd__(self, dseg)
        return self

    def __iter__(self):
        """
        Return a generator object comprising the current dseg's durs.

        >>> for i in Dseg([0, 2, 3, 1]):
        ...     print(i, end="")
        0231

        :return: iterator with the current dseg's elements.
        :rtype: iterator
        """
        return Segment.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the dseg.

        >>> len(Dseg([0, 2, 3, 1]))
        4
        """
        return Segment.__len__(self)

    def __reversed__(self):
        """
        Return a reverse iterator of the current dseg's durs.

        >>> list(reversed(Dseg([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current dseg's durs in
            reverse order.
        :rtype: iterator
        """
        return Segment.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed element.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s[2] = 0
        >>> s
        [0, 2, 0, 1]

        :param index: index at which the element changes the value.
        :param value: value to change the indexed element.
        :type index: int
        :type value: int
        """
        self._seg[index] = value

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Dseg([0, 2, 3, 1])
        Dseg([0, 2, 3, 1])

        :return: official representation of the object.
        :rtype: str
        """
        return "Dseg({})".format(self._seg)

    def append(self, dur):
        """
        Append a single dur to the end of the current dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.append(4)
        Dseg([0, 2, 3, 1, 4])

        :param dur: dur to append.
        :type dur: int
        :return: mutated dseg.
        :rtype: Dseg object
        """
        Segment.append(self, dur)
        return self

    def count(self, dur):
        """
        Return the number of occurrences of the dur.

        >>> Dseg([0, 2, 3, 1]).count(2)
        1
        >>> Dseg([0, 2, 3, 1]).count(4)
        0

        :param dur: dur to check the occurrence frequency in the current dseg.
        :type dur: int
        :return: the number of occurrences of the dur.
        :rtype: int
        """
        return Segment.count(self, dur)

    def extend(self, dseg):
        """
        Extend the current dseg by appending the input dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.extend([4, 6, 5])
        Dseg([0, 2, 3, 1, 4, 6, 5])

        :param dseg: dseg to append to the current dseg.
        :type dseg: segment
        :return: mutated dseg.
        :rtype: Dseg object
        """
        Segment.extend(self, dseg)
        return self

    def index(self, dur, start=0, stop=None):
        """
        Return the first index of the dur.

        Raise ValueError if the dur is not present.

        >>> Dseg([0, 2, 3, 1]).index(3)
        2
        >>> Dseg([0, 2, 3, 1]).index(4)
        ValueError

        :param dur: dur to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type dur: int
        :type start: int
        :type stop: int
        :return: first index of the dur.
        :rtype: int
        """
        return Segment.index(self, dur, start=start, stop=stop)

    def insert(self, index, dur):
        """
        Insert the dur at the specified index of the dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.insert(3, 2)
        Dseg([0, 2, 3, 2, 1])

        :param index: index at which the dur is inserted.
        :param dur: element to insert.
        :type index: int
        :type dur: int
        :return: mutated dseg.
        :rtype: Dseg object
        """
        self._seg.insert(index, dur)
        return self

    def pop(self, index=-1):
        """
        Remove and return an element at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.pop()
        1
        >>> s.pop(1)
        2
        >>> s
        [0, 3]

        :param index: index at which the element is popped.
        :type index: int
        :return: popped element.
        :rtype: int
        """
        return Segment.pop(self, index=index)

    def remove(self, value):
        """
        Remove the first occurrence of an element with the input value.

        Raise ValueError if the value is not present.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.remove(3)
        Dseg([0, 2, 1])

        :param value: value with which an element is removed.
        :type value: int
        :return: mutated dseg.
        :rtype: Dseg object
        """
        Segment.remove(self, value)
        return self

    def reverse(self):
        """
        Reverse the current dseg in place.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.reverse()
        Dseg([1, 3, 2, 0])

        :return: mutated dseg.
        :rtype: Dseg object
        """
        return Segment.reverse(self)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Dseg(self._seg)

    # Property methods --------------------------------------------------------

    @property
    def dseg(self):
        """
        Return the current dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.dseg
        [0, 2, 3, 1]

        :return: current dseg.
        :rtype: list
        """
        return self._seg

    @dseg.setter
    def dseg(self, dseg_):
        """
        Set the current dseg to the input dseg.

        >>> a = Dseg([0, 2, 3, 1])
        >>> a.dseg = [1, 3, 0, 2]
        >>> a.dseg
        [1, 3, 0, 2]

        :param dseg_: contour segment.
        :type dseg_: segment
        """
        self._seg = list(dseg_)

    # Mutator methods ---------------------------------------------------------

    def normalize(self):
        """
        Normalize the current cseg.

        See ``contour.normalForm()`` for more detail.

        >>> Dseg([1, 5, 3, 2]).normalize()
        Dseg([0, 3, 2, 1])

        :return: normal form of the current dseg.
        :rtype: Dseg object
        """
        return Segment.normalize(self)

    def invert(self):
        """
        Invert the current dseg.

        >>> Dseg([0, 2, 3, 1]).invert()
        Dseg([3, 1, 0, 2])

        :return: inversion of the current dseg.
        :rtype: Dseg object
        """
        return Segment.invert(self)

    def retrograde(self):
        """
        Retrograde the current dseg.

        >>> Dseg([0, 2, 3, 1]).retrograde()
        Dseg([1, 3, 2, 0])

        :return: retrograde of the current dseg.
        :rtype: Dseg object
        """
        return Segment.retrograde(self)

    def rotate(self, n, mode=0):
        """
        Cyclically permute the durs of the current dseg.

        >>> s = Dseg([0, 2, 3, 1])
        >>> s.copy().rotate(1, mode=0))
        Dseg([2, 3, 1, 0])
        >>> s.copy().rotate(1, mode=1))
        Dseg([1, 3, 0, 2])

        :param n: rotation index: the number of positions the durs are
            rotated. The index is calculated as n % cardinality, so n may be
            arbitrary int.
        :param mode: rotation mode: temporal order rotation(0), d-space
            registral order rotation (1).
        :type n: int
        :return: rotation of the current dseg
        :rtype: Dseg object
        """
        return Segment.rotate(self, n=n, mode=mode)

    def opI(self):
        """Shorthand for invert()."""
        return self.invert()

    def opR(self):
        """Shorthand for retrograde()."""
        return self.retrograde()

    def opRI(self):
        """Return the retrograde inversion of the current dseg."""
        return self.invert().retrograde()

    def simTransform(self, func=1, sim=0, card=None, fixed=None):
        """
        Transform the current dseg based on similarity.

        >>> a = Dseg([0, 2, 3, 1])
        >>> a.dsegs(func=1, sim=0.6, card=4, fixed={"-1": 0})  # candidates
        [((1, 2, 3, 0), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334),
         ((2, 1, 3, 0), 0.6666666666666666),
         ((2, 3, 1, 0), 0.6666666666666666),
         ((3, 1, 2, 0), 0.6666666666666666),
         ((2, 1, 2, 0), 0.6666666666666666)]
        >>> a.simTransform(func=1, sim=0.6, card=4, fixed={"-1": 0})
        Dseg([2, 1, 3, 0])

        :param func: the function to measure the similarity: DSIM (0), or
            ADMEMB (1)
        :param sim: similarity threshold [0, 1]. Measured with the current
            dseg, those dsegs which have a similarity value the same or higher
            than the sim value will be the candidate for transformation.
        :param card: when card value is given, the transformed dseg is of the
            specified cardinality.
        :param fixed: dict keys are the element positions to fix, and values
            are the elements' values.
        :type func: int
        :type sim: float
        :type card: int
        :type fixed: dict
        :return: similarity-transformation of the current dseg.
        :rtype: Dseg object
        """
        candidates = [i[0] for i in
                      self.dsegs(func=func, sim=sim, card=card, fixed=fixed)]
        if len(candidates) > 0:
            self._seg = list(random.choice(candidates))
        else:
            self._seg = []
        return self

    # Analysis methods --------------------------------------------------------

    def normalForm(self, nparr=False):
        """
        Return the normal form of the current dseg.

        See ``contour.normalForm()`` for more detail.

        >>> Dseg([-12, 8, 0, -2]).normalForm()
        [0, 3, 2, 1]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or a ndarray (nparr=True) of the
            current dseg.
        :rtype: list or ndarray
        """
        return Segment.normalForm(self, nparr=nparr)

    def primeForm(self, nparr=False):
        """
        Return the prime form of the current dseg.

        >>> Dseg([3, 1, 2, 0]).primeForm()
        [0, 2, 1, 3]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (numpy=False) or ndarray (numpy=True) of the prime
            form of the current dseg.
        :rtype: list or ndarray
        """
        return Segment.primeForm(self, nparr=nparr)

    def isNormalForm(self):
        """
        Return a bool that indicates whether the current dseg is normalized.

        >>> Dseg([0, 1, 4, 2]).isNormalForm()  # NF = [0, 1, 3, 2]
        False

        :return: True if dseg is normalized, False otherwise.
        :rtype: bool
        """
        return Segment.isNormalForm(self)

    def isPrimeForm(self):
        """
        Return a bool that indicates whether the current dseg is the prime
        form.

        >>> Dseg([1, 3, 2, 0]).isPrimeForm()  # PF = [0, 2, 3, 1]
        False

        :return: True if dseg is the prime form, False otherwise.
        :rtype: bool
        """
        return Segment.isPrimeForm(self)

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current dseg.

        >>> Dseg([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (numpy=False) or 2D ndarray (numpy=True) of the
            COM-matrix of the current dseg.
        :rtype: list or ndarray
        """
        return Segment.comMatrix(self, nparr=nparr)

    def dsegclassRelation(self):
        """
        Return the relation status of the current dseg tDo its dsegclass.

        See ``contour.segclassRelation`` for more detail.

        >>> Dseg([4, 1, 3, 2]).segclassRelation()  # Unnormalized
        -1
        >>> Dseg([0, 1, 3, 2]).segclassRelation()  # P (identity)
        0
        >>> Dseg([3, 2, 0, 1]).segclassRelation()  # I
        1
        >>> Dseg([2, 3, 1, 0]).segclassRelation()  # R
        2
        >>> Dseg([1, 0, 2, 3]).segclassRelation()  # RI
        3
        >>> Dseg([0, 2, 1, 3]).segclassRelation()  # Both P and RI related
        4
        >>> Dseg([3, 1, 2, 0]).segclassRelation()  # Both I and R related
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

    def dsubsegs(self, normalize=False):
        """
        Return the dsubsegments of the current dseg.

        The cardinalities of the dsubsegs are 2 to the cardinality of the
        current dseg. Therefore, the returned group of dsubsegments includes
        the current dseg itself.

        >>> a = Dseg([0, 6, 1, -12]).dsubsegs(normalize=True)
        >>> b = Dseg([1, 3, 2, 0]).dsubsegs(normalize=True)
        >>> a == b
        True
        >>> a
        {2: [(0, 1), (1, 0), (1, 0)],
         3: [(0, 2, 1), (2, 1, 0)],
         4: [(1, 3, 2, 0)]}

        :param normalize: the output dsubsegs are normalized when True,
            otherwise as is.
        :type normalize: bool
        :return: the dict of the dsubsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return Segment.subsegs(self, normalize=normalize, contiguous=True)

    def dsegs(self, func=1, sim=1.0, card=None, fixed=None):
        """
        Return dsegs within the similarity range.

        The output list of dsegs is in the order of similarity value high to
        low.

        Optional filtering criteria may be given for filtering the dsegs (the
        cardinality of and fixed elements in the dseg).

        >>> a = Dseg([0, 2, 3, 1])
        >>> a.segs(func=0, sim=0.8)  # DSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ...
         ((0, 2, 2, 1), 0.8333333333333334)]
        >>> a.segs(func=1, sim=0.6, fixed={"2": 1})  # ADMEMB
        [((2, 0, 1, 3), 0.6666666666666666),
         ((2, 3, 1, 0), 0.6666666666666666),
         ...
         ((2, 0, 1, 2), 0.6666666666666666)]

        :param func: the function to measure the similarity: DSIM (0) or
            ADMEMB (1).
        :param sim: similarity threshold [0.0, 1.0]. Measured with the current
            dseg, those dsegs which have a similarity value the same or higher
            than the sim value will be output.
        :param card: when card value is given, the output dsegs are of the
            specified cardinality.
        :param fixed: dict keys are the element positions to fix, and the
            values are the elements' values.
        :type func: int
        :type sim: float
        :type card: int
        :type fixed: dict
        :return: pairs of dseg and similarity value.
        :rtype: list of tuples
        """
        f = [1, 3][func]
        return Segment.segs(self, func=f, sim=sim, card=card, fixed=fixed)

    # Relation methods---------------------------------------------------------

    def dsim(self, dseg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current and the input dsegs.

        The input dseg must have the same cardinality as the current dseg,
        however, it does not have to be preprocessed to be in normal form--the
        method computes the similarity with its normal form accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> a = Dseg([2, 0, 1, 3])
        >>> b = [0, 1, 2, 3]
        >>> c = [1, 3, 0, 2]
        >>> d = [0, 2, 3, 1]
        >>> a.dsim(b)  # DSIM(A,B)
        0.6666666666666666
        >>> a.dsim(c)  # DSIM(A,C)
        0.5
        >>> a.dsim(d)  # DSIM(A,D)
        0.3333333333333333

        :param dseg: d-segment to measure the similarity with.
        :type dseg: segment
        :return: similarity value [0.0, 1.0].
        :rtype: float
        """
        return Segment.xsim(self, dseg)

    def demb(self, dseg):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input dseg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        .. Note::
            This contour similarity measurement method only works with
            dsegs of differing cardinalities--the input dseg must be
            larger than the current dseg.

        See the description of ``contour.xemb()`` for more detail.

        >>> a = [2, 1, 0, 3]
        >>> b = [3, 5, 2, 0, 6, 4, 1, 7]
        >>> Dseg(a).demb(b)  # DEMB(A,B)
        0.4

        :param dseg: d-segment to measure the similarity with.
        :type dseg: segment
        :return: the contour similarity value [0.0, 1.0].
        :rtype: float
        """
        return Segment.xemb(self, dseg, contiguous=True)

    def admemb(self, dseg, admembOpt=False):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        This contour similarity measurement method works with dsegs of
        both equal or unequal cardinalities--the input dseg may or may not be
        the same size as the current dseg.

        The input dseg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> # ADMEMB(C,D) with optimization on
        >>> a = [2, 1, 0, 3]
        >>> b = [3, 5, 2, 0, 6, 4, 1, 7]
        >>> Dseg(a).admemb(b, admembOpt=True)
        0.5588235294117647

        :param dseg: d-segment to measure the similarity with.
        :type dseg: segment
        :return: the contour similarity value [0.0, 1.0].
        :rtype: float
        """
        return Segment.axmemb(self, dseg, contiguous=True, admembOpt=admembOpt)

    # Realization methods------------------------------------------------------

    def realize(self, mdset, length=None, include=None, fixed=None):
        """
        Return a list of mdsegs possible with the current dseg.

        This method realizes rhythmic contours in md-space through associating
        the input mdset with the current dseg.

        For more information about dseg realization, see Theory section of
        the API document.

        >>> dseg = Dseg([0, 2, 1, 1, 1, 3])
        >>> mdset = {0.25, 0.5, 0.75, 1.0, 1.5, 2.0}
        >>> dseg.realize(mdset)
        [Mdseg([0.25, 0.75, 0.5, 0.5, 0.5, 1.0]),
         Mdseg([0.25, 0.75, 0.5, 0.5, 0.5, 1.5]),
         Mdseg([0.25, 1.0, 0.5, 0.5, 0.5, 1.5]),
         Mdseg([0.25, 0.75, 0.5, 0.5, 0.5, 2.0]),
         Mdseg([0.25, 1.0, 0.5, 0.5, 0.5, 2.0]),
         Mdseg([0.25, 1.0, 0.75, 0.75, 0.75, 1.5]),
         Mdseg([0.25, 1.5, 0.5, 0.5, 0.5, 2.0]),
         Mdseg([0.5, 1.0, 0.75, 0.75, 0.75, 1.5]),
         Mdseg([0.25, 1.0, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.0, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.25, 1.5, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.5, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.25, 1.5, 1.0, 1.0, 1.0, 2.0]),
         Mdseg([0.5, 1.5, 1.0, 1.0, 1.0, 2.0]),
         Mdseg([0.75, 1.5, 1.0, 1.0, 1.0, 2.0])]
        >>> dseg.realize(mdset, fixed={"0": 0.5})
        [Mdseg([0.5, 1.0, 0.75, 0.75, 0.75, 1.5]),
         Mdseg([0.5, 1.0, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.5, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.5, 1.0, 1.0, 1.0, 2.0])]
        >>> dseg.realize(mdset, fixed={"0": 0.5}, include=(1.5,))
        [Mdseg([0.5, 1.0, 0.75, 0.75, 0.75, 1.5]),
         Mdseg([0.5, 1.5, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.5, 1.0,  1.0, 1.0, 2.0])]
        >>> dseg.realize(mdset, fixed={"0": 0.5}, include=(1.5,),
        ... length=(6.0, 7.0))
        [Mdseg([0.5, 1.5, 0.75, 0.75, 0.75, 2.0]),
         Mdseg([0.5, 1.5, 1.0, 1.0, 1.0, 2.0])]

        :param mdset: mdurs to map to the current dseg.
        :param length: (min, max) of the "length" for the mdseg to make.
            Unlimited by default.
        :param include: the output mdsegs include these mdurs.
        :param fixed: dict keys are the mdur positions to fix, and the
            values are the mdurs.
        :type mdset: iterable
        :type length: list/tuple
        :type include: list/tupel
        :type fixed: dict
        :return: a list of Mdseg objects which represent the mdsegs realized
            with the current dseg and the input mdset, and filtered by the
            conditions, length, include, and fixed, if given. The Mdseg
            objects are sorted by the length from short to long.
        :rtype: list
        """
        dseg = self.normalForm()
        mdset = list(mdset)
        cardDseg = len(dseg)
        cardMdset = len(mdset)
        ucardDseg = countUniqueElements(dseg)

        # Pretest: the input mdset needs at least u#dseg mdurs.
        if ucardDseg > cardMdset:
            return

        # From the input mdset, make the variants to map to the current dseg.
        mdsets = [list(combi) for combi in combinations(mdset, ucardDseg)]
        # Duplicate mdur(s) in case of a repeated-element dseg.
        if ucardDseg < cardDseg:  # u#dseg < #dseg (durs repeated)
            diff = cardDseg - ucardDseg
            bags = []
            for m in mdsets:
                for rep in combinations_with_replacement(m, diff):
                    bags.append(m + list(rep))
            mdsets = bags

        # Make a list of mdsegs possible with the perms and the limitations.
        mdsegs = []
        pool = Pool(processes=c.MAX_PROCESSES)
        for mdset in mdsets:
            pool.apply_async(func=self._workerMakeMdsegs,
                             args=(mdset, length, include, fixed, dseg),
                             callback=lambda r: mdsegs.extend(r))
        pool.close()
        pool.join()

        # Return a list of mdsegs sorted by the length from short to long.
        return list(sorted(mdsegs, key=lambda x: x.length()))

    # Private methods ---------------------------------------------------------

    def _workerMakeMdsegs(self, mdset, length, include, fixed, dseg):
        """
        Return a list of Mdseg objects to accumulate in the main process.

        This is a Worker method used in ``Dseg.realize()``.
        """
        candidates = [Mdseg(m) for m in set(permutations(mdset))]

        # Filter the candidates by length.
        if length is not None:
            candidates = [mdseg for mdseg in candidates
                          if length[0] <= mdseg.length() <= length[1]]
        # Filter the candidates by inclusion.
        if include is not None:
            candidates = [mdseg for mdseg in candidates
                          if set(include).issubset(mdseg)]
        # Filter the candidates by fixed positions of pitches.
        if fixed is not None:
            temp = []
            for mdseg in candidates:
                try:
                    if all([mdseg[int(pos)] == val
                            for pos, val in fixed.items()]):
                        temp.append(mdseg)
                except IndexError:
                    continue
            candidates = temp
        # Filter the candidates by dseg.
        mdsegs = [mdseg for mdseg in candidates if mdseg.dseg() == dseg]

        return mdsegs
