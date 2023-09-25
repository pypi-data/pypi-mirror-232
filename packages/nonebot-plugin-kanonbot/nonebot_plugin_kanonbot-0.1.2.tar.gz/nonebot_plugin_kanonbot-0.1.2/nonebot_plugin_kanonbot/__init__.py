# coding=utf-8
from nonebot.plugin import PluginMetadata
import nonebot
import os
import re
import sqlite3
from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    Event,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER
)
import time
from .config import kn_config, command_list
from .bot_run import botrun
from .tools import get_file_path, get_command

config = nonebot.get_driver().config
# 读取配置
# -》无需修改代码文件，请在“.env”文件中改。《-
#
# 配置1：
# 管理员账号SUPERUSERS
# 需要添加管理员权限，参考如下：
# SUPERUSERS=["12345678"]
#
# 配置2：
# 文件存放目录
# 该目录是存放插件数据的目录，参考如下：
# bilipush_basepath="./"
# bilipush_basepath="C:/"
#
# 配置3：
# 读取自定义的命令前缀
# COMMAND_START=["/", ""]
#

# 配置1
try:
    adminqq = config.superusers
    adminqq = list(adminqq)
except Exception as e:
    adminqq = []
# 配置2：
try:
    basepath = config.kanonbot_basepath
    if "\\" in basepath:
        basepath = basepath.replace("\\", "/")
    if basepath.startswith("./"):
        basepath = os.path.abspath('.') + basepath.removeprefix(".")
        if not basepath.endswith("/"):
            basepath += "/"
    else:
        if not basepath.endswith("/"):
            basepath += "/"
except Exception as e:
    basepath = os.path.abspath('.') + "/KanonBot/"
# 配置3：
try:
    command_starts = config.COMMAND_START
except Exception as e:
    command_starts = ["/"]

# 插件元信息，让nonebot读取到这个插件是干嘛的
__plugin_meta__ = PluginMetadata(
    name="KanonBot",
    description="KanonBot for Nonebot2",
    usage="/help",
    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。
    homepage="https://github.com/SuperGuGuGu/nonebot_plugin_kanonbot",
    # 发布必填。
    supported_adapters={"~onebot.v11"},
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件可以保证兼容所有适配器（即仅使用基本适配器功能）可不填写，否则应该列出插件支持的适配器。
)

# 初始化文件
if not os.path.exists(basepath):
    os.makedirs(basepath)
cache_path = basepath + "cache/"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
cache_path = basepath + "file/"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

# 创建基础参数
returnpath = ""
plugin_dbpath = basepath + 'db/'
if not os.path.exists(plugin_dbpath):
    os.makedirs(plugin_dbpath)

run_kanon = on_message(priority=10, block=False)


