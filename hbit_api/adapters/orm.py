import logging

import sqlalchemy
from sqlalchemy.orm import registry, relationship

from hbit_api.domain import models

logger = logging.getLogger(__name__)

metadata = sqlalchemy.MetaData()


CASCADE = "CASCADE"

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True, index=True),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
    sqlalchemy.Column("hashed_password", sqlalchemy.Text),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean),
    sqlalchemy.Column("is_superuser", sqlalchemy.Boolean),
)


cwes = sqlalchemy.Table(
    "cwes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cwe_id", sqlalchemy.Integer, unique=True, index=True),
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
    sqlalchemy.Column("capec_id", sqlalchemy.Text, unique=True, index=True),
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
    sqlalchemy.Column("capec_id", sqlalchemy.ForeignKey("capecs.id", ondelete=CASCADE)),
    sqlalchemy.Column("cwe_id", sqlalchemy.ForeignKey("cwes.id", ondelete=CASCADE)),
    sqlalchemy.UniqueConstraint("capec_id", "cwe_id", name="unique_capec_id_cwe_id"),
    sqlalchemy.Index("index_capec_id_cwe_id", "capec_id", "cwe_id"),
)

cves = sqlalchemy.Table(
    "cves",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cve_id", sqlalchemy.Text, unique=True, index=True),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("published", sqlalchemy.DateTime),
    sqlalchemy.Column("last_modified", sqlalchemy.DateTime),
    sqlalchemy.Column("cvss", sqlalchemy.JSON),
)

map_patch_to_device = sqlalchemy.Table(
    "map_patch_to_device",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column(
        "patch_id", sqlalchemy.ForeignKey("patches.id", ondelete=CASCADE)
    ),
    sqlalchemy.Column(
        "device_id", sqlalchemy.ForeignKey("devices.id", ondelete=CASCADE)
    ),
    sqlalchemy.UniqueConstraint(
        "patch_id", "device_id", name="unique_patch_id_device_id"
    ),
    sqlalchemy.Index("index_patch_id_device_id", "patch_id", "device_id"),
)

devices = sqlalchemy.Table(
    "devices",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("identifier", sqlalchemy.Text, unique=True, index=True),
    sqlalchemy.Column(
        "manufacturer_id", sqlalchemy.ForeignKey("manufacturers.id", ondelete=CASCADE)
    ),
    sqlalchemy.Column("name", sqlalchemy.Text),
    sqlalchemy.Column("models", sqlalchemy.JSON),
    sqlalchemy.Column("released", sqlalchemy.Date, nullable=True),
    sqlalchemy.Column("discontinued", sqlalchemy.Date, nullable=True),
    sqlalchemy.Column("hardware_info", sqlalchemy.JSON),
)

map_cwe_to_cve = sqlalchemy.Table(
    "map_cwe_to_cve",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("cwe_id", sqlalchemy.ForeignKey("cwes.id", ondelete=CASCADE)),
    sqlalchemy.Column("cve_id", sqlalchemy.ForeignKey("cves.id", ondelete=CASCADE)),
    sqlalchemy.UniqueConstraint("cwe_id", "cve_id", name="unique_cwe_id_cve_id"),
    sqlalchemy.Index("index_cwe_id_cve_id", "cwe_id", "cve_id"),
)

manufacturers = sqlalchemy.Table(
    "manufacturers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.Text, unique=True, index=True),
)


patches = sqlalchemy.Table(
    "patches",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("build", sqlalchemy.Text, unique=True, index=True),
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
    sqlalchemy.Column("cve_id", sqlalchemy.ForeignKey("cves.id", ondelete=CASCADE)),
    sqlalchemy.Column(
        "patch_id", sqlalchemy.ForeignKey("patches.id", ondelete=CASCADE)
    ),
    sqlalchemy.UniqueConstraint("cve_id", "patch_id", name="unique_cve_id_patch_id"),
    sqlalchemy.Index("index_cve_id_patch_id", "cve_id", "patch_id"),
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
    _manufacturer_mapper = mapper_registry.map_imperatively(
        class_=models.Manufacturer,
        local_table=manufacturers,
    )
    _device_mapper = mapper_registry.map_imperatively(
        class_=models.Device,
        local_table=devices,
        properties={"manufacturer": relationship(_manufacturer_mapper)},
    )
    _patch_mapper = mapper_registry.map_imperatively(
        class_=models.Patch,
        local_table=patches,
        properties={
            "cves": relationship(
                _cve_mapper,
                secondary=map_cve_to_patch,
                collection_class=list,
            ),
            "devices": relationship(
                _device_mapper,
                secondary=map_patch_to_device,
                collection_class=list,
            ),
        },
    )
