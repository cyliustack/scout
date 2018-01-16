from scout_print import *
import json
def read_config(path_cfg):
    cfg = json.loads('{"filters":[{"keyword":"idle","color":"cadeblue"}, {"keyword":"flush", "color":"#00BFFF"} ], "enable_verbose":"false", "enable_plot_bandwidth":"false"}')
    try:
        with open(path_cfg) as f:
            cfg = json.load(f)
    except:
        with open( 'sofa.cfg', "w") as f:
            json.dump(cfg,f)
            f.write("\n")
    print_info("SOFA Configuration: ")    
    print(cfg)
    return cfg
