# -*- coding:utf-8 -*-

from api.lib.cmdb.const import AutoDiscoveryType

PRIVILEGED_USERS = ("cmdb_agent", "worker", "admin")

NET_DEVICE_NAMES = {"switch", 'router', 'firewall', 'printer'}

DEFAULT_INNER = [
    dict(name="阿里云", en="aliyun", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-aliyun'}, "en": "aliyun"}),
    dict(name="腾讯云", en="tencentcloud", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-tengxunyun'}, "en": "tencentcloud"}),
    dict(name="华为云", en="huaweicloud", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-huaweiyun'}, "en": "huaweicloud"}),
    dict(name="AWS", en="aws", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-aws'}, "en": "aws"}),

    dict(name="VCenter", en="vcenter", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'cmdb-vcenter'}, "category": "private_cloud", "en": "vcenter"}),
    dict(name="KVM", en="kvm", type=AutoDiscoveryType.HTTP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'ops-KVM'}, "category": "private_cloud", "en": "kvm"}),


    dict(name="Nginx", en="nginx", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-nginx'}, "en": "nginx", "collect_key": "nginx"}),
    dict(name="Apache", en="apache", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-apache'}, "en": "apache", "collect_key": "apache"}),
    dict(name="Tomcat", en="tomcat", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-tomcat'}, "en": "tomcat", "collect_key": "tomcat"}),
    dict(name="MySQL", en="mysql", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-mySQL'}, "en": "mysql", "collect_key": "mysql"}),
    dict(name="MSSQL", en="mssql", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
             option={'icon': {'name': 'caise-SQLServer'}, "en": "mssql", "collect_key": "sqlserver"}),
    dict(name="Oracle", en="oracle", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-oracle'}, "en": "oracle", "collect_key": "oracle"}),
    dict(name="Redis", en="redis", type=AutoDiscoveryType.COMPONENTS, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-redis'}, "en": "redis", "collect_key": "redis"}),

    dict(name="交换机", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-jiaohuanji'}}),
    dict(name="路由器", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-luyouqi'}}),
    dict(name="防火墙", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-fanghuoqiang'}}),
    # dict(name="打印机", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
    #      option={'icon': {'name': 'caise-dayinji'}}),
    dict(name="光纤交换机", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-fiber'}}),
    dict(name="F5", type=AutoDiscoveryType.SNMP, is_inner=True, is_plugin=False,
         option={'icon': {'name': 'caise-F5'}}),
]

CLOUD_MAP = {
    "aliyun": [
        {
            "category": "计算",
            "items": ["云服务器 ECS", "云服务器 Disk"],
            "map": {
                "云服务器 ECS": {"template": "templates/aliyun_ecs.json", "mapping": "ecs"},
                "云服务器 Disk": {"template": "templates/aliyun_ecs_disk.json", "mapping": "evs"},
            },
            "collect_key_map": {
                "云服务器 ECS": "ali.ecs",
                "云服务器 Disk": "ali.ecs_disk",
            },
        },
        {
            "category": "网络与CDN",
            "items": [
                "内容分发CDN",
                "负载均衡SLB",
                "专有网络VPC",
                "交换机Switch",
            ],
            "map": {
                "内容分发CDN": {"template": "templates/aliyun_cdn.json", "mapping": "CDN"},
                "负载均衡SLB": {"template": "templates/aliyun_slb.json", "mapping": "loadbalancer"},
                "专有网络VPC": {"template": "templates/aliyun_vpc.json", "mapping": "vpc"},
                "交换机Switch": {"template": "templates/aliyun_switch.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "内容分发CDN": "ali.cdn",
                "负载均衡SLB": "ali.slb",
                "专有网络VPC": "ali.vpc",
                "交换机Switch": "ali.switch",
            },
        },
        {
            "category": "存储",
            "items": ["块存储EBS", "对象存储OSS"],
            "map": {
                "块存储EBS": {"template": "templates/aliyun_ebs.json", "mapping": "evs"},
                "对象存储OSS": {"template": "templates/aliyun_oss.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "块存储EBS": "ali.ebs",
                "对象存储OSS": "ali.oss",
            },
        },
        {
            "category": "数据库",
            "items": ["云数据库RDS MySQL", "云数据库RDS PostgreSQL", "云数据库 Redis"],
            "map": {
                "云数据库RDS MySQL": {"template": "templates/aliyun_rds_mysql.json", "mapping": "mysql"},
                "云数据库RDS PostgreSQL": {"template": "templates/aliyun_rds_postgre.json", "mapping": "postgresql"},
                "云数据库 Redis": {"template": "templates/aliyun_redis.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "云数据库RDS MySQL": "ali.rds_mysql",
                "云数据库RDS PostgreSQL": "ali.rds_postgre",
                "云数据库 Redis": "ali.redis",
            },
        },
    ],
    "tencentcloud": [
        {
            "category": "计算",
            "items": ["云服务器 CVM"],
            "map": {
                "云服务器 CVM": {"template": "templates/tencent_cvm.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "云服务器 CVM": "tencent.cvm",
            },
        },
        {
            "category": "CDN与边缘",
            "items": ["内容分发CDN"],
            "map": {
                "内容分发CDN": {"template": "templates/tencent_cdn.json", "mapping": "CDN"},
            },
            "collect_key_map": {
                "内容分发CDN": "tencent.cdn",
            },
        },
        {
            "category": "网络",
            "items": ["负载均衡CLB", "私有网络VPC", "子网"],
            "map": {
                "负载均衡CLB": {"template": "templates/tencent_clb.json", "mapping": "loadbalancer"},
                "私有网络VPC": {"template": "templates/tencent_vpc.json", "mapping": "vpc"},
                "子网": {"template": "templates/tencent_subnet.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "负载均衡CLB": "tencent.clb",
                "私有网络VPC": "tencent.vpc",
                "子网": "tencent.subnet",
            },
        },
        {
            "category": "存储",
            "items": ["云硬盘CBS", "对象存储COS"],
            "map": {
                "云硬盘CBS": {"template": "templates/tencent_cbs.json", "mapping": "evs"},
                "对象存储COS": {"template": "templates/tencent_cos.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "云硬盘CBS": "tencent.cbs",
                "对象存储COS": "tencent.cos",
            },
        },
        {
            "category": "数据库",
            "items": ["云数据库 MySQL", "云数据库 PostgreSQL", "云数据库 Redis"],
            "map": {
                "云数据库 MySQL": {"template": "templates/tencent_rdb.json", "mapping": "mysql"},
                "云数据库 PostgreSQL": {"template": "templates/tencent_postgres.json", "mapping": "postgresql"},
                "云数据库 Redis": {"template": "templates/tencent_redis.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "云数据库 MySQL": "tencent.rdb",
                "云数据库 PostgreSQL": "tencent.rds_postgres",
                "云数据库 Redis": "tencent.redis",
            },
        },
    ],
    "huaweicloud": [
        {
            "category": "计算",
            "items": ["云服务器 ECS"],
            "map": {
                "云服务器 ECS": {"template": "templates/huaweicloud_ecs.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "云服务器 ECS": "huawei.ecs",
            },
        },
        {
            "category": "CDN与智能边缘",
            "items": ["内容分发网络CDN"],
            "map": {
                "内容分发网络CDN": {"template": "templates/huawei_cdn.json", "mapping": "CDN"},
            },
            "collect_key_map": {
                "内容分发网络CDN": "huawei.cdn",
            },
        },
        {
            "category": "网络",
            "items": ["弹性负载均衡ELB", "虚拟私有云VPC", "子网"],
            "map": {
                "弹性负载均衡ELB": {"template": "templates/huawei_elb.json", "mapping": "loadbalancer"},
                "虚拟私有云VPC": {"template": "templates/huawei_vpc.json", "mapping": "vpc"},
                "子网": {"template": "templates/huawei_subnet.json", "mapping": "vswitch"},
            },
            "collect_key_map": {
                "弹性负载均衡ELB": "huawei.elb",
                "虚拟私有云VPC": "huawei.vpc",
                "子网": "huawei.subnet",
            },
        },
        {
            "category": "存储",
            "items": ["云硬盘EVS", "对象存储OBS"],
            "map": {
                "云硬盘EVS": {"template": "templates/huawei_evs.json", "mapping": "evs"},
                "对象存储OBS": {"template": "templates/huawei_obs.json", "mapping": "objectStorage"},
            },
            "collect_key_map": {
                "云硬盘EVS": "huawei.evs",
                "对象存储OBS": "huawei.obs",
            },
        },
        {
            "category": "数据库",
            "items": ["云数据库RDS MySQL", "云数据库RDS PostgreSQL"],
            "map": {
                "云数据库RDS MySQL": {"template": "templates/huawei_rds_mysql.json", "mapping": "mysql"},
                "云数据库RDS PostgreSQL": {"template": "templates/huawei_rds_postgre.json", "mapping": "postgresql"},
            },
            "collect_key_map": {
                "云数据库RDS MySQL": "huawei.rds_mysql",
                "云数据库RDS PostgreSQL": "huawei.rds_postgre",
            },
        },
        {
            "category": "应用中间件",
            "items": ["分布式缓存Redis"],
            "map": {
                "分布式缓存Redis": {"template": "templates/huawei_dcs.json", "mapping": "redis"},
            },
            "collect_key_map": {
                "分布式缓存Redis": "huawei.dcs",
            },
        },
    ],
    "aws": [
        {
            "category": "计算",
            "items": ["云服务器 EC2"],
            "map": {
                "云服务器 EC2": {"template": "templates/aws_ec2.json", "mapping": "ecs"},
            },
            "collect_key_map": {
                "云服务器 EC2": "aws.ec2",
            },
        },
        {"category": "网络与CDN", "items": [], "map": {}, "collect_key_map": {}},
    ],
    "vcenter": [
        {
            "category": "计算",
            "items": [
                "主机",
                "虚拟机",
                "主机集群"
            ],
            "map": {
                "主机": "templates/vsphere_host.json",
                "虚拟机": "templates/vsphere_vm.json",
                "主机集群": "templates/vsphere_cluster.json",
            },
            "collect_key_map": {
                "主机": "vsphere.host",
                "虚拟机": "vsphere.vm",
                "主机集群": "vsphere.cluster",
            },
        },
        {
            "category": "网络",
            "items": [
                "网络",
                "标准交换机",
                "分布式交换机",
            ],
            "map": {
                "网络": "templates/vsphere_network.json",
                "标准交换机": "templates/vsphere_standard_switch.json",
                "分布式交换机": "templates/vsphere_distributed_switch.json",
            },
            "collect_key_map": {
                "网络": "vsphere.network",
                "标准交换机": "vsphere.standard_switch",
                "分布式交换机": "vsphere.distributed_switch",
            },
        },
        {
            "category": "存储",
            "items": ["数据存储", "数据存储集群"],
            "map": {
                "数据存储": "templates/vsphere_datastore.json",
                "数据存储集群": "templates/vsphere_storage_pod.json",
            },
            "collect_key_map": {
                "数据存储": "vsphere.datastore",
                "数据存储集群": "vsphere.storage_pod",
            },
        },
        {
            "category": "其他",
            "items": ["资源池", "数据中心", "文件夹"],
            "map": {
                "资源池": "templates/vsphere_pool.json",
                "数据中心": "templates/vsphere_datacenter.json",
                "文件夹": "templates/vsphere_folder.json",
            },
            "collect_key_map": {
                "资源池": "vsphere.pool",
                "数据中心": "vsphere.datacenter",
                "文件夹": "vsphere.folder",
            },
        },
    ],
    "kvm": [
        {
            "category": "计算",
            "items": ["虚拟机"],
            "map": {
                "虚拟机": "templates/kvm_vm.json",
            },
            "collect_key_map": {
                "虚拟机": "kvm.vm",
            },
        },
        {
            "category": "存储",
            "items": ["存储"],
            "map": {
                "存储": "templates/kvm_storage.json",
            },
            "collect_key_map": {
                "存储": "kvm.storage",
            },
        },
        {
            "category": "network",
            "items": ["网络"],
            "map": {
                "网络": "templates/kvm_network.json",
            },
            "collect_key_map": {
                "网络": "kvm.network",
            },
        },
    ],
}
