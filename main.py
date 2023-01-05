from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import datetime
import os

ck =  '1'

headerscookie = {'cookie': ck}
headers = {
    'authority': 'm.facebook.com',
    'accept': '*/*',
    'accept-language': 'vi,en;q=0.9,vi-VN;q=0.8,fr-FR;q=0.7,fr;q=0.6,en-US;q=0.5',
    'cookie': ck,
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


def Token():
    home = requests.get('https://business.facebook.com/adsmanager/manage/accounts', headers=headers).text
    uid_page = home.split('adAccountId: \\"')[1].split('\\"')[0]
    ads_page = requests.get(f'https://business.facebook.com/adsmanager/manage/accounts?act={uid_page}',
                            headers=headers).text
    token = ads_page.split('window.__accessToken="')[1].split('"')[0]
    print(token)
    return token

dictPixel = {   1:
            {'id': '449542583803743',
            'name': 'Pixel Nữ 25+'},
            2 :
            {'id' : '969729217756981',
            'name': 'Pixel 25+'},
            3:
            {'id' : '753517695875549',
            'name': 'Pixel 30+'},
            }

def SharePixel(idAcc_Ads, idPixel, token):
    result = ""
    dataid = {"account_id": idAcc_Ads, "business": "606755291020760",
              "access_token": token}
    url = "https://graph.facebook.com/v15.0/" + dictPixel[idPixel]['id'] +"/shared_accounts/"
    response = requests.post(url, data=dataid, headers=headerscookie).json()

    try:
        result = response['success']
        result = "✅ Share pixel " + dictPixel[idPixel]['name']  + " thành công: " + idAcc_Ads
    except:
        try:
            result =  "⛔ " + response['error']['error_user_msg']
        except:
            result = "⛔ " + response['error']['message']
    print(dictPixel[idPixel]['name'])
    print(response)
    return result

def getStats(idPixel, flagstat, token):


    pram = {"aggregation": "event_total_counts",
            "start_time": "2022-01-01T09:45:32",
            "access_token": token}
    url = "https://graph.facebook.com/v15.0/" + dictPixel[idPixel]['id'] + "/stats"
    resstock = requests.get(url, params=pram, headers=headerscookie).json()
    print(resstock['data'][0])
    starttime = dictPixel[idPixel]['name'] +  '\n' + "Tổng từ ngày: "  + resstock['data'][0]['start_time'][0:10] +  '\n'

    res =  starttime  +  '\n'
    listValue = resstock['data'][0]['data']
    chart = ''
    listCheck = ['ClickEvent','PageView','GeneralEvent','AddToCart','InitiateCheckout','Purchase']
    for i in range(0, len(listValue) -1):
        if resstock['data'][0]['data'][i]['value'] in listCheck:
            chart += resstock['data'][0]['data'][i]['value'] + ': ' + str(resstock['data'][0]['data'][i]['count']) + '\n'
    return res + chart

def Checkcurrli(day):
    payload = {
        'log': 'namvenus',
        'pwd': 'Nam123nam10tr$',
        'wp-submit': 'Log+In'
    }

    today = datetime.datetime.now()
    fday = today - datetime.timedelta(days=day)

    today = today.replace(microsecond=0).isoformat()
    fday = fday.replace(hour=0, minute=0, second=0)
    fday = fday.replace(microsecond=0).isoformat()

    after = fday
    before =  today

    session = requests.Session()
    res = session.post('https://curilic.com/wp-login.php/', data=payload)
    res = session.get('https://curilic.com/wp-admin/admin.php?page=wc-admin&path=%2Fanalytics%2Foverview')
    res = res.text
    wpcookie = res[int(res.find('createNonceMiddleware( "')) + 24: int(res.find('createNonceMiddleware( "')) + 34]
    print(wpcookie)
    headerwp = {'x-wp-nonce': wpcookie}
    reponse = session.get(
        'https://curilic.com/wp-json/wc-analytics/reports/performance-indicators?after=' + after + '&before=' + before + '&stats=revenue/total_sales,revenue/net_revenue,orders/orders_count,orders/avg_order_value,products/items_sold,revenue/refunds,coupons/orders_count,coupons/amount&_locale=user',
        headers=headerwp).json()
    print(reponse)
    timeline = "Từ : " + after + '\n'\
            + 'Đến: ' + before + '\n\n'\
            '-------OVER VIEW-------\n'
    res = timeline + '\n'\
          +  reponse[0]['label'] + ': ' + str(round(reponse[0]['value'], 2)) + '\n' \
          + reponse[1]['label'] + ': ' + str(round(reponse[1]['value'], 2)) + '\n' \
          + reponse[2]['label'] + ': ' + str(round(reponse[2]['value'], 2)) + '\n' \
          + reponse[3]['label'] + ': ' + str(round(reponse[3]['value'], 2)) + '\n' \
          + reponse[4]['label'] + ': ' + str(round(reponse[4]['value'], 2)) + '\n' \
          + reponse[5]['label'] + ': ' + str(round(reponse[5]['value'], 2)) + '\n' \
          + reponse[6]['label'] + ': ' + str(round(reponse[6]['value'], 2)) + '\n' \

    return res


async def CheckRev(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.text)
    message = update.message.text

    if message[4:6].isnumeric():
        day = int(message[4:6])
        res = Checkcurrli(day)
        await  update.message.reply_text(res)
    else:
        await  update.message.reply_text('⛔ sai cú pháp , get all revalue /cu , or get x day /cu x ( day = now - x')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.text)
    message = update.message
    listAcc = message.text.split()
    print(listAcc)
    idAcc_Ads = message.text[5:50]
    idpixel = int(message.text[3])
    flagStat = message.text[5:9]



    if len(message.text) ==4:
        token = Token()
        res = getStats(idpixel, flagStat, token)
        await update.message.reply_text(res)
        return

    if len(idAcc_Ads) == 0:
        await update.message.reply_text('⛔ Có vẻ bạn chưa nhập id Ads acc')
    elif len(idAcc_Ads) > 0 and len(idAcc_Ads) < 6:
        await update.message.reply_text('⛔ id Ads Acc bạn nhập là quá ngắn, Vui lòng kiểm tra lại')
    else:
        await update.message.reply_text("🤖Đang share pixel cho " + str(len(listAcc)-1) + " acc")
        token = Token()
        for i in range(1, len(listAcc)):
            print(i)
            res = SharePixel(listAcc[i], idpixel, token)
            await update.message.reply_text(res)




app = ApplicationBuilder().token("5774231926:AAFwJiyc57wH-UX_Q0sazXZL3gZERhySOUI").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("px1", share))
app.add_handler(CommandHandler("px2", share))
app.add_handler(CommandHandler("px3", share))
app.add_handler(CommandHandler("px3", share))
app.add_handler(CommandHandler("cu", CheckRev))


app.run_polling()