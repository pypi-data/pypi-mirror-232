import asyncio
import random
import re
from contextlib import suppress
from math import ceil
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    NoReturn,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)

from nonebot import logger, on_command, on_regex
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.internal.matcher import (
    Matcher,
    current_bot,
    current_event,
    current_matcher,
)
from nonebot.params import ArgPlainText, CommandArg
from nonebot.rule import Rule
from nonebot.typing import T_RuleChecker, T_State

from .config import config
from .data_source import (
    get_track_audio,
    get_track_info,
    get_track_lrc,
    get_voice_info,
    search_song,
    search_voice,
)
from .draw import draw_search_res, str_to_pic
from .msg_cache import (
    CALLING_MAP,
    SongCache,
    SongType,
    chat_last_song_cache,
    song_msg_id_cache,
)
from .types import (
    SearchResult,
    Song,
    SongInfo,
    SongSearchResult,
    VoiceBaseInfo,
    VoiceResource,
)
from .utils import format_alias, format_artists, format_lrc

LIST_MSG_ID_KEY = "list_msg_id"
SONG_CACHE_KEY = "song_cache"
CHECK_REPLY_KEY = "check_reply"
SEARCH_PARAM_KEY = "param"
SEARCH_CACHE_KEY = "cache"
SONG_TYPE_KEY = "type"
CURRENT_PAGE_KEY = "page"
MAX_PAGE_KEY = "page_max"
TIP_USER_KEY = "tip_user"

EXIT_COMMAND = ("退出", "tc", "取消", "qx", "quit", "q", "exit", "e", "cancel", "c", "0")
PREVIOUS_COMMAND = ("上一页", "syy", "previous", "p")
NEXT_COMMAND = ("下一页", "xyy", "next", "n")

LINK_TYPE_MAP: Dict[SongType, Tuple[str, ...]] = {
    "song": ("song", "url"),
    "voice": ("dj", "program"),
}

link_types: List[str] = []
[link_types.extend(x) for x in LINK_TYPE_MAP.values()]
link_type_reg = "|".join(link_types)

SONG_ID_REGEX = (
    rf"music\.163\.com(.*?)(?P<type>{link_type_reg})/?\?id=(?P<id>[0-9]+)(|&)"
)


async def cache_music_msg_rule(event: MessageEvent, state: T_State) -> bool:
    if reply := event.reply:
        song_cache = song_msg_id_cache.get(reply.message_id)
        if song_cache:
            state[SONG_CACHE_KEY] = song_cache
            return True

    return False


def get_type_from_url_type(type_name: str) -> SongType:
    type_name = type_name.lower()
    for k, v in LINK_TYPE_MAP.items():
        if type_name in v:
            return cast(Any, k)
    raise ValueError(f"invalid type {type_name}")


async def msg_or_reply_music_rule(event: MessageEvent, state: T_State) -> bool:
    check_reply: bool = state.get(CHECK_REPLY_KEY, True)
    message = event.reply.message if (check_reply and event.reply) else event.message

    res = re.search(SONG_ID_REGEX, str(message))
    if res:
        type_name = None
        with suppress(ValueError):
            type_name = get_type_from_url_type(res["type"])

        if type_name:
            state[SONG_CACHE_KEY] = SongCache(id=int(res["id"]), type=type_name)
            return True

    return False


async def chat_last_music_rule(event: MessageEvent, state: T_State) -> bool:
    if song_cache := chat_last_song_cache.get(event.get_session_id()):
        state[SONG_CACHE_KEY] = song_cache
        return True

    return False


async def auto_resolve_rule():
    return config.ncm_auto_resolve


def any_rule(*rules: Union[T_RuleChecker, Rule]) -> Callable[..., Awaitable[bool]]:
    async def rule(bot: Bot, event: Event, state: T_State):
        # 要按顺序执行，所以不能用 asyncio.gather
        for x in rules:  # noqa: SIM110
            if await Rule(x)(bot, event, state):
                return True
        return False

    return rule


music_msg_matcher_rule = any_rule(
    cache_music_msg_rule,
    msg_or_reply_music_rule,
    chat_last_music_rule,
)


async def delete_list_msg(msg_id: List[int], bot: Bot):
    if not (config.ncm_delete_list_msg and msg_id):
        return

    for i in msg_id:
        await asyncio.sleep(random.uniform(*config.ncm_delete_list_msg_delay))
        try:
            await bot.delete_msg(message_id=i)
        except Exception as e:
            logger.warning(f"撤回消息 {msg_id} 失败: {e!r}")


async def finish_with_delete_msg(
    msg: Optional[Union[str, MessageSegment, Message]] = None,
) -> NoReturn:
    bot = cast(Bot, current_bot.get())
    matcher = current_matcher.get()
    msg_id = current_matcher.get().state.get(LIST_MSG_ID_KEY)

    if msg_id:
        asyncio.create_task(delete_list_msg(msg_id, bot))

    await matcher.finish(msg)


