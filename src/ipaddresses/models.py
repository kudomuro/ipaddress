from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, Boolean, MetaData, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy import TypeDecorator
from ipaddress import ip_network, ip_address
from auth.models import user

from database import Base

metadata = MetaData()

iptypes = Table(
    "iptypes",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

modes = Table(
    "modes",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

nettypes = Table(
    "nettypes",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

objects = Table(
    "objects",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

spaces = Table(
    "spaces",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

vrfs = Table(
    "vrfs",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

equiptypes = Table(
    "equiptypes",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("titlerep", String, nullable=False),
)

ipaddress = Table(
    "ipaddress",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("space", Integer, ForeignKey(spaces.c.code)),
    Column("ip", postgresql.INET, nullable=False),
    Column("mask", Integer, default=32, nullable=False),
    Column("iptype", Integer, ForeignKey(iptypes.c.code)),
    Column("mode", Integer, ForeignKey(modes.c.code)),
    Column("nettype", Integer, ForeignKey(nettypes.c.code)),
    Column("vrf", Integer, ForeignKey(vrfs.c.code)),
    Column("title", String),
    Column("equiptype", Integer, ForeignKey(equiptypes.c.code)),
    Column("obj", Integer, ForeignKey(objects.c.code)),
    Column("lmuser", Integer, ForeignKey(user.c.id)),
    Column("lmdate", TIMESTAMP, default=datetime.utcnow),
    Column("parent_id", Integer),
    Column("child_count", Integer),
)

ipslog = Table(
    "ipslog",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("time", TIMESTAMP, default=datetime.utcnow, nullable=False),
    Column("operation", Integer, default=0, nullable=False),
    Column("oipcode", Integer),
    Column("ospace", Integer, ForeignKey(spaces.c.code)),
    Column("obegin", Integer),
    Column("oend", Integer),
    Column("omask", Integer),
    Column("oiptype", Integer, ForeignKey(iptypes.c.code)),
    Column("omode", Integer, ForeignKey(modes.c.code)),
    Column("onettype", Integer, ForeignKey(nettypes.c.code)),
    Column("ovrf", Integer, ForeignKey(vrfs.c.code)),
    Column("otitle", String),
    Column("oequiptype", Integer, ForeignKey(equiptypes.c.code)),
    Column("oobj", Integer, ForeignKey(objects.c.code)),
    Column("olmuser", Integer, ForeignKey(user.c.id)),
    Column("olmdate", TIMESTAMP, default=datetime.utcnow),
    Column("ipcode", Integer),
    Column("space", Integer, ForeignKey(spaces.c.code)),
    Column("begin", Integer),
    Column("end", Integer),
    Column("mask", Integer),
    Column("iptype", Integer, ForeignKey(iptypes.c.code)),
    Column("mode", Integer, ForeignKey(modes.c.code)),
    Column("nettype", Integer, ForeignKey(nettypes.c.code)),
    Column("vrf", Integer, ForeignKey(vrfs.c.code)),
    Column("title", String),
    Column("equiptype", Integer, ForeignKey(equiptypes.c.code)),
    Column("obj", Integer, ForeignKey(objects.c.code)),
    Column("lmuser", Integer, ForeignKey(user.c.id)),
    Column("lmdate", TIMESTAMP, default=datetime.utcnow),
)

count_host = Table(
    "count_host",
    metadata,
    Column("code", Integer, primary_key=True),
    Column("count", Integer, default=0),
)

class IPNetwork(TypeDecorator):
    impl = postgresql.INET

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        return ip_network(value)


class A(Base):
    __tablename__ = "a"

    id = Column(Integer, primary_key=True)
    data = Column(IPNetwork)