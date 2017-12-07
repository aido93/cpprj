define(`for_iterator',
`
ifelse($1,`const',`
for (auto& $2: $3)
{
$4$5 
}
',`
for (const auto& $2: $3)
{
$4$5 
}
')
'
for_iterator(is_const,it_name,container,tabstop,body)
