# -*- coding: utf-8 -*-
#
# Syncopy object simple summary statistics (mean, std, ...)
#


# Builtin/3rd party package imports
import numpy as np
import logging
import platform

# Local imports
# from .selectdata import _get_selection_size
from syncopy.shared.parsers import data_parser
from syncopy.shared.errors import SPYValueError, SPYWarning
from syncopy.statistics.compRoutines import NumpyStatDim
from syncopy.shared.kwarg_decorators import unwrap_select, detect_parallel_client

__all__ = ["mean", "std", "var", "median", "itc"]


@unwrap_select
@detect_parallel_client
def mean(spy_data, dim, keeptrials=True, **kwargs):
    """
    Calculates the average along arbitrary dimensions of a Syncopy
    data object ``spy_data``.

    Additional trial averaging can be performed with ``keeptrials=False``.
    Standalone (only) trial averaging can only be done sequentially
    and requires ``dim='trials'``.

    Parameters
    ----------
    spy_data : Syncopy data object
        The object where an average is to be computed
    dim : str
        Dimension label over which to calculate the statistic.
        Must be present in the ``spy_data`` object,
        e.g. 'channel' or 'trials'
    keeptrials : bool
        Set to ``False`` to trigger additional trial averaging
        Has no effect if ``dim='trials'``.

    Returns
    -------
    res : Syncopy data object
        New object with the desired dimension averaged out

    """

    # call general backend function with desired operation
    return _statistics(spy_data, operation="mean", dim=dim, keeptrials=keeptrials, **kwargs)


@unwrap_select
@detect_parallel_client
def std(spy_data, dim, keeptrials=True, **kwargs):
    """
    Calculates the standard deviation along arbitrary dimensions
    of a Syncopy data object ``spy_data``.

    Additional trial averaging can be performed with ``keeptrials=False``
    after the standard deviation got calculated.

    Parameters
    ----------
    spy_data : Syncopy data object
        The object where a standard deviation is to be computed
    dim : str
        Dimension label over which to calculate the statistic.
        Must be present in the ``spy_data`` object,
        e.g. 'channel' or 'trials'
    keeptrials : bool
        Set to ``False`` to trigger additional trial averaging.
        Has no effect if ``dim='trials'``.

    Returns
    -------
    res : Syncopy data object
        New object with the desired dimension averaged out

    """

    # call general backend function with desired operation
    return _statistics(spy_data, operation="std", dim=dim, keeptrials=keeptrials, **kwargs)


@unwrap_select
@detect_parallel_client
def var(spy_data, dim, keeptrials=True, **kwargs):
    """
    Calculates the variance along arbitrary dimensions of a Syncopy
    data object ``spy_data``.

    Additional trial averaging can be performed with ``keeptrials=False``
    after the variance got calculated.

    Parameters
    ----------
    spy_data : Syncopy data object
        The object where a variance is to be computed.
    dim : str
        Dimension label over which to calculate the statistic.
        Must be present in the ``spy_data`` object,
        e.g. 'channel' or 'trials'.
    keeptrials : bool
        Set to ``False`` to trigger additional trial averaging.
        Has no effect if ``dim='trials'``.

    Returns
    -------
    res : Syncopy data object
        New object with the desired dimension averaged out

    """

    # call general backend function with desired operation
    return _statistics(spy_data, operation="var", dim=dim, keeptrials=keeptrials, **kwargs)


@unwrap_select
@detect_parallel_client
def median(spy_data, dim, keeptrials=True, **kwargs):
    """
    Calculates the median along arbitrary dimensions of a
    Syncopy data object ``spy_data``.

    Additional trial averaging can be performed with ``keeptrials=False``
    after the median got calculated.

    Parameters
    ----------
    spy_data : Syncopy data object
        The object where a median is to be computed.
    dim : str
        Dimension label over which to calculate the statistic.
        Must be present in the ``spy_data`` object,
        e.g. 'channel' or 'trials'
    keeptrials : bool
        Set to ``False`` to trigger additional trial averaging.
        Has no effect if ``dim='trials'``.

    Returns
    -------
    res : Syncopy data object
        New object with the median of the desired dimension

    """

    # call general backend function with desired operation
    return _statistics(spy_data, operation="median", dim=dim, keeptrials=keeptrials, **kwargs)


