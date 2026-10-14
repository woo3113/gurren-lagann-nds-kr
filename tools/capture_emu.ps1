param([string]$Rom, [string]$Prefix)
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class CAP {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
 public struct RECT { public int L,T,R,B; }
}
"@
$emu = "D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64\melonDS.exe"
$outdir = "D:\20_게임\_한글패치\그랜라간\work"
Get-Process melonDS -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
Start-Process -FilePath $emu -ArgumentList @('-b','never',"`"$Rom`"")
Start-Sleep -Seconds 20
for ($i=1; $i -le 5; $i++) {
  $p = Get-Process melonDS -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { Write-Output "melonDS gone at $i"; break }
  $h = $p.MainWindowHandle
  [CAP]::ShowWindow($h,9)|Out-Null; [CAP]::SetForegroundWindow($h)|Out-Null
  Start-Sleep -Milliseconds 600
  $r = New-Object CAP+RECT
  [CAP]::GetClientRect($h,[ref]$r)|Out-Null
  $w=$r.R-$r.L; $hh=$r.B-$r.T
  if ($w -gt 0 -and $hh -gt 0) {
    $bmp = New-Object System.Drawing.Bitmap($w,$hh)
    $g=[System.Drawing.Graphics]::FromImage($bmp)
    $hdc=$g.GetHdc(); [CAP]::PrintWindow($h,$hdc,2)|Out-Null; $g.ReleaseHdc($hdc); $g.Dispose()
    $bmp.Save("$outdir\$($Prefix)_$i.png",[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
    Write-Output "captured $($Prefix)_$i ($w x $hh)"
  }
  Start-Sleep -Seconds 6
}
Get-Process melonDS -ErrorAction SilentlyContinue | Select-Object Id,MainWindowTitle | Format-Table -AutoSize
Write-Output "DONE"
