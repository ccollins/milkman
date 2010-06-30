def loop(func):
    def loop_generator(*args, **kwargs):
        while 1: 
            yield func(*args, **kwargs)
    return loop_generator