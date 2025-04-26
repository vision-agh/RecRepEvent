# author: Nikola Zubic

import os
import sys
import numpy as np
from representations.utils.operations import MixedDensityEventStack

N_CHANNELS = 12


def get_optimized_representation(reshaped_return_data, num_events, height, width):
    window_indexes = [3, 1, 1, 2, 5, 3, 3, 4, 1, 6, 0, 0]
    functions = [
        "timestamp",
        "timestamp_pos",
        "timestamp_neg",
        "count_neg",
        "count_pos",
        "polarity",
        "timestamp",
        "count",
        "timestamp_pos",
        "count",
        "timestamp_pos",
        "timestamp_neg",
    ]
    aggregations = [
        "max",
        "sum",
        "mean",
        "sum",
        "mean",
        "variance",
        "variance",
        "sum",
        "mean",
        "sum",
        "sum",
        "sum",
    ]

    stack_size = N_CHANNELS
    stacking_type = ["SBN", "SBT"][
        0
    ]  # stacking based on number of events (SBN) or time (SBT)

    indexes_functions_aggregations = window_indexes, functions, aggregations

    transformation = MixedDensityEventStack(
        stack_size,
        num_events,
        height,
        width,
        indexes_functions_aggregations,
        stacking_type,
    )
    rep = transformation.stack(reshaped_return_data)

    return rep

"""
Best observation: {'window': 0, 'function': 'polarity', 'aggregation': 'variance', 'C_p': 0.}
Best observation: {'window': 3, 'function': 'timestamp_neg', 'aggregation': 'variance', 'C_p': 0.}
Best observation: {'window': 2, 'function': 'count_neg', 'aggregation': 'mean', 'C_p': 0.}
Best observation: {'window': 6, 'function': 'polarity', 'aggregation': 'sum', 'C_p': 0.}
Best observation: {'window': 5, 'function': 'count_pos', 'aggregation': 'mean', 'C_p': 0.}
Best observation: {'window': 6, 'function': 'count', 'aggregation': 'sum', 'C_p': 0.}
Best observation: {'window': 2, 'function': 'timestamp_pos', 'aggregation': 'mean', 'C_p': 0.}
Best observation: {'window': 5, 'function': 'count_neg', 'aggregation': 'mean', 'C_p': 0.}
Best observation: {'window': 1, 'function': 'timestamp_neg', 'aggregation': 'max', 'C_p': 0.}
Best observation: {'window': 0, 'function': 'timestamp_pos', 'aggregation': 'max', 'C_p': 0.}
Best observation: {'window': 4, 'function': 'timestamp', 'aggregation': 'max', 'C_p': 0.}
Best observation: {'window': 1, 'function': 'count', 'aggregation': 'mean', 'C_p': 0.}

Optimization without clipping, 2nd representation search.
"""


# def get_optimized_representation(reshaped_return_data, num_events, height, width):
#     window_indexes = [0, 3, 2, 6, 5, 6, 2, 5, 1, 0, 4, 1]
#     functions = [
#         "polarity",
#         "timestamp_neg",
#         "count_neg",
#         "polarity",
#         "count_pos",
#         "count",
#         "timestamp_pos",
#         "count_neg",
#         "timestamp_neg",
#         "timestamp_pos",
#         "timestamp",
#         "count",
#     ]
#     aggregations = [
#         "variance",
#         "variance",
#         "mean",
#         "sum",
#         "mean",
#         "sum",
#         "mean",
#         "mean",
#         "max",
#         "max",
#         "max",
#         "mean",
#     ]

#     stack_size = N_CHANNELS
#     stacking_type = ["SBN", "SBT"][
#         0
#     ]  # stacking based on number of events (SBN) or time (SBT)

#     indexes_functions_aggregations = window_indexes, functions, aggregations

#     transformation = MixedDensityEventStack(
#         stack_size,
#         num_events,
#         height,
#         width,
#         indexes_functions_aggregations,
#         stacking_type,
#     )
#     rep = transformation.stack(reshaped_return_data)

#     return rep




