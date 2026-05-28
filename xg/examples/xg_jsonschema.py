import json

from jsonschema import Draft7Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])
        for error in validate_properties(
            validator, properties, instance, schema
        ):
            yield error

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


def generate_schema(json_data):
    schema = {}
    DefaultValidatingDraft7Validator.check_schema(schema)
    DefaultValidatingDraft7Validator(schema).validate(json_data)
    return schema


# Example usage
json_data = {"name": "John", "age": 30, "city": "New York"}

schema = generate_schema(json_data)
print(json.dumps(schema, indent=4))
