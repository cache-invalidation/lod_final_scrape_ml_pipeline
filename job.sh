#!/usr/bin/env bash

./lod_final_hadoop_toolkit/copy_html.sh
mv lod_final_hadoop_toolkit/articles.json articles.json

python job.py
