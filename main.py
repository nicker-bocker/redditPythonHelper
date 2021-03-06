import praw
import nltk
import datetime
import time
import os
import argparse, textwrap
# Logging Info
import logging
import traceback

from utils import archiveAndUpdateReddit
from utils import botHelperFunctions 
from utils import botMetrics
from utils import botSummons
from utils import buildComment
from utils import formatCode
from utils import learningSubmissionClassifiers
from utils import locateDB
from utils import questionIdentifier
from utils import searchStackOverflowWeb
from utils import summarizeText
from utils import textSupervision
from asecretplace import getPythonHelperBotKeys
  

'''  
Keith Murray 
email: kmurrayis@gmail.com


This bot is powered by coffee and the WestWorld Soundtrack. 

act = "JUST CODE IT"
print(act[:5]+ act[6:8][::-1]+act[9:])
'''

"""
def idealQuery(title, questions, keywords, tdm):
    # Using NLP Magic (yet to be determined): identify best keywords 
    #   to search stack overflow with
    text = title 
    text += ' '.join(questions) 
    text += '\n' + ' '.join(keywords)
    try:
        summary = summarizeText.summarizeDoc_SentToDoc(text, tdm, topSentCount=1)
    except Exception as e:
        print(e)
        logging.error(e)
        summary = ' '.join(keywords)
    logging.debug( '\t' + summary)
    query = 'python ' + summary
    return query

def stackOverflowInfo(title, text, questions, tdm):
    # Extract keywords for SO search
    postText = summarizeText.detokenize( title + text)

    key_phrase_set = summarizeText.wordRankKeywords(postText)
    if len(key_phrase_set) > 5:
        key_phrase_set = key_phrase_set[:5]

    x = ' '.join(key_phrase_set)
    
    # Best Query is max ()
    # PENDING IMPLEMENTATION, NOT YET READY

    query = idealQuery(title, questions, key_phrase_set, tdm)
    # Search SO
    try:
        searchResults = searchStackOverflowWeb.search_stackoverflow(query)
    except:
        # It's a bodge, but this block of code is slated to be changed soon anyway. 
        searchResults=[None]

    # Review results

    # If results are good, build SO Answer to msg
    result_msg = ""
    resultScore = []
    #resultTitle
    # BODGE
    '''
    Traceback (most recent call last):
  File "main.py", line 321, in <module>
    runBot(reddit, classifier, tdm, userNames, postHistory)
  File "main.py", line 294, in runBot
    buildHelpfulComment(submission, user, question_Set, classifier, tdm, reddit)
  File "main.py", line 106, in buildHelpfulComment
    key_phrases, so_msg, search_results = stackOverflowInfo(title, text, question_Set, tdm)
  File "main.py", line 72, in stackOverflowInfo
    if len(searchResults[0])> 0:
TypeError: object of type 'NoneType' has no len()
    '''
    if searchResults[0] is not None: 
        if len(searchResults[0])> 0:
            i = 1
            for key in searchResults[0]:
                result_msg += '\n' + str(i) + '. [' + key['Title'] + '](' + key['URL'] + ')'
                if i >= 3:
                    break
                i += 1


    msgIntro = "\n\nWhile I was at it, I checked [Stack Overflow](https://stackoverflow.com/) "

    msg = msgIntro

    if len(result_msg) > 0: 
        msg += "and found these results which might be useful:\n" + result_msg
    else:
        msg += "but I couldn't find a useful result"

    msgNotWorkingProperly = "\n\nThough fair warning, this section of the my code is under development, and I don't expect these links to be very useful."
    msg += msgNotWorkingProperly

    return key_phrase_set, msg, searchResults
"""
def buildHelpfulComment_DEPRECATED(submission, user, question_Set, classifier, tdm, reddit, suggested, crossPosted, quietMode):
    supervised = False
    underDev = True

    msgBagOfSents = []
    if suggested:
        msg = buildComment.alreadySuggestedComment()
        msgBagOfSents.append(buildComment.alreadySuggestedComment())
    #elif crossPosted:
     #   msg = UserCrossPosted()
    else:
        msg = buildComment.baseComment()
        msgBagOfSents.append()

    if supervised:
        msg = msg+buildComment.supervisedComment()
        msgBagOfSents.append(buildComment.supervisedComment())
        #print(title)
        #print(text)
        #print(submission.url)
        cleanURL = botHelperFunctions.shortenRedditURL(submission.url)
        sms_msg = "Is this post worth commenting on?\n" + cleanURL 
        reply = textSupervision.getUserFeedbackViaText(outgoingMsg=sms_msg).strip()
        #input_str = raw_input("Is this post worth commenting on?")
        if reply.lower() in ['y', 'yes']:
            #print("COOL BRO")
            #print("Keywords found: ", key_phrases, '\nSearch Result Size')
            #print(len(search_results[0]))
            #print('\tCommenting...')
            pass
        else:
            #print("Aw Damnit.")
            return
    # Sign the message
    msg += buildComment.signatureComment() 
    msgBagOfSents.append(buildComment.signatureComment() )
    # Say it's changing
    if underDev:
        msg += buildComment.inDevelopmentComment()
        msgBagOfSents.append(buildComment.inDevelopmentComment())
    logging.debug(msg)
    # Quiet Mode is used to debug, and avoid
    if not quietMode:
        archiveAndUpdateReddit.commentOnSubmmission(submission, msg, reddit, quietMode)
        archiveAndUpdateReddit.updateDatabase(user.name, submission.id)
        logging.debug( '\t\tCommented.')
    else:
        logging.debug("Quiet Mode is on, no actual post was made")
    

    return


