#!/bin/sh
# Builds "SQL Reference Finder.app" (needs Xcode command line tools: swiftc). Run from this folder.
set -e
cd "$(dirname "$0")"
APP="SQL Reference Finder.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/site"
swiftc -O app/main.swift -o "$APP/Contents/MacOS/SQLFinder" -framework Cocoa -framework WebKit
cp -R index.html css js "$APP/Contents/Resources/site/"
cat > "$APP/Contents/Info.plist" <<P
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>CFBundleName</key><string>SQL Reference Finder</string><key>CFBundleIdentifier</key><string>local.sqlfinder</string>
<key>CFBundleExecutable</key><string>SQLFinder</string><key>CFBundlePackageType</key><string>APPL</string><key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>11.0</string><key>NSHighResolutionCapable</key><true/></dict></plist>
P
codesign --force --sign - "$APP" >/dev/null 2>&1 || true
echo "built: $APP"
