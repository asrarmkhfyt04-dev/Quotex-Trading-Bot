[app]
title = Alking
package.name = alking_app
package.domain = org.alking
source.dir = bot          # <- هاد التغيير الوحيد اللي يهم
source.include_exts = py,png,jpg,kv,atlas,env,ttf
version = 1.0.0
requirements = python3,kivy,kivymd,numpy,requests
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 24
android.ndk = 25c
android.sdk = 33
android.build_tools = 33.0.2
android.accept_sdk_license = True
buildozer.use_setup_py = 1

[buildozer]
log_level = 1
warn_on_root = 1
