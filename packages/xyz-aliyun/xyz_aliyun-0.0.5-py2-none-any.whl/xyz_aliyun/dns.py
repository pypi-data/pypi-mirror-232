# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
import os
import sys

from typing import List

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from .utils import get_setting


class DnsApi():

    def __init__(self):
        A = lambda c: get_setting('dns', c)
        config = open_api_models.Config(
            access_key_id=A('SECRET_ID'),
            access_key_secret=A('SECRET_KEY')
        )
        self.client = Alidns20150109Client(config)

    def get_domain_record(self, domain_name, record, **kwargs):
        r = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=domain_name,
            key_word=record,
            search_mode='EXACT',
            **kwargs
        )
        rs = self.client.describe_domain_records(r)
        drs = rs.body.domain_records.record
        return drs[0] if len(drs) == 1 else None

    def update_domain_record(self, record_id, record, value, type='A', **kwargs):
        r = alidns_20150109_models.UpdateDomainRecordRequest(
            record_id=record_id,
            rr=record,
            value=value,
            type=type,
            **kwargs
        )
        rs = self.client.update_domain_record(r)
        return rs
