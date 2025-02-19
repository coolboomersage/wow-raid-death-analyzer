import requests
import os
import sys
import fileinput
import PIL.Image
import PIL.ImageTk
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from tkinter import ttk
from os import system, name
from datetime import timedelta
from dotenv import dotenv_values
from types import SimpleNamespace

#load warcraft logs api key from .env file
my_secrets = dotenv_values(".env")
wcl_api_key = my_secrets["wcl_api_key"]

def clear():
   if name == 'nt':
      _ = system('cls')
   else:
      _ = system('clear')

def mill_conv(milliseconds):
   t = timedelta(milliseconds=int(milliseconds))
   minutes = t.seconds // 60
   seconds = t.seconds % 60
   if seconds < 10:
      seconds = f"0{seconds}"
   return f"{minutes}:{seconds}"


def timestamp(fight_start, time):
    truetime = time - fight_start
    return(mill_conv(truetime))



#this is the format to get deaths from a specific pull
#https://www.warcraftlogs.com/v1/report/events/deaths/(fight ID)?encounter=(encounter id)&start=(start time in ms)&end=(ent time in ms)&api_key=(api key)

#this is how to get the name of the killing ability by using N witch is death number
#death_log['events'][N]['killingAbility']['name']



def callLog():
    global displayLogResult
    global fight_id
    fight_id = ""
    log = url_entry.get()
    while fight_id == "":
        try:
            #print(f"Log Link: ", end="")
            #fight_id = input().split("reports/")[1].split("#fight")[0]
            fight_id = log.split("reports/")[1].split("#fight")[0]
        except IndexError:
            #print("Error: Please double check the link provided and try again...")
            displayLogResult['text'] = "Error: Please double check the link provided and try again..."
            return()
    clear()

    fight_data = requests.get("https://www.warcraftlogs.com/v1/report/fights/{}?fight=1&api_key={}".format(fight_id,wcl_api_key)).json()
    #print("https://www.warcraftlogs.com/v1/report/fights/{}?fight=1&api_key={}".format(fight_id,wcl_api_key))


    f_fights = []
    for friendly in fight_data["friendlies"]:
        for f in friendly["fights"]:
            f_fights.append(f["id"])

    global friendly_IDs
    friendly_IDs = {}
    i = 0;
    while (i < len(fight_data['friendlies'])):
        friendly_IDs[fight_data['friendlies'][i]['id']] = fight_data['friendlies'][i]['name']
        i += 1

    clear()
    fight_text = "boss name: fight ID : fight NBR : bossPercent : phaseNBR\n"
    #print("boss name: fight ID : fight NBR : bossPercent : phaseNBR")
    i = 0
    global id2times
    id2times = {}
    for fight in fight_data["fights"]:
        if fight["boss"] != 0:
            if fight["id"] in f_fights:
                i += 1
                #print(fight["name"] + ": " + str(fight["id"]) + " : " + str(i) + " : " + str(fight["bossPercentage"] / 100) + " : " + str(len(fight["phases"])))
                if("phases" in fight):
                    fight_text += fight["name"] + ": " + str(fight["id"]) + " : " + str(i) + " : " + str(fight["bossPercentage"] / 100) + " : " + str(len(fight["phases"])) + "\n"
                else:
                    fight_text += fight["name"] + ": " + str(fight["id"]) + " : " + str(i) + " : " + str(fight["bossPercentage"] / 100) + " : " + "1" + "\n"
                id2times[fight["id"]] = {
                    "start_time": fight["start_time"],
                    "end_time": fight["end_time"],
                    "boss": fight["boss"],
                    "name": fight["name"],
                    "zoneName": fight["zoneName"],
                    "wipePercent": fight["bossPercentage"],
                }
                if("phases" in fight):
                    id2times[fight["id"]]["phases"] = len(fight["phases"])
                else:
                    id2times[fight["id"]]["phases"] = 1

    global fightinfo_label
    fightinfo_label['text'] = fight_text

    #select boss 0,2 - 0,3
    #select player 1,2 - 1,3
    #select pullNBR 2,2 - 2,4
    #select phase 3,2 - 3,3
    #select filter (boss / pullNBR / phase + boss) 4,2

    global unique_players
    global unique_bosses

    unique_players = ['-All-']
    i = 0
    while (i < len(fight_data['friendlies'])):
        if (fight_data['friendlies'][i]['name'] not in unique_players):
            unique_players.append(fight_data['friendlies'][i]['name'])
        i += 1
    unique_players = sorted(unique_players)

    unique_bosses = ['-All-']
    for fight in fight_data["fights"]:
        if fight["boss"] != 0 and fight["name"] not in unique_bosses:
            unique_bosses.append(fight["name"])
    unique_bosses = sorted(unique_bosses)


    global boss_options
    global player_options
    global pull_start_entry
    global pull_end_entry
    global phase_start_entry
    global phase_end_entry

    boss_selected = StringVar()
    boss_label = Label(root , text = "boss:")
    boss_label.grid(row=0,column=3)
    boss_options = ttk.Combobox(root , textvariable=boss_selected , values= unique_bosses , state="-All-")
    boss_options.grid(row=0,column=4)

    player_selected = StringVar()
    player_label = Label(root , text = "player:")
    player_label.grid(row=1,column=3)
    player_options = ttk.Combobox(root , textvariable=player_selected , values= unique_players , state="-All-")
    player_options.grid(row=1,column=4)
    
    pull_label = Label(root , text = "pullNBR range:")
    pull_label.grid(row=2,column=3)
    pull_start_entry = Entry(root)
    pull_start_entry.grid(row=2,column=4)
    pull_label_to = Label(root , text = " to ")
    pull_label_to.grid(row=2,column=5)
    pull_end_entry = Entry(root)
    pull_end_entry.grid(row=2,column=6)

    phase_label = Label(root , text = "phase range:")
    phase_label.grid(row=3,column=3)
    phase_start_entry = Entry(root)
    phase_start_entry.grid(row=3,column=4)
    phase_label_to = Label(root , text = " to ")
    phase_label_to.grid(row=3,column=5)
    phase_end_entry = Entry(root)
    phase_end_entry.grid(row=3,column=6)

    runBTN = Button(root , text = "get deaths" , command = getDeaths)
    runBTN.grid(row=1, column = 2)

    displayLogResult['text'] = "finished"


