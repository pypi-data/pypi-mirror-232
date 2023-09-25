from log_translate.business.AndroidCrashPattern_translator import CrashPatternTranslator
from log_translate.business.bluetooth_translator import BluetoothTranslator
from log_translate.data_struct import Log, Level
from log_translate.globals import remember_dict
import globals
from log_translate.log_translator import SysLogTranslator

remember_dict["packages"] = ["com.heytap.health.international", "com.heytap.health:transport",
                             "com.example.myapplication"]
translators = [SysLogTranslator(tag_translators=[BluetoothTranslator(), CrashPatternTranslator()])]


# def louwang(pid, tag, msg):
#     return Log(translated=f"漏网之鱼 {msg} ", level=Level.w)
#
#
# globals.lou_wang_zhi_yu = louwang
