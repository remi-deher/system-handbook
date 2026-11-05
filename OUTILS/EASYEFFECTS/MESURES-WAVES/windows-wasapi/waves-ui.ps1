param([string]$Label='snapshot',[switch]$TogglePlayback)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public static class TrialMouse {
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint dx,uint dy,uint data,System.UIntPtr extra);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr h);
}
'@
$w=[System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Children,(New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,'MaxxAudioPro')))
if($null -eq $w){throw 'Open Waves Playback page first'}
[TrialMouse]::SetForegroundWindow([IntPtr]$w.Current.NativeWindowHandle) | Out-Null
if($TogglePlayback){
 $p=$w.FindFirst([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::AutomationIdProperty,'cmdPower')))
 if($null -eq $p){throw 'Playback Power missing'}
 $r=$p.Current.BoundingRectangle
 [TrialMouse]::SetCursorPos([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))|Out-Null
 [TrialMouse]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
 [TrialMouse]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 800
}
$r=$w.Current.BoundingRectangle
$bmp=New-Object Drawing.Bitmap([int]$r.Width,[int]$r.Height)
$g=[Drawing.Graphics]::FromImage($bmp)
try{$g.CopyFromScreen([int]$r.X,[int]$r.Y,0,0,$bmp.Size);$bmp.Save("$PSScriptRoot\$Label.png")}finally{$g.Dispose();$bmp.Dispose()}
$w.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition) | Where-Object {$_.Current.ControlType -ne [System.Windows.Automation.ControlType]::Image} | ForEach-Object { [pscustomobject]@{Name=$_.Current.Name;ID=$_.Current.AutomationId;Type=$_.Current.ControlType.ProgrammaticName} } | ConvertTo-Json -Depth 4 | Set-Content "$PSScriptRoot\$Label-ui.json" -Encoding UTF8
