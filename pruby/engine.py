from .strategies import \
    ReadingStrategies, \
    BackfittingStrategies, \
    PeakfittingStrategies, \
    CorrectingStrategies, \
    TranslatingStrategies, \
    DrawingStrategies


class Engine:
    def __init__(self, calc):
        self.calc = calc
        self.reader = ReadingStrategies.default()
        self.backfitter = BackfittingStrategies.default()
        self.peakfitter = PeakfittingStrategies.default()
        self.corrector = CorrectingStrategies.default()
        self.translator = TranslatingStrategies.default()
        self.drawer = DrawingStrategies.default()

    def set_strategy(self, reading: str = '', backfitting: str = '',
                     peakfitting: str = '', correcting: str = '',
                     translating: str = '', drawing: str = '') -> None:
        """
        Sets engine strategy using strategy name string. To change any of the
        strategies directly using a `Strategy` object, set the value of one of:
        `self.reader`, `self.backfitter`, `self.peakfitter`, `self.corrector`,
        `self.translator` or `self.drawer` to a desired class instance instead.

        :param reading: If given, set `self.reader` to an instance
            of class registered in `ReadingStrategies` under this name.
        :param backfitting: If given, set `self.backfitter` to an instance
            of class registered in `BackfittingStrategies` under this name.
        :param peakfitting: If given, set `self.peakfitter` to an instance
            of class registered in `PeakfittingStrategies` under this name.
        :param correcting: If given, set `self.corrector` to an instance
            of class registered in `CorrectingStrategies` under this name.
        :param translating: If given, set `self.translator` to an instance
            of class registered in `TranslatingStrategies` under this name.
        :param drawing: If given, set `self.drawer` to an instance
            of class registered in `DrawingStrategies` under this name.
        """
        if reading:
            self.reader = ReadingStrategies.create(name=reading)
        if backfitting:
            self.backfitter = BackfittingStrategies.create(name=backfitting)
        if peakfitting:
            self.peakfitter = PeakfittingStrategies.create(name=peakfitting)
        if correcting:
            self.corrector = CorrectingStrategies.create(name=correcting)
        if translating:
            self.translator = TranslatingStrategies.create(name=translating)
        if drawing:
            self.drawer = DrawingStrategies.create(name=drawing)

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
