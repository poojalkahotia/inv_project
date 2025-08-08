from ..models import PurMaster

def get_party_report(from_date, to_date, partyname=None):
    filters = {'invdate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    return PurMaster.objects.filter(**filters).order_by('invdate')
