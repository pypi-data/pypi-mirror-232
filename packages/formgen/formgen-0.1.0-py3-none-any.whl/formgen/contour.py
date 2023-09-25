from itertools import combinations
from collections import Counter
from collections.abc import Sequence, MutableSequence
import numpy as np
from .query import catalog, toSegclassName
from .utils import adaptOutput, countRepeatedElements, factorial

__all__ = ["Segclass",
           "Segment",
           "isNormalForm",
           "isPrimeForm",
           "normalForm",
           "primeForm",
           "comMatrix",
           "int_comMatrix",
           "segclassMembers",
           "segclassRelation",
           "subsegs",
           "inversion",
           "retrograde",
           "opI",
           "opR",
           "opRI",
           "rotation",
           "xsim",
           "xemb",
           "xmemb",
           "axmemb"]


class Segclass(Sequence):
    """Generic class for contour segclass."""

    # Basic methods -----------------------------------------------------------

    def __init__(self, seg):
        """
        Constructor method.

        The segclass is represented by the prime form of the input seg.

        >>> Segclass([0, 2, 3, 1])

        :param seg: contour segment.
        :type seg: segment
        """
        Sequence.__init__(self)
        self._segclass = primeForm(seg)

    def __contains__(self, element):
        """
        Return a bool of the element membership to the current segclass.

        >>> s = Segclass([0, 2, 3, 1])
        >>> 2 in s
        True

        :param element: element to test the membership to the current segclass.
        :type element: int
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return Sequence.__contains__(self, element)

    def __getitem__(self, index):
        """
        Return the indexed element of the current segclass.

        >>> Segclass([0, 2, 3, 1])[3]
        1

        :param index: index to get an element.
        :type index: int
        :return: indexed element.
        :rtype: int
        """
        return self._segclass[index]

    def __iter__(self):
        """
        Return an iterator object comprising the current segclass's elements.

        >>> for i in Segclass([0, 2, 3, 1]):
        ...     print(i, end="")
        0231

        :return: iterator with the current segclass elements.
        :rtype: iterator
        """
        return Sequence.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current segclass.

        >>> len(Segclass([0, 2, 3, 1]))
        4

        :return: cardinality of the current segclass.
        :rtype: int
        """
        return len(self._segclass)

    def __reversed__(self):
        """
        Return a reverse iterator of the current segclass's elements.

        >>> list(reversed(Segclass([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current segclass
            elements in reverse order.
        :rtype: iterator
        """
        return Sequence.__reversed__(self)

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Segclass([0, 2, 3, 1])
        Segclass([0, 2, 3, 1])
        """
        return "Segclass({})".format(self._segclass)

    def count(self, element):
        """
        Return the number of occurrences of the element.

        >>> Segclass([0, 2, 3, 1]).count(2)
        1
        >>> Segclass([0, 2, 3, 1]).count(4)
        0

        :param element: element to check the occurrence frequency in the
            current segclass.
        :type element: int
        :return: the number of occurrences of the element.
        :rtype: int
        """
        return Sequence.count(self, element)

    def index(self, element, start=0, stop=None):
        """
        Return the first index of the element.

        Raise ValueError if the element is not present.

        >>> Segclass([0, 2, 3, 1]).index(3)
        2
        >>> Segclass([0, 2, 3, 1]).index(4)
        ValueError
        >>> Segclass([0, 1, 2, 0]).index(0, 1)
        3

        :param element: segclass element to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type element: int
        :type start: int
        :type stop: int
        :return: first index of the segclass element.
        :rtype: int
        """
        if stop is None:
            stop = len(self._segclass)
        return Sequence.index(self, element, start, stop)

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Segclass(self._segclass)

    # Property methods --------------------------------------------------------

    @property
    def segclass(self):
        """
        Return the current segclass.

        >>> s = Segclass([3, 1, 0, 2])
        >>> s.segclass
        [0, 2, 3, 1]  # segclass is represented by the prime form.

        :return: current segclass.
        :rtype: list
        """
        return self._segclass

    @segclass.setter
    def segclass(self, seg):
        """
        Set the current segclass to that of the input seg.

        >>> s = Segclass([3, 1, 0, 2])
        >>> s.segclass = [1, 3, 0, 2]
        >>> s.segclass
        [1, 3, 0, 2]

        :param seg: contour segment.
        :type seg: segment
        """
        self._segclass = primeForm(seg)

    # Analysis methods --------------------------------------------------------

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current segclass.

        >>> Segclass([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (nparr=False) or 2D ndarray (nparr=True) of the
            COM-matrix of the current segclass.
        :rtype: list or ndarray
        """
        return comMatrix(self._segclass, nparr)

    def segclassName(self):
        """
        Return the name of the current segclass.

        >>> Segclass([0, 2, 3, 1]).segclassName()
        4-4

        :return: the name of the current segclass.
        :rtype: str
        """
        return toSegclassName(tuple(self._segclass))

    def segclassMembers(self, nparr=False):
        """
        Return the members (P, I, R, and RI) of the current segclass.

        >>> Segclass([0, 2, 3, 1]).segclassMembers()
        {'I': [3, 1, 0, 2],
         'P': [0, 2, 3, 1],
         'R': [1, 3, 2, 0],
         'RI': [2, 0, 1, 3]}

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: the dict keys (P, I, R, and RI) are assigned with their
            corresponding segment as the values. The values are list
            (nparr=False) or numpy array (nparr=True) of normalized
            seg.
        :rtype: dict
        """
        return segclassMembers(self._segclass, nparr)

    def subsegs(self, normalize=False, contiguous=False):
        """
        Return the subsegments of the current segclass.

        The cardinalities of the subsegs are 2 to the cardinality of the
        segclass. Therefore, the returned group of subsegs includes the
        segclass itself.

        >>> s = Segclass([0, 2, 3, 1])
        >>> s.subsegs()
        {2: [(0, 2), (0, 3), (0, 1), (2, 3), (2, 1), (3, 1)],
         3: [(0, 2, 3), (0, 2, 1), (0, 3, 1), (2, 3, 1)],
         4: [(0, 2, 3, 1)]}
        >>> s.subsegs(normalize=True)
        {2: [(0, 1), (0, 1), (0, 1), (0, 1), (1, 0), (1, 0)],
         3: [(0, 1, 2), (0, 2, 1), (0, 2, 1), (1, 2, 0)],
         4: [(0, 2, 3, 1)]}
        >>> s.subsegs(contiguous=True)
        {2: [(0, 2), (2, 3), (3, 1)],
         3: [(0, 2, 3), (2, 3, 1)],
         4: [(0, 2, 3, 1)]}

        :param normalize: the output subsegs are normalized when True,
            otherwise as is.
        :param contiguous: the output subsegs include only contiguous ones when
            True, otherwise all the subsegs are returned.
        :type normalize: bool
        :type contiguous: bool
        :return: the dict of the subsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return subsegs(self._segclass, normalize, contiguous)

    def segclasses(self, func=2, sim=1.0, card=None):
        """
        Return segclasses within the similarity range.

        The returned segclasses are sorted by the lexicographic order and the
        number of repeated elements.

        >>> s = Segclass([0, 2, 3, 1])
        >>> s.segclasses(func=0, sim=0.7))  # CSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334),
         ((0, 1, 2, 1), 0.8333333333333334)]
        >>> s.segclasses(func=1, sim=0.7))  # DSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334),
         ((0, 1, 2, 1), 0.8333333333333334),
         ((0, 2, 2, 1), 0.8333333333333334)]
        >>> s.segclasses(func=2, sim=0.7))  # ACMEMB
        [((0, 1, 3, 2), 0.8636363636363636),
         ((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 3, 2, 1), 0.8181818181818182),
         ((0, 2, 1), 0.8),
         ((1, 3, 0, 2), 0.7727272727272727),
         ((1, 0, 3, 2), 0.7272727272727273),
         ((0, 1, 0, 2), 0.7272727272727273),
         ((0, 1, 2, 1), 0.7272727272727273)]
        >>> s.segclasses(func=3, card=4, sim=0.7)  # ADMEMB
        [((0, 3, 2, 1), 0.8333333333333334),
         ((0, 1, 2, 0), 0.8333333333333334)]

        :param func: the function to measure the similarity:

            * CSIM (0)
            * DSIM (1)
            * ACMEMB (2)
            * ADMEMB (3)

        :param sim: similarity threshold [0, 1]. Measured with the current
            segclass, those segclasses which have a similarity value the
            same or higher than sim will be output.
        :param card: when card value is given, the output segclasses are of the
            specific cardinality.
        :type func: int
        :type sim: float
        :type card: int
        :return: tuples of segclass and similarity value pairs.
        :rtype: list of tuples
        """
        m = ["CSIM", "DSIM", "ACMEMB", "ADMEMB"][func]
        dct = catalog["similaritySegclass"][tuple(self._segclass)][m]
        # list of segclasses (in the order of the similarity value high to low)
        segclasses = []
        for i in dct.items():
            if i[1] >= sim:
                segclasses.append(i)
            else:
                # Short-circuit evaluation!
                break
        # Filter the candidates by the cardinality.
        if card is not None:
            segclasses = [s for s in segclasses if len(s[0]) == card]
        return segclasses

    # Relation methods --------------------------------------------------------

    def xsim(self, seg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current segclass and the
        input seg.

        The input seg must have the same cardinality as the current
        segclass, however, does not have to be preprocessed to be in
        normal form nor prime form--the method computes the similarity with
        its segclass members accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> Segclass([0, 2, 3, 1]).xsim([3, 1, 0, 2]))
        1.0
        >>> Segclass([1, 0, 4, 3, 2]).xsim([1, 2, 4, 0, 3]))
        0.8

        :param seg: contour segment to measure the similarity with.
        :type seg: segment
        :return: similarity value [0, 1]
        :rtype: float
        """
        return xsim(self._segclass, seg, segclass=True)

    def xemb(self, seg, contiguous=False):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input seg does not have to be preprocessed to be in normal form
        nor prime form: the method computes the similarity with its segclass
        members accordingly.

        XEMB defined here is a generic form and functions as CEMB(A\_,
        B\_) (contiguous=False) and DEMB(A\_,B\_) (contiguous=True). The
        maximum similarity value is 1, and minimum 0.

        .. note::
            This contour similarity measurement method only works with
            segments of differing cardinalities: the input seg must be
            larger than the current segclass.

        See the description of ``contour.xemb()`` for more detail.

        >>> a = Segclass([0, 1, 2])
        >>> b = [3, 1, 4, 2, 0]
        >>> a.xemb(b)                   # CEMB(A_,B_) = 0.3
        0.3
        >>> a.xemb(b, contiguous=True)  # DEMB(A_,B_) = 0.33
        0.3333333333333333

        :param seg: contour segment.
        :param contiguous: the bool selects CEMB (False) or DEMB (True) to
            invoke.
        :type seg: segment
        :type contiguous: bool
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return xemb(self._segclass, seg, contiguous=contiguous, segclass=True)

    def axmemb(self, seg, contiguous=False, admembOpt=False):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        AXMEMB defined here is a generic form and functions as ACMEMB(X,A\_,
        B\_) (contiguous=False) and ADMEMB(X,A\_,B\_) (contiguous=True).

        This contour similarity measurement method works with segclasses of
        both equal or unequal cardinalities--the input seg may or may not be
        the same size as the current segclass.

        The input seg does not have to be preprocessed to be in normal form
        nor prime form--the method computes the similarity with its segclass
        members accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> a = Segclass([2, 1, 0, 3])
        >>> b = Segclass([2, 0, 3, 1])
        >>> c = Segclass([3, 5, 2, 0, 6, 4, 1, 7])
        >>> a.axmemb(c, contiguous=True, admembOpt=True) # ADMEMB(A_,C_)
        0.5588235294117647
        >>> b.axmemb(c, contiguous=True, admembOpt=True) # ADMEMB(B_,C_)
        0.4411764705882353
        >>> a.axmemb(b, contiguous=True, admembOpt=True) # ADMEMB(A_,B_)
        0.6666666666666666

        :param seg: contour segment to measure the similarity with.
        :param contiguous: the bool selects ACMEMB (False) or ADMEMB (True) to
            invoke.
        :param admembOpt: the bool indicates ADMEMB optimization on (True) /
            off (False).
        :type seg: segment
        :type contiguous: bool
        :type admembOpt: bool
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return axmemb(self._segclass, seg, contiguous=contiguous,
                      segclass=True, admembOpt=admembOpt)


