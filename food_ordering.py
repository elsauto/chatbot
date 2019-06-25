import sys
from termcolor import colored

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

import re

# Background
# A conversational chabot system helps restaurant guests order food and presents the
# resulting check (summary of the order) to the guests.

# As a starting point the guests’ check contains the following:
#   [2 large pepperoni pizzas, 3 sugar free sodas]
# Based on this, the customer decides to change one of the items of the check for another item. This
# change could be expressed in two ways:
#   ‘Make one soda regular’ (using the singular version of the name)
# or
#   ‘Make one of the drinks a regular’ (using a synonym of the item)
# These describe two alternative new orders that express the intent ‘change’:
#   [1 soda regular]
# or
#   [1 drinks regular] (note that the extraction of words will maintain the plural form)
#
# Task: Implement a function in Python that can take orders of both kinds (singular/plural or synonyms of
# original item) and change the original check returning a new_check that must look like this:
# [2 large pepperoni pizzas, 2 sugar free sodas, 1 regular soda]
# You can use both Python NLP libraries and/or implement you own tools (dictionaries, etc.)
# def change_check(check, new_order):
# return new_check

# Control array
order = []

# Request control dict
request_dict = {}

# Flavors, types and basic synonims
# NOTE synonyms could get obtained from wordnet
# For easiness we just create our own list
pizza_flavors = ['pepperoni', 'mushrooms', 'onions', 'sausage',
                 'bacon', 'extra-cheese', 'green peppers']

drink_flavors = ['regular', 'diet']

drink_synonims = ['drink', 'drinks', 'soda', 'sodas']

# Helpers

# Return number

# NOTE At this point either is a casteable int
# Or we can safely apply text2int
def _get_number(word):
    try:
        return int(word)
    except ValueError:
        return text2int(word.lower())


# Convert string to integer helper
def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty",
                "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


# Order
def start_order():
    # Start new order
    current_order = take_order()
    print_current_check(current_order)
    # Ask customer if any change is needed
    while customer_wants_change_check(current_order):
        change_check(current_order)
        print_current_check(current_order)


def take_order():
    # We assume items are listed following a few rules
    # since the input should be limited by UI components

    # For quantity, we expect numbers written as integers (e.g. 2)
    # TODO use helper to translate words to numbers

    # For drinks, we expect type and flavor (e.g. regular cola)

    # For food, we expect size, flavor and dish (e.g. pepperoni pizza)
    # NOTE is this a fair assumption for a chatbot?

    # Start by taking pizza order

    print(colored('Welcome to Sebastiano\'s. Please begin with your order. \n'
                  'When finished in every step, please just type', 'green'),
          colored('done.', 'yellow'))
    
    # Define new order
    order_dict = {'pizzas': {}, 'drinks': {}}
    
    _order_pizza(order_dict)

    _order_drinks(order_dict)
    
    return order_dict


# Ask customer which pizza/s they want and validate input
def _order_pizza(order_dict):
    first = True

    while True:
        if first:
            print(colored('First, lets start with your food. Available pizza options are:', 'green'),
                  colored((', '.join(pizza_flavors)), 'yellow'))
            print(colored(
                'Please input your choice by selecting quantity and flavor. E.g. 2 pepperoni pizzas', 'green'))
            line = input().lower()
            first = False
        else:
            line = input(colored(
                'Anything else?. You can still add some more flavors: \n', 'green')).lower()

        if line == "done":
            break
        else:
            if _is_valid(line):
                request_dict = _pre_process_request(line)
                if request_dict:
                    order_dict['pizzas'].update({
                        request_dict['pizzas']: request_dict['quantity']})
                    order.append(line)
            else:
                print(colored(
                    'Seems to be something we don\'t have, please enter your request again', 'red'))
                pass


def _is_valid(line):
    valid = re.match('^((\d|\w+)\s(\w+|\w+-\w+)\s(\w+))$', line)
    return valid


# Ask customer which drink/s they want and valide input
def _order_drinks(order_dict):
    first = True

    while True:
        if first:
            print(colored('Now, lets pick your drinks. Available drinks options are:', 'green'),
                  colored((', '.join(drink_flavors)), 'yellow'))
            print(colored(
                'Please input your choice by selecting quantity and flavor. E.g. 2 diet sodas', 'green'))
            line = input().lower()
            first = False
        else:
            line = input(colored(
                'Anything else?. You can still add some more drinks: \n', 'green')).lower()

        if line == "done":
            break
        else:
            if _is_valid(line):
                request_dict = _pre_process_request(line)
                if request_dict:
                    order_dict['drinks'].update({
                        request_dict['drinks']: request_dict['quantity']})
                    order.append(line)
            else:
                print(colored(
                    'Seems to be something we don\'t have, please enter your request again', 'red'))
                pass

def print_current_check(current_order):    
    pizzas = ""
    for flavor, quantity in current_order['pizzas'].items():
        pizzas += ("%d %s %s" % (quantity, flavor, "pizzas "))

    drinks = ""
    for flavor, quantity in current_order['drinks'].items():
        drinks += ("%d %s %s" % (quantity, flavor, "sodas "))

    print(colored('Your current check is: ' + pizzas + drinks, 'blue'))
        

