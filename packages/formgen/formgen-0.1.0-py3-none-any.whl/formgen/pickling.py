"""
This module includes functions that collectively generate a pickle file for
queries related to the objects in formgen modules.

A fresh copy of the pickle file can be made through directly running this
module script: a new ``catalog.pickle`` will be created in the same directory
where this script is in.
"""

from multiprocessing import Pool
import os
import pickle
import time
import datetime
from itertools import product
from .contour import (normalForm, primeForm, comMatrix, segclassMembers,
                      segclassRelation, xsim, axmemb)
from .utils import (countUniqueElements, countRepeatedElements, repeatPattern)
from .cspace import Cseg
from . import constants as c
from pcpy.relation import icvsim
from pcpy.query import makePFLists

# __all__ = []


def makeElements():
    """
    Return ``segLists`` and ``segclassLists``.

    This function creates all the possible segs and segclasses in the sizes of
    ``MINSEGCARD`` and ``MAXSEGCARD`` (both are package-wide constants in
    ``formgen.constants``).

    segLists and segclassLists are both nested lists in which the element-lists
    are the generated segs and segclasses ordered by their cardinalities.
    In the element-lists, the segs and segclasses are represented by tuples
    and sorted by the lexicographic order and then the number of repeated
    elements.

    :return: segLists and segclassLists.
    :rtype: tuple
    """
    print("Making elements started...")
    segLists = []
    segclassLists = []
    for card in range(c.MIN_SEG_CARD, c.MAX_SEG_CARD + 1):

        # Make seg and segclass elements
        products = product(range(card), repeat=card)
        segs = set([tuple(normalForm(s)) for s in products])
        segs.remove((0,) * card)  # Exclude one-element seg (e.g., (0,0,0))
        segclasses = set([tuple(primeForm(s)) for s in segs])

        # Sort the elements by the repeat counts first and lexicographic order.
        segs = sorted(segs, key=lambda x: (countRepeatedElements(x), x))
        segclasses = sorted(segclasses,
                            key=lambda x: (countRepeatedElements(x), x))

        # Add the lists of segs and segclasses to segLists and segclassLists.
        segLists.append(list(segs))
        segclassLists.append(list(segclasses))
    print("Making elements completed.")
    return segLists, segclassLists


def mapSegclasses(segclassLists):
    """
    Return the mapping of contour segclasses and their profiles.

    The mapping structure is a nested dict:

        {2, {PF: profile, ...},
         3, {PF: profile, ...},
         ...
         7, {PF: profile, ...}}

    The top-level dict has pairs of the key (cardinality [2, 7]) and
    the second-level dict which in turn has the key (segclass (PF))
    and the value (the profile data of the segclass).

    The profile of each segclass is also a dict. For example, the key
    segclass (0, 2, 1, 3) is associated with a dict as follows::

        {'uniqueElements': 4,
         'repeatPattern': 0,
         'SN': '4-3',
         'COM-matrix': [[0, 1, 1, 1],
                        [-1, 0, -1, 1],
                        [-1, 1, 0, 1],
                        [-1, -1, -1, 0]],
         'members': {'I': [3, 1, 2, 0],
                     'P': [0, 2, 1, 3],
                     'R': [3, 1, 2, 0],
                     'RI': [0, 2, 1, 3]}
         }

    The keys of the profile dict are:

        * ``uniqueElements``: an int for the number of unique elements in
          the segclass.
        * ``repeatPattern``: an int for the pattern of repeated elements in the
          segclass:

            - no repeats (0)
            - non-immediate repeats(s) (1)
            - immediate repeat(s) (2).

        * ``SN``: a str for the segclass name.
        * ``COM-matrix``: a 2D list for the COM-matrix.
        * ``members``: a dict for the segclass members (P, I, R, RI).

    :param segclassLists: lists of segclasses ordered by the cardinality.
    :type segclassLists: 2D list
    :return: nested dict with all the segclasses of sizes 2 to 7. It is
        sorted by the cardinality at the top-level dict and the PF (
        the number of repeated elements and the lexicographic order) in the
        second-level dict.
    :rtype: dict
    """
    dct = {}
    for card in range(c.MIN_SEG_CARD, c.MAX_SEG_CARD + 1):
        members = []
        index = 1
        for s in segclassLists[card - c.MIN_SEG_CARD]:
            profile = {"uniqueElements": countUniqueElements(s),
                       "repeatPattern": repeatPattern(s),
                       "SN": "{0}-{1}".format(card, index),
                       "COM-matrix": comMatrix(s),
                       "members": segclassMembers(s)}
            members.append((s, profile))
            index += 1
        dct[card] = dict(members)
    return dct


