[Setup]
AppName=Just A Cleaner
UninstallDisplayName=Just A Cleaner
AppVersion=0.1.4
DefaultDirName={autopf}\JustACleaner
DefaultGroupName=Just A Cleaner
UninstallDisplayIcon={app}\JustACleaner.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=JustACleaner_Setup
PrivilegesRequired=admin
SetupIconFile=cleanerlogo.ico

[Files]
Source: "dist\JustACleaner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Just A Cleaner"; Filename: "{app}\JustACleaner.exe"
Name: "{commondesktop}\Just A Cleaner"; Filename: "{app}\JustACleaner.exe"

[Run]
Filename: "{app}\JustACleaner.exe"; Description: "Launch Just A Cleaner"; Flags: nowait postinstall skipifsilent shellexec
