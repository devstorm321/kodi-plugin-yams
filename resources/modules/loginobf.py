import re
import traceback

BASE_URL = "https://einthusan.tv"
LOGIN_USERNAME = "kilavan8@gmail.com"
LOGIN_PASSWORD = "654321"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 " \
             "Safari/537.36 "
LANGUAGE = "tamil"


def login_info(s, refererurl):
    language = LANGUAGE
    headers = {
        "Origin": BASE_URL,
        "Referer": refererurl,
        "User-Agent": USER_AGENT}
    try:
        html1 = s.get(
            BASE_URL + "/login/?lang=" + language, headers=headers, allow_redirects=False,
        ).text

        csrf1 = re.findall("data-pageid=[\"'](.*?)[\"']", html1)[0]

        if "&#43;" in csrf1:
            csrf1 = csrf1.replace("&#43;", "+")

        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Referer"] = BASE_URL + "/login/?lang=" + language

        postdata2 = {
            "xEvent": "Login",
            "xJson": '{"Email":"'
                     + LOGIN_USERNAME
                     + '","Password":"'
                     + LOGIN_PASSWORD
                     + '"}',
            "arcVersion": 3,
            "appVersion": 59,
            "tabID": csrf1 + "48",
            "gorilla.csrf.Token": csrf1,
        }
        html2 = s.post(
            BASE_URL + "/ajax/login/?lang=" + language,
            headers=headers,
            cookies=s.cookies,
            data=postdata2,
            allow_redirects=False,
        )

        html3 = s.get(
            BASE_URL
            + "/account/?flashmessage=success%3A%3A%3AYou+are+now+logged+in.&lang="
            + language,
            headers=headers,
            cookies=s.cookies,
        ).text

        csrf3 = re.findall("data-pageid=[\"'](.*?)[\"']", html3)[0]

        postdata4 = {
            "xEvent": "notify",
            "xJson": '{"Alert":"SUCCESS","Heading":"AWESOME!","Line1":"You+are+now+logged+in.","Buttons":[]}',
            "arcVersion": 3,
            "appVersion": 59,
            "tabID": csrf1 + "48",
            "gorilla.csrf.Token": csrf3,
        }

        html4 = s.post(
            BASE_URL + "/ajax/account/?lang=" + language,
            headers=headers,
            cookies=s.cookies,
            data=postdata4,
        )
    except:
        traceback.print_exc()
        return s, False

    return s, True