def buildHelpfulComment(submission, user, reddit, suggested, crossPosted, answered, codePresent, correctlyFormatted, quietMode):
    supervised = False
    underDev = True
    
    bagOfSents = []
    # Intro
    bagOfSents.append(buildComment.botIntro())

    # User Sittuation Context Awareness
    if crossPosted:
        bagOfSents.append(buildComment.userCrossPosted())
    elif answered:
        bagOfSents.append(buildComment.alreadyAnsweredComment())
    elif suggested:
        bagOfSents.append(buildComment.alreadySuggestedComment())
    else:
        bagOfSents.append(buildComment.standardIntro())

    # Follow rules and help make code clear
    bagOfSents.append(buildComment.followSubRules())
    logging.info("Code Present: " + str(codePresent) + " | Correctly Formatted: " + str(correctlyFormatted))
    if not (codePresent and correctlyFormatted):
        # They've either not shown code or not shown
        #  well formatted code, we should suggest formatting
        bagOfSents.append(buildComment.formatCodeAndOS())

    # Another good location is the discord
    bagOfSents.append(buildComment.discord())

    if supervised:
        logging.debug("Asking about post")
        bagOfSents.append(buildComment.supervisedComment())
        cleanURL = botHelperFunctions.shortenRedditURL(submission.url)
        sms_msg = "Is this post worth commenting on?\n" + cleanURL 
        reply = textSupervision.getUserFeedbackViaText(outgoingMsg=sms_msg).strip()
        if reply.lower() not in ['y', 'yes']:  
            logging.debug("Told not to comment")          
            return
        logging.debug("Told to comment")
    
    # Sign the message
    bagOfSents.append(buildComment.signatureComment() )
    # Say it's changing
    if underDev:
        bagOfSents.append(buildComment.inDevelopmentComment())


    msg = '\n'.join(bagOfSents)    
    logging.debug(msg)
    # Quiet Mode is used to debug, and avoid
    if not quietMode:
        archiveAndUpdateReddit.commentOnSubmmission(submission, msg, reddit, quietMode)
        archiveAndUpdateReddit.updateDatabase(user.name, submission.id)
        logging.debug( '\t\tCommented.')
    else:
        logging.debug("Quiet Mode is on, no actual post was made")
    

    return


    
def xrequest_Key_Word_Filter(submission, phrase_set):
    '''
    This is a hand made feature set to id titles that make reddit-typical 
    requests for help, but might not phrase the request as a question

    '''

    # Consider adding a time delay here?
    
    text = ' '.join(summarizeText.parseStringSimple01(submission.title))
    # Pass phrase_set through string parser and back, it'll help? 
    #phrase_set = botHelperFunctions.load_autoreply_key_phrases(fl_path='misc/autoreplyKeyPhrases.txt')
    '''
    phrase_set = ['need help', '[help]', '[ help ]', '[question]', 
                    '[ question ]', 'noob ', 'n00b ', ' newb','please help', 
                    'noobie question', 'help!', 'help me', "isn't working",
                    'not working', 'issues with', 'issue with',
                    'looking for tutorial', 'Quick question', 'help needed',
                    'plz help', "what's wrong", "need some help", '[q]',
                    '[Beginner Question]']
    '''
    request_Made = False
    #print text
    for phrase in phrase_set:
        if ' '.join(summarizeText.parseStringSimple01(phrase)).lower() in text:
            logging.info(phrase + " Was used in the post title")
            request_Made = True
            break

    if request_Made:
        text = summarizeText.parseStringSimple01(submission.selftext)
        sents = nltk.sent_tokenize(' '.join(text))
        # Returning the last sentence is chosen purely based on a guess
        # It'll be more useful to select sents based on idf and entropy score
        try:
            return sents[-1]
        except:
            logging.info("Failed to grab last sentence: Probably links offsite")
            pass

    
    return False


