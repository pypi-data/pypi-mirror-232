"""
Flask-Tenable is a thin wrapper for pyTenable that enables the easy integration of pyTenable into flask applications.

To use the pyTenable objects app.config must contain:
    - TenableAD: TENABLE_AD_API_KEY
    - Downloads: TENABLE_DOWNLOADS_API_TOKEN
    - TenableIO: TENABLE_IO_ACCESS_KEY, TENABLE_IO_SECRET_KEY
    - Nessus: TENABLE_NESSUS_HOST, TENABLE_NESSUS_ACCESS_KEY, TENABLE_NESSUS_SECRET_KEY
    - TenableOT: TENABLE_OT_API_KEY
    - TenableSC: TENABLE_SC_HOST, TENABLE_SC_ACCESS_KEY, TENABLE_SC_SECRET_KEY
"""
from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, current_app
from tenable.ad import TenableAD
from tenable.dl import Downloads
from tenable.io import TenableIO
from tenable.nessus import Nessus
from tenable.ot import TenableOT
from tenable.sc import TenableSC

__all__ = [
    'Tenable'
]

# The pyTenable version this package is made for.
__version_tuple__ = (1, 4, 13)
__version__ = '.'.join(map(str, __version_tuple__))


@dataclass
class TenableConfig(object):
    """
    TenableConfig is a simple object that holds the configuration for the Tenable objects.
    """
    tenable_ad_api_key: str
    tenable_downloads_api_token: str
    tenable_io_access_key: str
    tenable_io_secret_key: str
    tenable_nessus_host: str
    tenable_nessus_access_key: str
    tenable_nessus_secret_key: str
    tenable_ot_api_key: str
    tenable_sc_host: str
    tenable_sc_access_key: str
    tenable_sc_secret_key: str

    instance: Tenable


def get_tenable(app: Flask = None) -> TenableConfig:
    app = app or current_app
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    return app.extensions['tenable']


class Tenable(object):
    """
    Tenable is a thin wrapper for pyTenable that enables the easy integration of pyTenable into flask applications.
    """
    _ad_instance: TenableAD = None
    _dl_instance: Downloads = None
    _io_instance: TenableIO = None
    _nessus_instance: Nessus = None
    _ot_instance: TenableOT = None
    _sc_instance: TenableSC = None

    def __init__(self, app: Flask = None, *args, **kwargs):
        """
        TenableConfig constructor.

        :param Flask app: The flask application to initialize the config with.
        """

        if app is not None:
            self.init_app(app, *args, **kwargs)

    def init_app(self, app, *args, **kwargs):
        """
        Initializes the TenableConfig object with the provided flask application.

        :param app: The flask application to initialize the config with.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['tenable'] = TenableConfig(
            tenable_ad_api_key=app.config.get('TENABLE_AD_API_KEY'),
            tenable_downloads_api_token=app.config.get('TENABLE_DOWNLOADS_API_TOKEN'),
            tenable_io_access_key=app.config.get('TENABLE_IO_ACCESS_KEY'),
            tenable_io_secret_key=app.config.get('TENABLE_IO_SECRET_KEY'),
            tenable_nessus_host=app.config.get('TENABLE_NESSUS_HOST'),
            tenable_nessus_access_key=app.config.get('TENABLE_NESSUS_ACCESS_KEY'),
            tenable_nessus_secret_key=app.config.get('TENABLE_NESSUS_SECRET_KEY'),
            tenable_ot_api_key=app.config.get('TENABLE_OT_API_KEY'),
            tenable_sc_host=app.config.get('TENABLE_SC_HOST'),
            tenable_sc_access_key=app.config.get('TENABLE_SC_ACCESS_KEY'),
            tenable_sc_secret_key=app.config.get('TENABLE_SC_SECRET_KEY'),
            instance=self
        )

    @property
    def ad(self) -> TenableAD:
        """
        Create or return a TenableAD instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_ad_api_key is None:
            raise RuntimeError('TENABLE_AD_API_KEY not configured.')
        if not self._ad_instance:
            self._ad_instance = TenableAD(api_key=current_app.extensions['tenable'].tenable_ad_api_key)
        return self._ad_instance

    @property
    def dl(self) -> Downloads:
        """
        Create or return a Downloads instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_downloads_api_token is None:
            raise RuntimeError('TENABLE_DOWNLOADS_API_TOKEN not configured.')
        if not self._dl_instance:
            self._dl_instance = Downloads(api_token=current_app.extensions['tenable'].tenable_downloads_api_token)
        return self._dl_instance

    @property
    def io(self) -> TenableIO:
        """
        Create or return a TenableIO instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_io_access_key is None:
            raise RuntimeError('TENABLE_IO_ACCESS_KEY not configured.')
        if current_app.extensions['tenable'].tenable_io_secret_key is None:
            raise RuntimeError('TENABLE_IO_SECRET_KEY not configured.')
        if not self._io_instance:
            self._io_instance = TenableIO(
                access_key=current_app.extensions['tenable'].tenable_io_access_key,
                secret_key=current_app.extensions['tenable'].tenable_io_secret_key
            )
        return self._io_instance

    @property
    def nessus(self) -> Nessus:
        """
        Create or return a Nessus instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_nessus_host is None:
            raise RuntimeError('TENABLE_NESSUS_HOST not configured.')
        if current_app.extensions['tenable'].tenable_nessus_access_key is None:
            raise RuntimeError('TENABLE_NESSUS_ACCESS_KEY not configured.')
        if current_app.extensions['tenable'].tenable_nessus_secret_key is None:
            raise RuntimeError('TENABLE_NESSUS_SECRET_KEY not configured.')
        if not self._nessus_instance:
            self._nessus_instance = Nessus(
                url=f"https://{current_app.extensions['tenable'].tenable_nessus_host}",
                access_key=current_app.extensions['tenable'].tenable_nessus_access_key,
                secret_key=current_app.extensions['tenable'].tenable_nessus_secret_key
            )
        return self._nessus_instance

    @property
    def ot(self) -> TenableOT:
        """
        Create or return a TenableOT instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_ot_api_key is None:
            raise RuntimeError('TENABLE_OT_API_KEY not configured.')
        if not self._ot_instance:
            self._ot_instance = TenableOT(api_key=current_app.extensions['tenable'].tenable_ot_api_key)
        return self._ot_instance

    @property
    def sc(self) -> TenableSC:
        """
        Create or return a TenableSC instance.
        """
        if not hasattr(current_app, 'extensions') or 'tenable' not in current_app.extensions:
            raise RuntimeError('Tenable not initialized.')
        if current_app.extensions['tenable'].tenable_sc_host is None:
            raise RuntimeError('TENABLE_SC_HOST not configured.')
        if current_app.extensions['tenable'].tenable_sc_access_key is None:
            raise RuntimeError('TENABLE_SC_ACCESS_KEY not configured.')
        if current_app.extensions['tenable'].tenable_sc_secret_key is None:
            raise RuntimeError('TENABLE_SC_SECRET_KEY not configured.')
        if not self._sc_instance:
            self._sc_instance = TenableSC(
                url=f"https://{current_app.extensions['tenable'].tenable_sc_host}",
                access_key=current_app.extensions['tenable'].tenable_sc_access_key,
                secret_key=current_app.extensions['tenable'].tenable_sc_secret_key
            )
        return self._sc_instance
