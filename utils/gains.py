class GainsEquator:
    def setup(self):
        self.full_gain = self.q_e * self.M_gain * self.R_gain * self.G_magic * self.divider * self.gain_out
        self.converter = self.mV_2_V * self.ns_2_s
        self.resulting_multiplier = self.converter / self.full_gain

    def __init__(self):
        self.q_e = 1.6E-19
        self.M_gain = 1E2
        self.R_gain = 1E4
        self.G_magic = 2.43
        self.divider = 0.5
        self.gain_out = 10
        self.mV_2_V = 1E-3
        self.ns_2_s = 1E-9

        self.full_gain = None
        self.converter = None
        self.resulting_multiplier = None

        self.setup()


class Gains_T15_34:
    def setup(self):
        self.full_gain = self.q_e * self.M_gain * self.R_gain * self.gain_out
        self.converter = self.mV_2_V * self.ns_2_s
        self.resulting_multiplier = self.converter / self.full_gain

    def __init__(self):
        self.M_gain = 1e2
        self.q_e = 1.6E-19
        self.gain_out = 10
        self.R_gain = 1E4

        self.mV_2_V = 1E-3
        self.ns_2_s = 1E-9

        self.full_gain = None
        self.converter = None
        self.resulting_multiplier = None

        self.setup()


class Gains_T15_35(Gains_T15_34):
    def setup(self):
        self.full_gain = self.q_e * self.M_gain * self.R_gain * self.gain_out
        self.converter = self.mV_2_V * self.ns_2_s
        self.resulting_multiplier = self.converter / self.full_gain

    def __init__(self):
        super().__init__()
        self.R_gain = 5E3

        self.setup()
