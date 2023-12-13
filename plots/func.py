#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Set of functions used to prepare or get information from data for plotly figures.
"""

from scipy.stats import linregress

def get_regression_line_stats(x, y, all_result=False, hypothesis='two-sided'):
    """
    Function to compute the linear least-squares regression for two sets
    of measurements x and y.

    x:              Array for x axis.
    y:              Array for y axis.
    all_result:     If True return an object with all regression details.
                    
    Return          a line containing the Pearson correlation value and
                    the p-value, which can be added as a legend in the
                    correlation plot.
    """
    result = linregress(x, y, alternative=hypothesis)
    r, p = result[2], result[3]
    display_line = f'Pearson coefficient: r={r:.2f}, p={p:.2f}'
    if all_result:
        return result
    else:
        return display_line
    
