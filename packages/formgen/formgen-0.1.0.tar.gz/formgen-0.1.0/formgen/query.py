import os.path
import pickle

__all__ = ["catalog",
           "toPrimeForm",
           "toSegclassName"]

filename = os.path.join(os.path.dirname(__file__), "pickles/catalog.pickle")
with open(filename, "rb") as f:
    catalog = pickle.load(f)


def toPrimeForm(sn):
    """
    Return the prime form of the input segclass name.

    >>> toPrimeForm("4-3")
    (0, 2, 1, 3)

    :param sn: segclass name.
    :type sn: str
    :return: prime form that corresponds with the input segclass name.
    :rtype: tuple
    """
    # Get cardinal and ordinal numbers
    card, ord_ = sn.split("-")
    # PFs are keys of the dict in catalog
    pfs = catalog["segclass"][int(card)].keys()
    return list(pfs)[int(ord_)-1]


def toSegclassName(pf):
    """
    Return the segclass name of the input prime form.

    >>> toSegclassName((0, 2, 1, 3))
    "4-3"

    :param pf: prime form.
    :type pf: tuple
    :return: segclass name of the input prime form.
    :rtype: str
    """
    return catalog["segclass"][len(pf)][pf]["SN"]

