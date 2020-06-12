from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import JavascriptException


from datetime import datetime, timedelta
from threading import Timer
import time

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
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


# # local variables
# from selenium.webdriver.chrome.options import Options as ChromeOptions
# chrome_op = ChromeOptions()
# chrome_op.add_argument('--headless')


# def getBrowser():
    return webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_op)


connection_url = 'mongodb+srv://admin:chitrankmishra@cluster0-nqpus.mongodb.net/MachineTranslation?retryWrites=true&w=majority'
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'MachineTranslation'
app.config['MONGO_URI'] = connection_url
mongo = PyMongo(app)

timer_status = 0

client = pymongo.MongoClient(connection_url)
ApiDatabase = client.get_database('MachineTranslation')

LanguageDataSet = ApiDatabase.LanguageDataSet
SiteData = ApiDatabase.SiteData


def set_timer_on():
    query_obj = {'Data': 'Timer', 'TimerStatus': 1}
    query = SiteData.update_one(
        {'Data': 'Timer'}, {'$set': query_obj}, upsert=True)


@app.route('/set-timer-off/', methods=['GET'])
def set_timer_off(n=0):
    query_obj = {'Data': 'Timer', 'TimerStatus': 0}
    query = SiteData.update_one(
        {'Data': 'Timer'}, {'$set': query_obj}, upsert=True)
    if(n):
        print('Timer set Off')
        return
    return jsonify({'result': 'Timer set Off'})


def check_timer():
    query_obj = {'Data': 'Timer'}
    query = SiteData.find_one(query_obj)
    if(query['TimerStatus']):
        return True
    return False


@app.route('/set-trainer-on/', methods=['GET'])
def set_trainer_on():
    query_obj = {'Data': 'Trainer', 'TrainerStatus': 1}
    query = SiteData.update_one(
        {'Data': 'Trainer'}, {'$set': query_obj}, upsert=True)
    return jsonify({'result': 'Trainer set On'})


@app.route('/set-trainer-off/', methods=['GET'])
def set_trainer_off():
    query_obj = {'Data': 'Trainer', 'TrainerStatus': 0}
    query = SiteData.update_one(
        {'Data': 'Trainer'}, {'$set': query_obj}, upsert=True)
    return jsonify({'result': 'Trainer set Off'})


def check_trainer():
    query_obj = {'Data': 'Trainer'}
    query = SiteData.find_one(query_obj)
    if(query['TrainerStatus']):
        return True
    return False


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
            'call_time': call_time
        }
    else:
        output = {
            'found': 0
        }
    browser.quit()
    return output


def openURL(url):
    browser = getBrowser()
    browser.get(url)
    browser.quit()


def bingTranslate(src, trg, phrase):
    url = 'https://www.bing.com/translator/?from='+src+'&to='+trg+'&text='+phrase
    script = 'return document.getElementById("tta_output_ta").value'
    return makeCall(url, script, ' ...')


def googleTranslate(src, trg, phrase):
    url = 'https://translate.google.co.in/#view=home&op=translate&sl=' + \
        src + '&tl=' + trg+'&text='+phrase
    script = 'return document.getElementsByClassName("tlid-translation")[0].textContent'
    return makeCall(url, script, None)


def deepLTranslate(src, trg, phrase):
    url = 'https://www.deepl.com/translator#'+src+'/'+trg+'/'+phrase
    script = 'return document.getElementsByClassName("lmt__textarea lmt__target_textarea")[0].value'
    return makeCall(url, script, '')


def yandexTranslate(src, trg, phrase):
    url = 'https://translate.yandex.com/?lang='+src+'-'+trg+'&text='+phrase
    script = 'return document.getElementById("translation").innerText'
    return makeCall(url, script, '')


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


