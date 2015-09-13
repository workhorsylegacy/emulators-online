schtasks /delete /f /tn "My App2"
schtasks /create /f /tn "My App2" /sc once /st 00:00 /tr "'C:/Program Files/Git/git-bash.exe' -c 'echo $PATH > c:/Users/Matt/Desktop/fuck'"
schtasks /run /tn "My App2"
