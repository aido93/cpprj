define(`for_counter',
`
ifelse($1,`signed',`
for (uint32_t $2=$3; $2<$4; ifelse($5,`1', `++$2', `$2+=$5'))
{
$6$7 
}
',`
for (int32_t $2=$3; $2<$4; ifelse($5,`1', `++$2', `$2+=$5'))
{
$6$7
}
')
'
for_counter(is_signed,name,begin,end,step,tabstop,body)
