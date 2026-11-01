set xa_parts [get_parts -quiet -filter {NAME =~ *xa7z020*}]
puts "XA7Z020_MATCH_COUNT=[llength $xa_parts]"
foreach part $xa_parts {
    puts "XA7Z020_PART=[get_property NAME $part]"
}
set pkg_parts [get_parts -quiet -filter {NAME =~ *xa7z020*clg400*}]
puts "XA7Z020_CLG400_MATCH_COUNT=[llength $pkg_parts]"
foreach part $pkg_parts {
    puts "XA7Z020_CLG400_PART=[get_property NAME $part]"
}
exit 0