@unwrap_select
def itc(spec_data, **kwargs):
    r"""
    Calculates the inter trial coherence for a
    SpectralData `spec_data` object, the input
    spectrum needs to be complex.
    The ITC of N trials is given by the length
    of the complex mean of vectors `z_i(f)`:

    .. math::
        1/N \sum_{i=1}^{N} z_i / |z_i|

    and have therefore values between 0 and 1.
    In the literature this measure is also often
    called the `Kuramoto order parameter`.

    For time-frequency spectra the trial sizes
    have to match exactly, and the output will
    be also additionally time dependent.

    Parameters
    ----------
    spec_data : :class:`~syncopy.SpectralData`
        The input spectrum, needs at least 2 trials

    Returns
    -------
    res  : :class:`~syncopy.SpectralData`
        The frequency dependent order parameters,
        the inter trial coherence
    """

    data_parser(spec_data, varname="spec_data", dataclass="SpectralData", empty=False)

    if spec_data.data.dtype != np.complex64 and spec_data.data.dtype != np.complex128:
        lgl = "complex valued spectra, set `output='fourier` in spy.freqanalysis!"
        act = "real valued spectral data"
        raise SPYValueError(lgl, "spec_data", act)

    logger = logging.getLogger("syncopy_" + platform.node())
    logger.debug(
        f"Computing intertrial coherence on SpectralData instance with shape {spec_data.data.shape}."
    )

    # takes care of remaining checks
    res = _trial_statistics(spec_data, operation="itc")
    write_log(spec_data, res, kwargs, op_name="itc")
    # attach cfg
    res.cfg.update(spec_data.cfg)
    return res


def _statistics(spy_data, operation, dim, keeptrials=True, **kwargs):

    """
    Entry point to calculate simple statistics (mean, std, ...) along arbitrary
    dimensions as long as the selected ``dim`` is contained
    within the ``dimord`` of the ``spy_data`` or ``dim='trials'``.
    Additional trial averaging can be triggered as usual with ``keeptrials=False``.

    For statistics over trials (``dim='trials'``), this function branches into the trial statistics
    function, which is NOT a CR as we need summary operations over trials,
    which is always sequential and out of scope of the ComputationalRoutines. However, as we require
    matching shapes for trial statistics, allocating the output shape is trivial.

    Parameters
    ----------
    spy_data : Syncopy data object
        The object where an average is to be computed
    operation : {'mean', 'std', 'var', 'median'}
        The statistical operation to perform
    dim : str
        Dimension label over which to calculate the statistic.
        Must be present in the ``spy_data`` object,
        e.g. 'channel' or 'trials'

    Returns
    -------
    res : Syncopy data object
        New object with the desired dimension averaged out

    See also
    --------
    NumpyStatDim: Compute class for parallel computation of trial-by-trial statistics
    _trial_statistics: Sequential computation of statistics over trials
    """

    # check that we have a non-empty Syncopy data object
    data_parser(spy_data, varname="spy_data", empty=False)

    if dim != "trials" and dim not in spy_data.dimord:
        lgl = f"one of {spy_data.dimord} or 'trials'"
        act = dim
        raise SPYValueError(lgl, "dim", act)

    log_dict = {
        "input": spy_data.filename,
        "operation": operation,
        "dim": dim,
        "keeptrials": keeptrials,
    }

    logger = logging.getLogger("syncopy_" + platform.node())
    logger.debug(
        f"Computing descriptive statistic {operation} on input from {spy_data.filename} along dimension {dim}, keeptrials={keeptrials}."
    )

    # If no active selection is present, create a "fake" all-to-all selection
    # to harmonize processing down the road (and attach `_cleanup` attribute for later removal)
    if spy_data.selection is None:
        spy_data.selectdata(inplace=True)
        spy_data.selection._cleanup = True
    else:
        # log also possible selections
        log_dict["selection"] = getattr(spy_data.selection, dim)

    # trial statistics
    if dim == "trials":
        if kwargs.get("parallel"):
            msg = "Trial statistics can be only computed sequentially, ignoring `parallel` keyword"
            SPYWarning(msg)
        out = _trial_statistics(spy_data, operation)

        # we have to attach the log here as no CR is involved
        # strip of non-sensical parameter
        log_dict.pop("keeptrials")
        write_log(spy_data, out, log_dict, "trial statistics")

    # any other statistic
    else:

        chan_per_worker = kwargs.get("chan_per_worker")
        if chan_per_worker is not None and "channel" in dim:
            msg = "Parallelization over channels not possible for channel averages"
            SPYWarning(msg)
            chan_per_worker = None

        axis = spy_data.dimord.index(dim)
        avCR = NumpyStatDim(operation=operation, axis=axis)

        # ---------------------------------
        # Initialize output and call the CR
        # ---------------------------------

        # initialize output object of same datatype
        out = spy_data.__class__(dimord=spy_data.dimord)

        avCR.initialize(
            spy_data,
            spy_data._stackingDim,
            keeptrials=keeptrials,
            chan_per_worker=chan_per_worker,
        )
        avCR.compute(spy_data, out, parallel=kwargs.get("parallel"), log_dict=log_dict)

    # revert helper all-to-all selection
    if hasattr(spy_data.selection, "_cleanup"):
        spy_data.cfg.pop("selectdata")
        spy_data.selection = None

    # re-attach config
    out.cfg.update(spy_data.cfg)

    return out


