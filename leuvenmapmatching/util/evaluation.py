# encoding: utf-8
"""
leuvenmapmatching.util.evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Methods to help set up and evaluate experiments.

:author: Wannes Meert
:copyright: Copyright 2018 DTAI, KU Leuven and Sirris.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import logging
from dtaidistance.alignment import needleman_wunsch, best_alignment

from . import dist_latlon
MYPY = False
if MYPY:
    from ..map.base import BaseMap
    from typing import List, Tuple, Optional, Callable


logger = logging.getLogger("be.kuleuven.cs.dtai.mapmatching")


def route_mismatch_factor(map_con, path_pred, path_grnd, window=None, dist_fn=None):
    # type: (BaseMap, List[int], List[int], Optional[int], Optional[Callable]) -> Tuple[float, float, float, float]
    """Evaluation method from Newson and Krumm (2009).

    :math:`f = \frac{d_{-} + d_{+}}{d_0}`

    With :math:`d_{-}` the length that is erroneously subtracted,
    :math:`d_{+}` the length that is erroneously added, and :math:`d_0` the
    distance of the correct route.

    This function only supports connected states (thus not switching between states
    that are not connected (e.g. parallel roads).
    """
    if dist_fn is None:
        dist_fn = dist_latlon.distance
    _, matrix = needleman_wunsch(path_pred, path_grnd, window=window)
    print(matrix[:10, :10])
    algn, _, _ = best_alignment(matrix)
    print(algn[:10])
    d_plus = 0  # length erroneously added
    d_min = 0  # length erroneously subtracted
    d_zero = 0  # length of correct route
    cnt_matches = 0  # number of perfect matches
    cnt_mismatches = 0

    for pred_pi, grnd_pi in algn:
        pred_p = path_pred[pred_pi]
        grnd_p = path_grnd[grnd_pi]
        grnd_d = map_con.path_dist(grnd_p)
        d_zero += grnd_d
        if pred_p == grnd_p:
            cnt_matches += 1
        else:
            # print(f"Mismatch: {pred_p} != {grnd_p}")
            cnt_mismatches += 1
            pred_d = map_con.path_dist(pred_p)
            d_plus += pred_d
            d_min += grnd_d

    factor = (d_min + d_plus) / d_zero
    return factor, cnt_matches, cnt_mismatches, d_zero