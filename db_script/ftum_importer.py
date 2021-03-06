import logging
import os
import urllib
from decimal import Decimal
try:
    import json
except ImportError:
    import simplejson as json

from knowledge_base.models import Funder,FunderFamily
from db_script.funder_family_initializer import FunderFamilyInitializer

JSON_ENDPOINT = "http://reporting.sunlightfoundation.com/outside-spending/API/committees/"
FTUM_BASE = "http://reporting.sunlightfoundation.com%s"

log = logging.getLogger('db_script.ftum_importer')

class FTUMImporter():
    def __init__(self,url=JSON_ENDPOINT):
        self.download_url = JSON_ENDPOINT
        self.jdict = self.download_json()
        self.funder_list = []
    def download_json(self):
        log.info('downloading FTUM json')
        page = urllib.urlopen(self.download_url)
        log.info('...downloaded')
        return json.loads(page.read())['committees']
    def upload_data(self):
        log.info('uploading FTUM data to funder models')
        for committee in self.jdict:
            fec_id = committee['fec_id']
            name = committee['name']
            log.info('updating funder %s'%(fec_id))
            try:
                funder = Funder.objects.get(FEC_id=fec_id)
            except Funder.DoesNotExist:
                log.warning('...creating funder %s (not in db yet!)'%(fec_id,))
                funder = Funder(FEC_id=fec_id,name=name)
                funder.save()
            funder.total_contributions = Decimal(
                    str(committee['total_contributions']))
            funder.cash_on_hand = Decimal(
                    str(committee['cash_on_hand']))
            funder.total_independent_expenditures = Decimal(
                    str(committee['total_independent_expenditures']))
            funder.ie_negative_percent = committee['ie_negative_percent']
            funder.ie_positive_percent = committee['ie_positive_percent']
            funder.ie_opposes_dems = Decimal(
                    str(committee['ie_opposes_dems']))
            funder.ie_opposes_reps = Decimal(
                    str(committee['ie_opposes_reps']))
            funder.ie_supports_dems = Decimal(
                    str(committee['ie_supports_dems']))
            funder.ie_supports_reps = Decimal(
                    str(committee['ie_supports_reps']))
            funder.ftum_url = FTUM_BASE%(committee['href'],)
            funder.save()
            self.funder_list.append(funder)
    def update_families(self):
        log.info('updating funder families')
        for f in self.funder_list:
            if not f.funder_family:
                ffi = FunderFamilyInitializer(f)
                ffi.assign_new_funder_family()
            funder_family = f.funder_family
            log.info('updating funder family %s'%(funder_family.primary_FEC_id,))
            funder_family.update_values()
