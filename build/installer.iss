#ifndef AppVersion
  #error AppVersion must come from app/version.py
#endif
#ifndef ProductName
  #error ProductName must come from app/version.py
#endif
[Setup]
AppId={{97D1CD48-54D0-4951-A662-9C62AA1A789B}
AppName={#ProductName}
AppVersion={#AppVersion}
AppPublisher={#ProductPublisher}
DefaultDirName={autopf}\MediaDownloader
DefaultGroupName={#ProductName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19045
OutputDir=..\dist\release
OutputBaseFilename=MediaDownloader-Setup
SetupIconFile=app.ico
UninstallDisplayIcon={app}\MediaDownloader.exe
Compression=lzma2
SolidCompression=yes
LicenseFile=..\LICENSE
VersionInfoVersion={#WindowsVersion}
VersionInfoDescription={#ProductName} Setup
VersionInfoProductName={#ProductName}
VersionInfoProductVersion={#WindowsVersion}
VersionInfoProductTextVersion={#AppVersion}
DisableProgramGroupPage=yes
[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "zh"; MessagesFile: "ChineseSimplified.isl"
[CustomMessages]
en.DesktopIcon=Create a desktop shortcut
zh.DesktopIcon=创建桌面快捷方式
en.LaunchApp=Launch Media Downloader
zh.LaunchApp=启动 Media Downloader
[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIcon}"; Flags: unchecked
[Files]
Source: "..\dist\MediaDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{autoprograms}\{#ProductName}"; Filename: "{app}\MediaDownloader.exe"
Name: "{autodesktop}\{#ProductName}"; Filename: "{app}\MediaDownloader.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\MediaDownloader.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent
; No user-data/download deletion, PATH edits, proxy settings, browser changes or telemetry.
