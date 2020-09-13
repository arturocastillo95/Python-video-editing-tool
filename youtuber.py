import pathlib
import os
import subprocess
import random
from shutil import rmtree
from pydub import AudioSegment

def fileTypeInPath(path, filetype):
	files = os.listdir(path)
	array = []
	for i in files:
		if i.endswith(filetype):
			array.append(i)
	return array

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def cutVideo(inputVideo, outputVideo, startT, endT):
	start = str(startT)
	end = str(endT)
	result = subprocess.run(["ffmpeg","-ss", start, "-i", inputVideo, "-to" , end, "-c", "copy", "-avoid_negative_ts","1", outputVideo])
	myPath = str(pathlib.Path(__file__).parent.absolute())
	return outputVideo

def randVideoPath(videoFolderPath, minLenght):
	vList = fileTypeInPath(videoFolderPath, ".mp4")
	leng = 0
	rand = 0
	video = ""
	while leng < minLenght:
		rand = random.randint(0, len(vList)-1)
		video = videoFolderPath + vList[rand]
		leng = get_length(video)
	return [video, leng]

def concatVideos(txtFilePath, outputName):
	result = subprocess.run(["ffmpeg","-f","concat","-safe","0","-i", txtFilePath, "-c", "copy", outputName])

def textVideoFile(videoList, outputPath):
	with open(outputPath, "w") as file:
		for i in videoList:
			line = "file "+ i +  "\n"
			file.write(line)

def videoCutDuration(totalRunTime, minLenght, maxLenght):
	chunks = []
	preRuntime = totalRunTime - maxLenght 
	while sum(chunks) < preRuntime:
		rand = randDouble(minLenght, maxLenght)
		chunks.append(rand)
	last = totalRunTime - sum(chunks)
	chunks.append(last)
	return chunks

def randDouble(minValue, maxValue):
	return round(random.uniform(minValue, maxValue), 2)

def addMusic(videoPath, musicPath, outputVideo):
	# result = subprocess.run(["ffmpeg", "-i", videoPath, "-i", musicPath, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", outputVideo])
	result = subprocess.run(["ffmpeg", "-i", videoPath, "-i", musicPath, "-map", "0:v", "-map", "1:a", "-c", "copy", outputVideo])
def createPath(s):
    try:  
        os.mkdir(s)
    except OSError:  
        assert False, "Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"
    return s

def deletePath(s): # Dangerous! Watch out!
    try:  
        rmtree(s,ignore_errors=False)
    except OSError:  
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

def overlaySequence(sequencePath, nameFormat, baseVideo, endTime, outputN):
	endT = str(endTime)
	time = endT + ") \'[out]"
	result = subprocess.run(["ffmpeg", "-i", baseVideo, "-framerate", "24", "-start_number","0", "-i", sequencePath + nameFormat,"-filter_complex","[0:v][1:v]overlay=enable=\'between(t,0.0," + time, "-map", "[out]", "-map", "0:a?", "-c:a", "copy", outputN])
	#result = subprocess.run(["ffmpeg", "-i", baseVideo, "-framerate", "24", "-start_number","0", "-i", sequencePath + nameFormat,"-filter_complex","[0:v]overlay=enable=\'between(t,0.0," + time, "-map", "[out]", "-map", "0:a?", "-c:a", "copy", outputN])

def deleteFiles(listofFiles):
	for i in listofFiles:
		os.remove(i)

def addSequence(inputVideo, sequencePath, sequenceNameFormat, sequenceLenght, startTime):
	concat = []
	inputVideoLenght = get_length(inputVideo)
	timeLenght = startTime + sequenceLenght

	if startTime != 0.0 and timeLenght != inputVideoLenght:
		#three chunks
		pass
	else:
		overlayChunk = cutVideo(inputVideo, "overlay.mp4", startTime, timeLenght)

		if startTime != 0.0:
			otherChunk = cutVideo(inputVideo, "part1.mp4", 0.00, startTime - 0.2)
			concat = [otherChunk, "overlayReady.mp4"]
		else:
			otherChunk = cutVideo(inputVideo, "part1.mp4", sequenceLenght + 0.2, inputVideoLenght)
			concat = ["overlayReady.mp4", otherChunk]

		overlaySequence(sequencePath, sequenceNameFormat, "overlay.mp4", inputVideoLenght, "overlayReady.mp4")
		textVideoFile(concat, "list.txt")
		os.remove(inputVideo)
		concatVideos("list.txt", inputVideo)
		deleteFiles([overlayChunk, otherChunk, "overlayReady.mp4", "list.txt"])

finalVideoName = input("Nombre del video final: ")

#Video Library path
myPath = str(pathlib.Path(__file__).parent.absolute())
videoLibraryPath = myPath + "/RESOURCES/VIDEOS/"
musicLibraryPath = myPath + "/RESOURCES/MUSIC/"

introPath = myPath + "/RESOURCES/INTRO_1/"
introNameFormat = "Comp1_%05d.png"
introLenght = get_length(introPath + "reference-MP4.mp4")

outroPath = myPath + "/RESOURCES/OUTRO_1/"
outroNameFormat = "End Screen 2_%05d.png"
outroLenght = get_length(outroPath + "EndScreen2-MP4.mp4")

musicFiles = fileTypeInPath(musicLibraryPath, ".mp3")
songPath = musicLibraryPath + musicFiles[random.randint(0, len(musicFiles) - 1)]
videoLen = get_length(songPath)

tempPath = createPath(myPath + "/TEMP") + "/"

arr = videoCutDuration(videoLen, 3.50, 11.00)
concatList = []

for i in arr:
 	vid = randVideoPath(videoLibraryPath, i)
 	name = i + random.randint(12, 230)
 	outputN = str(name) + ".mp4"
 	startTime = randDouble(0.0, vid[1] - i)
 	pathV = cutVideo(vid[0], tempPath + outputN, startTime, i)
 	concatList.append(pathV)

textVideoFile(concatList, tempPath + "concat.txt")
concatVideos(tempPath + "concat.txt", tempPath + "joined.mp4")

concatVideoLenght = get_length(tempPath + "joined.mp4")

#Add Outro
addSequence(tempPath + "joined.mp4", outroPath, outroNameFormat, outroLenght, concatVideoLenght - outroLenght)

#Add Intro
addSequence(tempPath + "joined.mp4", introPath, introNameFormat, introLenght, 0.0)


addMusic(tempPath + "joined.mp4", songPath, finalVideoName)
deletePath(myPath + "/TEMP")