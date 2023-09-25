from collections.abc import MutableSequence
from itertools import groupby
from .utils import adaptOutput, int_
from .contour import normalForm

__all__ = ["Pseg", "psegToPcseg", "psegToPsseg"]


class Pseg(MutableSequence):
    """P-space segment"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, pseg):
        """
        Constructor method.

        The pitches are labeled according to the middle C set to 60.

        >>> Pseg([52, 60, 63, 69])  # [E3, C4, Eb4, A4]
        Pseg([52, 60, 63, 69])

        :param pseg: p-segment.
        :type pseg: segment
        """
        MutableSequence.__init__(self)
        self._pseg = list(pseg)

    def __contains__(self, p):
        """
        Return a bool of the element membership to the current pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> 63 in s
        True

        :param p: pitch to test the membership to the current pseg.
        :type p: int
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return MutableSequence.__contains__(self, p)

    def __delitem__(self, index):
        """
        Delete the indexed element.

        >>> s = Pseg([52, 60, 63, 69])
        >>> del s[1]
        >>> s
        Pseg([52, 63, 69])

        :param index: index at which the element is deleted.
        """
        del self._pseg[index]

    def __getitem__(self, index):
        """
        Return the indexed pitch of the current pseg.

        >>> Pseg([52, 60, 63, 69])[3]
        69

        :param index: index to get a pitch.
        :type index: int
        :return: indexed pitch.
        :rtype: int
        """
        return self._pseg[index]

    def __iadd__(self, pseg):
        """
        Append the input pseg to the current pseg in-place.

        This operation is equivalent to self.extend(pseg) but invoked by +=
        operator.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s += [73, 77]
        >>> s
        Pseg([52, 60, 63, 69, 73, 77])

        :param pseg: pseg to append to the current pseg.
        :type pseg: segment
        :return: mutated pseg.
        :rtype: Pseg object
        """
        MutableSequence.__iadd__(self, pseg)
        return self

    def __iter__(self):
        """
        Return a generator object comprising the current pseg's elements.

        >>> for i in Pseg([52, 60, 63, 69]):
        ...     print(i)
        52
        60
        64
        69

        :return: iterator with the current pseg's elements.
        :rtype: iterator
        """
        return MutableSequence.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current pseg.

        >>> len(Pseg([52, 60, 63, 69]))
        4

        :return: cardinality of the current pseg.
        :rtype: int
        """
        return len(self._pseg)

    def __reversed__(self):
        """
        Return a reverse iterator of the current pseg's elements.

        >>> list(reversed(Pseg([52, 60, 63, 69])))
        [69, 63, 60, 52]

        :return: iterator that iterates over the current pseg elements in
            reverse order.
        :rtype: iterator
        """
        return MutableSequence.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed element.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s[2] = 51
        >>> s
        Pseg([52, 60, 51, 69])

        :param index: index at which the element changes the value.
        :param value: value to change the indexed element.
        :type index: int
        :type value: int
        """
        self._pseg[index] = value

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Pseg([52, 60, 63, 69])
        Pseg([52, 60, 63, 69]))

        :return: official representation of the object.
        :rtype: str
        """
        return "Pseg({})".format(self._pseg)

    def append(self, p):
        """
        Append a single pitch to the end of the current pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.append(58)
        Pseg([52, 60, 63, 69, 58])

        :param p: pitch to append.
        :type p: int
        :return: mutated pseg.
        :rtype: Pseg object
        """
        MutableSequence.append(self, p)
        return self

    def count(self, p):
        """
        Return the number of occurrences of the pitch.

        >>> Pseg([52, 60, 63, 60]).count(60)
        2

        :param p: pitch to check the occurrence frequency in the
            current pseg.
        :type p: int
        :return: the number of occurrences of the pitch.
        :rtype: int
        """
        return MutableSequence.count(self, p)

    def extend(self, pseg):
        """
        Extend the current pseg by appending the input pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.extend([73, 77])
        Pseg([52, 60, 63, 69, 58])

        :param pseg: pseg to append to the current pseg.
        :type pseg: segment
        :return: mutated pseg.
        :rtype: Pseg object
        """
        MutableSequence.extend(self, pseg)
        return self

    def index(self, p, start=0, stop=None):
        """
        Return the first index of the pitch.

        Raise ValueError if the element is not present.

        >>> Pseg([52, 60, 63, 69]).index(63)
        2
        >>> Pseg([52, 60, 63, 69]).index(61)
        ValueError
        >>> Pseg([52, 60, 64, 52]).index(52, 1)
        3

        :param p: pitch to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type p: int
        :type start: int
        :type stop: int
        :return: first index of the pitch.
        :rtype: int
        """
        if stop is None:
            stop = len(self._pseg)
        return MutableSequence.index(self, p, start, stop)

    def insert(self, index, p):
        """
        Insert the pitch at the specified index of the pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.insert(3, 64)
        Pseg([52, 60, 63, 64, 69])

        :param index: index at which the pitch is inserted.
        :param p: element to insert.
        :type index: int
        :type p: int
        :return: mutated pseg.
        :rtype: Pseg object
        """
        self._pseg.insert(index, p)
        return self

    def pop(self, index=-1):
        """
        Remove and return an element at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.pop()
        69
        >>> s.pop(1)
        60
        >>> s
        [52, 63]

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

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.remove(63)
        Pseg([52, 60, 69])

        :param value: value with which an element is removed.
        :type value: int
        :return: mutated pseg.
        :rtype: Pseg object
        """
        MutableSequence.remove(self, value)
        return self

    def reverse(self):
        """
        Reverse the current pseg in place.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.reverse()
        Pseg([69, 63, 60, 52])

        :return: mutated pseg.
        :rtype: Pseg object
        """
        MutableSequence.reverse(self)
        return self

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Pseg(self._pseg)

    # Property methods --------------------------------------------------------

    @property
    def pseg(self):
        """
        Return the current pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.pseg
        [52, 60, 63, 69]

        :return: current pseg.
        :rtype: list
        """
        return self._pseg

    @pseg.setter
    def pseg(self, pseg_):
        """
        Set the current pseg to the input pseg.

        >>> s = Pseg([52, 60, 63, 69])
        >>> s.pseg = [48, 54, 57, 56]
        >>> s.pseg
        [48, 54, 57, 56]

        :param pseg_: p-segment.
        :type pseg_: segment
        """
        self._pseg = list(pseg_)

    # Mutator methods ---------------------------------------------------------

    def transpose(self, n):
        """
        Transposes the current pseg.

        >>> Pseg([52, 60, 63, 69]).transpose(-12)
        [40, 48, 51, 57]

        :param n: number of semitones to transpose the pseg.
        :type n: int
        :return: transposed pseg.
        :rtype: Pseg object
        """
        self._pseg = [p + n for p in self._pseg]
        return self

    def invert(self, center):
        """
        Inverts the current pseg.

        >>> Pseg([61, 64, 69]).invert(60)
        Pseg([62, 56, 51])

        :param center: inversional center.
        :type center: int
        :return: inversion of the current pseg.
        :rtype: Pseg object
        """
        self._pseg = [center - (p - center) for p in self._pseg]
        return self

    def retrograde(self):
        """
        Retrograde the current pseg.

        >>> Pseg([52, 60, 63, 69]).retrograde()
        Pseg([69, 63, 60, 52])

        :return: retrograde of the current pseg.
        :rtype: Pseg object
        """
        self._pseg = list(reversed(self._pseg))
        return self

    def rotate(self, n):
        """
        Cyclically permute the elements of the current pseg.

        >>> Pseg([52, 60, 63, 69]).rotate(2)
        Pseg([63, 69, 52, 60])
        >>> Pseg([52, 60, 63, 69]).rotate(-3)
        Pseg([60, 63, 69, 52])

        :param n: rotation index
        :type n: int
        :return: cyclical permutation of the current pseg.
        :rtype: Pseg object
        """
        n = n % len(self._pseg)
        # Temporal order rotation
        self._pseg = self._pseg[n:] + self._pseg[:n]
        return self

    def opT(self, n):
        """Shorthand for transpose()."""
        return self.transpose(n)

    def opI(self, center):
        """Shorthand for invert()."""
        return self.invert(center)

    def opR(self):
        """Shorthand for retrograde()."""
        return self.retrograde()

    # Analysis methods --------------------------------------------------------

    def min(self):
        """
        Return the minimum pitch of the current pseg.

        >>> Pseg([52, 60, 63, 69]).min()
        52

        :return: minimum pitch of the current pseg.
        :rtype: int
        """
        return min(self._pseg)

    def max(self):
        """
        Return the maximum pitch of the current pseg.

        >>> Pseg([52, 60, 63, 69]).max()
        69

        :return: maximum pitch of the current pseg.
        :rtype: int
        """
        return max(self._pseg)

    def int_(self, n, mode=0, nparr=False):
        """
        Return an INTn vector.

        n indicates the difference between order position numbers of the two
        elements compared; that is, INT3 compares elements which are 3
        positions apart.

        >>> s = [60, 54, 74, 59]
        >>> Pseg(s).int_(1, mode=0))
        [-6, 20, -15]
        >>> Pseg(s).int_(1, mode=1))
        [6, 20, 15]
        >>> Pseg(s).int_(1, mode=2))
        [6, 8, 9]
        >>> Pseg(s).int_(1, mode=3))
        [6, 4, 3]

        :param n: n in INTn.
        :param mode: the measured intervals are:

            * ordered pitch intervals (0)
            * unordered pitch intervals (1)
            * ordered pitch-class intervals (2)
            * unordered pitch-class intervals (3)

        :param nparr: selector for the output data type.
        :type n: int
        :type mode: int
        :type nparr: bool
        :return: a list (nparr=False) or ndarray (nparr=True) of INTn vector.
        :rtype: list or ndarray
        """
        return int_(self._pseg, n, mode, nparr)

    def length(self):
        """
        Return the "length" of the current pseg.

        Pseg length is the sum of unordered intervals between the successive
        pitches in the segment.

        >>> Pseg([52, 60, 63, 69]).length()
        15

        :return: pseg length.
        :rtype: int
        """
        return sum(map(abs, self.int_(1)))

    def cseg(self, nparr=False):
        """
        Return the cseg of the current pseg.

        >>> Pseg([60, 52, 63, 69]).cseg()
        [1, 0, 2, 3]

        Consecutively repeated pitches are treated as a single cp.

        >>> Pseg([60, 52, 52, 69]).cseg()
        [1, 0, 2]

        :return: cseg of the current pseg.
        :rtype: list
        """
        # Remove consecutive pitches.
        pseg = [p for p, _ in groupby(self._pseg)]
        return normalForm(pseg, nparr=nparr)

    def pcseg(self, nparr=False):
        """
        Return the pcseg of the current pseg.

        >>> Pseg([52, 60, 63, 69]).pcseg()
        [4, 0, 3, 9]

        :param nparr: selector for the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or ndarray (nparr=True) of the pcseg
            of the current pseg.
        :rtype: list or ndarray
        """
        return psegToPcseg(self._pseg, nparr=nparr)

    def psseg(self, nparr=False):
        """
        Return the psseg of the current pseg.

        >>> Pseg([52, 60, 63, 69]).psseg()
        [2, 0, 1]

        :param nparr: selector for the output data type.
        :type nparr: bool
        :return: a list (nparr=False) or ndarray (nparr=True) of the psseg
            of the current pseg.
        :rtype: list or ndarray
        """
        intervals = Pseg(self._pseg).int_(1, mode=1)
        return psegToPsseg(self._pseg, nparr=nparr)


# Utility functions -----------------------------------------------------------

def psegToPcseg(pseg, nparr=False):
    """
    Return the pcseg of the input pseg.

    >>> psegToPcseg([52, 60, 63, 69])
        [4, 0, 3, 9]

    :param pseg: p-segment.
    :param nparr: selector for the output data type.
    :type pseg: segment
    :type nparr: bool
    :return: a list (nparr=False) or ndarray (nparr=True) of the pcseg.
    :rtype: list or ndarray
    """
    return adaptOutput(list(map(lambda p: p % 12, pseg)), nparr=nparr)


def psegToPsseg(pseg, nparr=False):
    """
    Return the psseg of the input pseg.

    >>> psegToPsseg([52, 60, 63, 69])
        [2, 0, 1]

    :param pseg: p-segment.
    :param nparr: selector for the output data type.
    :type pseg: segment
    :type nparr: bool
    :return: a list (nparr=False) or ndarray (nparr=True) of the psseg.
    :rtype: list or ndarray
    """
    intervals = Pseg(pseg).int_(1, mode=1)
    return adaptOutput(list(normalForm(intervals)), nparr=nparr)
