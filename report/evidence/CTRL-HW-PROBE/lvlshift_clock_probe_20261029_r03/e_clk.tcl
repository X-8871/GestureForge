connect -url tcp:127.0.0.1:3121
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
foreach a {0xF8000170 0xF8000180 0xF8000190 0xF8000120 0xF8000100 0xF8000900} {
  catch {mrd $a 1} r
  puts "REG_$a = $r"
}
