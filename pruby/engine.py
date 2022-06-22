


class Engine:
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
        self._set_strategy(reading, 'reader')
        self._set_strategy(backfitting, 'backfitter')
        self._set_strategy(peakfitting, 'peakfitter')
        self._set_strategy(correcting, 'corrector')
        self._set_strategy(translating, 'translator')
        self._set_strategy(drawing, 'drawer')

    def _set_strategy(self, key, strategy_type):
        if key is '':
            return
        for strategy in getattr(self, strategy_type + 's'):
            if strategy.name == key:
                setattr(self, strategy_type, strategy)
                return
        raise KeyError('Unknown strategy name "{}"'.format(key))

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