def mapSegs(segLists, dctSegclass):
    """
    Return the mapping of contour segments and their profiles.

    The mapping is a nested dict::

        {2, {NF: profile, ...},
         3, {NF: profile, ...},
         ...
         7, {NF: profile, ...}}

    The top-level dict has pairs of the key (cardinality [2, 7]) and the
    second-level dict which in turn has the key (seg (NF)) and the value
    (the profile data of the seg).

    The profile of each seg is a dict. For example, the key seg (0, 2, 1,
    3) is associated with a dict as follows::

        {'uniqueElements': 4,
         'repeatPattern': 0,
         'COM-matrix': [[0, 1, 1, 1],
                        [-1, 0, -1, 1],
                        [-1, 1, 0, 1],
                        [-1, -1, -1, 0]],
         'SN': '4-3',
         'PF': (0, 2, 1, 3),
         'relation': 4
         }

    The keys of the profile dict are:

        * ``uniqueElements``: an int for the number of unique elements in
          the seg.
        * ``repeatPattern``: an int for the pattern of repeated elements in the
          seg:

            - no repeats (0)
            - non-immediate repeats(s) (1)
            - immediate repeat(s) (2).
        * ``SN``: a str for the seg name.
        * ``PF``: a tuple for the prime form.
        * ``COM-matrix``: a 2D list for the COM-matrix.
        * ``relation``: an int for the segclass relation status:

            - identity (0)
            - inversion (1)
            - retrograde (2)
            - retrograde-inversion (3)
            - both identity and retrograde-inversion (4)
            - both inversion and retrograde (5).

    :param segLists: lists of segs ordered by the cardinality.
    :param dctSegclass: mapping of segclass profiles.
    :type segLists: 2D list
    :type dctSegclass: dict
    :return: nested dict with all the segs of sizes 2 to 7. It is sorted by
        the cardinality at the top-level dict and the NF (the lexicographic
        order and the number of repeated elements) in the second-level dict.
    :rtype: dict
    """
    dct = {}
    for card in range(c.MIN_SEG_CARD, c.MAX_SEG_CARD + 1):
        members = []
        for s in segLists[card - c.MIN_SEG_CARD]:
            pf = tuple(primeForm(s))
            profile = {"uniqueElements": countUniqueElements(s),
                       "repeatPattern": repeatPattern(s),
                       "SN": dctSegclass[card][pf]["SN"],
                       "PF": pf,
                       "COM-matrix": comMatrix(s),
                       "relation": segclassRelation(s)}
            members.append((s, profile))
        dct[card] = dict(members)
    return dct


def workerSimilaritySegclass(s, segclasses, dctSegclass):
    """
    Worker function to compute the segclass similarity values.

    :param s: segclass for which the func measures similarity for.
    :param segclasses: all the segclasses to measure similarity with s1.
    :param dctSegclass: segclass profile.
    :type s: tuple
    :type segclasses: list
    :type dctSegclass: dict
    :return: segclasses with the measured similarity values.
    :rtype: dict
    """
    dct = {}
    s1 = s
    card1 = len(s1)
    rep1 = dctSegclass[card1][s1]["repeatPattern"] != 2
    csims, dsims, acmembs, admembs = [], [], [], []
    for s2 in segclasses:
        card2 = len(s2)
        rep2 = dctSegclass[card2][s2]["repeatPattern"] != 2
        # Do not compare a segclass with itself.
        if s1 == s2:
            continue
        # CSIM, DSIM: cardinalities must be the same.
        if card1 == card2:
            xsimVal = xsim(s1, s2, segclass=True)
            # DSIM may include immediately repeated elements.
            dsims.append((s2, xsimVal))
            # CSIM considers only segs without immediate repeat(s).
            if rep1 and rep2:
                csims.append((s2, xsimVal))
        # ACMEMB considers only segs without immediate repeat(s).
        if rep1 and rep2:
            acmembs.append((s2, axmemb(s1, s2, contiguous=False,
                                       segclass=True)))
        # ADMEMB considers only contiguous subsegments.
        admembs.append((s2, axmemb(s1, s2, contiguous=True,
                                   segclass=True, admembOpt=True)))
    dct[s1] = {
        "CSIM": dict(sorted(csims, key=lambda x: x[1], reverse=True)),
        "DSIM": dict(sorted(dsims, key=lambda x: x[1], reverse=True)),
        "ACMEMB": dict(sorted(acmembs, key=lambda x: x[1], reverse=True)),
        "ADMEMB": dict(sorted(admembs, key=lambda x: x[1], reverse=True))
    }
    return dct


