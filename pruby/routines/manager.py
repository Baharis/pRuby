from .reading import RawTxtReadingRoutine, MetaTxtReadingRoutine
from .fitting import HuberBackFittingRoutine, SateliteBackFittingRoutine, \
    GaussianPeakFittingRoutine, PseudovoigtPeakFittingRoutine,\
    CamelPeakFittingRoutine
from .correcting import VosR1CorrectionRoutine, RaganR1CorrectionRoutine, \
    NoneCorrectionRoutine
from .translating import LiuTranslationRoutine, WeiTranslationRoutine, \
    MaoTranslationRoutine, PiermariniTranslationRoutine
from .drawing import TraditionalDrawingRoutine, SimpleDrawingRoutine


class RoutineManager:
    """
    A class to menage all routines. Its utility includes building routines,
    remembering which routines are defined and so on.
    """
    def __init__(self):
        self.roles = ['reading', 'backfitting', 'peakfitting',
                      'correcting', 'translating', 'drawing']
        self.dict = {role: [] for role in self.roles}

    @property
    def default(self):
        return {role: self.dict[role][0] for role in self.roles}

    @property
    def names(self):
        return {role: [r.name for r in self.dict[role]] for role in self.roles}

    def select(self, role, name=''):
        if name is '':
            return self.default[role]
        else:
            for routine in self.dict[role]:
                if routine.name == name:
                    return routine
        raise KeyError('No type "{} name "{}" routine found'.format(role, name))

    def subscribe(self, role, routine):
        self.dict[role].append(routine)


routine_manager = RoutineManager()
routine_manager.subscribe('reading', RawTxtReadingRoutine())
routine_manager.subscribe('reading', MetaTxtReadingRoutine())
routine_manager.subscribe('backfitting', HuberBackFittingRoutine)
routine_manager.subscribe('backfitting', SateliteBackFittingRoutine)
routine_manager.subscribe('peakfitting', GaussianPeakFittingRoutine)
routine_manager.subscribe('peakfitting', PseudovoigtPeakFittingRoutine)
routine_manager.subscribe('peakfitting', CamelPeakFittingRoutine)
routine_manager.subscribe('correcting', VosR1CorrectionRoutine)
routine_manager.subscribe('correcting', RaganR1CorrectionRoutine)
routine_manager.subscribe('correcting', NoneCorrectionRoutine)
routine_manager.subscribe('translating', LiuTranslationRoutine)
routine_manager.subscribe('translating', WeiTranslationRoutine)
routine_manager.subscribe('translating', MaoTranslationRoutine)
routine_manager.subscribe('translating', PiermariniTranslationRoutine)
routine_manager.subscribe('drawing', TraditionalDrawingRoutine())
routine_manager.subscribe('drawing', SimpleDrawingRoutine())