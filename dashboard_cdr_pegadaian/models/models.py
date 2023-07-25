# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields, api, _, _lt, tools, exceptions
from odoo.osv import expression
from odoo.osv.expression import AND, TRUE_DOMAIN, normalize_domain
from odoo.tools import date_utils, lazy
from odoo.tools.misc import get_lang
from odoo.exceptions import UserError, ValidationError, AccessError
# import numpy as np
# from collections import defaultdict
# from threading import Thread
import datetime
# from odoo.addons.shipyard_v2.models import sync_ifs as sync_tools
import traceback
from google.cloud import bigquery
import re
import time
import os
import json
# from bson import json_util

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/opt/odoo/bigquery/odooabc-ltd-cf8c47caf62b.json"
# os.environ['LD_LIBRARY_PATH'] = "/opt/oracle/instantclient_21_6/"



class CdrDataRecord(models.Model):
    _name = 'cdr.data.record'
    _description = 'CDR Data Record'

    name = fields.Char()
    timestats = fields.Datetime()
    disconnect_time_ts = fields.Datetime()
    seq_num = fields.Float()
    calling_party_origin_address = fields.Char()
    requested_address = fields.Char()
    media_capability_requested = fields.Char()
    connected = fields.Boolean()
    releasing_party = fields.Char()
    release_q850 = fields.Char()
    release_sip = fields.Char()
    release_reason_internal = fields.Char()
    orig_party_type = fields.Char()
    term_party_type = fields.Char()
    orig_party_business_group_name = fields.Char()
    term_party_business_group_name = fields.Char()
    orig_party_user_agent = fields.Char()
    term_party_user_agent = fields.Char()
    ic_seize_time = fields.Char()
    og_seize_time = fields.Char()
    ringing_time = fields.Char()
    connect_time = fields.Char()
    disconnect_time = fields.Char()
    duration = fields.Float()
    orig_party_subscriber_addr = fields.Char()
    term_party_subscriber_addr = fields.Char()

    def insert_cdr_data(self):
        client = bigquery.Client()
        table_id = "odooabc-ltd.test_fikri.dashboard-cdr"
        data = []
        now_str = str(tools.datetime.now())

        query = """
             SELECT combined.orig_addr,
                    combined.term_addr,
                    combined.timestats,
                    combined.msi_branch,
                    combined.duration_orig,
                    combined.duration_term,
                    combined.Kanwil,
                    combined.Area,
                    combined.releasing_party
                FROM (
                    SELECT cdr.orig_party_subscriber_addr AS orig_addr,
                        NULL AS term_addr,
                        cdr.timestats,
                        msi_orig.branch AS msi_branch,
                        SUM(cdr.duration) AS duration_orig,
                        NULL AS duration_term, -- Adding NULL as a placeholder for duration_term
                        msi_orig.kanwil AS Kanwil,
                        bd.area AS Area,
                        cdr.releasing_party
                    FROM cdr_data_record cdr
                    LEFT JOIN branch_msisdn msi_orig ON REGEXP_REPLACE(cdr.orig_party_subscriber_addr, '^0+', '') = msi_orig.msisdn
                    LEFT JOIN branch_detail bd ON msi_orig.branch = bd.nama_outlet 
                    WHERE cdr.term_party_subscriber_addr IS NULL
                    GROUP BY msi_orig.branch, orig_addr, cdr.timestats, msi_orig.kanwil, bd.area, cdr.releasing_party

                    UNION ALL

                    SELECT NULL AS orig_addr,
                        cdr.term_party_subscriber_addr AS term_addr,
                        cdr.timestats,
                        msi_term.branch AS msi_branch,
                        NULL AS duration_orig, -- Adding NULL as a placeholder for duration_orig
                        SUM(cdr.duration) AS duration_term,
                        msi_term.kanwil AS Kanwil,
                        bd.area AS Area,
                        cdr.releasing_party
                    FROM cdr_data_record cdr
                    LEFT JOIN branch_msisdn msi_term ON REGEXP_REPLACE(cdr.term_party_subscriber_addr, '^0+', '') = msi_term.msisdn
                    LEFT JOIN branch_detail bd ON msi_term.branch = bd.nama_outlet
                    WHERE cdr.orig_party_subscriber_addr IS NULL
                    GROUP BY msi_term.branch, term_addr, cdr.timestats, msi_term.kanwil, bd.area, cdr.releasing_party
                ) AS combined;

        """
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        # print(f'results {results}')
        for result in results:
            column = {}
            column['orig'] = result['orig_addr']
            column['term'] = result['term_addr']
            column['branch'] = result['msi_branch']
            column['duration'] = ''
            column['duration_orig'] = result['duration_orig']
            column['duration_term'] = result['duration_term']
            column['kanwil'] = result['kanwil']
            column['area'] = result['area']
            column['releasing_party'] = result['releasing_party']
            column['date'] = str(result['timestats'])
            column['timestats'] = now_str
            data.append(column)

        # print(f'DATA {data}')
        results = client.insert_rows_json(table_id, data)
        print(f'RESULT {results}')
        if results == []:
            print('BERHASIL')
        else:
            print('Error: {error}'.format(error=results))

class BranchMSISDN(models.Model):
    _name = 'branch.msisdn'
    _description = 'Branch MSI SDN'

    name = fields.Char()
    msisdn = fields.Char()
    branch = fields.Char()
    branch_colocation = fields.Char()
    role = fields.Char()
    kanwil = fields.Char()

class BranchData(models.Model):
    _name = 'branch.detail'
    _description = 'Branch Detail'

    name = fields.Char()
    
    kanwil = fields.Char()
    kode_kanwil = fields.Char()
    area = fields.Char()
    kode_area = fields.Char()
    cabang_induk = fields.Char()
    kode_induk = fields.Char()
    nama_outlet = fields.Char()
    kode_outlet = fields.Char()
    status = fields.Selection([
        ('cabang', 'Cabang'),
        ('upc', 'UPC'),
    ], string='Status')
    konven_syariah = fields.Selection([
        ('konven', 'Konven'),
        ('syariah', 'Syariah'),
    ], string='Konven/Syariah')
    nomor_telepon_utama = fields.Char()
    nomor_telepon_kedua = fields.Char()
    alamat = fields.Char()
    rt = fields.Char('RT')
    rw = fields.Char('RW')
    kode_pos = fields.Char()
    kode_kelurahan = fields.Char()
    kelurahan = fields.Char()
    kode_kecamatan = fields.Char()
    kecamatan = fields.Char()
    kode_kab_kota = fields.Char('Kode Kab/Kota')
    kab_kota = fields.Char('Kab/Kota')
    provinsi = fields.Char()