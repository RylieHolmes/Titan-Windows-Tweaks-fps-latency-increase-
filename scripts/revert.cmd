@echo off
setlocal
set "TWEAK_ID=%~1"
if defined TWEAK_ID ( goto %TWEAK_ID% )
exit /b 1

:timers
    bcdedit /set disabledynamictick no >nul & bcdedit /set useplatformclock true >nul
    goto :eof
:responsiveness
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 2 /f >nul
    goto :eof
:mmcss_games
    reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /f >nul 2>&1
    goto :eof
:timeouts
    reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "400" /f >nul
    reg add "HKCU\Control Panel\Desktop" /v "WaitToKillAppTimeout" /t REG_SZ /d "5000" /f >nul
    goto :eof
:fse_and_gamemode
    reg add "HKCU\SYSTEM\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f >nul
    reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 0 /f >nul
    reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 0 /f >nul
    goto :eof
:power_plan
    powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e >nul
    powercfg /delete e1f2d9c8-3333-4a34-862b-72c01933c02f >nul 2>&1
    goto :eof
:cpu_tweaks
    powercfg -setacvalueindex SCHEME_CURRENT sub_processor CPMINCORES 10 >nul
    powercfg -setacvalueindex SCHEME_CURRENT sub_processor PROCTHROTTLEMIN 5 >nul
    powercfg -setacvalueindex SCHEME_CURRENT sub_sleep ALLOWSTANDBY 1 >nul
    powercfg /setactive SCHEME_CURRENT >nul
    goto :eof
:disable_mitigations
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverride" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverrideMask" /f >nul 2>&1
    goto :eof
:kbm_settings
    reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f >nul
    reg add "HKCU\Control Panel\Keyboard" /v "KeyboardDelay" /t REG_SZ /d "1" /f >nul
    goto :eof
:disable_usb_powersaving
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\USB" /v "DisableSelectiveSuspend" /t REG_DWORD /d 0 /f >nul
    goto :eof
:network_tweaks
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 10 /f >nul
    for /f "delims=" %%q in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { $_.InterfaceGuid }"') do (
        reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\%%q" /v TCPNoDelay /f >nul 2>&1
        reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\%%q" /v TcpAckFrequency /f >nul 2>&1
    )
    goto :eof
:storage_tweaks
    For /f "Delims=" %%k In ('Reg.exe Query HKLM\SYSTEM\CurrentControlSet\Enum /f "{4d36e967-e325-11ce-bfc1-08002be10318}" /d /s ^| Find "HKEY_LOCAL_MACHINE"') Do ( Reg.exe Delete "%%k\Device Parameters\Disk" /v UserWriteCacheSetting /f >nul 2>&1 )
    fsutil behavior set memoryusage 1 >nul & fsutil behavior set DisableDeleteNotify 0 >nul
    fsutil behavior set disable8dot3 2 >nul
    goto :eof
:debloat_tweaks
    reg add "HKLM\Software\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 1 /f >nul
    sc config XblAuthManager start= auto >nul & sc config XblGameSave start= demand >nul
    sc config DiagTrack start= auto >nul
    schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /Enable >nul
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "EnableSmartScreen" /t REG_DWORD /d 1 /f >nul
    goto :eof
:debloat_services
    sc config MapsBroker start= auto >nul
    sc config Spooler start= auto >nul
    sc config bthserv start= auto >nul
    goto :eof
:debloat_apps
    echo Re-installing UWP apps is complex and best handled by a System Restore point.
    goto :eof
:memory
    powershell -NoProfile -Command "Enable-MMAgent -MemoryCompression" >nul
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d 3 /f >nul
    sc config "SysMain" start=auto >nul & sc start "SysMain" >nul
    goto :eof
:gpu_amd
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v "StutterMode" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000\UMD" /v "ShaderCache" /f >nul 2>&1
    goto :eof
:gpu_intel
    reg delete "HKLM\Software\Intel\GMM" /v "DedicatedSegmentSize" /f >nul 2>&1
    goto :eof
:gpu_nvidia
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm" /v "DisablePreemption" /f >nul 2>&1
    reg delete "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "Preemption" /f >nul 2>&1
    goto :eof
:clean_devices
    echo This action has no revert.
    goto :eof