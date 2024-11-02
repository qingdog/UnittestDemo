import logging

import requests

from databases.aiomysql_client import AioMySQLClient

headers = {"content-type": "application/json;charset=UTF-8",
           "authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyRGVwdElkIjoxMDMsInVzZXJfaWQiOjEsInVzZXJfa2V5IjoiYjkwMmNhMzMtMTI2MS00NzZjLWE3OGMtMjViNGZjMTJjMjFiIiwidXNlcm5hbWUiOiJhZG1pbiJ9.UVOdE02aAg1V_322M_wk144C3r87uwzOufQxV60_SO3uxryAzYWU12Mi0sZIPE8YtA5Qk_QpwWs383qkJ1pHbg"}
session = requests.session()
base_url = "http://192.168.50.202:9999"


def policy_dept_select(url, body, method="POST"):
    response = session.request(method=method, url=base_url + url, headers=headers, json=body, verify=True)
    return response.json()


def policy_project_add(city_name, dept_id, name, province, city, area, rank, rankName, address, mobile, method="POST"):
    url = "/test-api/policylibrary/policy/project/add"
    body = {"name": f"{city_name}测试匹配", "establishedTime": 0, "salesIncome": 0, "equipmentCost": 0,
            "infomationCost": 0,
            "staffNum": 0, "developmentCost": 0, "projectSumCost": 0, "entryExitCost": 0, "subsidyType": "[]",
            "phone": mobile, "address": address, "matchIndustryIds": "[100]", "type": 1,
            "review": "1", "matchIndustry": [{"name": "制造业", "level": 1, "id": 100, "parentid": 0}], "area": area,
            "city": city, "province": province, "deptName": name,
            "deptId": dept_id, "rank": rank, "rankName": rankName, "reportInfoDTOS": [], "associationInfoDTOS": [],
            "extensionDTO": {"originText": "<p>1</p>", "preferentialPolicy": "", "reportCondition": "<p>2</p>",
                             "reportMaterial": "", "fileVoList": []}, "fromSource": 2}

    response = session.request(method=method, url=base_url + url, headers=headers, json=body, verify=True)
    return response.json()


def policy_dept_add(area, city, province, name, rank=4):
    if area is None:
        rank = 3
        if city is None:
            rank = 2
    url = "/test-api/policylibrary/policy/dept/add"
    body = {"area": area, "categoryDTOList": [{"categoryId": "1", "childCategoryIds": [300]},
                                              {"categoryId": "null", "childCategoryIds": [1]}],
            "city": city, "deptCategory": [300], "name": name,
            "province": province, "publishStatus": 0, "rank": rank, "superDeptIds": []}
    response = session.request(method="POST", url=base_url + url, headers=headers, json=body, verify=True)
    return response.json()


async def main():
    mysql_client = await AioMySQLClient.get_instance()
    mysql_client = await mysql_client.connect(host="192.168.50.221", port=3306, user="liqi_cloud_test",
                                              password="G85BkJywwRxY5XBy", db="liqi_cloud_test")
    # 根据26个省份新增组织部门，新增项目
    # lqc_city_s = await query(mysql_client, sql="select * from lqc_city where leveltype = 1")
    lqc_city_s = await query(mysql_client, sql="select * from lqc_city where leveltype = 2 ")
    # lqc_city_s = await query(mysql_client, sql="select * from lqc_city where leveltype = 3")
    # lqc_city_s = await query(mysql_client, sql="select * from lqc_city where leveltype = 3 and parentid=710400")

    area = None
    for lqc_city in lqc_city_s:
        area = {"id": lqc_city["id"], "name": lqc_city["name"]}
        city_name = lqc_city["name"]
        if city_name == "和平区":
            pass

        url = "/test-api/policylibrary/policy/dept/select"
        body = {"name": f"{city_name}发展", "page": 1, "size": 10}
        dept = policy_dept_select(url, body, method="POST")
        dept_list = dept["data"]["list"]

        # if len(dept_list) == 0:
        lqc_city_s2 = await query(mysql_client, sql=f"select * from lqc_city where id ={lqc_city["parentid"]}")
        city = None
        if len(lqc_city_s2) > 0:
            city_name = lqc_city_s2[0]["name"] + "-" + city_name
            city = {"id": lqc_city_s2[0]["id"], "name": lqc_city_s2[0]["name"]}
            city_name2 = lqc_city_s2[0]["name"]
            body = {"name": f"{city_name}发展", "page": 1, "size": 10}
            # body = {"name": f"{city_name}发展1", "page": 1, "size": 10}
            dept = policy_dept_select(url, body, method="POST")
            dept_list2 = dept["data"]["list"]
            if len(dept_list2) == 0:
                lqc_city_s3 = await query(mysql_client,
                                          sql=f"select * from lqc_city where id ={lqc_city_s2[0]["parentid"]}")
                province = None
                if len(lqc_city_s3) > 0:
                    if lqc_city_s3[0]["id"] != 100000 and lqc_city_s3[0]["id"] != 100001:
                        province = {"id": lqc_city_s3[0]["id"], "name": lqc_city_s3[0]["name"]}
                        city_name = lqc_city_s3[0]["name"] + "-" + city_name
                        city_name3 = lqc_city_s3[0]["name"]
                        body = {"name": f"{city_name}发展", "page": 1, "size": 10}
                        dept = policy_dept_select(url, body, method="POST")
                        dept_list3 = dept["data"]["list"]
                pass
                if province is None:
                    dept_add = policy_dept_add(province, area, city, f"{city_name}发展")
                else:
                    dept_add = policy_dept_add(area, city, province, f"{city_name}发展")
                logging.warning(f"{city_name} {dept_add}")

        body = {"name": f"{city_name}发展", "page": 1, "size": 10}
        dept = policy_dept_select(url, body, method="POST")
        dept_list = dept["data"]["list"]

        if len(dept_list) == 0:
            logging.warning(
                f"{city_name}发展 ===================================================== 没有这个组织部门！{lqc_city}")
            continue
        dept0 = dept_list[0]
        name = dept0["province"]["name"]
        if dept0["city"]:
            name = name + "-" + dept0["city"]["name"]
        if dept0["area"]:
            name = name + "-" + dept0["area"]["name"]
        project_add = policy_project_add(name, dept0["id"], dept0["name"], dept0["province"], dept0["city"],
                                         dept0["area"], dept0["rank"], dept0["rankName"], dept0["address"],
                                         dept0["mobile"], method="POST")
        if project_add["code"] != 200:
            print(f"{project_add} {name}")
        # update lqc_project_base_info set match_or_not = 1,publis_status = 1 where name rlike "测试匹配"

    pass


async def query(mysql_client, sql: str):
    # result_business = await mysql_client.execute_query("select * from qiye_base_business limit 10")
    results = []
    async for row in mysql_client.async_for_cursor(sql=sql):
        results.append(row)
    return results  # 返回结果列表


if __name__ == '__main__':
    # main()
    AioMySQLClient.run(run_main=main)
