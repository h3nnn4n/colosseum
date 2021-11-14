from colosseum.manager import Manager


def match(world, agent_paths):
    manager = Manager(world, agent_paths)
    manager.start()
    manager.ping()
    manager.loop()
    manager.stop()
    return manager.scores