class Segment(MutableSequence):
    """Generic class for contour segment."""

    # Basic methods -----------------------------------------------------------

    def __init__(self, seg):
        """
        Constructor method.

        >>> Segment([0, 2, 3, 1])

        :param seg: contour segment.
        :type seg: segment
        """
        MutableSequence.__init__(self)
        self._seg = list(seg)

    def __contains__(self, element):
        """
        Return a bool of the element membership to the current segment.

        >>> s = Segment([0, 2, 3, 1])
        >>> 2 in s
        True

        :param element: element to test the membership to the current segment.
        :type element: int
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return MutableSequence.__contains__(self, element)

    def __delitem__(self, index):
        """
        Delete the indexed element.

        >>> s = Segment([0, 2, 3, 1])
        >>> del s[2]
        >>> s
        [0, 2, 1]

        :param index: index at which the element is deleted.
        """
        del self._seg[index]

    def __getitem__(self, index):
        """
        Return the indexed element of the current segment.

        >>> Segment([0, 2, 3, 1])[3]
        1

        :param index: index to get an element.
        :type index: int
        :return: indexed element.
        :rtype: int
        """
        return self._seg[index]

    def __iadd__(self, elements):
        """
        Append the input contour elements to the current seg in-place.

        This operation is equivalent to self.extend(elements) but invoked by +=
        operator.

        >>> s = Segment([0, 2, 3, 1])
        >>> s += [4, 6, 5]
        >>> s
        Segment([0, 2, 3, 1, 4, 6, 5])

        :param elements: contour elements to append to the current seg.
        :type elements: list
        :return: mutated seg.
        :rtype: Segment object
        """
        MutableSequence.__iadd__(self, elements)
        return self

    def __iter__(self):
        """
        Return an iterator object comprising the current seg elements.

        >>> for i in Segment([0, 2, 3, 1]):
        ...     print(i, end="")
        0231

        :return: iterator with the current seg's elements.
        :rtype: iterator
        """
        return MutableSequence.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current seg.

        >>> len(Segment([0, 2, 3, 1]))
        4

        :return: cardinality of the current seg.
        :rtype: int
        """
        return len(self._seg)

    def __reversed__(self):
        """
        Return a reverse iterator of the current seg's elements.

        >>> list(reversed(Segment([0, 2, 3, 1])))
        [1, 3, 2, 0]

        :return: iterator that iterates over the current segment
            elements in reverse order.
        :rtype: iterator
        """
        return MutableSequence.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed element.

        >>> s = Segment([0, 2, 3, 1])
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

        >>> Segment([0, 2, 3, 1])
        Segment([0, 2, 3, 1])

        :return: official representation of the object.
        :rtype: str
        """
        return "Segment({})".format(self._seg)

    def append(self, element):
        """
        Append a single element to the end of the current seg.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.append(4)
        Segment([0, 2, 3, 1, 4])

        :param element: element to append.
        :type element: int
        :return: mutated seg.
        :rtype: Segment object
        """
        MutableSequence.append(self, element)
        return self

    def count(self, element):
        """
        Return the number of occurrences of the element.

        >>> Segment([0, 2, 3, 1]).count(2)
        1
        >>> Segment([0, 2, 3, 1]).count(4)
        0

        :param element: element to check the occurrence frequency in the
            current segment.
        :type element: int
        :return: the number of occurrences of the element.
        :rtype: int
        """
        return MutableSequence.count(self, element)

    def extend(self, elements):
        """
        Extend the current seg by appending the input contour elements.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.extend([4, 6, 5])
        Segment([0, 2, 3, 1, 4, 6, 5])

        :param elements: contour elements to append to the current seg.
        :type elements: segment
        :return: mutated seg.
        :rtype: Segment object
        """
        MutableSequence.extend(self, elements)
        return self

    def index(self, element, start=0, stop=None):
        """
        Return the first index of the element.

        Raise ValueError if the element is not present.

        >>> Segment([0, 2, 3, 1]).index(3)
        2
        >>> Segment([0, 2, 3, 1]).index(4)
        ValueError

        :param element: segment element to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type element: int
        :type start: int
        :type stop: int
        :return: first index of the segment element.
        :rtype: int
        """
        if stop is None:
            stop = len(self._seg)
        return MutableSequence.index(self, element, start, stop)

    def insert(self, index, element):
        """
        Insert the element at the specified index of the seg.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.insert(3, 2)
        Segment([0, 2, 3, 2, 1])

        :param index: index at which the element is inserted.
        :param element: element to insert.
        :type index: int
        :type element: int
        :return: mutated seg.
        :rtype: Segment object
        """
        self._seg.insert(index, element)
        return self

    def pop(self, index=-1):
        """
        Remove and return an element at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Segment([0, 2, 3, 1])
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
        return MutableSequence.pop(self, index=index)

    def remove(self, value):
        """
        Remove the first occurrence of an element with the input value.

        Raise ValueError if the value is not present.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.remove(3)
        Segment([0, 2, 1])

        :param value: value with which an element is removed.
        :type value: int
        :return: mutated seg.
        :rtype: Segment object
        """
        MutableSequence.remove(self, value)
        return self

    def reverse(self):
        """
        Reverse the current seg in place.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.reverse()
        Segment([1, 3, 2, 0])

        :return: mutated seg.
        :rtype: Segment object
        """
        MutableSequence.reverse(self)
        return self

    def copy(self):
        """
        Return a deep copy of the current state of the object.

        >>> a = Segment([1, 5, 3, 2])
        >>> b = a.copy().normalize()
        >>> print(a, b)
        [1, 5, 3, 2] [0, 3, 2, 1]
        """
        return Segment(self._seg)

    # Property methods --------------------------------------------------------

    @property
    def seg(self):
        """
        Return the current seg.

        >>> s = Segment([3, 1, 0, 2])
        >>> s.seg
        [0, 2, 3, 1]

        :return: current seg.
        :rtype: list
        """
        return self._seg

    @seg.setter
    def seg(self, s):
        """
        Set the current seg to the input seg.

        >>> a = Segment([3, 1, 0, 2])
        >>> a.seg = [1, 3, 0, 2]
        >>> a.seg
        [1, 3, 0, 2]

        :param s: contour segment.
        :type s: segment
        """
        self._seg = list(s)

    # Mutator methods ---------------------------------------------------------

    def normalize(self):
        """
        Normalize the current seg.

        See ``contour.normalForm()`` for more detail.

        >>> Segment([1, 5, 3, 2]).normalize()
        Segment([0, 3, 2, 1])

        :return: normal form of the current seg.
        :rtype: Segment object
        """
        self._seg = normalForm(self._seg)
        return self

    def invert(self):
        """
        Invert the current seg.

        >>> Segment([0, 2, 3, 1]).invert()
        Segment([3, 1, 0, 2])

        :return: inversion of the current seg.
        :rtype: Segment object
        """
        self._seg = inversion(self._seg)
        return self

    def retrograde(self):
        """
        Retrograde the current seg.

        >>> Segment([0, 2, 3, 1]).retrograde()
        Segment([1, 3, 2, 0])

        :return: retrograde of the current seg.
        :rtype: Segment object
        """
        self._seg = retrograde(self._seg)
        return self

    def rotate(self, n, mode=0):
        """
        Cyclically permute the elements of the current seg.

        >>> s = Segment([0, 2, 3, 1])
        >>> s.copy().rotate(1, mode=0))
        Segment([2, 3, 1, 0])
        >>> s.copy().rotate(1, mode=1))
        Segment([1, 3, 0, 2])

        :param n: rotation index: the number of positions the seg elements are
            rotated. The index is calculated as n % cardinality, so n may be
            arbitrary int.
        :param mode: rotation mode: temporal order rotation(0), registral order
            rotation (1).
        :type n: int
        :type mode: int
        :return: rotation of the current seg
        :rtype: Segment object
        """
        self._seg = rotation(self._seg, n=n, mode=mode)
        return self

    def opI(self):
        """Shorthand for invert()."""
        return self.invert()

    def opR(self):
        """Shorthand for retrograde()."""
        return self.retrograde()

    def opRI(self):
        """Return the retrograde inversion of the current seg."""
        self._seg = opRI(self._seg)
        return self

    # Analysis methods --------------------------------------------------------

    def normalForm(self, nparr=False):
        """
        Return the normal form of the current seg.

        See ``contour.normalForm()`` for more detail.

        >>> Segment([-12, 8, 0, -2]).normalForm()
        [0, 3, 2, 1]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or a ndarray (nparr=True) of the
            current seg.
        :rtype: list or ndarray
        """
        return normalForm(self._seg, nparr=nparr)

    def primeForm(self, nparr=False):
        """
        Return the prime form of the current seg.

        >>> Segment([3, 1, 2, 0]).primeForm()
        [0, 2, 1, 3]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or ndarray (nparr=True) of the prime
            form of the current seg.
        :rtype: list or ndarray
        """
        return primeForm(self._seg, nparr=nparr)

    def isNormalForm(self):
        """
        Return a bool that indicates whether the current seg is normalized.

        >>> Segment([0, 1, 4, 2]).isNormalForm()  # NF = [0, 1, 3, 2]
        False

        :return: True if seg is normalized, False otherwise.
        :rtype: bool
        """
        return isNormalForm(self._seg)

    def isPrimeForm(self):
        """
        Return a bool that indicates whether the current seg is the prime form.

        >>> Segment([1, 3, 2, 0]).isPrimeForm()  # PF = [0, 2, 3, 1]
        False

        :return: True if seg is the prime form, False otherwise.
        :rtype: bool
        """
        return isPrimeForm(self._seg)

    def comMatrix(self, nparr=False):
        """
        Return the COM-matrix of the current seg.

        >>> Segment([0, 2, 3, 1]).comMatrix(nparr=True)
        [[ 0  1  1  1]
         [-1  0  1 -1]
         [-1 -1  0 -1]
         [-1  1  1  0]]

        :param nparr: selector of the output data type.
        :type nparr: bool
        :return: a nested list (nparr=False) or 2D ndarray (nparr=True) of the
            COM-matrix of the current seg.
        :rtype: list or ndarray
        """
        return comMatrix(self._seg, nparr=nparr)

    def segclassRelation(self):
        """
        Return the relation status of the current seg to its segclass.

        See ``contour.segclassRelation`` for more detail.

        >>> Segment([4, 1, 3, 2]).segclassRelation()  # Unnormalized
        -1
        >>> Segment([0, 1, 3, 2]).segclassRelation()  # P (identity)
        0
        >>> Segment([3, 2, 0, 1]).segclassRelation()  # I
        1
        >>> Segment([2, 3, 1, 0]).segclassRelation()  # R
        2
        >>> Segment([1, 0, 2, 3]).segclassRelation()  # RI
        3
        >>> Segment([0, 2, 1, 3]).segclassRelation() # Both P and RI related
        4
        >>> Segment([3, 1, 2, 0]).segclassRelation() # Both I and R related
        5

        :return: the segclass member relation status:

            * unnormalized (-1)
            * identity (0)
            * inversion (1)
            * retrograde (2)
            * retrograde-inversion (3)
            * both identity and retrograde-inversion (4)
            * both inversion and retrograde (5).

        :rtype: int
        """
        return segclassRelation(self._seg)

    def subsegs(self, normalize=False, contiguous=False):
        """
        Return the subsegments of the current seg.

        The cardinalities of the subsegs are 2 to the cardinality of the
        current seg. Therefore, the returned group of subsegments includes
        the current seg itself.

        >>> a = Segment([0, 6, 1, -12]).subsegs(normalize=True)
        >>> b = Segment([1, 3, 2, 0]).subsegs(normalize=True)
        >>> a == b
        True
        >>> a
        {2: [(0, 1), (0, 1), (1, 0), (1, 0), (1, 0), (1, 0)],
         3: [(0, 2, 1), (1, 2, 0), (1, 2, 0), (2, 1, 0)],
         4: [(1, 3, 2, 0)]}

        :param normalize: the output subsegs are normalized when True,
            otherwise as is.
        :param contiguous: the output subsegs include only contiguous ones when
            True, otherwise all the subsegs are returned.
        :type normalize: bool
        :type contiguous: bool
        :return: the dict of the subsegs which are sorted by the cardinalities
            for its keys.
        :rtype: dict
        """
        return subsegs(self._seg, normalize=normalize, contiguous=contiguous)

    def segs(self, func=2, sim=1.0, card=None, fixed=None):
        """
        Return the segs within the similarity range.

        The output list of segs is in the order of similarity value from
        high to low.

        Optional filtering criteria may be given for filtering the segs (the
        cardinality of and fixed elements in the seg).

        >>> a = Segment([0, 2, 3, 1])
        >>> a.segs(func=0, sim=0.6, fixed={"1": 3})  # CSIM
        [((0, 3, 2, 1), 0.8333333333333334),
         ((0, 3, 1, 2), 0.6666666666666666),
         ((1, 3, 2, 0), 0.6666666666666666)]
        >>> a.segs(func=1, sim=0.8)  # DSIM
        [((0, 1, 3, 2), 0.8333333333333334),
         ((0, 3, 2, 1), 0.8333333333333334),
         ...
         ((0, 2, 2, 1), 0.8333333333333334)]
        >>> a.segs(func=2, sim=0.7)  # ACMEMB
        [((0, 1, 3, 2), 0.8636363636363636),
         ((0, 2, 1, 3), 0.8181818181818182),
         ...
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.segs(func=2, sim=0.7, fixed={"0": 0, "2": 1})
        [((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 2, 1), 0.8),
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.segs(func=2, sim=0.7, card=4, fixed={"0": 0, "2": 1})
        [((0, 2, 1, 3), 0.8181818181818182),
         ((0, 3, 1, 2), 0.8181818181818182),
         ((0, 2, 1, 2), 0.7272727272727273)]
        >>> a.segs(func=3, sim=0.6, fixed={"2": 1})  # ADMEMB
        [((2, 0, 1, 3), 0.6666666666666666),
         ((2, 3, 1, 0), 0.6666666666666666),
         ...
         ((2, 0, 1, 2), 0.6666666666666666)]
        >>> a.segs(func=4, sim=0.6, fixed={"3": 1})  # CAS
        [((0, 1, 2, 1), 1.0),
         ((0, 3, 2, 1), 0.6666666666666666),
         ...
         ((2, 0, 2, 1), 0.6666666666666666)]
        >>> a.segs(func=5, sim=0.6, fixed={"2": 3})  # CASV
        [((0, 1, 3, 2), 1.0),
         ((1, 2, 3, 0), 1.0),
         ...
         ((2, 1, 3, 0), 0.6666666666666666)]
        >>> a.segs(func=6, sim=0.8, fixed={"2": 3})  # CCV1
        [((1, 0, 3, 2), 0.9),
         ((0, 1, 3, 2), 0.8),
         ((2, 0, 3, 1), 0.8)]
        >>> a.segs(func=7, sim=0.8, fixed={"1": 2})  # CCV2
        [((1, 2, 0, 3), 1.0),
         ((0, 2, 0, 1), 0.9166666666666666),
         ...
         ((1, 2, 3, 0), 0.8333333333333334)]

        :param func: the function to measure the similarity:

            * CSIM (0)
            * DSIM (1)
            * ACMEMB (2)
            * ADMEMB (3)
            * CAS (4)
            * CASV (5)
            * CCV1 (6)
            * CCV2 (7)

        :param sim: similarity threshold [0, 1]. Measured with the current
            seg, those segs which have a similarity value the same or higher
            than the sim value will be output.
        :param card: when card value is given, the output segs are of the
            specified cardinality.
        :param fixed: dict keys are the element positions to fix, and values
            are the elements' values.
        :type func: int
        :type sim: float
        :type card: int
        :type fixed: dict
        :return: tuples of seg and similarity value.
        :rtype: list
        """
        m = ["CSIM", "DSIM", "ACMEMB", "ADMEMB", "CAS", "CASV", "CCV1",
             "CCV2"][func]
        nf = tuple(normalForm(self._seg))
        dct = catalog["similaritySeg"][nf][m]
        # Collect candidate segments by the similarity value.
        candidates = []
        for i in dct.items():
            if i[1] >= sim:
                candidates.append(i)
            else:
                break  # Short-circuit evaluation
        # Filter the candidates by the cardinality.
        if card is not None:
            candidates = [c for c in candidates if len(c[0]) == card]
        # Filter the candidates by the fixed elements.
        segs = []
        if fixed is not None:
            for c in candidates:
                # Candidate is validated if it satisfies all the fixed elements
                try:
                    if all([c[0][int(pos)] == val
                            for pos, val in fixed.items()]):
                        segs.append(c)
                except IndexError:
                    continue
        else:
            segs = candidates
        return segs

    # Relation methods --------------------------------------------------------

    def xsim(self, seg):
        """
        Return a value of contour similarity function (Marvin 1988).

        The similarity is measured between the current and the input segs.

        The input seg must have the same cardinality as the current seg,
        however, does not have to be preprocessed to be in normal form--the
        method computes the similarity with its normal form accordingly.

        See the description of ``contour.xsim()`` for more detail.

        >>> a = Segment([2, 0, 1, 3])
        >>> b = [0, 1, 2, 3]
        >>> c = [1, 3, 0, 2]
        >>> d = [0, 2, 3, 1]
        >>> a.xsim(b)  # CSIM(A,B)
        0.6666666666666666
        >>> a.xsim(c)  # CSIM(A,C)
        0.5
        >>> a.xsim(d)  # CSIM(A,D)
        0.3333333333333333

        :param seg: contour segment to measure the similarity with.
        :type seg: segment
        :return: similarity value [0, 1].
        :rtype: float
        """
        return xsim(self._seg, seg)

    def xemb(self, seg, contiguous=False):
        """
        Return a value of contour-embedding function (Marvin 1988).

        The input seg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        XEMB defined here is a generic form and functions as CEMB(A,
        B) (contiguous=False) and DEMB(A,B) (contiguous=True). The maximum
        similarity value is 1, and minimum 0.

        .. note::
            This contour similarity measurement method only works with
            segments of differing cardinalities--the input seg must be
            larger than the current seg.

        See the description of ``contour.xemb()`` for more detail.

        >>> a = [0, 1, 2]
        >>> b = [0, 2, 1, 3, 4]
        >>> Segment(a).xemb(b)  # CEMB(A,B)
        0.7
        >>> c = [2, 1, 0, 3]
        >>> d = [3, 5, 2, 0, 6, 4, 1, 7]
        >>> Segment(c).xemb(d, contiguous=True)  # DEMB(C,D)
        0.4

        :param seg: contour segment to measure the similarity with.
        :param contiguous: the bool selects CEMB (False) or DEMB (True) to
            invoke.
        :type seg: segment
        :type contiguous: bool
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return xemb(self._seg, seg, contiguous=contiguous)

    def axmemb(self, seg, contiguous=False, admembOpt=False):
        """
        Return a value of all-mutually-embedded-contour function (Marvin 1988).

        AXMEMB defined here is a generic form and functions as ACMEMB(X,A,
        B) (contiguous=False) and ADMEMB(X,A,B) (contiguous=True).

        This contour similarity measurement method works with segments of
        both equal or unequal cardinalities--the input seg may or may not be
        the same size as the current seg.

        The input seg does not have to be preprocessed to be in normal
        form--the method computes the similarity with its normal form
        accordingly.

        See the description of ``contour.axemb()`` for more detail.

        >>> # ACMEMB(A,B)
        >>> a = [0, 1, 2, 3]
        >>> b = [0, 2, 1, 3, 4]
        >>> Segment(a).axmemb(b)
        0.7837837837837838
        >>> # ADMEMB(C,D) with optimization on
        >>> c = [2, 1, 0, 3]
        >>> d = [3, 5, 2, 0, 6, 4, 1, 7]
        >>> Segment(c).axmemb(d, contiguous=True, admembOpt=True)
        0.5588235294117647

        :param seg: contour segment to measure the similarity with.
        :param contiguous: the bool selects ACMEMB (False) or ADMEMB (True) to
            invoke.
        :param admembOpt: the bool indicates ADMEMB optimization on (True) /
            off (False).
        :type seg: segment
        :type contiguous: bool
        :type admembOpt: bool
        :return: the contour similarity value [0, 1].
        :rtype: float
        """
        return axmemb(self._seg, seg, contiguous=contiguous,
                      admembOpt=admembOpt)


# Analysis functions ----------------------------------------------------------

def isNormalForm(seg):
    """
    Return a bool that indicates whether the input seg is normalized.

    >>> isNormalForm([0, 1, 4, 2])  # NF = [0, 1, 3, 2]
    False

    :param seg: contour segment.
    :type seg: segment
    :return: True if seg is normalized, False otherwise.
    :rtype: bool
    """
    n = len(seg)
    r = countRepeatedElements(seg)
    return set(seg) == set(range(n - r))


def isPrimeForm(seg):
    """
    Return a bool that indicates whether the input seg is the prime form.

    >>> isPrimeForm([1, 3, 2, 0])  # PF = [0, 2, 3, 1]
    False

    :param seg: contour segment.
    :type seg: segment
    :return: True if seg is the prime form, False otherwise.
    :rtype: bool
    """
    return list(seg) == primeForm(seg)


def normalForm(seg, nparr=False):
    """
    Return the normal form of the input segment.

    This function is equivalent to Marvin's translation function (Marvin
    and Laprade 1987).

    When a seg includes repeated elements, the elements of the normalized
    seg are renumbered with integers in range of [0, (n-1-r)] where n is
    the cardinality and r is the number of repeated elements. This function
    can be applied to segments with negative elements, thus any pseg can be
    converted to a normalized cseg (e.g., pseg [-12,8,0,-2] normalized to
    cseg [0,3,2,1]).

    >>> normalForm([-12, 8, 0, -2]))
    [0, 3, 2, 1]
    >>> normalForm([1, 4, 3, 4, 7], nparr=True)
    [0 2 1 2 3]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: a list (nparr=False) or a ndarray (nparr=True) of the
        normalized segment.
    :rtype: list or ndarray
    """
    u, indices = np.unique(np.array(seg), return_inverse=True)
    ranks = np.arange(len(u))
    n = ranks[indices]
    return adaptOutput(n, nparr)


def primeForm(seg, nparr=False):
    """
    Return the prime form of the input segment.

    The function uses Marvin's prime form algorithm (Marvin and Laprade 1987).

    >>> primeForm([0, 3, 1, 2])
    [0, 3, 1, 2]
    >>> primeForm([3, 0, 2, 1])
    [0, 3, 1, 2]
    >>> primeForm([1, 2, 0, 4])
    [0, 3, 1, 2]
    >>> primeForm([3, 2, 4, 1])
    [0, 3, 1, 2]
    >>> x = [3, 2, 5, 1, 3]
    >>> px = primeForm(x)
    >>> ix = inversion(x)   # Same as opI(x)
    >>> rx = retrograde(x)  # Same as opR(x)
    >>> rix = retrograde(inversion(x))  # Same as opRI(x)
    >>> px
    [1, 2, 0, 3, 1]
    >>> primeForm(ix)
    [1, 2, 0, 3, 1]
    >>> primeForm(rx)
    [1, 2, 0, 3, 1]
    >>> primeForm(rix)
    [1, 2, 0, 3, 1]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: a list (nparr=False) or ndarray (nparr=True) of the prime form
        segment.
    :rtype: list or ndarray
    """
    s = list(seg)
    card = len(s)
    r = countRepeatedElements(s)
    # Normalize set if it is not normalized.
    if not isNormalForm(s):
        s = normalForm(s)
    # Invert if n-1-r minus last element < first element.
    #   If they are the same value, compare the second and the second-to-last
    #   elements, and so on until the "tie" is broken.
    for i in range(card):
        x = (card - 1 - r) - s[-i-1]
        y = s[i]
        if x == y:
            continue
        elif x < y:
            s = inversion(s)
            break
        else:
            break
    # Retrograde if last element < first element
    #   If they are the same value, compare the second and the second-to-last
    #   elements, and so on until the "tie" is broken.
    for i in range(card):
        x = s[-i-1]
        y = s[i]
        if x == y:
            continue
        elif x < y:
            s = retrograde(s)
            break
        else:
            break
    return adaptOutput(s, nparr)


def comMatrix(seg, nparr=False):
    """
    Return the COM-matrix of the input segment.

    >>> s1 = [0, 3, 1, 2, 4]
    >>> s2 = [0, 2, 1, 0, 2]
    >>> comMatrix(s1, nparr=True))
    [[ 0  1  1  1  1]
     [-1  0 -1 -1  1]
     [-1  1  0  1  1]
     [-1  1 -1  0  1]
     [-1 -1 -1 -1  0]]
    >>> comMatrix(s2, nparr=True)
    [[ 0  1  1  0  1]
     [-1  0 -1 -1  0]
     [-1  1  0 -1  1]
     [ 0  1  1  0  1]
     [-1  0 -1 -1  0]]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: a nested list (nparr=False) or 2D ndarray (nparr=True) of the
        COM-matrix.
    :rtype: list or ndarray
    """
    card = len(seg)
    matrix = np.zeros([card, card], dtype=np.int64)
    row = 0
    for i in seg:
        col = 0
        for j in seg:
            val = j - i
            if val > 0:
                val = 1
            elif val < 0:
                val = -1
            else:
                val = 0
            matrix[row, col] = val
            col += 1
        row += 1
    return adaptOutput(matrix, nparr)


def int_comMatrix(comMatrix, n=1, nparr=False):
    """
    Return an INTn vector out of the input COM-matrix.

    INTn is any of the diagonals to the right of the main diagonal (upper
    left-hand to lower right-hand corner) of the COM-matrix, in which n
    stands for the difference between order position numbers of the two
    elements compared; that is, INT3 compares elements which are 3 positions
    apart.

    >>> m = comMatrix([0, 3, 1, 2, 4])
    >>> m
    [[ 0  1  1  1  1]
     [-1  0 -1 -1  1]
     [-1  1  0  1  1]
     [-1  1 -1  0  1]
     [-1 -1 -1 -1  0]]
    >>> int_comMatrix(m, 0)
    [0, 0, 0, 0, 0]
    >>> int_comMatrix(m, 1)
    [1, -1, 1, 1]
    >>> int_comMatrix(m, 2)
    [1, -1, 1]
    >>> int_comMatrix(m, 3)
    [1, 1]
    >>> int_comMatrix(m, 4)
    [1]

    :param comMatrix: the COM-matrix to compute INTn.
    :param n: n in INTn.
    :param nparr: selector of the output data type.
    :type: 2D list or ndarray
    :type n: int
    :type nparr: bool
    :return: a list (nparr=False) or ndarray (nparr=True) of INTn vector.
    :rtype: list or ndarray
    """
    v = np.diag(comMatrix, n)
    return adaptOutput(v, nparr)


def segclassMembers(seg, nparr=False):
    """
    Return the segment class members (P, I, R, and RI) of the input segment.

    The input seg is assumed to be in the prime form (if not it is converted
    to the prime form in the function process anyway).

    >>> segclassMembers([2, 0, 1, 3]))
    {'I': [3, 1, 0, 2],
     'P': [0, 2, 3, 1],
     'R': [1, 3, 2, 0],
     'RI': [2, 0, 1, 3]}
    >>> segclassMembers([3, 2, 0, 4, 1], nparr=True)
    {'I': array([3, 2, 0, 4, 1]),
     'P': array([1, 2, 4, 0, 3]),
     'R': array([3, 0, 4, 2, 1]),
     'RI': array([1, 4, 0, 2, 3])}

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: the dict keys (P, I, R, and RI) are assigned with their
        corresponding segment as the values. The values are list
        (nparr=False) or numpy array (nparr=True) of normalized seg.
    :rtype: dict
    """
    p = primeForm(seg, nparr)
    i = opI(p, nparr)
    r = opR(p, nparr)
    ri = opRI(p, nparr)
    return dict((("P", p), ("I", i), ("R", r), ("RI", ri)))


def segclassRelation(seg):
    """
    Return the relation status of the input seg to its segclass.

    Note that the input seg does not hold any segclass relation unless it
    is normalized. Also, segclasses whose members are invariant under the RI
    operator have two, not four members. That is, for a given seg A,
    PA == RIA and IA == RA.

    >>> segclassRelation([4, 1, 3, 2]))  # Unnormalized
    -1
    >>> segclassRelation([0, 1, 3, 2]))  # P (identity)
    0
    >>> segclassRelation([3, 2, 0, 1]))  # I
    1
    >>> segclassRelation([2, 3, 1, 0]))  # R
    2
    >>> segclassRelation([1, 0, 2, 3]))  # RI
    3
    >>> segclassRelation([0, 2, 1, 3]))  # [0,2,1,3] is both P and RI related
    4
    >>> segclassRelation([3, 1, 2, 0]))  # [3,1,2,0] is both I and R related
    5

    :param seg: contour segment.
    :type seg: segment
    :return: segclass member relation status:

        * unnormalized (-1)
        * identity (0)
        * inversion (1)
        * retrograde (2)
        * retrograde-inversion (3)
        * both identity and retrograde-inversion (4)
        * both inversion and retrograde (5).

    :rtype: int
    """
    seg = list(seg)
    if not isNormalForm(seg):
        return -1
    m = segclassMembers(seg)
    transforms = [m["P"], m["I"], m["R"], m["RI"]]
    if transforms[0] != transforms[3]:
        for i in range(4):
            if seg == transforms[i]:
                return i
    else:
        if seg == transforms[0]:
            return 4
        else:
            return 5


def subsegs(seg, normalize=False, contiguous=False):
    """
    Return the subsegments of the input seg.

    The cardinalities of the subsegs are 2 up to the cardinality of the seg.
    Therefore, the returned group of subsegments includes the seg itself.

    >>> a = [1, 0, 4, 3, 2]
    >>> b = [2, 0, 1, 4, 3]
    >>> subsegs(a)
    {2: [(1, 0),
         (1, 4),
         ...
         (3, 2)],
     3: [(1, 0, 4),
         (1, 0, 3),
         ...
         (4, 3, 2)],
     4: [(1, 0, 4, 3),
         (1, 0, 4, 2),
         ...
         (0, 4, 3, 2)],
     5: [(1, 0, 4, 3, 2)]}
    >>> subsegs(b, contiguous=True)
    {2: [(2, 0), (0, 1), (1, 4), (4, 3)],
     3: [(2, 0, 1), (0, 1, 4), (1, 4, 3)],
     4: [(2, 0, 1, 4), (0, 1, 4, 3)],
     5: [(2, 0, 1, 4, 3)]}
    >>> subsegs(a, normalize=True)[2]
    [(1, 0), (0, 1), ... (1, 0)]

    :param seg: contour segment.
    :param normalize: the output subsegs are normalized when True,
        otherwise as is.
    :param contiguous: the output subsegs include only contiguous ones when
        True, otherwise all the subsegs are returned.
    :type seg: segment
    :type normalize: bool
    :type contiguous: bool
    :return: the dict of the subsegs which are sorted by the cardinalities
        for their keys.
    :rtype: dict
    """
    card = len(seg)
    subsegs_ = []
    if card <= 2:
        return
    if contiguous:
        for i in range(2, card+1):     # i is cardinality of subseg.
            col = []
            for j in range(card-i+1):  # j is the onset index.
                s = seg[j:j+i]
                if normalize:
                    s = normalForm(s)
                col.append(tuple(s))
            subsegs_.append((i, col))
        return dict(subsegs_)
    else:
        for i in range(2, card+1):
            col = combinations(seg, i)
            if normalize:
                col = [tuple(normalForm(x)) for x in col]
            subsegs_.append((i, list(col)))
        return dict(subsegs_)


# Transformation functions ----------------------------------------------------

def inversion(seg, nparr=False):
    """
    Return an inversion of the input seg.

    The input seg is assumed to be in a normal form. For example,
    unnormalized seg like [5,2,4,1] will have negative elements when
    inverted as [-2,1,-1,2]. This is not an error--normalize the input seg
    before input as [3,1,2,0] to invert to [0,2,1,3].

    >>> inversion([0, 3, 2, 1]))
    [3, 0, 1, 2]
    >>> inversion(np.array([1, 3, 4, 0, 2, 4]), nparr=True)
    [3 1 0 4 2 0]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: a list (nparr=False) or a ndarray (nparr=True) of the inversion
        of the seg.
    :rtype: list or ndarray
    """
    n = len(seg)
    r = countRepeatedElements(seg)
    s = [(n - 1 - r) - seg[i] for i in range(n)]
    return adaptOutput(s, nparr)


def retrograde(seg, nparr=False):
    """
    Return a retrograde of the input seg.

    >>> retrograde([0, 3, 2, 1]))
    [1, 2, 3, 0]
    >>> retrograde(np.array([1, 3, 4, 0, 2, 4]), nparr=True))
    [4 2 0 4 3 1]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :type seg: segment
    :type nparr: bool
    :return: a list (nparr=False) or a ndarray (nparr=True) of the
        retrograde of the seg.
    :rtype: list or ndarray
    """
    return adaptOutput(list(reversed(seg)), nparr)


def opI(seg, nparr=False):
    """Shorthand for inversion(seg, nparr=False)"""
    return inversion(seg, nparr)


def opR(seg, nparr=False):
    """Shorthand for retrograde(seg, nparr=False)"""
    return retrograde(seg, nparr)


def opRI(seg, nparr=False):
    """Shorthand for retrograde(inversion(seg), nparr)"""
    return retrograde(inversion(seg), nparr)


def rotation(seg, n, mode=0, nparr=False):
    """
    Return a rotation of the input seg.

    >>> a = [0, 2, 1, 3]
    >>> # Temporal Order Rotation:
    >>> rotation(a, 1, mode=0))
    [2, 1, 3, 0]
    >>> rotation(a, 2, mode=0))
    [1, 3, 0, 2]
    >>> rotation(a, 3, mode=0))
    [3, 0, 2, 1]
    >>> rotation(a, -1, mode=0))
    [3, 0, 2, 1]
    >>> # Registral Order Rotation:
    >>> rotation(a, 1, mode=1))
    [1, 3, 2, 0]
    >>> rotation(a, 2, mode=1))
    [2, 0, 3, 1]
    >>> rotation(a, 3, mode=1))
    [3, 1, 0, 2]
    >>> rotation(a, 6, mode=1))
    [2, 0, 3, 1]

    :param seg: contour segment.
    :param nparr: selector of the output data type.
    :param n: rotation index: the number of positions the seg elements are
        rotated. The index is calculated as n % cardinality, so n may be
        arbitrary int.
    :param mode: rotation mode: temporal order rotation(0), registral order
        rotation (1).
    :type seg: segment
    :type nparr: bool
    :type n: int
    :type mode: int
    :return: a list (nparr=False) or a ndarray (nparr=True) of the rotation
        of the seg.
    :rtype: list or ndarray
    """
    s = list(seg)
    n = n % len(seg)
    # Temporal order rotation
    if mode == 0:
        s = s[n:] + s[:n]
    # Registral order rotation
    elif mode == 1:
        s = [(i + n) % len(s) for i in s]
    return adaptOutput(s, nparr)


# Similarity functions --------------------------------------------------------

def xsim(seg1, seg2, segclass=False):
    """
    Return a value of contour similarity function (Marvin 1988).

    XSIM defined here is a generic form and functions as CSIM and DSIM. It
    works with a pair of segments of the same cardinality. The maximum
    similarity value is 1.0, and minimum 0.0.

    Example for CSIM (Marvin 1988, 83):

    >>> a = [2, 0, 1, 3]
    >>> b = [0, 1, 2, 3]
    >>> c = [1, 3, 0, 2]
    >>> d = [0, 2, 3, 1]
    >>> xsim(a, b)  # CSIM(A,B)
    0.6666666666666666
    >>> xsim(a, c)  # CSIM(A,C)
    0.5
    >>> xsim(a, d)  # CSIM(A,D)
    0.3333333333333333

    Example for CSIM (csegclass comparison) (Marvin 1988, 87):

    >>> a = [0, 2, 3, 1]
    >>> b = [3, 1, 0, 2]
    >>> c = [1, 0, 4, 3, 2]
    >>> d = [1, 2, 4, 0, 3]
    >>> xsim(a, b, segclass=True)  # CSIM(A_,B_) = 1.00
    1.0
    >>> xsim(c, d, segclass=True)  # CSIM(C_,D_) = 0.80
    0.8

    Example for DSIM (Marvin 1988, 169):

    >>> a = [2, 1, 0, 3, 5, 4]
    >>> b = [5, 0, 2, 3, 4, 1]
    >>> xsim(a, b)  # DSIM(A,B) = 0.60
    0.6

    :param seg1: contour segment.
    :param seg2: contour segment.
    :param segclass: when True, the function measures similarity by
        comparing the COM-matrix of seg1 and those of every segclass members
        (P, I, R, and RI) of seg2 and then returns the highest value; when
        False, the measurement is only between seg1 and seg2.
    :type seg1: segment
    :type seg2: segment
    :type segclass: bool
    :return: contour similarity value [0, 1].
    :rtype: float
    """
    # Pretest--the segs to compare must have the same cardinality.
    if len(seg1) != len(seg2):
        return
    m1 = comMatrix(seg1)
    # Non-segclass comparison
    if not segclass:
        count, total = _compareCells(m1, comMatrix(seg2))
        return count / total
    # Segclass comparison
    else:
        values = []
        for member in segclassMembers(seg2).values():
            count, total = _compareCells(m1, comMatrix(member))
            values.append(count / total)
        return max(values)


def xemb(seg1, seg2, contiguous=False, segclass=False):
    """
    Return a value of contour-embedding function (Marvin 1988).

    XEMB defined here is a generic form and functions as CEMB(A,
    B) (contiguous=False) and DEMB(A,B) (contiguous=True). The maximum
    similarity value is 1, and minimum 0.

    .. note::
        This contour similarity measurement function only works with
        segments of differing cardinalities--the formal parameter seg1 must be
        smaller than seg2.

    Example for CEMB (Marvin 1988, 91):

    >>> a = [0, 1, 2]
    >>> b = [0, 2, 1, 3, 4]
    >>> c = [3, 1, 4, 2, 0]
    >>> xemb(a, b))  # CEMB(A,B)
    0.7

    Example for CEMB (csegclass comparison):

    >>> xemb(a, c, segclass=True)  # CEMB(A_,C_)
    0.3

    :param seg1: contour segment.
    :param seg2: contour segment.
    :param contiguous: the bool selects CEMB (False) or DEMB (True) to invoke.
    :param segclass: when True, the function measures similarity between
        seg1 and every segclass members (P, I, R, and RI) of seg2 and then
        returns the highest value; when False, the measurement is just
        between seg1 and seg2.
    :type seg1: segment
    :type seg2: segment
    :type contiguous: bool
    :type segclass: bool
    :return: the contour similarity value [0, 1].
    :rtype: float
    """
    # Pretest: seg1 must smaller than seg2
    card1, card2 = len(seg1), len(seg2)
    if card1 >= card2:
        return
    nf = tuple(normalForm(seg1))
    # Non-segclass comparison
    if not segclass:
        # Tally card1-sized embedded contours of seg2 in the normal form.
        s = subsegs(seg2, normalize=True, contiguous=contiguous)
        tally = Counter(s[card1])
        return tally[nf] / _countSubsegs(card1, card2, contiguous)
    # Segclass comparison
    else:
        values = []
        for member in segclassMembers(seg2).values():
            s = subsegs(member, normalize=True, contiguous=contiguous)
            tally = Counter(s[card1])
            values.append(tally[nf] / _countSubsegs(card1, card2, contiguous))
        return max(values)


def xmemb(n, seg1, seg2, contiguous=False, segclass=False):
    """
    Return a value of mutually-embedded-contour function (Marvin, 1988).

    XMEMB defined here is a generic form and functions as CMEMBn(X,A,
    B) (contiguous=False) or DMEMBn(X,A,B) (contiguous=True).

    The total number of mutually embedded segments of cardinality n is
    divided by the number of n-cardinality subsegments possible in order to
    return a decimal number approaching 1 as segments A and B are more
    similar. The maximum similarity value is 1, and minimum 0.

    This contour similarity measurement function works with segments of
    both equal or unequal cardinalities--the formal parameter seg1 and seg2
    may or may not be the same size.

    Example for CMEMB (Marvin 1988, 94):

    >>> a = [1, 0, 4, 3, 2]
    >>> b = [2, 0, 1, 4, 3]
    >>> xmemb(4, a, b)  # CMEMB4(A,B)
    0.5
    >>> xmemb(3, a, b)  # CMEMB3(A,B)
    0.8
    >>> xmemb(2, a, b)  # CMEMB2(A,B)
    1.0

    Example for CMEMB (csegclass comparison);

    >>> xmemb(4, a, b, segclass=True)  # CMEMB4(A_,B_)
    0.5

    Example for DEMB (Marvin 1988, 171):

    >>> a = [2, 1, 0, 3]
    >>> b = [2, 0, 3, 1]
    >>> c = [3, 5, 2, 0, 6, 4, 1, 7]
    >>> xmemb(3, a, c, contiguous=True)  # DMEMB3(A,B)
    0.75
    >>> xmemb(3, b, c, contiguous=True))  # DMEMB3(B,C) = 0.63
    0.625

    Example test for DMEMB (dsegclass comparison):

    >>> xmemb(3, b, c, contiguous=True, segclass=True)  # DMEMB3(B_,C_)
    0.625

    :param n: the cardinality of mutually embedded subsegment X.
    :param seg1: contour segment.
    :param seg2: contour segment.
    :param contiguous: the bool selects CMEMB (False) or DMEMB (True) to
        invoke.
    :param segclass: when True, the function measures similarity between
        seg1 and every segclass members (P, I, R, and RI) of seg2 and then
        returns the highest value; when False, the measurement is just between
        seg1 and seg2.
    :type n: int
    :type seg1: segment
    :type seg2: segment
    :type contiguous: bool
    :type segclass: bool
    :return: the contour similarity value [0, 1].
    :rtype: float
    """
    card1, card2 = len(seg1), len(seg2)
    if n > min(card1, card2):
        return
    total = _countSubsegs(n, card1, contiguous) + \
            _countSubsegs(n, card2, contiguous)
    # Non-segclass comparison
    if not segclass:
        count = _countMutualSubsegs(n, seg1, seg2, contiguous=contiguous)
        return count / total
    # Segclass comparison
    else:
        values = []
        for member in segclassMembers(seg2).values():
            count = _countMutualSubsegs(n, seg1, member, contiguous=contiguous)
            values.append(count / total)
        return max(values)


def axmemb(seg1, seg2, contiguous=False, segclass=False, admembOpt=False):
    """
    Return a value of all-mutually-embedded-contour function (Marvin 1988).

    AXMEMB defined here is a generic form and functions as ACMEMB(X,A,
    B) (contiguous=False) and ADMEMB(X,A,B) (contiguous=True).

    The total number of mutually embedded segments of cardinality 2 through
    the cardinality of the smaller segment is divided by the total number of
    possible subsegments of the compared two segments (excluding the null seg
    for each and the one-element subsegment). The maximum similarity value
    is 1, and minimum 0.

    This contour similarity measurement function works with segments of
    both equal or unequal cardinalities--the formal parameter seg1 and seg2
    may or may not be the same size.

    **ADMEMB optimization**

    This function provides two modes for ADMEMB output through the
    admembOpt parameter:

    * admembOpt=False (default)
        - Calculate denominator as in Marvin's original formulation, so that
          the denominator is the total number of possible contiguous dsubsegs
          of both A and B, "up to the cardinality of the smaller dseg."
    * admembOpt=True
        - Calculate denominator by reflecting the notion in that even though
          pairs of compared dsegs have the same number of mutually embedded
          dsubsegs, "the more different in size the compared dsegs, the less
          similar they are." Thus, the denominator is the total number of
          possible contiguous dsubsegs of both A and B "of all the
          cardinalities."

    Example for ACMEMB (Marvin 1988, 94):

    >>> a = [0, 1, 2, 3]
    >>> b = [0, 2, 1, 3]
    >>> c = [0, 2, 1, 3, 4]
    >>> axmemb(a, b)  # ACMEMB(A,B)
    0.7727272727272727
    >>> axmemb(a, c)  # ACMEMB(A,C)
    0.7837837837837838
    >>> axmemb(b, c)  # ACMEMB(B,C)
    0.8918918918918919

    Example for ACMEMB (csegclass comparison):

    >>> axmemb(a, b, segclass=True)  # ACMEMB(A_,B_)
    0.7727272727272727
    >>> axmemb(a, c, segclass=True)  # ACMEMB(A_,C_)
    0.7837837837837838
    >>> axmemb(b, c, segclass=True)  # ACMEMB(B_,C_)
    0.8918918918918919

    Example for DEMB (Marvin 1988, 171)

    >>> a = [2, 1, 0, 3]
    >>> b = [2, 0, 3, 1]
    >>> c = [3, 5, 2, 0, 6, 4, 1, 7]
    >>> axmemb(a, c, contiguous=True)  # ADMEMB(A,C)
    0.7916666666666666
    >>> axmemb(b, c, contiguous=True)  # ADMEMB(B,C)
    0.625
    >>> axmemb(a, b, contiguous=True)  # ADMEMB(A,B)
    0.6666666666666666

    Example for ADMEMB (csegclass comparison):

    >>> axmemb(a, c, segclass=True, contiguous=True)  # ADMEMB(A_,C_)
    0.7916666666666666
    >>> axmemb(b, c, segclass=True, contiguous=True)  # ADMEMB(B_,C_)
    0.625
    >>> axmemb(a, b, segclass=True, contiguous=True)  # ADMEMB(A_,B_)
    0.6666666666666666

    Example for ADMEMB with an optimized denominator:

    >>> axmemb(a, c, contiguous=True, admembOpt=True))  # ADMEMB(A,C)
    0.5588235294117647
    >>> axmemb(b, c, contiguous=True, admembOpt=True))  # ADMEMB(B,C)
    0.4411764705882353
    >>> axmemb(a, b, contiguous=True, admembOpt=True))  # ADMEMB(A,B)
    0.6666666666666666

    :param seg1: contour segment.
    :param seg2: contour segment.
    :param contiguous: the bool selects ACMEMB (False) or ADMEMB (True) to
        invoke.
    :param segclass: when True, the function measures similarity between
        seg1 and every segclass members (P, I, R, and RI) of seg2 and then
        returns the highest value; when False, the measurement is just
        between seg1 and seg2.
    :param admembOpt: the bool indicates ADMEMB optimization on (True) / off
        (False).
    :type seg1: segment
    :type seg2: segment
    :type contiguous: bool
    :type segclass: bool
    :type admembOpt: bool
    :return: the contour similarity value [0, 1].
    :rtype: float
    """
    card1, card2 = len(seg1), len(seg2)
    smallerCard, largerCard = min(card1, card2), max(card1, card2)

    # Pretest
    if smallerCard < 2:
        return

    # Denominator of AXMEMB
    if not contiguous:              # ACMEMB
        total = _countTotalSubsegs(card1) + _countTotalSubsegs(card2)
    elif contiguous and admembOpt:  # ADMEMB with the optimized denom
        total = _countTotalSubsegs(smallerCard, contiguous=True) + \
                _countTotalSubsegs(largerCard, contiguous=True)
    else:                           # ADMEMB with the denom as in Marvin
        total = _countTotalSubsegs(smallerCard, contiguous=True) + \
                _countSubsegsUpTo(smallerCard, largerCard, contiguous=True)

    # Numerator of AXMEMB
    #   Count the number of subsegs mutually embedded in seg1 and seg2
    #   from cardinality 2 through the cardinality of the smaller segment.
    if not segclass:  # Non-segclass comparison
        count = 0
        for n in range(2, smallerCard + 1):
            count += _countMutualSubsegs(n, seg1, seg2, contiguous=contiguous)
        return count / total
    else:             # Segclass comparison
        values = []
        for member in segclassMembers(seg2).values():
            count = 0
            for n in range(2, smallerCard + 1):
                count += _countMutualSubsegs(n, seg1, member,
                                             contiguous=contiguous)
            values.append(count / total)
        return max(values)


# Helper (private) functions --------------------------------------------------

def _compareCells(matrix1, matrix2):
    """
    Compares cells in two square matrices at the corresponding positions.

    :param matrix1: 2D square matrix.
    :param matrix2: 2D square matrix.
    :type matrix1: list or ndarray
    :type matrix2: list or ndarray
    :return: a tuple (x, y) where x is the number of cell positions that
        have the same value, y is the total cells compared.
    :rtype: tuple
    """
    # matrix1 and 2 are assumed to be square matrices of the same shape.
    m1, m2 = np.array(matrix1), np.array(matrix2)
    count = 0
    dim = m1.shape[0]
    for row in range(dim-1):
        for col in range(row+1, dim):
            if m1[row, col] == m2[row, col]:
                count += 1
    return count, sum(range(1, dim))  # (count, total)


def _countSubsegs(m, n, contiguous=False):
    """
    Return the number of m-sized subsegments of an n-sized segment.

    :param m: the cardinality of embedded segments.
    :param n: the cardinality of covering segment.
    :param contiguous: selector to indicate the subseg is contiguous (True)
        or not (False).
    :type m: int
    :type n: int
    :type contiguous: bool
    :return: the number of m-sized subsegs.
    :rtype: int
    """
    if m > n:
        return 0
    if contiguous:
        return n - m + 1
    else:
        # n! / (m! * (n-m)!)
        return factorial(n) // (factorial(m) * factorial(n - m))


def _countSubsegsUpTo(m, n, contiguous=False):
    """
    Return the total number of subsegments of cardinality 2 through m of
    n-sized segment.

    :param m: the maximum cardinality of subsegs to count.
    :param n: the cardinality of the covering segment.
    :param contiguous: selector to indicate the subseg is contiguous (True)
        or not (False).
    :type m: int
    :type n: int
    :type contiguous: bool
    :return: the total number of subsegs of cardinality 2 through m.
    :rtype: int
    """
    if m > n:
        return
    count = 0
    for i in range(2, m+1):
        count += _countSubsegs(i, n, contiguous=contiguous)
    return count


def _countMutualSubsegs(n, seg1, seg2, contiguous=False):
    """
    Return the number of subsegments mutually embedded in seg1 and seg2.

    :param n: the cardinality of mutually embedded subsegment X.
    :param seg1: contour segment.
    :param seg2: contour segment.
    :param contiguous: selector to indicate the mutually-embedded
        subsegments are contiguous (True) or not (False).
    :type n: int
    :type seg1: segment
    :type seg2: segment
    :type contiguous: bool
    :return: the number of subsegments mutually embedded in seg1 and seg2.
    :type: int
    """
    if min(len(seg1), len(seg2)) < n:
        return 0
    s1 = subsegs(seg1, normalize=True, contiguous=contiguous)
    s2 = subsegs(seg2, normalize=True, contiguous=contiguous)
    tally1 = Counter(s1[n])
    tally2 = Counter(s2[n])
    # Mutually embedded segments (normal form) of cardinality n.
    mutual = tally1.keys() & tally2.keys()
    count = 0  # Count of mutually embedded seg in seg1 and seg2
    for s in mutual:
        count += tally1[s] + tally2[s]
    return count


def _countTotalSubsegs(n, contiguous=False):
    """
    Return the total number of subsegments possible in a seg of cardinality n.

    :param n: the segment from which subsegs are counted.
    :param contiguous: selector to indicate the subsegs are contiguous (True)
        or not (False).
    :type n: int
    :type contiguous: bool
    :return: the number of possible subsegments.
    :rtype: int
    """
    if n < 2:
        return
    if contiguous:
        return (n*n - n) // 2
    else:
        return 2**n - n - 1
