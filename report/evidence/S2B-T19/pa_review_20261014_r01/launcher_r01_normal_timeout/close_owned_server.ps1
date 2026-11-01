# 仅记录mock服务闭合，不调用设备或进程。
[IO.File]::AppendAllText((Join-Path $PSScriptRoot "mock_events.log"),"mock_close_server`n")
