from colosseum.manager import Manager


def match(world, **kwargs):
    manager = Manager(world, **kwargs)
    manager.start()
    manager.loop()
    manager.stop()
    return manager.results
