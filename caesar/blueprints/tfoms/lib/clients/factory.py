# -*- coding: utf-8 -*-


class ClientFactory(object):

    @staticmethod
    def create(region_code, url):
        if region_code == 'pnz':
            from .pnz import TFOMSClient
        elif region_code == 'spb':
            from .spb import TFOMSClient
        else:
            raise NotImplementedError(u'Client for "{0}" is not implemented'.format(region_code))
        return TFOMSClient(url)