def customer_wants_change_check(current_order):
    change_order = input(colored('Do you wish to modify your order? [y\\N]: ', 'green')).lower()
    if change_order == 'y' or change_order == 'yes':
        return True
    else:
        print(colored(
            'Thanks for your order, we will delivering it soon!', 'blue'))
        return False

def change_check(check, new_order=[]):
    new_order = input(colored('What do you want to change?: ', 'green')).lower()

    new_order_dict = _pre_process_request(new_order)
    
    if new_order_dict:
        action = new_order_dict.get('action', 'add')
        quantity = new_order_dict.get('quantity')
        pizzas = new_order_dict.get('pizzas')
        drinks = new_order_dict.get('drinks')

        if action == "update":            
            if drinks:
                diet_quantity = check['drinks'].get('diet', 0)
                regular_quantity = check['drinks'].get('regular', 0)
                if new_order_dict['drinks'] == 'regular':
                    diet_quantity -= quantity
                    regular_quantity += quantity    
                elif new_order_dict['drinks'] == 'diet':
                    diet_quantity += quantity
                    regular_quantity -= quantity 
                
                check['drinks'].update({'diet': max(0, diet_quantity)})
                check['drinks'].update({'regular': max(0, regular_quantity)})

            if pizzas:
                pass
                # NOTE Action not defined in challenge, open to discussion
                # with the interviewer
   
        elif action == "add":
            if drinks:
                drinks_quantity = check['drinks'].get(drinks, 0) + quantity
                check['drinks'].update({drinks: max(0, drinks_quantity)})
            
            if pizzas:
                pizzas_quantity = check['pizzas'].get(pizzas, 0) + quantity
                check['pizzas'].update({pizzas: max(0, pizzas_quantity)})

        elif action == "delete":
            if drinks:
                drinks_quantity = check['drinks'][drinks] - quantity
                check['drinks'].update({drinks: max(0, drinks_quantity)})
        
            if pizzas:
                pizzas_quantity = check['pizzas'][pizzas] - quantity
                check['pizzas'].update({pizzas: max(0, pizzas_quantity)})
        else:
            print(colored(
                'We couldn\'t process your change, please try again', 'red'))


# Stopword removal and stemming/lemmatization
def _pre_process_request(request):
    ps = PorterStemmer()
    stop_words = set(stopwords.words("english"))

    # tokenize request
    tokenized_set = word_tokenize(request)

    # remove stop words
    # make lookups more efficient
    filtered_set = []
    for w in tokenized_set:
        if w not in stop_words:
            filtered_set.append(w)

    # stemming using porter stemmer algorithm
    stemmed_words = []
    for w in filtered_set:
        stemmed_words.append(ps.stem(w))
    
    clean_order = stemmed_words
    
    # action
    request_dict = {}
    
    # there are items to modify
    quantity = 0; pizza_flavor = 0; drink_type = 0
    
    for w in clean_order:
        if isa_verb(w):
            if w == "make":
                # need to update order
                request_dict.update({'action': 'update'})
            elif w == "add":
                # need to add something
                request_dict.update({'action': 'add'})
            elif w == "remove":
                # need to remove something
                request_dict.update({'action': 'remove'})
        elif isa_number(w):
            quantity = _get_number(w)
            request_dict.update({'quantity': quantity})
        elif isvalid_flavor(w):
            pizza_flavor = 1
            request_dict.update({'pizzas': w})
        elif isvalid_drink_type(w):
            drink_type = 1
            request_dict.update({'drinks': w})
    
    # TODO Add pairs control
    # If we got a pizza flavor, then we need the word "pizza"
    # If we got a drink type, then we need the word (or synonym)
    # for "drink"
    
    if not quantity:
        print(colored(
                'You need to specify an amount, please enter your request again', 'red'))
        request_dict = {} 
    
    if not (pizza_flavor or drink_type):
        print(colored(
                'Seems to be something we don\'t have, please enter your request again', 'red'))
        request_dict = {}
    
    return request_dict


# Validations
def isvalid_item(item, inventory):
    if item in inventory:
        return True
    else:
        return False


def isa_number(word):
    try:
        int(word)
        return True
    except ValueError:
        try:
            text2int(word.lower())
            return True
        except Exception:
            return False


def isa_verb(word):
    possible_verbs = ['make', 'add', 'remove']
    return isvalid_item(word, possible_verbs)


def isvalid_drink_type(drink_type):
    valid_drink_types = ['regular', 'sugar-free', 'diet']
    return isvalid_item(drink_type, valid_drink_types)


def isvalid_drink(drink):
    valid_drinks = ['drink', 'drinks', 'soda', 'sodas']
    isvalid_item(drink, valid_drinks)


def isvalid_food(food):
    # We assume is the only kind of food we sell
    valid_food = ['pizza']
    isvalid_item(food, valid_food)


def isvalid_flavor(flavor):
    valid_flavor = ['pepperoni', 'mushrooms', 'mushroom',
                    'onions', 'onion', 'sausag', 'sausage', 'sausages',
                    'bacon', 'extra-cheese', 'extra-chees',
                    'green-pepp', 'green-peppers']
    return isvalid_item(flavor, valid_flavor)


# More sophisticated way for looking synonyms
def _lookup_syn(word):
    for syn in wordnet.synsets(word):
        for name in syn.lemma_names():
            print(name)

start_order()