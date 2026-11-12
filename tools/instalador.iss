; Instalador do Maré de Mentiras (Inno Setup 6).
; Antes, gere dist\onefile\MareDeMentiras.exe com o PyInstaller (ver README).
; Compilar: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" tools\instalador.iss
; Resultado: dist\instalador\MareDeMentiras-Setup.exe

#define Versao "1.5"

[Setup]
AppId={{6E3B1F2A-7C4D-4E8B-9A51-3D2C7F0B8E61}
AppName=Maré de Mentiras
AppVersion={#Versao}
AppVerName=Maré de Mentiras {#Versao}
AppPublisher=Gabriel Costa
AppPublisherURL=https://github.com/GabrielLima2006/JogoA3
DefaultDirName={autopf}\Maré de Mentiras
DefaultGroupName=Maré de Mentiras
DisableProgramGroupPage=yes
; instala só para o usuário atual (%LOCALAPPDATA%\Programs), sem pedir administrador
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist\instalador
OutputBaseFilename=MareDeMentiras-Setup
SetupIconFile=icone.ico
UninstallDisplayIcon={app}\MareDeMentiras.exe
UninstallDisplayName=Maré de Mentiras
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\onefile\MareDeMentiras.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Maré de Mentiras"; Filename: "{app}\MareDeMentiras.exe"
Name: "{group}\Desinstalar Maré de Mentiras"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Maré de Mentiras"; Filename: "{app}\MareDeMentiras.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MareDeMentiras.exe"; Description: "{cm:LaunchProgram,Maré de Mentiras}"; Flags: nowait postinstall skipifsilent
