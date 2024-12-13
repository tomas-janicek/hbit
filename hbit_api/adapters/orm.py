import logging

import sqlalchemy
from sqlalchemy.orm import registry, relationship

from hbit_api.domain import models

logger = logging.getLogger(__name__)

metadata = sqlalchemy.MetaData()

# TODO: Can I add on delete CASCADE?
# TODO: What other constraints do I use in SCS?

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
    sqlalchemy.Column("hashed_password", sqlalchemy.Text),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean),
    sqlalchemy.Column("is_superuser", sqlalchemy.Boolean),
)


cwes = sqlalchemy.Table(
    "cwes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cwe_id", sqlalchemy.Integer, unique=True),
    sqlalchemy.Column("name", sqlalchemy.Text),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("extended_description", sqlalchemy.Text),
    sqlalchemy.Column("likelihood_of_exploit", sqlalchemy.Text),
    sqlalchemy.Column("background_details", sqlalchemy.JSON),
    sqlalchemy.Column("potential_mitigations", sqlalchemy.JSON),
    sqlalchemy.Column("detection_methods", sqlalchemy.JSON),
)


capecs = sqlalchemy.Table(
    "capecs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("capec_id", sqlalchemy.Text, unique=True),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("extended_description", sqlalchemy.Text),
    sqlalchemy.Column("likelihood_of_attack", sqlalchemy.Text),
    sqlalchemy.Column("severity", sqlalchemy.Text),
    sqlalchemy.Column("execution_flow", sqlalchemy.JSON),
    sqlalchemy.Column("prerequisites", sqlalchemy.JSON),
    sqlalchemy.Column("skills_required", sqlalchemy.JSON),
    sqlalchemy.Column("resources_required", sqlalchemy.JSON),
    sqlalchemy.Column("consequences", sqlalchemy.JSON),
)


map_capec_to_cwe = sqlalchemy.Table(
    "map_capec_to_cwe",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("capec_id", sqlalchemy.ForeignKey("capecs.id")),
    sqlalchemy.Column("cwe_id", sqlalchemy.ForeignKey("cwes.id")),
    sqlalchemy.UniqueConstraint("capec_id", "cwe_id", name="unique_capec_id_cwe_id"),
)

cves = sqlalchemy.Table(
    "cves",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cve_id", sqlalchemy.Text, unique=True),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("published", sqlalchemy.DateTime),
    sqlalchemy.Column("last_modified", sqlalchemy.DateTime),
    sqlalchemy.Column("cvss", sqlalchemy.JSON),
)

map_cwe_to_cve = sqlalchemy.Table(
    "map_cwe_to_cve",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cwe_id", sqlalchemy.ForeignKey("cwes.id")),
    sqlalchemy.Column("cve_id", sqlalchemy.ForeignKey("cves.id")),
    sqlalchemy.UniqueConstraint("cwe_id", "cve_id", name="unique_cwe_id_cve_id"),
)

patches = sqlalchemy.Table(
    "patches",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("build", sqlalchemy.Text, unique=True),
    sqlalchemy.Column("os", sqlalchemy.Text),
    sqlalchemy.Column("name", sqlalchemy.Text),
    sqlalchemy.Column("version", sqlalchemy.Text),
    sqlalchemy.Column("major", sqlalchemy.Integer),
    sqlalchemy.Column("minor", sqlalchemy.Integer),
    sqlalchemy.Column("patch", sqlalchemy.Integer),
    sqlalchemy.Column("released", sqlalchemy.Date, nullable=True),
)

map_cve_to_patch = sqlalchemy.Table(
    "map_cve_to_patch",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cve_id", sqlalchemy.ForeignKey("cves.id")),
    sqlalchemy.Column("patch_id", sqlalchemy.ForeignKey("patches.id")),
    sqlalchemy.UniqueConstraint("cve_id", "patch_id", name="unique_cve_id_patch_id"),
)


def start_mappers() -> None:
    logger.info("Starting mappers")
    mapper_registry = registry()

    _user_mapper = mapper_registry.map_imperatively(
        class_=models.User,
        local_table=users,
    )
    _capec_mapper = mapper_registry.map_imperatively(
        class_=models.CAPEC,
        local_table=capecs,
    )
    _cwe_mapper = mapper_registry.map_imperatively(
        class_=models.CWE,
        local_table=cwes,
        properties={
            "capecs": relationship(
                _capec_mapper,
                secondary=map_capec_to_cwe,
                collection_class=list,
            )
        },
    )
    _cve_mapper = mapper_registry.map_imperatively(
        class_=models.CVE,
        local_table=cves,
        properties={
            "cwes": relationship(
                _cwe_mapper,
                secondary=map_cwe_to_cve,
                collection_class=list,
            )
        },
    )
    _patch_mapper = mapper_registry.map_imperatively(
        class_=models.Patch,
        local_table=patches,
        properties={
            "cves": relationship(
                _cve_mapper,
                secondary=map_cve_to_patch,
                collection_class=list,
            )
        },
    )