def xbasicQuestionClassify(submission, user, classifier, tdm):
    """
    A really simple classifier. if a submission is old enough, has low enough votes
    and asks a question, it's treated as a basic question that r/learnpython is 
    better suited for.
    Parameters
    ----------
    submission : praw submission object
    user : praw user object
    classifier : nltk classifier object
    tdm : term document matrix object
    Returns
    -------
     
    Notes
    -----
    It's not what I want, but it'll force me to
    References
    ----------
    Examples
    --------
    """
    #title = summarizeText.parseStringSimple01(submission.title)
    #text = summarizeText.parseStringSimple01(submission.selftext)
    #postText = title + text

    postAge = datetime.datetime.utcnow() - submission.created_utc
    hours2 = datetime.timedelta(hours=2)
    logging.debug(  '\t'+"Post Age: "+ str(postAge) )

    votes = submission.score 
    upvoteRatio = submission.upvote_ratio 


    #print title
    logging.debug(  '\t'+ "Votes: "+ str(votes))
    logging.debug(  '\t'+ "Upvote Ratio: "+str( upvoteRatio))

    if postAge < hours2:
        return False

    if votes > 0:
        return False

    if upvoteRatio > 0.41:
        return False

    if submission.id not in submission.url:
        # Links off site 
        logging.debug(  '\t'+'Results: Error. Classification is dead,  (URL) Mismatch. ')
        return False



    # ID if a question is here right now
    title = summarizeText.parseStringSimple01(submission.title, removeURL=True)
    text = summarizeText.parseStringSimple01(submission.selftext, removeURL=True)
    postText = title + text
    sents = nltk.sent_tokenize(' '.join(postText))# nltk.sent_tokenize(title) + nltk.sent_tokenize(text)
    #print " ".join(sents)
    question_Sents = []
    for sent in sents:
        sentDisplay = ' '.join(sent.strip().split('\n'))
        #print '\t', sentDisplay.strip()
        classified = questionIdentifier.classifyString(sent, classifier)
        #print classified
        if "question" in classified.lower():
            question_Sents.append(sent)
            logging.debug(str(classified) +': '+ str(sent))
            print('\tSentence: ', sent)
            print('\tClassified As: ', classified)
        #print '\t', classified
    if len(question_Sents) > 0:
        logging.info('|'.join(question_Sents))
        return question_Sents
    logging.debug("\tNo Question Identified")



    
    # All else
    return False 

def checkForLearnPythonSuggestion(reddit, submission):
    # This is to check and see if learn python has been suggested 
    topComments = submission.get_top_level_comments(reddit)
    suggestedTime = -1
    for comment in topComments:
        text = comment.body
        #words = text.split()
        if 'learnpython' in text:
            logging.debug("Someone has already Suggested r/learnpython")
            suggestedTime = comment.created_utc
            return True, suggestedTime

    return False, suggestedTime


def checkForAlreadyAnswered(reddit, user, submission):
    '''
    Soft Skill extension
    'Wow thank you so much!'
    'I think I get it'
    'Thanks a lot for pointing that out! I actually oversaw that on the site but now i'm working on getting it running'
    '''

    return False

