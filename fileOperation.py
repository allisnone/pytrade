import os 
import os.path 
import shutil 
import time,datetime

def copyFiles(sourceDir,  targetDir): 
    if sourceDir.find(".svn") > 0: 
        return 
    for file in os.listdir(sourceDir): 
        sourceFile = os.path.join(sourceDir,  file) 
        targetFile = os.path.join(targetDir,  file) 
        if os.path.isfile(sourceFile): 
            if not os.path.exists(targetDir):  
                os.makedirs(targetDir)  
            if not os.path.exists(targetFile) or(os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):  
                    open(targetFile, "wb").write(open(sourceFile, "rb").read()) 
        if os.path.isdir(sourceFile): 
            First_Directory = False 
            copyFiles(sourceFile, targetFile)
            
def coverFiles(sourceDir,  targetDir): 
    for file in os.listdir(sourceDir): 
        sourceFile = os.path.join(sourceDir,  file) 
        targetFile = os.path.join(targetDir,  file) 
        #cover the files 
        if os.path.isfile(sourceFile): 
            open(targetFile, "wb").write(open(sourceFile, "rb").read())
            
def removeFileInFirstDir(targetDir): 
    for file in os.listdir(targetDir): 
        targetFile = os.path.join(targetDir,  file) 
        if os.path.isfile(targetFile): 
            os.remove(targetFile)

def moveFileto(sourceDir,  targetDir):      
    shutil.copy(sourceDir,  targetDir)
    
def writeVersionInfo(targetDir): 
    open(targetDir, "wb").write("Revison:")
    

def getCurTime(): 
    nowTime = time.localtime() 
    year = str(nowTime.tm_year) 
    month = str(nowTime.tm_mon) 
    if len(month) < 2: 
        month = '0' + month 
    day =  str(nowTime.tm_yday) 
    if len(day) < 2: 
        day = '0' + day 
    return (year + '-' + month + '-' + day)

if  __name__ =="__main__": 
    print("Start(S) or Quilt(Q) \n")
    flag = True 
    while (flag): 
        answer = raw_input() 
        if  'Q' == answer: 
            flag = False 
        elif 'S'== answer : 
            formatTime = getCurTime() 
            targetFoldername = "Build " + formatTime + "-01" 
            Target_File_Path += targetFoldername

            copyFiles(Debug_File_Path,   Target_File_Path) 
            removeFileInFirstDir(Target_File_Path) 
            coverFiles(Release_File_Path,  Target_File_Path) 
            moveFileto(Firebird_File_Path,  Target_File_Path) 
            moveFileto(AssistantGui_File_Path,  Target_File_Path) 
            writeVersionInfo(Target_File_Path+"\\ReadMe.txt") 
            print("all sucess" )
        else: 
            print("not the correct command")