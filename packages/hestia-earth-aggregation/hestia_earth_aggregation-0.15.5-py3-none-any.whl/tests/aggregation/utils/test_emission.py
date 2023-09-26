from hestia_earth.schema import SiteSiteType, TermTermType

from hestia_earth.aggregation.utils.emission import all_in_system_boundary


def test_all_in_system_boundary():
    product = {
        '@id': 'wheatGrain',
        'termType': TermTermType.CROP.value
    }
    siteType = SiteSiteType.CROPLAND.value
    term_ids = all_in_system_boundary(product, siteType)
    assert len(term_ids) == 57

    product = {
        '@id': 'ricePlantFlooded',
        'termType': TermTermType.CROP.value
    }
    siteType = SiteSiteType.CROPLAND.value
    term_ids = all_in_system_boundary(product, siteType)
    assert len(term_ids) == 58

    product = {
        '@id': 'meatBeefCattleLiveweight',
        'termType': TermTermType.ANIMALPRODUCT.value
    }
    siteType = SiteSiteType.ANIMAL_HOUSING.value
    term_ids = all_in_system_boundary(product, siteType)
    assert len(term_ids) == 29
