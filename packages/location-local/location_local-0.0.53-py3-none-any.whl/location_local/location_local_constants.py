from logger_local.LoggerComponentEnum import LoggerComponentEnum


class LocationLocalConstants:
    LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 113
    LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'location local python package'
    OBJECT_FOR_LOGGER_CODE = {
        'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
        'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': 'tal.g@circ.zone'
    }

    OBJECT_FOR_LOGGER_TEST = {
        'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
        'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'developer_email': 'tal.g@circ.zone'
    }

    UNKNOWN_LOCATION_ID = 37522
    DEFAULT_NEGIHBORHOOD_NAME = 'Default Neighborhood'
    DEFAULT_COUNTY_NAME = 'Default County'
    DEFAULT_REGION_NAME = 'Default Region'
    DEFAULT_STATE_NAME = 'Default State'
    DEFAULT_COUNTRY_NAME = 'UNKNOWN'
    DEFAULT_ADDRESS_LOCAL_LANGUAGE = 'Default Address Local Language'
    DEFAULT_ADDRESS_ENGLISH = 'Default Address English'
    DEFAULT_POSTAL_CODE = 'Default Postal Code'
    DEFAULT_PLUS_CODE = 'Default Plus Code'
    DEFAULT_COORDINATE = {'latitude': 0.0, 'longitude': 0.0}
    LOCATION_SCHEMA_NAME = 'location'
    LOCATION_TABLE_NAME = 'location_table'
    LOCATION_VIEW_NAME = 'location_view'
    COUNTRY_TABLE_NAME = 'country_table'
    COUNTRY_ML_TABLE_NAME = 'country_ml_table'
    COUNTRY_ML_VIEW_NAME = 'country_ml_view'
    COUNTY_TABLE_NAME = 'county_table'
    COUNTY_ML_TABLE_NAME = 'county_ml_table'
    COUNTY_ML_VIEW_NAME = 'county_ml_view'
    NEIGHBORHOOD_TABLE_NAME = 'neighborhood_table'
    NEIGHBORHOOD_ML_TABLE_NAME = 'neighborhood_ml_table'
    NEIGHBORHOOD_ML_VIEW_NAME = 'neighborhood_ml_view'
    REGION_TABLE_NAME = 'region_table'
    REGION_ML_TABLE_NAME = 'region_ml_table'
    REGION_ML_VIEW_NAME = 'region_ml_view'
    STATE_TABLE_NAME = 'state_table'
    STATE_ML_TABLE_NAME = 'state_ml_table'
    STATE_ML_VIEW_NAME = 'state_ml_view'


