import os
import shutil
import signal
import time
from sys import executable

import psutil
from bot.helper.ext_utils.telegraph_helper import telegraph
from pyrogram import idle
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from bot import IGNORE_PENDING_REQUESTS, app, bot, botStartTime, dispatcher, updater, IS_VPS
from bot.helper.ext_utils import fs_utils
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    LOGGER,
    editMessage,
    sendLogFile,
    sendMessage,
    sendMarkup,
)
from bot.modules import (  # noqa
    authorize,
    cancel_mirror,
    clone,
    delete,
    list,
    mirror,
    mirror_status,
    watch,
    leech_settings,
    speedtest,
    count,
)


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = (
        f"<b>البوت شغال من:</b> {currentTime}\n"
        f"<b>المساحة الكلية:</b> {total}\n"
        f"<b>المستخدم:</b> {used}  "
        f"<b>المتاح:</b> {free}\n\n"
        f"استخدام البيانات\n<b>رفع:</b> {sent}\n"
        f"<b>تنزيل:</b> {recv}\n\n"
        f"<b>البروسيسور:</b> {cpuUsage}% "
        f"<b>الرام:</b> {memory}% "
        f"<b>الذاكرة:</b> {disk}%"
    )
    sendMessage(stats, context.bot, update)

def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("الريبو", "https://github.com/MMETMA/MirrorBot-AR")
    buttons.buildbutton("مالك البوت", "https://t.me/MMETMA")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
البوت ده ممكن يعمل نسخ للروابط علي جوجل درايڤ!
اكتب /{BotCommands.HelpCommand} عشان تشوف كل اوامر البوت
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            'عفوا! انت ليس مصرح لك باستخدام البوت.\nممكن تعمل بوت خاص بيك من الريبو.',
            context.bot,
            update,
            reply_markup,
        )

def restart(update, context):
    restart_message = sendMessage("جار اعادة التشغيل, من فضلك انتظر!", context.bot, update)
    # Save restart message ID and chat ID in order to edit it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f"{end_time - start_time} ms", reply)


def log(update, context):
    sendLogFile(context.bot, update)

def bot_help(update, context):
    help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: عشان يظهرلك الرسالة دي
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [لينك مباشر][Magnet]: رفع الملف علي جوجل درايڤ. ابعت <b>/{BotCommands.MirrorCommand}</b> لمساعدة اكتر.
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.LeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [download_url][magnet_link][torent_file]: Start leeching to Telegram and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent, Use <b>/{BotCommands.QbLeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url][gdtot_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url][gdtot_url]: Count file/folder of Google Drive
<br><br>
<b>/{BotCommands.deleteCommand}</b> [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link. Send <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechSetCommand}</b>: Leech settings
<br><br>
<b>/{BotCommands.SetThumbCommand}</b>: Reply photo to set it as Thumbnail
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all downloading tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: Search in Google Drive(s)
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
'''

    help_string = f'''
/{BotCommands.HelpCommand} عشان يظهرلك الرسالة دي    
/{BotCommands.MirrorCommand} [لينك مباشر][لينك تورنت]: عمل ميرور علي جوجل درايف.
/{BotCommands.ZipMirrorCommand} [لينك مباشر][لينك تورنت]: ضغط الملفات بصيغة zip وعمل ميرور.
/{BotCommands.LeechCommand} [لينك مباشر][لينك تورنت]: رفع الملفات لتليجرام.
/{BotCommands.ZipLeechCommand} [لينك مباشر][لينك تورنت]: ضغط الملفات بصيغة zip ورفعها لتليجرام.
/{BotCommands.WatchCommand} [لينك يوتيوب]: ميرور لينكات اليوتيوب. دوس علي /{BotCommands.WatchCommand} لمساعدة اكتر.
/{BotCommands.TarWatchCommand} [لينك يوتيوب]: ضغط فيديوهات اليوتيوب ورفعها بصيغة tar.
/{BotCommands.LeechTarWatchCommand} [لينك يوتيوب]: رفع فيديو يوتيوب لتليجرام.
/{BotCommands.CloneCommand} [لينك جوجل درايف]: نسخ الملف او الفولدر علي جوجل درايف.
/{BotCommands.CancelMirror}  قم بالرد علي الرسالة اللي بدأت بيها الميرور عشان تلغيه.    
/{BotCommands.UnzipMirrorCommand} [لينك مباشر][لينك تورنت]: فك الضغط وعمل ميرور علي جوجل درايف.
'''
    help = telegraph.create_page(
            title='MMETMA Mirror Help',
            content=help_string_telegraph,
        )["path"]
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("كل الاوامر", f"https://telegra.ph/{help}")
    buttons.buildbutton("مساعدة لاعادة التسمية", "https://telegra.ph/Magneto-Python-Aria---Custom-Filename-Examples-01-20")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    sendMarkup(help_string, context.bot, update, reply_markup)
''''''    



botcmds = [
    (f"{BotCommands.HelpCommand}", "للحصول علي مساعدة تفصيلية"),
    (f"{BotCommands.MirrorCommand}", "عمل ميرور للرابط"),
    (f"{BotCommands.LeechCommand}", "رفع الملفات لتليجرام"),
    (f"{BotCommands.UnzipLeechCommand}", "استخراج الملفات ورفعها لتليجرام"),
    (f"{BotCommands.LeechWatchCommand}", "رفع فيديو يوتيوب لتيليجرام"),
    (f"{BotCommands.LeechZipWatchCommand}", "ضغط قائمة تشغيل يوتيوب ورفعها لتليجرام"),
    (f"{BotCommands.ZipLeechCommand}", "ضغط الملفات ورفعها لتليجرام"),
    (f"{BotCommands.ZipMirrorCommand}", "ضغط الملفات وعمل ميرور"),
    (f"{BotCommands.UnzipMirrorCommand}", "استخراج الملفات وعمل ميرور"),
    (f"{BotCommands.CloneCommand}", "عمل نسخ لروابط درايڤ"),
    (f"{BotCommands.deleteCommand}", "حذف الملف من جوجل درايڤ [للمالك فقط]"),
    (f"{BotCommands.WatchCommand}", "ميرور لروابط يوتيوب"),
    (f"{BotCommands.ZipWatchCommand}", "ضغط قائمة تشغيل يوتيوب وعمل ميرور"),
    (f'{BotCommands.ListCommand}','بحث في جوجل درايڤ'),
    (f"{BotCommands.CancelMirror}", "الغاء عملية"),
    (f"{BotCommands.CancelAllCommand}", "الغاء كل العمليات [للمالك فقط]"),
    (f"{BotCommands.CountCommand}", "عد الملفات في روابط جوجل درايڤ"),
    (f"{BotCommands.StatusCommand}", "الحصول علي حالة عمليات الميرور الحالية"),
    (f"{BotCommands.StatsCommand}", "احصائيات استخدام البوت"),
    (f"{BotCommands.SpeedCommand}", "اختبار سرعة البوت"),
]


def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.new_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("تم اعادة التشغيل بنجاح!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(
        BotCommands.StartCommand,
        start,
        run_async=True,
    )
    ping_handler = CommandHandler(
        BotCommands.PingCommand,
        ping,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    restart_handler = CommandHandler(
        BotCommands.RestartCommand,
        restart,
        filters=CustomFilters.owner_filter | CustomFilters.sudo_user,
        run_async=True,
    )
    help_handler = CommandHandler(
        BotCommands.HelpCommand,
        bot_help,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    stats_handler = CommandHandler(
        BotCommands.StatsCommand,
        stats,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    log_handler = CommandHandler(
        BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True
    )
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)


app.start()
main()
idle()
