from queue import Queue 
from threading import Thread
import urllib, os

urlopen = urllib.FancyURLopener()
base_url = "http://podcast-media.ucsd.edu/Podcasts/"
classnames= [
				"CSE120-Operating Systems-sp15",
				"CSE190-Data Mining-sp15",
				"CSE291-Neural Networks-sp15",
				"CSE190-Data Mining-fa15",
				"CSE190-Robotics-sp16",
				"CSE190-Neural Networks-fa16",
				"CSE103-Probability-fa16",
				"CSE258-Recommender Systems-wi17",
				"CSE158-Recommender System-wi17"
			]

classes = 	[ 
				["sp15/cse120sp15/cse120sp15", "1830"],
				["sp15/cse1901sp15/cse1901sp15", "1830"],
				["sp15/cse2911sp15/cse2911sp15","1400"],
				["fa15/cse190fa15/cse190fa15","1700"],
				["sp16/cse190sp16/cse190sp16","1100"],
				["fa16/cse190fa16/cse190fa16", "0800"],
				["fa16/cse103fa16/cse103fa16","2000"],
				["wi17/cse258_wi17/cse258_wi17","1830"],
				["wi17/cse158_wi17/cse158_wi17","1700"]
			]

startdates=	[
				(3,31,2015,"TuTh"),
				(3,31,2015,"TuTh"),
				(3,31,2015,"TuTh"),
				(9,28,2015,"MW"),
				(3,28,2016,"MWF"),
				(9,20,2016,"TuTh"),
				(9,26,2016,"MW"),
				(1,9,2017,"MW"),
				(1,9,2017,"MW")
			]

class UrlDownloader(Thread):
	def __init__(self, myqueue):
		Thread.__init__(self)
		self.myqueue = myqueue

	def run(self):
		while self.myqueue:
			classnameurl, url,savefilename = self.myqueue.get()
			try:
				urltest = urllib.urlopen(url)
				if urltest.getcode() == 200:
					urlopen.retrieve(url,savefilename)
					print classnameurl, "\t---> ",savefilename.rsplit("/",1)[-1],"  COMPLETE"
				else:
					print classnameurl, "\t---> ",savefilename.rsplit("/",1)[-1]," INVALID"
			except:
				print classnameurl, "\t---> ",savefilename.rsplit("/",1)[-1], "  FAILED"
			self.myqueue.task_done()

def getGenerativeDates(*args):
	startmonth,startdate,startyear,occurance = args
	classes = len(occurance)
	if occurance[0] != "M": classes /= 2

	currdate = startdate
	currmonth = startmonth
	curryear = startyear
	week = 1
	fstr = (lambda x: "{0:0>2}".format(x))
	resultdates = []

	def nextdate(currdate,currmonth,curryear,offset=2):
		months30days = set([9,4,6,11])
		if currmonth in months30days: montype = 30 
		elif curryear == 2016 and currmonth == 2: montype = 29
		elif currmonth == 2: montype = 28
		else: montype = 31
		if currdate + offset > montype:
			if currmonth == 12: 
				curryear += 1
				currmonth = 1
			else:
				currmonth += 1
			currdate = (currdate + offset) - montype
		else:
			currdate += offset
		return (currdate,currmonth,curryear)


	while week <= 10:
		weeklist = []
		for day_occurance in range(classes):
			weeklist.append(fstr(currmonth)+fstr(currdate)+str(curryear))
			daysoffset = 2
			if day_occurance == classes-1:
				if occurance[-1] == "F": daysoffset = 3
				else: daysoffset = 5
			currdate, currmonth, curryear = nextdate(currdate,currmonth,curryear,daysoffset)
		
		week += 1
		resultdates.append(weeklist)
		
	return resultdates


def classfetcher(myqueue):
	for idx,(classbaseurl,secnum) in enumerate(classes):
		if not os.path.exists(classnames[idx]):
			os.makedirs(classnames[idx])

		for weekdates in getGenerativeDates(*startdates[idx]):
			for date in weekdates:
				url = base_url + classbaseurl + "-{0}-{1}.mp4".format(date,secnum)
				savefilename = "./{0}/{1}-{2}-{3}.mp4".format(classnames[idx],date[:2],\
					date[2:4],date[4:])
				myqueue.put((classnames[idx],url,savefilename))
				

myqueue = Queue()
for numthreads in xrange(10):
	urldownloader = UrlDownloader(myqueue)
	urldownloader.daemon = True
	urldownloader.start()

classfetcher(myqueue)

myqueue.join()
print "Exited safely"
		