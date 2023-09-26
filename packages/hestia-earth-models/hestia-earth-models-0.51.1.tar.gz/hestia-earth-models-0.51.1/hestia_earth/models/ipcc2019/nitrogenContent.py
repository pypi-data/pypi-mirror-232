from hestia_earth.schema import PropertyStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property, get_node_property, node_has_no_property
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": "crop",
            "value": "> 0",
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "dryMatter"}]
            }
        }]
    }
}
LOOKUPS = {
    "crop": [
        "IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes", "N_Content_AG_Residue", "N_Content_BG_Residue"
    ]
}
RETURNS = {
    "Products": [{
        "properties": [{
            "@type": "Property",
            "value": "",
            "statsDefinition": "modelled"
        }]
    }]
}
TERM_ID = 'nitrogenContent'
PROPERTY_KEY = 'dryMatter'
PRODUCT_COLUMN_MAPPING = {
    'aboveGroundCropResidueTotal': LOOKUPS['crop'][2],
    'belowGroundCropResidue': LOOKUPS['crop'][3]
}


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.MODELLED.value
    return prop


def _get_crop_value(crop_id: str, column: str):
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, crop_id, column), None)


# Single crop


def _get_single_product_value(crop_id: str, product_id: str):
    column = PRODUCT_COLUMN_MAPPING[product_id]
    return _get_crop_value(crop_id, column) if column else None


def _run_single_product(crop_residue_products: list, product: dict):
    crop_id = product.get('term', {}).get('@id')

    def run_product(product: dict):
        term_id = product.get('term', {}).get('@id')
        value = _get_single_product_value(crop_id, term_id)
        prop = _property(value) if value is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else product

    return non_empty_list(map(run_product, crop_residue_products))


def _should_run_single_crop_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    columns = list(PRODUCT_COLUMN_MAPPING.values())
    has_single_values = any(_get_crop_value(term_id, column) for column in columns)

    debugValues(product, model=MODEL, term=term_id, property=TERM_ID,
                has_single_values=has_single_values)

    return all([has_single_values])


# Multiple crops


def _multiple_crop_product_values(crop: dict, residue_id: str):
    term_id = crop.get('term', {}).get('@id')
    value = list_sum(crop.get('value'))
    dm = get_node_property(crop, PROPERTY_KEY).get('value', 0)
    yield_dm = _get_crop_value(term_id, LOOKUPS['crop'][0])
    n_content = _get_crop_value(term_id, PRODUCT_COLUMN_MAPPING[residue_id])
    ratio = _get_crop_value(term_id, LOOKUPS['crop'][1]) if residue_id == 'belowGroundCropResidue' else 1
    debugValues(crop, model=MODEL, term=residue_id,
                crop=term_id,
                dryMatter=dm,
                ratio_yield_dm=yield_dm,
                nitrogenContent=n_content,
                ratio=ratio)
    return (value * dm / 100 * yield_dm * (ratio or 1), n_content) if n_content is not None else None


def _run_multiple_products(crop_residue_products: list, crop_products: list):
    def run_product(product: dict):
        term_id = product.get('term', {}).get('@id')
        values = non_empty_list([_multiple_crop_product_values(p, term_id) for p in crop_products])
        total = sum([value for value, _ in values])
        value = sum([value * n_content for value, n_content in values]) / total if total > 0 else None
        prop = _property(value) if value is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None

    return non_empty_list(map(run_product, crop_residue_products))


def _should_run_multiple_crop_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value', [0]))
    prop = get_node_property(product, PROPERTY_KEY).get('value')
    yield_dm = _get_crop_value(term_id, LOOKUPS['crop'][0])

    debugValues(product, model=MODEL, term=term_id, property=TERM_ID,
                dryMatter=prop,
                yield_dm=yield_dm)

    return all([value > 0, prop, yield_dm is not None])


def _should_run_product(product: dict):
    return product.get('term', {}).get('@id') in PRODUCT_COLUMN_MAPPING


def _should_run(cycle: dict):
    products = list(filter(node_has_no_property(TERM_ID), cycle.get('products', [])))
    crop_residue_products = list(filter(_should_run_product, products))

    has_crop_residue_products = len(crop_residue_products) > 0

    crop_products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)

    single_crops = list(filter(_should_run_single_crop_product, crop_products))
    single_crop = single_crops[0] if len(single_crops) == 1 else None
    has_single_crop = single_crop is not None

    multiple_crops = list(filter(_should_run_multiple_crop_product, crop_products))
    has_multiple_crops = len(multiple_crops) > 1

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_crop_residue_products=has_crop_residue_products)

    should_run = all([has_crop_residue_products, has_single_crop or has_multiple_crops])

    for product in crop_residue_products:
        term_id = product.get('term', {}).get('@id')
        logRequirements(cycle, model=MODEL, term=term_id, property=TERM_ID,
                        has_single_crop=has_single_crop,
                        has_multiple_crops=has_multiple_crops)
        logShouldRun(cycle, MODEL, term_id, should_run, property=TERM_ID)

    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, crop_residue_products, single_crop, multiple_crops


def run(cycle: dict):
    should_run, crop_residue_products, single_crop, multiple_crops = _should_run(cycle)
    return (
        _run_single_product(crop_residue_products, single_crop) if single_crop else
        _run_multiple_products(crop_residue_products, multiple_crops)
    ) if should_run else []
