# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import gzip as _gzip
import io


from .abc import Codec
from .compat import ensure_ndarray, ensure_contiguous_ndarray, PY2


class GZip(Codec):
    """Codec providing gzip compression using zlib via the Python standard library.

    Parameters
    ----------
    level : int
        Compression level.

    """

    codec_id = 'gzip'

    def __init__(self, level=1):
        self.level = level

    def encode(self, buf):

        # normalise inputs
        buf = ensure_contiguous_ndarray(buf)
        if PY2:  # pragma: py3 no cover
            # view as u1 needed on PY2
            # ref: https://github.com/zarr-developers/numcodecs/pull/128#discussion_r236786466
            buf = buf.view('u1')

        # do compression
        compressed = io.BytesIO()
        with _gzip.GzipFile(fileobj=compressed,
                            mode='wb',
                            compresslevel=self.level) as compressor:
            compressor.write(buf)

        try:
            compressed = compressed.getbuffer()
        except AttributeError:  # pragma: py3 no cover
            compressed = compressed.getvalue()

        return ensure_ndarray(compressed)

    # noinspection PyMethodMayBeStatic
    def decode(self, buf, out=None):

        # normalise inputs
        buf = ensure_contiguous_ndarray(buf)

        # do decompression
        buf = io.BytesIO(buf)
        with _gzip.GzipFile(fileobj=buf, mode='rb') as decompressor:
            if out is not None:
                out = ensure_contiguous_ndarray(out)
                decompressor.readinto(out)
                if decompressor.read(1) != b'':
                    raise ValueError("Unable to fit data into `out`")
            else:
                out = ensure_ndarray(decompressor.read())

        # handle destination - Python standard library zlib module does not
        # support direct decompression into buffer, so we have to copy into
        # out if given
        return out
