#define AppName "Study Coach"
#define AppVersion "0.4.0"
[Setup]
AppId={{F2EE559C-A3A9-43B3-A8EC-1C543AFF04AE}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Study Coach Community
DefaultDirName={localappdata}\Programs\StudyCoach
DefaultGroupName=Study Coach
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=StudyCoach-Windows-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\StudyCoach.exe

[Files]
Source: "..\..\dist\StudyCoach-Windows-Portable\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

Source: "installed.flag"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Study Coach"; Filename: "{app}\StudyCoach.exe"
Name: "{autodesktop}\Study Coach"; Filename: "{app}\StudyCoach.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\StudyCoach.exe"; Description: "Start Study Coach"; Flags: nowait postinstall skipifsilent