def getDeaths():
    #print(id2times[list(id2times.keys())[1]])
    if (pull_start_entry.get() != ''):
        i = max(int(pull_start_entry.get()) , 0)
    else:
        i = 0
    
    if (pull_end_entry.get() != ''):
        end_pull = min(int(pull_end_entry.get()) , len(id2times))
    else:
        end_pull = len(id2times)

    #print(player_options.get())
    if(player_options.get() != ''):
        target_player = player_options.get()
    else:
        target_player = '-All-'

    if(boss_options.get() != ''):
        target_boss = boss_options.get()
    else:
        target_boss = '-All-'

    if(phase_start_entry.get() != ''):
        phase_start = max(0 , int(phase_start_entry.get()))
    else:
        phase_start = 0

    if (phase_end_entry.get() != ''):
        phase_end = min(int(phase_end_entry.get()) , len(id2times))
    else:
        phase_end = len(id2times)

    death_list = []
    death_name = []
    while (i < end_pull):
        not_wipe = True
        start_time = id2times[list(id2times.keys())[i]]['start_time']
        end_time = id2times[list(id2times.keys())[i]]['end_time']
        death_log = requests.get("https://www.warcraftlogs.com/v1/report/events/deaths/{}?&start={}&end={}&api_key={}".format(fight_id,start_time,end_time,wcl_api_key)).json()
        #print("https://www.warcraftlogs.com/v1/report/events/deaths/{}?&start={}&end={}&api_key={}".format(fight_id,start,end,wcl_api_key))
        j = 0
        #print("processing pull NBR: " + str(i+1))
        global root
        displayLogResult['text'] = "processing pull NBR: " + str(i+1)
        root.update()
        while (j < len(death_log['events']) and not_wipe == True):
            if(target_player == "-All-" or target_player == friendly_IDs[death_log['events'][j]['targetID']]):
                if 'killingAbility' in death_log['events'][j]:
                    if (id2times[list(id2times.keys())[i]]['name'] == target_boss or target_boss == '-All-'):
                        if (int(id2times[list(id2times.keys())[i]]['phases']) >= phase_start and int(id2times[list(id2times.keys())[i]]['phases']) <= phase_end):
                            #print(death_log['events'][j]['killingAbility']['name'] + " : " + friendly_IDs[death_log['events'][j]['targetID']] + " : " + timestamp(start_time , death_log['events'][j]['timestamp']))
                            death_list.append([death_log['events'][j]['killingAbility']['name'] , friendly_IDs[death_log['events'][j]['targetID']] , timestamp(start_time , death_log['events'][j]['timestamp'])])
                            death_name.append(death_log['events'][j]['killingAbility']['name'])
                else:
                    #print("wipe detected, going to next pull")
                    not_wipe = False
            j += 1
        #print("\n")
        i += 1

    #print(death_list)

    deathNoDupe = list(set(death_name))
    death_counts = []
    i = 0
    while (i < len(deathNoDupe)):
        death_counts.append(death_name.count(deathNoDupe[i]))
        i += 1


    raw_data_file = open("recent_raw_data.txt","w+")
    raw_data_file.close()
    raw_data_file = open("recent_raw_data.txt","w+")
    i = 0
    while (i < len(death_list)):
        raw_data_file.write(str(death_list[i][0]) + " , " + str(death_list[i][1]) + " , " + str(death_list[i][2]) + '\n')
        i +=1
    raw_data_file.close()
    #########################################
    #                                       #
    #        TIME TO GENERATE GRAPHS        #
    #                                       #
    #########################################


    global Pie
    global imgPie

    try:
        os.remove('recentPie.png')
    except:
        pass
    
    plt.pie(death_counts , labels = deathNoDupe)
    plt.savefig('recentPie.png' , bbox_inches = 'tight')
    plt.close()


    Pie = PIL.Image.open('recentPie.png')
    imgPie = Canvas(root , width = Pie.size[0] , height = Pie.size[1])
    imgPie.grid(row = 3 , column = 0)
    Pie = PIL.ImageTk.PhotoImage(PIL.Image.open("recentPie.png"))
    imgPie.create_image(20 , 0 , image = Pie , anchor = 'nw')

    displayLogResult['text'] = "finished"

#window
root = Tk()
root.iconbitmap("DS.ico")

#create wigit for log result
displayLogResult = Label(root , text = "no result yet")
displayLogResult.grid(row=2,column=0)

#title / dim / icon
root.title("wow raid death analyser")
root.geometry('640x360')
root.iconbitmap("DS.ico")

#log input window
url_label = Label(root , text = "log URL:")
url_entry = Entry(root)
fightinfo_label = Label(root , text = "")
fightinfo_label.grid_propagate(False)
#fightNBR_entry = Entry(root)
#fightNBR_entry.insert(END, str(1))

url_label.grid(row=0,column=0)
url_entry.grid(row=0,column=1)
fightinfo_label.grid(row = 0 , column = 2)
#fightNBR_entry.grid(row = 1 , column = 1)

#button
btn1 = Button(root , text = "get fight info" , command = callLog)
btn1.grid(row=2, column = 1)

#mainloop
root.mainloop()