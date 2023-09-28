import simpleregistry


class RegisteredDataclass(metaclass=simpleregistry.RegisteredMeta):
    def __post_init__(self):
        self.Config.registry.register(self)