def xgetSubsUsersInteractsIn(reddit, user, limitCount=25):
    '''
    Effectively a very basic funtion. However, because of the use-case
    it has an added flag to show whether or not the user has previously
    suggested the learnpython sub. 

    This whole function will probably be deleted at a later date for
    more optimized functions including:

    check whether or not user has suggested learnpython before
    check whether or not it has been suggested to them before
    check whether they use any learn programming related subs
    check whether the user makes duplicate posts
    check whether the user posts blog spam

    This incarnation is useful, but it burns api calls for very little 
    gains. 

    
 /r/cpp_questions
 /r/javahelp
 /r/LearnJavaScript
 /r/learnpython
 /r/learnmachinelearning
 /r/MLQuestions
 /r/learnprogramming
    '''
    learning_Subs = botHelperFunctions.get_learning_sub_Names()
    postsInLearningSubs = []
    redditSubs = {}
    submissionList = user.getUserPosts(reddit, limitCount)
    commentList = user.getUsersComments(reddit, limitCount)
    hasSuggestedLearnPython = False


    for submission in submissionList:
        if str(submission.subreddit ) in redditSubs:
            redditSubs[str(submission.subreddit )] += 1
        else:
            redditSubs[str(submission.subreddit )] = 1
        if str(submission.subreddit ).lower() in learning_Subs:
            postsInLearningSubs.append(submission)
        
    for comment in commentList:
        if 'learnpython' in comment.body.lower():
            hasSuggestedLearnPython = True
        if str(comment.subreddit ) in redditSubs:
            redditSubs[str(comment.subreddit )] += 1
        else:
            redditSubs[str(comment.subreddit )] = 1
        
    return redditSubs, hasSuggestedLearnPython, postsInLearningSubs
    
def xbasicUserClassify(reddit, user, userNames, submission, suggestedTime, antiSpamList):
    
    # Need to classify a user here
    # Only post if 
    DayLimit = 700
    timeDelt = datetime.timedelta(days=DayLimit)
    accountAge = datetime.datetime.utcnow() - user.created_utc

    antiSpamList = xpopOldSpammers(antiSpamList, ageLimitHours=12) # Should stop growing dict memory leak

        
    # Don't bother commenting if I've talked to the user before
    if str(user.name) in userNames:
        logging.info( "\tI've already commented on a post by "+ str(user.name) )
        msg = "\tI've already commented on a post by " + str(user.name) 
        print(msg)
        if submission.id not in antiSpamList:
            antiSpamList[submission.id] = submission.created_utc
            msg = msg.strip() + "\n\nPost in Question: "+ botHelperFunctions.shortenRedditURL(submission.url)
            textSupervision.send_update(msg)
        return False, [], antiSpamList


    if accountAge > timeDelt:
        logging.debug('\t'+ str(user.name))
        # User is old enough to know better
        # This is emperically false but I need some limits
        # Actually in practice the bot nearly never comments because of this
        logging.debug( str( accountAge) + " User Should Know Better, They're old enough")
        #print  '\t', "USER SHOULD KNOW BETTER"
        #return False, []


    subs, directedOthersToLearn, postsInLearningSubs = xgetSubsUsersInteractsIn(reddit, user)
    if 'learnpython' in subs:
        # Probably should check if user has posted in the sub more recently than current post
        logging.info("User " + str(user.name) + " has posted in r/learnpython before")


    if directedOthersToLearn:
        logging.info("User " + str(user.name) + " has directed others to r/learnpython")
        return False, [], antiSpamList

    return True, postsInLearningSubs, antiSpamList


def xuser_Already_Took_Advice(submission, postsInLearningSubs, suggestedTime):
    '''
    See whether or not user has posted in learning subs, and distinguish between
    following advice vs just posting in multiple places vs posting in learning 
    subs some time after vs unrelated

    
    Notes
    -----
    This is a bit messy
    The bot balances two users: the average r/python redditor (AR), and the user posting
    the question, OP (original poster).
    To the AR, it doesn't matter that the OP has already posted in the correct sub, it 
    matters that the r/python sub has OP's post. 
    To the OP, it doesn't matter where they post, they want an answer. 
    The Guiding principle is be helpful and don't spam. 
    Considering OP, if they were informed to try somewhere else, and they did, they 
    don't need to be told to do what has already been done. 
    If OP has cross posted as a 'see what sticks' method, they do need to be told to 
    not post here but post similar queries to learning subs. 

    If the bot takes on mod like roles (flagging posts for mod review) then the AR 
    should be the bots first focus. 
    Otherwise
    The bot should care about OP, and try to help. If the bots actions don't add value, 
    the bot should remain inactive. 

    It would be nice to acknowledge if the user has cross posted, but I'm not sure if that 
    would make 
    
    
    '''
    tookAdvice = False
    crossPosted = False
    askedLearningLater = False
    if len(postsInLearningSubs) > 0:
        pythonPostTime = submission.created_utc
        for post in postsInLearningSubs:
            learningPostTime = post.created_utc
            if suggestedTime  != -1:
                if learningPostTime - suggestedTime >  datetime.timedelta(seconds=0):
                    tookAdvice = True
                    logging.info("User took Advice")
            else:
                if abs(learningPostTime - pythonPostTime) < datetime.timedelta(seconds=30*60):
                    crossPosted = True
                    logging.info("User Cross Posted")
                elif learningPostTime- pythonPostTime  > datetime.timedelta(seconds=30*60):
                    askedLearningLater = True
                    
                    logging.info("User posted in learning Sub after a while ")


    return tookAdvice, crossPosted, askedLearningLater


