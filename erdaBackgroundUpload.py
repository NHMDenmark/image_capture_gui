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
import logging
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
            logging.info('ERDA Upload okay for %s'%cacheFile)
            return True
        else:
            logging.info('Something messed up %s '%cacheFile)
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
    if len(ARWFiles):
        paths = [os.path.join(folder, image) for image in ARWFiles]
        paths.sort(key=os.path.getctime)
        return [path.split('/')[-1] for path in paths]
    else:
        return '', ''

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
            logging.info('Deleting %s'%path)
            deleteFile(path)
    
if __name__ == '__main__':
    while True:
        sleep(1)
        try:
            logging.basicConfig(filename='/Users/robertahunt/Documents/gui/logs/erda_upload_log.txt', level=logging.INFO)
            
            deleteNonARWFilesFromLocalCache()

            logging.info('Getting lists of files')
            local_files = getARWFiles(CACHE_FOLDER)
            logging.info(local_files)
            
            if len(local_files):
                logging.info('Starting ERDA')
                erda = ERDA()
            
                erda_files = erda.getFiles(ERDA_FOLDER)
        
            
                for local_file in local_files:
                    logging.info('looking at file: %s'%local_file)
                    arwCachePath = os.path.join(CACHE_FOLDER, local_file)
                    logging.info('creating tiff')
                    tiffCachePath = createTiff(arwCachePath)
                    tiff_name = tiffCachePath.split('/')[-1]
                    
                    arwLocalPath = os.path.join(STORAGE_FOLDER, local_file)
                    tiffLocalPath = os.path.join(STORAGE_FOLDER, tiff_name)
                    
                    #what happens if file already uploaded
                    
                    
                    arwERDAPath = os.path.join(ERDA_FOLDER, local_file)
                    tiffERDAPath = os.path.join(ERDA_FOLDER, tiff_name)
                    
                    erda.upload(tiffCachePath, tiffERDAPath)
                    uploadedTiff = erda.checkUploaded(tiffERDAPath, tiffCachePath)
                    
                    erda.upload(arwCachePath, arwERDAPath)
                    uploadedARW = erda.checkUploaded(arwERDAPath, arwCachePath)
                    
                    
                    if uploadedARW & uploadedTiff:
                        logging.info('Deleting cached files')
                        deleteFile(arwCachePath)
                        deleteFile(tiffCachePath)
                    
                erda.close()
        except Exception as ex:
            if 'erda' in locals():
                if hasattr(erda, 'sftp'):
                    erda.sftp.close()
                    
            logging.warning('Exception encountered: '+str(ex))
    
