#!/usr/bin/env bash

cd lod_final_mltools
pip install -r requirements.txt
./load_model.sh
cd ..

cd load_final_vkscrap
pip install -r requirements.txt
cd ..
