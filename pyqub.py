#包检查
import pkg_resources
import subprocess
#解析配置
try:
    import configparser
except:
    print('安装缺失的包-configparser')
    subprocess.run(['pip','install','configparser'])
    import configparser
#web连接
try:
    import requests
except:
    print('安装缺失的包-urllib3')
    subprocess.run(['pip','install','urllib3'])
    import requests
#正则
import re
#邮件
import smtplib
from email.mime.text import MIMEText
from email.header import Header
#计时
import time
import datetime
#json解析
import json


#global
checkInv = 300#检测间隔
startmail = True
checkrqiner = False
checkofficial = False

wallet = ''

officialuser = 'guest@qubic.li'
officialpass = 'guest13@Qubic.li'

mailaddr = ''
smtpcode = ''
mailtitle = ''

rqinertitle = ''
officialtitle = ''

class QUB:
        def __init__(self):
            #rqiner-不再获取纪元信息
            # self.epoch = 0
            self.iterrate = 0
            self.devices = 0
            self.solutions = 0
            #official
            self.iterrate_o = 0
            self.devices_o = 0
            self.solutions_o = 0
        #从使用token的官池获取信息
        def getFromOfficialToken(self,officialU,officialP):
            print('正在获取官池信息...')
            if(not checkofficial):
                print('你没有设置检测官池，跳过')
                return False
            try:
                #login
                rBody = {'userName': officialU, 'password': officialP, 'twoFactorCode': ''}
                rHeaders = {'Accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
                r = requests.post('https://api.qubic.li/Auth/Login', data=json.dumps(rBody), headers=rHeaders)
                token = r.json()['token']
                #get-minercontrol
                rHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
                r = requests.get('https://api.qubic.li/My/MinerControl', headers=rHeaders)
                rtext = str(r.json())
                self.devices_o = int(re.findall(r'\'activeMiners\':([\s\S]*?),',rtext)[0])
                self.iterrate_o = int(re.findall(r'], \'currentIts\':([\s\S]*?),',rtext)[0])
                self.solutions_o = int(re.findall(r'\'totalSolutions\':([\s\S]*?),',rtext)[0])
                return True
            except:
                print('获取官方网页数据失败')
                return False
        #从rqiner获取参数
        def getFromRQiner(self,walletaddr):
            print('正在获取rqiner信息...')
            if(not checkrqiner):
                print('你没有设置检测rqiner，跳过')
                return False
            try:
                urladdr = 'https://pooltemp.qubic.solutions/info?miner='+walletaddr
                req = Request(urladdr, headers={'User-Agent': 'Mozilla/5.0'})
                page = urllib.request.urlopen(req)
                html = page.read()
                html = html.decode('UTF-8')
                self.epoch = int(re.findall(r'epoch":([\s\S]*?),',html)[0])
                self.iterrate = float(re.findall(r'iterrate":([\s\S]*?),',html)[0])
                self.devices = int(re.findall(r'devices":([\s\S]*?),',html)[0])
                self.solutions = int(re.findall(r'solutions":([\s\S]*?),',html)[0])
                return True
            except:
                print('获取rqiner网页数据失败')
                return False
        #转化为str信息
        def toString(self):
            retstr = '当前状态：\n================='
            global checkrqiner
            if(checkrqiner):
                retstr = retstr + '\n--rqiner--\n算力: '+str(self.iterrate)+'\n设备: '+str(self.devices)+'\n块数: '+str(self.solutions)
            else:
                retstr = retstr + '\n--不检测rqiner--'
            global checkofficial
            if(checkofficial):
                retstr = retstr + '\n--官池--\n算力: '+str(self.iterrate_o)+'\n设备: '+str(self.devices_o)+'\n块数: '+str(self.solutions_o)
            else:
                retstr = retstr + '\n--不检测官池--'
            retstr = retstr + '\n================='
            return retstr
        #输出
        def infoOut(self):
            print(self.toString())
    print('获取附加数据中...')

    rBody = {'userName': 'guest@qubic.li', 'password': 'guest13@Qubic.li', 'twoFactorCode': ''}
    rHeaders = {'Accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
    r = requests.post('https://api.qubic.li/Auth/Login', data=json.dumps(rBody), headers=rHeaders)
    token = r.json()['token']
    rHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
    r = requests.get('https://api.qubic.li/Score/Get', headers=rHeaders)
    networkStat = r.json()

    retstr = '参考数据:\n=================\n'
    retstr = retstr + '全网算力：' + str(networkStat['estimatedIts']) + '\n'
    retstr = retstr + '平均分数：' + str(int(networkStat['averageScore'])) + '\n'
    retstr = retstr + '出块速度：' + str(networkStat['solutionsPerHour']) + '\n'
    #单位价格
    crypto_currency = 'qubic-network'
    destination_currency = 'usd'
    cg_client = CoinGeckoAPI()
    prices = cg_client.get_price(ids=crypto_currency, vs_currencies=destination_currency)
    qubicPrice = prices[crypto_currency][destination_currency]
    retstr = retstr + '当前价格：' + "{:.8f}".format(qubicPrice) + '\n'
    #你的预期
    # retstr = retstr + '每块预期价值:' + "{:.8f}".format(qubicPrice) + '\n'
    # retstr = retstr + '每日预期块数：' + "{:.8f}".format(qubicPrice) + '\n'
    # retstr = retstr + '每日预期收益：' + "{:.8f}".format(qubicPrice) + '\n'

    retstr = retstr + "================="

    return retstr

#读出配置
def CheckConfig(file):
    print('check config file:')
    config = configparser.ConfigParser()
    config.read_file(open(file, encoding = 'utf-8'))
    global checkrqiner
    global checkofficial
    if('default' in config):
        global checkInv
        checkInv = float(config['default']['inv'])
        global startmail
        startmail = (config['default']['startmail']=='yes')

        checkrqiner = (config['default']['checkRqiner']=='yes')
        checkofficial = (config['default']['checkOfficial']=='yes')
    if('wallet' in config):
        global wallet
        wallet = config['wallet']['addr']
        if(checkrqiner and wallet==''):
            checkrqiner=False
            print('你选择了检测rqiner数据，但没有设置钱包地址，要访问rqiner数据需要你的钱包地址')
    if('official' in config):
        global officialuser
        officialuser = config['official']['officialUser']
        global officialpass
        officialpass = config['official']['officialPass']
        if(checkofficial and (officialuser=='' or officialpass == '')):
            checkofficial = False
            print('你选择了检查官方数据，但没有设置你的app.qubic.li登录信息，要访问官池数据需要你的登录信息')
    if('smtp' in config):
        global mailaddr
        mailaddr = config['smtp']['email']
        global smtpcode
        smtpcode = config['smtp']['smtpcode']
        global mailtitle
        mailtitle = config['smtp']['mailtitle']
    if((not checkrqiner) and (not checkofficial)):
        print('rqiner和官池你都不检测，还跑集贸啊？不跑了！')
        exit(0)
    print('检查间隔：'+ str(checkInv)+'秒\n钱包公钥：'+wallet+'\n邮箱地址：'+mailaddr)
    # print('官池账户: '+str(officialuser)+'\n官池密码: '+str(officialpass))

def CurTimeStr():
    now = datetime.datetime.now()
    tfmt = now.strftime('%Y-%m-%d %H:%M:%S')
    return tfmt

#通过IMAP服务以邮件发送
def SendMail(tile,info):
    #imap,smtp
    sender = mailaddr
    receivers = mailaddr

    msg = MIMEText(info + '\n\n' + CurTimeStr(),"plain",'utf-8')
    msg['Subject'] = Header(tile,'utf-8')
    msg['From'] = sender
    msg['To'] = receivers
    print('尝试发送邮件: '+tile)
    try:
        smtp = smtplib.SMTP('smtp.qq.com')
        smtp.login(sender,smtpcode)
        smtp.sendmail(sender,receivers,msg.as_string())
        smtp.quit()
        print('successfully sent email')
    except:
        print('邮件发送出错，考虑网络问题或检查smtp设置')

# exit(0)

#0 检查配置
CheckConfig('config.cfg')

#正常流程：
#开启，第一次检查，然后进行轮询
print('开始-' + CurTimeStr())
oldqub = QUB()
if(checkrqiner):
    oldqub.getFromRQiner(wallet)
if(checkofficial):
    oldqub.getFromOfficialToken(officialuser,officialpass)
oldqub.infoOut() 

if(startmail):
    pass
    #发一次起始邮件
    SendMail('qub监控启动',oldqub.toString())

print('下次检测于：'+str(int(checkInv))+'秒后...')

lasttime = time.time()
elsptime = 0
while(True):
    #计时检测
    curtime = time.time()
    elsptime += curtime-lasttime
    lasttime = curtime
    if(elsptime<checkInv):
        continue
    #正常执行一次获取和对比
    elsptime-=checkInv
    #do some thing
    print('新一轮检测开始于' + CurTimeStr())
    newqub = QUB()
    if(checkrqiner):
        if(not newqub.getFromRQiner(wallet)):
            pass
    if(checkofficial):
        if(not newqub.getFromOfficialToken(officialuser,officialpass)):
            pass
    #验证
    bChangeAndSend = False
    if ((newqub.solutions>oldqub.solutions) or (newqub.solutions_o>oldqub.solutions_o)):
        #新块被发现
        SendMail(mailtitle,newqub.toString())
        bChangeAndSend = True
    if(not bChangeAndSend):
        print('本次监测未发现明显变动。')
    oldqub = newqub
    oldqub.infoOut()
    print('下次检测于：'+str(int(checkInv))+'秒后...')