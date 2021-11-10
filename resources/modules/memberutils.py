import re
import sys, io
import urllib.error, urllib.parse
from requests import request

from datetime import date
import calendar

import threading
import time

try:
    import simplejson as json
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    import json

import xbmcaddon
import xbmcgui
import xbmc, xbmcvfs
import os

import stripe

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

stripe.api_key = 'sk_live_4QOTmGxmSVkkU1wKnnouddBt'

amember_api_key = 'scl7gadiEXhus1p2wpvT'
amember_api_stripe = 'http://yamshost.org/amember/api/stripe-token?_key=%s&user_id=%s&stripe_id=%s'
amember_api_users = 'http://yamshost.org/amember/api/users'
amember_api_user_info = 'http://yamshost.org/amember/api/users?_key=%s&_filter[login]=%s'
amember_api_invoices = 'http://yamshost.org/amember/api/invoices'
amember_api_cancel_invoice = 'http://yamshost.org/amember/api/invoices/%s'
amember_api_products = 'http://yamshost.org/amember/api/products?_key=%s&_filter[%s]=%s'
amember_api_check_access = 'http://yamshost.org/amember/api/check-access/by-login?_key=%s&login=%s'
amember_api_user_access = 'http://yamshost.org/amember/api/access?_key=%s&_filter[user_id]=%s&_filter[product_id]=%s&_count=200'
amember_api_user_access_page = 'http://yamshost.org/amember/api/access?_key=%s&_filter[user_id]=%s&_filter[product_id]=%s&_page=%s&_count=200'

astreamweb_code_verification = 'http://astreamweb.com/codeverification.txt'

__settings__ = xbmcaddon.Addon(id='plugin.video.yams')

addonPath = xbmcvfs.translatePath(__settings__.getAddonInfo('path'))
storage = os.path.join(addonPath,'resources/storage.db')

# Currency: USD, EUR, GBP

