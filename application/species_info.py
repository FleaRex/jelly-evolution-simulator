from typing import Optional

import numpy as np
import math

from domain.creature import Creature


class SpeciesInfo:
    def __init__(
        self, _sim, creature: Optional[Creature], ancestor: Optional[Creature]
    ) -> None:
        self.sim = _sim
        self.species_id = creature.species
        self.ancestor_id = None
        self.num_ancestor_species = 0
        if ancestor is not None:
            self.ancestor_id = ancestor.species
            self.num_ancestor_species = (
                self.sim.species_info[ancestor.species].num_ancestor_species + 1
            )

        self.apex_pop = 0
        self.reign = []
        self.reps = np.zeros(
            4, dtype=int
        )  # Representative ancestor, first, apex, and last creatures of this species.
        self.prominent = False

        if ancestor is not None:
            self.reps[0] = ancestor.id_number

        self.reps[1] = creature.id_number
        # TODO: This smells
        self.coor = None

    # TODO: There's an argument this should be in UI
    def become_prominent(
        self,
    ):  # if you are prominent, all your ancestors become prominent.
        self.prominent = True
        self.insert_into_prominent_species_list()
        if self.ancestor_id is not None:  # you have a parent
            ancestor = self.sim.species_info[self.ancestor_id]
            if not ancestor.prominent:
                ancestor.become_prominent()

    def insert_into_prominent_species_list(self):
        i = self.species_id
        p = self.sim.prominent_species
        while (
            len(p) <= self.num_ancestor_species
        ):  # this level doesn't exist yet. Add new levels of the genealogy tree to acommodate you
            p.append([])
        p_l = p[self.num_ancestor_species]
        insert_index = 0
        for index in range(
            len(p_l)
        ):  # inefficient sorting thing, but there are <50 species so who cares
            other = p_l[index]
            ancestor_compare = (
                0
                if self.num_ancestor_species == 0
                else self.sim.species_info[other].ancestor_id - self.ancestor_id
            )
            if ancestor_compare == 0:  # siblings
                if other < i:
                    insert_index = index + 1
            else:  # not siblings trick to avoid family trees tangling (all siblings should be adjacent)
                if ancestor_compare < 0:
                    insert_index = index + 1
        p_l.insert(insert_index, i)

    def get_when(self, index):
        return math.floor(self.reps[index] // self.sim.creature_count)

    # TODO: Why does this not use the self.sim for the fitness?
    def get_performance(self, sim, index):
        gen = math.floor(self.reps[index] // self.sim.creature_count)
        c = self.reps[index] % self.sim.creature_count
        creature = sim.creatures[gen][c]
        return creature.fitness
