#!/usr/bin/env python3
"""
Generate a high-quality JSON Schema from the canonical configuration model.

This is the single source of truth for the shape of
`create-payload-config.json`.

Run this script (or `make generate-config-schema`) whenever you change
the model.
The output powers excellent VS Code IntelliSense via JSON Schema.
"""

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, EmailStr, Field


class Template(StrEnum):
    blank = "blank"
    website = "website"
    ecommerce = "ecommerce"
    plugin = "plugin"
    payload_demo = "payload-demo"
    payload_website = "payload-website"


class DbAdapter(StrEnum):
    postgres = "postgres"
    mongodb = "mongodb"
    sqlite = "sqlite"
    d1_sqlite = "d1-sqlite"
    vercel_postgres = "vercel-postgres"


class Agent(StrEnum):
    claude = "claude"
    codex = "codex"
    cursor = "cursor"
    none = "none"


class CreatePayloadConfig(BaseModel):
    """Strongly typed configuration for XGIC Payload CMS Dev Containers.

    This model is the source of truth for both:
    - The generated JSON Schema (for .json editing + VS Code IntelliSense)
    - Runtime validation in tooling
    """

    projectName: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        description=(
            "The folder name for the generated Payload project "
            "(lowercase, numbers, and hyphens only)"
        ),
        examples=["website", "my-payload-cms"],
    )

    template: Template = Field(
        default=Template.website,
        description="Which official Payload starter template to scaffold",
    )

    example: str | None = Field(
        default=None,
        description=(
            "Optional: Use a specific Payload example instead of a template"
        ),
    )

    agent: Agent = Field(
        default=Agent.none,
        description=(
            "Coding agent skill to install inside the generated project. "
            "Use 'none' (recommended) when running inside a dev "
            "container or CI to avoid installing "
            "Claude Code / Cursor / Codex skills."
        ),
    )

    dbAdapter: DbAdapter = Field(
        default=DbAdapter.postgres,
        description="Database adapter to configure for the generated project",
    )

    dbName: str = Field(
        default="payload_db",
        description=(
            "Logical database name (used when creating the DB in "
            "Postgres/Mongo)"
        ),
    )

    dbUser: str = Field(
        default="payload",
        description="Database user name",
    )

    dbUri: str | None = Field(
        default=None,
        description=(
            "Full database connection string. In normal devcontainer "
            "usage this is overridden "
            "at runtime from the live .devcontainer/.env (which contains "
            "freshly generated credentials). "
            "You may leave a placeholder value here."
        ),
        examples=["postgres://payload:<PASSWORD>@postgres:5432/payload_db"],
    )

    adminEmail: EmailStr = Field(
        default="admin@example.com",
        description=(
            "Email address for the initial admin user in the Payload "
            "admin panel"
        ),
    )

    telemetry: bool = Field(
        default=False,
        description="Whether to enable Payload's anonymous telemetry",
    )


if __name__ == "__main__":
    # Resolve output path relative to this script so it always lands
    # next to the main config file
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "create-payload-config.schema.json"

    schema = CreatePayloadConfig.model_json_schema()

    # Enhance the schema for humans and editors
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["$id"] = (
        "https://raw.githubusercontent.com/XGIC/payload-cms-dev-containers/main/.devcontainer/create-payload-config.schema.json"
    )
    schema["title"] = "XGIC Create Payload Config"
    schema["description"] = (
        "Configuration for the XGIC Payload CMS Dev Container. "
        "Controls project name, template, database settings, "
        "and optional agent integration. "
        "This file has rich JSON Schema support for excellent VS Code "
        "IntelliSense."
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")

    print(f"✅ Generated {output_path.relative_to(script_dir.parent.parent)}")
    print(
        "   Rich VS Code IntelliSense is now available "
        "for create-payload-config.json"
    )
