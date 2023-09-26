from hestia_earth.schema import PracticeJSONLD, PracticeStatsDefinition
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node


def _new_practice(data, value: float = None):
    node = PracticeJSONLD().to_dict()
    term = data.get('term') if isinstance(data, dict) else download_hestia(data)
    node['term'] = linked_node(term)
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = PracticeStatsDefinition.CYCLES.value
    return node
