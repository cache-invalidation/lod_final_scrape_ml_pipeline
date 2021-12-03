# lod_final_scrape_ml_pipeline
Repository with systemctl job for scrapping data and running ML pipelines

## Installation
Right after cloning, you will need to initialize submodules, To do so, run 
```
git submodule update --init --recursive
```

Run the `install.sh` script, it will handle most of the work. After that don't forget to go into `lod_final_vkscrap` and set up `credentials.py` the way it is described in the [submodule's repository](https://github.com/cache-invalidation/lod_final_vkscrap).