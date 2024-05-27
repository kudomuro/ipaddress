import ipaddress
from anytree import Node, RenderTree
import json
from sqlalchemy.orm import class_mapper
from ipaddress import ip_network, IPv4Interface, ip_address, IPv4Network, IPv4Address
from typing import List
from ipaddresses.schemas import GetIpaddressForApp
from sqlalchemy.ext.declarative import DeclarativeMeta
import pprint

def insert_children(data):
    # Создаем словарь для хранения дочерних элементов
    children_dict = {}
    parent_dict = []

    # Группируем элементы по родительским идентификаторам
    for item in data:
        parent_id = item['parent_id']
        if parent_id not in children_dict:
            children_dict[parent_id] = []
        children_dict[parent_id].append(item)  

    for item in data:
        if (item['parent_id'] is None): 
            parent_dict.append(item) 
    # Вставляем дочерние элементы в родительские
    for item in data:     
        item['children'] = children_dict.get(item['code'], [])

    pprint.pprint(parent_dict)
    # print(type(data))

    return parent_dict

def build_tree(data):
    mapping = {}
    children = set()
    for child, parent in data:
        mapping.setdefault(parent, {})[child] = (
            {} if child in children
            else mapping.setdefault(child, {})
        )
        children.add(child)
    return {
        parent: mapping[parent]
        for parent in mapping.keys() - children
    }