def xpopOldSpammers(antiSpamList, ageLimitHours):
    # This is a bodge because it's late
    ageLimit = datetime.timedelta(hours=ageLimitHours)
    oldKeys = []
    for key in antiSpamList:
        age = datetime.datetime.utcnow() - antiSpamList[key]
        if age > ageLimit:
            oldKeys.append(key)
    for key in oldKeys:
        if key in antiSpamList:
            del antiSpamList[key]

    return antiSpamList


            

def checkForSummons(msg):
    summonID = None
    if msg.subject.strip() == "username mention":
        if (msg.body.strip() == 'u/pythonHelperBot !reformat') or (msg.body.strip() == '/u/pythonHelperBot !reformat'):
            print("SUMMONS")
            print(msg.id)
            summonID = msg.id
        print(msg.body)
    
    return summonID



def check_for_key_phrase(submission, phrase_set):
    botHelperFunctions.logPostFeatures(submission)
    request_Made = learningSubmissionClassifiers.request_Key_Word_Classifier(submission, phrase_set)
    return request_Made

def lookForKeyPhrasePosts(reddit, setOfPosts, phrase_set):

    oldPosts = setOfPosts.copy() # https://stackoverflow.com/questions/5861498/
    setOfPosts = archiveAndUpdateReddit.getNewPosts(reddit, submissionList=setOfPosts)
    submissionsToCommentOn_KP = []
    for key in setOfPosts:
        if key not in oldPosts:
            submission, user = setOfPosts[key]
            request_Made = check_for_key_phrase(submission, phrase_set)
            if request_Made:
                submissionsToCommentOn_KP.append(key)

    return setOfPosts, submissionsToCommentOn_KP



def basicQuestion_classifyPost(submission, classifier):
    botHelperFunctions.logPostFeatures(submission)
    question_Sents = learningSubmissionClassifiers.basicQuestionClassify(submission, classifier)
    return question_Sents

def handleSetOfSubmissions(reddit, setOfPosts, postHistory, classifier):

    submissionsToCommentOn_BC = []
    for key in setOfPosts:
        if key not in postHistory:
            submission, user = setOfPosts[key]
            question_Sents = basicQuestion_classifyPost(submission, classifier)
            if question_Sents:
                submissionsToCommentOn_BC.append(key)
    return submissionsToCommentOn_BC


def getReadyToComment(reddit, setOfPosts, userNames, postHistory, commentOnThese, antiSpamList, codeVTextClassifier, quietMode):

    # Remove Duplicates as a precaution
    #commentOnThese = list(set(commentOnThese))

    for key in setOfPosts:
        if key in commentOnThese:
            if key not in postHistory:
                submission, user = setOfPosts[key]
                logging.debug("Processing a valid post")
                botHelperFunctions.logPostFeatures(submission)
                suggested, suggestedTime = checkForLearnPythonSuggestion(reddit, submission)
                user_status, postsInLearningSubs, antiSpamList = learningSubmissionClassifiers.basicUserClassify(reddit, user, userNames, submission, suggestedTime, antiSpamList) 
                if user_status:
                    logging.debug(  '\t'+ "User is valid")
                    tookAdvice = False
                    crossPosted = False
                    askedLearningLater = False
                    if len(postsInLearningSubs) > 0:
                        tookAdvice, crossPosted, askedLearningLater = botHelperFunctions.user_Already_Took_Advice(submission, postsInLearningSubs, suggestedTime)
                        
                    if not tookAdvice and not askedLearningLater:
                        # Shutup if already directed, and user listened
                        answered=False
                        codePresent=False
                        correctlyFormatted=False
                        msg, changesMade, codePresent, correctlyFormatted = formatCode.reformat(submission.selftext, codeVTextClassifier)

                        buildHelpfulComment(submission, user, reddit, suggested, crossPosted, answered, codePresent, correctlyFormatted, quietMode)
                        userNames.append(str(user.name))
                        postHistory.append(str(submission.id))


    return userNames, postHistory, antiSpamList



