import xml.etree.ElementTree as ET
import os
import time
import urllib.request
import zipfile
import re
import jsonlines
import random
import sys
import select

# Check if data files are there.
# Links are checked up to Oct. 1, 2020

# Winogrande is like a pair of pants: it comes
# in sizes and flavours. xs/s/m/l/xl, and then
# train and test, and some "debiased".

# Here we go with train_xl.jsonl and train_xl-labels.lst,
# but feel free to try the others out.


####
# Get files

Winograd='WSCollection.xml'
WinograndeQ='./winogrande_1.1/train_xl.jsonl'
WinograndeA='./winogrande_1.1/train_xl-labels.lst'

# Get Winograd
if not os.path.isfile(Winograd):
    os.system('clear')
    print("Please wait, downloading Winograd")
    time.sleep(5)
    url = "https://cs.nyu.edu/faculty/davise/papers/WinogradSchemas/WSCollection.xml"
    with urllib.request.urlopen(url) as response:
        data = response.read()
        with open("WSCollection.xml","wb") as file:
            file.write(data)

# Get Winogrande
if not (os.path.isfile(WinograndeQ) and os.path.isfile(WinograndeA)):
    os.system('clear')
    print("Please wait, downloading Winogrande")
    time.sleep(5)
    url = "https://storage.googleapis.com/ai2-mosaic/public/winogrande/winogrande_1.1.zip"
    with urllib.request.urlopen(url) as response:
        data = response.read()
        with open("winogrande_1.1.zip","wb") as file:
            file.write(data)
    with zipfile.ZipFile("winogrande_1.1.zip", 'r') as zip_ref:
        zip_ref.extractall(".")


####
# Process files

# Parse Winograd

tree = ET.parse('WSCollection.xml')
root = tree.getroot()

# This corrects some weirdness in the dataset
def cleanSentence(sentence):
    sentence = sentence.replace('\n', ' ')
    sentence = re.sub(' +',' ', sentence)
    return sentence

WinogradQA = []

for schema in root:
    schemaDict = {}
    text = schema.find('text')
    txt1 = text.find('txt1').text
    pron = text.find('pron').text
    txt2 = text.find('txt2').text
    answers = schema.find('answers')
    # Get ambiguous sentence
    ambigSentence = txt1 + pron + txt2
    ambigSentence = cleanSentence(ambigSentence)
    # Get first substituted sentence
    firstPronounSub = answers[0].text
    firstSentence = txt1 + " " + firstPronounSub + txt2
    firstSentence = cleanSentence(firstSentence)

    # Get second substituted sentence
    secondPronounSub = answers[1].text
    secondSentence = txt1 + " " + secondPronounSub + txt2
    secondSentence = cleanSentence(secondSentence)

    # Print whole schema
    #print "*********************"
    #print "Ambigous Sentence:"
    schemaDict["AmbSen"] = ambigSentence

    #print "Correct Substitution:"
    correctAnswer = schema.find('correctAnswer').text
    if "A" in correctAnswer:
        schemaDict["CorSen"]=firstSentence
        #print "Incorrect Substitution:"
        schemaDict["InCorSen"]=secondSentence
    else:
        schemaDict["CorSen"]=secondSentence
        #print "Incorrect Substitution"
        schemaDict["InCorSen"]=firstSentence
    WinogradQA.append(schemaDict)

# Parse Winogrande

WinograndeQA_long = []

# Read file into data structure
with jsonlines.open(WinograndeQ) as reader:
    for obj in reader:
        WinograndeQA_long.append(obj)

counter = 0
with open(WinograndeA) as f:
    for line in f: # read rest of lines
        number = int(line.split()[0])
        WinograndeQA_long[counter]["answer"]=number
        counter+=1


# At this point the WinograndeQA has the following format:

#{'qID': '3D5G8J4N5CI2K40F4RZLF9OG2CKVTH-2',
# 'sentence': "Kyle doesn't wear leg warmers to bed,
#              while Logan almost always does. _ is more likely to live in a colder climate.",
# 'option1': 'Kyle',
# 'option2': 'Logan',
# 'answer': '2'}

# This is preprocessed to have a structure that mirrors the WinogradQA structure.

