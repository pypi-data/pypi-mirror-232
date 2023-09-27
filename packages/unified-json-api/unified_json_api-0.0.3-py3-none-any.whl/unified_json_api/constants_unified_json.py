from logger_local.LoggerComponentEnum import LoggerComponentEnum

class ConstantsUnifiedJson:

    UNIFIED_JSON_COMPONENT_ID = 214
    UNIFIED_JSON_COMPONENT_NAME = "unified-json-api-python-pacakge"
    DEVELOPER_EMAIL = "tal.g@circ.zone"

    OBJECT_FOR_LOGGER_CODE = {
        'component_id': UNIFIED_JSON_COMPONENT_ID,
        'component_name': UNIFIED_JSON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': DEVELOPER_EMAIL
    }

    OBJECT_FOR_LOGGER_TEST = {
        'component_id': UNIFIED_JSON_COMPONENT_ID,
        'component_name': UNIFIED_JSON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'developer_email': DEVELOPER_EMAIL
    }