class keepAlive(threading.Thread):
    def __init__(self, threadID, name, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.isAlive = True

    def run(self):
        print(("Keeping Window Alive: " + self.name))

        while self.isAlive:
            time.sleep(self.delay)
        print(("Allowing Window to be destroyed: " + self.name))

    def killIt(self):
        self.isAlive = False

class card_payment(xbmcgui.WindowXMLDialog):
    def show(self):
        self.opened = True
        self.doModal()

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin('Skin.Reset(AnimeWindowXMLDialogClose)')
        xbmc.executebuiltin('Skin.SetBool(AnimeWindowXMLDialogClose)')

        self.name = ''
        self.card_number = ''
        self.expiry_month = ''
        self.expiry_year = ''
        self.sec_cvv = ''
        self.zip = ''
        self.opened = False
        self.status = False

        # keep alive window
        self.thread1 = keepAlive(1, "Thread-1", 5)
        self.thread1.start()

        pass

    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            xbmc.executebuiltin('Skin.Reset(AnimeWindowXMLDialogClose)')
            xbmc.executebuiltin('Skin.ResetSettings()')
            self.close()
        pass

    def onFocus(self, controlID):
        pass

    def onClick(self, controlID):
        if controlID == 44:
            xbmc.executebuiltin('Skin.Reset(AnimeWindowXMLDialogClose)')
            xbmc.executebuiltin('Skin.ResetSettings()')
            self.close()
        elif controlID == 45:
            self.name = self.getControl(38).getText()
            self.card_number = self.getControl(39).getText()
            self.expiry_month = self.getControl(40).getText()
            self.expiry_year = self.getControl(41).getText()
            self.sec_cvv = self.getControl(42).getText()
            self.zip = self.getControl(43).getText()
            self.status = True

            xbmc.executebuiltin('Skin.Reset(AnimeWindowXMLDialogClose)')
            xbmc.executebuiltin('Skin.ResetSettings()')
            self.close()
        pass

    def getData(self):
        data = {'status': self.status, 'name': self.name, 'number': self.card_number, 'month': self.expiry_month, 'year': self.expiry_year, 'cvv': self.sec_cvv, 'zip': self.zip}
        return data

    def __del__(self):
        print('Destroying Payment Class')

    def killIt(self):
        if self.opened:
            dialog = xbmcgui.Dialog()
            dialog.ok('IMPORTANT MESSAGE', '', 'If you are running Kodi 14.2 or lower there is a chance your system will crash due to a bug in the handling of the popup windows. If this is the case please restart Kodi and your profile will automatically be updated.', '')
        self.thread1.killIt()

def stripeCommand(params):
    try:
        if params['task'] == 'token':
            stripeResult = stripe.Token.create(
                                               card={
                                               'name': params['name'],
                                               'number': params['number'],
                                               'exp_month': params['month'],
                                               'exp_year': params['year'],
                                               'cvc': params['cvc'],
                                               'address_zip': params['zip']
                                               })

            dic = json.dumps(stripeResult)
            data = json.loads(dic)
            result = {'status': True, 'token': data['id']}
        elif params['task'] == 'customer':
            stripeResult = stripe.Customer.create(
                                                  email=params['email'],
                                                  description='Customer for %s' % params['email'],
                                                  source=params['token']
                                                  )

            dic = json.dumps(stripeResult)
            data = json.loads(dic)
            result = {'status': True, 'cust_id': data['id']}
        elif params['task'] == 'charge':
            stripeResult = stripe.Charge.create(
                                                amount=params['amount'],
                                                currency=params['currency'],
                                                customer=params['customer'],
                                                description=params['sub']
                                                )
            dic = json.dumps(stripeResult)
            data = json.loads(dic)
            result = {'status': True, 'charge_id': data['id']}
        else:
            result = {'status': False, 'reason': 'Unknown Stripe Command'}

        return result
    except stripe.error.CardError as e:
        body = e.json_body
        err  = body['error']
        __log(err['message'])

        dialog = xbmcgui.Dialog()
        dialog.ok("Stripe Error: %s" % err['code'], err['message'])
        pass
    except stripe.error.InvalidRequestError as e:
        body = e.json_body
        err  = body['error']
        dialog = xbmcgui.Dialog()
        dialog.ok("Stripe Error: Invalid Request", err['message'])
        pass
    except stripe.error.AuthenticationError as e:
        body = e.json_body
        err  = body['error']
        dialog = xbmcgui.Dialog()
        dialog.ok("Stripe Error: Authentication Error", err['message'])
        pass
    except stripe.error.APIConnectionError as e:
        body = e.json_body
        err  = body['error']
        dialog = xbmcgui.Dialog()
        dialog.ok("Stripe Error: Communication", err['message'])
        pass
    except stripe.error.StripeError as e:
        body = e.json_body
        err  = body['error']
        dialog = xbmcgui.Dialog()
        dialog.ok("Stripe Error", err['message'])
        pass
    except Exception as e:
        dialog = xbmcgui.Dialog()
        dialog.ok("AStreamWeb Error", "Ooops something went wrong and we were unable to process the command. Please try again.")
        pass

    result = {'status': False, 'reason': 'Stripe Error'}
    return result

def amemberCommand(params):
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    if params['task'] == 'customer':
        post_data = {'_key' : amember_api_key,
                    'format': 'xml',
                    'login': params['login'],
                    'pass': params['pass'],
                    'email': params['email'],
                    'name_f': params['name_f'],
                    'name_l': params['name_l']}
        post_data = urllib.parse.urlencode(post_data)
        data = request('POST', amember_api_users, headers=headers, data=post_data)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'token': data[0]['user_id']}
    elif params['task'] == 'invoice':
        begin = date.today()
        expire = add_months(begin, 1)

        if params['product_rebill_times'] == '0':
            status = 1
        else:
            status = 2

        post_data = {'_key': amember_api_key,
                    'user_id': params['user_id'],
                    'paysys_id': 'stripe',
                    'currency': params['currency'],
                    'first_subtotal': params['product_first_price'],
                    'first_discount': '0.00',
                    'first_tax': '0.00',
                    'first_shipping': '0.00',
                    'first_total': params['product_first_price'],
                    'first_period': params['product_first_period'],
                    'is_confirmed': 1,
                    'status': status,
                    'nested[invoice-items][0][item_id]': params['product_id'],
                    'nested[invoice-items][0][item_type]': 'product',
                    'nested[invoice-items][0][item_title]': params['product_title'],
                    'nested[invoice-items][0][item_description]': params['product_desc'],
                    'nested[invoice-items][0][qty]': 1,
                    'nested[invoice-items][0][first_discount]': '0.00',
                    'nested[invoice-items][0][first_price]': params['product_first_price'],
                    'nested[invoice-items][0][first_tax]': '0.00',
                    'nested[invoice-items][0][first_shipping]': '0.00',
                    'nested[invoice-items][0][first_total]': params['product_first_price'],
                    'nested[invoice-items][0][first_period]': params['product_first_period'],
                    'nested[invoice-items][0][currency]': params['currency'],
                    'nested[invoice-items][0][billing_plan_id]': params['billing_plan_id'],
                    'nested[invoice-payments][0][user_id]': params['user_id'],
                    'nested[invoice-payments][0][paysys_id]': 'stripe',
                    'nested[invoice-payments][0][receipt_id]': params['receipt_id'],
                    'nested[invoice-payments][0][currency]': params['currency'],
                    'nested[invoice-payments][0][amount]': params['product_first_price'],
                    'nested[access][0][user_id]': params['user_id'],
                    'nested[access][0][product_id]': params['product_id'],
                    'nested[access][0][begin_date]': '%s-%s-%s' % (begin.year, begin.month, begin.day),
                    'nested[access][0][expire_date]': '%s-%s-%s' % (expire.year, expire.month, expire.day)}

        if status == 2:
            post_data.update({'rebill_times': params['product_rebill_times'],
                              'rebill_date': '%s-%s-%s' % (expire.year, expire.month, expire.day),
                              'second_subtotal': params['product_second_price'],
                              'second_discount': '0.00',
                              'second_tax': '0.00',
                              'second_shipping': '0.00',
                              'second_total': params['product_second_price'],
                              'second_period': params['product_second_period'],
                              'nested[invoice-payments][0][rebill_date]': '%s-%s-%s' % (expire.year, expire.month, expire.day),
                              'nested[invoice-items][0][rebill_times]': params['product_rebill_times'],
                              'nested[invoice-items][0][second_discount]': '0.00',
                              'nested[invoice-items][0][second_price]': params['product_second_price'],
                              'nested[invoice-items][0][second_tax]': '0.00',
                              'nested[invoice-items][0][second_shipping]': '0.00',
                              'nested[invoice-items][0][second_total]': params['product_second_price'],
                              'nested[invoice-items][0][second_period]': params['product_second_period']})

        post_data = urllib.parse.urlencode(post_data)

        data = request('POST', amember_api_invoices, headers=headers, data=post_data)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'invoice': json.dumps(data)}
    elif params['task'] == 'link_stripe':
        url = amember_api_stripe % (amember_api_key, params['user_id'], params['stripe_id'])
        data = request('GET', url, headers=headers)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'products': json.dumps(data)}
    elif params['task'] == 'products':
        url = amember_api_products % (amember_api_key, 'comment', 'KODI')
        data = request('GET', url, headers=headers)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'products': json.dumps(data)}
    elif params['task'] == 'product_detail':
        url = amember_api_products % (amember_api_key, 'product_id', params['product_id'])
        data = request('GET', url, headers=headers)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'product_detail': json.dumps(data)}
    elif params['task'] == 'check_access':
        url = amember_api_check_access %(amember_api_key, params['login'])
        data = request('GET', url, headers=headers)
        result = data.json()
    elif params['task'] == 'user_info':
        url = amember_api_user_info %(amember_api_key, params['login'])
        data = request('GET', url, headers=headers)
        result = data.json()
    elif params['task'] == 'user_access':
        if params['page']:
            url = amember_api_user_access_page % (amember_api_key, params['user_id'], params['product_id'], params['pagenum'])
        else:
            url = amember_api_user_access % (amember_api_key, params['user_id'], params['product_id'])
        data = request('GET', url, headers=headers)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'subscriptions': json.dumps(data)}
    elif params['task'] == 'cancel_subscription':
        cancel = date.today()

        post_data = {'_key' : amember_api_key,
                     'status': 3,
                     'tm_cancelled': '%s-%s-%s' % (cancel.year, cancel.month, cancel.day),
                     'rebill_date': ''}

        data = request('PUT', amember_api_cancel_invoice  %params['invoice_id'], headers=headers, data=post_data)
        data = data.json()

        if 'error' in data:
            result = {'status': False, 'reason': data['message']}
        else:
            result = {'status': True, 'cancel': json.dumps(data)}
    elif params['task'] == 'exclusion':
        excludes = list()

        url = amember_api_check_access %(amember_api_key, params['login'])
        data = request('GET', url, headers=headers)
        user = data.json()

        if user['ok']:
            if 'subscriptions' in user:
                subscriptions = user['subscriptions']
                for sub in subscriptions:
                    excludes.append(int(sub))

        result = {'status': True, 'excludes': excludes}
    elif params['task'] == 'check_expire':
        url = amember_api_user_access % (amember_api_key, params['user_id'], params['product_id'])
        data = request('GET', url, headers=headers)
        data = data.json()

        size = data['_total']
        if size > 200:
            # calculate last page and call json again
            page = size / 200
            offset = size % 200
            if offset == 0:
                page = page - 1

            url = amember_api_user_access_page % (amember_api_key, params['user_id'], params['product_id'], page)
            data = request('GET', url, headers=headers)
            data = data.json()

        invoice_id = ''
        access_id = 0
        for index in range(data['_total']):
            if data[str(index)]['access_id'] > access_id:
                access_id = data[str(index)]['access_id']
                invoice_id = data[str(index)]['invoice_id']

        if invoice_id is not None:
            post_data = {'_key' : amember_api_key}

            data = request('PUT', amember_api_cancel_invoice  %invoice_id, headers=headers, data=post_data)
            data = data.json()
            __log(data)

            if data[0]['status'] == '1' or data[0]['tm_cancelled'] is not None:
                result = {'status': True, 'isExpire': True}
            else:
                result = {'status': True, 'isExpire': False}
        else:
            result = {'status': True, 'isExpire': False}
    else:
        result = {'status': False, 'reason': 'Unknown aMember API Call'}

    return result

