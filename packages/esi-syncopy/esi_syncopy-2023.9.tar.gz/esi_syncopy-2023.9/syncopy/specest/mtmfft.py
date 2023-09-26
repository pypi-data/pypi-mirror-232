# -*- coding: utf-8 -*-
#
# Spectral estimation with (multi-)tapered FFT
#

# Builtin/3rd party package imports
import numpy as np
from scipy import signal
import logging
import platform

# local imports
from ._norm_spec import _norm_spec, _norm_taper


def mtmfft(
    data_arr,
    samplerate,
    nSamples=None,
    taper="hann",
    taper_opt=None,
    demean_taper=False,
    ft_compat=False,
):
    """
    (Multi-)tapered fast Fourier transform. Returns
    full complex Fourier transform for each taper.
    Multi-tapering only supported with Slepian windwows (`taper="dpss"`).

    Parameters
    ----------
    data_arr : (N,) :class:`numpy.ndarray`
        Uniformly sampled multi-channel time-series data
        The 1st dimension is interpreted as the time axis
    samplerate : float
        Samplerate in Hz
    nSamples : int or None
        Absolute length of the (potentially to be padded) signals
        or `None` for no padding.
    taper : str or None
        Taper function to use, one of `scipy.signal.windows`
        Set to `None` for no tapering.
    taper_opt : dict or None
        Additional keyword arguments passed to the `taper` function.
        For multi-tapering with ``taper='dpss'`` set the keys
        `'Kmax'` and `'NW'`.
        For further details, please refer to the
        `SciPy docs <https://docs.scipy.org/doc/scipy/reference/signal.windows.html>`_
    demean_taper : bool
        Set to `True` to perform de-meaning after tapering
    ft_compat : bool
        Set to `True` to use Field Trip's normalization,
        which is NOT independent of the padding size

    Returns
    -------
    ftr : 3D :class:`numpy.ndarray`
         Complex output has shape ``(nTapers x nFreq x nChannels)``.
    freqs : 1D :class:`numpy.ndarray`
         Array of Fourier frequencies

    Notes
    -----
    For a (MTM) power spectral estimate average the absolute squared
    transforms across tapers:

    ``Sxx = np.real(ftr * ftr.conj()).mean(axis=0)``

    The FFT result is normalized such that this yields the
    spectral power. For a clean harmonic this will give a
    peak power of `A**2 / 2`, with `A` as harmonic amplitude.
    """

    # attach dummy channel axis in case only a
    # single signal/channel is the input
    if data_arr.ndim < 2:
        data_arr = data_arr[:, np.newaxis]

    # raw length without padding
    signal_length = data_arr.shape[0]
    if nSamples is None:
        nSamples = signal_length

    nChannels = data_arr.shape[1]

    freqs = np.fft.rfftfreq(nSamples, 1 / samplerate)
    nFreq = freqs.size

    # no taper is boxcar
    if taper is None:
        taper = "boxcar"

    if taper_opt is None:
        taper_opt = {}

    taper_func = getattr(signal.windows, taper)
    # only really 2d if taper='dpss' with Kmax > 1
    # here we take the actual signal lengths!
    windows = np.atleast_2d(taper_func(signal_length, **taper_opt))
    # normalize window with total (after padding) length
    windows = _norm_taper(taper, windows, nSamples)

    # Fourier transforms (nTapers x nFreq x nChannels)
    ftr = np.zeros((windows.shape[0], nFreq, nChannels), dtype="complex64")

    logger = logging.getLogger("syncopy_" + platform.node())
    logger.debug(
        f"Running mtmfft on {len(windows)} windows, data chunk has {nSamples} samples and {nChannels} channels."
    )

    for taperIdx, win in enumerate(windows):
        win = np.tile(win, (nChannels, 1)).T
        win *= data_arr
        # de-mean again after tapering - needed for Granger!
        if demean_taper:
            win -= win.mean(axis=0)
        ftr[taperIdx] = np.fft.rfft(win, n=nSamples, axis=0)
        # FT uses potentially padded length `nSamples`, which dilutes the power
        if ft_compat:
            ftr[taperIdx] = _norm_spec(ftr[taperIdx], nSamples, samplerate)
        # here the normalization adapts such that padding is NOT changing power
        else:
            ftr[taperIdx] = _norm_spec(
                ftr[taperIdx],
                signal_length * np.sqrt(nSamples / signal_length),
                samplerate,
            )

    return ftr, freqs


def _get_dpss_pars(tapsmofrq, nSamples, samplerate):

    """Helper function to retrieve dpss parameters from tapsmofrq"""

    # taper width parameter in sample units
    NW = tapsmofrq * nSamples / samplerate

    # from the minBw formula in `input_processors.process_taper`
    # Kmax is at least 1!
    Kmax = int(2 * NW - 1)  # optimal number of tapers

    # ..but NW can be 0.9999999999999999..
    # catch those floating point issues
    Kmax = Kmax if Kmax > 1 else 1

    return NW, Kmax
