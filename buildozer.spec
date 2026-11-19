
[app]

# Application information
title = Fahmi Trading App
package.name = fahmiapp
package.domain = org.fahmi

# Source directory
source.dir = .

# Source files included in APK
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt

# Application version
version = 2.0.0

# Python requirements
requirements = python3,kivy,requests

# Application display
orientation = portrait
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android SDK configuration
android.api = 35
android.minapi = 24

# Android NDK
android.ndk = 28c

# Android architecture
android.archs = arm64-v8a

# Python for Android
p4a.branch = develop

# Android application settings
android.allow_backup = True

# Android private storage
android.private_storage = True

# Copy native libraries
android.copy_libs = 1

# Accept SDK license
android.accept_sdk_license = True


[buildozer]

# Buildozer logging
log_level = 2

# Display root warning
warn_on_root = 1
