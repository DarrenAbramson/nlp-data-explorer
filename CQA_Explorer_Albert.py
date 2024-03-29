import json
import time
import os
import sys
import random
import select
import urllib.request
import pandas as pd
import ast

# Check if data files are there.
# As of Aug. 23, here are the hard links
# to the AWS storage provided by the authors
# of Commonsense QA at
# https://www.tau-nlp.org/commonsenseqa
# https://s3.amazonaws.com/commensenseqa/train_rand_split.jsonl

# Download just the random training partition of the data. if not in the
# current directory. Only ~3.8MB of data

#if not os.path.isfile("train_rand_split.jsonl"):
#    os.system('clear')
#    print("Please wait, downloading training random split (~3.8MB)")
#    time.sleep(5)
#    url = "https://s3.amazonaws.com/commensenseqa/train_rand_split.jsonl"#
#
#    with urllib.request.urlopen(url) as response:
#        data = response.read() # a `bytes` object
#        with open("train_rand_split.jsonl", "wb") as file:
#            file.write(data)

# In this variant of CQA_Explorer we read the questions and Albert status
# from a .CSV generated by scoring the above data set using PLLs.

albertQuestionSet = pd.read_csv("albert-xxlarge-v2_CQA.csv")

albertGotRight = albertQuestionSet[albertQuestionSet["isCorrect"]]
albertGotWrong = albertQuestionSet[albertQuestionSet["isCorrect"]==False]

# Data structure for storing the entire contents of the downloaded file.
# questionsWithAnswers = []

# Questions that are asked during a single run to save and print
# performance record and statistics, and IDs of asked questions.
askedQuestions = []

totalQuestionsAsked = 0.
totalQuestionsRight = 0.

# Read file into data structure
#with jsonlines.open('train_rand_split.jsonl') as reader:
#    for obj in reader:
#        questionsWithAnswers.append(obj)

# Store total number of questions for random question selection
numQuestions = len(albertGotRight) + len(albertGotWrong)

# Uncomment lines below to verify size of dataset.
# Should print:
## The number of questions is 9741
## numQuesString = f"The number of questions is {numQuestions}"
## print(numQuesString)
## time.sleep(2)


# Welcome screen
os.system('clear')
print("Welcome to CommonsenseQA Explorer!")
print("This program does not store data between runs, \
so save your system.out somewhere!")
print("")
print("")

# Query for time limit
timeLimit = False
timeLimit = input("Would you like a time limit for questions? (y/n) ")

secondsToWait = -1
timedTest = False

if timeLimit == "y":
    print("")
    seconds = input("Please enter a time limit in seconds. ")
    try:
        seconds = int(seconds)
        secondsToWait = seconds
        timedTest = True
        print("Successfully set time limit to ", seconds)
    except:
        print("Sorry, you must enter an integer value.")
    
    #finally:
    #    print("No timelimit!")
    
time.sleep(2)
os.system('clear')

# Query for albert right/wrong mix
#timeLimit = False
#timeLimit = input("Would you like a time limit for questions? (y/n) ")
#secondsToWait = -1
#timedTest = False

albertRightQs = 0
albertWrongQs = 0

albertRightQs = input(f"How many of the {len(albertGotRight)} CQA examples that Albert got right would you like to try? ")
albertWrongQs = input(f"How many of the {len(albertGotWrong)} CQA examples that Albert got wrong would you like to try? ")

questionsWithAnswers = pd.concat([albertGotRight.sample(int(albertRightQs)), albertGotWrong.sample(int(albertWrongQs))])
questionsWithAnswers = questionsWithAnswers.sample(frac=1)

time.sleep(2)
os.system('clear')

# Approach borrowed from https://stackoverflow.com/questions/15528939/python-3-timed-input/15533404#15533404

# Helper exception for timeout approach
class TimeoutExpired(Exception):
    pass

# Helper function for taking input with a timeout
def input_with_timeout(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [],[], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n') # expect stdin to be line-buffered
    raise TimeoutExpired

# Main question answering function with branching for timeout/no timeout
def do_question(doMore=True, timed=False):
    # Referencing main variables
    global totalQuestionsAsked
    global totalQuestionsRight
    

    # Get next question, 0 based indexing
    newQuestion = questionsWithAnswers.iloc[int(totalQuestionsAsked)]

    questionText = newQuestion["questionText"]

    options = ast.literal_eval(newQuestion["options"])

    totalQuestionsAsked += 1

    
    # Print question
    # Looks better flush at top.
    # print("")
    print(questionText)
    print("")
    
    # Print answer options
    for opt in options:
        #print("")
        print(opt["label"], opt["text"])
    
    print("")
    
    # Timing starts after info taken from user and q/a printed,
    # but before branching into timed/untimed interfaces.
    timeStart = time.perf_counter()
    
    if timed:
        
        prompt = "You have %d seconds to choose the correct answer (case sensitive):\n" % secondsToWait
        
        try:
            answer = input_with_timeout(prompt, secondsToWait)
        except TimeoutExpired:
            print('Sorry, times up')
            # Set answer to an always wrong answer
            answer = "Q"
        else:
            print('Got %r' % answer)
            
    
    else:
        prompt = "enter answer (case sensitive): "
        answer = input(prompt)
    
    
    timeFinish = time.perf_counter()
    timeElapsed = timeFinish - timeStart

    if answer == newQuestion["answerKey"]:
        # Increment correct
        totalQuestionsRight += 1
        #time.sleep(2)
    os.system('clear')
    
    # Record enough to reconstruct this question/answer event:
    # * time
    # * user answer
    # * correct answer -- NOPE since is in existing data structure
    # * question (just use existing data structure?)
    thisQuestion = [newQuestion, answer, timeElapsed]
    askedQuestions.append(thisQuestion)
    
    print("")
    answer = input("Go again?  ")
    if answer == "n" or totalQuestionsAsked == len(questionsWithAnswers):
        doMore = False
        percentCorrect = totalQuestionsRight/totalQuestionsAsked
        goodbyeString = f"Thanks for playing! your overall score was {percentCorrect}."
        print(goodbyeString)
        for q in askedQuestions:
            print(q)
    return doMore

doMore = True

while doMore:
    if timedTest:
        time.sleep(2)
        os.system("clear")
        doMore = do_question(doMore, True)
    else:
        time.sleep(2)
        os.system("clear")
        doMore = do_question(doMore, False)
