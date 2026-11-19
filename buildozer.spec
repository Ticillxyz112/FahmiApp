[app]

# Application information
title = Fahmi Trading App
package.name = fahmiapp
package.domain = org.fahmi
version = 2.0.1

# Source directory
source.dir = .

# Include Python and application resources
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
source.include_patterns = *.py,*.kv

# Exclude unnecessary directories
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,env

# Python requirements
requirements = python3,kivy,requests

# Application settings
orientation = portrait
fullscreen = 0

# Android settings
android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a

# Python-for-Android
p4a.branch = develop

# Storage and compatibility
android.allow_backup = True
android.private_storage = True
android.copy_libs = 1
android.accept_sdk_license = True

# Build settings
[buildozer]
log_level = 2
warn_on_root = 1
