import math


class EnergyGrid:
    def __init__(self, min_energy: float, max_energy: float, point_count: int, is_log: bool) -> None:
        if min_energy > max_energy:
            raise ValueError(f'max_energy ({max_energy}) is less than min_energy ({min_energy})')
        if point_count <= 0:
            raise ValueError(f'points count <= 0: {point_count}')
        if min_energy < 0:
            raise ValueError(f'min_energy < 0: {min_energy}')
        self.min_energy = min_energy
        self.max_energy = max_energy
        self.point_count = point_count
        self.is_log = is_log
        self.points = self._calc_grid()
    
    def _calc_grid(self):
        if self.is_log:
            de = ((math.log(self.max_energy) - math.log(self.min_energy)) / (self.point_count - 1) 
                  if self.point_count > 1 else 0)
            lme = math.log(self.min_energy)
            return [math.exp(lme + i*de) for i in range(self.point_count)]
        else:
            de = (self.max_energy - self.min_energy) / (self.point_count - 1) if self.point_count > 1 else 0
            return [self.min_energy + i*de for i in range(self.point_count)]

    @property
    def grid(self):
        return self.points

    