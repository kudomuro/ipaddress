import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from ipaddresses.models import ipaddress, iptypes, modes, nettypes, objects, spaces, vrfs, equiptypes, count_host
from ipaddresses.utils import insert_children, build_tree
from auth.models import user
from src.auth.base_config import auth_backend, fastapi_users, current_user

from typing import List
from ipaddresses.schemas import GetIpaddress, GetIpaddressForApp, GetIpaddressForTree, CreateIpaddress, GetIpaddressSpace, GetIpaddressIptype, GetIpaddressMode, GetIpaddressNettype, GetIpaddressVrf, GetIpaddressEquiptype
from ipaddress import ip_network, IPv4Interface, ip_address, IPv4Network

router = APIRouter(
    prefix="/ipaddresses",
    tags=["Ipaddress"]
)

@router.get("/get_ip", response_model=List[GetIpaddress])
async def get_ipaddress(get_ip: IPv4Interface, user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, ipaddress.c.mask, iptypes.c.title.label('iptype'), modes.c.title.label('mode'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.title, equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), user.c.username.label('lmuser'), ipaddress.c.lmdate, ipaddress.c.parent_id).\
        select_from(
            ipaddress.outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                join(spaces, ipaddress.c.space==spaces.c.code).\
                outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                outerjoin(user, ipaddress.c.lmuser==user.c.id)
        ).where(ipaddress.c.ip == get_ip).order_by(ipaddress.c.ip)
    result = await session.execute(query)
    return result.all()

@router.get("/all", response_model=List[GetIpaddressForTree])
async def get_all_ipaddresses(parent: int = None, session: AsyncSession = Depends(get_async_session)):
    query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip.label("ip"), iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
        select_from(
            ipaddress.\
                outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                join(spaces, ipaddress.c.space==spaces.c.code).\
                outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                outerjoin(count_host, ipaddress.c.code==count_host.c.code)
        ).order_by('ip')
    result = await session.execute(query)
    dict_result = [dict(r._mapping) for r in result]
    tree = insert_children(dict_result)
    return tree

@router.get("/get_ip_table/{ip_id}", response_model=List[CreateIpaddress])
async def get_ipaddress_an_id(ip_id: int, user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(ipaddress.c.code, ipaddress.c.space, ipaddress.c.ip, ipaddress.c.mask, ipaddress.c.iptype, ipaddress.c.mode, ipaddress.c.nettype, ipaddress.c.vrf, ipaddress.c.title, ipaddress.c.equiptype, ipaddress.c.obj, ipaddress.c.lmuser).where(ipaddress.c.code == ip_id).order_by(ipaddress.c.ip)
    result = await session.execute(query)
    return result.all()

@router.get("/app", response_model=List[GetIpaddressForApp])
async def get_all_ipaddresses_for_app(sort = "ip", skip: int = 1,
    limit: int = 50, session: AsyncSession = Depends(get_async_session)):
    offset_value = (skip - 1) * limit
    if (sort[0]=="-"):
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip.label("ip"), iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).filter((iptypes.c.title == 'Хост') | (iptypes.c.title == 'Группа')).order_by(desc(sort[1:])).offset(offset_value).limit(limit)
    else:
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip.label("ip"), iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).filter((iptypes.c.title == 'Хост') | (iptypes.c.title == 'Группа')).order_by(sort).offset(offset_value).limit(limit)
    result = await session.execute(query)
    # dict_result = [dict(r._mapping) for r in result]
    # tree = insert_children(dict_result)
    return result.all()

@router.get("/range", response_model=List[GetIpaddressForApp])
async def get_range_ipaddresses(sort = "ip", skip: int = 1,
    limit: int = 50, session: AsyncSession = Depends(get_async_session)):
    offset_value = (skip - 1) * limit
    if (sort[0]=="-"):
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).where(iptypes.c.title == "Сеть").order_by(desc(sort[1:])).offset(offset_value).limit(limit)
    else:
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).where(iptypes.c.title == "Сеть").order_by(sort).offset(offset_value).limit(limit)        
    result = await session.execute(query)
    # dict_result = [dict(r._mapping) for r in result]
    # tree = insert_children(dict_result)
    return result.all()

@router.get("/prefix", response_model=List[GetIpaddressForApp])
async def get_prefix_ipaddresses(sort = "ip", skip: int = 1,
    limit: int = 50, session: AsyncSession = Depends(get_async_session)):
    offset_value = (skip - 1) * limit
    if (sort[0]=="-"):
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).where(iptypes.c.title == "Диапазон").order_by(desc(sort[1:])).offset(offset_value).limit(limit)
    else:
        query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
            select_from(
                ipaddress.\
                    outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                    join(spaces, ipaddress.c.space==spaces.c.code).\
                    outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                    outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                    outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                    outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                    outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                    outerjoin(count_host, ipaddress.c.code==count_host.c.code)
            ).where(iptypes.c.title == "Диапазон").order_by(sort).offset(offset_value).limit(limit)       
    result = await session.execute(query)
    # dict_result = [dict(r._mapping) for r in result]
    # print(dict_result)
    # tree = insert_children(dict_result)
    return result.all()

@router.get("/ip/{ip_id}", response_model=List[GetIpaddress])
async def get_full_ipaddress_an_id(ip_id: int, user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip, ipaddress.c.mask, iptypes.c.title.label('iptype'), modes.c.title.label('mode'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.title, equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), user.c.username.label('lmuser'), ipaddress.c.lmdate, ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask).\
        select_from(
            ipaddress.outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                join(spaces, ipaddress.c.space==spaces.c.code).\
                outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                outerjoin(user, ipaddress.c.lmuser==user.c.id)
        ).where(ipaddress.c.code == ip_id)
    result = await session.execute(query)
    return result.all()

