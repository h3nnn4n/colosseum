from colosseum.manager import Manager


def run_match(world, **kwargs):
    manager = Manager(world, **kwargs)
    manager.start()
    manager.loop()
    manager.stop()
    return manager.results