def workerSimilaritySeg(s, segs, dctSeg):
    """
    Worker function to compute the seg similarity values.

    :param s: seg for which the func measures similarity for.
    :param segs: all the segs to measure similarity with s1.
    :param dctSeg: dict of seg profile.
    :type s: tuple
    :type segs: list
    :type dctSeg: dict
    :return: segs with the measured similarity values.
    :rtype: dict
    """
    dct = {}
    s1 = s
    card1 = len(s1)
    rep1 = dctSeg[card1][s1]["repeatPattern"] != 2
    csims, dsims, acmembs, admembs = [], [], [], []
    cass, casvs, ccv1s, ccv2s = [], [], [], []
    for s2 in segs:
        card2 = len(s2)
        rep2 = dctSeg[card2][s2]["repeatPattern"] != 2
        # Do not compare a seg with itself.
        if s1 == s2:
            continue
        # All the segment similarity functions, except ACMEMB and
        #   ADMEMB, are applicable only to a pair of segments of the same
        #   cardinality.
        if card1 == card2:
            xsimVal = xsim(s1, s2)
            # DSIM may include consecutively repeated elements.
            dsims.append((s2, xsimVal))
            # CSIM, CAS, CASV, CCV1, CCV2 consider only csegs.
            if rep1 and rep2:
                csims.append((s2, xsimVal))
                cass.append((s2, Cseg(s1).simCAS(s2, norm=True)))
                casvs.append((s2, Cseg(s1).simCASV(s2, norm=True)))
                ccv1s.append((s2, Cseg(s1).simCCV1(s2, norm=True)))
                ccv2s.append((s2, Cseg(s1).simCCV2(s2, norm=True)))
        # ACMEMB considers only csegs and accept differing cardinalities.
        if rep1 and rep2:
            acmembs.append((s2, axmemb(s1, s2, contiguous=False)))
        # ADMEMB considers only contiguous subsegments.
        admembs.append((s2, axmemb(s1, s2, contiguous=True,
                                   admembOpt=True)))
    dct[s1] = {
        "CAS": dict(sorted(cass, key=lambda x: x[1], reverse=True)),
        "CASV": dict(sorted(casvs, key=lambda x: x[1], reverse=True)),
        "CCV1": dict(sorted(ccv1s, key=lambda x: x[1], reverse=True)),
        "CCV2": dict(sorted(ccv2s, key=lambda x: x[1], reverse=True)),
        "CSIM": dict(sorted(csims, key=lambda x: x[1], reverse=True)),
        "DSIM": dict(sorted(dsims, key=lambda x: x[1], reverse=True)),
        "ACMEMB": dict(sorted(acmembs, key=lambda x: x[1], reverse=True)),
        "ADMEMB": dict(sorted(admembs, key=lambda x: x[1], reverse=True))
    }
    return dct


def workerSimilaritySC(pf, pfs):
    """
    Worker function to compute the SC similarity values.

    :param pf: SC for which the func measures similarity for.
    :param pfs: all the SCs to measure similarity with pf.
    :type pf: tuple
    :type pfs: list
    :return: PFs with the measured similarity values.
    :rtype: dict
    """
    dct = {}
    s1 = pf
    icvsims, recrels = [], []

    for s2 in pfs:
        if s1 == s2:
            continue
        icvsims.append((s2, icvsim(s1, s2, raw=False)))
        # recrels.append((s2, recrel(s1, s2)))

    dct[s1] = {
        "ICVSIM": dict(sorted(icvsims, key=lambda x: x[1], reverse=True)),
        "RECREL": dict(sorted(recrels, key=lambda x: x[1], reverse=True))}

    return dct


