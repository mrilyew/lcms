from resources.Globals import contextmanager, secrets, os, platform, sys, random, json, consts, Path, requests, mimetypes, wget, zipfile
from collections import defaultdict

class Utils():
    def parse_args(self):
        args = sys.argv
        parsed_args = {}
        key = None
        for arg in args[1:]:
            if arg.startswith('--'):
                if key:
                    parsed_args[key] = True
                key = arg[2:]
                parsed_args[key] = True
            #elif arg.startswith('-'):
            #    if key:
            #        parsed_args[key] = True
            #    key = arg[1:]
            #    parsed_args[key] = True
            else:
                if key:
                    parsed_args[key] = arg
                    key = None
                else:
                    pass

        return parsed_args
    
    def parse_params(self, input_data):
        params = {}
        params_arr = input_data.split('&')
        for param in params_arr:
            try:
                _spl = param.split('=')
                params[_spl[0]] = _spl[1]
            except IndexError:
                pass
        
        return params
    
    def random_int(self, min, max):
        return random.randint(min, max)
    
    def parse_json(self, text):
        try:
            return json.loads(text)
        except:
            return {}
    
    def str_to_path(self, path):
        return Path(path)
    
    def remove_protocol(self, strr):
        return strr.replace("https://", "").replace("http://", "").replace("ftp://", "")

    def find_owner(self, id, profiles, groups):
        search_array = profiles
        if id < 0:
            search_array = groups
        
        for item in search_array:
            if item.get('id') == abs(int(id)):
                return item
            
        return None
    
    def fast_get_request(self, url: str ='', user_agent=''):
        result = requests.get(url, headers={
            'User-Agent': user_agent
        })
        parsed_result = None
        if result.headers.get('content-type').index('application/json') != -1:
            parsed_result = json.loads(result.content)

        return parsed_result
    
    def proc_strtr(self, text, length = 0):
        newString = text[:length]

        return newString + ("..." if text != newString else "")
    
    def parse_entity(self, input_string: str, allowed_entities = ["entity", "collection"]):
        from db.Entity import Entity
        from db.Collection import Collection

        elements = input_string.split('entity')
        if len(elements) > 1 and elements[0] == "":
            if "entity" in allowed_entities:
                entity_id = elements[1]
                return Entity.get(entity_id)
        elif 'collection' in input_string:
            if "collection" in allowed_entities:
                collection_id = input_string.split('collection')[1]
                return Collection.get(collection_id)
        else:
            return None

    def extract_metadata_to_dict(self, mtdd):
        metadata_dict = defaultdict(list)

        for line in mtdd:
            key_value = line.split(": ", 1)
            if key_value[0].startswith('- '):
                key = key_value[0][2:]
                metadata_dict[key].append(key_value[1])

        return dict(metadata_dict)
    
    def json_values_to_string(self, data):
        result = []

        if isinstance(data, dict):
            for value in data.values():
                result.append(self.json_values_to_string(value))

        elif isinstance(data, list):
            for item in data:
                result.append(self.json_values_to_string(item))

        else:
            return str(data)
        
        return ' '.join(filter(None, result))
    
    def get_mime_type(self, filename: str):
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type
    
    def get_ext(self, filename: str):
        file_splitted_array = filename.split('.')
        file_output_ext = ''
        if len(file_splitted_array) > 1:
            file_output_ext = file_splitted_array[-1]

        return file_output_ext
    
    def is_generated_ext(self, ext: str):
        return ext in ["php", "html"]
    
    def getChromishPlatform(self):
        arch = ""
        system_arch = ""
        system = platform.system().lower()
        architecture = platform.machine().lower() 

        if architecture in ['x86_64', 'amd64']:
            arch = '64'
        elif architecture in ['i386', 'i686', 'x86']:
            arch = '32'
        elif architecture in ['arm64', 'aarch64']:
            arch = 'arm64'
        else:
            arch = architecture

        match system:
            case "darwin":
                if architecture in ['arm64', 'aarch64']:
                    architecture = "arm64"
                else:
                    architecture = "x64"
                
                system_arch = f"mac-{architecture}"
            case "windows":
                system_arch = f"win{arch}"
            case _:
                system_arch = f"{system}{arch}"
        
        return system_arch
    
    def getRandomHash(self, __bytes: int = 32):
        return secrets.token_urlsafe(__bytes)
    
    def typicalPluginsList(self, folder: str):
        dir = f"{consts["executable"]}\\{folder}"

        return os.listdir(dir)
    
    def clearJson(self, __json):
        if isinstance(__json, dict):
            return {key: self.clearJson(value) for key, value in __json.items() if isinstance(value, (dict, list, str))}
        elif isinstance(__json, list):
            return [self.clearJson(item) for item in __json if isinstance(item, (dict, list, str))]
        elif isinstance(__json, str):
            return __json
        else:
            return None
    
    @contextmanager
    def overrideDb(self, __class, __db):
        old_db = __class._meta.database
        __class._meta.database = __db
        yield
        __class._meta.database = old_db
    
utils = Utils()