@app.route('/trainer/', methods=['GET'])
def trainer():

    query_obj = {'Data': 'LanguageCodes'}
    languages = SiteData.find_one(query_obj)
    languages = languages['LanguageCodes']
    # for x in languages:
    #     print(languages[x])

    google_eff = [[0 for i in range(len(languages))]
                  for j in range(len(languages))]
    yandex_eff = [[0 for i in range(len(languages))]
                  for j in range(len(languages))]
    bing_eff = [[0 for i in range(len(languages))]
                for j in range(len(languages))]

    for i in range(len(languages)):
        google_eff[i][i] = 1
        yandex_eff[i][i] = 1
        bing_eff[i][i] = 1

    partial_data = SiteData.find_one({'Data': 'PartialEfficiency'})
    iteration_done = int(partial_data['Iteration'])

    if(iteration_done > -1):
        print('Already Done %sth iterations' % iteration_done)
        x = 0
        efficiency_tuple = partial_data['EfficiencyTuple']
        for i in range(len(languages)):
            for j in range(len(languages)):
                google_eff[i][j] = efficiency_tuple[x]['Efficiency']['Google']
                yandex_eff[i][j] = efficiency_tuple[x]['Efficiency']['Yandex']
                bing_eff[i][j] = efficiency_tuple[x]['Efficiency']['Bing']
                x += 1

    iteration_count = 0
    s_index = 0
    for src in languages:
        t_index = 0
        for trg in languages:

            if(languages[src] == languages[trg]):
                t_index += 1
                continue

            print('\033[94m' + 'Translating from '+src+' to '+trg)

            src_data = LanguageDataSet.find_one({'Language': src})['Data']
            p_index = 0

            for phrase in src_data:
                p_index += 1
                print('\033[31m' + 'Phrase: '+phrase)

                if(iteration_count <= iteration_done):
                    print('\033[94m' + 'Already Done\n')
                    iteration_count += 1
                    continue

                res_deepL = deepLTranslate(
                    languages[src], languages[trg], phrase)
                res_google = googleTranslate(
                    languages[src], languages[trg], phrase)
                res_bing = bingTranslate(
                    languages[src], languages[trg], phrase)
                res_yandex = yandexTranslate(
                    languages[src], languages[trg], phrase)

                score_google = compareString(
                    res_google['translation'], res_deepL['translation'])
                score_yandex = compareString(
                    res_yandex['translation'], res_deepL['translation'])
                score_bing = compareString(
                    res_bing['translation'], res_deepL['translation'])

                google_eff[s_index][t_index] = (
                    google_eff[s_index][t_index] * (p_index-1) + (len(phrase)-score_google)/len(phrase))/p_index

                yandex_eff[s_index][t_index] = (
                    yandex_eff[s_index][t_index] * (p_index-1) + (len(phrase)-score_yandex)/len(phrase))/p_index

                bing_eff[s_index][t_index] = (
                    bing_eff[s_index][t_index] * (p_index-1) + (len(phrase)-score_bing)/len(phrase))/p_index

                print('\033[93m' + 'DeepL: '+res_deepL['translation'])
                print('\033[93m' + 'Google: '+res_google['translation'])
                print('\033[0m' + 'Score:', score_google, 'Current Eff:',
                      google_eff[s_index][t_index])
                print('\033[93m' + 'Bing: '+res_bing['translation'])
                print('\033[0m' + 'Score:', score_bing, 'Current Eff:',
                      bing_eff[s_index][t_index])
                print('\033[93m' + 'Yandex: '+res_yandex['translation'])
                print('\033[0m' + 'Score:', score_yandex, 'Current Eff:',
                      yandex_eff[s_index][t_index])

                efficiency_tuple = []
                res_s_in = 0
                for res_s in languages:
                    res_t_in = 0
                    for res_t in languages:
                        obj = {
                            'From': languages[res_s],
                            'To': languages[res_t],
                            'Efficiency': {'Google': google_eff[res_s_in][res_t_in], 'Bing': bing_eff[res_s_in][res_t_in], 'Yandex': yandex_eff[res_s_in][res_t_in]}
                        }
                        efficiency_tuple.append(obj)
                        res_t_in += 1
                    res_s_in += 1
                update_time = datetime.now()
                query_obj = {
                    'Data': 'PartialEfficiency',
                    'Iteration': iteration_count,
                    'LastUpdated': update_time,
                    'EfficiencyTuple': efficiency_tuple
                }
                SiteData.update_one({'Data': 'PartialEfficiency'}, {
                                    '$set': query_obj}, upsert=True)
                print('\033[94m' + 'Partial Result Uploaded...')

                iteration_count += 1

                # print(google_eff)
                # print(bing_eff)
                # print(yandex_eff)
                # exit()
                print('\033[0m')

            t_index += 1
        s_index += 1

    print('Trainer Done... Uploading final results')
    print(datetime.now())
    trainingDone()


