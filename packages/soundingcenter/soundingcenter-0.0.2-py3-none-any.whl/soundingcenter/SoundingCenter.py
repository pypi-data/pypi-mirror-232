from requests import Response, get, post


class Api:
    def __init__(self, base_url: str, username: str, password: str, logging: bool = False):
        self.base_url = base_url
        self.auth = (username, password)
        self.logging = logging

    def log(self, response: Response):
        if self.logging and not response.ok:
            print(response.status_code)
            print(response.content)

    def get(self, path: str):
        request = get(
            url=f'{self.base_url}/{path}',
            headers={
                'Accept': 'application/json',
            },
            auth=self.auth,
        )

        self.log(request)
        return request

    def post(self, path: str, json):
        request = post(
            url=f'{self.base_url}/{path}',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            auth=self.auth,
            json=json,
        )

        self.log(request)
        return request

    def user(self):
        return self.get('user')

    def create_user(self, email: str, password: str, role: str, name: str):
        return self.post('user', {
            'email': email,
            'password': password,
            'role': role,
            'name': name,
        })

    def create_station(self, name: str, station_type: str, wmo_id: int):
        return self.post('station', {
            'name': name,
            'type': station_type,
            'wmo_id': wmo_id
        })

    def attach_station_to_user(self, user_id: int, station_id: int):
        return self.post(f'user/{user_id}/attachStation/{station_id}', {})
