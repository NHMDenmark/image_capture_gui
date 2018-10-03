#Background process

#run on infinite loop inside try function
#Make sure sftp is mounted
#Open local storage
#Create tiff from img
#copy from local to erda
#Do checksum
#delete local copy
import os
import pysftp
import paramiko
import subprocess

from time import sleep
from base64 import b64decode
from guis.settings.local_settings import (SFTP_PUBLIC_KEY, ERDA_USERNAME, 
                                     ERDA_SFTP_PASSWORD, ERDA_HOST,
                                     ERDA_PORT, ERDA_FOLDER, DUMP_FOLDER, 
                                     CACHE_FOLDER, STORAGE_FOLDER)

class ERDA():
    def __init__(self):
        self.sftp = self.connectSFTP()
        
    def connectSFTP(self):
        key = paramiko.RSAKey(data=b64decode(SFTP_PUBLIC_KEY))
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.add(ERDA_HOST, 'ssh-rsa', key)
        
        sftp = pysftp.Connection(host=ERDA_HOST, username=ERDA_USERNAME, 
                                 password=ERDA_SFTP_PASSWORD, cnopts=cnopts)
        return sftp
    
    def upload(self, localPath, remotePath):
        self.sftp.put(localPath, remotePath)
    
    def getFiles(self, folder):
        return self.sftp.listdir(folder)
    
    def checkUploaded(self, erdaPath, cachePath):
        erdaFolder = '/'.join(erdaPath.split('/')[:-1])
        files = self.getFiles(erdaFolder)
        cacheFile = cachePath.split('/')[-1]
        
        if cacheFile in files:
            print('ERDA Upload okay for %s'%cacheFile)
            return True
        else:
            print('Something messed up %s '%cacheFile)
            return False
    
    def close(self):
        self.sftp.close()
        

    
def createTiff(arwPath):
    name = arwPath.split('/')[-1].split('.')[0]
    tiffFile = name + '.tiff'
    tiffPath = os.path.join(CACHE_FOLDER, tiffFile)
   
    subprocess.check_output(['sips', '-s','format','tiff', arwPath, '--out', tiffPath])
    return tiffPath
    
def getARWFiles(folder):
    ARWFiles = [f for f in getFiles(folder) if f.endswith('.arw')]
    return ARWFiles

def getFiles(folder):
    return os.listdir(folder)
    
def checkSum(file1, file2):
    pass
    
def deleteFile(_file):
    return os.remove(_file)
    
def deleteNonARWFilesFromLocalCache():
    local_files = getFiles(CACHE_FOLDER)
    for local_file in local_files:
        if (not local_file.endswith('.arw')) & (not local_file.endswith('.DS_Store')):
            path = os.path.join(CACHE_FOLDER, local_file)
            deleteFile(path)
            
def copyToLocalStorage(currentPath, newPath):
    subprocess.check_output(['cp', currentPath, newPath])
    
if __name__ == '__main__':
    #while True:
    for i in range(1):
        print('Deleting 1')
        deleteNonARWFilesFromLocalCache()
        print('starting ERDA')
        erda = ERDA()
        local_files = getARWFiles(CACHE_FOLDER)
        erda_files = erda.getFiles(ERDA_FOLDER)

        
        for local_file in local_files:
            print('looking at file: %s'%local_file)
            arwCachePath = os.path.join(CACHE_FOLDER, local_file)
            print('creating tiff')
            tiffCachePath = createTiff(arwCachePath)
            tiff_name = tiffCachePath.split('/')[-1]
            
            arwLocalPath = os.path.join(STORAGE_FOLDER, local_file)
            tiffLocalPath = os.path.join(STORAGE_FOLDER, tiff_name)
            
            print('Copying ARW Locally')
            copyToLocalStorage(arwCachePath, arwLocalPath)
            print('Copying Tiff Locally')
            copyToLocalStorage(tiffCachePath, tiffLocalPath)
            
            #what happens if file already uploaded
            
            
            arwERDAPath = os.path.join(ERDA_FOLDER, local_file)
            tiffERDAPath = os.path.join(ERDA_FOLDER, tiff_name)
            
            erda.upload(arwCachePath, arwERDAPath)
            uploadedARW = erda.checkUploaded(arwERDAPath, arwCachePath)
            
            erda.upload(tiffCachePath, tiffERDAPath)
            uploadedTiff = erda.checkUploaded(tiffERDAPath, tiffCachePath)
            
            if uploadedARW & uploadedTiff:
                deleteFile(arwCachePath)
                deleteFile(tiffCachePath)
            
        erda.close()
        sleep(1)
#        except Exception as ex:
#            if 'erda' in locals():
#                if hasattr(erda, 'sftp'):
#                    erda.sftp.close()
#                    
#            print(str(ex))
    
