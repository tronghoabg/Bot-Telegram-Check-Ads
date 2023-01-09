import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import time
import threading

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
headerCK3 = {
            'authority': 'mbasic.facebook.com',
            'accept': '*/*',
            'origin': 'mbasic.facebook.com',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
headerCK2 = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authority': 'business.facebook.com',
            'accept': '*/*',
            'origin': 'https://business.facebook.com',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }

def getToken(ck):
    stt = 1
    listADS = ''
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

async def testcomand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('test command')

def getListGroup(ck, token):
    listGroups = ''
    stt=0
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me/groups?fields=administrator,id,member_count&limit=1000&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'data' in json:
        objGroups = json['data']
        templeObj = []
        for group in objGroups:
            if group['administrator'] == True:
                stt+=1
                obj = {}
                obj['stt'] = stt
                obj['id'] = group['id']
                obj['membercount'] = str(group['member_count']) + ' Member'
                templeObj.append(obj)
        for f in templeObj:
            for i in f:
                listGroups+=str(f[i]) + '/'
            listGroups+='\n'
    if listGroups== '':
        listGroups+=str(stt) + '/No Groups\n'
    return listGroups


def getListBM(ck, token , fbdt):
    stt = 0
    listBM = ''
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me/businesses?fields=id,created_time,is_disabled_for_integrity_reasons,sharing_eligibility_status,allow_page_management_in_www,can_use_extended_credit,name,timezone_id,timezone_offset_hours_utc,verification_status,owned_ad_accounts{account_status},client_ad_accounts{account_status},owned_pages,client_pages,business_users,owned_pixels{name}&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'data' in json:
        stt+=1
        objBm = json['data']
        templeObjBM = []
        for bm in objBm:
            templeObj = {}
            templeObj['stt'] = stt
            templeObj['id'] = bm['id']
            if 'allow_page_management_in_www' in bm:
                templeObj['status'] = 'Acti'
            else:
                templeObj['status'] = 'Die'
            
            if 'can_use_extended_credit' in bm:
                templeObj['limit']= '$250+'
            else:
                templeObj['limit'] = bm['can_use_extended_credit']

            lvBM = getBmlimit(ck, bm['id'], fbdt)
            templeObj['lv'] = 'BM' + str(lvBM)
            templeObjBM.append(templeObj)
        for f in templeObjBM:
            for i in f:
                listBM+=str(f[i]) + '/'
            listBM+='\n'
    if listBM == '':
        listBM+= str(stt) + '/No BM\n'
    return listBM
def getBmlimit(ck, idBm, fbdt):
    headerCK['cookie'] = ck
    url = 'https://business.facebook.com/business/adaccount/limits/?business_id=' + idBm + '&__a=1&fb_dtsg=' + fbdt
    json = requests.get(url=url, headers=headerCK).text
    try:
        bmLevel = json.split('adAccountLimit":')[1].split('}')[0]
        levelBM = bmLevel
    except:
        levelBM = 0
        pass
    return levelBM

def getListFanPage(ck,token):
    stt = 0
    listPage = ''
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me?fields=accounts.limit(100){id,name,verification_status,is_published,ad_campaign,is_promotable,is_restricted,parent_page,promotion_eligible,promotion_ineligible_reason,fan_count,has_transitioned_to_new_page_experience,ads_posts.limit(100),picture}&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    if 'accounts' in json:
        stt+=1
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
        listPage+= str(stt+1) + '/No FanPage\n'
    return listPage

