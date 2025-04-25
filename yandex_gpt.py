import os
from dotenv import load_dotenv
import requests
import argparse

from models import EventInput, PlanUpdateInput


class YandexGPT:
    def __init__(self, url, token, folder_id):
        self.url = url
        self.token = token
        self.folder_id = folder_id

    def __get_data(self):
        data = {}
        data["modelUri"] = f"gpt://{self.folder_id}/yandexgpt"
        data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}

        return data

    def generate_plan(self, data: EventInput) -> str:
        yandex_req = self.__get_data()
        yandex_req["messages"] = [
            {
                "role": "system",
                "text": "Вы - полезный помощник, который составляет подробные и продуманные планы групповых мероприятий. На основе предоставленных сведений о мероприятии составьте творческий и практичный план, учитывающий тип мероприятия, количество участников, место проведения и любые особые пожелания. Включите соответствующие идеи по расписанию, мероприятиям, необходимым материалам, бронированию (если это необходимо) и способам улучшения впечатлений.",
            },
            {
                "role": "user",
                "text": (
                    f"Пожалуйста, составь подробный и креативный план мероприятия на основе следующих данных:\n\n"
                    f"- Название: {data.title}\n"
                    f"- Описание: {data.description}\n"
                    f"- Тип мероприятия: {data.event_type}\n"
                    f"- Количество участников: {data.participants}\n"
                    f"- Дата: {data.event_date or 'TBD'}\n"
                    f"- Локация: {data.location or 'TBD'}\n"
                    f"- Особые пожелания: {data.user_prompt or 'Нет'}\n\n"
                    f"В плане укажи:\n"
                    f"- Предложенную структуру или расписание\n"
                    f"- Идеи для активностей\n"
                    f"- Советы с учетом количества участников\n"
                    f"- При необходимости — предложения по еде, декору или развлечениям\n"
                    f"- Полезные рекомендации, чтобы мероприятие прошло отлично"
                ),
            },
        ]
        response = self.__send_request_to_api(yandex_req)

        return self.__extract_llm_output(response)

    def update_plan(self, data: PlanUpdateInput) -> str:
        yandex_req = self.__get_data()
        yandex_req["messages"] = [
            {
                "role": "system",
                "text": "Вы - полезный помощник, который составляет подробные и продуманные планы групповых мероприятий. На основе предоставленных сведений о мероприятии составьте творческий и практичный план, учитывающий тип мероприятия, количество участников, место проведения и любые особые пожелания. Включите соответствующие идеи по расписанию, мероприятиям, необходимым материалам, бронированию (если это необходимо) и способам улучшения впечатлений.",
            },
            {
                "role": "user",
                "text": (
                    f"Пожалуйста, обнови план мероприятия на основе следующих данных:\n\n"
                    f"- Исходный план: {data.original_plan}\n"
                    f"- Комментарий пользователя: {data.user_comment or 'Нет'}\n\n"
                    f"Внеси изменения в соответствии с комментариями."
                ),
            },
        ]
        response = self.__send_request_to_api(yandex_req)

        return self.__extract_llm_output(response)

    def __send_request_to_api(self, yandex_req):
        return requests.post(
            self.url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            json=yandex_req,
        ).json()

    def __extract_llm_output(self, result_output) -> str:
        try:
            return result_output["result"]["alternatives"][0]["message"]["text"][
                "plan_text"
            ]
        except (KeyError, IndexError, TypeError):
            return "Error: Invalid response format"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_text", required=True, help="User text")
    args = parser.parse_args()

    load_dotenv()
    # read token and folder_id from environment variables or config
    url = os.environ["YC_URL"]
    token = os.environ["YC_API_KEY"]
    folder_id = os.environ["YC_FOLDER_ID"]

    yandexGpt = YandexGPT(url, token, folder_id)