def _trial_statistics(in_data, operation="mean"):
    """
    Calculates simple statistics (mean, std, ...) over trials. No trivial
    parallelization is possible here, hence we fallback to good ol' sequential
    computing. For this to work, the shapes of all trials have to match exactly.

    To be still memory safe, the computations stream new data on a trial-by-trial
    basis and then 'manually' accumulate trial-by-trial to the result.
    """

    # If no active selection is present, create a "fake" all-to-all selection
    # to harmonize processing down the road (and attach `_cleanup` attribute for later removal)
    if in_data.selection is None:
        in_data.selectdata(inplace=True)
        in_data.selection._cleanup = True

    nTrials = len(in_data.selection.trials)
    if nTrials < 1:
        lgl = "at least 1 trial"
        act = f"got {nTrials} trials"
        raise SPYValueError(lgl, "in_data", act)

    # index 1st selected trial
    idx0 = in_data.selection.trial_ids[0]
    # we always have at least one (all-to-all) trial selection
    out_shape = in_data.selection.trials[idx0].shape

    # now look at the other ones
    for trl in in_data.selection.trials:
        if trl.shape != out_shape:
            lgl = "all trials to have the same shape"
            act = f"found trials of different shape: {out_shape} and {trl.shape}"
            raise SPYValueError(lgl, "in_data", act)

    # this is the target array, such that we will have
    # the data of 2 trials concurrently in memory
    result = np.zeros(out_shape, dtype=in_data.data.dtype.type)

    # --- now we can compute the desired statistic ---

    if operation == "mean":
        result = _trial_average(in_data, result)
    elif operation == "var":
        result = _trial_var(in_data, result)
    elif operation == "std":
        result = np.sqrt(_trial_var(in_data, result))
    elif operation == "itc":
        # itc is only available for SpectralData
        # ..get's checked in `spy.itc` above
        result = _trial_circ_average(in_data, result)
        # average out tapers (if any)
        taper_ax = in_data.dimord.index("taper")
        result = np.mean(result, axis=taper_ax, keepdims=True)
        # now take the abs to get the resultant vector
        result = np.abs(result)
        # silence already digested taper selection
        in_data.selection._taper = None

    # there is no apparent clever way to achieve
    # this efficiently over multiple dimensions
    elif operation == "median":
        raise NotImplementedError("Trial median not supported at the moment")

    # --- Consctruct the single-trial(!) Syncopy output object

    out_data = in_data.__class__(data=result, dimord=in_data.dimord, samplerate=in_data.samplerate)

    # only 1 trial left, all trials had to have the same shape
    # so just copy from the 1st
    out_data.trialdefinition = in_data.selection.trialdefinition[0, :][None, :]

    # propagate the rest of the properties
    for prop in in_data.selection._dimProps:
        selection = getattr(in_data.selection, prop)
        if selection is not None:
            if np.issubdtype(type(selection), np.number):
                selection = [selection]
            setattr(out_data, prop, getattr(in_data, prop)[selection])

    # revert helper all-to-all selection
    if hasattr(in_data.selection, "_cleanup"):
        in_data.cfg.pop("selectdata")
        in_data.selection = None

    return out_data