def mapSimilaritySegclass(segclassLists, dctSegclass):
    """
    Return the mapping of segclass pairs with the similarity value.

    The mapping is a nested dict::

        {PF, {"CSIM": {PF: simVal, ...},
              "DSIM": {PF, simVal, ...},
              "ACMEMB": {PF, simVal, ...},
              "ADMEMB": {PF, simVal, ...}}

    The keys of the nested dicts refer to the functions used to measure the
    similarity between every segclass and every other segclass of
    cardinalities 3 through 7:

        * ``CSIM`` and ``DSIM`` refer to ``contour.xsim(seg1, seg2,
          segclass=True)``. Both seg1 and seg2 have the same cardinality.
        * ``ACMEMB`` refers to ``contour.axmemb(seg1, seg2, contiguous=False,
          segclass=True)``.
        * ``ADMEMB`` refers to ``contour.axmemb(seg1, seg2, contiguous=True,
          segclass=True, admembOpt=True)``.

    .. note::
        * In c-space, segclasses with immediately repeated elements are not
          possible, thus similarity values with such segclasses are
          excluded from CSIM and ACMEMB.
        * The values of ADMEMB is generated with the optimization
          ``admembOpt=True``, thus the similarity value differs from that of
          Marvin's original ADMEMB.

    The values for these keys are also dicts, each of which comprises
    pairs of segclass (PF) and similarity value. These pairs are ordered in
    the dict according to the similarity value from high to low. Further,
    those segclasses that have the same similarity value are ordered by the
    cardinality, the lexicographic order, and the number of repeated elements.

    For example, the key segclass (0, 2, 1, 3) is associated with a dict as
    follows::

        {'CSIM': {(0, 1, 2, 3): 0.8333333333333334,
                  (0, 3, 1, 2): 0.8333333333333334,
                  ...
                  (1, 0, 2, 1): 0.5},
         'DSIM': {(0, 1, 2, 3): 0.8333333333333334,
                  (0, 3, 1, 2): 0.8333333333333334,
                  ...
                  (0, 1, 1, 0): 0.3333333333333333}
         'ACMEMB': {(0, 1, 3, 2): 0.8636363636363636,
                    (0, 2, 3, 1): 0.8181818181818182,
                    ...
                    (0, 1, 0, 1): 0.45454545454545453},
         'ADMEMB': {(1, 0, 3, 2): 0.8333333333333334,
                    (1, 3, 0, 2): 0.8333333333333334,
                    ...
                    (0, 0, 1, 1): 0.25}}

    :param segclassLists: lists of segclasses ordered by the cardinality.
    :param dctSegclass: mapping of segclass profiles.
    :type segclassLists: 2D list
    :type dctSegclass: OrderedDict
    :return: nested dict for all the segclasses associated with dicts
        for the similarity measuring functions. Each of the inner dicts
        comprises pairs of segclass and similarity value, which
        are ordered by the similarity value from high to low.
    :rtype: dict
    """
    # Join the nested lists of segclasses.
    segclasses = [s for segclassList in segclassLists for s in segclassList]
    segclasses = segclasses[1:]  # Remove the two-element segclass.

    dct = {}  # dict to add elements in the parallel processes.

    pool = Pool(processes=c.MAX_PROCESSES)
    for s in segclasses:
        pool.apply_async(func=workerSimilaritySegclass,
                         args=(s, segclasses, dctSegclass),
                         callback=lambda r: dct.update(r))
    pool.close()
    pool.join()

    return dct


