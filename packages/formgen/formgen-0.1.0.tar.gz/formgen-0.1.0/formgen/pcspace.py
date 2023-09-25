from collections.abc import MutableSequence
from .utils import int_, checkInput
from pcpy.pcset import Pcset as PcsetBaseClass

__all__ = ["Pcseg", "Pcset"]


class Pcseg(MutableSequence):
    """Pc-space segment"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, pcseg):
        """
        Constructor method.

        >>> Pcseg([6, 4, 0, 1])
        Pcseg([6, 4, 0, 1])

        :param pcseg: pitch-class segment.
        :type pcseg: segment
        """
        checkInput(pcseg, checkPc=True)
        MutableSequence.__init__(self)
        self._pcseg = list(pcseg)

    def __contains__(self, pc):
        """
        Return a bool of the element membership to the current pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> 4 in s
        True

        :param pc: pitch to test the membership to the current pcseg.
        :type pc: int
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return MutableSequence.__contains__(self, pc)

    def __delitem__(self, index):
        """
        Delete the indexed element.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> del s[1]
        >>> s
        Pseg([6, 0, 1])

        :param index: index at which the element is deleted.
        """
        del self._pcseg[index]

    def __getitem__(self, index):
        """
        Return the indexed pc of the current pcseg.

        >>> Pcseg([6, 4, 0, 1])[3]
        1

        :param index: index to get a pc.
        :type index: int
        :return: indexed pc.
        :rtype: int
        """
        return self._pcseg[index]

    def __iadd__(self, pcseg):
        """
        Append the input pcseg to the current pcseg in-place.

        This operation is equivalent to self.extend(pcseg) but invoked by +=
        operator.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s += [7, 9]
        >>> s
        Pcseg([6, 4, 0, 1, 7, 9])

        :param pcseg: pcseg to append to the current pcseg.
        :type pcseg: segment
        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        MutableSequence.__iadd__(self, pcseg)
        return self

    def __iter__(self):
        """
        Return a generator object comprising the current pcseg's elements.

        >>> for i in Pcseg([6, 4, 0, 1]):
        ...     print(i)
        6
        4
        0
        1

        :return: iterator with the current pcseg's elements.
        :rtype: iterator
        """
        return MutableSequence.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current pcseg.

        >>> len(Pcseg([6, 4, 0, 1]))
        4

        :return: cardinality of the current pcseg.
        :rtype: int
        """
        return len(self._pcseg)

    def __reversed__(self):
        """
        Return a reverse iterator of the current pcseg's elements.

        >>> list(reversed(Pcseg([6, 4, 0, 1])))
        [1, 0, 4, 6]

        :return: iterator that iterates over the current pcseg elements in
            reverse order.
        :rtype: iterator
        """
        return MutableSequence.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed element.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s[2] = 3
        >>> s
        Pcseg([6, 4, 3, 1])

        :param index: index at which the element changes the value.
        :param value: value to change the indexed element.
        :type index: int
        :type value: int
        """
        self._pcseg[index] = value

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Pcseg([6, 4, 0, 1])
        Pcseg([6, 4, 0, 1])

        :return: official representation of the object.
        :rtype: str
        """
        return "Pcseg({})".format(self._pcseg)

    def append(self, pc):
        """
        Append a single pc to the end of the current pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.append(3)
        Pcseg([6, 4, 0, 1, 3])

        :param pc: pc to append.
        :type pc: int
        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        MutableSequence.append(self, pc)
        return self

    def count(self, pc):
        """
        Return the number of occurrences of the pc.

        >>> Pcseg([6, 1, 0, 1]).count(1)
        2

        :param pc: pc to check the occurrence frequency in the
            current pcseg.
        :type pc: int
        :return: the number of occurrences of the pc.
        :rtype: int
        """
        return MutableSequence.count(self, pc)

    def extend(self, pcseg):
        """
        Extend the current pcseg by appending the input pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.extend([7, 9])
        Pcseg([6, 4, 0, 1, 7, 9])

        :param pcseg: pcseg to append to the current pcseg.
        :type pcseg: segment
        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        MutableSequence.extend(self, pcseg)
        return self

    def index(self, pc, start=0, stop=None):
        """
        Return the first index of the pc.

        Raise ValueError if the element is not present.

        >>> Pcseg([6, 4, 0, 1]).index(0)
        2
        >>> Pcseg([6, 4, 0, 1]).index(3)
        ValueError
        >>> Pcseg([6, 4, 0, 6]).index(6, 1)
        3

        :param pc: pc to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type pc: int
        :type start: int
        :type stop: int
        :return: first index of the pc.
        :rtype: int
        """
        if stop is None:
            stop = len(self._pcseg)
        return MutableSequence.index(self, pc, start, stop)

    def insert(self, index, pc):
        """
        Insert the pc at the specified index of the pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.insert(3, 3)
        Pcseg([6, 4, 0, 3, 1])

        :param index: index at which the pc is inserted.
        :param pc: element to insert.
        :type index: int
        :type pc: int
        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        self._pcseg.insert(index, pc)
        return self

    def pop(self, index=-1):
        """
        Remove and return an element at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.pop()
        1
        >>> s.pop(1)
        4
        >>> s
        [6, 0]

        :param index: index at which the element is popped.
        :type index: int
        :return: popped element.
        :rtype: int
        """
        return MutableSequence.pop(self, index=index)

    def remove(self, value):
        """
        Remove the first occurrence of a pc with the input value.

        Raise ValueError if the value is not present.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.remove(0)
        Pcseg([6, 4, 1])

        :param value: value with which a pc is removed.
        :type value: int
        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        MutableSequence.remove(self, value)
        return self

    def reverse(self):
        """
        Reverse the current pseg in place.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.reverse()
        Pcseg([1, 0, 4, 6])

        :return: mutated pcseg.
        :rtype: Pcseg object
        """
        MutableSequence.reverse(self)
        return self

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Pcseg(self._pcseg)

    # Property methods --------------------------------------------------------

    @property
    def pcseg(self):
        """
        Return the current pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.pcseg
        [6, 4, 0, 1]

        :return: current pcseg.
        :rtype: list
        """
        return self._pcseg

    @pcseg.setter
    def pcseg(self, pcseg_):
        """
        Set the current pcseg to the input pcseg.

        >>> s = Pcseg([6, 4, 0, 1])
        >>> s.pcseg = [1, 3, 7, 0]
        >>> s.pcseg
        [1, 3, 7, 0]

        :param pcseg_: pitch-class segment.
        :type pcseg_: segment
        """
        checkInput(pcseg_, checkPc=True)
        self._pcseg = list(pcseg_)

    # Mutator methods ---------------------------------------------------------

    def normalize(self):
        """

        :return:
        """
        # TODO--implement later
        pass

    def transpose(self, n):
        """

        :param n:
        :return:
        """
        # TODO--implement later
        pass

    def invert(self):
        """

        :return:
        """
        # TODO--implement later
        pass

    def invertXY(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        # TODO--implement later
        pass

    def rotate(self, n, mode=0):
        """
        mode (0) = temporal rotation
            Ex. [6, 1, 3, 0]
                n = 1, [1, 3, 0, 6]
                n = 2, [3, 0, 6, 1]
                n = 3, [0, 6, 1, 3]
                n = 4, [6, 1, 3, 0]
        mode (1) = member rotation (pc-space clockwise)
            Ex. [6, 1, 3, 0]
                n = 1, [0, 3, 6, 1]
                n = 2, [1, 6, 0, 3]
                n = 3, [3, 0, 1, 6]
                n = 4, [6, 1, 3, 0]

        :param n:
        :param mode:
        :return:
        """
        # TODO--implement later
        pass

    def opT(self, n):
        """

        :param n:
        :return:
        """
        # TODO--implement later
        pass

    def opI(self):
        """

        :return:
        """
        # TODO--implement later
        pass

    # Analysis methods --------------------------------------------------------

    def int_(self, n, mode=0, nparr=False):
        """
        Return an INTn vector.

        n indicates the difference between order position numbers of the two
        elements compared; that is, INT3 compares elements which are 3
        positions apart.

        >>> s = [0, 8, 2, 11]
        >>> Pcseg(s).int_(1, mode=0))
        [8, 6, 9]
        >>> Pcseg(s).int_(1, mode=1))
        [4, 6, 3]

        :param n: n in INTn.
        :param mode: the measured intervals are:

            * ordered pitch-class intervals (0)
            * unordered pitch-class intervals (1)

        :param nparr: selector for the output data type.
        :type n: int
        :type mode: int
        :type nparr: bool
        :return: a list (nparr=False) or ndarray (nparr=True) of INTn vector.
        :rtype: list or ndarray
        """
        return int_(self._pcseg, n, mode=[2, 3][mode], nparr=nparr)

    def ais(self):
        """
        Return the AIS of the current pcseg.

        AIS (adjacency interval series) is a series of unordered pc intervals
        (interval-classes) between adjacent pcs.

        >>> Pcseg([0, 8, 2, 11]).ais()
        [4, 6, 3]

        :return: AIS of the current pcseg.
        :rtype: list
        """
        return self.int_(1, mode=1)

    def bip(self):
        """
        Return the BIP of the current pcseg.

        BIP (basic interval pattern) is the normalized pattern of an ic
        succession. For example, if the ic succession of a pcseg is [1, 4, 1,
        1], the resulting BIP is [1, 1, 1, 4].

        >>> Pcseg([0, 11, 6, 5, 8, 9]).bip()
        [1, 1, 1, 3, 5]

        :return: BIP of the current pcseg.
        :rtype: list
        """
        return sorted(self.int_(1, mode=1))

    def normalForm(self):
        """

        :return pcseg: pcseg NOT self -- normalized Pcseg() is output
        from the mutative method, normalize().
        :rtype: list
        """
        # TODO--implement later
        pass

    def primeForm(self):
        """

        :return pcseg:
        :rtype: list
        """
        # TODO--implement later
        pass


class Pcset(PcsetBaseClass):
    """Pc-space set"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, pcs):
        """
        Constructor method.

        >>> Pcseg({6, 4, 0, 1})

        :param pcs: pcs to form a pcset.
        :type pcs: iterable
        """
        checkInput(pcs, checkPc=True)
        PcsetBaseClass.__init__(self, pcs)
