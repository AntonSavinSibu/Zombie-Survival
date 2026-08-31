[app]

# (str) Title of your application
title = Zombie Survival

# (str) Package name
package.name = zombiesurvival

# (str) Package domain (needed for android/ios packaging)
package.domain = com.antonsavinsibu

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,zip,wav,ogg,mp3,ttf,json

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,pygame

# (str) Supported orientation
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) The entry point of your application
entrypoint = zombie.py

# Android specific
android.api = 34
android.minapi = 23
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.build_tools_version = 34.0.0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