def startupBot():
    print("Loading bot")
    logging.debug("Loading Bot")


    paths = locateDB.get_db_file_locations()
    #print "File Path Keys: ", paths.keys()
    #print paths
    # Make some form of error check for the path variable 
    #assert paths[enlishDB] is not False

    # Load Term-Doc Matrix Datastructure
    tdm = summarizeText.buildModelFromDocsInFolder(sourceDataPath=paths["englishDB"])
    # NLTK classifier (Statement, YNQuestion, WHQuestion, etc)
    classifier = questionIdentifier.buildClassifier02NLTKChat()
    # Code vs Text classifier 
    codeVTextClassifier = formatCode.buildTextCodeClassifier(sourceDataPath=paths["codeText"])

    # Reddit API 
    keySet = getPythonHelperBotKeys.GETREDDIT()
    #assert 1 == 2
    reddit = praw.Reddit(client_id=keySet[0], client_secret=keySet[1], 
                     password=keySet[2], user_agent=keySet[3],
                    username=keySet[4])

    # Py SQL Database 
    userNames, postHistory = archiveAndUpdateReddit.startupDatabase()
    # Ignore all mod posts: they know what they're doing
    for mod in reddit.subreddit('python').moderator():
        userNames.append(str(mod))
    

    logging.debug( "Loaded. Running...")
    return reddit, classifier, codeVTextClassifier, tdm, userNames, postHistory


def xrunBotX(reddit, classifier, codeVTextClassifier, tdm, userNames, postHistory, quietMode=False):
    
    phrase_set = botHelperFunctions.load_autoreply_key_phrases(fl_path='misc/autoreplyKeyPhrases.txt')
    
    setOfPosts = archiveAndUpdateReddit.grabAndUpdateNewPosts(reddit)
    unreadCount = botSummons.handleInbox(reddit, codeVTextClassifier, quietMode=quietMode)
    antiSpamList = {} # Used in basicUserClassify to only text me once per submission by a repeat user
    while True:
        for key in setOfPosts:
            submission, user = setOfPosts[key]
            if str(submission.id) not in postHistory:
                logging.debug( '*'*50)
                logging.debug('[POST]   | ' + str(submission.title.encode('ascii', 'ignore')))
                logging.debug('[AUTHOR] | ' + str(user.name))
                logging.debug('[ID]     | ' + str(submission.id))
                question_Set = xbasicQuestionClassify(submission, user, classifier, tdm)
                request_Made = xrequest_Key_Word_Filter(submission, phrase_set)
                if question_Set or request_Made:
                    # BODGE
                    if request_Made and not question_Set:
                        question_Set = request_Made 
                    
                    logging.debug(  '\t'+ "Found a valid post")
                    suggested, suggestedTime = checkForLearnPythonSuggestion(reddit, submission)
                    user_status, postsInLearningSubs, antiSpamList = xbasicUserClassify(reddit, user, userNames, submission, suggestedTime, antiSpamList) 
                    if user_status:
                        logging.debug(  '\t'+ "User is valid")

                        if len(postsInLearningSubs) > 0:
                            tookAdvice, crossPosted, askedLearningLater = xuser_Already_Took_Advice(submission, postsInLearningSubs, suggestedTime)
                        else: 
                            tookAdvice = False
                            crossPosted = False
                            askedLearningLater = False

                        # Check to see if user has already posted to LP

                        if not tookAdvice and not askedLearningLater:
                            # Shutup if already directed, and user listened
                            answered=False
                            codePresent=False
                            correctlyFormatted=False
                            buildHelpfulComment(submission, user, reddit, suggested, crossPosted, answered, codePresent, correctlyFormatted, quietMode)
                            userNames.append(str(user.name))
                            postHistory.append(str(submission.id))
                            #pass

        botMetrics.performanceVisualization(reddit)
        unreadCount = botSummons.handleInbox(reddit, codeVTextClassifier, unreadCount=unreadCount, sendText= True, quietMode=quietMode)
        logging.debug( "Sleeping..." + str(datetime.datetime.now()))
        time.sleep(15*60)
        setOfPosts = archiveAndUpdateReddit.grabAndUpdateNewPosts(reddit, submissionList=setOfPosts)





