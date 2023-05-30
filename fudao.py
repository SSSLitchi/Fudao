import math
import time
import numpy as np
import requests
import math
from scipy.stats import binom

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

def send_mail(high_fre):
    con = smtplib.SMTP_SSL('smtp.163.com', 465)
    con.login('sfx2691236752@163.com', 'NKTSBGKPJOSIRIWR')

    msg = MIMEMultipart()
    subject = Header('设定阈值{}以达到'.format(high_fre), 'utf-8').encode()
    msg['Subject'] = subject
    msg['From'] = 'sfx2691236752@163.com <sfx2691236752@163.com>'
    msg['To'] = '2691236752@qq.com'
    con.sendmail('sfx2691236752@163.com', '2691236752@qq.com', msg.as_string())
    con.quit()

import pymysql
from datetime import datetime

db = pymysql.connect(host='localhost',
                     user='root',
                     password='11111111',
                     database='Fudao',
                     charset='utf8')

# now_time = "_{:02}_{:02}_{:02}_{:02}".format(datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute)


# def update(id):
#     with open("fudao{}.txt".format(now_time), "a") as f:
#         msg = '{}'.format(id)
#         # print(msg)
#         try:
#             f.write(msg)
#         except:
#             print("err")

def insert(sql="insert into record(time,pool_id) values ('2021-05-15-12-12',2)"):
    # print(sql)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()
    except:
        print("insert error")
def update(start_time,end_time,pool_id):
    insert("insert into record(start_time,end_time,pool_id) values ({},{},{}) ON DUPLICATE KEY UPDATE pool_id = VALUES(pool_id); ".format(start_time,end_time,pool_id))
    # print(start_time,end_time,pool_id)


last_id = 0
flag = True

out_money = 0
in_money = 0

choose = []

url = 'https://api.live.bilibili.com/xlive/fuxi-interface/ExploreController/actInitial?_ts_rpc_args_=[3158628,"67175339",101814]'
res = requests.get(url).json()['_ts_rpc_return_']
res_data = res['data']
poolList = []
for item in (res_data['poolList']):
    poolList.append(list(item.values()))
poolList = np.array(poolList)

pool = np.array(
    [[1, 5, 19.2], [2, 10, 9.9], [3, 5, 19.2], [4, 5, 19.2], [5, 15, 6.9], [6, 25, 4.0], [7, 5, 19.2], [8, 45, 2.4]])

low_pool = np.array([1, 3, 4, 7,2]) - 1
high_pool = np.array([ 5, 6, 8]) - 1

nums = np.zeros(8)
lh_nums = np.zeros(2)
frequents = np.zeros(8)
low_frequents = np.zeros(1)
high_frequents = np.zeros(1)

# send_mail(high_frequents)

logurl = "https://api.live.bilibili.com/xlive/fuxi-interface/ExploreController/getExploreLog?_ts_rpc_args_=[]"
res = requests.get(logurl).json()['_ts_rpc_return_']['data']['logList']
for i in range(len(res) - 1, -1, -1):
    # update(res[i]['poolId'] - 1)
    update(res[i]['roundTime'],res[i]['roundTime']+79,res[i]['poolId'])

    nums[res[i]['poolId'] - 1] += 1
    frequents += 1
    frequents[res[i]['poolId'] - 1] = 0

    if (res[i]['poolId'] - 1) in low_pool:
        low_frequents = 0
        high_frequents += 1
        lh_nums[0] += 1
    else:
        low_frequents += 1
        high_frequents = 0
        lh_nums[1] += 1

# the_frequents = np.ceil(1/pool[:,-1]*200)
# low_the_frequents = np.ceil(1/(pool[low_pool][:,-1].sum())*200)
# high_the_frequents = np.ceil(1/(pool[high_pool][:,-1].sum())*200)

# 概率小于等于0.05时为小概率时间

the_frequents = np.ceil(np.log(0.01) / np.log(1 - pool[:, -1] / 100))
low_the_frequents = np.ceil(np.log(0.01) / np.log(1 - pool[low_pool][:, -1].sum() / 100))
high_the_frequents = np.ceil(np.log(0.007) / np.log(1 - pool[high_pool][:, -1].sum() / 100))
# low_the_frequents = 4
# high_the_frequents = 10

# 初始化
temp_cur = 100 * nums / (nums.sum())
print("统计次数:{}        当前岛屿:{}".format(nums.sum(), poolList[res[0]['poolId'] - 1]))
print("岛屿:{:>6},{:>6},{:>6},{:>6},{:>6},{:>6},{:>6},{:>6}\n".format(poolList[0][1], poolList[1][1], poolList[2][1],
                                                                    poolList[3][1], poolList[4][1], poolList[5][1],
                                                                    poolList[6][1], poolList[7][1]))
print(
    "当前:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(temp_cur[0], temp_cur[1], temp_cur[2],
                                                                                  temp_cur[3], temp_cur[4], temp_cur[5],
                                                                                  temp_cur[6], temp_cur[7]))
temp_the = pool[:, -1]