async def send_music(song: SongInfo):
    matcher = current_matcher.get()

    is_song = isinstance(song, Song)
    calling = CALLING_MAP["song" if is_song else "voice"]
    song_id = song.id if is_song else song.mainTrackId
    bitrate = 999999
    # 管你妈那么多闲事干嘛，直接上最高就得了
    # bitrate = (
    #     song.privilege.pl if is_song and song.privilege.plLevel else None
    # ) or 999999

    try:
        audio_info = await get_track_audio([song_id], bitrate)
    except Exception:
        logger.exception(f"获取{calling}播放链接失败")
        await finish_with_delete_msg(f"获取{calling}播放链接失败，请检查后台输出")

    if not audio_info:
        await finish_with_delete_msg(f"抱歉，没有获取到{calling}播放链接")

    info = audio_info[0]
    seg = MessageSegment(
        "music",
        {
            "type": "custom",
            "subtype": "163",
            "url": info.url,
            "voice": info.url,
            "title": format_alias(song.name, song.alia) if is_song else song.name,
            "content": format_artists(song.ar) if is_song else song.radio.name,
            "image": song.al.picUrl if is_song else song.coverUrl,
        },
    )

    try:
        ret: Dict[str, Any] = await matcher.send(seg)
    except Exception as e:
        logger.warning(f"发送{calling}卡片失败：{e!r}")
        # await finish_with_delete_msg(f"发送{calling}卡片失败")

    song_cache = SongCache(id=song.id, type="song" if is_song else "voice")
    event = cast(MessageEvent, current_event.get())

    chat_last_song_cache[event.get_session_id()] = song_cache
    if msg_id := ret.get("message_id"):
        song_msg_id_cache[msg_id] = song_cache

    await finish_with_delete_msg()


async def get_cache_by_index(
    cache: Dict[int, SearchResult],
    arg: int,
) -> Optional[SongInfo]:
    ori_index = arg - 1
    page_index = ceil(ori_index / config.ncm_list_limit)
    page_index = 1 if page_index == 0 else page_index
    index = ori_index % config.ncm_list_limit

    res = cache.get(page_index)
    if not (res):
        return None

    results = res.songs if isinstance(res, SongSearchResult) else res.resources
    if (not results) or (not (0 <= index < len(results))):
        return None

    got = results[index]
    if isinstance(got, VoiceResource):
        return got.baseInfo
    return got


async def get_page(page: int = 1) -> MessageSegment:
    matcher = current_matcher.get()
    state = matcher.state

    param: str = state[SEARCH_PARAM_KEY]
    cache: Dict[int, SearchResult] = state[SEARCH_CACHE_KEY]
    song_type: SongType = state[SONG_TYPE_KEY]
    calling = CALLING_MAP[song_type]

    if not (res := cache.get(page)):
        func = search_song if song_type == "song" else search_voice
        try:
            res = await func(param, page=page)
        except Exception:
            logger.exception(f"搜索{calling}失败")
            await finish_with_delete_msg(f"搜索{calling}失败，请检查后台输出")

    is_song = isinstance(res, SongSearchResult)
    total_count = res.songCount if is_song else res.totalCount
    results = res.songs if is_song else res.resources
    if not results:
        await finish_with_delete_msg(f"没搜到任何{calling}捏")

    state[CURRENT_PAGE_KEY] = page
    cache[page] = res
    state[MAX_PAGE_KEY] = ceil(total_count / config.ncm_list_limit)

    if page == 1 and len(results) == 1:
        await get_cache_by_index(cache, 1)

    try:
        pic = await draw_search_res(res, page)
    except Exception:
        logger.exception(f"绘制{calling}列表失败")
        await finish_with_delete_msg(f"绘制{calling}列表失败，请检查后台输出")

    return MessageSegment.image(pic)


async def send_page(page: int = 1, reject: bool = False, pause: bool = False):
    matcher = current_matcher.get()
    state = matcher.state

    resp = await matcher.send(await get_page(page))
    msg_id = resp.get("message_id")

    if LIST_MSG_ID_KEY not in state:
        state[LIST_MSG_ID_KEY] = []

    if msg_id:
        state[LIST_MSG_ID_KEY].append(msg_id)

    if reject:
        await matcher.reject()
    elif pause:
        await matcher.pause()


@overload
async def get_song_info(song_id: int, song_type: Literal["song"]) -> Optional[Song]:
    ...


@overload
async def get_song_info(
    song_id: int,
    song_type: Literal["voice"],
) -> Optional[VoiceBaseInfo]:
    ...


async def get_song_info(song_id, song_type):
    if song_type == "voice":
        return await get_voice_info(song_id)

    song = await get_track_info([song_id])
    return song[0] if song else None


cmd_pick_song = on_command(
    "点歌",
    aliases={"网易云", "wyy"},
    state={SONG_TYPE_KEY: "song"},
)
cmd_pick_voice = on_command(
    "电台",
    aliases={"声音", "网易电台", "wydt", "wydj"},
    state={SONG_TYPE_KEY: "voice"},
)


