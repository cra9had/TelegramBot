import requests
from loguru import logger
from settings import email, password


logger.add("logs.log", format="{name} {message}")


class Api:
    host = "https://dci-nl.pq.hosting/"
    session = requests.Session()

    @logger.catch
    def get_server_status(self, server_id: int) -> str:
        url = self.host + "api/dci/v3/server"
        response = self.session.get(self.host + "api/dci/v3/server")
        logger.info(f"{url} {response.status_code}")
        for server in response.json()["list"]:
            if server["id"] == server_id:
                return server["power_status"]

    @logger.catch
    def change_power_status(self, server_id: int, power_status: str) -> None:
        url = f"{self.host}api/dci/v3/server/{server_id}/{power_status}"
        response = self.session.post(f"{self.host}api/dci/v3/server/{server_id}/{power_status}", json={})
        logger.info(f"{url} {response.status_code}")

    @logger.catch
    def auth(self) -> None:
        url = self.host + "auth/v4/public/token"
        response = self.session.post(url, json={"email": email, "password": password},
                                     verify=False)
        logger.info(f"{url} {response.status_code}")
        token = response.json()["token"]
        self.session.headers = {
            "cookie": "_ga=GA1.2.225725015.1654530805; _gid=GA1.2.805829616.1654530805; _ym_uid=1654593427636434740; "
                      "_ym_d=1654593427; _ym_isad=2; supportOnlineTalkID=6kUCOPfDCoxEPDAtvmkPytMx2Oqybe3U; lang6=ru; "
                      f"ses6={token}",
            "x-xsrf-token": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/102.0.0.0 Safari/537.36 ",
            "isp-box-instance": "true"
        }
        print(token)


if __name__ == '__main__':
    api = Api()
    api.auth()
    api.change_power_status(136, "power_reset")

