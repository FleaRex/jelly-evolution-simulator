import math

import numpy as np
import pygame
from pygame import Surface

from enums import Color
from inbound_adapters.pygame_ui.shapes import (
    draw_rect,
    draw_text_rect,
    center_text,
    draw_clock,
)
from utils import dist_to_text, species_to_color, array_lerp, lerp, list_lerp


class UiCreature:
    def __init__(self, creature, _ui) -> None:
        self.icons = [None] * 2
        self.icon_coor = None
        self.ui = _ui
        self.creature = creature

    def draw_cell(self, surface, node_state, frame, transform, x, y) -> None:
        tx, ty, s = transform
        color = self.traits_to_color(self.creature.dna, x, y, frame)
        points = []
        for p in range(4):
            px = x
            if p == 1 or p == 2:
                px += 1
            py = y + p // 2
            points.append(
                [tx + node_state[px, py, 0] * s, ty + node_state[px, py, 1] * s]
            )

        pygame.draw.polygon(surface, color, points)

    def draw_environment(self, surface, transform) -> None:
        # sky
        draw_rect(surface, transform, None, Color.BLACK)

        # signs
        font = self.ui.big_font if transform[2] >= 50 else self.ui.small_font
        for meters in range(0, 3000, 100):
            u = meters * self.creature.sim.units_per_meter
            draw_rect(surface, transform, [u - 0.2, -6, u + 0.2, 0], Color.SIGN)
            draw_text_rect(
                surface,
                transform,
                [u - 1.5, -6.8, u + 1.5, -5.4],
                Color.SIGN,
                Color.WHITE,
                f"{meters}cm",
                font,
            )

        # ground
        draw_rect(surface, transform, [None, 0, None, None], Color.WHITE)

    def draw_creature(
        self,
        surface,
        node_state,
        frame,
        transform,
        draw_labels: bool,
        should_draw_clock: bool,
    ):
        if draw_labels:
            self.draw_environment(surface, transform)

        cell_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA, 32)
        for x in range(self.creature.sim.width):
            for y in range(self.creature.sim.height):
                self.draw_cell(cell_surface, node_state, frame, transform, x, y)
        surface.blit(cell_surface, (0, 0))

        if draw_labels:
            tx, ty, s = transform
            avg_x = np.mean(node_state[:, :, 0], axis=(0, 1))
            lx = tx + avg_x * s
            ly = 20
            lw = 100
            lh = 36
            ar = 15
            pygame.draw.rect(surface, (255, 0, 0), (lx - lw / 2, ly, lw, lh))
            pygame.draw.polygon(
                surface,
                (255, 0, 0),
                ((lx, ly + lh + ar), (lx - ar, ly + lh), (lx + ar, ly + lh)),
            )
            center_text(
                surface,
                f"{dist_to_text(avg_x, True, self.creature.sim.units_per_meter)}",
                lx,
                ly + 18,
                Color.WHITE,
                self.ui.small_font,
            )

        ratio = 1 - frame / self.creature.sim.trial_time

        if should_draw_clock:
            draw_clock(
                surface,
                (40, 40, 32),
                ratio,
                str(math.ceil(ratio * self.creature.sim.trial_time / self.ui.fps)),
                self.ui.small_font,
            )

    def draw_icon(self, icon_dim, bg_color, beat_fade_time: int) -> Surface:
        icon: Surface = pygame.Surface(icon_dim, pygame.SRCALPHA, 32)
        icon.fill(bg_color)
        transform = [
            icon_dim[0] / 2,
            icon_dim[0] / (self.creature.sim.width + 2),
            icon_dim[0] / (self.creature.sim.height + 2.85),
        ]
        self.draw_creature(
            icon, self.creature.calmState, beat_fade_time, transform, False, False
        )
        r = icon_dim[0] * 0.09
        r2 = icon_dim[0] * 0.12
        pygame.draw.circle(
            icon,
            species_to_color(self.creature.species, self.ui),
            (icon_dim[0] - r2, r2),
            r,
        )

        return icon

    def traits_to_color(self, dna, x, y, frame):
        beat = self.creature.sim.frame_to_beat(frame)
        beat_prev = (
            beat + self.creature.sim.beats_per_cycle - 1
        ) % self.creature.sim.beats_per_cycle
        prog = self.creature.sim.frame_to_beat_fade(frame)

        location_index = x * self.creature.sim.height + y
        dna_index = (
            location_index * self.creature.sim.beats_per_cycle + beat
        ) * self.creature.sim.traits_per_box
        dna_index_prev = (
            location_index * self.creature.sim.beats_per_cycle + beat_prev
        ) * self.creature.sim.traits_per_box

        traits = dna[dna_index : dna_index + self.creature.sim.traits_per_box]
        traits_prev = dna[
            dna_index_prev : dna_index_prev + self.creature.sim.traits_per_box
        ]
        traits = array_lerp(traits_prev, traits, prog)

        red = min(max(int(128 + traits[0] * 128), 0), 255)
        green = min(max(int(128 + traits[1] * 128), 0), 255)
        alpha = min(
            max(int(155 + traits[2] * 100), 64), 255
        )  # alpha can't go below 25%
        color_result = (red, green, 255, alpha)

        if self.creature.codon_with_change is not None:
            next_green = 0
            if (
                dna_index
                <= self.creature.codon_with_change
                < dna_index + self.creature.sim.traits_per_box
            ):
                next_green = 1

            prev_green = 0
            if (
                dna_index_prev
                <= self.creature.codon_with_change
                < dna_index_prev + self.creature.sim.traits_per_box
            ):
                prev_green = 1

            green_ness = lerp(prev_green, next_green, prog)
            color_result = list_lerp(color_result, (0, 255, 0, 255), green_ness)

        return color_result
