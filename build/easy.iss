; One-click per-user extraction and launch. No elevation or setup wizard.
#ifndef AppVersion
  #error AppVersion must come from app/version.py
#endif
[Setup]
AppId=MediaDownloaderEasy
AppName=Media Downloader
AppVersion={#AppVersion}
AppPublisher=Media Downloader Contributors
DefaultDirName={localappdata}\MediaDownloader-Easy
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19045
OutputDir=..\dist\release
OutputBaseFilename=MediaDownloader-Easy-Windows-x64
SetupIconFile=app.ico
Compression=lzma2
SolidCompression=yes
Uninstallable=no
CreateAppDir=yes
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
DisableFinishedPage=yes
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#WindowsVersion}
[Languages]
Name: "zh"; MessagesFile: "ChineseSimplified.isl"
[Files]
Source: "..\dist\MediaDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "easy-defaults.json"; DestDir: "{localappdata}\MediaDownloader\config"; DestName: "app_settings.json"; Flags: onlyifdoesntexist uninsneveruninstall
[Run]
Filename: "{app}\MediaDownloader.exe"; Flags: nowait runasoriginaluser
[Code]
function InitializeSetup(): Boolean;
var
  ExitCode: Integer;
begin
  if WizardSilent then
    Result := True
  else begin
    Result := False;
    if FileExists(ExpandConstant('{localappdata}\MediaDownloader-Easy\MediaDownloader.exe')) then begin
      if not Exec(ExpandConstant('{localappdata}\MediaDownloader-Easy\MediaDownloader.exe'), '', '', SW_SHOWNORMAL, ewNoWait, ExitCode) then
        MsgBox('无法启动，请把文件保存到电脑后重新双击。', mbError, MB_OK);
    end else if not Exec(ExpandConstant('{srcexe}'), '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
      MsgBox('无法启动，请把文件保存到电脑后重新双击。', mbError, MB_OK);
  end;
end;
