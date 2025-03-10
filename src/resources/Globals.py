# Python preinstalled / pip libs
import operator
import time
import traceback
import threading
import platform
import os
import win32api
import win32file
import json
import sys
import random
import yt_dlp
import shutil
import requests
import mimetypes
import importlib
import json5
import math
import wget
import zipfile
import asyncio
import aiohttp
import secrets
import copy
from fake_useragent import UserAgent as FakeUserAgent
from PIL import Image, ImageOps
from moviepy import VideoFileClip
from playhouse.shortcuts import model_to_dict
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from urllib.parse import urlparse
from urllib.parse import urlencode
from pathlib import Path
from datetime import datetime
from functools import reduce
from contextlib import contextmanager

# Internal classes

loop = asyncio.get_event_loop()

from resources.Exceptions import ApiException
from resources.Consts import consts
from submodules.Config import config
from submodules.Logger import logger
from submodules.FileManager import file_manager 
from submodules.Utils import utils
from submodules.HTMLFormatter import HTMLFormatter
from core.DownloadManager import download_manager
from resources.AssetsCacheStorage import assets_cache_storage
from submodules.WebCrawler import Crawler
from submodules.web_services.VkApi import VkApi
from db.BaseModel import db, BaseModel
from core.Response.ExecuteResponse import ExecuteResponse
from core.Storage import storage

# Repos

from repositories.Extractors import Extractors as ExtractorsRepository
from repositories.Thumbnails import Thumbnails as ThumbnailsRepository
from repositories.Acts import Acts as ActsRepository
from repositories.Services import Services as ServicesRepository
