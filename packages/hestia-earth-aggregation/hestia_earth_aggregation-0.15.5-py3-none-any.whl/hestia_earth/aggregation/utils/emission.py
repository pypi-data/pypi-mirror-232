from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name

_COLUMN_NAME = 'inHestiaDefaultSystemBoundary'
_ALLOW_ALL = 'all'


def is_in_system_boundary(term_id: str):
    lookup = download_lookup('emission.csv')
    value = get_table_value(lookup, 'termid', term_id, column_name(_COLUMN_NAME))
    # handle numpy boolean
    return not (not value)


def all_in_system_boundary(term: dict, site_type: str):
    lookup = download_lookup('emission.csv')
    # find all emissions in system boundary
    term_ids = list(filter(is_in_system_boundary, list(lookup.termid)))
    # filter emissions allowed on product/siteType

    def is_allowed(emission_term_id: str, column: str, condition: str):
        values = get_table_value(lookup, 'termid', emission_term_id, column_name(column))
        values = (values or _ALLOW_ALL).split(';')
        return True if _ALLOW_ALL in values or not condition else condition in values

    return [
        term_id for term_id in term_ids if all([
            is_allowed(term_id, 'siteTypesAllowed', site_type),
            is_allowed(term_id, 'productTermTypesAllowed', term.get('termType')),
            is_allowed(term_id, 'productTermIdsAllowed', term.get('@id'))
        ])
    ]


_DEFAULT_TIER = EmissionMethodTier.TIER_1.value


def get_method_tier(emissions: list):
    values = set([e.get('methodTier', _DEFAULT_TIER) for e in emissions])
    return list(values)[0] if len(values) == 1 else _DEFAULT_TIER
