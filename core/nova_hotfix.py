"""
Nova hotfix component module
"""
from core.nova_release import NovaRelease


class NovaHotfix(NovaRelease):
    """Nova hotfix component"""

    def __init__(self, project, version, delivery, hotfix):
        super().__init__(project, version, delivery)
        self.hotfix = hotfix

    def __str__(self):
        return f"""
            Nova {self.version}. 
            Delivery {self.__delivery}. 
            Hotfix {self.hotfix}"""

    def __repr__(self):
        return self.__str__()
