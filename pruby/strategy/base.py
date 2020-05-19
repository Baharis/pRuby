from .reading import *
from .backfitting import *
from .peakfitting import *
from .correcting import *
from .translating import *
from .drawing import *


class Strategy:
    readers = [RawTxtReadingStrategy(), MetaTxtReadingStrategy()]
    backfitters = [HuberBackfittingStrategy(), SateliteBackfittingStrategy()]
    peakfitters = [GaussianPeakfittingStrategy(),
                   PseudovoigtPeakfittingStrategy(), CamelPeakfittingStrategy()]
    correctors = [VosR1CorrectingStrategy(), RaganR1CorrectingStrategy()]
    translators = [LiuTranslatingStrategy(), PiermariniTranslatingStrategy(),
                   MaoTranslatingStrategy(), WeiTranslatingStrategy()]
    drawers = [ComplexDrawingStrategy(), SimpleDrawingStrategy()]

    def __init__(self, calc):
        self.calc = calc
        self.reader = self.readers[0]
        self.backfitter = self.backfitters[0]
        self.peakfitter = self.peakfitters[0]
        self.corrector = self.correctors[0]
        self.translator = self.translators[0]
        self.drawer = self.drawers[0]

    def set(self, reading='', backfitting='', peakfitting='',
            correcting='', translating='', drawing=''):
        for r in self.readers:
            self.reader = r if r.name == reading else self.reader
        for b in self.backfitters:
            self.backfitter = b if b.name == backfitting else self.backfitter
        for p in self.peakfitters:
            self.peakfitter = p if p.name == peakfitting else self.peakfitter
        for c in self.correctors:
            self.corrector = c if c.name == correcting else self.corrector
        for t in self.translators:
            self.translator = t if t.name == translating else self.translator
        for d in self.drawers:
            self.drawer = d if d.name == drawing else self.drawer

    def read(self):
        self.reader.read(self.calc)

    def backfit(self):
        self.backfitter.backfit(self.calc)

    def peakfit(self):
        self.peakfitter.peakfit(self.calc)

    def correct(self):
        self.corrector.correct(self.calc)

    def translate(self):
        self.translator.translate(self.calc)

    def draw(self):
        self.drawer.draw(self.calc)
