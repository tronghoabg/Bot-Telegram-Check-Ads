import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


listPage = ''
listADS = ''
listBM = ''
countUser = 0

headerCK = {
            'authority': 'm.facebook.com',
            'accept': '*/*',
            'origin': 'https://m.facebook.com',
            'referer': 'https://www.facebook.com',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }

def getToken( ck, stt):
    global listADS
    headerCK['cookie'] = ck
    
    ads_page = requests.get(f'https://www.facebook.com/adsmanager/manage/campaigns', headers=headerCK).text
    flag = ads_page.find('__accessToken=')
    if flag < 0:
        home = requests.get('https://business.facebook.com/adsmanager/manage/accounts', headers=headerCK).text
        flag = home.find('adAccountId: \\"')
        if flag > -1:
            uid_page = home.split('adAccountId: \\"')[1].split('\\"')[0]
            ads_page = requests.get(f'https://business.facebook.com/adsmanager/manage/accounts?act={uid_page}', headers=headerCK).text
            token = ads_page.split('window.__accessToken="')[1].split('"')[0]
        else:
            token = 'NO'
            listADS += str(stt) + '/Cookies Die\n'
    else:
        listADS += str(stt) + '/No Ads Acount\n'
        token = ads_page.split('window.__accessToken="')[1].split('"')[0]
    return token

def getListBM(ck, token , stt):
    global listBM
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me/businesses?fields=id,created_time,is_disabled_for_integrity_reasons,sharing_eligibility_status,allow_page_management_in_www,can_use_extended_credit,name,timezone_id,timezone_offset_hours_utc,verification_status,owned_ad_accounts{account_status},client_ad_accounts{account_status},owned_pages,client_pages,business_users,owned_pixels{name}&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'data' in json:
        objBm = json['data']
        

def getListFanPage(ck,token,stt):
    global listPage
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me?fields=accounts.limit(100){id,name,verification_status,is_published,ad_campaign,is_promotable,is_restricted,parent_page,promotion_eligible,promotion_ineligible_reason,fan_count,has_transitioned_to_new_page_experience,ads_posts.limit(100),picture}&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'accounts' in json:
        objPage = json['accounts']['data']
        templeObjPage = []
        for page in objPage:
            templeObj = {}
            templeObj['stt'] = stt
            templeObj['id'] = page['id']
            templeObj['like'] = str(page['fan_count']) + ' like'
            templeObjPage.append(templeObj)
        for f in templeObjPage:
                    for i in f:
                        listPage+=str(f[i]) + '/'
                    listPage+='\n'
    else:
        listPage+= str(stt) + '/No FanPage\n'

def getListAccInfo( ck, token, stt):
    global listADS
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me/adaccounts?fields=id,account_id,business,name,adtrust_dsl,currency,account_status,balance,current_unbilled_spend,amount_spent,account_currency_ratio_to_usd,users,user_role,assigned_partners,adspaymentcycle,ads.limit(1000){effective_status}&limit=1000&sort=name_ascending&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'data' in json:
        objListAcc = json['data']
        templeArrObj = []
        
        for acc in objListAcc:
            templeObj = {}
            templeObj['c_user'] = stt
            templeObj['status']  = getStatusAcc(acc['account_status'])
            if 'business' in acc:
                templeObj['adtype'] = "BM"
            else:
                templeObj['adtype'] = "AD"
            templeObj['currency'] =  acc['currency']
            templeObj['balance'] =  round(int(acc['balance'])*0.01)
            threshold = getThresHoldAcc(acc['account_id'], ck , token)
            templeObj['thress'] =  threshold
            if acc['adtrust_dsl'] == -1:
                templeObj['limit'] = 'No limit'
            else:
                templeObj['limit'] = round(int(acc['adtrust_dsl']))
            templeObj['spend'] =  round(int(acc['amount_spent']) * 0.01)
            templeArrObj.append(templeObj)
        for u in templeArrObj:
            for i in u:
                listADS+=str(u[i]) + '/'
            listADS+='\n'


def getThresHoldAcc( acc, ck, token):
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v14.0/act_' + acc + '?fields=account_id,owner_business,created_time,next_bill_date,currency,adtrust_dsl,timezone_name,timezone_offset_hours_utc,business_country_code,disable_reason,adspaymentcycle{threshold_amount},balance,is_prepay_account,owner,all_payment_methods{pm_credit_card{display_string,exp_month,exp_year,is_verified},payment_method_direct_debits{address,can_verify,display_string,is_awaiting,is_pending,status},payment_method_paypal{email_address},payment_method_tokens{current_balance,original_balance,time_expire,type}},total_prepay_balance,insights.date_preset(maximum){spend}&access_token='+ token + '&locale=en_US'
    json = requests.get(url=url,headers=headerCK).json()
    threshold = 0
    if 'adspaymentcycle' in json:
        threshold = round(int(json['adspaymentcycle']['data'][0]['threshold_amount']) * 0.01)
    return threshold

def getStatusAcc(num):
    switcher = {
        1: 'Acti',
        2: 'Die',
        3: 'Nợ',
        7: 'Pending Review',
        8: 'Pending Settlement',
        9: 'Preriod',
        100: 'Pending Closure',
        101: 'Close',
        201: 'Any Active',
        202: 'Any Close',
    }

    return switcher.get(num, 'Unknow')

def checkAd(ck):
    global countUser
    countUser+=1
    stt = countUser
    token = getToken(ck,stt)
    if token != 'NO':
        infoAD = getListAccInfo(ck, token, stt)
        infoPage = getListFanPage(ck, token, stt)
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global listADS, listPage, countUser
    text = update.message.text
    arrCk = text.split(',')
    if text.find('datr') > -1 and text.find('c_user') > -1:
        await context.bot.delete_message(update.message.chat.id, update.message.message_id)
    for ck in arrCk:
        if text.find('datr') > -1 and text.find('c_user') > -1:
            start = ck.find('c_user') + 7
            end = ck.find(';', start + 1)
            c_user = ck[start:end]
            print("Checking for: " + c_user)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="💥 Checking for: " + c_user)
            listADS = ''
            listPage = ''
            countUser = 0
            checkAd(ck)
            mess = '📊 List Ads Account\n' + listADS + '📘List Fan Page\n' + listPage
            print(mess)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess)


if __name__ == '__main__':
    application = ApplicationBuilder().token('5712740653:AAFreDzJcJMwmYXULecs3-l5rHOpY5XSb78').build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()