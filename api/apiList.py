class ApiList():
    __headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Platform": "Y%2fnOm9Q6SjVaSxnxNdJgeQ%3d%3d",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    __zs_login = "http://120.25.209.187:8080/recruit.students/login/in?"

    __dvd = "http://api.deiyoudian.com"

    __dvd_login = f"{__dvd}/api/user/seller/v1/user/userloginbypassword"

    def getZsLogin(self):
        return self.__zs_login

    def get_dvd_headers(self):
        return self.__headers

    def get_dvd_login(self):
        return self.__dvd_login