def norm(init):
    # print(init)
    return 1-np.exp(-init)
    #return init/(init+1)

# the_frequents = 0.5 * frequents * temp_the + 0.5 * 100 * temp_the / temp_cur
the_frequents = 0.5 * norm(frequents * temp_the/100)  + 0.5 * norm(temp_the / temp_cur) 
the_frequents *=norm(nums.sum()/50)



print(
    "理论:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(temp_the[0], temp_the[1], temp_the[2],
                                                                                  temp_the[3], temp_the[4], temp_the[5],
                                                                                  temp_the[6], temp_the[7]))
print("频次:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(frequents[0], frequents[1],
                                                                                    frequents[2], frequents[3],
                                                                                    frequents[4], frequents[5],
                                                                                    frequents[6], frequents[7]))
print("理论:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(the_frequents[0], the_frequents[1],
                                                                                    the_frequents[2], the_frequents[3],
                                                                                    the_frequents[4], the_frequents[5],
                                                                                    the_frequents[6], the_frequents[7]))
print("低倍:{:9.2f}/{:.2f}    高倍:{:9.2f}/{:.2f}\n".format(low_frequents, low_the_frequents, high_frequents,
                                                        high_the_frequents))
print("低倍:{:9.2f}/{:.2f}    高倍:{:9.2f}/{:.2f}\n".format(100 * lh_nums[0] / lh_nums.sum(), pool[low_pool][:,-1].sum(),
                                                        100 * lh_nums[1] / lh_nums.sum(), pool[high_pool][:,-1].sum()))

# if high_frequents >= high_the_frequents:
#     send_mail(high_frequents)


# try_idx = [5, 6] + [i for i in range(19, 100)]
# try_idx = [0,1,2,3,4,5,6,7]
#
# rate = 1
# if high_frequents in try_idx:
#     choose_idx = high_pool
#     out_money -= (rate * len(choose_idx))
#     choose = choose_idx.tolist()
# else:
#     choose_idx = []

#*
# temp_mul = frequents*temp_the*temp_the/temp_cur
#+
weight = np.ones(8)
weight[low_pool] = 0
temp_mul = the_frequents*weight 
# input(temp_mul[temp_mul>0].min())
if temp_mul[temp_mul>0].min() >= 0.75:
    send_mail(65536)
# input(temp_mul)
rate = 1

