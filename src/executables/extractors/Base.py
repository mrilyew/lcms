from resources.Globals import storage, os, utils, file_manager, json, logger
from db.Entity import Entity

class BaseExtractor:
    name = 'base'
    category = 'template'
    passed_params = {}

    def __init__(self, temp_dir=None, del_dir_on_fail=True):
        self.temp_dir = temp_dir
        self.del_dir_on_fail = del_dir_on_fail

    def passParams(self, args):
        self.passed_params["display_name"] = args.get("display_name", None)
        self.passed_params["description"] = args.get("description", None)
        self.passed_params["is_hidden"] = args.get("is_hidden", False)
    
    def saveAsCollection(self, __EXECUTE_RESULT):
        from db.Collection import Collection

        FINAL_COLLECTION = Collection()
        if self.passed_params.get("display_name") == None:
            if __EXECUTE_RESULT.get("suggested_name") == None:
                FINAL_COLLECTION.name = "N/A"
            else:
                FINAL_COLLECTION.name = __EXECUTE_RESULT.get("suggested_name")
        else:
            FINAL_COLLECTION.name = self.passed_params.get("display_name")

        if __EXECUTE_RESULT.get("suggested_description") != None:
            FINAL_COLLECTION.description = __EXECUTE_RESULT.get("suggested_description")
        else:
            FINAL_COLLECTION.description = self.passed_params.get("description")

        FINAL_COLLECTION.order = Collection.getAllCount()
        if FINAL_COLLECTION.get("source") != None:
            FINAL_COLLECTION.source = __EXECUTE_RESULT.get("source")

        FINAL_COLLECTION.save()

        return FINAL_COLLECTION

    def saveAsEntity(self, __EXECUTE_RESULT):
        FINAL_ENTITY = Entity()
        if __EXECUTE_RESULT.get("hash") != None:
            __hash = utils.getRandomHash(32)
        else:
            __hash = __EXECUTE_RESULT.get("hash")
        
        indexation_content_ = __EXECUTE_RESULT.get("indexation_content")
        entity_internal_content_ = __EXECUTE_RESULT.get("entity_internal_content")

        FINAL_ENTITY.hash = __hash
        if entity_internal_content_ != None:
            FINAL_ENTITY.entity_internal_content = json.dumps(entity_internal_content_)
        else:
            FINAL_ENTITY.entity_internal_content = json.dumps(indexation_content_)
        if __EXECUTE_RESULT.get("main_file") != None:
            FINAL_ENTITY.file_id = __EXECUTE_RESULT.get("main_file").id
        
        if __EXECUTE_RESULT.get("unlisted", 0) == 1:
            FINAL_ENTITY.unlisted = 1

        if __EXECUTE_RESULT.get("linked_files") != None:
            FINAL_ENTITY.linked_files = ",".join(str(v) for v in __EXECUTE_RESULT.get("linked_files"))
        
        FINAL_ENTITY.extractor_name = self.name
        if self.passed_params.get("display_name") != None:
            FINAL_ENTITY.display_name = self.passed_params["display_name"]
        else:
            if __EXECUTE_RESULT.get("main_file") == None:
                if __EXECUTE_RESULT.get("suggested_name") == None:
                    FINAL_ENTITY.display_name = "N/A"
                else:
                    FINAL_ENTITY.display_name = __EXECUTE_RESULT.get("suggested_name")
            else:
                FINAL_ENTITY.display_name = __EXECUTE_RESULT.get("main_file").upload_name
        
        if self.passed_params.get("description") != None:
            FINAL_ENTITY.description = self.passed_params["description"]
        if __EXECUTE_RESULT.get("source") != None:
            FINAL_ENTITY.source = __EXECUTE_RESULT.get("source")
        if __EXECUTE_RESULT.get("indexation_content") != None:
            #FINAL_ENTITY.indexation_content = json.dumps(indexation_content_) # remove
            FINAL_ENTITY.indexation_content_string = str(utils.json_values_to_string(indexation_content_)).replace('None', '').replace('  ', ' ').replace('\n', ' ')
        else:
            FINAL_ENTITY.indexation_content_string = json.dumps(utils.json_values_to_string(entity_internal_content_)).replace('None', '').replace('  ', ' ').replace('\n', ' ')
        
        FINAL_ENTITY.save()

        return FINAL_ENTITY

    def saveToDirectory(self, __EXECUTE_RESULT):
        stream = open(os.path.join(self.temp_dir, "data.json"), "w")
        if __EXECUTE_RESULT != None:
            stream.write(json.dumps({
                "source": __EXECUTE_RESULT.source,
                "entity_internal_content": __EXECUTE_RESULT.entity_internal_content,
                "indexation_content": __EXECUTE_RESULT.indexation_content,
                "hash": __EXECUTE_RESULT.hash,
            }, indent=2))
        
        stream.close()

    def onFail(self):
        if self.del_dir_on_fail == True:
            file_manager.rmdir(self.temp_dir)

    async def run(self, args):
        pass
    
    async def postRun(self):
        pass
    
    # Typical preview
    def thumbnail(self, entity, args={}):
        from resources.Globals import ThumbnailsRepository
        __FILE = entity.file
        if __FILE == None:
            return None
        
        ext = __FILE.extension
        if args.get("preview_file"):
            ext = utils.get_ext(args.get("preview_file"))
        
        thumb = (ThumbnailsRepository()).getByFormat(ext)
        if thumb == None:
            return None
        
        thumb_class = thumb(save_dir=__FILE.getDirPath())
        return thumb_class.run(file=__FILE,params=args)
    
    async def fastGetEntity(self, params, args):
        from db.File import File

        self.passParams(params)
        EXTRACTOR_RESULTS = await self.execute({})
        if params.get("is_hidden", False) == True:
            EXTRACTOR_RESULTS["entities"][0]["unlisted"] = 1

        __file = EXTRACTOR_RESULTS.get("entities")[0].get("file")
        if __file != None:
            file = File.fromJson(__file, self.temp_dir)
            EXTRACTOR_RESULTS["entities"][0]["main_file"] = file
        
        RETURN_ENTITY = self.saveAsEntity(EXTRACTOR_RESULTS.get("entities")[0])

        if EXTRACTOR_RESULTS.get("entities")[0].get("main_file") != None:
            EXTRACTOR_RESULTS.get("entities")[0].get("main_file").moveTempDir()
        
            thumb_result = self.thumbnail(entity=RETURN_ENTITY,args=EXTRACTOR_RESULTS.get("entities")[0])
            if thumb_result != None:
                RETURN_ENTITY.preview = json.dumps(thumb_result)
                RETURN_ENTITY.save()
        
        await self.postRun()
        return RETURN_ENTITY
            
    def describe(self):
        return {
            "id": self.name,
            "category": self.category,
            "hidden": getattr(self, "hidden", False),
            "params": getattr(self, "params", {})
        }

    def describeSource(self, INPUT_ENTITY):
        return {"type": "none", "data": {
            "source": None
        }}

    async def execute(self, args):
        EXTRACTOR_RESULTS = None

        try:
            EXTRACTOR_RESULTS = await self.run(args=args)
        except Exception as x:
            logger.logException(x, section="Exctractors")
            self.onFail()

            raise x

        return EXTRACTOR_RESULTS
    
