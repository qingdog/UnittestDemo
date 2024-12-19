import asyncio
import logging
import re
import time

import requests

from utils.aiomysql_client import AioMySQLClient

headers = {"content-type": "application/json;charset=UTF-8",
           "authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyRGVwdElkIjoxMDMsInVzZXJfaWQiOjEsInVzZXJfa2V5IjoiNGU3NWE2MTItNWE5MC00NzhlLTgwYjMtMDM1OTY0ZWE3ODhiIiwidXNlcm5hbWUiOiJhZG1pbiJ9.tb5M4tKly5QaSPTLrxw2KaIfVwueNze0Ji1d2BIHbBdEYxmfFZBa6np68Cet9Tnftss5eBpDMChf7X2kBh4jow"}
session = requests.session()
base_url = "http://192.168.50.202:9999"


def qiye_collect_info_save(entity_id, company, method="POST"):
    url = "/test-api/qiyelibrary/qiye/collectInfo/save"
    body = {"entityId": entity_id, "enterpriseCategory": None, "siteArea": None, "getBankloanFlag": None,
            "hasOtherBranches": None, "publicInstitutionFlag": None, "patentInventionCount": None,
            "patentUtilityModelCount": None, "patentSoftwareCopyrightCount": None, "patentDesignCount": None,
            "veteranCount": 0, "graduateCount": 0, "avgSalary": None, "socialSecurityEmployeeCount": 10,
            "seniorTitleCount": None, "intermediateTitleCount": None, "juniorTitleCount": None, "doctorCount": None,
            "masterCount": None, "bachelorCount": None, "freshGraduateCount": None, "contactPerson": None,
            "contactPhone": None, "lastYearOperatingIncome": 100, "lastYearAssetLiabilityRatio": None,
            "lastYearFixedAssetsTotal": None, "lastYearRAndDExpense": None, "lastYearValueAddedTax": None,
            "lastYearAverageSalary": 1000, "remainingContributionAmount": None, "preferentialPolicyFlag": "",
            "company": company, "isAllUpdate": 0}

    response = session.request(method=method, url=base_url + url, headers=headers, json=body, verify=True)
    return response.json()


def qiye_begin_match_project(url, body, method="POST"):
    response = session.request(method=method, url=base_url + url, headers=headers, json=body, verify=True)
    return response.json()


def qiye_project_reportable(url, body, method="POST", index=5):
    response = session.request(method=method, url=base_url + url, headers=headers, json=body, verify=True)

    if len(response.json()["data"]["list"]) == 0:
        if index >= 0:
            index -= 1
            time.sleep(3)
            return qiye_project_reportable(url="/test-api/qiyelibrary/qiye/project/reportable", body=body)
    return response.json()


async def query(
        sql: str):
    mysql_client = AioMySQLClient()
    # result_business = await mysql_client.execute_query("select * from qiye_base_business limit 10")
    results = []
    async for row in mysql_client.async_for_cursor(sql=sql):
        results.append(row)
    return results  # 返回结果列表