def mapSimilaritySeg(segLists, dctSeg):
    """
    Return the mapping of seg pairs with the similarity value.

    The mapping is a nested dict::

        {NF: {"CAS": {NF: simVal, ...},
              "CASV": {NF: simVal, ...},
              "CCV1": {NF: simVal, ...},
              "CCV2": {NF: simVal, ...},
              "CSIM": {NF: simVal, ...},
              "DSIM": {NF: simVal, ...},
              "ACMEMB": {NF: simVal, ...},
              "ADMEMB": {NF: simVal, ...}}}

    The keys of the nested dicts refer to the functions used to measure the
    similarity between every seg and every other seg of cardinalities 3
    through 7:

        * ``CAS`` measured by ``cspace.Cseg(seg1).cas(seg2, norm=True)``.
        * ``CASV`` measured by ``cspace.Cseg(seg1).casv(seg2, norm=True)``.
        * ``CCV1`` measured by ``cspace.Cseg(seg1).ccv1(seg2, norm=True)``.
        * ``CCV2`` measured by ``cspace.Cseg(seg1).ccv2(seg2, norm=True)``.
        * ``CSIM`` and ``DSIM`` measured by ``contour.xsim(seg1, seg2)``. Both
          seg1 and seg2 have the same cardinality.
        * ``ACMEMB`` measured by
          ``contour.axmemb(seg1, seg2, contiguous=False)``.
        * ``ADMEMB`` measured by
          ``contour.axmemb(seg1, seg2, contiguous=True, admembOpt=True)``.

    .. note::
        * In c-space, segs with consecutively repeated elements are not
          possible, thus similarity values with such segs are excluded from
          CAS, CASV, CCV1, CCV2, CSIM, and ACMEMB,
        * The values of ADMEMB is generated with the optimization
          ``admembOpt=True``, thus the similarity value differs from
          that of Marvin's original ADMEMB.

    The values for these keys are also dicts, each of which comprises
    pairs of seg (NF) and similarity value. These key/value pairs are
    ordered in the dict according to the similarity value from high to low.
    Further, those segs that have the same similarity value are ordered by the
    cardinality, the lexicographic order, and the number of repeated elements.

    For example, the key seg (0, 2, 1, 3) is associated with a dict as
    follows::

        {'CAS': {(0, 3, 1, 2): 1.0,
                 (1, 2, 0, 3): 1.0,
                 ...
                 (1, 0, 1, 0): 0.0},
         'CASV': {(0, 1, 3, 2): 1.0,
                  (0, 2, 3, 1): 1.0,
                  ...
                  (3, 2, 1, 0): 0.3333333333333333},
         'CCV1': {(0, 1, 3, 2): 1.0,
                  (1, 0, 2, 3): 1.0,
                  ...
                  (3, 2, 1, 0): 0.1},
         'CCV2': {(0, 1, 3, 2): 1.0,
                  (1, 0, 2, 3): 1.0,
                  ...
                  (3, 2, 1, 0): 0.16666666666666666},
         'CSIM': {(0, 1, 2, 3): 0.8333333333333334,
                  (0, 3, 1, 2): 0.8333333333333334),
                  ...
                  (1, 0, 1, 0): 0.0},
         'DSIM': {(0, 1, 2, 3): 0.8333333333333334,
                  (0, 3, 1, 2): 0.8333333333333334,
                  ...
                  (1, 1, 1, 0): 0.0}
         'ACMEMB': {(0, 1, 3, 2), 0.8636363636363636,
                    (1, 0, 2, 3), 0.8636363636363636,
                    ...
                    (2, 1, 0), 0.26666666666666666},
         'ADMEMB': {(1, 0, 3, 2), 0.8333333333333334,
                    (2, 0, 3, 1), 0.8333333333333334,
                    ...
                    (1, 1, 1, 0), 0.16666666666666666}}

    :param segLists: lists of segs ordered by the cardinality.
    :param dctSeg: mapping of seg profiles.
    :type segLists: 2D list
    :type dctSeg: dict
    :return: nested dict for all the segs associated with dicts for
        the similarity measuring functions. Each of the inner dicts comprises
        pairs of a seg key and a similarity value, which are ordered by the
        similarity value from high to low.
    :rtype: dict
    """
    # Join the nested lists.
    segs = [s for segList in segLists for s in segList]
    segs = segs[2:]  # Remove the two-element segs.

    dct = {}  # dict to add elements in the parallel processes.

    pool = Pool(processes=c.MAX_PROCESSES)
    for s in segs:
        pool.apply_async(func=workerSimilaritySeg,
                         args=(s, segs, dctSeg),
                         callback=lambda r: dct.update(r))
    pool.close()
    pool.join()

    return dct


