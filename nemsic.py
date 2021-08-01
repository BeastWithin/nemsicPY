#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import time
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
import adafruit_dht
from email.mime.text import MIMEText
import logging

SMTPserver = 'smtp.office365.com'
port =587
sender =     'nemsic@hotmail.com'
destination = ['eczsinancengiz@gmail.com']
#destination = ['eczpinar.ekmek@gmail.com']
USERNAME = "nemsic@hotmail.com"
PASSWORD = "Y3QLt66TLGRkxNt"
# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'
subject="NemSıc Alarm"
lastAlarmSent=""
logging.basicConfig(filename='NemSıc.log', level=logging.DEBUG) #log tutmak için
sensorPins={23:"Oda Sensoru", #birdençok sensor eklenebilir
            #24:"Buzdolabı Sensoru",
            }
#DHT işlemleri
def get_data(sensorpin):
    den=0
    sıc=None
    nem=None
    while den<25: #25 defa sensor okumayı denesin diye, olmazsa None dönsün
        try: 
            dhtDevice = adafruit_dht.DHT11(sensorpin)
            sıc=dhtDevice.temperature
            nem=dhtDevice.humidity
            dhtDevice.exit() #sensorün yine okunabilmesi için şart. yoksa ligpio işlemi yüzünden hata veriyor. 
            break
        except:
            dhtDevice.exit()
            den+=1
            logging.error("Sensor okunamadı: Deneme {}".format(den))
            time.sleep(0.77)
            continue
    return (sıc,nem)


def sendalarm(okunanDeğerler):
    content="\n{}".format(str(time.ctime()))# şimdiki zamanı ekleme
    for sensor in okunanDeğerler:
        sıc,nem=okunanDeğerler[sensor]
        content+="\nSensor:{}\tSıcaklık:{}°C\tNem:%{}".format(sensor,sıc,nem) #ne kadar sensor varsa okumaları listeleme
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    try:
        conn = SMTP(SMTPserver,port)
    except:
        logging.error("Email sunucusuna bağlanılamadı.")
        return
    #conn.set_debuglevel(1)
    conn.ehlo()
    conn.starttls()
    try:
        conn.login(USERNAME, PASSWORD)
    except:
        logging.error("Login Hatası")
        return
    #try:
        #print("{} tarafından {} adresine {} konulu mesaj yollanıyor...",format(sender,destination,subject))
    try:
        conn.sendmail(sender, destination, msg.as_string())
    except:
        logging.error("Email gönderimi başarısız")
    #except:
        #print("Başaramadık abi")
    #finally:
    conn.quit()

while True:
    sıcaklıklar=[]
    okunanDeğerler={sensorPins[i]:get_data(i) for i in sensorPins}
    #sıc,nem=get_data(23)
    #pyexcel_ods.write_data(str(time.strftime("%Y %m"))+" data.ods",{time.strftime("%d"):[["Saat",time.strftime("%H:%M:%S")],["Sıcaklık",2],["Nem",2]]})
    for sensor in okunanDeğerler:
        sıc=okunanDeğerler[sensor][0]
        nem=okunanDeğerler[sensor][1]
        sıcaklıklar.append(sıc)
        os.system("echo {},{},{} >> '{}.txt'".format(time.strftime("%H:%M:%S"),sıc,nem,time.strftime("%Y %m"))) #txt dosyasına verileri kaydetme
    if not all([s for s in sıcaklıklar]):# sensorden None dönüyorsa alarm
        sendalarm(okunanDeğerler)
    elif not all([s<25 for s in sıcaklıklar]):#sensor 25 dereceden fazlaysa alarm
        sendalarm(okunanDeğerler)
            
    time.sleep(600) #ölçümler arası 10 dakika

