

import praw
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging

# Not sure about these two. It is metrics though..
try:
    import moviepy.editor as mpy
except:
    logging.warning("Unable to import moviepy editor, karmaPlotstoGif() will not function")
    
from PIL import Image


from utils import archiveAndUpdateReddit
from utils import botHelperFunctions


'''  
Keith Murray 
email: kmurrayis@gmail.com
'''


def questionAndAnswer(query):
    '''
    Hopefully this will be the first implementation of "Soft Skills"
    Questions I want to answer
    How well does this bot work
    How does this bot work
    How useful has the bot been to users
    How much does this bot fail 
    '''

    return

def karmaPlot(date, karma, totalCommentKarma):
    dirName = "karma"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    
    color = ['red' if k < 0  else 'black' if k < 2 else 'blue' for k in karma]
    # Adjust x axis date display angle
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
    plt.gcf().autofmt_xdate()
    # Deal with weird x min/max bug (without, scale will be improperly set to +- ~ 2 months)
    # See:
    # https://github.com/matplotlib/matplotlib/issues/5963
    plt.xlim(xmin=min(date)-datetime.timedelta(days=1), xmax=max(date)+datetime.timedelta(days=1))
    # Actual thing we care about
    plt.scatter(date, karma, color=color) 
    curTime = datetime.datetime.utcnow()
    fname = str(curTime.strftime("%Y%m%d_%H%M"))
    prettyTime = curTime.strftime('%Y-%m-%d %H:%M')

    plt.title(prettyTime + " Comment Karma: " + str(totalCommentKarma))
    axes = plt.gca()
    # Try and remove y axis wiggle
    ymin, ymax = axes.get_ylim()
    ymag = max(abs(ymin), ymax)
    plt.ylim(ymin=-ymag, ymax=ymag) 
    #plt.show()
    plt.savefig(os.path.join(dirName, fname + '.png'), bbox_inches='tight')
    plt.close()

    
    fl = open(os.path.join(dirName, "totalKarmaByTime.txt"), 'a')
    fl.write(prettyTime + "\t" + str(totalCommentKarma)+'\n')
    fl.close()


    return

def totalKarmaLinePlot():
    # Load file
    dirName = "karma"    
    fl = open(os.path.join(dirName, "totalKarmaByTime.txt"), 'r')
    timeRange = []
    karmaCount = []
    for line in fl:
        line = line.strip()
        prettyTime, totalCommentKarma = line.split('\t')
        karmaCount.append(int(totalCommentKarma))
        timestamp = datetime.datetime.strptime(prettyTime, '%Y-%m-%d %H:%M')
        timeRange.append(timestamp)
    fl.close()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
    plt.gcf().autofmt_xdate()
    # Deal with weird x min/max bug (without, scale will be improperly set to +- ~ 2 months)
    # See:
    # https://github.com/matplotlib/matplotlib/issues/5963
    plt.xlim(xmin=min(timeRange)-datetime.timedelta(days=1), xmax=max(timeRange)+datetime.timedelta(days=1))
    # Actual thing we care about
    plt.plot(timeRange, karmaCount) 

    plt.show()
    plt.close()
    return


def performanceVisualization(reddit):
    # Only run once per unit time

    # Running
    user = archiveAndUpdateReddit.get_redditor_by_name(reddit, 'pythonHelperBot')
    totalCommentKarma = user.comment_karma
    date, karma = archiveAndUpdateReddit.makeCommentKarmaReport(user, reddit) 
    karmaPlot(date, karma, totalCommentKarma)
    return




def karmaPlotstoGif(outfileName="redditBotKarma.mp4", filePath = "karma"):


    # Temp dir to stage all adjusted sized images
    tempDirName = "temp"
    if not os.path.exists(tempDirName):
        os.makedirs(tempDirName)
    
    # Grab all files
    fileList = []
    if os.path.isfile(filePath):
        fileList.append(filePath)
    else:
        for dirname, dirnames, filenames in os.walk(filePath):
            for filename in filenames:
                fileList.append(os.path.join(dirname, filename))
    
    # sort only images by timestamp 
    fileList = sorted([x for x in fileList if x[-4:] == ".png"])

    # Get max width and heigth of images 
    for imgF in fileList:
        maxW = 0
        maxH = 0
        with Image.open(imgF) as img:
            width, height = img.size
            maxW = max(maxW, width)
            maxH = max(maxH, height)

    #
    tempL = []
    for  imgF in fileList:
        imgFName = os.path.basename(imgF)
        
        with Image.open(imgF) as img:
            im = img.resize((maxW, maxH), Image.ANTIALIAS)
            imPath = os.path.normpath(tempDirName+'/'+imgFName)
            im.save(imPath)
            tempL.append(imPath)


    if len(tempL) > 0:
        clip = mpy.ImageSequenceClip(tempL, fps=10)
        clip.write_videofile(outfileName, fps=10)
        print("Built Gif")

        
    print("Deleting temp files ")
    for fl in tempL:
        os.remove(os.path.normpath(fl))
        #print fl 

    return 
    


def measureUserReaction(post, user, suggestionTime):
    '''
    For every user u/pythonHelperBot has interacted with,
    Check to see if they posted in r/learnpython a certain time 
    after their post (some function of next batch of user activity)


    '''
    limitCount = 10
    learningSubs = botHelperFunctions.get_learning_sub_Names()
    submissionList = archiveAndUpdateReddit.getUserPosts(user, limitCount=limitCount)
    tookAdvice = False
    for submission in submissionList:
        if str(submission.subreddit).lower() in learningSubs:
            post_Time = datetime.datetime.utcfromtimestamp(submission.created_utc)
            if post_Time - suggestionTime > 0:
                # Here you could check to see if the posts are similar, but we'll ignore that
                # On the assumption that the bot is useful if it encourages users to ask
                # future questions in the correct sub. And that question 1 might have already 
                # been answered, but there might be a followup question incoming.
                tookAdvice = True

    

    return tookAdvice


