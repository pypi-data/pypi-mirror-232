import numpy as np

# __all__ = []


def adaptOutput(data, nparr):
    """
    Return the input data adapted to NumPy ndarray or list data type.

    :param data: input data.
    :param nparr: selector for the output data type.
    :type data: segment or 2D array
    :type nparr: bool
    :return: the input data is adapted to ndarray if nparr=True, a list is
        output otherwise.
    :rtype: list or ndarray
    """
    data = np.array(data)
    if nparr:
        return data
    else:
        return data.tolist()


def countRepeatedElements(seg):
    """
    Return the number of repeated-elements in the input seg.

    >>> countRepeatedElements([3, 3, 1, 2, 2, 3])
    3

    :param seg: contour segment.
    :type seg: segment
    :return: the number of repeated-elements in the input seg.
    :rtype: int
    """
    return len(seg) - len(set(seg))


def countUniqueElements(seg):
    """
    Return the number of unique elements in the input seg.

    >>> countUniqueElements([3, 3, 3, 1, 2, 2, 4])
    4

    :param seg: contour segment.
    :type seg: segment
    :return: the number of unique elements in the input seg.
    :rtype: int
    """
    return len(set(seg))


def factorial(n):
    """
    Return the factorial of n.

    :param n: n for n!.
    :type n: int
    :return: n!
    :rtype: int
    """
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def repeatPattern(seg):
    """
    Return the pattern of repeated-elements in the input seg.

    >>> repeatPattern([0, 3, 2, 1])
    0
    >>> repeatPattern([3, 4, 1, 3, 0])
    1
    >>> repeatPattern([3, 1, 0, 0, 2])
    2

    :param seg: contour segment.
    :type seg: segment
    :return: the pattern of repeated-elements in the input seg:

        * no repeat exists (0)
        * non-consecutive repeat(s) exists (1)
        * consecutive repeat(s) exists (2)

    :rtype: int
    """
    # No repeated-elements
    if countRepeatedElements(seg) == 0:
        return 0
    # One or more repeated-elements
    else:
        # Check the presence of consecutively repeated elements.
        for i in range(len(seg) - 1):
            if seg[i] == seg[i+1]:
                return 2
        # Non-consecutive repeat(s) exist.
        return 1


def isPc(value):
    """
    Check whether the input value is valid for a pc.

    :param value: value to be checked as a pc.
    :type: int
    :return: True is if the input value is mod 12 int and valid for a pc,
        and False otherwise.
    :rtype: bool
    """
    return value == (value % 12)


def checkInput(elements, checkRep=False, checkLen=None, checkPc=False,
               checkDup=False):
    """
    Raise an error when the input is not contextually valid.

    >>> checkInput([0, 2, 1, 1], checkRep=True)
    ValueError: Cseg cannot have consecutively repeated elements.
    >>> checkInput([0, 1], checkLen=3)
    ValueError: The input iterable must have at least 3 elements.
    >>> checkInput({0, 1, 13}, checkPc=True)
    ValueError: The input iterable includes non-pc element(s).
    >>> checkInput([0, 1, 4, 1], checkDup=True)
    ValueError: The input iterable includes duplicate pcs.

    :param elements: elements to form a seg or a set.
    :param checkRep: if true, raises error if the input iterable includes
        consecutively repeated elements. This criterion is relevant to cseg
        and pseg.
    :param checkLen: raises error if the input iterable does not have at
        least the specified number of elements.
    :param checkPc: if true, raises error if the input iterable has element(s)
        that is not mod-12 int.
    :param checkDup: if true, raises error if the input iterable has
        duplicate elements, which is not allowed for a pcset.
    :type elements: iterable
    :type checkRep: bool
    :type checkLen: int
    :type checkPc: bool
    :type checkDup: bool
    """
    try:
        if (checkRep is True) and (repeatPattern(elements) == 2):
            raise ValueError("Cseg cannot have consecutively repeated "
                             "elements.")
        elif (checkLen is not None) and (len(elements) < checkLen):
            raise ValueError("The input iterable must have at least {} "
                             "elements.".format(checkLen))
        elif (checkPc is True) and any(not(isPc(v)) for v in elements):
            raise ValueError("The input iterable includes non-pc element(s).")
        elif (checkDup is True) and (countRepeatedElements(elements) != 0):
            raise ValueError("The input iterable includes duplicate pcs.")
    except ValueError:
        raise


def int_(seg, n, mode=0, nparr=False):
    """
    Return an INTn vector.

    n indicates the difference between order position numbers of the two
    elements compared; that is, INT3 compares elements which are 3
    positions apart.

    >>> s = [60, 54, 74, 59]
    >>> int_(s, 1, mode=0))
    [-6, 20, -15]
    >>> int_(s, 1, mode=1))
    [6, 20, 15]
    >>> int_(s, 1, mode=2))
    [6, 8, 9]
    >>> int_(s, 1, mode=3))
    [6, 4, 3]

    :param seg: p-segment (use any mode) or pc-segment (use either mode 2 or 3)
    :param n: n in INTn.
    :param mode: the measured intervals are:

        * ordered pitch intervals (0)
        * unordered pitch intervals (1)
        * ordered pitch-class intervals (2)
        * unordered pitch-class intervals (3)

    :param nparr: selector for the output data type.
    :type seg: segment
    :type n: int
    :type mode: int
    :type nparr: bool
    :return: a list (nparr=False) or ndarray (nparr=True) of INTn vector.
    :rtype: list or ndarray
    """
    v = []
    card = len(seg)
    for i in range(card - n):
        v.append(seg[i + n] - seg[i])  # Ordered pitch intervals
    if mode == 0:
        pass
    elif mode == 1:
        v = list(map(abs, v))  # Unordered pitch intervals
    else:
        v = list(map(lambda x: x % 12, v))  # Ordered pc intervals
        if mode == 3:
            v = [12 - x if x > 6 else x for x in v]  # Unordered pc intervals
    return adaptOutput(v, nparr)