def mapSimilaritySC():
    """
    Return the mapping of SC pairs with the similarity value.

    The mapping is a nested dict::

        {PF: {"ICVSIM": {PF: simVal, ...},
              "RECREL": {PF: simVal, ...}}}

    The keys of the nested dicts refer to the functions used to measure the
    similarity between every SC and every other SC of cardinalities 3
    through 9:

        * ``ICVSIM`` measured by ``pcsets.relation(s1, s2, raw=False)``.
        * ``RECREL`` measured by ``pcsets.recrel(s1, s2, raw=False)``.

    The values for these keys are also dicts, each of which comprises
    pairs of SC (PF) and similarity value. These key/value pairs are
    ordered in the dict according to the similarity value from high to low.
    Further, those SCs that have the same similarity value are ordered by the
    cardinality, the lexicographic order, and the number of repeated elements.

    For example, the key PF (0, 1, 4, 8) (SC4-19) is associated with a dict as
    follows::

        {'ICVSIM': {(0, 1, 3, 4, 8): 0.8682670156122432,
                    (0, 1, 4, 5, 8): 0.8682670156122432,
                    ...
                    (0, 2, 4, 6, 8, 10): 0.24756361025839854}},
         'RECREL': {PLACEHOLDER}}

    :return: nested dict for all the SCs associated with dicts for
        the similarity measuring functions. Each of the inner dicts comprises
        pairs of a SC key and a similarity value, which are ordered by the
        similarity value from high to low.
    :rtype: dict
    """
    # Create a list of PFs for the cardinalities between 3 and 9 inclusive.
    pfs = [pf for pfList in makePFLists() for pf in pfList]

    dct = {}  # dict to add elements in the parallel processes.

    pool = Pool(processes=c.MAX_PROCESSES)
    for pf in pfs:
        pool.apply_async(func=workerSimilaritySC,
                         args=(pf, pfs),
                         callback=lambda r: dct.update(r))
    pool.close()
    pool.join()

    return dct


def mapSCProbTable():
    pass


def mapSimilarityBCSet():
    pass


def mapModels():
    pass


def makeDctSegclass(segclassLists, switch):
    """Return the dict of segclasses for the catalog."""
    filename = os.path.join(os.path.dirname(__file__),
                            "pickles/dct_segclass.pickle")
    if switch:  # Write a new dict to a pickle file.
        print("Making dict for segclass profiles started...")
        dctSegclass = mapSegclasses(segclassLists)
        with open(filename, "wb") as outfile:
            pickle.dump(dctSegclass, outfile, pickle.HIGHEST_PROTOCOL)
        print("Making dict for segclass profiles completed.")
    else:      # Read the existing dict from a pickle file.
        with open(filename, "rb") as f:
            dctSegclass = pickle.load(f)
    return dctSegclass


def makeDctSeg(segLists, dctSegclass, switch):
    """Return the dict of segments for the catalog."""
    filename = os.path.join(os.path.dirname(__file__),
                            "pickles/dct_seg.pickle")
    if switch:  # Write a new dict to a pickle file.
        print("Making dict for seg profiles started...")
        dctSeg = mapSegs(segLists, dctSegclass)
        with open(filename, "wb") as outfile:
            pickle.dump(dctSeg, outfile, pickle.HIGHEST_PROTOCOL)
        print("Making dict for seg profiles completed.")
    else:       # Read the existing dict from a pickle file.
        with open(filename, "rb") as f:
            dctSeg = pickle.load(f)
    return dctSeg


def makeDctSimilaritySegclass(segclassLists, dctSegclass, switch):
    """
    Return the dict for the key "similaritySegclass" in the catalog.

    :param segclassLists: Nested list of segclasses.
    :param dctSegclass: segclass profiles.
    :param switch: indicate whether to newly generate a dict.
    :type segclassLists: list
    :type dctSegclass: dict
    :type switch: bool
    :return: segclasses mapped with every other segclasses based on
        the similarity values.
    :rtype: dict
    """
    filename = os.path.join(os.path.dirname(__file__),
                            "pickles/dct_similarity_segclass.pickle")
    if switch:  # Write a new dict to a pickle file.
        print("Making dict for segclass similarity started...")
        dctSimilaritySegclass = mapSimilaritySegclass(segclassLists,
                                                      dctSegclass)
        with open(filename, "wb") as outfile:
            pickle.dump(dctSimilaritySegclass, outfile,
                        pickle.HIGHEST_PROTOCOL)
        print("Making dict for segclass similarity completed.")
    else:       # Read the existing dict from a pickle file.
        with open(filename, "rb") as f:
            dctSimilaritySegclass = pickle.load(f)
    return dctSimilaritySegclass


