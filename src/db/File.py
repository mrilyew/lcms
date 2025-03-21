from resources.Globals import consts, BaseModel, Path, os, utils, shutil
from peewee import TextField, IntegerField, BigIntegerField, AutoField, BooleanField, TimestampField

# File is not a file, its a directory with main file and secondary files.
# So the dir and main file names as hash
class File(BaseModel):
    self_name = 'file'
    temp_dir = ''

    id = AutoField() # ABSOLUTE ID
    hash = TextField(null=True,default=utils.getRandomHash(64)) # Entity hash
    upload_name = TextField(index=True,default='N/A') # Upload name (with extension)
    extension = TextField(null=True,default="json") # File extension
    filesize = BigIntegerField(default=0) # Size of file
    #dir_filesize = BigIntegerField(default=0) # Size of dir

    def moveTempDir(self):
        from resources.Globals import storage
        
        # Renaming main file 
        MAIN_FILE_PATH = Path(self.temp_dir + '\\' + self.upload_name)
        MAIN_FILE_PATH_NEW = f'{self.temp_dir}\\{str((str(self.hash) + '.' + self.extension))}'
        MAIN_FILE_PATH.rename(MAIN_FILE_PATH_NEW)
        
        # Making short hash directory
        # And returning full hash directory.
        FULL_HASH_DIRECTORY = Path(storage.makeHashDir(self.hash, only_return=True))
        
        Path(self.temp_dir).rename(FULL_HASH_DIRECTORY)

    def getApiStructure(self):
        fnl = {
            "extension": self.extension,
            "id": self.id,
            "upload_name": self.upload_name,
            "filesize": self.filesize,
            "file_path": self.getPath(),
            "dir_path": self.getDirPath(),
        }

        return fnl

    def getPath(self):
        STORAGE_PATH = consts["storage"]
        HASH = self.hash

        COLLECTION_PATH = os.path.join(STORAGE_PATH, "files", HASH[0:2])
        ENTITY_PATH = os.path.join(COLLECTION_PATH, HASH, f"{HASH}.{str(self.extension)}")

        return ENTITY_PATH
    
    def getDirPath(self, need_check = False):
        STORAGE_PATH = consts["storage"]
        HASH = self.hash

        COLLECTION_PATH = os.path.join(STORAGE_PATH, "files", str(HASH[0:2]), HASH)
        COLLECTION_PATH_OBJ = Path(COLLECTION_PATH)

        if need_check == True and COLLECTION_PATH_OBJ.exists() == False:
            COLLECTION_PATH_OBJ.mkdir(parents=True, exist_ok=True)

        return COLLECTION_PATH

    @staticmethod
    def fromJson(json_input, temp_dir):
        __file = File()
        __file.extension = json_input.get("extension")

        if json_input.get("hash") == None:
            __file.hash = utils.getRandomHash(32)
        else:
            __file.hash = json_input.get("hash")
        
        __file.upload_name = json_input.get("upload_name")
        __file.filesize = json_input.get("filesize")
        __file.temp_dir = temp_dir
        
        __file.save()

        return __file