async def main():
    # 广东省
    reg_provinces_code = "440000"
    reg_city_code = "440300"
    reg_district_code = "440300"

    # 固定一个省份 所有不同区域下的单个企业
    # select reg_district,reg_district_code,count(*) from qiye_base_business where reg_provinces_code =440000 group by reg_district_code limit 30
    sql1 = (
        f"select entity_id,company,reg_provinces_code,reg_city_code,reg_district_code,reg_address, reg_provinces,reg_city,reg_district from qiye_base_business "
        f"where reg_provinces_code = {reg_provinces_code} group by reg_district_code")

    # 固定省份 不同城市的企业
    # select reg_city,reg_city_code,count(*) from qiye_base_business where reg_provinces_code =440000 group by reg_city_code limit 30
    sql2 = (
        f"select entity_id,company,reg_provinces_code,reg_city_code,reg_district_code,reg_address, reg_provinces,reg_city,reg_district from qiye_base_business "
        f"where reg_provinces_code ={reg_provinces_code} group by reg_city_code")

    # 固定省市 不同区域的企业
    # select reg_district_code,reg_district,count(*) from qiye_base_business where reg_provinces_code =440000 and reg_city_code = 440300 group by reg_district_code
    sql3 = (
        f"select entity_id,company,reg_provinces_code,reg_city_code,reg_district_code,reg_address, reg_provinces,reg_city,reg_district from qiye_base_business "
        f"where reg_provinces_code ={reg_provinces_code} and reg_city_code = {reg_city_code} group by reg_district_code")

    collects = {}
    mysql_client = await AioMySQLClient.get_instance()
    # result_business = await query(sql3)
    async for qiye_base_business in mysql_client.fetchmany_until_over(sql=sql3, size=10):
        for base_business in qiye_base_business:
            print(base_business["entity_id"], end=" ")
            if base_business["entity_id"] and base_business["company"]:
                collect_info = qiye_collect_info_save(entity_id=base_business["entity_id"],
                                                      company=base_business["company"])

                match_project = qiye_begin_match_project(
                    url=f'/test-api/qiyelibrary/qiye/begin/matchProject/{base_business["entity_id"]}', body=None,
                    method="get")
                # collects["entity_id"] = collect_info
        print()
        # 睡眠12s，等10条数据匹配

        delay_seconds = 12
        print(f"正在睡眠{delay_seconds}秒", end="")
        for _ in range(int(delay_seconds)):
            print(".", end="", flush=True)  # 每秒打印一个点，不换行
            await asyncio.sleep(1)  # 每次延迟一秒
        print(" sleep done.", end="\n", flush=True)

        for base_business in qiye_base_business:
            if base_business["entity_id"] and base_business["company"]:
                body = {"pageNo": 1, "pageSize": 10, "entityId": f"{base_business["entity_id"]}"}
                project_reportable = qiye_project_reportable("/test-api/qiyelibrary/qiye/project/reportable", body)

                is_match = False
                # 如果企业有城市编码
                re_text = ""
                if base_business["reg_city_code"]:
                    reg_city = base_business["reg_city"]

                    is_district = False
                    # 如果企业有区域编码
                    if base_business["reg_district_code"]:
                        is_district = True
                        reg_district = base_business["reg_district"]
                        for project in project_reportable["data"]["list"]:
                            project_name = project["projectName"]
                            re_text = reg_city + "-" + reg_district + "测试匹配"
                            if re.search(re_text, project_name):
                                is_match = True
                    else:
                        for project in project_reportable["data"]["list"]:
                            project_name = project["projectName"]
                            re_text = reg_city + "测试匹配"
                            if re.search(re_text, project_name):
                                is_match = True
                            # 如果没有区域 则不应该匹配上
                            if re.search(project_name,
                                         r".+-.+-.*(市|区|县|城|旗|盟|自治州|岛|街道|镇|乡|产业基地|园|港|部|区.|委|委会)测试匹配$"):
                                is_match = False
                                break
                else:
                    if base_business["reg_provinces_code"] is None:
                        logging.warning("跳过...")
                    else:
                        reg_provinces = base_business["reg_provinces"]
                        is_match = False

                        for project in project_reportable["data"]["list"]:
                            project_name = project["projectName"]
                            re_text = reg_provinces + "测试匹配"
                            if re.search(re_text, project_name):
                                is_match = True

                            project_name = project["projectName"]
                            reg_provinces_code = base_business["reg_provinces_code"]
                            if re.search(project_name,
                                         r".+-.*(市|盟|区|州|直辖县级|县|香港岛|九龙|新界|澳门半岛|氹仔岛|路环岛|钓鱼岛)测试匹配$"):
                                is_match = False
                                break
                if not is_match:
                    logging.error(f"{base_business["entity_id"]} {base_business["company"]} 【匹配文本：{re_text}】 匹配失败！")

    session.close()


if __name__ == '__main__':
    # 启动 asyncio 事件循环并调用 main 函数
    asyncio.run(main())
