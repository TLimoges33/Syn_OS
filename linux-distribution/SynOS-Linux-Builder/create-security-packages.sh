#!/bin/bash

# SynOS Complete Security Distribution Package Creator
# Creates comprehensive package lists for BlackArch and Kali equivalent tools

cat > config/package-lists/synos-security-complete.list.chroot << 'EOF'
# SynOS Complete Security Distribution - All Tools from BlackArch and Kali

# ==================== CORE SYSTEM ====================
live-boot
live-config
live-config-systemd
systemd
rsyslog
dbus
udev
firmware-linux
firmware-linux-nonfree

# ==================== DESKTOP ENVIRONMENT ====================
mate-desktop-environment
mate-terminal
mate-panel
mate-control-center
mate-session-manager
lightdm
lightdm-gtk-greeter
xorg
xinit
x11-xserver-utils
firefox-esr
chromium

# ==================== VIRTUALIZATION & VM SUPPORT ====================
qemu-system-x86
qemu-system-arm
qemu-utils
qemu-kvm
libvirt-daemon-system
libvirt-clients
virt-manager
virt-viewer
virtualbox
docker.io
docker-compose
vagrant

# ==================== NETWORK ANALYSIS ====================
wireshark
wireshark-qt
tshark
tcpdump
nmap
netcat-openbsd
socat
netsniff-ng
ettercap-text-only
ettercap-graphical
dsniff
snort
suricata
ntopng
aircrack-ng
airmon-ng
airodump-ng
aireplay-ng
kismet
hostapd
dnsmasq
bridge-utils
openvpn
tor
proxychains4
macchanger
mitmproxy

# ==================== WEB APPLICATION SECURITY ====================
nikto
dirb
dirbuster
gobuster
wfuzz
ffuf
hydra
medusa
john
john-data
hashcat
hashcat-data
sqlmap
patator
cewl
crunch
wordlists
seclists
burpsuite
zaproxy
commix
w3af

# ==================== VULNERABILITY ASSESSMENT ====================
openvas
openvas-scanner
nuclei
masscan
zmap
unicornscan
hping3
fping
arping
nbtscan
enum4linux
smbclient
rpcclient
showmount
snmpwalk
onesixtyone
smtp-user-enum
dnsrecon
dnsenum
sublist3r
fierce
theharvester
sparta
legion

# ==================== EXPLOITATION FRAMEWORKS ====================
metasploit-framework
armitage
beef-xss
routersploit
exploitdb
searchsploit

# ==================== REVERSE ENGINEERING ====================
radare2
cutter
ghidra
gdb
gdb-multiarch
binwalk
hexedit
bless
objdump
readelf
strings
ltrace
strace
valgrind
upx-ucl
yara
binutils

# ==================== DIGITAL FORENSICS ====================
autopsy
sleuthkit
volatility
volatility3
bulk-extractor
foremost
scalpel
testdisk
photorec
ddrescue
dc3dd
dcfldd
ewf-tools
afflib-tools
yara
clamav
clamav-daemon
chkrootkit
rkhunter
aide
tripwire
osquery

# ==================== CRYPTOGRAPHY & STEGANOGRAPHY ====================
hashcat
hashcat-data
john
john-data
ophcrack
fcrackzip
pdfcrack
steghide
outguess
stegsnow
exiftool
exiv2
mat2
gpg
openssl

# ==================== WIRELESS SECURITY ====================
aircrack-ng
airmon-ng
airodump-ng
aireplay-ng
airbase-ng
airdecap-ng
kismet
wifite
reaver
bully
pixiewps
hostapd-wpe
freeradius
wpa-supplicant
hostapd
hcxtools
hashcat-utils

# ==================== SOCIAL ENGINEERING ====================
social-engineer-toolkit
maltego
theharvester
recon-ng
shodan
spiderfoot
photon
sherlock

# ==================== MOBILE SECURITY ====================
apktool
dex2jar
jadx
adb
fastboot
android-tools-adb
android-tools-fastboot

# ==================== CLOUD SECURITY ====================
awscli
azure-cli
kubectl
terraform
ansible
docker-bench-security

# ==================== AI/ML SECURITY TOOLS ====================
python3
python3-pip
python3-dev
python3-venv
python3-tensorflow
python3-torch
python3-sklearn
python3-pandas
python3-numpy
python3-scipy
python3-matplotlib
python3-seaborn
jupyter-notebook
python3-requests
python3-urllib3

# ==================== PROGRAMMING & DEVELOPMENT ====================
build-essential
gcc
g++
make
cmake
autotools-dev
git
subversion
vim
emacs
code
python3
python2
ruby
ruby-dev
perl
php
php-cli
nodejs
npm
yarn
golang
golang-go
rust-all
openjdk-11-jdk
openjdk-8-jdk
maven
gradle

# ==================== DATABASES ====================
mysql-server
mysql-client
postgresql
postgresql-client
mongodb
redis-server
sqlite3
sqlitebrowser

# ==================== NETWORK SERVICES ====================
apache2
apache2-utils
nginx
nginx-extras
openssh-server
openssh-client
telnet
ftp
tftp
nfs-common
samba
samba-client
winbind
snmp
snmp-mibs-downloader

# ==================== SYSTEM UTILITIES ====================
curl
wget
rsync
unzip
p7zip-full
p7zip-rar
rar
unrar
htop
iotop
nethogs
iftop
nload
vnstat
tree
locate
mlocate
findutils
grep
sed
awk
sort
uniq
cut
tr
tee
less
more
head
tail
watch
screen
tmux
expect
parallel

# ==================== HARDWARE TOOLS ====================
flashrom
avrdude
openocd
minicom
picocom
cu
setserial

# ==================== ADDITIONAL SECURITY TOOLS ====================
lynis
tiger
clamav-daemon
freshclam
rkhunter
chkrootkit
debsums
aide
samhain
fail2ban
psad
fwlogwatch
logwatch
syslog-ng
auditd
wpscan
joomscan
droopescan
cmsmap
davtest
padbuster
bed
spike
fuzzer

# ==================== WORDLISTS & DICTIONARIES ====================
wordlists
seclists
rockyou
dirb
dirbuster
wfuzz

# ==================== ADDITIONAL KALI TOOLS ====================
enum4linux-ng
impacket-scripts
responder
bloodhound
neo4j
crackmapexec
evil-winrm
ldapdomaindump
ldeep

# ==================== BLACKARCH EQUIVALENT TOOLS ====================
amass
subfinder
assetfinder
httprobe
aquatone
eyewitness
nuclei-templates
gau
waybackurls
hakrawler
paramspider
arjun
linkfinder
secretfinder
jwttool
jwt-cracker

# ==================== VM AUTO-SETUP TOOLS ====================
wget
curl
git
python3-requests
qemu-guest-agent
spice-vdagent
EOF

echo "SynOS Security package list created successfully!"
echo "Total packages: $(grep -v '^#' config/package-lists/synos-security-complete.list.chroot | grep -v '^$' | wc -l)"