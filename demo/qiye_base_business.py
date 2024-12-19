import decimal
from dataclasses import dataclass
from datetime import date


@dataclass
class QiyeBaseBusiness:
    """COMMENT='工商信息'"""
    id: int  # '自增id',
    entityId: str  # '统一社会信用代码/唯一id',
    company: str  # '公司名称',
    companyFormerName: str  # '曾用名',
    legalName: str  # '法定代表人',
    regCapital: decimal.Decimal  # '注册资本',
    regCapitalType: int  # '注册资本类型。1：人民币；2：美元；3：欧元；4：其他；5：全部',
    regDate: date  # '成立日期',
    entStatus: int  # '经营状态',
    licenseNumber: str  # '工商注册号',
    industryLv1: int  # '行业一级分类编码',
    industryLv1Name: str  # '行业一级分类名',
    industryLv2: int  # '行业二级分类',
    industryLv2Name: str  # '行业二级分类名',
    entType: int  # '0：全部；1：有限责任公司；2：股份有限公司；3：国有企业；4：外商投资企业；5：个人独资企业；6：有限合伙人；"\r\n+
    # "7：普通合伙人；8：个体工商户；9：联营企业；10：集体所有值；11：其他',
    entTypeStr: str  # '企业类型名',
    colleguesNum: int  # '人员规模',
    opFrom: str  # '经营期限自',
    opTo: str  # '经营期限至',
    regOrg: str  # '登记机关',
    checkDate: str  # '核准日期',
    regAddress: str  # '注册地址',
    opScope: int  # '经营范围',
    phone: str  # '联系方式',
    phoneType: str  # '联系方式类型，多个逗号隔开。1：手机；2：座机',
    email: str  # '邮箱',
    offcialSite: str  # '官网',
    regProvinces: str  # '省',
    regProvincesCode: int  # '省码',
    regCity: str  # '市',
    regCityCode: int  # '市码',
    regDistrict: str  # '区',
    regDistrictCode: int  # '区码',
    regBuilding: str  # '楼层',
    logo: str  # 'logo',
    tags: str  # '企业标签，逗号分隔。1：独角兽；2：瞪羚企业；3：创新企业；4：高新企业；5：央企；6：国企；7：中国500强；8：世界500强；9：上市企业；0：全部',
    ocid: int  # 'ocid',
    createTime: date  # '创建时间',
    updateTime: date  # '更新时间',
    phoneContactType: int  # '联系方式类型，1：手机；2：座机；3：手机和座机',
    operated: int
    migrated: int

