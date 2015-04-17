#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
from urlparse import urlparse
import urllib2
import binascii
import uuid
import random
import time


class UrlUtil:

    def __init__(self):
        pass

    @staticmethod
    def get_crc_by_url(url, work_dir=None):

        if work_dir is None:
            work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tmp'))
        try:
            path = urlparse(url)
        except:
            return -1
        try:
            file = urllib2.urlopen(url, timeout=5)
        except:
            return -2
        # +TODO: We must generate unique name for each file
        filename = work_dir + str(uuid.uuid4()) #os.path.basename(path.path)
        try:
            with open(filename, 'wb') as f:
                rd = file.read()
                f.write(rd)

            with open(filename, 'rb') as fr:
                content = fr.read()
                raw_crc = binascii.crc32(content)
        except IOError:
            return -3

        if raw_crc < 0:
            raw_crc = raw_crc & 0xffffffff
        crc = hex(raw_crc)
        try:
            pass
            os.remove(filename)
        except (IOError, OSError):
            pass
        return crc

