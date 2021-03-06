
import sys
import codecs
import random
import os

import urllib

from flask import Flask, json, jsonify, request
from flask import render_template, url_for, redirect

from words import Word, Words


WORDS = []

# read in lists of words from file system
def get_words_lists():

  files = os.listdir('./lists')
  names_list = []

  for file in files:
      if file.find('.txt'):
        print (file)
        names = file.split('.')
        names_list.append(names[0])
        WORDS.append(Words(names[0]))

  return names_list

app = Flask(__name__)

# root path, redirect to the lists page
@app.route('/')
def root():
  return redirect(url_for('get_words_list'))

# static test page: welcome
@app.route('/welcome')
def welcome():
  return redirect(url_for('static', filename='welcome.html'))

# synamic test page: hello
@app.route('/hello')
def hello(name=None):

  return render_template('hello.html')

# main entrance of the app, lists of words
@app.route('/list', methods=['GET', 'POST'])
def get_words_list(name=None):

  names_list = []
  for words in WORDS:
    names_list.append(words.name)

  if names_list:
    return render_template('list.html', lists=names_list)
  else:
    return render_template('hello.html', name='Empty List')
    
# the entrance page for a list of words:
#   - all words listed
#   - status and link for flash cards
#   - status and link for quiz
@app.route('/words')   
def get_words(name=None, card_reset=False, quiz_reset=False):

  if len(request.args) > 0:
    words_list = None
    for words_list in WORDS:
      print (words_list.name)
      if words_list.name == request.args['name']: break
    
    if words_list:
      if request.args['card_reset']=='True': 
        words_list.card_count = 0

      if request.args['quiz_reset']=='True': 
        words_list.quiz_count = 0
        for word in words_list.words:
          word.revisit_quiz = True

      return render_template('words.html', words=words_list)
      
  return render_template('hello.html', name='No Words!')

# quiz page for a words list
@app.route('/quiz')
def show_quiz(name=None, revisit=-1):

  if len(request.args) > 0:
    name = request.args['name']
    revisit = request.args['revisit']

    for words_list in WORDS:
      if words_list.name == name: break

    if words_list:

      if not revisit == '-1':
        words_list.words[int(revisit)].revisit_quiz = True
      else: words_list.quiz_count += 1

      if words_list.quiz_count <= words_list.total:
        i = random.randint(0, words_list.total-1)

        while words_list.words[i].revisit_quiz == False:
          i = random.randint(0, words_list.total-1)

        print (words_list.quiz_count, ":", i, words_list.words[i].english_name, revisit)
          
        words_list.words[i].revisit_quiz = False
        words_list.words[i].generate_quiz()
        
        return render_template('quiz.html', words_list=words_list.words, name=name, index=i, count= words_list.quiz_count)

      else: 
        words_list.quiz_count -= 1
        return render_template('quiz.html', words_list=words_list.words, name=name, index=-1, count= words_list.quiz_count)

    return render_template('hello.html', name='No Quiz')


@app.route('/answer', methods=['POST'])
def show_answer(answer=None):

  if len(request.args) > 0:
    answer = request.args['answer']
    print (answer)
    return jsonify({'answer': answer})
  else: return jsonify({'answer': ' '})

# flash card page for a lsit of words  
@app.route('/card')
def get_flash_card(name=None, direction='next'):

  if len(request.args) > 0:
    name = request.args['name']
    direction = request.args['direction']

    for words_list in WORDS:
      if words_list.name == name: break
   
    if words_list:

      if direction == 'next':
        words_list.card_count += 1
      else: words_list.card_count -= 1

      print (direction, words_list.total, words_list.card_count)

      if words_list.card_count <= words_list.total and words_list.card_count > 0:
        return render_template('card.html', words_list=words_list, name=name)
      else: 
        words_list.card_count -= 1
        return render_template('card.html', words_list=[], name=name)

  else:
    return render_template('hello.html', name='No Word')
    
if __name__ == '__main__':
  print ("initializing in main(): read in words...")
  names_list = get_words_lists()

  app.debug = True
  app.run()


