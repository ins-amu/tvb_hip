
class Cache:
    pass


class Stage:
    """
    When inputs and command line are content hashed, and a hit
    is found in the cache, we pull the results which are either a tar'd
    directory or a file.

    Assumes that the cmd effect is invariant e.g. same environment etc.

    """

    def __init__(self, cache, cmd, output_path, *input_paths):
        self.cache = cache
        self.signature = cmd, output, inputs
        

def recon_all(cache, t1):
    t1_md5 = t1.md5()
    if t1_md5 not in cache['recon_all']:

        cache['recon_all'] = result
    return cache['recon_all'][t1_md5]
