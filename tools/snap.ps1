param([string]$Out = "C:\Users\woo31\AppData\Local\Temp\opencode\snap.png")
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class SN {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
 public struct RECT { public int L,T,R,B; }
}
"@
$p = Get-Process melonDS -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { Write-Output "no melonDS"; exit 1 }
Write-Output ("title: " + $p.MainWindowTitle)
$h = $p.MainWindowHandle
[SN]::ShowWindow($h,9) | Out-Null
[SN]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 500
$r = New-Object SN+RECT
[SN]::GetClientRect($h,[ref]$r) | Out-Null
$w = $r.R - $r.L; $hh = $r.B - $r.T
if ($w -le 0 -or $hh -le 0) { Write-Output "bad rect"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w,$hh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[SN]::PrintWindow($h,$hdc,2) | Out-Null
$g.ReleaseHdc($hdc); $g.Dispose()
$bmp.Save($Out,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Output ("saved " + $Out + " (" + $w + "x" + $hh + ")")