@run_kanon.handle()
async def kanon(event: Event, bot: Bot):
    # 获取消息基础信息
    botid = str(bot.self_id)
    atmsg = event.get_message()["at"]
    atmsgs = []
    if len(atmsg) >= 1:
        for i in atmsg:
            atmsgg = str(i.data["qq"])
            atmsgg.removeprefix('[CQ:at,qq=')
            atmsgg.removesuffix(']')
            atmsgs.append(atmsgg)
    msg = str(event.get_message())
    qq = event.get_user_id()
    timelong = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    msg = re.sub(u"\\[.*?]", "", msg)
    msg = msg.replace('"', "'")
    commands = get_command(msg)
    command = commands[0]
    now = int(time.time())

    # ## 心跳服务相关 ##
    if kn_config("botswift-state"):
        botswift_db = f"{basepath}db/botswift.db"
        conn = sqlite3.connect(botswift_db)
        cursor = conn.cursor()
        # 检查表格是否存在，未存在则创建
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
        datas = cursor.fetchall()
        tables = []
        for data in datas:
            if data[1] != "sqlite_sequence":
                tables.append(data[1])
        if "heart" not in tables:
            cursor.execute(f'create table "heart"'
                           f'("botid" VARCHAR(10) primary key, times VARCHAR(10), hearttime VARCHAR(10))')
        # 读取bot名单
        cursor.execute(f'select * from heart')
        datas = cursor.fetchall()
        bots_list = []
        for data in datas:
            bots_list.append(data[0])
        # 如果发消息的用户为bot，则刷新心跳
        if qq in bots_list:
            cursor.execute(f'SELECT * FROM heart WHERE "botid" = "{qq}"')
            data = cursor.fetchone()
            cache_times = int(data[1])
            cache_hearttime = int(data[2])
            cursor.execute(f'replace into heart("botid", "times", "hearttime") '
                           f'values("{qq}", "0", "{now}")')
            conn.commit()
        cursor.close()
        conn.close()

    # 判断是否响应
    commandname = ""
    commandlist = command_list()
    run = False
    # 识别精准
    if not run:
        cache_commandlist = commandlist["精准"]
        if command in list(cache_commandlist):
            commandname = cache_commandlist[command]
            run = True
    # 识别emoji
    if not run:
        path = f"{basepath}file/emoji.db"
        if os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute(f'select * from emoji where emoji = "{command}"')
            data = cursor.fetchone()
            cursor.close()
            conn.close()
            if data is not None:
                run = True
                commandname = "群聊功能-emoji"
    # 识别开头
    if not run:
        cache_commandlist = commandlist["开头"]
        for cache_command in list(cache_commandlist):
            if command.startswith(cache_command):
                commandname = cache_commandlist[cache_command]
                run = True
                break
    # 识别结尾
    if not run:
        cache_commandlist = commandlist["结尾"]
        for cache_command in list(cache_commandlist):
            if command.endswith(cache_command):
                commandname = cache_commandlist[cache_command]
                run = True
                break
    # 识别模糊
    if not run:
        cache_commandlist = commandlist["模糊"]
        for cache_command in list(cache_commandlist):
            if cache_command in command:
                commandname = cache_commandlist[command]
                run = True
                break
    # 识别精准2
    if not run:
        cache_commandlist = commandlist["精准2"]
        if command in list(cache_commandlist):
            commandname = cache_commandlist[command]
            run = True
    if not run and kn_config(""):
        conn = sqlite3.connect(await get_file_path("emoji_1.db"))
        cursor = conn.cursor()
        cursor.execute(f'select * from emoji where emoji = "{command}"')
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        if data is not None:
            commandname = "emoji"
            run = True

    # 排除部分相应词
    if run:
        if commandname == 'caicaikan':
            if len(command) >= 7:
                run = False
        if commandname == 'blowplane':
            if len(command) >= 7:
                run = False
        if commandname == "亲亲" or \
                commandname == "可爱" or \
                commandname == "咬咬" or \
                commandname == "摸摸" or \
                commandname == "贴贴" or \
                commandname == "逮捕":
            if len(command) >= 7:
                run = False
    # 开始处理消息
    if run:
        # 创建变量内容
        code = 0
        dbpath = basepath + "db/"
        configdb = dbpath + 'config.db'
        autoreplydb = dbpath + 'autoreply.db'
        userdatas_db = dbpath + "userdatas.db"

        # 获取消息内容
        allfriendlist = []
        allgroupmember_data = []
        if isinstance(event, GroupMessageEvent):
            # 群消息
            groupcode = str(event.group_id)
            commandname_list = ["jinrilaopo", "jiehun", "keai", "welcome"]
            if commandname in commandname_list:
                allgroupmember_data = await bot.get_group_member_list(group_id=int(groupcode))
            # 获取用户权限
            if await GROUP_ADMIN(bot, event):
                info_premission = '5'  # 管理员
            elif await GROUP_OWNER(bot, event):
                info_premission = '10'  # 群主
            else:
                info_premission = '0'  # 群员
            # 如果群聊内at机器人，则添加at信息。
            if event.is_tome():
                atmsgs.append(botid)
        else:
            # 私聊
            groupcode = 'p' + str(event.get_user_id())
            info_premission = '10'
        groupcode = 'g' + groupcode
        # 获取消息包含的图片
        imgmsgmsg = event.get_message()["image"]
        imgmsgs = []
        if len(imgmsgmsg) >= 1:
            for i in imgmsgmsg:
                imgmsgg = str(i.data["url"])
                imgmsgs.append(imgmsgg)
        else:
            imgmsgs = []

        # 组装信息，进行后续响应
        msg_info = {
            "msg": msg,
            "commands": commands,
            "atmsgs": atmsgs,
            "info_premission": info_premission,
            "commandname": commandname,
            "groupcode": groupcode,
            "qq": qq,
            "imgmsgs": imgmsgs
        }
        logger.info(msg_info)
        data = await botrun(bot, allfriendlist, allgroupmember_data, msg_info)
        logger.info(data)
        # 获取返回信息，进行回复
        code = int(data["code"])
        message = data["message"]
        imgpath = data["returnpath"]
        imgpath2 = data["returnpath2"]
        imgpath3 = data["returnpath3"]
        at = data["at"]

        # 排除部分无效内容
        if code == 1:
            if message is None or message == "":
                code = 0
                logger.error("空消息")
                logger.error(data)
        elif code == 2:
            if not os.path.exists(imgpath):
                code = 0
                logger.error("空图片")
                logger.error(data)
        elif code == 3:
            if message is None or message == "" or not os.path.exists(imgpath):
                code = 0
                logger.error("空消息或图片")
                logger.error(data)
        elif code == 4:
            if (
                    message is None or
                    message == "" or
                    not os.path.exists(imgpath) or
                    not os.path.exists(imgpath2)
            ):
                code = 0
                logger.error("空消息或图片")
                logger.error(data)
        elif code == 5:
            if (
                    message is None or
                    message == "" or
                    not os.path.exists(imgpath) or
                    not os.path.exists(imgpath2) or
                    not os.path.exists(imgpath3)
            ):
                code = 0
                logger.error("空消息或图片")
                logger.error(data)

        # 开始返回消息
        if code == 0:
            pass
        elif code == 1:
            msg = MessageSegment.text(message)
            if at is not False:
                msgat = MessageSegment.at(at)
                msgn = MessageSegment.text('\n')
                msg = msgat + msgn + msg
            await run_kanon.finish(msg)
        elif code == 2:
            msg = MessageSegment.image(r"file:///" + imgpath)
            if at is not False:
                msgat = MessageSegment.at(at)
                msg = msgat + msg
            await run_kanon.finish(msg)
        elif code == 3:
            msg1 = MessageSegment.text(message)
            msg2 = MessageSegment.image(r"file:///" + imgpath)
            if at is not False:
                msgat = MessageSegment.at(at)
                msgn = MessageSegment.text('\n')
                msg = msgat + msgn + msg1 + msg2
            else:
                msg = msg1 + msg2
            await run_kanon.finish(msg)
        elif code == 4:
            msg0 = MessageSegment.text(message)
            msg1 = MessageSegment.image(r"file:///" + imgpath)
            msg2 = MessageSegment.image(r"file:///" + imgpath2)
            msg = msg0 + msg1 + msg2
            await run_kanon.finish(msg)
        elif code == 5:
            msg0 = MessageSegment.text(message)
            msg1 = MessageSegment.image(r"file:///" + imgpath)
            msg2 = MessageSegment.image(r"file:///" + imgpath2)
            msg3 = MessageSegment.image(r"file:///" + imgpath3)
            msg = msg0 + msg1 + msg2 + msg3
            await run_kanon.finish(msg)
        else:
            pass
    await run_kanon.finish()