total_count = 0
correct_count  =0
choose_idx = np.where(temp_mul>=0.7)[0]
# choose_idx = np.argsort(temp_mul)[-4:]
rate = min(500//max((len(choose_idx),1)),rate)
out_money += (rate * len(choose_idx))
choose = choose_idx.tolist()
if len(choose_idx)>0:
    total_count +=1


# # print(choose_idx)
# # input()
# for i in range(choose_num):
#     print(poolList[choose_idx[choose_num-i-1]],"loss:",temp[choose_idx[choose_num-i-1]])
print("-----------------------------------------------------")

while True:
    try:
        time.sleep(2)
        url = 'https://api.live.bilibili.com/xlive/fuxi-interface/ExploreController/actInitial?_ts_rpc_args_=[3158628,"67175339",101814]'
        res = requests.get(url).json()['_ts_rpc_return_']
        res_data = res['data']
        # actStartTime = res_data['actStartTime']
        # actEndTime = res_data['actEndTime']
        # currentTime = res_data['currentTime']
        # processSeconds = res_data['processSeconds']
        # waitSeconds = res_data['waitSeconds']
        # poolList  = np.array(res_data['poolList'])
        # marqueeList = res_data['marqueeList']

        roundInfo = res_data['roundInfo']

        roundEndTime = roundInfo['roundEndTime']
        roundStartTime = roundInfo['roundStartTime']
        # roundEndTime = roundInfo['roundEndTime']
        # roundStartTime = roundInfo['roundStartTime']
        # roundLotteryTime = roundInfo['roundLotteryTime']

        if roundInfo['roundId'] == last_id:
            pass
        else:
            flag = True

        last_id = roundInfo['roundId']
        if roundInfo['winPoolId'] != 0:
            if flag:
                # print(roundInfo['roundId'],":",roundStartTime,"|||",roundEndTime,"|||",time.time())
                if int(roundInfo['winPoolId'] - 1) in choose_idx:
                    correct_count+=1
                    in_money += (rate * pool[int(roundInfo['winPoolId'] - 1)][1])
                    rate = max(1,int(out_money-in_money)*2//10)
                else:
                    #rate *= 2
                    # rate =1
                    rate = max(1,int(out_money-in_money)*2//10)
                    # rate = min(125, rate)

                nums[int(roundInfo['winPoolId'] - 1)] += 1
                frequents += 1
                frequents[int(roundInfo['winPoolId'] - 1)] = 0
                if int(roundInfo['winPoolId'] - 1) in low_pool:
                    low_frequents = 0
                    high_frequents += 1
                    lh_nums[0] += 1
                    
                else:
                    # if high_frequents>5:
                    #     high_the_frequents-=1
                    # else:
                    #     high_the_frequents+=1
                    low_frequents += 1
                    high_frequents = 0
                    lh_nums[1] += 1

                temp_cur = 100 * nums / (nums.sum())
                # the_frequents = 0.5*frequents * temp_the + 0.5* 100 * temp_the / temp_cur
                the_frequents = 0.5 * norm(frequents * temp_the/100)  + 0.5 * norm(temp_the / temp_cur) 
                the_frequents *=norm(nums.sum()/50)
                print("{}_{}_{}_{}_{}".format(datetime.now().year,datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().minute))

                print("\n投入:{:.2f},收入:{:.2f},回报率:{:.2f}%\n".format(out_money, in_money,100*correct_count/max(1,total_count)))
                print("统计次数:{}        当前岛屿:{}".format(nums.sum(), poolList[int(roundInfo['winPoolId'] - 1)]))
                print("岛屿:{:>6},{:>6},{:>6},{:>6},{:>6},{:>6},{:>6},{:>6}\n".format(poolList[0][1], poolList[1][1],
                                                                                    poolList[2][1], poolList[3][1],
                                                                                    poolList[4][1], poolList[5][1],
                                                                                    poolList[6][1], poolList[7][1]))

                print("当前:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(temp_cur[0],
                                                                                                    temp_cur[1],
                                                                                                    temp_cur[2],
                                                                                                    temp_cur[3],
                                                                                                    temp_cur[4],
                                                                                                    temp_cur[5],
                                                                                                    temp_cur[6],
                                                                                                    temp_cur[7]))
                temp_the = pool[:, -1]
                print("理论:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(temp_the[0],
                                                                                                    temp_the[1],
                                                                                                    temp_the[2],
                                                                                                    temp_the[3],
                                                                                                    temp_the[4],
                                                                                                    temp_the[5],
                                                                                                    temp_the[6],
                                                                                                    temp_the[7]))
                print("频次:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(frequents[0],
                                                                                                    frequents[1],
                                                                                                    frequents[2],
                                                                                                    frequents[3],
                                                                                                    frequents[4],
                                                                                                    frequents[5],
                                                                                                    frequents[6],
                                                                                                    frequents[7]))
                print("理论:{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f},{:9.2f}\n".format(the_frequents[0],
                                                                                                    the_frequents[1],
                                                                                                    the_frequents[2],
                                                                                                    the_frequents[3],
                                                                                                    the_frequents[4],
                                                                                                    the_frequents[5],
                                                                                                    the_frequents[6],
                                                                                                    the_frequents[7]))
                print(
                    "低倍:{:9.2f}/{:.2f}    高倍:{:9.2f}/{:.2f}\n".format(low_frequents, low_the_frequents, high_frequents,
                                                                      high_the_frequents))
                print("低倍:{:9.2f}/{:.2f}    高倍:{:9.2f}/{:.2f}\n".format(100 * lh_nums[0] / lh_nums.sum(), pool[low_pool][:,-1].sum(),                  100 * lh_nums[1] / lh_nums.sum(), pool[high_pool][:,-1].sum()))

                # if high_frequents >= high_the_frequents:
                #     send_mail(high_frequents)

                # if high_frequents in try_idx:
                #     choose_idx = high_pool
                #     out_money -= (rate * len(choose_idx))
                #     choose = choose_idx.tolist()
                # else:
                #     choose_idx = []
                # temp_mul = temp_the * frequents
                #*
                # temp_mul = frequents * temp_the * temp_the / temp_cur
                #+
                # temp_mul = the_frequents
                temp_mul = the_frequents*weight
                if temp_mul[temp_mul>0].min() >= 0.75:
                    send_mail(65536)

                choose_idx = np.where(temp_mul >= 0.7)[0]
                # choose_idx = np.argsort(temp_mul)[-4:]
                if len(choose_idx)>0:
                    total_count +=1

                out_money += (rate * len(choose_idx))
                choose = choose_idx.tolist()

                # choose_num = 8

                # choose_idx = temp.argsort()[-choose_num:]
                # # print(choose_idx)

                # # input()
                # for i in range(choose_num):
                #     print(poolList[choose_idx[choose_num-i-1]],"loss:",temp[choose_idx[choose_num-i-1]])
                print("-----------------------------------------------------")
                # update(int(roundInfo['winPoolId'] - 1))
                update(roundStartTime,roundEndTime,roundInfo['winPoolId'])

                # print(100*nums/(nums.sum()))
                with open("fudao.txt", "a") as f:
                    msg = '{},{},{}\n'.format(roundInfo['roundId'], roundInfo['winPoolId'],
                                              poolList[roundInfo['winPoolId'] - 1])
                    # print(msg)
                    try:
                        f.write(msg)
                    except:
                        print("err")
            flag = False
    except:
        print("error")
        # print((nums))
        # print(nums / (nums.sum()))

        # print("\r",time.time()," ",roundInfo['roundId'],' ',roundInfo['roundEndTime'],"---",roundInfo['winPoolId'],end=" ")
