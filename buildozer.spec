[app]
# (str) Title of your application
title = Alking

# (str) Package name
package.name = alking_app

# (str) Package domain (needed for android packaging)
package.domain = org.alking

# (str) Source code where the main.py lives
source.dir = bot

# (list) Source files to include (let's include all python and env files)
source.include_exts = py,png,jpg,kv,atlas,env

# (str) Application version
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,kivymd,selenium,undetected-chromedriver,pandas,pandas-ta,requests,python-dotenv,numpy

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25c

# (str) Android Build Tools version
android.build_tools = 33.0.2

# (bool) Accept Android SDK license
android.accept_sdk_license = True

# (bool) Use setup.py check
buildozer.use_setup_py = 1

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
