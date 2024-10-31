import dataclasses
import decimal
from datetime import datetime, date, timedelta
import requests
from databases.aiomysql_client import AioMySQLClient
from databases.qiye_base_business import QiyeBaseBusiness
from logs.mylogging import MyLogging

if __name__ == '__main__':

    def send(entity_id="91110101MA003TBX2T"):
        url = f"http://192.168.50.206:9200/qiye_base_business/_search?pretty&from=0&size=100"
        body = {
            "query": {
                "match": {
                    "entityId": entity_id
                }
            }
        }
        headers = {"Content-Type": "application/json;charset=utf-8"}
        response = requests.session().request(method="POST", url=url, headers=headers, json=body, verify=False)
        source = response.json()["hits"]["hits"][0]["_source"]

        # merged_dict = {**data, **base_data}
        return source


    async def query(sql="select * from qiye_base_business limit 2160000, 300000"):
        logger = MyLogging.getLogger()
        logger.setLevel(10)
        mysql_client = await AioMySQLClient.get_instance()
        # result_business = await mysql_client.execute_query("select * from qiye_base_business limit 10")
        no = 2160000
        async for row in mysql_client.async_for_cursor(sql):
            row: dict
            # print(result_business[0]) 取出来每一行 *离散作为参数 []合成列表
            # qiye_base_businesses = [QiyeBaseBusiness(*row) for row in result_business]
            business = QiyeBaseBusiness(*row.values())
            if isinstance(business.regDate, date):
                business.regDate = business.regDate.strftime("%Y-%m-%d")

            merged_dict: dict = send(business.entityId)
            # dumps = json.dumps(merged_dict)

            # 字符串转Decimal保持8位小数并四舍五入
            if "regCapital" in merged_dict:
                merged_dict["regCapital"] = decimal.Decimal(str(merged_dict["regCapital"])).quantize(
                    decimal.Decimal('1e-8'), rounding=decimal.ROUND_HALF_UP)
            # 保持数据和mysql默认值一致
            if "colleguesNum" not in merged_dict:
                merged_dict["colleguesNum"] = 0
            if "phoneContactType" not in merged_dict:
                logger.debug(f"{dict(sorted(merged_dict.items()))}", extra={"user": f"{no} "})
                merged_dict["phoneContactType"] = 0

            date_format = "%Y-%m-%dT%H:%M:%S"
            if "createTime" in merged_dict:
                if len(merged_dict["createTime"]) > 19:
                    # 加0.5秒即四舍五入，再减去毫秒部分
                    create_time = datetime.strptime(merged_dict["createTime"], "%Y-%m-%dT%H:%M:%S.%f")
                    rounded_time = create_time + timedelta(seconds=0.5)
                    rounded_time = rounded_time - timedelta(microseconds=rounded_time.microsecond)
                    merged_dict["createTime"] = rounded_time
                else:
                    merged_dict["createTime"] = datetime.strptime(merged_dict["createTime"], "%Y-%m-%dT%H:%M:%S")
            if "updateTime" in merged_dict:
                if len(merged_dict["updateTime"]) > 19:
                    # 加0.5秒即四舍五入，再减去毫秒部分
                    updateTime = datetime.strptime(merged_dict["updateTime"], "%Y-%m-%dT%H:%M:%S.%f")
                    rounded_time = updateTime + timedelta(seconds=0.5)
                    rounded_time = rounded_time - timedelta(microseconds=rounded_time.microsecond)
                    merged_dict["updateTime"] = rounded_time
                else:
                    merged_dict["updateTime"] = datetime.strptime(merged_dict["updateTime"], "%Y-%m-%dT%H:%M:%S")

            # 把 dataclasses 对象转字典
            business_dict = dataclasses.asdict(business)
            # 移除value等于None的键值对
            business_dict = {k: v for k, v in business_dict.items() if v is not None}

            business_dict.pop("operated")
            business_dict.pop("migrated")
            business_dict.pop("id")

            if business_dict != merged_dict:
                # 字典排序
                logger.warning(f"{sorted(business_dict.items())}", extra={"user": f"{no} "})
                logger.warning(f"{sorted(merged_dict.items())}", extra={"user": f"{no} "})
            elif no % 10000 == 0:
                logger.info(business.entityId, extra={"user": f"{no} "})

            no += 1


    AioMySQLClient.run(run_main=query)
