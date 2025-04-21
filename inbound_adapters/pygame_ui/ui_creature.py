class UiCreature:
    def __init__(self, creature, _ui) -> None:
        self.icons = [None] * 2
        self.icon_coor = None
        self.ui = _ui
        self.creature = creature
