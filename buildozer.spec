[app]
title = CryptoLiveSimulator
package.name = cryptolivesimulator
package.domain = org.kivy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,otf,csv,json
version = 1.0
requirements = python3,kivy,requests,pandas,ta,arabic_reshaper,bidi
orientation = portrait
fullscreen = 1

# صلاحيات التطبيق: إنترنت + العمل في الخلفية
android.permissions = INTERNET,FOREGROUND_SERVICE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED

# إضافة ملف الخط العربي (تأكد أن الملف في مجلد المشروع)
android.add_asset = AQEEQSANSPRO-Light.otf.ttf

# إظهار أيقونة التطبيق (اختياري)
# icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[python]
# إذا كان هناك ملفات/مجلدات تريد استبعادها
# blacklist = tests,docs

[android]
android.api = 34
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a
android.build_tools_version = 34.0.0

android.allow_backup = 1
android.logcat_filters = *:S python:D

# دعم الواجهة العربية
android.extra_args = --lang=ar

android.entrypoint = org.kivy.android.PythonActivity

# لدعم ملفات البيانات الإضافية
android.include_exts = csv,json

# إضافة ملفات إضافية إن وجدت
# android.add_asset = fonts/

# دعم جميع الشاشات
# android.manifest.intent_filters = 

# لدعم أنواع مكتبات أخرى أو إعدادات إضافية أضف هنا حسب الحاجة
