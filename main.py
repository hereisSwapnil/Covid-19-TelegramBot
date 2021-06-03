import telebot
from bs4 import BeautifulSoup as bs
import requests
import pyrebase
import config

bot = telebot.TeleBot(token=config.token_public)
# ...................................................................................................
# Database
firebase = pyrebase.initialize_app(config.firebaseConfig)
db = firebase.database()
# ...................................................................................................

def all_info_get():
    url = "https://www.mygov.in/covid-19"
    response = requests.get(url)
    bs_html = bs(response.text , "html.parser")
    info = bs_html.find("div","information_row")
    L = ""

    acblock1 = info.find("div" , "active-case")
    acblock2 = acblock1.find("div" , "block-active-cases")
    active_cases = acblock2.find("span" , "icount").get_text().rstrip().lstrip()
    acblock3 = acblock2.find("div" , "increase_block")
    active_cases_new_today = acblock3.find("div" , "color-green down-arrow").get_text().rstrip().lstrip()

    ttblock1 = info.find("div" , "iblock t_case")
    ttblock2 = ttblock1.find("div" , "iblock_text")
    total_cases = ttblock2.find("span" , "icount").get_text().rstrip().lstrip()
    ttblock3 = ttblock2.find("div" , "increase_block")
    total_cases_new_today = ttblock3.find("div" , "color-red up-arrow").get_text().rstrip().lstrip()

    dcblock1 = info.find("div" , "iblock discharge")
    dcblock2 = dcblock1.find("div" , "iblock_text")
    discharged_cases = dcblock2.find("span" , "icount").get_text().rstrip().lstrip()
    dcblock3 = dcblock2.find("div" , "increase_block")
    discharged_cases_new_today = dcblock3.find("div" , "color-green up-arrow").get_text().rstrip().lstrip()

    dblock1 = info.find("div" , "iblock death_case")
    dblock2 = dblock1.find("div" , "iblock_text")
    death_cases = dblock2.find("span" , "icount").get_text().rstrip().lstrip()
    dblock3 = dblock2.find("div" , "increase_block")
    death_cases_new_today = dblock3.find("div" , "color-red up-arrow").get_text().rstrip().lstrip()

    Text_line = f"*Total Cases* : {total_cases}\n(+{total_cases_new_today})\n*Active* : {active_cases}\n(+{active_cases_new_today})\n*Discharged* : {discharged_cases}\n(+{discharged_cases_new_today})\n*Deaths* : {death_cases}\n(+{death_cases_new_today})"
    return Text_line


def get_state_info(code):
    url = "https://www.mygov.in/covid-19"
    response = requests.get(url)
    bs_html = bs(response.text , "html.parser")
    info = bs_html.find("div","information_row")
    a = bs_html.find("div" , "marquee_data view-content")
    b = a.findAll("div" , "views-row")
    st_details = []
    for i in range(36):
        a = b[i]
        a_1 = a.find("div" ,"st_all_counts" )
        st_name = a.find("span" , "st_name").get_text()
        st_number = a.find("span" , "st_number").get_text()
        tick_confirmed = a_1.find("div" , "tick-confirmed" ).get_text()
        tick_active = a_1.find("div" , "tick-active").get_text()
        tick_discharged = a_1.find("div" , "tick-discharged").get_text()
        tick_death = a_1.find("div" , "tick-death").get_text()
        list = []
        list.append(st_name)
        list.append(st_number)
        list.append(tick_confirmed)
        list.append(tick_active)
        list.append(tick_discharged)
        list.append(tick_death)
        st_details.append(list)

    return st_details[code]



# ////////////////////////commands...

@bot.message_handler(commands=["send"])
def send_welcome(message):
    ids = []
    if message.from_user.username == config.owner:
            peoples = db.get()
            for people in peoples.each():
                a = people.val()
                ids.append(a.get("id")) 
                a = message.text
                a = a[6:]
                text = a
                for i in range (len(ids)):
                    try:
                        id = str(ids[i])
                        bot.send_message(id , text)
                    except:
                        pass
                ids = []


@bot.message_handler(commands=["admin"])
def send_welcome(message):
    if message.from_user.username == config.owner:
        text_1 = f"/send_daily \n/send\nThese are commands for admin"
        bot.reply_to(message , text_1)


