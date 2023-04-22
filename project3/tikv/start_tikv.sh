curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
wait
source ~/.bash_profile
wait
tiup update --self && tiup update playground
wait
tiup playground --db 1 --pd 1 --kv 3
wait