def runBot(reddit, classifier, codeVTextClassifier, tdm, userNames, postHistory, quietMode=False):
    
    phrase_set = botHelperFunctions.load_autoreply_key_phrases(fl_path='misc/autoreplyKeyPhrases.txt')
    
    setOfPosts = archiveAndUpdateReddit.grabAndUpdateNewPosts(reddit)
    unreadCount = botSummons.handleInbox(reddit, codeVTextClassifier, quietMode=quietMode)
    antiSpamList = {} # Used in basicUserClassify to only text me once per submission by a repeat user

  
    threeMin = 3
    lastThreeMin = datetime.datetime.now() - datetime.timedelta(seconds=threeMin*60)
    fifteenMin = 15
    lastFifteenMin = datetime.datetime.now() - datetime.timedelta(seconds=fifteenMin*60)

    while True:
        commentOnThese = [] 
        if datetime.datetime.now() - lastThreeMin > datetime.timedelta(seconds=threeMin*60):
            #print("3 mins")
            # Handle Inbox
            unreadCount = botSummons.handleInbox(reddit, codeVTextClassifier, unreadCount=unreadCount, sendText= True, quietMode=quietMode)

            # Get new posts, respond to keywords
            setOfPosts, submissionsToCommentOn = lookForKeyPhrasePosts(reddit, setOfPosts, phrase_set)
            commentOnThese += submissionsToCommentOn

            lastThreeMin = datetime.datetime.now()
            logging.debug( "3 minute region is Sleeping..." + str(datetime.datetime.now()))

        if datetime.datetime.now() - lastFifteenMin > datetime.timedelta(seconds=fifteenMin*60):
            #print("15 mins")
            # Update posts
            setOfPosts = archiveAndUpdateReddit.updatePosts(reddit, submissionList=setOfPosts) 

            # reclassify posts
            commentOnThese += handleSetOfSubmissions(reddit, setOfPosts, postHistory, classifier)

            # Performance Visualizations 
            botMetrics.performanceVisualization(reddit)
            lastFifteenMin = datetime.datetime.now()
            logging.debug( "15 minute region is Sleeping..." + str(datetime.datetime.now()))


        # Comment on all classified submissions
        userNames, postHistory, antiSpamList =  getReadyToComment(reddit, setOfPosts, userNames, postHistory, commentOnThese, antiSpamList, codeVTextClassifier, quietMode)

        time.sleep(30)




def interface():
    args = argparse.ArgumentParser(
        prog='main.py', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='A reddit bot to help direct new users to r/learnpython',
        epilog=textwrap.dedent('''\
            To run the bot without the risk of commenting, run quiet mode.
        '''))
    args.add_argument('-q', '--quiet-mode', type=bool, default=False,\
                      help='[True/False] Run the program without posting to reddit or texting')
    args = args.parse_args()
    return args


# https://i.imgur.com/vHRUkak.gif Mos Fire
# https://i.imgur.com/3i8EM9Q.jpg Kiss and wave
# https://i.imgur.com/9RnHTMs.mp4 Woody entrance 





if __name__ == "__main__":
    args = interface()
    quietMode = args.quiet_mode
    if quietMode:
        # Fair assumption that the user is watching the terminal during quiet mode
        print("Bot is Running in Quite Mode")
    # Logging Stuff
    dirName = "logs"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    logFileName =   'LOG_'+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
    filePath = os.path.join(dirName, logFileName) 
    logging.basicConfig(filename=filePath, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s():%(lineno)s - %(message)s')
    if quietMode:
        logging.debug("Running in Quiet Mode")

    reddit, classifier, codeVTextClassifier, tdm, userNames, postHistory = startupBot()
    try:
        runBot(reddit, classifier, codeVTextClassifier, tdm, userNames, postHistory, quietMode=quietMode)
    except KeyboardInterrupt:
        print("Concluding Program")
        logging.debug("Keyboard Interrupt: Ending Program")
    except:
        logging.error("\n"+traceback.format_exc())
        fl = open("ERRORLOG.log", 'a')
        fl.write("\n"+"*"*50+"\n"+traceback.format_exc())
        fl.close()
        print(traceback.format_exc())
        trc = traceback.format_exc().strip().split("\n")[-1]
        msg = "Program exited on Error:\n"+str(trc)
        if len(msg) > 133:
            msg = msg[:130] + '...'
            print(msg)
        print(msg)
        if not quietMode:
            textSupervision.send_update(msg)

    


