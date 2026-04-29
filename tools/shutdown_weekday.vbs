Set objShell = CreateObject("WScript.Shell")

' Shutdown 5 menit (300 detik)
objShell.Run "shutdown -s -t 300 -c ""Komputer akan mati dalam 5 menit... Klik NO untuk batal"""

' Popup selalu di depan
jawab = MsgBox("Komputer akan dimatikan dalam 5 menit." & vbCrLf & "Klik NO untuk membatalkan.", 4 + 32 + 4096, "Konfirmasi Shutdown")

If jawab = 7 Then
    objShell.Run "shutdown -a"
    MsgBox "Shutdown dibatalkan", 64 + 4096, "Info"
End If