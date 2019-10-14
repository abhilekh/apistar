import re
from urllib.parse import urljoin, ParseResult

import typesystem
from apistar.document import Document, Field, Link, Section
from apistar.schemas.jsonschema import JSON_SCHEMA

import apistar.schemas.util as sutil

SCHEMA_REF = typesystem.Object(
    properties={"$ref": typesystem.String(pattern="^#/components/schemas/")}
)

REQUESTBODY_REF = typesystem.Object(
    properties={"$ref": typesystem.String(pattern="^#/components/requestBodies/")}
)

RESPONSE_REF = typesystem.Object(
    properties={"$ref": typesystem.String(pattern="^#/components/responses/")}
)

definitions = typesystem.SchemaDefinitions()

OPEN_API = typesystem.Object(
    title="OpenAPI",
    properties={
        "openapi": typesystem.String(),
        "info": typesystem.Reference("Info", definitions=definitions),
        "servers": typesystem.Array(
            items=typesystem.Reference("Server", definitions=definitions)
        ),
        "paths": typesystem.Reference("Paths", definitions=definitions),
        "components": typesystem.Reference("Components", definitions=definitions),
        "security": typesystem.Array(
            items=typesystem.Reference("SecurityRequirement", definitions=definitions)
        ),
        "tags": typesystem.Array(
            items=typesystem.Reference("Tag", definitions=definitions)
        ),
        "externalDocs": typesystem.Reference(
            "ExternalDocumentation", definitions=definitions
        ),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["openapi", "info", "paths"],
)

definitions["Info"] = typesystem.Object(
    properties={
        "title": typesystem.String(allow_blank=True),
        "product": typesystem.String(allow_blank=True),
        "description": typesystem.Text(allow_blank=True),
        "termsOfService": typesystem.URL(),
        "contact": typesystem.Reference("Contact", definitions=definitions),
        "license": typesystem.Reference("License", definitions=definitions),
        "version": typesystem.String(allow_blank=True),
        "site_favicon": typesystem.String(allow_blank=True),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["title", "version"],
)

definitions["Contact"] = typesystem.Object(
    properties={
        "name": typesystem.String(allow_blank=True),
        "url": typesystem.URL(),
        "email": typesystem.Email(),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["License"] = typesystem.Object(
    properties={"name": typesystem.String(), "url": typesystem.URL()},
    required=["name"],
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Server"] = typesystem.Object(
    properties={
        "url": typesystem.URL(),
        "description": typesystem.Text(allow_blank=True),
        "variables": typesystem.Object(
            additional_properties=typesystem.Reference(
                "ServerVariable", definitions=definitions
            )
        ),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["url"],
)

definitions["ServerVariable"] = typesystem.Object(
    properties={
        "enum": typesystem.Array(items=typesystem.String()),
        "default": typesystem.String(),
        "description": typesystem.Text(allow_blank=True),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["default"],
)

definitions["Paths"] = typesystem.Object(
    pattern_properties={
        "^/": typesystem.Reference("Path", definitions=definitions),
        "^x-": typesystem.Any(),
    },
    additional_properties=False,
)

definitions["Path"] = typesystem.Object(
    properties={
        "summary": typesystem.String(allow_blank=True),
        "description": typesystem.Text(allow_blank=True),
        "get": typesystem.Reference("Operation", definitions=definitions),
        "put": typesystem.Reference("Operation", definitions=definitions),
        "post": typesystem.Reference("Operation", definitions=definitions),
        "delete": typesystem.Reference("Operation", definitions=definitions),
        "options": typesystem.Reference("Operation", definitions=definitions),
        "head": typesystem.Reference("Operation", definitions=definitions),
        "patch": typesystem.Reference("Operation", definitions=definitions),
        "trace": typesystem.Reference("Operation", definitions=definitions),
        "servers": typesystem.Array(
            items=typesystem.Reference("Server", definitions=definitions)
        ),
        "parameters": typesystem.Array(
            items=typesystem.Reference("Parameter", definitions=definitions)
        ),
        # TODO: | ReferenceObject
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Operation"] = typesystem.Object(
    properties={
        "tags": typesystem.Array(items=typesystem.String()),
        "summary": typesystem.String(allow_blank=True),
        "description": typesystem.Text(allow_blank=True),
        "externalDocs": typesystem.Reference(
            "ExternalDocumentation", definitions=definitions
        ),
        "operationId": typesystem.String(),
        "parameters": typesystem.Array(
            items=typesystem.Reference("Parameter", definitions=definitions)
        ),  # TODO: | ReferenceObject
        "requestBody": REQUESTBODY_REF
        | typesystem.Reference(
            "RequestBody", definitions=definitions
        ),  # TODO: RequestBody | ReferenceObject
        "responses": typesystem.Reference("Responses", definitions=definitions),
        # TODO: 'callbacks'
        "deprecated": typesystem.Boolean(),
        "security": typesystem.Array(
            typesystem.Reference("SecurityRequirement", definitions=definitions)
        ),
        "servers": typesystem.Array(
            items=typesystem.Reference("Server", definitions=definitions)
        ),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["ExternalDocumentation"] = typesystem.Object(
    properties={
        "description": typesystem.Text(allow_blank=True),
        "url": typesystem.URL(),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["url"],
)

definitions["Parameter"] = typesystem.Object(
    properties={
        "name": typesystem.String(),
        "in": typesystem.Choice(choices=["query", "header", "path", "cookie"]),
        "description": typesystem.Text(allow_blank=True),
        "required": typesystem.Boolean(),
        "deprecated": typesystem.Boolean(),
        "allowEmptyValue": typesystem.Boolean(),
        "style": typesystem.Choice(choices=["matrix", "label", "form", "simple", "spaceDelimited", "pipeDelimited", "deepObject"]),
        "schema": JSON_SCHEMA | SCHEMA_REF,
        "example": typesystem.Any(),
        # TODO: Other fields
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["name", "in"],
)

definitions["RequestBody"] = typesystem.Object(
    properties={
        "description": typesystem.String(allow_blank=True),
        "content": typesystem.Object(
            additional_properties=typesystem.Reference(
                "MediaType", definitions=definitions
            )
        ),
        "required": typesystem.Boolean(),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Responses"] = typesystem.Object(
    properties={
        "default": typesystem.Reference("Response", definitions=definitions)
        | RESPONSE_REF
    },
    pattern_properties={
        "^([1-5][0-9][0-9]|[1-5]XX)$": typesystem.Reference(
            "Response", definitions=definitions
        )
        | RESPONSE_REF,
        "^x-": typesystem.Any(),
    },
    additional_properties=False,
)

definitions["Response"] = typesystem.Object(
    properties={
        "description": typesystem.String(allow_blank=True),
        "content": typesystem.Object(
            additional_properties=typesystem.Reference(
                "MediaType", definitions=definitions
            )
        ),
        "headers": typesystem.Object(
            additional_properties=typesystem.Reference(
                "Header", definitions=definitions
            )
        ),
        # TODO: Header | ReferenceObject
        # TODO: links
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["MediaType"] = typesystem.Object(
    properties={
        "schema": JSON_SCHEMA | SCHEMA_REF,
        "example": typesystem.Any(),
        # TODO 'examples', 'encoding'
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Header"] = typesystem.Object(
    properties={
        "description": typesystem.Text(),
        "required": typesystem.Boolean(),
        "deprecated": typesystem.Boolean(),
        "allowEmptyValue": typesystem.Boolean(),
        "style": typesystem.Choice(choices=["matrix", "label", "form", "simple", "spaceDelimited", "pipeDelimited", "deepObject"]),
        "schema": JSON_SCHEMA | SCHEMA_REF,
        "example": typesystem.Any(),
        # TODO: Other fields
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Components"] = typesystem.Object(
    properties={
        "schemas": typesystem.Object(additional_properties=JSON_SCHEMA),
        "responses": typesystem.Object(
            additional_properties=typesystem.Reference(
                "Response", definitions=definitions
            )
        ),
        "parameters": typesystem.Object(
            additional_properties=typesystem.Reference(
                "Parameter", definitions=definitions
            )
        ),
        "requestBodies": typesystem.Object(
            additional_properties=typesystem.Reference(
                "RequestBody", definitions=definitions
            )
        ),
        "securitySchemes": typesystem.Object(
            additional_properties=typesystem.Reference(
                "SecurityScheme", definitions=definitions
            )
        ),
        # TODO: Other fields
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
)

definitions["Tag"] = typesystem.Object(
    properties={
        "name": typesystem.String(),
        "description": typesystem.Text(allow_blank=True),
        "externalDocs": typesystem.Reference(
            "ExternalDocumentation", definitions=definitions
        ),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["name"],
)

definitions["SecurityRequirement"] = typesystem.Object(
    additional_properties=typesystem.Array(items=typesystem.String())
)

definitions["SecurityScheme"] = typesystem.Object(
    properties={
        "type": typesystem.Choice(
            choices=["apiKey", "http", "oauth2", "openIdConnect"]
        ),
        "description": typesystem.Text(allow_blank=True),
        "name": typesystem.String(),
        "in": typesystem.Choice(choices=["query", "header", "cookie"]),
        "scheme": typesystem.String(),
        "bearerFormat": typesystem.String(),
        "flows": typesystem.Any(),  # TODO: OAuthFlows
        "openIdConnectUrl": typesystem.String(format="url"),
    },
    pattern_properties={"^x-": typesystem.Any()},
    additional_properties=False,
    required=["type"],
)


METHODS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]


# def lookup(value: dict, keys: [list, tuple], default: typesystem.Any = None):
#     '''Check in my nested dict.'''
#     assert isinstance(keys, (list, tuple))
#     for key in keys:
#         try:
#             value = value[key]
#         except (KeyError, IndexError, TypeError):
#             return default
#     return value


def _simple_slugify(text):
    if text is None:
        return None
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"[_]+", "_", text)
    return text.strip("_")


class OpenAPI:
    def load(self, data: dict):
        title = sutil.lookup(data, ["info", "title"])
        description = sutil.lookup(data, ["info", "description"])
        product = sutil.lookup(data, ["info", "product"])
        version = sutil.lookup(data, ["info", "version"])
        base_url = sutil.lookup(data, ["servers", 0, "url"])
        schema_definitions = self.get_schema_definitions(data)
        content = self.get_content(data, base_url, schema_definitions)
        return Document(
            title=title,
            description=description,
            version=version,
            url=base_url,
            product=product,
            content=content,
        )

    def get_schema_definitions(self, data: dict) -> typesystem.SchemaDefinitions:
        definitions = typesystem.SchemaDefinitions()
        schemas = sutil.lookup(data, ["components", "schemas"], {})
        for key, value in schemas.items():
            ref = f"#/components/schemas/{key}"
            definitions[ref] = typesystem.from_json_schema(
                value, definitions=definitions
            )
        return definitions

    def get_content(self, data: dict, base_url: str, schema_definitions: typesystem.SchemaDefinitions):
        """
        Return all the links in the document, layed out by tag and operationId.
        """
        links_by_tag = {}
        links = []

        for path, path_info in data.get("paths", {}).items():
            operations: dict = {key: path_info[key] for key in path_info if key in METHODS}
            for operation, operation_info in operations.items():
                tag = sutil.lookup(operation_info, ["tags", 0])
                link = self.get_link(
                    base_url,
                    path,
                    path_info,
                    operation,
                    operation_info,
                    schema_definitions,
                )
                if link is None:
                    continue

                if tag is None:
                    links.append(link)
                elif tag not in links_by_tag:
                    links_by_tag[tag] = [link]
                else:
                    links_by_tag[tag].append(link)

        sections = [
            Section(name=_simple_slugify(tag), title=tag.title(), content=links)
            for tag, links in links_by_tag.items()
        ]
        return links + sections

    def get_link(
            self, base_url: str, path: str, path_info: str, operation: str, operation_info: dict,
            schema_definitions: typesystem.SchemaDefinitions
    ):
        """
        Return a single link in the document.
        """
        name = operation_info.get("operationId")
        title = operation_info.get("summary")
        description = operation_info.get("description")

        if name is None:
            name = _simple_slugify(title)
            if not name:
                return None

        # Allow path info and operation info to override the base url.
        base_url = sutil.lookup(path_info, ["servers", 0, "url"], default=base_url)
        base_url = sutil.lookup(operation_info, ["servers", 0, "url"], default=base_url)

        # Parameters are taken both from the path info, and from the operation.
        parameters = path_info.get("parameters", [])
        parameters += operation_info.get("parameters", [])

        fields = [
            self.get_field(parameter, schema_definitions) for parameter in parameters
        ]

        # TODO: Handle media type generically here...
        body_schema = sutil.lookup(
            operation_info, ["requestBody", "content", "application/json", "schema"]
        )

        encoding = None
        if body_schema:
            encoding = "application/json"
            if "$ref" in body_schema:
                ref = body_schema["$ref"]
                schema = schema_definitions.get(ref)
                field_name = ref[len("#/components/schemas/") :].lower()
            else:
                schema = typesystem.from_json_schema(
                    body_schema, definitions=schema_definitions
                )
                field_name = "body"
            field_name = sutil.lookup(
                operation_info, ["requestBody", "x-name"], default=field_name
            )
            fields += [Field(name=field_name, location="body", schema=schema)]

        if isinstance(base_url, ParseResult):
            base_url = base_url.geturl()

        return Link(
            name=name,
            url=urljoin(base_url, path),
            method=operation,
            title=title,
            description=description,
            fields=fields,
            encoding=encoding,
        )

    def get_field(self, parameter, schema_definitions):
        """
        Return a single field in a link.
        """
        name = parameter.get("name")
        location = parameter.get("in")
        description = parameter.get("description")
        required = parameter.get("required", False)
        schema = parameter.get("schema")
        example = parameter.get("example")

        if schema is not None:
            if "$ref" in schema:
                ref = schema["$ref"]
                schema = schema_definitions.get(ref)
            else:
                schema = typesystem.from_json_schema(
                    schema, definitions=schema_definitions
                )

        return Field(
            name=name,
            location=location,
            description=description,
            required=required,
            schema=schema,
            example=example
        )
