# import pandas as pd
import uproot
import os
import json
import numpy as np
from pymcabc.generate_event import GENEvents
from pymcabc.particle import Particle
from pymcabc.decay_particle import DecayParticle
from pymcabc.detector import Detector


class SaveEvent:
    """
    class of saving events
    Parameters:
        Nevent (int): number of events to generate
        boolDecay (bool): optional.  decay particles or not
        boolDetector (bool): optional.  gaussian smearing on particles
        boolTruth (bool): optional.  save truth events
    """

    def __init__(
        self,
        Nevent: int,
        boolDecay: bool = True,
        boolDetector: bool = True,
        boolTruth: bool = True,
        detector_sigma=1.0,
        detector_factor=1.0,
    ):
        """
         saving events
        Parameters:
            Nevent (int): number of events to generate
            boolDecay (bool): optional.  decay particles or not
            boolDetector (bool): optional.  gaussian smearing on particles
            boolTruth (bool): optional.  save truth events
        """
        self.Nevent = Nevent
        self.detector_sigma = detector_sigma
        self.detector_factor = detector_factor

        with open("library.json", "r") as f:
            library = json.load(f)
        self.w_max = library["w_max"][0]
        self.Ecm = library["Ecm"][0] 
        input_string = library["process"][0]
        input_string = input_string.replace(" > ", " ")
        input_string = input_string.split(" ")
        self.output_1 = input_string[2]
        self.output_2 = input_string[3]
        if self.output_1 == self.output_2:
            self.output_1 = self.output_1 + "_1"
            self.output_2 = self.output_2 + "_2"

        self.decay_process = library["decay_process"]
        if self.decay_process[0] != "NaN":
            decay_split = self.decay_process[0].replace(" > ", " ")
            decay_split = decay_split.split(" ")
            self.decayed1 = decay_split[1]
            self.decayed2 = decay_split[2]
        (
            self.p1_e,
            self.p1_px,
            self.p1_py,
            self.p1_pz,
            self.p2_e,
            self.p2_px,
            self.p2_py,
            self.p2_pz,
        ) = GENEvents(self.Nevent).gen_events()
        self.top1 = Particle(self.p1_e, self.p1_px, self.p1_py, self.p1_pz)
        self.top2 = Particle(self.p2_e, self.p2_px, self.p2_py, self.p2_pz)

        self.boolDecay = boolDecay
        self.boolDetector = boolDetector
        self.boolTruth = boolTruth

    def to_root(self, name: str = "ABC_events.root"):
        """function to save event as ROOT file
        Parameters:
            name (str): name of root file

        """

        check_extension = os.path.splitext(name)
        if check_extension[1] != ".root":
            raise ValueError("Output supported with .root extension only") 

        if self.boolTruth == True:
            file = uproot.recreate("truth_" + name)
            file["events"] = {
                self.output_1 + "_E": self.top1.E,
                self.output_1 + "_Px": self.top1.px,
                self.output_1 + "_Py": self.top1.py,
                self.output_1 + "_Pz": self.top1.pz,
                self.output_2 + "_E": self.top2.E,
                self.output_2 + "_Px": self.top2.px,
                self.output_2 + "_Py": self.top2.py,
                self.output_2 + "_Pz": self.top2.pz,
            }

        if self.boolDecay == False or self.decay_process == "NaN":
            if self.boolDetector == True:
                self.top1 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(self.top1)
                self.top2 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(self.top2)

            file = uproot.recreate(name)
            file["events"] = {
                self.output_1 + "_E": self.top1.E,
                self.output_1 + "_Px": self.top1.px,
                self.output_1 + "_Py": self.top1.py,
                self.output_1 + "_Pz": self.top1.pz,
                self.output_2 + "_E": self.top2.E,
                self.output_2 + "_Px": self.top2.px,
                self.output_2 + "_Py": self.top2.py,
                self.output_2 + "_Pz": self.top2.pz,
            }
        else:
            file = uproot.recreate(name)
            top1 = self.top1
            top2 = self.top2
            decay1, decay2 = DecayParticle().prepare_decay(top1)
            decay3, decay4 = DecayParticle().prepare_decay(top2)
            if self.boolDetector == True:
                #if decay1.px[0] == -9 and decay1.E[0] == -9:
                self.top1 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(self.top1)
                #if decay2.px[0] == -9 and decay2.E[0] == -9:
                self.top2 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(self.top2)
                # self.top1 = Detector(self.detector_sigma,self.detector_factor).gauss_smear(self.top1)
                # self.top2 = Detector(self.detector_sigma,self.detector_factor).gauss_smear(self.top2)

                decay1 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(decay1)
                decay2 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(decay2)
                decay3 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(decay3)
                decay4 = Detector(
                    self.detector_sigma, self.detector_factor
                ).gauss_smear(decay4)


            file["events"] = {
                self.output_1 + "_E": self.top1.E,
                self.output_1 + "_Px": self.top1.px,
                self.output_1 + "_Py": self.top1.py,
                self.output_1 + "_Pz": self.top1.pz,
                self.output_1 + "_E_decay_" + self.decayed1: decay1.E,
                self.output_1 + "_Px_decay_" + self.decayed1: decay1.px,
                self.output_1 + "_Py_decay_" + self.decayed1: decay1.py,
                self.output_1 + "_Pz_decay_" + self.decayed1: decay1.pz,
                self.output_1 + "_E_decay_" + self.decayed2: decay2.E,
                self.output_1 + "_Px_decay_" + self.decayed2: decay2.px,
                self.output_1 + "_Py_decay_" + self.decayed2: decay2.py,
                self.output_1 + "_Pz_decay_" + self.decayed2: decay2.pz,
                self.output_2 + "_E": self.top2.E,
                self.output_2 + "_Px": self.top2.px,
                self.output_2 + "_Py": self.top2.py,
                self.output_2 + "_Pz": self.top2.pz,
                self.output_2 + "_E_decay_" + self.decayed1: decay3.E,
                self.output_2 + "_Px_decay_" + self.decayed1: decay3.px,
                self.output_2 + "_Py_decay_" + self.decayed1: decay3.py,
                self.output_2 + "_Pz_decay_" + self.decayed1: decay3.pz,
                self.output_2 + "_E_decay_" + self.decayed2: decay4.E,
                self.output_2 + "_Px_decay_" + self.decayed2: decay4.px,
                self.output_2 + "_Py_decay_" + self.decayed2: decay4.py,
                self.output_2 + "_Pz_decay_" + self.decayed2: decay4.pz,
            }
