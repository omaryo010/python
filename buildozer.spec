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
android.permissions = INTERNET,FOREGROUND_SERVICE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED
android.add_asset = AQEEQSANSPRO-Light.otf.ttf

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 30
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a
android.build_tools_version = 33.0.0
android.allow_backup = 1
android.logcat_filters = *:S python:D
android.extra_args = --lang=ar
android.entrypoint = org.kivy.android.PythonActivity
android.include_exts = csv,json
android.sdk_path = $HOME/android-sdk