@bot.message_handler(commands=["send_daily"])
def send_welcome(message):
    ids = []
    if message.from_user.username == config.owner:
        text = f"Commands :\n1.  /get     [ This will provide u details of India ]\n2.  /sthelp     [ This is help you to get state-wise data ]\n3.  /subscribe     [ To recieve further updates ]\n4.  /unsubscribe     [ Not to recieve further updates ]"
        peoples = db.get()
        for people in peoples.each():
            a = people.val()
            ids.append(a.get("id"))

        for i in range (len(ids)):
            try:
                id = str(ids[i])
                bot.send_message(id , all_info_get() , parse_mode ="Markdown")
                bot.send_message(id, text , parse_mode ="Markdown" )
            except:
                pass
        
        ids = []


@bot.message_handler(commands=["subscribe"])
def send_welcome(message):
    ids = []
    try:
        id =  message.from_user.id
        a = message.from_user.username
        if a==None:
            a = message.from_user.first_name
        else:
            a = "@"+a
        good = a+" has subscribed Covid-19 Bot"
        text = f"You have Subscribed to our Covid-19 Bot\nYou will recieve further updates and notifications\nIf you dont want to recieve notification then /unsubscribe"

        peoples = db.get()
        for people in peoples.each():
            a = people.val()
            ids.append(a.get("id"))

        to_do = ""
        for i in range(len(ids)):
            if ids[i] == message.from_user.id:
                to_do = "no"
        
        if to_do != "no":

            data = {
                    "id" : id
                    }

            db.push(data)

            bot.reply_to(message , text)
            bot.send_message(config.owner_id_telegram, good)       
        else:
            bot.reply_to(message , "You have already Subscribed !!")
        ids = []

    except:
        bot.reply_to(message , "Problem in following your request . Please wait and try again later")
        bot.send_message(config.owner_id_telegram, "subscribe command is making a problem") 
        ids = []


@bot.message_handler(commands=["unsubscribe"])
def send_welcome(message):
    ids = []
    try:
        id =  message.from_user.id
        if id == config.owner_id_telegram:
             bot.reply_to(message , "Lol You can't Unsubscribe !!")
        elif id != config.owner_id_telegram :
            a = message.from_user.username
            if a==None:
                a = str(message.from_user.first_name) 
            else:
                a = "@"+ a
            good = a + " has unsubscribed Covid-19 Bot"
            text = f"You have Unsubscribed to our Covid-19 Bot\nYou will not recieve further updates and notifications\nIf you want to recieve notification then /subscribe"
                
            peoples = db.get()
            for people in peoples.each():
                a = people.val()
                ids.append(a.get("id"))

            to_do = ""
            for i in range(len(ids)):
                if ids[i] == message.from_user.id:
                    to_do = "no"
                
            if to_do == "no":
                        ids = []
                        keys = []
                        peoples = db.get()
                        for people in peoples.each():
                            a = people.val()
                            b = people.key()
                            keys.append(b)
                            ids.append(a.get("id"))

                        for i in range (len(ids)):
                            if ids[i] == id:
                                index = i

                        db.child(keys[index]).remove()
                        ids = []
                        bot.reply_to(message , text)
                        bot.send_message(config.owner_id_telegram, good)   

        else:
            bot.reply_to(message , "You have already Unsubscribed !!")
            ids = []
    except:
        bot.reply_to(message , "Problem in following your request . Please wait and try again later")
        bot.send_message(config.owner_id_telegram, "subscribe command is making a problem")
        ids = []


@bot.message_handler(commands=["start"])
def send_welcome(message):
    ids = []
    try:
        s = message.from_user.username
        if s == None :
            text = f"Hey "  + ", Welcome to COVID - 19 bot...This will provide you\nlatest details For Coronavirus Disease( INDIA ) .\nCommands :\n1.  /get     [ This will provide u details ]\n2.  /help     [ This is help you with commands ]\n2.  /sthelp     [ This is help you to get state-wise data ]\n3.  /subscribe     [ To recieve further updates ]\n4.  /unsubscribe     [ Not to recieve further updates ]"
            bot.reply_to(message , text)
        else:
            s_final = "@" + s
            good = s_final +" has joined Covid-19 Bot"
            text = f"Hey "  + s +", Welcome to COVID - 19 bot...This will provide you\nlatest details For Coronavirus Disease( INDIA ) .\nCommands :\n1.  /get     [ This will provide u details ]\n2.  /help     [ This is help you with commands ]\n2.  /sthelp     [ This is help you to get state-wise data ]\n3.  /subscribe     [ To recieve further updates ]\n4.  /unsubscribe     [ Not to recieve further updates ]"
            bot.reply_to(message , text)
            bot.send_message(config.owner_id_telegram, good )
        

        peoples = db.get()
        for people in peoples.each():
            a = people.val()
            ids.append(a.get("id"))


        to_do = ""
        for i in range(len(ids)):
            if ids[i] == message.from_user.id:
                to_do = "no"
        
        if to_do != "no":
            id = message.from_user.id

            data = {
                "id" : id
                    }

            db.push(data)

        else:
            pass
        ids = []

    except:
        bot.reply_to("Problem in following your request . Please wait and try again later")
        bot.send_message(config.owner_id_telegram,"start command is making a problem")


