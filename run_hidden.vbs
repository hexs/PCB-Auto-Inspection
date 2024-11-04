Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\PythonProjects\PCB-Auto-Inspection\run.bat" & Chr(34), 0
Set WshShell = Nothing