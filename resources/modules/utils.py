import datetime as dt
import requests


def log(text):
    print((dt.datetime.now(), 'AstreamWeb : {}'.format(text)))


class ApiError(Exception):
    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return self.exception


def postHtml(url, form_data={}, headers={}, compression=True, NoCookie=None):
    try:
        _user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 ' + \
                      '(KHTML, like Gecko) Chrome/13.0.782.99 Safari/535.1'
        headers['User-Agent'] = _user_agent
        if compression:
            headers['Accept-Encoding'] = 'gzip'
        resp = requests.request('POST', url=url, headers=headers, data=form_data)
        data = resp.content
        resp.close()
    except Exception as e:
        if 'SSL23_GET_SERVER_HELLO' in str(e):
            # notify('Oh oh','Python version to old - update to Krypton or FTMC')
            raise requests.HTTPError()
        else:
            # notify('Oh oh','It looks like this website is down.')
            raise requests.HTTPError()
        return None
    return data
