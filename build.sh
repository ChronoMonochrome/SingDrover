#!/bin/bash

nuitka --standalone --onefile \
       --linux-onefile-icon=src/icon.png \
       --output-filename=SingDrover \
       --plugin-enable=upx \
       --upx-binary=/usr/bin/upx \
       src/main.py \
       --nofollow-import-to=bcrypt \
       --nofollow-import-to=cryptography \
       --nofollow-import-to=numpy \
       --nofollow-import-to=yaml
