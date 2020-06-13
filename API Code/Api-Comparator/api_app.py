from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import JavascriptException

import time

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo


# # deployment environment variables
import os
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')


def getBrowser():
    return webdriver.Chrome(executable_path=os.environ.get(
        'CHROMEDRIVER_PATH'), chrome_options=chrome_options)


# # # local variables
# from selenium.webdriver.chrome.options import Options as ChromeOptions
# chrome_op = ChromeOptions()
# chrome_op.add_argument('--headless')


# def getBrowser():
#     return webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_op)


connection_url = 'mongodb+srv://admin:chitrankmishra@cluster0-nqpus.mongodb.net/MachineTranslation?retryWrites=true&w=majority'
app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient(connection_url)
ApiDatabase = client.get_database('MachineTranslation')

LanguageDataSet = ApiDatabase.LanguageDataSet
SiteData = ApiDatabase.SiteData


def makeCall(url, script, default):
    browser = getBrowser()
    response = default
    try:
        browser.get(url)
        srt_time = time.time()

        while(response == default):
            response = browser.execute_script(script)

        end_time = time.time()
        call_time = end_time-srt_time

    except JavascriptException:
        print(JavascriptException.args)

    except NoSuchElementException:
        print(NoSuchElementException.args)

    if(response != default):
        output = {
            'found': 1,
            'translation': response,
            'url': url,
            'calltime': call_time
        }
    else:
        output = {
            'found': 0,
            'translation': 'Not Available',
            'url': url,
            'calltime': 'Not Available'
        }

    browser.quit()
    return jsonify({'result': output})
    # return output


def openURL(url):
    browser = getBrowser()
    browser.get(url)
    browser.quit()


def compareString(s1, s2):  # edit distance algorithm
    dp = [[0 for i in range(len(s1)+1)] for j in range(len(s2)+1)]

    for i in range(0, len(s1)+1):
        dp[0][i] = i
    for i in range(0, len(s2)+1):
        dp[i][0] = i

    for i in range(1, len(s2)+1):
        for j in range(1, len(s1)+1):
            if(s1[j-1] == s2[i-1]):
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i-1][j-1], dp[i][j-1])+1

    return dp[len(s2)][len(s1)]


@app.route('/get-languages/', methods=['GET'])
def getLanguages():
    queryObj = {'Data': 'LanguageCodes'}
    query = SiteData.find_one(queryObj)
    output = query['LanguageCodes']
    return jsonify({'result': output})


@app.route('/get-translators/', methods=['GET'])
def getTranslators():
    queryObj = {'Data': 'Translators'}
    query = SiteData.find_one(queryObj)
    output = query['Translators']
    return jsonify({'result': output})


@app.route('/get-efficiency/<src>/<trg>/', methods=['GET'])
def getEfficiency(src, trg):
    queryObj = {'Data': 'Efficiency'}
    query = SiteData.find_one(queryObj)
    output = {}
    for x in query['EfficiencyTuple']:
        if(x['From'] == src and x['To'] == trg):
            output['Efficiency'] = x['Efficiency']
            break
    return jsonify({'result': output})


@app.route('/get-efficiency-tuple/', methods=['GET'])
def getEfficiencyTuple():
    queryObj = {'Data': 'Efficiency'}
    query = SiteData.find_one(queryObj)
    output = query['EfficiencyTuple']
    return jsonify({'result': output})
    # return output


@app.route('/bing-translate/<src>/<trg>/<phrase>/', methods=['GET'])
def bingTranslate(src, trg, phrase):
    url = 'https://www.bing.com/translator/?from='+src+'&to='+trg+'&text='+phrase
    script = 'return document.getElementById("tta_output_ta").value'
    return makeCall(url, script, ' ...')


@app.route('/google-translate/<src>/<trg>/<phrase>/', methods=['GET'])
def googleTranslate(src, trg, phrase):
    url = 'https://translate.google.co.in/#view=home&op=translate&sl=' + \
        src + '&tl=' + trg+'&text='+phrase
    script = 'return document.getElementsByClassName("tlid-translation")[0].textContent'
    return makeCall(url, script, None)


@app.route('/deepL-translate/<src>/<trg>/<phrase>/', methods=['GET'])
def deepLTranslate(src, trg, phrase):
    url = 'https://www.deepl.com/translator#'+src+'/'+trg+'/'+phrase
    script = 'return document.getElementsByClassName("lmt__textarea lmt__target_textarea")[0].value'
    return makeCall(url, script, '')


@app.route('/yandex-translate/<src>/<trg>/<phrase>/', methods=['GET'])
def yandexTranslate(src, trg, phrase):
    url = 'https://translate.yandex.com/?lang='+src+'-'+trg+'&text='+phrase
    script = 'return document.getElementById("translation").innerText'
    return makeCall(url, script, '')


@app.route('/test/')
def test():
    return


if __name__ == "__main__":
    app.run(debug=True)
    # print(getEfficiencyTuple())
    # getEfficiency('en', 'it')
    # phrase = 'Hi, I am Chitrank. I am an Engineer. I am very good as a person.'
    # phrases = ['Hi, My name is Chitrank.', 'I am an engineer.']

    # openURL('https://www.google.com/')

    # print("Bing:\t", bingTranslate('en', 'de', phrase))
    # print("Google:\t", googleTranslate('en', 'de', phrase))
    # print("DeepL:\t", deepLTranslate('en', 'de', phrase))
    # browser.quit()
