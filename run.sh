#!/bin/bash
/home/chip/miniconda/bin/python /home/chip/active-sg-badminton/save_data.py
cd /home/chip/active-sg-badminton
/usr/bin/git add data/latest.json
/usr/bin/git commit -m "adding latest.json"
/usr/bin/git push origin master
cd ~