WinograndeQA = []
for schema in WinograndeQA_long:
    schemaDict = {}
    ans = schema["answer"]
    sent = schema["sentence"]
    opt1 = sent.replace("_", schema["option1"])
    opt2 = sent.replace("_", schema["option2"])
    schemaDict["AmbSen"] = sent
    if ans == 1:
        schemaDict["CorSen"] = opt1
        schemaDict["InCorSen"] = opt2
    else:
        schemaDict["CorSen"] = opt2
        schemaDict["InCorSen"] = opt1
    WinograndeQA.append(schemaDict)


numGrad = len(WinogradQA)
numGrande = len(WinograndeQA)

# time.sleep(2)
# os.system('clear')
# print("the number of Winograd is " + str(numGrad))
# print("the number of Winogrande is " + str(numGrande))
# time.sleep(2)
# os.system('clear')

# the number of Winograd is 285
# the number of Winograd is 40398

# Now both data sources should have a format that is identical.
# Winograd comes with pronouns, but Winogrande comes with "_".
# So the quiz is structured only to present substitutions and pick
# the one that is sensible.

# print("Here are some random Winograd:")
# for i in range(0,10):
#      print(random.choice(WinogradQA))
# print("Here are some random Winogrande:")
# for i in range(0,10):
#      print(random.choice(WinograndeQA))

# Example:
# {'AmbSen':
#     'James went to buy a skateboard, which was on sale, or rollerblades. He picked the _ since money was tight.',
#  'CorSen':
#     'James went to buy a skateboard, which was on sale, or rollerblades. He picked the rollerblades since money was tight.',
#  'InCorSen':
#     'James went to buy a skateboard, which was on sale, or rollerblades. He picked the skateboard since money was tight.'}
####
# UI and scoring

# Welcome screen
os.system('clear')
print("Welcome to Winograd/Winogrande Explorer!")
print("This program does not store data between runs, \
so save your system.out somewhere!")
print("")
print("")

# Query for time limit
timeLimit = False
timeLimit = input("Would you like a time limit for individual questions? (y/n) ")

secondsToWait = -1
timedTest = False

if timeLimit == "y":
    print("")
    seconds = input("Please enter a time limit in seconds. ")
    try:
        seconds = int(seconds)
        secondsToWait = seconds
        timedTest = True
        print("Successfully set time limit to", seconds)
    except:
        print("Sorry, you must enter an integer value.")

    #finally:
    #    print("No timelimit!")

time.sleep(2)
os.system('clear')

# Query for grad/grande mix
# numGrad and numGrande defined above.

gradMix = 0
grandeMix = 0

print("")
gradMixIn = input("Please enter the number of Winograd, no more than " + str(numGrad) + "\n")
try:
    gradMix = int(gradMixIn)
    if gradMix > numGrad:
        gradMix = 0
        print("sorry, too many! Winograd set to 0.")
    elif gradMix < 0:
        gradMix = 0
        print("You must enter a positive number. Winograd set to 0.")
    else:
        print("Successfully set the number of Winograd questions to", str(gradMix))
except:
    print("Sorry, you must enter an integer value.")

time.sleep(2)
os.system('clear')

# Query for grad/grande mix
# numGrad and numGrande defined above.

print("")
grandeMixIn = input("Please enter the number of Winogrande, no more than " + str(numGrande) + "\n")
try:
    grandeMix = int(grandeMixIn)
    if grandeMix > numGrande:
        grandeMix = 0
        print("sorry, too many! Winogrande set to 0.")
    elif grandeMix < 0:
        grandeMix = 0
        print("You must enter a positive number. Winogrande set to 0.")
    else:
        print("Successfully set the number of Winogrande questions to", str(grandeMix))
except:
    print("Sorry, you must enter an integer value.")

time.sleep(2)
os.system('clear')

# Need to build a single data structure with random ordering of Winograd and Winogrande questions
# This data structure should "remember" which are d and which are nde.

# Make grad first, then grande. Then permute.

gradList = random.sample(WinogradQA, gradMix)
grandeList = random.sample(WinograndeQA, grandeMix)

for i in gradList:
    i["source"]="d"

for i in grandeList:
    i["source"]="nde"

queryList = gradList + grandeList

random.shuffle(queryList)

#print(str(queryList))
#for i in range(3):
#    print(queryList[i])
#    time.sleep(3)
#time.sleep(10)

# Code to check results
# time.sleep(2)
# os.system('clear')
# print("gradList: \n" + str(gradList))
# print("grandeList: \n" + str(grandeList))
# print("queryList: \n" + str(queryList))
# time.sleep(10)
# os.system('clear')

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


# Questions that are asked during a single run to save and print
# performance record and statistics, and IDs of asked questions.
askedQuestions = []

