[app]
title = Zombie Survival
package.name = zombiesurvival
package.domain = com.antonsavinsibu
source.dir = .
source.include_exts = py,png,jpg,jpeg,zip,wav,ogg,mp3,ttf,json
version = 1.0.0

entrypoint = main.py
requirements = python3,pygame,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,pillow

orientation = landscape
fullscreen = 1

android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.build_tools_version = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 0