def trainingDone():
    partial_data = SiteData.find_one({'Data': 'PartialEfficiency'})
    output = {}
    output['Data'] = 'Efficiency'
    output['EfficiencyTuple'] = partial_data['EfficiencyTuple']
    output['LastUpdated'] = datetime.now()
    query = SiteData.update_one({'Data': 'Efficiency'}, {
                                '$set': output}, upsert=True)
    print('Final Results Uploaded...!')
    print(datetime.now())
    return


@app.route('/update-dataset/', methods=['GET'])
def updateDataSet():
    query_obj = {'Data': 'LanguageCodes'}
    languages = SiteData.find_one(query_obj)
    languages = languages['LanguageCodes']

    # Translating Source Data using DeepL Translator
    src = 'English'
    src_lang = languages[src]
    src_data = {'Language': src}
    src_data = LanguageDataSet.find_one(src_data)
    src_data = src_data['Data']

    for x in languages:
        if x == src:
            continue

        trg_lang = languages[x]
        trg_data = []
        # print(l_code)
        i = 0
        for y in src_data:
            print(str(i)+'\033[94m' + '. Translating %s' % (y) +
                  '\033[93m' + 'from %s to %s' % (src_lang, trg_lang))
            i += 1
            response = deepLTranslate(src_lang, trg_lang, y)
            if(response['found']):
                trg_data.append(response['translation'])
                print('\033[0m' + response['translation'])

        print('\033[93m' + 'Uploading the new Data set....'+x)
        query_obj = {'Language': x,
                     'Data': trg_data}
        query = LanguageDataSet.update_one(
            {'Language': x}, {'$set': query_obj}, upsert=True)


@app.route('/set-dataset/', methods=['GET'])
def setDataSet():
    file = open('english sentences.txt', 'r')
    src_data = []
    for x in file:
        src_data.append(x)

    src = 'English'
    updatedDataSet = {
        'Language': src,
        'Data': src_data,
    }
    query = LanguageDataSet.update_one(
        {'Language': src}, {'$set': updatedDataSet}, upsert=True)

    print('DataSet Uploaded....English')
    updateDataSet()


@app.route('/start-timer/', methods=['GET'])
def startTimer():
    day = 0
    if(check_timer()):
        return {'result': 'Timer running'}
    if(not check_trainer()):
        return {'result': 'Trainer is Off'}

    set_timer_on()
    while(True):
        if(not check_timer() or not check_trainer()):
            break
        x = datetime.today()
        y = x.replace(day=x.day, hour=22, minute=30, second=0,
                      microsecond=0) + timedelta(days=day)
        delta_t = y-x
        secs = delta_t.total_seconds()
        print('Timer: ', secs)
        time.sleep(1)
        if(secs < 0):
            trainer()
            day = 1
            print('Trainer called')


@app.route('/test/', methods=['GET'])
def test():
    return jsonify({'result': 'Test Called'})


if __name__ == "__main__":

    # set_timer_off(1)
    # startTimer()
    trainer()
    app.run(debug=True)
    # print('App Running..')
    # phrase = 'Hi, I am Chitrank. I am an Engineer. I am very good as a person.'

    # setDataSet()
    # t = Timer(secs, trainer)
    # t.start()
    # openURL('https://www.google.com/')

    # print("Bing:\t", bingTranslate('en', 'de', phrase))
    # print("Google:\t", googleTranslate('en', 'de', phrase))
    # print("DeepL:\t", deepLTranslate('en', 'de', phrase))
    # browser.quit()
