from models.nova_release import NovaRelease


class NovaHotfix(NovaRelease):
    def __init__(self, project, version, delivery, hotfix):
        super().__init__(project, version, delivery)
        self.hotfix = hotfix

    def __str__(self):
        return 'Nova ' + str(self.version) + ". Delivery " + str(self.delivery) + ". Hotfix " + str(self.hotfix)

    def __repr__(self):
        return self.__str__()