def captureUserInfo():
    dialog = xbmcgui.Dialog()
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    if dialog.yesno('AStreamWeb Account Creation',
                    'Do you wish to proceed with creating an account?'):
        name_f = dialog.input('Please Enter Your First Name', type=xbmcgui.INPUT_ALPHANUM)
        name_l = dialog.input('Please Enter Your Last Name', type=xbmcgui.INPUT_ALPHANUM)
        email = dialog.input('Please Enter Your Email Address', type=xbmcgui.INPUT_ALPHANUM)

        validUser = False
        while not validUser:
            username = dialog.input('Please Enter Your Desired Username', type=xbmcgui.INPUT_ALPHANUM)
            url = amember_api_check_access %(amember_api_key, username)
            data = request('GET', url, headers=headers)
            result = data.json()
            if not result['ok']:
                validUser = True
            else:
                dialog.ok('Username Taken',
                          'That username already exists. Please try another.')

        isSame = False
        while not isSame:
            pass_1 = dialog.input('Please Enter A Password', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            __log(pass_1)
            pass_2 = dialog.input('Please Enter The Same Password Again', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            __log(pass_2)

            if pass_1 == pass_2:
                isSame = True
            else:
                dialog.ok('Password Error',
                          'The passwords you entered do not match. Please make sure you enter the same password twice. Ensure CAPSLOCK is turned off.')


        user = {'error': False, 'name_f': name_f, 'name_l': name_l, 'email': email, 'pass': pass_1, 'username': username}
    else:
        user = {'error': True}
    return user

def codeverification(username):
    response = urllib.request.urlopen(astreamweb_code_verification)
    data = response.read()
    data = json.loads(data)

    if username == '' and data['active'] == 1:
        dialog = xbmcgui.Dialog()
        dialog.ok('Locked for new subscriptions',
                  'We are currently not allowing new members to AstreamWeb')
        return False

    return True
    
def fetchStorage():
    with io.open(storage, 'r') as data_file:
        data = json.load(data_file)
    return data

def writeStorage(customer_id=None, user_id=None, email=None):
    data = {'customer_id': customer_id, 'user_id': user_id, 'email': email}
    with io.open(storage, 'wb') as data_file:
        json.dump(data, data_file)

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return date(year, month, day)

def __log(text):
    import datetime as dt

    print((dt.datetime.now(), 'AstreamWeb addon: %s' % text))
