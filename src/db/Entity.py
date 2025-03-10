from resources.Globals import consts, time, operator, reduce, Path, os, BaseModel, json5, file_manager, logger
from peewee import TextField, IntegerField, BigIntegerField, AutoField, BooleanField, TimestampField
from db.File import File

class Entity(BaseModel):
    self_name = 'entity'

    id = AutoField() # Absolute id
    main_file = TextField(null=True) # File extension
    files_list = TextField(null=True) # Files list
    hash = TextField(null=True) # Entity hash
    display_name = TextField(index=True,default='N/A') # Name that shown in list. Set by api
    description = TextField(index=True,null=True) # Description of entity. Set by api
    source = TextField(null=True) # Source of content (URL or path). Set by extractor
    indexation_content_string = TextField(index=True,null=True) # Content that will be used for search. Set by extractor. Duplicates "indexation_content" but without keys.
    # indexation_content = TextField(null=True) # TODO remove Additional info in json (ex. video name)
    frontend_data = TextField(null=True) # Info that will be used in frontend. Set by frontend.
    extractor_name = TextField(null=True,default='base') # Extractor that was used for entity
    tags = TextField(index=True,null=True) # csv tags
    preview = TextField(null=True) # Preview in json format
    # flags = IntegerField(default=0) # Flags.
    type = IntegerField(default=0) # 0 - main is the first file from dir
                                # 1 - main info is from "type_sub" (jsonистый объект)
    entity_internal_content = TextField(null=True,default=None) # DB info type. Format will be taken from "format" (json, xml)
    unlisted = BooleanField(index=True,default=0)
    deleted = BooleanField(index=True,default=0) # Is softly deleted
    author = TextField(null=True,default=consts['pc_fullname']) # Author of entity
    declared_created_at = TimestampField(default=time.time())
    created_at = TimestampField(default=time.time())
    edited_at = TimestampField(null=True, default=None)
    
    @property
    def orig_source(self):
        p1, p2 = self.source.split(":", 1)

        return p2
    
    @property
    def main_file_obj(self):
        return File.get(self.main_file)

    def delete(self, delete_dir=True):
        if delete_dir == True:
            file_manager.rmdir(self.getDirPath())

        self.deleted = 1
        self.save()

    # Ну и зачем всё это было. Ладно, может пригодится.
    def getCorrectSource(self):
        from resources.Globals import ExtractorsRepository

        __ext = (ExtractorsRepository()).getByName(self.extractor_name)
        if __ext == None:
            return {"type": "none", "data": {}}

        return __ext().describeSource(INPUT_ENTITY=self)

    def getFormattedInfo(self):
        entity_internal_content = getattr(self, "entity_internal_content", "{}")
        if entity_internal_content == None:
            entity_internal_content = "{}"
        
        return json5.loads(entity_internal_content)

    def getApiStructure(self):
        tags = ",".split(self.tags)
        if tags[0] == ",":
            tags = []
        
        frontend_data = None
        try:
            frontend_data = json5.loads(getattr(self, "frontend_data", "{}"))
        except Exception as wx:
            logger.logException(wx,noConsole=True)
            frontend_data = "{}"
        
        fnl = {
            "id": self.id,
            "format": self.format,
            "original_name": self.original_name,
            "display_name": self.display_name,
            "description": self.description,
            "filesize": self.filesize,
            "source": self.getCorrectSource(),
            "entity_internal_content": self.getFormattedInfo(),
            "frontend_data": frontend_data,
            "tags": tags,
            "flags": self.flags,
            "type": self.type,
            "created": self.created_at,
            "edited": self.edited_at,
            "author": self.author,
        }

        if self.type != 1:
            fnl.path = self.getPath()
            fnl.dir = self.getDirPath()

        return fnl
    
    def getPath(self):
        storage = consts['storage']
        hash = self.hash

        collection_path = os.path.join(storage, "files", hash[0:2])
        entity_path = os.path.join(collection_path, hash, hash + '.' + str(self.format))

        return entity_path
    
    def getDirPath(self, need_check = False):
        storage_path = consts['storage']
        hash = self.hash

        collection_path = os.path.join(storage_path, "files", str(hash[0:2]), hash)
        coll_path = Path(collection_path)

        if need_check == True and coll_path.exists() == False:
            coll_path.mkdir(parents=True, exist_ok=True)

        return collection_path

    @staticmethod
    def fetchItems(query = None, columns_search = []):
        items = Entity.select().where(Entity.unlisted == 0).where(Entity.deleted == 0)
        conditions = []

        for column in columns_search:
            match column:
                case "original_name":
                    conditions.append((Entity.original_name.contains(query)))
                case "display_name":
                    conditions.append((Entity.display_name.contains(query)))
                case "description":
                    conditions.append((Entity.description.contains(query)))
                case "source":
                    conditions.append((Entity.source.contains(query)))
                case "index":
                    conditions.append((Entity.index_content.contains(query)))
                case "saved":
                    conditions.append((Entity.extractor_name.contains(query)))
                case "author":
                    conditions.append((Entity.author.contains(query)))
        
        if conditions:
            items = items.where(reduce(operator.or_, conditions))
        
        return items.order_by(Entity.id.desc())
    
    @staticmethod
    def get(id):
        try:
            return Entity.select().where(Entity.id == id).where(Entity.deleted == 0).get()
        except:
            return None
