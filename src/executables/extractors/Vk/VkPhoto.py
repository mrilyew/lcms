from executables.extractors.Base import BaseExtractor
from resources.Globals import os, download_manager, ExecuteResponse, VkApi, Path, json5, config, utils, logger
from resources.Exceptions import NotFoundException
#from core.Wheels import metadata_wheel, additional_metadata_wheel
from db.File import File

# Downloads photo from vk.com using api.
class VkPhoto(BaseExtractor):
    name = 'VkPhoto'
    category = 'Vk'
    params = {
        "item_id": {
            "desc_key": "item_id_desc",
            "type": "string",
            "maxlength": 3
        },
    }
    
    def passParams(self, args):
        self.passed_params["item_id"] = args.get("item_id")
        self.passed_params["preset_json"] = args.get("preset_json", None)
        self.passed_params["access_token"] = args.get("access_token", config.get("vk.access_token", None))
        self.passed_params["api_url"] = args.get("api_url", "api.vk.com/method")
        self.passed_params["vk_path"] = args.get("vk_path", "vk.com")

        assert self.passed_params.get("item_id") != None or self.passed_params.get("preset_json") != None, "item_id not passed"
        assert self.passed_params.get("access_token") != None, "access_token not passed"
        assert self.passed_params.get("api_url") != None, "api_url not passed"
        assert self.passed_params.get("vk_path") != None, "vk_path not passed"
    
    async def __recieveById(self, item_id):
        __vkapi = VkApi(token=self.passed_params.get("access_token"),endpoint=self.passed_params.get("api_url"))
        return await __vkapi.call("photos.getById", {"photos": item_id, "extended": 1, "photo_sizes": 1})
    
    async def run(self, args):
        # TODO add check for real links like vk.com/photo1_1
        __PHOTO_RES = None
        __PHOTO_ID  = self.passed_params.get("item_id")
        __PHOTO_OBJECT = None
        if self.passed_params.get("preset_json") == None:
            __PHOTO_RES = await self.__recieveById(__PHOTO_ID)
            try:
                __PHOTO_OBJECT = __PHOTO_RES[0]
                __PHOTO_ID  = f"{__PHOTO_OBJECT.get("owner_id")}_{__PHOTO_OBJECT.get("id")}"
            except:
                __PHOTO_OBJECT = None
        else:
            __PHOTO_RES = self.passed_params.get("preset_json")
            try:
                __PHOTO_OBJECT = __PHOTO_RES
            except Exception:
                __PHOTO_OBJECT = None
        
        if __PHOTO_OBJECT == None:
            raise NotFoundException("photo not found")

        ORIGINAL_NAME = "photo.jpg"
        SAVE_PATH = Path(os.path.join(self.temp_dir, ORIGINAL_NAME))
        logger.log(message=f"Recieved photo {__PHOTO_ID}",section="VK",name="message")
        
        PHOTO_URL = ""
        if __PHOTO_OBJECT.get("orig_photo") != None:
            PHOTO_URL = __PHOTO_OBJECT.get("orig_photo").get("url")
        else:
            if __PHOTO_OBJECT.get("url") != None:
                PHOTO_URL = __PHOTO_OBJECT.get("url")
            else:
                try:
                    __photo_size = next((d for d in __PHOTO_OBJECT.get("sizes") if d.get("type") == "w"), None)
                    PHOTO_URL = __photo_size.get("url")
                except Exception as ___e:
                    logger.logException(___e, section="Vk")

                    __photo_sizes = sorted(__PHOTO_OBJECT.get("sizes"), key=lambda x: (x['width'] is None, x['width']))
                    PHOTO_URL = __photo_sizes[0].get("url")
        
        HTTP_REQUEST = await download_manager.addDownload(end=PHOTO_URL,dir=SAVE_PATH)
        
        __file = File()
        __file.extension = "jpg"
        __file.upload_name = ORIGINAL_NAME
        __file.filesize = SAVE_PATH.stat().st_size
        __file.temp_dir = self.temp_dir
        __file.hash = utils.getRandomHash(64)
        __file.save()

        __PHOTO_OBJECT["site"] = self.passed_params.get("vk_path")
        __indexation = utils.clearJson(__PHOTO_OBJECT)

        return ExecuteResponse({
            "main_file": __file,
            "suggested_name": f"VK Photo {str(__PHOTO_ID)}",
            "source": "vk:photo"+str(__PHOTO_ID),
            "indexation_content": __indexation,
            "entity_internal_content": __PHOTO_OBJECT
        })

    def describeSource(self, INPUT_ENTITY):
        return {"type": "vk", "data": {
            "source": f"https://{INPUT_ENTITY.getFormattedInfo().get("vk_path")}/" + INPUT_ENTITY.orig_source
        }}
