from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from ipaddress import ip_network, IPv4Interface, ip_address, IPv4Address, IPv4Network
from sqlalchemy.dialects import postgresql

class GetIpaddress(BaseModel):
    code: int
    space: str
    ip: IPv4Interface
    mask: int
    iptype: Optional[str]
    mode: Optional[str]
    nettype: Optional[str]
    vrf: Optional[str]
    title: Optional[str]
    equiptype: Optional[str]
    obj: Optional[str]
    lmuser: Optional[str]
    lmdate: Optional[datetime]
    parent_id: Optional[int]

class CreateIpaddress(BaseModel):
    space: int
    ip: IPv4Interface
    mask: int
    iptype: Optional[int]
    mode: Optional[int]
    nettype: Optional[int]
    vrf: Optional[int]
    title: Optional[str]
    equiptype: Optional[int]
    obj: Optional[int]
    lmuser: Optional[int]


class GetIpaddressForApp(BaseModel):
    code: int
    space: str
    ip: IPv4Network
    iptype: Optional[str]
    title: Optional[str]
    mode: Optional[str]
    equiptype: Optional[str]    
    obj: Optional[str]    
    nettype: Optional[str]
    vrf: Optional[str]
    parent_id: Optional[int]
    child_count: Optional[int]
    mask: Optional[int]
    count_host: Optional[int]

class GetIpaddressForTree(BaseModel):
    code: int
    space: str
    ip: IPv4Network
    iptype: Optional[str]
    title: Optional[str]
    mode: Optional[str]
    equiptype: Optional[str]    
    obj: Optional[str]    
    nettype: Optional[str]
    vrf: Optional[str]
    parent_id: Optional[int]
    child_count: Optional[int]
    mask: Optional[int]
    count_host: Optional[int]
    children: List[GetIpaddressForTree]

class GetIpaddressSpace(BaseModel):
    code: int    
    title: str

class GetIpaddressIptype(BaseModel):
    code: int    
    title: str

class GetIpaddressMode(BaseModel):
    code: int    
    title: str

class GetIpaddressNettype(BaseModel):
    code: int    
    title: str

class GetIpaddressVrf(BaseModel):
    code: int    
    title: str

class GetIpaddressEquiptype(BaseModel):
    code: int    
    title: str