@cmd_pick_song.handle()
@cmd_pick_voice.handle()
async def _(matcher: Matcher, arg_msg: Message = CommandArg()):
    if arg_msg.extract_plain_text().strip():
        matcher.set_arg("arg", arg_msg)


@cmd_pick_song.got("arg", "请发送搜索内容")
@cmd_pick_voice.got("arg", "请发送搜索内容")
async def _(matcher: Matcher, state: T_State, arg: str = ArgPlainText("arg")):
    song_type: SongType = state[SONG_TYPE_KEY]
    calling = CALLING_MAP[song_type]

    param = arg.strip()
    if not param:
        await matcher.finish("消息无文本，放弃点播")

    if param.isdigit():
        song = None
        with suppress(Exception):
            song = await get_song_info(int(param), song_type)
        if song:
            await matcher.send(f"检测到输入了{calling} ID，将直接获取并发送对应{calling}")
            await send_music(song)

    state[SEARCH_PARAM_KEY] = param
    state[CURRENT_PAGE_KEY] = 1
    state[SEARCH_CACHE_KEY] = {}
    await send_page(pause=True)


@cmd_pick_song.handle()
@cmd_pick_voice.handle()
async def _(matcher: Matcher, state: T_State, event: MessageEvent):
    arg = event.get_message().extract_plain_text().strip().lower()
    page: int = state[CURRENT_PAGE_KEY]
    page_max: int = state[MAX_PAGE_KEY]

    if arg in EXIT_COMMAND:
        await finish_with_delete_msg("已退出选择")

    if arg in PREVIOUS_COMMAND:
        if page <= 1:
            await matcher.reject("已经是第一页了")
        await send_page(page - 1, reject=True)

    if arg in NEXT_COMMAND:
        if page >= page_max:
            await matcher.reject("已经是最后一页了")
        await send_page(page + 1, reject=True)

    if arg.isdigit():
        cache: Dict[int, SearchResult] = state[SEARCH_CACHE_KEY]
        song = await get_cache_by_index(cache, int(arg))
        if not song:
            await matcher.reject("序号输入有误，请重新输入")
        await send_music(song)

    if config.ncm_illegal_cmd_finish:
        await finish_with_delete_msg("非正确指令，已退出点歌")

    await matcher.reject("非正确指令，请重新输入\nTip: 你可以发送 `退出` 来退出点歌模式")


cmd_get_song = on_command(
    "解析",
    aliases={"resolve", "parse", "get"},
    rule=music_msg_matcher_rule,
)
reg_song_url = on_regex(
    SONG_ID_REGEX,
    rule=Rule(auto_resolve_rule) & msg_or_reply_music_rule,
    state={CHECK_REPLY_KEY: False, TIP_USER_KEY: True},
)


@cmd_get_song.handle()
@reg_song_url.handle()
async def _(matcher: Matcher, state: T_State):
    song_cache: SongCache = state[SONG_CACHE_KEY]
    calling = CALLING_MAP[song_cache.type]

    tip_user = state.get(TIP_USER_KEY, False)
    if tip_user:
        await matcher.send("检测到您发送了网易云音乐卡片/链接，正在为您解析播放链接")

    try:
        if song_cache.type == "voice":
            song = await get_voice_info(song_cache.id)
        else:
            song = await get_track_info([song_cache.id])
            song = song[0] if song else None
    except Exception:
        logger.exception(f"获取{calling}信息失败")
        await matcher.finish(f"获取{calling}信息失败，请检查后台输出")

    if not song:
        await matcher.finish(f"未获取到对应{calling}信息")

    await send_music(song)


cmd_get_lrc = on_command(
    "歌词",
    aliases={"lrc", "lyric", "lyrics"},
    rule=music_msg_matcher_rule,
)


@cmd_get_lrc.handle()
async def _(matcher: Matcher, state: T_State):
    song_cache: SongCache = state[SONG_CACHE_KEY]

    if song_cache.type == "voice":
        await matcher.finish("电台节目无法获取歌词")

    song_id = song_cache.id
    try:
        lrc_data = await get_track_lrc(song_id)
    except Exception:
        logger.exception("获取歌曲歌词失败")
        await matcher.finish("获取歌曲歌词失败，请检查后台输出")

    lrc = format_lrc(lrc_data)
    if not lrc:
        await matcher.finish("该歌曲没有歌词")

    await matcher.finish(MessageSegment.image(await str_to_pic(lrc)))


cmd_get_cache_link = on_command(
    "链接",
    aliases={"link", "url"},
    rule=music_msg_matcher_rule,
)


@cmd_get_cache_link.handle()
async def _(matcher: Matcher, state: T_State):
    song_cache: SongCache = state[SONG_CACHE_KEY]
    song_id = song_cache.id

    link_type = "dj" if song_cache.type == "voice" else song_cache.type
    await matcher.finish(f"https://music.163.com/{link_type}?id={song_id}")