def makeDctSimilaritySeg(segLists, dctSeg, switch):
    """
    Return the dict for the key "similaritySeg" in the catalog.

    :param segLists: Nested list of segs.
    :param dctSeg: seg profiles.
    :param switch: indicate whether to newly generate a dict.
    :type segLists: list
    :type dctSeg: dict
    :type switch: bool
    :return: segs mapped with every other segs based on the similarity values.
    :rtype: dict
    """
    filename = os.path.join(os.path.dirname(__file__),
                            "pickles/dct_similarity_seg.pickle")
    if switch:  # Write a new dict to a pickle file.
        print("Making dict for seg similarity started...")
        dctSimilaritySeg = mapSimilaritySeg(segLists, dctSeg)
        with open(filename, "wb") as outfile:
            pickle.dump(dctSimilaritySeg, outfile, pickle.HIGHEST_PROTOCOL)
        print("Making dict for seg similarity completed.")
    else:  # Read the existing dict from a pickle file.
        with open(filename, "rb") as f:
            dctSimilaritySeg = pickle.load(f)
    return dctSimilaritySeg


def makeDctSimilaritySC(switch):
    """
    Return the dict for the key "similaritySC" in the catalog.

    :param switch: indicate whether to newly generate a dict.
    :type switch: bool
    :return: SCs mapped with every other SCs based on the similarity values.
    :rtype: dict
    """
    filename = os.path.join(os.path.dirname(__file__),
                            "pickles/dct_similarity_sc.pickle")
    if switch:  # Write a new dict to a pickle file.
        print("Making dict for SC similarity started...")
        dctSimilaritySC = mapSimilaritySC()
        with open(filename, "wb") as outfile:
            pickle.dump(dctSimilaritySC, outfile, pickle.HIGHEST_PROTOCOL)
        print("Making dict for SC similarity completed.")
    else:  # Read the existing dict from a pickle file.
        with open(filename, "rb") as f:
            dctSimilaritySC = pickle.load(f)
    return dctSimilaritySC


def makeDctSCProbTable():
    # Make entry "SCProbTable" to dctAll
    pass


def makeDctSimilarityBCSet():
    # Make entry "similarityBCSet" to dctAll
    pass


def makeDctModel():
    # Make entry "model" to dctAll
    pass


def makeCatalog(switches):
    """
    Make a pickle file for the database queries.

    :param switches: list of bools that indicates which dicts to create.
        The list items correspond with the dicts in the following order:

        * switches[0] = segclass
        * switches[1] = seg
        * switches[2] = similaritySegclass
        * switches[3] = similaritySeg
        * switches[4] = similaritySC
        * switches[5] = SCProbTable
        * switches[6] = similarityBCSet
        * switches[7] = model
        * switches[8] = catalog (consolidation of all the subdicts)

    :type switches: list
    """
    # Create all the possible segs and segclasses
    segLists, segclassLists = makeElements()

    # Make a dictionary for each query category.
    dctSegclass = makeDctSegclass(segclassLists, switches[0])
    dctSeg = makeDctSeg(segLists, dctSegclass, switches[1])
    dctSimilaritySegclass = makeDctSimilaritySegclass(segclassLists,
                                                      dctSegclass, switches[2])
    dctSimilaritySeg = makeDctSimilaritySeg(segLists, dctSeg, switches[3])
    dctSimilaritySC = makeDctSimilaritySC(switches[4])
    # dctSCProbTable = makeDctSCProbTable(params, switches[5])
    # dctSimilarityBCSet = makeDctSimilarityBCSet(params, switches[6])
    # dctModel = makeDctModels(params, switches[7])

    if switches[8]:
        # Make the parent dictionary for all the catalog entries.
        dctAll = {
            "segclass": dctSegclass,
            "seg": dctSeg,
            "similaritySegclass": dctSimilaritySegclass,
            "similaritySeg": dctSimilaritySeg,
            "similaritySC": dctSimilaritySC,
            # "SCProbTable": dctSCProbTable,
            # "similarityBCSet": dctSimilarityBCSet,
            # "model": dctModel
        }

        # Write the parent dict to a pickle file.
        with open("../pickles/catalog.pickle", "wb") as outfile:
            pickle.dump(dctAll, outfile, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    dcts = ["segclass",
            "seg",
            "similaritySegclass",
            "similaritySeg",
            "similaritySC",
            "SCProbTable",
            "similarityBCSet",
            "model",
            "catalog (consolidation of all the subdicts)"]
    answers = []
    for d in dcts:
        a = input("Generate dict for {0} (Y/N)? >>> ".format(d))
        answers.append(a.lower()[0] == "y")
    print()
    startTime = time.time()
    makeCatalog(answers)
    elapsed = str(datetime.timedelta(seconds=(time.time() - startTime)))
    print("\nDone!")
    print("Process time: {0}".format(elapsed))
