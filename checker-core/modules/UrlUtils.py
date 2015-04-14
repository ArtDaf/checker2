#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
from urlparse import urlparse
import urllib2
import binascii
import random
import time


class UrlUtil:

    @staticmethod
    def getCrcUrl(url, workdir):
        try:
            path = urlparse(url)
        except:
            return 0x00000001
        try:
            file = urllib2.urlopen(url, timeout=5)
        except:
            return 0x00000002
        filename = workdir + os.path.basename(path.path)
        try:
            with open(filename, 'wb') as f:
                rd = file.read()
                f.write(rd)

            with open(filename, 'rb') as fr:
                content = fr.read()
                rawCrc = binascii.crc32(content)
        except IOError:
            return 0x00000003

        if rawCrc < 0:
            rawCrc = rawCrc & 0xffffffff
        crc = hex(rawCrc)
        try:
            pass
            os.remove(filename)
        except (IOError, OSError):
            pass
        return crc

