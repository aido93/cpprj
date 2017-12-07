define(`switch',
`
$2switch($1)
$2{
forloop(`i',1,$3, `
$2$2case $4[i]:
$2$2{
$2$2$2
$2$2$2break;
$2$2}')
}
')
switch(name,tabstop,len,list)