def _trial_average(in_data, out_arr):
    """
    Straigthforward sequential trial average. Shape checking
    and dealing with selections is done in _trial_statistics.

    Parameters
    ----------
    in_data : Syncopy data object
        To get a fresh trial indexer instance, pointing to the trial arrays
    out_arr : np.ndarray
        The empty NumPy array of correct shape to collect the results
    """

    trials = in_data.selection.trials
    for trl in trials:
        out_arr += trl

    # normalize
    out_arr /= len(trials)

    return out_arr


def _trial_var(in_data, out_arr):
    """
    Sequential variance over trials. Shape checking
    and dealing with selections is done in _trial_statistics.

    Parameters
    ----------
    in_data : Syncopy data object
        To get a fresh trial indexer instance, pointing to the trial arrays
    out_arr : np.ndarray
        The empty NumPy array of correct shape to collect the results
    """

    # first we need the trial average
    average = np.zeros(out_arr.shape, dtype=out_arr.dtype)
    average = _trial_average(in_data, average)

    trials = in_data.selection.trials
    for trl in trials:
        # absolute value for complex numbers
        out_arr += np.abs(trl - average) ** 2

    # normalize
    out_arr /= len(trials)

    return out_arr


def _trial_circ_average(in_data, out_arr):
    """
    Sequential complex average on the unit circle, can be used for
    inter trial coherence (order parameter) or mean phase estimation.
    Shape checking and dealing with selections is done in `_trial_statistics`.

    Parameters
    ----------
    in_data : Syncopy data object of complex dtype, e.g. :class:`~syncopy.SpectralData`
        Complex valued data
    out_arr : np.ndarray
        The empty NumPy array of correct shape to collect the results
    """

    trials = in_data.selection.trials
    for trl in trials:
        # add unit vectors on complex plane
        out_arr += trl / np.abs(trl)

    # normalize
    out_arr /= len(trials)

    # and return complex resultant vector

    return out_arr


# -- Helpers --


def write_log(data, out, log_dict, op_name):
    """
    For trial statistics without CR we
    take care of the log here
    """
    # Copy log from source object and write header
    out._log = str(data._log) + out._log
    logHead = f"computed {op_name} with settings\n"
    logOpts = ""
    for k, v in log_dict.items():
        logOpts += "\t{key:s} = {value:s}\n".format(
            key=k,
            value=str(v) if len(str(v)) < 80 else str(v)[:30] + ", ..., " + str(v)[-30:],
        )
    out.log = logHead + logOpts


def _attach_stat_doc(orig_doc):
    """
    NOT USED ATM - could be useful for other method doc strings

    This is a helper to attach the full doc to the statistical methods in ContinuousData.
    Including the `select` and `parallel` sections from the kwarg decorators,
    which can/should only be applied once.

    It critically depends on the Syncopy object to be named ``spy_data`` and the
    dimension parameter to be named ``dim``
    """

    # the wrapper
    def _attach_doc(func):
        # delete the `spy_data` entries which
        # are not needed (got self in the methods)
        doc = orig_doc.replace(" ``spy_data``", "")
        idx1 = doc.find("spy_data")
        idx2 = doc.find("dim", idx1)
        doc = doc[:idx1] + doc[idx2:]

        func.__doc__ = doc
        return func

    return _attach_doc
