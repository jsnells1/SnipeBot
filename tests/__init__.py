import pytest
from data.models.data_models import database, Calendar, CarePackage, CarePackageRwds, HotPotato, Scores, SnipingMods, Soapbox, SqliteSequence


def setup_module(module):
    database.init(':memory:')
    database.create_tables([Calendar, CarePackage, CarePackageRwds,
                            HotPotato, Scores, SnipingMods, Soapbox])
