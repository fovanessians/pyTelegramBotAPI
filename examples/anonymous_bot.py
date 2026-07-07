# This bot is needed to connect two people and their subsequent anonymous communication
#
# Avaiable commands:
# `/start` - Just send you a messsage how to start
# `/find` - Find a person you can contact
# `/stop` - Stop active conversation

import telebot
from telebot import types

# Initialize bot with your token
bot = telebot.TeleBot('TOKEN')

# The `users` variable is needed to contain chat ids that are either in the search or in the active dialog, like {chat_id, chat_id}
users = {}
# The `freeid` variable is needed to contain chat id, that want to start conversation
# Or, in other words: chat id of user in the search
freeid = None

# `/start` command handler
#
# That command only sends you 'Just use /find command!'
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, 'Just use /find command!')

# `/find` command handler
#
# That command finds opponent for you
#
# That command according to the following principle:
# 1. You have written `/find` command
# 2. If you are already in the search or have an active dialog, bot sends you 'Shut up!'
# 3. If not:
#   3.1. Bot sends you 'Finding...'
#   3.2. If there is no user in the search:
#       3.2.2. `freeid` updated with `your_chat_id`
#   3.3. If there is user in the search:
#       3.3.1. Both you and the user in the search recieve the message 'Founded!'
#       3.3.2. `users` updated with a {user_in_the_search_chat_id, your_chat_id}
#       3.3.3. `users` updated with a {your_chat_id, user_in_the_search_id}
#       3.3.4. `freeid` updated with `None`
@bot.message_handler(commands=['find'])
def find(message: types.Message):
    global freeid

    if message.chat.id not in users:
        bot.send_message(message.chat.id, 'Finding...')

        if freeid is None:
            freeid = message.chat.id
        else:
            # Question:
            # Is there any way to simplify this like `bot.send_message([message.chat.id, freeid], 'Founded!')`?
            bot.send_message(message.chat.id, 'Founded!')
            bot.send_message(freeid, 'Founded!')

            users[freeid] = message.chat.id
            users[message.chat.id] = freeid
            freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'Shut up!')

# `/stop` command handler
#
# That command stops your current conversation (if it exist)
#
# That command according to the following principle:
# 1. You have written `/stop` command
# 2. If you are not have active dialog or you are not in search, bot sends you 'You are not in search!'
# 3. If you are in active dialog:
#   3.1. Bot sends you 'Stopping...'
#   3.2. Bot sends 'Your opponent is leavin`...' to your opponent
#   3.3. {your_opponent_chat_id, your_chat_id} removes from `users`
#   3.4. {your_chat_id, your_opponent_chat_id} removes from `users`
# 4. If you are only in search:
#   4.1. Bot sends you 'Stopping...'
#   4.2. `freeid` updated with `None`
@bot.message_handler(commands=['stop'])
def stop(message: types.Message):
    global freeid

    if message.chat.id in users:
        bot.send_message(message.chat.id, 'Stopping...')
        bot.send_message(users[message.chat.id], 'Your opponent is leavin`...')

        del users[users[message.chat.id]]
        del users[message.chat.id]
        
        print(users, freeid) # Debug purpose, you can remove that line
    elif message.chat.id == freeid:
        bot.send_message(message.chat.id, 'Stopping...')
        freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'You are not in search!')

# message handler for conversation
#
# That handler needed to send message from one opponent to another
# If you are not in `users`, you will recieve a message 'No one can hear you...'
# Otherwise all your messages are sent to your opponent
#
# Questions:
# 1. Is there any way to improve readability like `content_types=['all']`?
# 2. Is there any way to register this message handler only when i found the opponent?
@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def chatting(message: types.Message):
    if message.chat.id in users:
        bot.copy_message(users[message.chat.id], users[users[message.chat.id]], message.id)
    else:
        bot.send_message(message.chat.id, 'No one can hear you...')

#############CLASSIFICATION###############
##########################################
from transformers import pipeline
from PIL import Image
import io
# Load Google's SigLIP model (Open weights, Apache 2.0 license)
'''zero-shot image classification pipeline using the SigLIP (Sigmoid Loss for Language Image Pre-Training) '''
classifier = pipeline(
  "zero-shot-image-classification", model="google/siglip-so400m-patch14-384")

@bot.message_handler(commands=["animals"])
def animals(message):  
  #input file_id
  bot.send_message(message.chat.id, "Upload the photo you want to classify")
  # Register id handler for the next message
  bot.register_next_step_handler(message, process_id)
  
def process_id(message):
  if message.content_type != 'photo':
    bot.reply_to(message, "That's not a photo.")
  else:  
      # Download the image from Telegram
      file_id = message.photo[-1].file_id
      file_info = bot.get_file(message.photo[-1].file_id)
      downloaded_file = bot.download_file(file_info.file_path)
      bot.send_message(message.chat.id, f"processing...\n *{file_id}* \n into the Bretters algorithm, please wait...", parse_mode="Markdown")
      # Convert bytes to PIL Image
      image = Image.open(io.BytesIO(downloaded_file)).convert("RGB")
      #classification algorithm
      results = classifier(image, candidate_labels=["eagle or   rabbit", "a photo of a tough, hawk"]) #results[0]['label']
      listResults = []
      for item in results:
        label = item.get('label')
        score = item.get('score')
        listResults.append((label, score))
  print(listResults[0][0])
  print(listResults[0][1])
  print(listResults[1][0])
  print(listResults[1][1])
  bot.reply_to(message, 'strong probability of being ' + listResults[0][0])

##########################################
#############CLASSIFICATION###############

bot.infinity_polling(skip_pending=True)
