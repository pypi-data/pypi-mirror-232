from talkytimes.base import AbstractAutomation


class TalkyTimesAutomation(AbstractAutomation):

    def save_users(self, *, min_value: int, max_value: int):
        page = min_value
        service = "/platform/account/search"
        body = {"filters": {"ageTo": 90, "ageFrom": 18, "gender": None},
                "limit": 100}
        while page < max_value:
            body["page"] = page
            response = self.driver.execute_script(
                script=self.__get_script(service=service, body=body)
            )
            data = response.get("data")
            users = data.get("users")
            if not len(users) > 0:
                break
            for user in users:
                self.db.create_or_update(
                    profile_id=self.profile_id,
                    external_id=str(user.get("id")),
                    status=user.get("is_online")
                )
            page += 1

    def save_users_chat(self, *, min_value: int, max_value: int):
        users = self.db.get_users(profile_id=self.profile_id)
        count = min_value
        for user in users[min_value:max_value]:
            external_id = user.get("id")
            service = f"/platform/chat/restriction?idRegularUser={external_id}"
            response = self.driver.execute_script(
                script=self.__get_script(service=service)
            )
            data = response.get("data")
            self.db.update_user(
                id=user.get("id"),
                item=dict(
                    messages=data.get("messagesLeft"),
                    emails=data.get("lettersLeft"),
                    customer_status=data.get("is_online")
                )
            )
            count += 1
