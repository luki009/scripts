#!/bin/bash
if [[ `whoami` -ne "crypto" ]]
then
  echo "Please run script as user 'crypto'"
  exit 1
fi

COIN_CLI=`find /home/crypto/ -name "*-cli" ! -path "*qa*"`
COIN=`awk -F'/' '{ print $(NF) }' <<< $COIN_CLI | cut -d"-" -f1`

echo $COIN
#
case $coin in
bulwark)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/bulwark-crypto/Bulwark.git
  cd Bulwark && git pull
  ./autogen.sh
  ./configure
  make

  cd ~
  Bulwark/src/bulwark-cli getinfo
  Bulwark/src/bulwark-cli stop
  rm -rf Bulwark/
  mv tmp/Bulwark ./
  Bulwark/src/bulwarkd -daemon
  Bulwark/src/bulwark-cli getinfo
  rm -rf tmp
;;
alqo)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/ALQOCRYPTO/ALQO
  cd ALQO && git pull
  ./autogen.sh
  ./configure
  make

  cd ~
  ALQO/src/alqo-cli getinfo
  ALQO/src/alqo-cli stop
  rm -rf ALQO/
  mv tmp/ALQO ./
  ALQO/src/alqod -daemon
  ALQO/src/alqo-cli getinfo
  rm -rf tmp
;;
bitcloud)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/LIMXTEC/Bitcloud.git
  cd Bitcloud && git pull
  ./autogen.sh
  ./configure
  make

  cd ~
  Bitcloud/src/bitcloud-cli getinfo
  Bitcloud/src/bitcloud-cli stop
  rm -rf Bitcloud/
  mv tmp/Bitcloud ./
  Bitcloud/src/bitcloudd -daemon
  Bitcloud/src/bitcloud-cli getinfo
  rm -rf tmp
;;
innova)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/innovacoin/innova
  cd innova && git pull
  ./autogen.sh
  ./configure
  make

  cd ~
  innova/src/innova-cli getinfo
  innova/src/innova-cli stop
  rm -rf innova/
  mv tmp/innova ./
  innova/src/innovad -daemon
  innova/src/innova-cli getinfo
  rm -rf tmp
;;
crowdcoin)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/crowdcoinChain/Crowdcoin
  cd Crowdcoin && git pull
  ./autogen.sh
  ./configure
  make

  cd ~
  Crowdcoin/src/crowdcoin-cli getinfo
  Crowdcoin/src/crowdcoin-cli stop
  rm -rf Crowdcoin/
  mv tmp/Crowdcoin ./
  Crowdcoin/src/crowdcoind -daemon
  Crowdcoin/src/crowdcoin-cli getinfo
  rm -rf tmp
;;
crown)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/Crowndev/crown-core
  mv crown-core Crown
  cd Crown
  ./autogen.sh
  ./configure
  make

  cd ~
  Crown/src/crown-cli getinfo
  Crown/src/crown-cli stop
  rm -rf Crown/
  mv tmp/Crown ./
  Crown/src/crownd -daemon
  Crown/src/crown-cli getinfo
  rm -rf tmp
;;
smartcash)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/SmartCash/Core-Smart
  mv Core-Smart/ smartcash
  cd smartcash
  ./autogen.sh
  ./configure
  make

  cd ~
  smartcash/src/smartcash-cli getinfo
  smartcash/src/smartcash-cli stop
  rm -rf smartcash/
  mv tmp/smartcash ./
  smartcash/src/smartcashd -daemon
  smartcash/src/smartcash-cli getinfo
  rm -rf tmp
;;
vivo)
  cd ~
  rm -rf tmp
  mkdir tmp && cd tmp
  git clone https://github.com/vivocoin/vivo
  cd vivo
  ./autogen.sh
  ./configure
  make

  cd ~
  vivo/src/vivo-cli getinfo
  vivo/src/vivo-cli stop
  rm -rf vivo/
  mv tmp/vivo ./
  vivo/src/vivod -daemon
  vivo/src/vivo-cli getinfo
  rm -rf tmp
;;
*)
  echo "Wallet not supported for update" >&2
  exit 1
;;
esac