def getListAccInfo(ck, token, fbdt):
    stt=0
    listADS = ''
    headerCK['cookie'] = ck
    url = 'https://graph.facebook.com/v15.0/me/adaccounts?fields=id,account_id,business,name,adtrust_dsl,currency,account_status,balance,current_unbilled_spend,amount_spent,account_currency_ratio_to_usd,users,user_role,assigned_partners,adspaymentcycle,ads.limit(1000){effective_status}&limit=1000&sort=name_ascending&access_token=' + token
    json = requests.get(url=url,headers=headerCK).json()
    user_id = requests.get(url='https://graph.facebook.com/v15.0/me?fields=id&access_token=' + token, headers=headerCK).json()
    user_id = user_id['id']
    if 'data' in json:
        objListAcc = json['data']
        templeArrObj = []
        
        for acc in objListAcc:
            stt+=1
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
            card = getCard(ck, user_id, acc['account_id'], fbdt)
            templeObj['card'] = card
            templeArrObj.append(templeObj)
        for u in templeArrObj:
            for i in u:
                if i=='card' and u[i] != '':
                    listADS+='\n'
                    listADS+= u[i]
                else:
                    listADS+=str(u[i]) + '/'
            listADS+='\n'
    return listADS

def getCard(ck, user, act, fbdt):
    listCard =''
    headerCK2['cookie'] = ck
    fromdata = {
        'av': user,
        '__user': user,
        '__a': 1,
        'variables': '{"paymentAccountID":' +act+'}',
        'doc_id':'5369940383036972',
        'fb_dtsg': fbdt,
    }
    url = 'https://business.facebook.com/api/graphql/'
    r = requests.post(url, data=fromdata, headers=headerCK2).json()
    if 'data' in r:
        objCard = r['data']['billable_account_by_payment_account']['billing_payment_account']['billing_payment_methods']
        for card in objCard:
            usability = card['usability']
            if usability == 'UNVERIFIED_OR_PENDING_AUTH':
                usability = 'NEEDS'
            card = card['credential']
            if card['__typename'] == 'ExternalCreditCard':
                listCard+= ' -' +card['card_association'] + ': ' + usability + '\n'
            else:
                listCard+= ' -' +card['__typename'] + ': ' + usability + '\n '
    return listCard

def getThresHoldAcc(acc, ck, token):
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

def getFbdt(ck):
    headerCK3['cookie'] = ck
    json = requests.get(url = 'https://mbasic.facebook.com', headers=headerCK3).text
    fb_dtsg = json.split('name="fb_dtsg" value="')[1].split('"')[0]
    return fb_dtsg

def checkAd(ck):
    start_time = time.time()
    token = getToken(ck)
    caption = 'Cookies này đã hết hạn'
    if token != 'NO':
        fbdt = getFbdt(ck)

        #infoAD = threading.Thread(target=getListAccInfo, args=(ck, token, fbdt,))
        #infoPage = threading.Thread(target=getListFanPage, args=(ck, token,))
        #infoBM = threading.Thread(target=getListBM, args=(ck, token, fbdt,))
        #infoGroups = threading.Thread(target=getListGroup, args=(ck, token,))

        #infoAD.start()
        #infoPage.start()
        #infoBM.start()
        #infoGroups.start()

        #infoAD.join()
        #infoPage.join()
        #infoBM.join()
        #infoGroups.join()
        
        infoAD = getListAccInfo(ck, token, fbdt)
        infoPage = getListFanPage(ck, token)
        infoBM = getListBM(ck, token, fbdt)
        infoGroups = getListGroup(ck, token)


        caption =   '✅ List ADS\n'\
                    +infoAD +'\n'\
                    +'✅ List FanPage\n'\
                    +infoPage+'\n'\
                    +'✅ List BM\n'\
                    + infoBM +'\n'\
                    +'✅ List Groups\n'\
                    + infoGroups +'\n'
    print("--- %s seconds ---" % (time.time() - start_time))
    return caption

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.find('datr') > -1 and text.find('c_user') > -1:
        await context.bot.delete_message(update.message.chat.id, update.message.message_id)
        start = text.find('c_user') + 7
        end = text.find(';', start + 1)
        c_user = text[start:end]
        print("Checking for: " + c_user)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="💥 Checking for: " + c_user)
        mess = checkAd(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=mess)


if __name__ == '__main__':
    application = ApplicationBuilder().token('5712740653:AAFreDzJcJMwmYXULecs3-l5rHOpY5XSb78').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    start_fbdt = CommandHandler('fbdt', testcomand)
    application.add_handler(start_fbdt)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    application.run_polling()