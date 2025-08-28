@echo off
setlocal
set "TWEAK_ID=%~1"
if defined TWEAK_ID ( goto %TWEAK_ID% )
exit /b 1

:timers
    bcdedit /set disabledynamictick yes >nul & bcdedit /deletevalue useplatformclock >nul 2>&1
    goto :eof
:responsiveness
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 38 /f >nul
    goto :eof
:mmcss_games
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 2 /f >nul
    goto :eof
:timeouts
    reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "0" /f >nul
    reg add "HKCU\Control Panel\Desktop" /v "WaitToKillAppTimeout" /t REG_SZ /d "2000" /f >nul
    goto :eof
:fse_and_gamemode
    reg add "HKCU\SYSTEM\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 0 /f >nul
    reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul
    reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul
    goto :eof
:power_plan
    for /f "tokens=2 delims=:" %%a in ('powercfg /l ^| find "High"') do for /f "tokens=*" %%b in ("%%a") do set HP_GUID=%%b
    powercfg /duplicatecheme %HP_GUID% e1f2d9c8-3333-4a34-862b-72c01933c02f
    powercfg /changename e1f2d9c8-3333-4a34-862b-72c01933c02f "Titan Power Plan" >nul
    powercfg /setactive e1f2d9c8-3333-4a34-862b-72c01933c02f >nul
    goto :eof
:cpu_tweaks
    powercfg -setacvalueindex SCHEME_CURRENT sub_processor CPMINCORES 100 >nul
    powercfg -setacvalueindex SCHEME_CURRENT sub_processor PROCTHROTTLEMIN 100 >nul
    powercfg /setactive SCHEME_CURRENT >nul
    goto :eof
:disable_mitigations
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 3 /f >nul
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul
    goto :eof
:kbm_settings
    reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f >nul
    reg add "HKCU\Control Panel\Keyboard" /v "KeyboardDelay" /t REG_SZ /d "0" /f >nul
    goto :eof
:disable_usb_powersaving
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\USB" /v "DisableSelectiveSuspend" /t REG_DWORD /d 1 /f >nul
    goto :eof
:network_tweaks
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul
    for /f "delims=" %%q in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { $_.InterfaceGuid }"') do (
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\%%q" /v TCPNoDelay /t REG_DWORD /d 1 /f >nul
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\%%q" /v TcpAckFrequency /t REG_DWORD /d 1 /f >nul
    )
    goto :eof
:storage_tweaks
    For /f "Delims=" %%k In ('Reg.exe Query HKLM\SYSTEM\CurrentControlSet\Enum /f "{4d36e967-e325-11ce-bfc1-08002be10318}" /d /s ^| Find "HKEY_LOCAL_MACHINE"') Do ( Reg.exe Add "%%k\Device Parameters\Disk" /v "UserWriteCacheSetting" /t REG_DWORD /d 1 /f >nul 2>&1 )
    fsutil behavior set memoryusage 2 >nul & fsutil behavior set DisableDeleteNotify 1 >nul
    goto :eof
:debloat_tweaks
    reg add "HKLM\Software\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul
    sc config XblAuthManager start= disabled >nul & sc config XblGameSave start= disabled >nul
    sc config DiagTrack start= disabled >nul
    schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /Disable >nul
    goto :eof
:debloat_services
    sc config MapsBroker start= disabled >nul
    sc config Spooler start= disabled >nul
    sc config bthserv start= disabled >nul
    goto :eof
:debloat_apps
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-AppxPackage *Microsoft.BingWeather* | Remove-AppxPackage"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-AppxPackage *Microsoft.GetHelp* | Remove-AppxPackage"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-AppxPackage *Microsoft.MicrosoftSolitaireCollection* | Remove-AppxPackage"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-AppxPackage *Microsoft.People* | Remove-AppxPackage"
    goto :eof
:ram_low
    powershell -NoProfile -Command "Enable-MMAgent -MemoryCompression" >nul
    goto :ram_common
:ram_high
    powershell -NoProfile -Command "Disable-MMAgent -MemoryCompression" >nul
    goto :ram_common
:ram_common
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d 0 /f >nul
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d 0 /f >nul
    sc stop "SysMain" >nul & sc config "SysMain" start=disabled >nul
    goto :eof
:gpu_amd
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v "StutterMode" /t REG_DWORD /d "0" /f >nul
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000\UMD" /v "ShaderCache" /t REG_BINARY /d "3200" /f >nul
    goto :eof
:gpu_intel
    reg add "HKLM\Software\Intel\GMM" /v "DedicatedSegmentSize" /t REG_DWORD /d "512" /f >nul
    goto :eof
:gpu_nvidia
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm" /v "DisablePreemption" /t Reg_DWORD /d "1" /f >nul
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "Preemption" /t REG_DWORD /d 0 /f >nul
    goto :eof
:clean_devices
    POWERSHELL -NoProfile -ExecutionPolicy Bypass -Command "$Devices = Get-PnpDevice | Where-Object { $_.Status -eq 'Unknown' }; foreach ($Device in $Devices) { try { &\"pnputil\" /remove-device $Device.InstanceId } catch {} }"
    goto :eof