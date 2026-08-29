[app]

title = Zombie Survival
package.name = zombiesurvival
package.domain = com.antonsavinsibu

source.dir = .
source.include_exts = py,png,jpg,jpeg,zip,wav,ogg,mp3,ttf,json

entrypoint = zombie_mobile.py

version = 1.0.0

requirements = python3,pygame

orientation = landscape

fullscreen = 1

android.api = 35
android.minapi = 23
android.archs = arm64-v8a

android.permissions = INTERNET

[buildozer]

log_level = 2
warn_on_root = 1