@router.get("/child/{ip_id}", response_model=List[GetIpaddressForApp])
async def get_child_ipaddress_an_ip_parent(ip_id: int, user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(ipaddress.c.code, spaces.c.title.label('space'), ipaddress.c.ip.label("ip"), iptypes.c.title.label('iptype'), ipaddress.c.title, modes.c.title.label('mode'), equiptypes.c.title.label('equiptype'), objects.c.title.label('obj'), nettypes.c.title.label('nettype'), vrfs.c.title.label('vrf'), ipaddress.c.parent_id, ipaddress.c.child_count, ipaddress.c.mask, count_host.c.count.label("count_host")).\
        select_from(
            ipaddress.\
                outerjoin(iptypes, ipaddress.c.iptype==iptypes.c.code).\
                join(spaces, ipaddress.c.space==spaces.c.code).\
                outerjoin(modes, ipaddress.c.mode==modes.c.code).\
                outerjoin(nettypes, ipaddress.c.nettype==nettypes.c.code).\
                outerjoin(vrfs, ipaddress.c.vrf==vrfs.c.code).\
                outerjoin(equiptypes, ipaddress.c.equiptype==equiptypes.c.code).\
                outerjoin(objects, ipaddress.c.obj==objects.c.code).\
                outerjoin(count_host, ipaddress.c.code==count_host.c.code)
        ).where(ipaddress.c.parent_id == ip_id).order_by('ip')
    result = await session.execute(query)
    # dict_result = [dict(r._mapping) for r in result]
    # tree = insert_children(dict_result)
    return result.all()

@router.post("/add/ip/")
async def add_ipaddress(new_ip: CreateIpaddress, user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    enter_ip = new_ip.ip
    # Проверка существует ли указанный ip
    async def finde_same_ip(enter_ip):
        query = (
            select(ipaddress)
            .where(ipaddress.c.ip == enter_ip)
        )     
        result = await session.execute(query)
        return result.fetchone()              
    query_check_ip = await finde_same_ip(enter_ip)
    check_ip = query_check_ip is None # Если True, значит такого адреса нет
    print("Указанный адрес не существует:", check_ip, query_check_ip)
    # Поиск родительской сети для адреса
    # subquery_find_parent = select([text(f"'{enter_ip}'::inet AS new_ip")]).alias("new_address")
    async def find_parent(enter_ip):
        new_address = {"new_ip": enter_ip}
        query = (
            select(ipaddress)
            .where(text(":new_ip << ip"))
            .order_by(text("masklen(ip) DESC"))
            .limit(1)
        )
        result = await session.execute(query, new_address)
        return result.fetchone()    
    
    async def find_count_child(parent_network_id):
        query_count_child = (
           select(func.count(ipaddress.c.parent_id))
            .filter(ipaddress.c.parent_id == parent_network_id)
        )
        # query_count_child = ("SELECT COUNT(*) FROM ipaddress WHERE parent_id = '{parent_network_id}' GROUP BY parent_id;")
        result = await session.execute(query_count_child)
        count_result = result.first()
        return count_result
    
    parent_network = await find_parent(enter_ip)
    print("Родительская сеть:", parent_network)
    if not(parent_network is None):
        parent_network_id = parent_network[0]
        print("Родительская сеть parent_network_id:", parent_network_id)
        parent_network_mask = parent_network[3]
        print("Родительская сеть parent_network_mask:", parent_network_mask)

    if (check_ip):
        if not(parent_network is None):
            count_child = await find_count_child(parent_network_id)
            print('Количество потомков: ', count_child[0])
            percent_use = (count_child[0]*100)/(2**(32-parent_network_mask)-2)    
            print("Процент использования:", percent_use)    
            if (percent_use<100):
                stmt = insert(ipaddress).values(**new_ip.dict())
                await session.execute(stmt)
                await session.commit()
                print("stmt=", stmt)
                return {'status': 'success'}
            else:
                print("Все адреса в сети заняты")  
                return {'status': 'network_full'}
        return {'status': 'success'}
    else:
        return {'status': 'address_exists'}

@router.get("/spaces", response_model=List[GetIpaddressSpace])
async def get_spaces(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(spaces.c.code, spaces.c.title)
    result = await session.execute(query)
    return result.all()

@router.get("/iptypes", response_model=List[GetIpaddressIptype])
async def get_iptypes(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(iptypes.c.code, iptypes.c.title)
    result = await session.execute(query)
    return result.all()

@router.get("/modes", response_model=List[GetIpaddressMode])
async def get_modes(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(modes.c.code, modes.c.title)
    result = await session.execute(query)
    return result.all()

@router.get("/nettypes", response_model=List[GetIpaddressNettype])
async def get_nettypes(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(nettypes.c.code, nettypes.c.title)
    result = await session.execute(query)
    return result.all()

@router.get("/vrfs", response_model=List[GetIpaddressVrf])
async def get_vrfs(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(vrfs.c.code, vrfs.c.title)
    result = await session.execute(query)
    return result.all()

@router.get("/equiptypes", response_model=List[GetIpaddressEquiptype])
async def get_vrfs(user_auth = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(equiptypes.c.code, equiptypes.c.title)
    result = await session.execute(query)
    return result.all()