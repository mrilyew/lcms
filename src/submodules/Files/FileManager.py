from resources.Globals import win32file, win32api, os, shutil, Path

class FileInfo():
    def __init__(self, entry, extended = False):
        self.name = entry.name
        self.path = entry.path
        self.type = 'file'
        self.extended = extended
        if entry.is_dir():
            self.type = 'dir'
        elif entry.is_symlink():
            self.type = 'symlink'

        if extended == True:
            stat = entry.stat()
            self.size = stat.st_size
            self.created_time = stat.st_ctime
            self.modified_time = stat.st_mtime
            self.accessed_time = stat.st_atime
            self.owner = stat.st_uid
            self.group = stat.st_gid
            self.permissions = stat.st_mode

    def takeInfo(self):
        base = {
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "extended": self.extended,
            "type": self.type
        }
        
        if(self.extended == True):
            base['size'] = self.size
            base['created_time'] = self.created_time
            base['modified_time'] = self.modified_time
            base['accessed_time'] = self.accessed_time
            base['owner'] = self.owner
            base['group'] = self.group
            base['permissions'] = self.permissions

        return base

class FileManager():
    def __init__(self):
        pass

    def getFolderItems(self, path, offset = 0, limit = 50, extended = False):
        return_array = []

        with os.scandir(path) as entries:
            entries = list(entries)
            total_count = len(entries)
            cutted_entries = entries[offset:limit + offset]

            for entry in cutted_entries:
                return_array.append(FileInfo(entry, extended))
            
            return return_array, total_count, len(return_array), offset + limit < total_count
        
    def getFolderSize(self, dir):
        return sum(file.stat().st_size for file in Path(dir).rglob('*'))
        
    def createFile(self, filename, dir, content=None):
        path = dir + '\\' + filename
        stream = open(path, 'w', encoding='utf-8')
        if content != None:
            stream.write(content)
        
        stream.close()

    def newFile(self, path, content=None, write_mode = "wb"):
        stream = open(str(path), write_mode)
        if content != None:
            stream.write(content)
        
        stream.close()

    def moveFile(self, input_path, output_path):
        shutil.move(str(input_path), str(output_path))
    
    def copyFile(self, input_path, output_path):
        shutil.copy2(str(input_path), str(output_path))
    
    def symlinkFile(self, input_path, output_path):
        os.symlink(str(input_path), str(output_path))
    
    def rmdir(self, str_path):
        path = Path(str_path)
        
        for sub in path.iterdir():
            if sub.is_dir():
                self.rmdir(sub)
            else:
                sub.unlink()

        path.rmdir()

    # https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    def copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
    
file_manager = FileManager()
