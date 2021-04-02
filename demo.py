import json

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command

nr = InitNornir(config_file='config.yaml')
selab = nr.filter(F(groups__contains='selab'))

def get_mgmt_ip(inst):
    output = inst.run(task=netmiko_send_command,
                      command_string='show int mgmt0 | json')
    return output

def get_host_info(inst):
    output = inst.run(task=netmiko_send_command,
                      command_string='show version | json')
    return output

def get_lldp_info(inst):
    output = inst.run(task=netmiko_send_command,
                      command_string='show lldp neighbors | json')
    return output

host_info = get_host_info(selab)
lldp_info = get_lldp_info(selab)
mgmt_info = get_mgmt_ip(selab)

intf_name_map = {
    'Eth': 'Ethernet'
}

def short_intfname(intf_name):
    for key, value in intf_name_map.items():
        if intf_name.startswith(value):
            return intf_name.replace(value, key)
    return intf_name

def get_nodes_info(host_info=host_info, mgmt_info=mgmt_info, node_id=0):
    nodes = []
    nodes_dict = {}
    host_id_map = {}
    ip_id_map = {}

    # 获取 node id、name 等信息保存在 nodes_dict 字典
    # 保存 inventory.host 和 node id 的 mapping 关系
    for host, result in host_info.items():
        try:
            result_dict = json.loads(result.result)
            nodes_dict.update({
                host: {
                    'id': node_id,
                    'name': result_dict['host_name'],
                    'model': result_dict['chassis_id'],
                    'image': result_dict['kickstart_ver_str']
                }
            })
            host_id_map[host] = node_id
            node_id += 1
        except:
            continue

    # 为 nodes_dict 字典补充管理 ip 地址，同时保存管理 ip 和 node id 的 mapping 关系
    for host, result in mgmt_info.items():
        try:
            result_dict = json.loads(result.result)
            mgmt_ip = result_dict['TABLE_interface']['ROW_interface']['eth_ip_addr']
            nodes_dict[host]['mgmt_ip'] = mgmt_ip
            ip_id_map[mgmt_ip] = host_id_map[host]
        except:
            continue

    # 从 nodes_dict 字典提取信息，生成 nodes:[]
    for host, dict in nodes_dict.items():
        nodes.append(dict)

    return nodes, host_id_map, ip_id_map, node_id

nodes, host_id_map, ip_id_map, node_id = get_nodes_info()

def get_links(lldp_info=lldp_info):
    links_list = []
    links = []
    link_id = 0
    for host, result in lldp_info.items():
        try:
            result_list = json.loads(result.result)['TABLE_nbor']['ROW_nbor']
            for item in result_list:

                # 不在拓扑上显示管理交换机，如果本地接口是 mgmt0，则不处理数据
                if item['l_port_id'] != 'mgmt0':
                    local_id = host_id_map[host]
                    local_intf = short_intfname(item['l_port_id'])

                    # 判断邻居的管理 IP 是否在 Inventory 里面。如果不在，则补充 nodes[] 信息
                    if item['mgmt_addr'] in ip_id_map.keys():
                        remote_id = ip_id_map[item['mgmt_addr']]
                    else:
                        nodes.append({
                            'id': node_id,
                            'name': item['chassis_id']
                        })
                        remote_id = node_id
                        node_id += 1

                    # 统一本地接口和邻居接口名称的格式
                    remote_intf = short_intfname(item['port_id'])

                local_end = (local_id, local_intf)
                remote_end = (remote_id, remote_intf)

                # 判断 Link 是否是重复的，只有新的 Link 才被写入 Links[]
                if (local_end, remote_end) not in links_list and \
                        (remote_end, local_end) not in links_list:
                    links_list.append((local_end, remote_end))
                    links.append({
                        'id': link_id,
                        'source': local_id,
                        'target': remote_id,
                        'srcIfName': local_intf,
                        'tgtIfName': remote_intf
                    })
                    link_id += 1

        except:
            continue

    return links

links = get_links()

topology_dict = {
    'nodes': nodes,
    'links': links
}

DATA_JS_FILENAME = 'app/data.js'
FILE_HEAD = 'var topologyData = '

def write_data_js(topology_json, header=FILE_HEAD, dst=DATA_JS_FILENAME):
    with open(dst, 'w') as f:
        f.write(header)
        f.write(json.dumps(topology_json, indent=4, sort_keys=True))
        f.write(';')

write_data_js(topology_dict)