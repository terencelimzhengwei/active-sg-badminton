#!/bin/bash
/home/chip/miniconda/bin/python /home/chip/active-sg-badminton/save_data.py
/usr/bin/git add /home/chip/active-sg-badminton/data/latest.json
/usr/bin/git commit -m "adding latest.json"
/usr/bin/git push origin master
