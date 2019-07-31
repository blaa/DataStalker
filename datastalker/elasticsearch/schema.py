
# Basic types
STR_ANALYZED = {"type": "text"}
STR_NOT_ANALYZED = {"type": "keyword"}
STR = STR_NOT_ANALYZED
a ={
    "type": "text",
    "fields": {
        "raw": {
            "type": "keyword",
        },
    }
}

INT = {"type": "integer"}
DATE = {"type": "date"}
DOUBLE = {"type": "double"}
BOOL = {"type": "boolean"}
GEO = {"type": "geo_point"}

# Analyzed subobject
OBJECT = {"type": "object", "enabled": True}

# Not-analysed subobject
META = {"type": "object", "enabled": False}