@bot.message_handler(commands = ["sthelp"])
def helpst_get(message):
    try:
        text = "/andaman \n/andhra \n/arunachal \n/assam \n/bihar \n/chandigarh \n/chhattisgarh \n/dadra \n/delhi \n/goa \n/gujrat \n/haryana \n/himachal \n/jnk \n/jharkhand \n/karnataka \n/kerala \n/ladakh \n/lakshadweep \n/madhya \n/maharashtra \n/manipur \n/meghalaya \n/mizoram \n/nagaland \n/odisha \n/puducherry \n/punjab \n/rajasthan \n/sikkim \n/tamil \n/telengana \n/tripura \n/up \n/uttarakhand \n/westbengal"
        bot.reply_to(message , text)
    except:
        bot.reply_to(message , "Problem in following your request . Please wait and try again later")
        bot.send_message(config.owner_id_telegram,"sthelp command is making a problem")


@bot.message_handler(commands=["help"])
def help_message(message):
    try:
        text = f"Commands :\n1.  /get     [ This will provide u details of India ]\n2.  /sthelp     [ This is help you to get state-wise data ]\n3.  /subscribe     [ To recieve further updates ]\n4.  /unsubscribe     [ Not to recieve further updates ]"
        bot.reply_to(message , text)
    except:
        bot.reply("Problem in following your request . Please wait and try again later")
        bot.send_message(config.owner_id_telegram,"help command is making a problem")


@bot.message_handler(commands=["get"])
def get_message(message):
    try:
        L = all_info_get()
    except:
        L = "Error in getting Information . Please Try Again Later . "

    if L == "Error in getting Information . Please Try Again Later . " :
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"get command is making a problem")
    else:
        bot.reply_to(message , L , parse_mode ="Markdown")




# ///////////////////////////////////////////////////////////////


@bot.message_handler(commands = ["andaman"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(0)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"andaman command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["andhra"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(1)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"andhra command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["arunachal"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(2)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"arunachal command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["assam"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(3)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"assam command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["bihar"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(4)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"bihar command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["chandigarh"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(5)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"chandigarh command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["chhattisgarh"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(6)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"chhattisgarh command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["dadra"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(7)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"dadra command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["delhi"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(8)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"delhi command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["goa"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(9)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"goa command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["gujrat"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(10)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"gujrat command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["haryana"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(11)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"haryana command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["himachal"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(12)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"himachal command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["jnk"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(13)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"jnk command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["jharkhand"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(14)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"jharkhand command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["karnataka"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(15)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"karnataka command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["kerala"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(16)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"kerala command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["ladakh"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(17)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"ladakh command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["lakshadweep"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(18)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"lakshadweep command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["madhya"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(19)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"madhya command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["maharashtra"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(20)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"maharashtra command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["manipur"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(21)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"manipur command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["meghalaya"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(22)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"meghalaya command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["mizoram"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(23)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"mizoram command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["nagaland"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(24)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"nagaland command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["odisha"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(25)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"odisha command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["puducherry"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(26)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"puducherry command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["punjab"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(27)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"punjab command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["rajasthan"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(28)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"rajasthan command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["sikkim"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(29)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"sikkim command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["tamil"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(30)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"tamil command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["telengana"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(31)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"telengana command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["tripura"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(32)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"tripura command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["up"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(33)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"up command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["uttarakhand"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(34)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"uttarakhand command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

@bot.message_handler(commands = ["westbengal"])
def andaman_get(message):
    state_de = ""
    try:
        a = get_state_info(35)

    except:
        state_de = "no"

    if state_de == "no":
        bot.reply_to(message , "Error in getting Information . Please Try Again Later .")
        bot.send_message(config.owner_id_telegram,"westbengal command is making a problem")

    elif state_de != "no":
        name = f"Covid cases in *{a[0]}* :-"
        confirm = a[2]
        active = a[3]
        discharge = a[4]
        death = a[5]
        text = f"{name}\n{confirm}\n{active}\n{discharge}\n{death}"
        bot.reply_to(message , text , parse_mode ="Markdown")

# //////////////////////////////////////////////////////////////


while True:
    print("Started")
    bot.polling()