winogradAsked = 0.
winograndeAsked = 0.
winogradRight = 0.
winograndeRight = 0.

# Main question answering function with branching for timeout/no timeout
def do_question(queryListIndex, doMore=True, timed=False):
    # Referencing main variables
    global winogradAsked
    global winograndeAsked
    global winogradRight
    global winograndeRight
    global askedQuestions

    # Questions are already in random order

    # Randomized order, so either
    # 1. CorSen
    # 2. InCorSen

    # or
    # 1. InCorSen
    # 2. CorSen
    questionDict = queryList[queryListIndex]

    # print(f"queryListIndex is {queryListIndex} and questionDict is {questionDict}")

    isWinograd = questionDict["source"] == "d"

    if isWinograd:
        winogradAsked += 1
    else:
        winograndeAsked += 1

    corSen = questionDict["CorSen"]
    inCorSen = questionDict["InCorSen"]

    corFirst = bool(random.getrandbits(1))

    if corFirst:
        print(f"1. {corSen} \n")
        print(f"2. {inCorSen} \n")
    else:
        print(f"1. {inCorSen} \n")
        print(f"2. {corSen} \n")

    # Timing starts after info taken from user and q/a printed,
    # but before branching into timed/untimed interfaces.
    timeStart = time.perf_counter()

    if timed:

        prompt = "You have %d seconds to choose the correct sentence:\n" % secondsToWait

        try:
            answer = input_with_timeout(prompt, secondsToWait)
        except TimeoutExpired:
            print('Sorry, times up')
            # Set answer to an always wrong answer
            answer = "0"
        else:
            print('Got %r' % answer)


    else:
        prompt = "enter answer: "
        answer = input(prompt)

    timeFinish = time.perf_counter()
    timeElapsed = timeFinish - timeStart

    correctNum = 1 if corFirst else 2
    answer = int(answer)
    correct = answer == correctNum

    if correct:
        # Increment correct
        if isWinograd:
            winogradRight+=1
        else:
            winograndeRight+=1
        #time.sleep(2)
    os.system('clear')

    # Record enough to reconstruct this question/answer event:
    # * time
    # * user answer
    # * correct answer -- NOPE since is in existing data structure
    # * question (just use existing data structure?)
    thisQuestion = {"questionDict":questionDict,"answer":answer,"correctNum":correctNum,"timeElapsed":timeElapsed}
    askedQuestions.append(thisQuestion)


    # 0 based indexing means after the length(list) - 1 question
    # has been asked we are done. There shouldn't be a 'Go again'
    # query.

    if queryListIndex == len(queryList) - 1:
        doMore = False
        printFinal()
        return doMore

    print("")
    answer = input("Go again?  ")
    if answer == "n":
        doMore = False
        printFinal()

    return doMore

def printFinal():
# Referencing main variables
    global winogradAsked
    global winograndeAsked
    global winogradRight
    global winograndeRight
    global askedQuestions

    #print(f"winogradAsked:{winogradAsked}\n"\
    #                       f"winograndeAsked:{winograndeAsked} \n"\
    #                       f"winogradRight:{winogradRight} \n"\
    #                       f"winograndeAsked:{winograndeAsked}")
    totalQuestionsRight = winogradRight + winograndeRight
    totalQuestionsAsked = winogradAsked + winograndeAsked


    percentCorrect = totalQuestionsRight/totalQuestionsAsked
    if winogradAsked == 0:
        percentGradCorrect = 1
    else:
        percentGradCorrect = winogradRight/winogradAsked
    if winograndeAsked == 0:
        percentGrandeCorrect = 1
    else:
        percentGrandeCorrect = winograndeRight/winograndeAsked

    goodbyeString1 = f"Thanks for playing!\nYour overall score was {percentCorrect}."
    goodbyeString2 = f"Your Winograd score was {percentGradCorrect}."
    goodbyeString3 = f"Your Winogrande score was {percentGrandeCorrect}."

    print(goodbyeString1)
    print(goodbyeString2)
    print(goodbyeString3)

    for q in askedQuestions:
        print(q)


idx = 0
doMore = True

while doMore:
    if idx < len(queryList):
        if timedTest:
            # print(idx)
            time.sleep(2)
            os.system("clear")
            doMore = do_question(idx, doMore, True)
            idx = idx+1
        else:
            time.sleep(2)
            os.system("clear")
            doMore = do_question(idx, doMore, False)
            idx = idx+1
