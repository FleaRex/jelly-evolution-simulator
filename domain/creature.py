import random

import numpy as np

from inbound_adapters.pygame_ui.ui_creature import UiCreature


class Creature:
    def __init__(self, d, p_id_number, parent_species, _sim, _ui) -> None:
        self.dna = d
        self.calmState = None
        self.id_number = p_id_number
        self.fitness = None
        self.rank = None
        self.living = True
        self.species = self.get_species(parent_species)
        self.sim = _sim
        self.codon_with_change = None
        # TODO: Prepping for inversion of parent and child
        self.ui_creature = UiCreature(self, _ui)

    def get_species(self, parent_species):
        if parent_species == -1:
            return self.id_number
        else:
            return parent_species

    def save_calm_state(self, arr):
        self.calmState = arr

    def get_mutated_dna(self, sim):
        mutation = np.clip(np.random.normal(0.0, 1.0, self.dna.shape[0]), -99, 99)
        result = self.dna + sim.mutation_rate * mutation
        new_species = self.species

        big_mut_loc = 0
        if random.uniform(0, 1) < self.sim.big_mutation_rate:  # do a big mutation
            new_species = sim.species_count
            sim.species_count += 1
            cell_x = random.randint(0, self.sim.width - 1)
            cell_y = random.randint(0, self.sim.height - 1)
            cell_beat = random.randint(0, self.sim.beats_per_cycle - 1)

            big_mut_loc = (
                cell_x * self.sim.height * self.sim.beats_per_cycle
                + cell_y * self.sim.beats_per_cycle
                + cell_beat
            ) * self.sim.traits_per_box
            for i in range(self.sim.traits_per_box):
                delta = 0
                while abs(delta) < 0.5:
                    delta = np.random.normal(0.0, 1.0, 1)
                result[big_mut_loc + i] += delta

                # Cells that endure a big mutation are also required to be at least somewhat rigid,
                # because if a cell goes from super-short to super-tall but has low rigidity the whole time,
                # then it doesn't really matter.
                if i == 2 and result[big_mut_loc + i] < 0.5:
                    result[big_mut_loc + i] = 0.5

        return result, new_species, big_mut_loc
