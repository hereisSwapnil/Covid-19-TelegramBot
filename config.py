import os

firebaseConfig = {
    "apiKey": str(os.environ['apikey']),
    "authDomain": str(os.environ['authd']),
    "databaseURL": str(os.environ['dataurl']),
    "projectId": str(os.environ['projectid']),
    "storageBucket": str(os.environ['storagebkt']),
    "messagingSenderId": str(os.environ['messagesendid']),
    "appId": str(os.environ['appid']),
    "measurementId": str(os.environ['measureid'])
  }

token_public = str(os.environ['YOUR_TELEGRAMBOT_TOKEN'])
owner = str(os.environ['OWNER_USERNAME'])
owner_id_telegram = int(os.environ['OWNER_TELEGRAM_ID'])
