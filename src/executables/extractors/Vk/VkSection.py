from resources.Globals import VkApi, logger, math, asyncio, copy
from executables.extractors.Vk.VkBase import VkBase
from resources.Exceptions import InvalidPassedParam

class VkSection(VkBase):
    name = 'VkSection'
    category = 'Vk'
    manual_params = True
    docs = {
        "description": {
            "name": {
                "ru": "VK Раздел",
                "en": "VK Section"
            },
            "definition": {
                "ru": "Шаблон объекта из vk.com",
                "en": "Object template from vk.com"
            }
        }
    }

    def declare():
        params = {}
        params["item_id"] = {
            "docs": {
                "definition": {
                    "ru": "ID объекта/пользователя/группы. Если \"section\" = \"fave\" — название секции",
                    "en": "ID of object/user/group. If \"section\" = \"fave\" — name of fave section",
                },
            },
            "type": "string",
        }
        params["section"] = {
            "docs": {
                "definition": {
                    "ru": "Название секции",
                    "en": "Name of section",
                },
                "values": {
                    "photos": {
                        "ru": "Все фотографии пользователя/группы",
                        "en": "All photos of user/group"
                    },
                    "wall": {
                        "ru": "Все посты со стены пользователя/группы",
                        "en": "All posts from user/group"
                    },
                    "album": {
                        "ru": "Фотографии из альбома",
                        "en": "Photos from album"
                    },
                    "board": {
                        "ru": "Все комментарии из обсуждения",
                        "en": "All comments from board"
                    },
                    "fave": {
                        "ru": "Весь контент из закладок",
                        "en": "Content from fave",
                    },
                    "post_comments": {
                        "ru": "Все комментарии под постом",
                        "en": "All comments below post",
                    },
                    "video_comments": {
                        "ru": "Все комментарии под видео",
                        "en": "All comments below video",
                    },
                    "photo_comments": {
                        "ru": "Все комментарии под фото",
                        "en": "All comments below photo",
                    },
                    "photo_all_comments": {
                        "ru": "Все комментарии под альбомом",
                        "en": "All comments below album",
                    },
                    "notes_comments": {
                        "ru": "Все комментарии под заметкой",
                        "en": "All comments below note",
                    },
                    "messages": {
                        "ru": "Все сообщения из беседы",
                        "en": "All messages from discussion",
                    },
                }
            },
            "type": "array",
            "values": ["photos", "wall", "album", "board", "fave", "post_comments", "video_comments", "photo_comments", "photo_all_comments", "notes_comments", "messages"],
            "assertion": {
                "assert_not_null": True,
            },
        }
        params["api_timeout"] = {
            "docs": {
                "definition": {
                    "ru": "Таймаут между вызовами API",
                    "en": "Timeout before API calls",
                },
            },
            "type": "int",
            "default": 0,
        }
        params["limit"] = {
            "docs": {
                "definition": {
                    "ru": "Лимит полученных записей",
                    "en": "Limit of recieved entities",
                },
            },
            "type": "int",
            "default": 0,
        }
        params["per_page"] = {
            "docs": {
                "definition": {
                    "ru": "Число полученных записей при каждом вызове",
                    "en": "Number of recieved entities by every call",
                },
            },
            "type": "int",
            "default": 100
        }
        params["start_range"] = {
            "docs": {
                "definition": {
                    "ru": "Номер первой итерации",
                    "en": "Number of first iteration",
                },
            },
            "type": "int",
            "default": 0
        }
        params["filter"] = {
            "type": "string",
            "default": None,
            "assertion": {
                "only_when": [
                    {"section": ["wall"]}
                ]
            }
        }
        params["download_attachments_json_list"] = {
            "docs": {
                "definition": {
                    "ru": "Перечисленный через запятую список экспортируемых attachments",
                    "en": "Number of first iteration",
                },
                "examples": ["*", "photo,video,audio,album,link,article"]
            },
            "type": "string",
            "default": "*",
            "assertion": {
                "only_when": [
                    {"section": ["wall", "messages"]},
                    {
                        "section": ["fave"],
                        "item_id": "post"
                    }
                ]
            }
        }
        params["download_attachments_file_list"] = {
            "type": "string",
            "default": "photo",
            "assertion": {
                "only_when": [
                    {"section": ["wall", "messages"]},
                    {
                        "section": ["fave"],
                        "item_id": "post"
                    }
                ]
            }
        }
        params["download_reposts"] = {
            "type": "bool",
            "default": True,
            "assertion": {
                "only_when": [
                    {"section": ["wall", "messages"]},
                    {
                        "section": ["fave"],
                        "item_id": "post"
                    }
                ]
            }
        }
        params["download_comments"] = {
            "type": "bool",
            "default": False,
            "assertion": {
                "only_when": [
                    {"section": ["wall", "messages"]},
                    {
                        "section": ["fave"],
                        "item_id": "post"
                    }
                ]
            }
        }
        params["rev"] = {
            "type": "bool",
            "default": True,
            "assertion": {
                "only_when": [
                    {"section": ["album", "messages"]}
                ]
            }
        }
        params["tag_id"] = {
            "type": "int",
            "assertion": {
                "only_when": [
                    {"section": ["fave"]}
                ]
            }
        }
        params["comment_id"] = {
            "type": "int",
            "assertion": {
                "only_when": [
                    {"section": ["post_comments"]}
                ]
            }
        }
        params["download_file"] = {
            "type": "bool",
            "default": True,
            "assertion": {
                "only_when": [
                    {"section": ["fave"]}
                ]
            }
        }

        return params

    def _collection(self):
        __item_ids = self.passed_params.get("item_id")
        item_id_collection = __item_ids.split(",")[0]

        __collection = {
            "suggested_name": f"Vk Collection {item_id_collection}",
        }

        match(self.passed_params.get("section")):
            case "photos":
                __collection["suggested_name"] = f"Vk Photos {item_id_collection}"
            case "wall":
                __collection["suggested_name"] = f"Vk Wall {item_id_collection}"
            case "album":             
                __collection["suggested_name"] = f"Vk Album {item_id_collection}"
            case "post_comments":
                __suggested_name = f"Vk Comments from {self.passed_params.get("section").replace("_comments", "")} {item_id_collection}"
                __collection["suggested_name"] = __suggested_name
            case "messages":
                __collection["suggested_name"] = f"Vk Conversation {item_id_collection}"

        return __collection

    async def run(self, args):
        __vkapi = VkApi(token=self.passed_params.get("access_token"),endpoint=self.passed_params.get("api_url"))
        __total_count = 0
        __downloaded_count = 0
        __times = 0
        __per_page = int(self.passed_params.get("per_page"))
        __start_range = int(self.passed_params.get("start_range"))
        __method = ""
        __dict_name = "items"
        __final_entities = []
        __has_profile = False
        __pass_params = {}
        __extractor = None
        __extract_type = False
        __count_call = None
        __extractor_params = {
            "unlisted": 1,
            "access_token": self.passed_params.get("access_token"),
            "api_url": self.passed_params.get("api_url"),
            "vk_path": self.passed_params.get("vk_path"),
            "download_file": self.passed_params.get("download_file"),
        }

        __item_ids = self.passed_params.get("item_id")
        item_id_collection = __item_ids.split(",")[0]

        from executables.extractors.Vk.VkPhoto import VkPhoto
        from executables.extractors.Vk.VkPost import VkPost
        from executables.extractors.Vk.VkIdentity import VkIdentity
        from executables.extractors.Vk.VkVideo import VkVideo
        from executables.extractors.Vk.VkArticle import VkArticle
        from executables.extractors.Vk.VkLink import VkLink
        from executables.extractors.Vk.VkComment import VkComment
        from executables.extractors.Vk.VkMessage import VkMessage

        # Making first call
        match(self.passed_params.get("section")):
            case "photos":
                __method = "photos.getAll"
                __count_call = await __vkapi.call(__method, {"owner_id": item_id_collection, "count": 1})
                __extractor = VkPhoto
                __pass_params = {
                    "owner_id": item_id_collection, 
                    "extended": 1,
                    "photo_sizes": 1
                }
            case "wall":
                __method = "wall.get"
                __temp_final_params = {"owner_id": item_id_collection, "count": 1}
                if self.passed_params.get("filter") != None:
                    __temp_final_params["filter"] = self.passed_params.get("filter")

                __has_profile = True
                __count_call = await __vkapi.call(__method, __temp_final_params)
                __extractor = VkPost
                __extractor_params["download_attachments_json_list"] = self.passed_params.get("download_attachments_json_list")
                __extractor_params["download_attachments_file_list"] = self.passed_params.get("download_attachments_file_list")
                __extractor_params["download_reposts"] = self.passed_params.get("download_reposts")
                __extractor_params["download_comments"] = False
                __pass_params = {
                    "owner_id": item_id_collection, 
                    "extended": 1, 
                    "photo_sizes": 1,
                }
                if self.passed_params.get("filter") != None:
                    __pass_params["filter"] = self.passed_params.get("filter")
            case "album":
                __method = "photos.get"
                __spl = item_id_collection.split("_")
                __owner_id = __spl[0]
                __item_id =  __spl[1]

                match __item_id:
                    case "0":
                        __item_id = "profile"
                    case "00":
                        __item_id = "wall"
                    case "000":
                        __item_id = "saved"

                __pass_params = {
                    "owner_id": __owner_id,
                    "album_id": __item_id,
                    "rev": int(self.passed_params.get("rev")), 
                    "extended": 1,
                    "photo_sizes": 1,
                }
                __count_call = await __vkapi.call(__method, {"owner_id": __owner_id, "album_id": __item_id, "count": 1})
                __extractor = VkPhoto
            case "fave":
                min_group_fields = "activity,photo_100,photo_200,photo_50,is_member,is_closed,description,members_count,is_subscribed"
                min_user_fields = "photo_50,online,photo_max,last_seen"
                __extract_type = True

                match self.passed_params.get("item_id"):
                    case "users" | "groups" | "hints":
                        __method = "fave.getPages"
                        __pass_params = {
                            "type": self.passed_params.get("item_id"),
                        }
                        __extractor = VkIdentity
                    case "post" | "video" | "article" | "link":
                        __method = "fave.get"
                        __pass_params = {
                            "item_type": self.passed_params.get("item_id"),
                            "extended": 1,
                        }

                        match self.passed_params.get("item_id"):
                            case "post":
                                __extractor = VkPost
                                __extractor_params["download_attachments_json_list"] = self.passed_params.get("download_attachments_json_list")
                                __extractor_params["download_attachments_file_list"] = self.passed_params.get("download_attachments_file_list")
                                __extractor_params["download_reposts"] = self.passed_params.get("download_reposts")
                                __extractor_params["download_comments"] = False
                            case "video":
                                __extractor = VkVideo
                            case "article":
                                __extractor = VkArticle
                            case "link":
                                __extractor = VkLink

                __extractor_params["download_avatar"] = self.passed_params.get("download_file")
                __extractor_params["download_cover"] = self.passed_params.get("download_cover")

                _tmp_call = {"item_type": self.passed_params.get("item_id"), "count": 1}
                __pass_params["fields"] = min_group_fields + "," + min_user_fields
                if self.passed_params.get("tag_id") != None:
                    __pass_params["tag_id"] = self.passed_params.get("tag_id")
                    _tmp_call["tag_id"] = self.passed_params.get("tag_id")

                __count_call = await __vkapi.call(__method, _tmp_call)
            case "post_comments" | "board" | "photo_comments" | "photo_all_comments" | "video_comments" | "notes_comments":
                __spl = item_id_collection.split("_")
                __owner_id = __spl[0]
                __item_id =  __spl[1]

                __pass_params = {
                    "need_likes": 1, 
                    "sort": "asc",
                    "extended": 1,
                    "thread_items_count": self.passed_params.get("thread_items_count", 10),
                }

                match(self.passed_params.get("section")):
                    case "post_comments":
                        __pass_params["owner_id"] = __owner_id
                        __pass_params["post_id"] = __item_id
                        __method = "wall.getComments"
                        if self.passed_params.get("comment_id") != None:
                            __pass_params["comment_id"] = self.passed_params.get("comment_id")
                    case "board":
                        __pass_params["group_id"] = abs(__owner_id)
                        __pass_params["topic_id"] = __item_id
                        __method = "board.getComments"
                    case "notes_comments":
                        __pass_params["owner_id"] = __owner_id
                        __pass_params["note_id"] = __item_id
                        __method = "notes.getComments"
                    case "photo_all_comments":
                        __pass_params["owner_id"] = __owner_id
                        __pass_params["album_id"] = __item_id
                        __method = "photos.getAllComments"
                    case "photo_comments":
                        __pass_params["owner_id"] = __owner_id
                        __pass_params["photo_id"] = __item_id
                        __method = "photos.getComments"
                    case "video_comments":
                        __pass_params["owner_id"] = __owner_id
                        __pass_params["video_id"] = __item_id
                        __method = "video.getComments"

                __temp_params = __pass_params
                __temp_params["count"] = 1

                __count_call = await __vkapi.call(__method, __temp_params)
                __extractor = VkComment
            case "messages":
                __method = "messages.getHistory"
                __count_call = await __vkapi.call(__method, {"peer_id": item_id_collection, "count": 1})
                __extractor = VkMessage
                __pass_params = {
                    "peer_id": item_id_collection, 
                    "extended": 1
                }
                __extractor_params["download_attachments_json_list"] = self.passed_params.get("download_attachments_json_list")
                __extractor_params["download_attachments_file_list"] = self.passed_params.get("download_attachments_file_list")
                __extractor_params["download_reposts"] = self.passed_params.get("download_reposts")
            case _:
                raise InvalidPassedParam("invalid section")

        __total_count = __count_call.get("count")
        __times = math.ceil(__total_count / __per_page)
        __extractor = __extractor(write_mode=self.write_mode)

        logger.log(message=f"Total {__total_count} items; will be {__times} calls",section="VkSection",name="message")
        for time in range(__start_range, __times):
            offset = __per_page * time
            if self.passed_params.get("limit") > 0 and (__downloaded_count > self.passed_params.get("limit")):
                break

            logger.log(message=f"{time + 1}/{__times} time of items recieving; {offset} offset",section="VkCollection",name="message")

            __pass_params["count"] = __per_page
            __pass_params["offset"] = offset
            __time_call = await __vkapi.call(__method, __pass_params)

            __items = __time_call.get(__dict_name)
            '''if len(__items) < 1:
                logger.log(message=f"Time {time + 1}/{__times}: no items. Probaly broken count. Exiting...",section="VkCollection",name="message")
                break'''

            __tasks = []
            for item in __items:
                if self.passed_params.get("limit") > 0 and (__downloaded_count > self.passed_params.get("limit")):
                    break

                item_id = str(item.get("owner_id")) + "_" + str(item.get("id"))

                __extractor_params["item_id"] = item_id
                __extractor_params["__json_info"] = item

                if __has_profile == True:
                    __extractor_params["__json_profiles"] = __time_call.get("profiles")
                    __extractor_params["__json_groups"] = __time_call.get("groups")

                # Я думаю, важен не сам факт сохранения всей информации о закладке,
                # а сам её контент. Так что будут отброшены лишние данные
                if __extract_type == True:
                    __type = item.get("type")
                    __extractor_params["__json_info"] = item.get(__type)

                __task = asyncio.create_task(self._execute_sub(__extractor, copy.deepcopy(__extractor_params), __final_entities))
                __tasks.append(__task)

                #if self.passed_params.get("download_timeout") != 0:
                #    await asyncio.sleep(self.passed_params.get("download_timeout"))

                __downloaded_count += 1

            await asyncio.gather(*__tasks, return_exceptions=False)

            if self.passed_params.get("api_timeout") != 0:
                await asyncio.sleep(self.passed_params.get("api_timeout"))

        #await __extractor.postRun(return_entities=__final_entities)

        return {
            "entities": __final_entities
        }
