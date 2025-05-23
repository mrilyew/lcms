from executables.thumbnail.Base import BaseThumbnail
from resources.Globals import math, config, utils, os
from PIL import Image
from moviepy import VideoFileClip

class TVideo(BaseThumbnail):
    name = 'TVideo'
    accept = ["mp4", "mov"]

    def run(self, file, params={}):
        size = (config.get("thumbnail.width"), config.get("thumbnail.height"))
        __previews = {
            "photo": []
        }

        path = file.getPath()
        if params.get("preview_file"):
            path = params.get("preview_file")
        
        with VideoFileClip(path) as video:
            duration = video.duration
            frag_len = (duration / 10)

            for i in range(0, 10):
                __hash = utils.getRandomHash(8)
                __new_prev = os.path.join(self.save_dir, f"{__hash}_thumb_{i}.jpg")
                __previews["photo"].append({
                    "path": f"{__hash}_thumb_{i}.jpg",
                    "width": config.get("thumbnail.width"),
                    "height": config.get("thumbnail.height")
                })
                
                i_duration = i * frag_len

                frame = video.get_frame(i_duration)
                img = Image.fromarray(frame)
                img.thumbnail(size, Image.LANCZOS)
                new_img = Image.new('RGB', size, (0, 0, 0))
                new_img.paste(
                    img,
                    ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
                )
                new_img.save(__new_prev)
        
        return __previews
