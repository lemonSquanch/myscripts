#!/bin/bash

sudo pacman -Syu;
sudo pacman -S os-prober;
sudo os-prober;
# ...

sudo pacman -S xorg-server \
               kde-meta-kdegraphics \
               kde-applications \
               kdeedu \
               kdeutils \
               plasma-meta \
               vim \
               gvim \
               qtcreator \
               emacs \
               firefox \
               chromium \
               thunderbird \
               truecrypt \
               dolphin \
               guake \
               git \
               gcc \
               gdb \
               clang \
               cmake \
               kcolorchooser \
               clamav \
               clamtk \
               gource \
               vlc \
               gimp \
               krita \
               docker \
               inkscape \
               gnuplot \
               libreoffice \
               okular \
               iotop \
               iftop \
               gperftools \
               iperf \
               iperf3 \
               perf \
               kdesdk-kcachegrind \
               valgrind \
               afl \
               afl-utils \
               clang-tools-extra \
               virtualbox \
               baobab \
               weechat \
               hexchat \
               irssi \
               quassel-client \
               virtualbox-guest-dkms \
               linux-headers \
               gparted \
               pigz \
               pbzip2 \
               tk \
               meson;

sudo freshclam;

# ...
