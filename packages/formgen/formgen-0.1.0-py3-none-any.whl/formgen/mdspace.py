from collections.abc import MutableSet, MutableSequence
from . import constants as c
from .contour import normalForm

__all__ = ["Mdset", "Mdseg"]


class Mdset(MutableSet):
    """Md-space set"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, mdset):
        """
        Constructor method.

        >>> Mdset({0.25, 0.5, 1.5})
        Mdset({0.25, 0.5, 1.5})

        :param mdset: md-space set.
        :type mdset: iterable
        """
        MutableSet.__init__(self)
        self._mdset = set(mdset)

    def __and__(self, mdset):
        """
        Return self & mdset.

        Intersection operation: returns a set containing mdurs in both the
        input and current mdset.

        >>> Mdset({0.25, 0.5, 1.5}) & {0.5, 1.5, 2.0}
        Mdset({0.5, 1.5})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Intersection of the input and current mdsets.
        :rtype: Mdset object
        """
        return MutableSet.__and__(self, set(mdset))

    def __contains__(self, mdur):
        """
        Return a bool of the element membership to the current mdset.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> 0.5 in s
        True

        :param mdur: mdur to test the membership to the current mdset.
        :type mdur: float
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return mdur in self._mdset

    def __eq__(self, mdset):
        """
        Return self == mdset.

        >>> Mdset({0.5, 1.5, 2.0}) == {0.5, 1.5, 2.0}
        True

        :param mdset: md-space set.
        :type mdset: iterable
        :return: True if the input and current mdsets are the same,
            False otherwise.
        :rtype: bool
        """
        return MutableSet.__eq__(self, set(mdset))

    def __gt__(self, mdset):
        """
        Return self > mdset.

        Proper superset: also tests that the current and input mdsets are not
        the same.

        >>> Mdset({0.5, 1.5, 2.0}) > {0.5, 1.5, 2.0}
        False

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self > mdset.
        :rtype: bool
        """
        return MutableSet.__gt__(self, set(mdset))

    def __ge__(self, mdset):
        """
        Return self >= mdset.

        Superset: tests whether every element in the input mdset is also in
        the current mdset.

        >>> Mdset({0.5, 1.5, 2.0}) >= {0.5, 1.5}
        True

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self >= mdset.
        :rtype: bool
        """
        return MutableSet.__ge__(self, set(mdset))

    def __iand__(self, mdset):
        """
        Return self &= mdset.

        Augmented assignment for intersection.

        >>> s = Mdset({0.5, 1.5})
        >>> s &= {0.5, 2.0}
        >>> s
        Mdset({0.5})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self &= mdset.
        :rtype: bool
        """
        return MutableSet.__iand__(self, set(mdset))

    def __ior__(self, mdset):
        """
        Return self |= mdset.

        Augmented assignment for union.

        >>> s = Mdset({0.5, 1.5})
        >>> s |= {0.5, 2.0}
        >>> s
        Mdset({0.5, 1.5, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self |= mdset.
        :rtype: bool
        """
        return MutableSet.__ior__(self, set(mdset))

    def __isub__(self, mdset):
        """
        Return self -= mdset.

        Augmented assignment for difference.

        >>> s = Mdset({0.5, 1.5})
        >>> s -= {0.5, 2.0}
        >>> s
        Mdset({1.5})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self -= mdset.
        :rtype: bool
        """
        return MutableSet.__isub__(self, set(mdset))

    def __iter__(self):
        """
        Return a generator object comprising the current mdset's elements.

        >>> for i in Mdset({0.25, 0.5, 1.5}):
        ...     print(i)
        0.25
        0.5
        1.5

        :return: iterator with the current mdset's elements.
        :rtype: iterator
        """
        return self._mdset.__iter__()

    def __ixor__(self, mdset):
        """
        Return self ^= mdset.

        Augmented assignment for symmetric difference.

        >>> s = Mdset({0.5, 1.5})
        >>> s ^= {0.5, 2.0}
        >>> s
        Mdset({1.5, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self ^= mdset.
        :rtype: bool
        """
        return MutableSet.__ixor__(self, set(mdset))

    def __le__(self, mdset):
        """
        Return self <= mdset.

        Subset: tests whether every element in the current mdset is also in
        the input mdset.

        >>> Mdset({0.5, 1.5}) <= {0.5, 1.5, 2.0}
        True

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self <= mdset.
        :rtype: bool
        """
        return MutableSet.__le__(self, set(mdset))

    def __len__(self):
        """
        Return the cardinality of the current mdset.

        >>> len(Mdset({0.25, 0.5, 1.5}))
        3

        :return: cardinality of the current mdset.
        :rtype: int
        """
        return len(self._mdset)

    def __lt__(self, mdset):
        """
        Return self < mdset.

        Proper subset: also tests that the current and input mdsets are not
        the same.

        >>> Mdset({0.5, 1.5, 2.0}) < {0.5, 1.5, 2.0}
        False

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self < mdset.
        :rtype: bool
        """
        return MutableSet.__lt__(self, set(mdset))

    def __ne__(self, mdset):
        """
        Return self != mdset.

        >>> Mdset({0.5, 1.5, 2.0}) != {0.5, 1.5, 2.0}
        False

        :param mdset: md-space set.
        :type mdset: iterable
        :return: self != mdset.
        :rtype: bool
        """
        return MutableSet.__ne__(self, set(mdset))

    def __or__(self, mdset):
        """
        Return self | mdset.

        Union operation: returns a mdset containing mdurs in either the
        input or current mdset.

        >>> Mdset({0.25, 0.5, 1.5}) | {0.5, 1.5, 2.0}
        Mdset({0.25, 0.5, 1.5, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Union of the input and current mdsets.
        :rtype: Mdset object
        """
        return MutableSet.__or__(self, set(mdset))

    def __sub__(self, mdset):
        """
        Return self - mdset.

        Return a mdset containing mdurs in the current mdset that are not in
        the input mdset.

        >>> Mdset({0.25, 0.5, 1.5}) - {0.5, 1.5, 2.0}
        Mdset({0.25})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Difference of the input and current mdsets.
        :rtype: Mdset object
        """
        return MutableSet.__sub__(self, set(mdset))

    def __xor__(self, mdset):
        """
        Return self ^ mdset

        Symmetric difference operation: returns a mdset with mdurs in
        either the input or current mdset but not both.

        >>> Mdset({0.25, 0.5, 1.5}) ^ {0.5, 1.5, 2.0}
        Mdset({0.25, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Symmetric difference of the input and current mdsets.
        :rtype: Mdset object
        """
        return MutableSet.__xor__(self, set(mdset))

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Mdset({0.25, 0.5, 1.5})
        Mdset({0.25, 0.5, 1.5})

        :return: official representation of the object.
        :rtype: str
        """
        return "Mdset({})".format(self._mdset)

    def add(self, mdur):
        """
        Add an mdur to the current mdset.

        This has no effect if the mdur is already present.

        >>> Mdset({0.25, 0.5, 1.5}).add(2.0)
        Mdset({0.25, 0.5, 2.0, 1.5})

        :param mdur: mdur to add to the current mdset.
        :type mdur: float
        :return: mutated mdset.
        :return: Mdset object
        """
        self._mdset.add(mdur)
        return self

    def clear(self):
        """
        Remove all elements from the current mdset.

        >>> a = Mdset({0.25, 0.5, 1.5})
        >>> a.clear()
        Mdset(set())

        :return: mutated mdset.
        :return: Mdset object
        """
        self._mdset = set()
        return self

    def discard(self, mdur):
        """
        Remove an mdur from the current mdset if it is a member.

        Unlike remove(), discard() does not raise an error if the mdur is
        not a member.

        >>> Mdset({0.25, 0.5, 1.5}).discard(1.5)
        Mdset({0.25, 0.5})

        :param mdur: mdur to remove from the current mdset.
        :type mdur: float
        :return: mutated mdset.
        :return: Mdset object
        """
        self._mdset.discard(mdur)
        return self

    def isdisjoint(self, mdset):
        """
        Return True if the input and current mdsets have a null intersection.

        >>> Mdset({0.25, 0.5, 1.5}).isdisjoint({1.5, 2.0})
        False

        :param mdset: md-space set.
        :type mdset: iterable
        :return: True if the input and current mdsets have a null
            intersection, False otherwise.
        :rtype: bool
        """
        return MutableSet.isdisjoint(self, set(mdset))

    def pop(self):
        """
        Remove and return an arbitrary element of the current mdset.

        Raises KeyError if the mdset is empty.

        >>> Mdset({0.25, 0.5, 1.5}).pop()
        0.25

        :return: an arbitrary element of the current mdset.
        :rtype: float
        """
        return MutableSet.pop(self)

    def remove(self, mdur):
        """
        Remove an element by value from the current mdset.

        If the element is not a member, raise a KeyError.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> s.remove(1.5)
        Mdset({0.25, 0.5})
        >>> s.remove(1.5)
        KeyError: 1.5

        :param mdur: mdur to remove from the current mdset.
        :type mdur: float
        :return: mutated mdset.
        :return: Mdset object
        """
        MutableSet.remove(self, mdur)
        return self

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Mdset(self._mdset)

    # Property methods --------------------------------------------------------

    @property
    def mdset(self):
        """
        Return the current mdset.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> s.mdset
        {0.25, 0.5, 1.5}

        :return: current mdset.
        :rtype: set
        """
        return self._mdset

    @mdset.setter
    def mdset(self, mdset_):
        """
        Set the current mdset to the input mdset.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> s.mdset = {1.25, 1.5, 2.5}
        >>> s.mdset
        {1.25, 1.5, 2.5}

        :param mdset_: md-space set.
        :type mdset_: iterable
        """
        self._mdset = set(mdset_)

    # Mutator methods ---------------------------------------------------------

    def union(self, mdset):
        """
        Update and return the current mdset with the union of itself and
        the input mdset.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> s.union({0.5, 1.5, 2.0})
        Mdset({0.25, 0.5, 1.5, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Union of the input and current mdsets.
        :rtype: Mdset object
        """
        self._mdset |= set(mdset)
        return self

    def intersection(self, mdset):
        """
        Update and return the current mdset with the intersection of itself and
        the input mdset.

        >>> s = Mdset({0.5, 1.5})
        >>> s.intersection({0.5, 2.0})
        Mdset({0.5})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Intersection of the input and current mdsets.
        :rtype: Mdset object
        """
        self._mdset &= set(mdset)
        return self

    def difference(self, mdset):
        """
        Update and return the current mdset with the difference of itself and
        the input mdset.

        >>> s = Mdset({0.5, 1.5})
        >>> s.difference({0.5, 2.0})
        Mdset({1.5})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Difference of the input and current mdsets.
        :rtype: Mdset object
        """
        self._mdset -= set(mdset)
        return self

    def symmetricDifference(self, mdset):
        """
        Update and return the current mdset with the symmetric difference of
        itself and the input mdset.

        >>> s = Mdset({0.25, 0.5, 1.5})
        >>> s.symmetricDifference({0.5, 1.5, 2.0})
        Mdset({0.25, 2.0})

        :param mdset: md-space set.
        :type mdset: iterable
        :return: Symmetric difference of the input and current mdsets.
        :rtype: Mdset object
        """
        self._mdset ^= set(mdset)
        return self

    # Analysis methods --------------------------------------------------------

    def min(self):
        """
        Return the minimum mdur of the current mdset.

        >>> Mdset({0.25, 0.5, 1.5}).min()
        0.25

        :return: minimum mdur of the current mdset.
        :rtype: float
        """
        return min(self)

    def max(self):
        """
        Return the maximum mdur of the current mdset.

        >>> Mdset({0.25, 0.5, 1.5}).max()
        1.5

        :return: maximum mdur of the current mdset.
        :rtype: float
        """
        return max(self)


class Mdseg(MutableSequence):
    """Md-space set"""

    # Basic methods -----------------------------------------------------------

    def __init__(self, mdseg):
        """
        Constructor method.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0])
        Mdseg([0.25, 0.5, 0.25, 1.0])

        :param mdseg: md-space segment.
        :type mdseg: segment
        """
        MutableSequence.__init__(self)
        self._mdseg = list(mdseg)
        self._qint = c.QUANTIZATION_INTERVAL

    def __contains__(self, mdur):
        """
        Return a bool of the element membership to the current mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> 0.25 in s
        True

        :param mdur: mdur to test the membership to the current mdseg.
        :type mdur: float
        :return: True if the element is in self, False otherwise.
        :rtype: bool
        """
        return MutableSequence.__contains__(self, mdur)

    def __delitem__(self, index):
        """
        Delete the indexed element.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> del s[1]
        >>> s
        Pseg([0.25, 0.25, 1.0])

        :param index: index at which the element is deleted.
        """
        del self._mdseg[index]

    def __getitem__(self, index):
        """
        Return the indexed mdur of the current mdseg.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0])[3]
        1.0

        :param index: index to get a mdur.
        :type index: int
        :return: indexed mdur.
        :rtype: float
        """
        return self._mdseg[index]

    def __iadd__(self, mdseg):
        """
        Append the input mdseg to the current mdseg in-place.

        This operation is equivalent to self.extend(mdseg) but invoked by +=
        operator.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s += [1.5, 0.5]
        >>> s
        Mdseg([0.25, 0.5, 0.25, 1.0, 1.5, 0.5])

        :param mdseg: mdseg to append to the current mdseg.
        :type mdseg: segment
        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        MutableSequence.__iadd__(self, mdseg)
        return self

    def __iter__(self):
        """
        Return a generator object comprising the current mdseg's elements.

        >>> for i in Mdseg([0.25, 0.5, 0.25, 1.0]):
        ...     print(i)
        0.25
        0.5
        0.25
        1.0

        :return: iterator with the current mdseg's elements.
        :rtype: iterator
        """
        return MutableSequence.__iter__(self)

    def __len__(self):
        """
        Return the cardinality of the current mdseg.

        >>> len(Mdseg([0.25, 0.5, 0.25, 1.0]))
        4

        :return: cardinality of the current mdseg.
        :rtype: int
        """
        return len(self._mdseg)

    def __reversed__(self):
        """
        Return a reverse iterator of the current mdseg's elements.

        >>> list(reversed(Mdseg([0.25, 0.5, 0.25, 1.0])))
        [1.0, 0.25, 0.5, 0.25]

        :return: iterator that iterates over the current mdseg elements in
            reverse order.
        :rtype: iterator
        """
        return MutableSequence.__reversed__(self)

    def __setitem__(self, index, value):
        """
        Set the value of the indexed element.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s[2] = 0.125
        >>> s
        Mdseg([0.25, 0.5, 0.125, 1.0])

        :param index: index at which the element changes the value.
        :param value: value to change the indexed element.
        :type index: int
        :type value: float
        """
        self._mdseg[index] = value

    def __repr__(self):
        """
        Return the official string representation of the object.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0])
        Mdseg([0.25, 0.5, 0.25, 1.0])

        :return: official representation of the object.
        :rtype: str
        """
        return "Mdseg({})".format(self._mdseg)

    def append(self, mdur):
        """
        Append a single mdur to the end of the current mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.append(1.5)
        Mdseg([0.25, 0.5, 0.25, 1.0, 1.5])

        :param mdur: mdur to append.
        :type mdur: float
        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        MutableSequence.append(self, mdur)
        return self

    def count(self, mdur):
        """
        Return the number of occurrences of the mdur.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).count(0.25)
        2

        :param mdur: mdur to check the occurrence frequency in the
            current mdseg.
        :type mdur: float
        :return: the number of occurrences of the mdur.
        :rtype: int
        """
        return MutableSequence.count(self, mdur)

    def extend(self, mdseg):
        """
        Extend the current mdseg by appending the input mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.extend([1.5, 2.0])
        Mdseg([0.25, 0.5, 0.25, 1.0, 1.5, 2.0])

        :param mdseg: mdseg to append to the current mdseg.
        :type mdseg: segment
        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        MutableSequence.extend(self, mdseg)
        return self

    def index(self, mdur, start=0, stop=None):
        """
        Return the first index of the mdur.

        Raise ValueError if the element is not present.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).index(0.25)
        0
        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).index(1.5)
        ValueError
        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).index(0.25, 1)
        2

        :param mdur: mdur to check the first index.
        :param start: start index for search.
        :param stop: stop index for search.
        :type mdur: float
        :type start: int
        :type stop: int
        :return: first index of the mdur.
        :rtype: int
        """
        if stop is None:
            stop = len(self._mdseg)
        return MutableSequence.index(self, mdur, start, stop)

    def insert(self, index, mdur):
        """
        Insert the mdur at the specified index of the mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.insert(3, 1.5)
        Mdseg([0.25, 0.5, 0.25, 1.5, 1.0])

        :param index: index at which the mdur is inserted.
        :param mdur: element to insert.
        :type index: int
        :type mdur: float
        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        self._mdseg.insert(index, mdur)
        return self

    def pop(self, index=-1):
        """
        Remove and return an element at the index (default last).

        Raise IndexError if the index is out of range.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.pop()
        1.0
        >>> s.pop(1)
        0.5
        >>> s
        [0.25, 0.25]

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

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.remove(0.25)
        Mdseg([0.5, 0.25, 1.0])

        :param value: value with which an element is removed.
        :type value: float
        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        MutableSequence.remove(self, value)
        return self

    def reverse(self):
        """
        Reverse the current mdseg in place.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.reverse()
        Mdseg([1.0, 0.25, 0.5, 0.25])

        :return: mutated mdseg.
        :rtype: Mdseg object
        """
        MutableSequence.reverse(self)
        return self

    def copy(self):
        """Return a deep copy of the current state of the object."""
        return Mdseg(self._mdseg)

    # Property methods --------------------------------------------------------

    @property
    def mdseg(self):
        """
        Return the current mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.mdseg
        [0.25, 0.5, 0.25, 1.0]

        :return: current mdseg.
        :rtype: list
        """
        return self._mdseg

    @property
    def qint(self):
        """
        Return the current quantization interval.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.qint
        0.125  # Default interval

        :return: current quantization interval.
        :rtype: float
        """
        return self._qint

    @mdseg.setter
    def mdseg(self, mdseg_):
        """
        Set the current mdseg to the input mdseg.

        >>> s = Mdseg([0.25, 0.5, 0.25, 1.0])
        >>> s.mdseg = [1.0, 1.5, 0.5]
        >>> s.mdseg
        [1.0, 1.5, 0.5]

        :param mdseg_: md-space segment.
        :type mdseg_: iterable
        """
        self._mdseg = list(mdseg_)

    @qint.setter
    def qint(self, qint_):
        """
        Set the current quantization interval to the input value.

        >>> s = Mdset([0.25, 0.5, 0.25, 1.0])
        >>> s.qint = 0.5
        >>> s.qint
        0.5

        :param qint_: quantization interval.
        :type qint_: float
        """
        self._qint = float(qint_)

    # Analysis methods --------------------------------------------------------

    def length(self):
        """
        Return the "length" of the current pseg.

        Mdseg length is the sum of mdurs.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).length()
        2.0

        :return: Mdseg length.
        :rtype: float
        """
        return sum(self.mdseg)

    def dseg(self, nparr=False):
        """
        Return the dseg of the current mdseg.

        >>> Mdseg([0.25, 0.5, 0.25, 1.0]).dseg()
        [0, 1, 0, 2]

        :return: dseg of the current mdseg.
        :rtype: list
        """
        return normalForm(self.mdseg, nparr=nparr)
