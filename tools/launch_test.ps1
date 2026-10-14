param([string]$Rom, [int]$Samples = 18, [int]$Interval = 3)
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class LT {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
 public struct RECT { public int L,T,R,B; }
}
"@
$emu = (Get-Content "C:\Users\woo31\AppData\Local\Temp\opencode\emu_path.txt" -Raw).Trim()
$tmp = "C:\Users\woo31\AppData\Local\Temp\opencode\t.nds"
Copy-Item $Rom $tmp -Force
Get-Process melonDS -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process -FilePath $emu -ArgumentList "`"$tmp`""
Start-Sleep -Seconds 4
for ($i=1; $i -le $Samples; $i++) {
  $p = Get-Process melonDS -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { Write-Output "t=$i GONE"; break }
  $h = $p.MainWindowHandle
  [LT]::ShowWindow($h,9)|Out-Null
  Start-Sleep -Milliseconds 250
  $r = New-Object LT+RECT
  [LT]::GetClientRect($h,[ref]$r)|Out-Null
  $w=$r.R-$r.L; $hh=$r.B-$r.T
  if ($w -le 0 -or $hh -le 0) { Write-Output "t=$i NOWIN"; Start-Sleep -Seconds $Interval; continue }
  $bmp = New-Object System.Drawing.Bitmap($w,$hh)
  $gg=[System.Drawing.Graphics]::FromImage($bmp)
  $hdc=$gg.GetHdc(); [LT]::PrintWindow($h,$hdc,2)|Out-Null; $gg.ReleaseHdc($hdc); $gg.Dispose()
  $rect = New-Object System.Drawing.Rectangle(0,0,$w,$hh)
  $data=$bmp.LockBits($rect,[System.Drawing.Imaging.ImageLockMode]::ReadOnly,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $stride=$data.Stride
  $bytes=New-Object byte[] ($stride*$hh)
  [System.Runtime.InteropServices.Marshal]::Copy($data.Scan0,$bytes,0,$bytes.Length)
  $bmp.UnlockBits($data)
  $y0=[int]($hh*0.55); $y1=[int]($hh*0.98); $x0=[int]($w*0.15); $x1=[int]($w*0.85)
  $sumB=0.0; $sumR=0.0; $n=0; $white=0
  for ($y=$y0; $y -lt $y1; $y+=4) {
    for ($x=$x0; $x -lt $x1; $x+=4) {
      $idx=$y*$stride+$x*3
      $b=$bytes[$idx]; $gr=$bytes[$idx+1]; $rr=$bytes[$idx+2]
      $sumB+=($rr+$gr+$b)/3.0; $sumR+=($rr-$b); $n++
      if ($rr -gt 235 -and $gr -gt 235 -and $b -gt 235) { $white++ }
    }
  }
  $bright=$sumB/$n; $red=$sumR/$n; $wf=$white/$n
  Write-Output ("t=$i bright={0:N1} red={1:N1} white={2:N2}" -f $bright,$red,$wf)
  $bmp.Dispose()
  Start-Sleep -Seconds $Interval
}
Get-Process melonDS -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Output "DONE"
