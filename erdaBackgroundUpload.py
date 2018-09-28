#Background process

#run on infinite loop inside try function
#Make sure sftp is mounted
#Open local storage
#Create tiff from img
#copy from local to erda
#Do checksum
#delete local copy

from time import sleep
from guis.settings.local_settings import (SFTP_PUBLIC_KEY, ERDA_USERNAME, 
                                     ERDA_SFTP_PASSWORD, ERDA_HOST,
                                     ERDA_PORT, ERDA_FOLDER, DUMP_FOLDER, CACHE_FOLDER)

def uploadToERDA(localPath, remotePath):
    key = paramiko.RSAKey(data=b64decode(SFTP_PUBLIC_KEY))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys.add(ERDA_HOST, 'ssh-rsa', key)
    
    sftp = pysftp.Connection(host=ERDA_HOST, username=ERDA_USERNAME, 
                             password=ERDA_SFTP_PASSWORD, cnopts=cnopts)

    sftp.put(localPath,remotePath)
    sftp.close()
    
    #self.commandLine(['cp',tempRawPath,rawImgPath])   
    
    
def checkSFTPMounted():
    pass
    
def createTiff(arwPath):
    name = arwPath.split('/')[-1].split('.')[0]
    tiffFile = name + '.tiff'
    tiffPath = os.path.join(CACHE_FOLDER, tiffFile)
   
    self.commandLine(['sips', '-s','format','tiff', arwPath, '--out', tiffPath])
    
def getFiles(folder):
    return os.listdir(folder)
    
def checkSum(file1, file2):
    pass
    
def deleteFile(file):
    return os.remove(file)
    
def deleteNonARWFilesFromLocalStorage():
    local_files = getFiles(CACHE_FOLDER)
    for file in local_files:
        if not file.endswith('.arw'):
            deleteFile(file)
    
if __name__ == '__main__':
    while True:
        try:
            checkSFTPMounted()
            deleteNonARWFilesFromLocalStorage()
            local_files = getFiles(CACHE_FOLDER)
            erda_files = getFiles(ERDA_FOLDER)
            
            for local_file in local_files:
                arwLocalPath = os.path.join(CACHE_FOLDER, local_file)
                #what happens if file already uploaded
                
                tiffLocalPath = createTiff(arwPath)
                arwERDAPath = os.path.join(ERDA_FOLDER, local_file)
                tiffERDAPath = os.path.join(ERDA_FOLDER, local_file)
                
                uploadToERDA(arwLocalPath, arwERDAPath)
                checkSum(arwERDAPath, arwLocalPath)
                
                uploadToERDA(tiffLocalPath, tiffERDAPath)
                checkSum(tiffERDAPath, tiffLocalPath)
                
                deleteFile(arwLocalPath)
                deleteFile(tiffLocalPath)
                
            
            sleep(1)
        except:
            pass
    
