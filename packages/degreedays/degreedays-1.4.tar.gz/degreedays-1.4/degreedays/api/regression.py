
import sys
import re
from degreedays._private import Immutable, XmlElement
import degreedays._private as private
import degreedays.time
from degreedays.api.data import Temperature, TemperatureUnit, Location, \
    DatedDataSet, DataValue, SourceDataError
import degreedays.api

__all__ = ['DayNormalization', 'ExpectedCorrelation', 'PredictorType',
    'RegressionTag', 'InputPeriod', 'InputData', 'ExtraPredictorSpec',
    'RegressionSpec', 'RegressionTestPlan', 'RegressionRequest',
    'RegressionComponent', 'BaseloadRegressionComponent',
    'ExtraRegressionComponent', 'DegreeDaysRegressionComponent',
    'RegressionComponents', 'Regression', 'RegressionResponse', 'RegressionApi']

# See TemperatureUnit for an explanation of this pattern.  We use it for all
# enums.
class _DayNormalizationMetaclass(type):
    def __iter__(cls):
        for u in (DayNormalization.WEIGHTED, DayNormalization.UNWEIGHTED,
                DayNormalization.NONE):
            yield u
_DayNormalizationSuper = _DayNormalizationMetaclass('_DayNormalizationSuper',
    (Immutable,), {'__slots__': ()})
class DayNormalization(_DayNormalizationSuper):
    __slots__ = ('__name', '__nameUpper')
    # Set later, but defined here for Intellisense.
    WEIGHTED = None
    UNWEIGHTED = None
    NONE = None
    def __init__(self, name):
        if ((name == 'Weighted' and DayNormalization.WEIGHTED is None) or
                (name == 'Unweighted' and DayNormalization.UNWEIGHTED is None) or
                (name == 'None' and DayNormalization.NONE is None)):
            self.__name = name
        else:
            raise TypeError('This is not built for direct '
                'instantiation.  Please use DayNormalization.WEIGHTED, '
                'DayNormalization.UNWEIGHTED, or DayNormalization.NONE.')
        self.__nameUpper = name.upper()
    def _equalityFields(self):
        return self.__name
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'DayNormalization.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('DayNormalization').setValue(self.__name)
    @classmethod
    def _check(cls, param, paramName='dayNormalization'):
        if type(param) is not DayNormalization:
            raise TypeError(private.wrongTypeString(param, paramName,
                DayNormalization, 'DayNormalization.WEIGHTED, '
                'DayNormalization.UNWEIGHTED, or DayNormalization.NONE.'))
        return param
DayNormalization.WEIGHTED = DayNormalization('Weighted')
DayNormalization.UNWEIGHTED = DayNormalization('Unweighted')
DayNormalization.NONE = DayNormalization('None')


class _ExpectedCorrelationMetaclass(type):
    def __iter__(cls):
        for u in (ExpectedCorrelation.POSITIVE, ExpectedCorrelation.NEGATIVE,
                ExpectedCorrelation.POSITIVE_OR_NEGATIVE):
            yield u
_ExpectedCorrelationSuper = _ExpectedCorrelationMetaclass(
    '_ExpectedCorrelationSuper', (Immutable,), {'__slots__': ()})
class ExpectedCorrelation(_ExpectedCorrelationSuper):
    __slots__ = ('__name', '__nameUpper')
    # Set later, but defined here for Intellisense.
    POSITIVE = None
    NEGATIVE = None
    POSITIVE_OR_NEGATIVE = None
    def __init__(self, name):
        if ((name == 'Positive' and ExpectedCorrelation.POSITIVE is None) or
                (name == 'Negative' and ExpectedCorrelation.NEGATIVE is None)):
            self.__name = name
            self.__nameUpper = name.upper()
        elif (name == 'PositiveOrNegative' and
                ExpectedCorrelation.POSITIVE_OR_NEGATIVE is None):
            self.__name = name
            self.__nameUpper = 'POSITIVE_OR_NEGATIVE'
        else:
            raise TypeError('This is not built for direct instantiation.  '
                'Please use ExpectedCorrelation.POSITIVE, '
                'ExpectedCorrelation.NEGATIVE, or '
                'ExpectedCorrelation.POSITIVE_OR_NEGATIVE.')
    def _equalityFields(self):
        return self.__name
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'ExpectedCorrelation.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('ExpectedCorrelation').setValue(self.__name)
    @classmethod
    def _check(cls, param, paramName='expectedCorrelation'):
        if type(param) is not ExpectedCorrelation:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExpectedCorrelation, 'ExpectedCorrelation.POSITIVE, '
                'ExpectedCorrelation.NEGATIVE, or '
                'ExpectedCorrelation.POSITIVE_OR_NEGATIVE.'))
        return param
ExpectedCorrelation.POSITIVE = ExpectedCorrelation('Positive')
ExpectedCorrelation.NEGATIVE = ExpectedCorrelation('Negative')
ExpectedCorrelation.POSITIVE_OR_NEGATIVE = \
    ExpectedCorrelation('PositiveOrNegative')


class _PredictorTypeMetaclass(type):
    def __iter__(cls):
        for u in (PredictorType.CUMULATIVE, PredictorType.AVERAGE):
            yield u
_PredictorTypeSuper = _PredictorTypeMetaclass('_PredictorTypeSuper',
    (Immutable,), {'__slots__': ()})
class PredictorType(_PredictorTypeSuper):
    __slots__ = ('__name', '__nameUpper')
    # Set later, but defined here for Intellisense.
    CUMULATIVE = None
    AVERAGE = None
    def __init__(self, name):
        if ((name == 'Cumulative' and PredictorType.CUMULATIVE is None) or
                (name == 'Average' and PredictorType.AVERAGE is None)):
            self.__name = name
        else:
            raise TypeError('This is not built for direct '
                'instantiation.  Please use PredictorType.CUMULATIVE or '
                'PredictorType.AVERAGE.')
        self.__nameUpper = name.upper()
    def _equalityFields(self):
        return self.__name
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'PredictorType.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('PredictorType').setValue(self.__name)
    @classmethod
    def _check(cls, param, paramName='predictorType'):
        if type(param) is not PredictorType:
            raise TypeError(private.wrongTypeString(param, paramName,
                PredictorType,
                'PredictorType.CUMULATIVE or PredictorType.AVERAGE.'))
        return param
PredictorType.CUMULATIVE = PredictorType('Cumulative')
PredictorType.AVERAGE = PredictorType('Average')


class _RegressionTagMetaclass(type):
    def __iter__(cls):
        for u in (RegressionTag.SHORTLIST, RegressionTag.NOTABLE_OTHER,
                RegressionTag.REQUESTED, RegressionTag.IN_SHORTLIST_RANGE):
            yield u
_RegressionTagSuper = _RegressionTagMetaclass('_RegressionTagSuper',
    (Immutable,), {'__slots__': ()})
class RegressionTag(_RegressionTagSuper):
    __slots__ = ('__name', '__nameUpper')
    # Set later, but defined here for Intellisense.
    SHORTLIST = None
    NOTABLE_OTHER = None
    REQUESTED = None
    IN_SHORTLIST_RANGE = None
    def __init__(self, name):
        if ((name == 'Shortlist' and RegressionTag.SHORTLIST is None) or
                (name == 'Requested' and RegressionTag.REQUESTED is None)):
            self.__name = name
            self.__nameUpper = name.upper()
        elif (name == 'NotableOther' and RegressionTag.NOTABLE_OTHER is None):
            self.__name = name
            self.__nameUpper = 'NOTABLE_OTHER'
        elif (name == 'InShortlistRange' and
              RegressionTag.IN_SHORTLIST_RANGE is None):
            self.__name = name
            self.__nameUpper = 'IN_SHORTLIST_RANGE'
        else:
            raise TypeError('This is not built for direct '
                'instantiation.  Please use RegressionTag.SHORTLIST, '
                'RegressionTag.NOTABLE_OTHER, RegressionTag.REQUESTED, or '
                'RegressionTag.IN_SHORTLIST_RANGE.')
    def _equalityFields(self):
        return self.__name
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'RegressionTag.' + self.__nameUpper
    @classmethod
    def _check(cls, param, paramName='regressionTag'):
        if type(param) is not RegressionTag:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionTag, 'RegressionTag.SHORTLIST, '
                'RegressionTag.NOTABLE_OTHER, RegressionTag.REQUESTED, or '
                'RegressionTag.IN_SHORTLIST_RANGE.'))
        return param
RegressionTag.SHORTLIST = RegressionTag('Shortlist')
RegressionTag.NOTABLE_OTHER = RegressionTag('NotableOther')
RegressionTag.REQUESTED = RegressionTag('Requested')
RegressionTag.IN_SHORTLIST_RANGE = RegressionTag('InShortlistRange')


_MAX_EXTRA_PREDICTORS = 2
_EXTRA_PREDICTOR_KEY_REGEXP_STRING = '[-_.a-zA-Z0-9]{1,60}$'
_EXTRA_PREDICTOR_KEY_REGEXP = re.compile(_EXTRA_PREDICTOR_KEY_REGEXP_STRING)



def _checkExtraPredictorKey(key, errorMessageStart=''):
    if not private.isString(key):
        raise TypeError('%sExtra-predictor keys must be strings.' %
            errorMessageStart)
    if not _EXTRA_PREDICTOR_KEY_REGEXP.match(key):
        raise ValueError('%sInvalid extra-predictor key (%r) - it should match '
            'the regular expression %s.' % (errorMessageStart,
                private.logSafe(key), _EXTRA_PREDICTOR_KEY_REGEXP_STRING))
    return key


class InputPeriod(Immutable):
    __slots__ = ('__dayRange', '__usage', '__extraPredictorsOrNone')
    def __init__(self, dayRange, usage, extraPredictorsOrNone=None):
        self.__dayRange = degreedays.time.DayRange._check(dayRange)
        self.__usage = private.checkNumeric(usage, 'usage')
        if extraPredictorsOrNone is None:
            self.__extraPredictorsOrNone = None
        else:
            dictCopy = private.checkDict(
                extraPredictorsOrNone, 'extraPredictorsOrNone').copy()
            if len(dictCopy) > _MAX_EXTRA_PREDICTORS:
                raise ValueError('Cannot have more than %d extra predictors - '
                    '%d is too many.' % (_MAX_EXTRA_PREDICTORS, len(dictCopy)))
            for key, value in private.getDictItemsIterable(dictCopy):
                _checkExtraPredictorKey(key)
                private.checkNumeric(value, 'An extra-predictor value')
            self.__extraPredictorsOrNone = dictCopy
    def _equalityFields(self):
        # Order won't matter for equality comparisons of the dict
        return (self.__dayRange, self.__usage, self.__extraPredictorsOrNone)
    def __hash__(self):
        h = hash((self.__class__, self.__dayRange, self.__usage))
        if self.__extraPredictorsOrNone is not None:
            h = private.getDictHash(self.__extraPredictorsOrNone, h)
        return h
    @property
    def dayRange(self):
        return self.__dayRange
    @property
    def usage(self):
        return self.__usage
    @property
    def extraPredictorCount(self):
        if self.__extraPredictorsOrNone is None:
            return 0
        return len(self.__extraPredictorsOrNone)
    @property
    def extraPredictorKeys(self):
        # As of python 3.7 dicts are ordered by insertion order, which is what
        # we want for usability (though it's not essential).  So we don't do
        # anything extra to try to preserve insertion order.
        if self.__extraPredictorsOrNone is None:
            return ()
        return tuple(self.__extraPredictorsOrNone)
    def getExtraPredictor(self, key):
        if self.__extraPredictorsOrNone is None:
            raise KeyError(
                'This InputPeriod does not have any extra predictors.')
        else:
            # Following will throw a KeyError if key isn't found.
            return self.__extraPredictorsOrNone[key]
    def _extraPredictorsKeyEqualsOrderUnimportant(self, inputPeriod):
        if self.__extraPredictorsOrNone is None:
            return inputPeriod.__extraPredictorsOrNone is None
        return ((len(self.__extraPredictorsOrNone) ==
                len(inputPeriod.__extraPredictorsOrNone)) and
            all(k in self.__extraPredictorsOrNone for
                k in inputPeriod.__extraPredictorsOrNone))
    def __str__(self):
        s = []
        if len(self.__dayRange) == 1:
            s.append(str(self.__dayRange.first))
        else:
            s.append(str(self.__dayRange))
        s.append(': %g' % self.__usage)
        if self.__extraPredictorsOrNone is not None:
            for key, value in private.getDictItemsIterable(
                    self.__extraPredictorsOrNone):
                s.append(', %s %g' % (key, value))
        return ''.join(s)
    def __repr__(self):
        if self.__extraPredictorsOrNone is None:
            return 'InputPeriod(%r, %r)' % (self.__dayRange, self.__usage)
        else:
            return ('InputPeriod(%r, %r, %r)' %
                (self.__dayRange, self.__usage, self.__extraPredictorsOrNone))
    def _toXml(self):
        e = XmlElement('InputPeriod').addChild(self.__dayRange._toXml())
        e.newChild('Usage').setValue(self.__usage)
        if self.__extraPredictorsOrNone is not None:
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorsOrNone):
                e.newChild('ExtraPredictor').addAttribute('key', k).setValue(v)
        return e
    @classmethod
    def _check(cls, param, paramName="inputPeriod"):
        if type(param) is not InputPeriod:
            raise TypeError(private.wrongTypeString(param, paramName,
                InputPeriod))
        return param


class InputData(Immutable):
    __slots__ = ('__inputPeriods',)
    def __mustAddMessage(self, minimum, added, extraPredictors):
        s = []
        s.append('%d InputPeriod ' % added)
        if added != 1:
            s.append('items ')
        s.append('is not enough. ')
        if extraPredictors > 0:
            s.append('With %d extra predictor' % extraPredictors)
            if extraPredictors > 1:
                s.append('s')
            s.append(' y')
        else:
            s.append('Y')
        s.append(('ou must have at least %d (although this is just a bare '
            'minimum to generate regressions - realistically you really want '
            'at least %d for useful results).') %
            (minimum, 10 + extraPredictors))
        return ''.join(s)
    def __init__(self, *args):
        periods = []
        def add(item):
            index = len(periods)
            if index >= 1096:
                raise ValueError(
                    'Cannot have more than 1096 InputPeriod items.')
            if isinstance(item, InputPeriod):
                if index > 0:
                    last = periods[index - 1]
                    if not item.dayRange.first > last.dayRange.last:
                        raise ValueError(('Problem DayRange at index %d (%s) - '
                            'it must start after the previous DayRange (%s) '
                            'finished.') %
                                (index, item.dayRange, last.dayRange))
                    if not item._extraPredictorsKeyEqualsOrderUnimportant(last):
                        raise ValueError(('The item at index %d has different '
                            'extra-predictor keys %s to previous items %s.  If '
                            'adding extra predictors the same predictors must '
                            'be present for each and every InputPeriod.  If '
                            'you are missing extra-predictor data for some '
                            'periods, just leave those periods out of the '
                            'InputData.') % (index, item.extraPredictorKeys,
                                last.extraPredictorKeys))
                periods.append(item)
            elif private.isString(item):
                # Have to be careful with strings cos they look like a
                # sequence but will cause a stack overflow, see:
                # https://stackoverflow.com/questions/1835018/
                InputPeriod._check(item,
                    'An item passed into the InputData constructor')
            else:
                # assume it's a sequence, just let it throw error if not
                # Could do a try catch too, so can give a useful error
                # message if it's not a sequence or a InputPeriod.
                for innerItem in item:
                    add(innerItem)
        for arg in args:
            add(arg)
        length = len(periods)
        if length == 0:
            raise ValueError(self.__mustAddMessage(3, 0, 0))
        last = periods[-1]
        noExtraPredictors = last.extraPredictorCount
        minimum = 3 + noExtraPredictors
        if length < minimum:
            raise ValueError(self.__mustAddMessage(
                minimum, length, noExtraPredictors))
        self.__inputPeriods = tuple(periods)
    def _equalityFields(self):
        return self.__inputPeriods
    @property
    def periods(self):
        return self.__inputPeriods
    @property
    def extraPredictorKeys(self):
        return self.__inputPeriods[0].extraPredictorKeys
    @property
    def fullRange(self):
        return degreedays.time.DayRange(self.__inputPeriods[0].dayRange.first,
            self.__inputPeriods[-1].dayRange.last)
    def __str__(self):
        s = []
        s.append('InputData(')
        s.append(str(len(self.__inputPeriods)))
        s.append(' periods from (')
        s.append(str(self.__inputPeriods[0]))
        s.append(') to (')
        s.append(str(self.__inputPeriods[-1]))
        s.append('))')
        return ''.join(s)
    def __repr__(self):
        return 'InputData(%r)' % (self.__inputPeriods,)
    def _toXml(self):
        e = XmlElement('InputData')
        for p in self.__inputPeriods:
            e.addChild(p._toXml())
        return e
    @classmethod
    def _check(cls, param, paramName="inputData"):
        if type(param) is not InputData:
            raise TypeError(private.wrongTypeString(param, paramName,
                InputData))
        return param


class ExtraPredictorSpec(Immutable):
    __slots__ = ('__predictorType', '__expectedCorrelation')
    def __init__(self, predictorType, expectedCorrelation):
        self.__predictorType = PredictorType._check(predictorType)
        self.__expectedCorrelation = ExpectedCorrelation._check(
            expectedCorrelation)
    def _equalityFields(self):
        return (self.__predictorType, self.__expectedCorrelation)
    @property
    def predictorType(self):
        return self.__predictorType
    @property
    def expectedCorrelation(self):
        return self.__expectedCorrelation
    def _getInnerString(self):
        return '%s, %s' % (self.__predictorType, self.__expectedCorrelation)
    def __str__(self):
        return 'ExtraPredictorSpec(%s)' % self._getInnerString()
    def __repr__(self):
        return ('ExtraPredictorSpec(%r, %r)' %
            (self.__predictorType, self.__expectedCorrelation))
    def _toXml(self, key):
        e = XmlElement('ExtraPredictorSpec').addAttribute('key', key)
        e.newChild('PredictorType').setValue(self.__predictorType)
        e.newChild('ExpectedCorrelation').setValue(self.__expectedCorrelation)
        return e
    @classmethod
    def _check(cls, param, paramName="extraPredictorSpec"):
        if type(param) is not ExtraPredictorSpec:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExtraPredictorSpec))
        return param


class RegressionSpec(Immutable):
    __slots__ = ('__heatingBaseTemperatureOrNone',
        '__coolingBaseTemperatureOrNone', '__extraPredictorKeys')
    def __init__(self, heatingBaseTemperatureOrNone=None,
            coolingBaseTemperatureOrNone=None,
            extraPredictorKeys=()):
        if heatingBaseTemperatureOrNone is not None:
            Temperature._check(
                heatingBaseTemperatureOrNone, 'heatingBaseTemperatureOrNone')
        if coolingBaseTemperatureOrNone is not None:
            Temperature._check(
                coolingBaseTemperatureOrNone, 'coolingBaseTemperatureOrNone')
            if (heatingBaseTemperatureOrNone is not None and
                    (heatingBaseTemperatureOrNone.unit !=
                        coolingBaseTemperatureOrNone.unit)):
                raise ValueError('If heatingBaseTemperatureOrNone and '
				    'coolingBaseTemperatureOrNone are both supplied, they must '
                    'both have the same TemperatureUnit.')
        self.__heatingBaseTemperatureOrNone = heatingBaseTemperatureOrNone
        self.__coolingBaseTemperatureOrNone = coolingBaseTemperatureOrNone
        if private.isString(extraPredictorKeys):
            # Allow the user to pass a single string.
            epTuple = (extraPredictorKeys,)
        else:
            epTuple = tuple(extraPredictorKeys)
        self.__extraPredictorKeys = private.checkTupleItems(
            epTuple, private.checkString, 'extraPredictorKeys')
        if len(self.__extraPredictorKeys) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('A RegressionSpec cannot have more than %d '
                'extra-predictor keys.' % _MAX_EXTRA_PREDICTORS)
    def _equalityFields(self):
        return (self.__heatingBaseTemperatureOrNone,
            self.__coolingBaseTemperatureOrNone,
            # Don't care about ordering for equality.
            frozenset(self.__extraPredictorKeys))
    @property
    def heatingBaseTemperatureOrNone(self):
        return self.__heatingBaseTemperatureOrNone
    @property
    def coolingBaseTemperatureOrNone(self):
        return self.__coolingBaseTemperatureOrNone
    @property
    def extraPredictorKeys(self):
        # Same order they were passed in with.
        return self.__extraPredictorKeys
    def _appendInnerString(self, s):
        s.append('baseload')
        if self.__heatingBaseTemperatureOrNone is not None:
            s.append(', HDD %s' % self.__heatingBaseTemperatureOrNone)
        if self.__coolingBaseTemperatureOrNone is not None:
            s.append(', CDD %s' % self.__coolingBaseTemperatureOrNone)
        for key in self.__extraPredictorKeys:
            s.append(', ')
            s.append(key)
    def __str__(self):
        s = []
        s.append('RegressionSpec(')
        self._appendInnerString(s)
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = []
        s.append('RegressionSpec(')
        added = False
        if self.__heatingBaseTemperatureOrNone is not None:
            s.append('heatingBaseTemperatureOrNone=%r' %
                self.__heatingBaseTemperatureOrNone)
            added = True
        if self.__coolingBaseTemperatureOrNone is not None:
            if added:
                s.append(', ')
            s.append('coolingBaseTemperatureOrNone=%r' %
                self.__coolingBaseTemperatureOrNone)
            added = True
        if len(self.__extraPredictorKeys) > 0:
            if added:
                s.append(', ')
            # Use repr instead of %r so dict doesn't get interpreted as args.
            s.append('extraPredictorKeys=' + repr(self.__extraPredictorKeys))
        s.append(')')
        return ''.join(s)
    def _toXml(self):
        e = XmlElement('RegressionSpec')
        if self.__heatingBaseTemperatureOrNone is not None:
            e.newChild('HeatingBaseTemperature').setValue(
                self.__heatingBaseTemperatureOrNone._toNumericString())
        if self.__coolingBaseTemperatureOrNone is not None:
            e.newChild('CoolingBaseTemperature').setValue(
                self.__coolingBaseTemperatureOrNone._toNumericString())
        for k in self.__extraPredictorKeys:
            e.newChild('ExtraPredictorKey').setValue(k)
        return e
    @classmethod
    def _check(cls, param, paramName="regressionSpec"):
        if type(param) is not RegressionSpec:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionSpec))
        return param


_MAX_CUSTOM_BASE_TEMPS = 120
_MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS = 60
_MAX_REQUESTED_REGRESSION_SPECS = 60

class RegressionTestPlan(Immutable):
    __slots__ = ('__temperatureUnit', '__dayNormalization',
        '__customTestHeatingBaseTemperaturesOrNone',
        '__customTestCoolingBaseTemperaturesOrNone',
        '__extraPredictorSpecs', '__requestedRegressionSpecs')
    def __getCustomTempsOrNone(self, unit, tempsOrNone, paramName):
        if tempsOrNone is None:
            return None
        cleaned = set()
        for temp in tempsOrNone:
            if type(temp) is Temperature:
                if temp.unit != unit:
                    raise ValueError('All %s items must be specified in %s, '
                        'the unit specified for this RegressionTestPlan.' %
                            (paramName, unit))
                cleaned.add(temp)
            else:
                try:
                    cleaned.add(Temperature(temp, unit))
                except TypeError:
                    _, e, _ = sys.exc_info() # for Python 2.5 compatibility
                    raise TypeError('Problem value in %s: %s' % (paramName, e))
                except ValueError:
                    _, e, _ = sys.exc_info()
                    raise ValueError('Problem value in %s: %s' % (paramName, e))
        return tuple(sorted(cleaned))
    def __init__(self, temperatureUnit,
            dayNormalization=DayNormalization.WEIGHTED,
            customTestHeatingBaseTemperaturesOrNone=None,
            customTestCoolingBaseTemperaturesOrNone=None,
            extraPredictorSpecs={},
            requestedRegressionSpecs=()):
        self.__temperatureUnit = TemperatureUnit._check(temperatureUnit)
        self.__dayNormalization = DayNormalization._check(dayNormalization)
        self.__customTestHeatingBaseTemperaturesOrNone = \
            self.__getCustomTempsOrNone(temperatureUnit,
                customTestHeatingBaseTemperaturesOrNone,
                'customTestHeatingBaseTemperaturesOrNone')
        self.__customTestCoolingBaseTemperaturesOrNone = \
            self.__getCustomTempsOrNone(temperatureUnit,
                customTestCoolingBaseTemperaturesOrNone,
                'customTestCoolingBaseTemperaturesOrNone')
        # Create a defensive copy of the dict for usual reasons but also so the
        # default {} value cannot be modified for future calls.
        self.__extraPredictorSpecs = private.checkDict(
            extraPredictorSpecs, 'extraPredictorSpecs').copy()
        if len(self.__extraPredictorSpecs) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('extraPredictorSpecs has %d extra predictors, when'
                ' the maximum allowed is %d.' %
                    (len(self.__extraPredictorSpecs), _MAX_EXTRA_PREDICTORS))
        for k, v in private.getDictItemsIterable(self.__extraPredictorSpecs):
            _checkExtraPredictorKey(k,
                'Problem key in extraPredictorSpecs dict.  ')
            ExtraPredictorSpec._check(v, 'A value in extraPredictorSpecs dict')
        # Use set to exclude duplicates.  In other libraries we sort, but the
        # order doesn't actually matter so let's keep it simple.
        self.__requestedRegressionSpecs = frozenset(requestedRegressionSpecs)
        for spec in self.__requestedRegressionSpecs:
            if type(spec) is not RegressionSpec:
                raise TypeError('requestedRegressionSpecs must contain only '
                    'RegressionSpec objects.')
            for key in spec.extraPredictorKeys:
                if not key in self.__extraPredictorSpecs:
                    raise ValueError('You have a requested RegressionSpec with '
                        'an extra-predictor key %s, but extraPredictorSpecs '
                        'does not contain an ExtraPredictorSpec for that '
                        'extra-predictor key.' % key)
        if (len(self.__requestedRegressionSpecs) >
                _MAX_REQUESTED_REGRESSION_SPECS):
            raise ValueError('requestedRegressionSpecs has %d items, when the '
                'maximum allowed is %d.' % len(self.__requestedRegressionSpecs,
                    _MAX_REQUESTED_REGRESSION_SPECS))
        def count(tempsOrNone):
            if tempsOrNone is None:
                return 0
            return len(tempsOrNone)
        customHdd = count(self.__customTestHeatingBaseTemperaturesOrNone)
        customCdd = count(self.__customTestCoolingBaseTemperaturesOrNone)
        customTotal = customHdd + customCdd
        if (((self.__customTestHeatingBaseTemperaturesOrNone is None) !=
                (self.__customTestCoolingBaseTemperaturesOrNone is None)) and
                customTotal > _MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS):
            if self.__customTestHeatingBaseTemperaturesOrNone is not None:
                defined = "customTestHeatingBaseTemperaturesOrNone"
                leftDefault = "cooling"
            else:
                defined = "customTestCoolingBaseTemperaturesOrNone"
                leftDefault = "heating"
            raise ValueError('You have defined the %s and left the API to '
                'choose the test %s base temperatures automatically.  In this '
                'case the maximum number of %s allowed is %d, but you have '
                'defined %d which is too many.' % (defined, leftDefault,
                    defined, _MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS, customTotal))
        elif customTotal > _MAX_CUSTOM_BASE_TEMPS:
            raise ValueError('You have defined %d custom test heating base '
                'temperatures and %d custom test cooling base temperatures, '
                'making %d in total, which is greater than the maximum allowed '
                'total of %d.' % (customHdd, customCdd, customTotal,
                    _MAX_CUSTOM_BASE_TEMPS))
    def _equalityFields(self):
        return (self.__temperatureUnit, self.__dayNormalization,
            self.__customTestHeatingBaseTemperaturesOrNone,
            self.__customTestCoolingBaseTemperaturesOrNone,
            self.__extraPredictorSpecs, self.__requestedRegressionSpecs)
    def __hash__(self):
        h = hash((self.__class__, self.__temperatureUnit,
            self.__dayNormalization,
            self.__customTestHeatingBaseTemperaturesOrNone,
            self.__customTestCoolingBaseTemperaturesOrNone,
            self.__requestedRegressionSpecs))
        return private.getDictHash(self.__extraPredictorSpecs, h)
    @property
    def temperatureUnit(self):
        return self.__temperatureUnit
    @property
    def dayNormalization(self):
        return self.__dayNormalization
    @property
    def customTestHeatingBaseTemperaturesOrNone(self):
        return self.__customTestHeatingBaseTemperaturesOrNone
    @property
    def customTestCoolingBaseTemperaturesOrNone(self):
        return self.__customTestCoolingBaseTemperaturesOrNone
    @property
    def extraPredictorKeys(self):
        return tuple(self.__extraPredictorSpecs)
    def getExtraPredictorSpec(self, key):
        # Following will throw a KeyError if key isn't found.
        return self.__extraPredictorSpecs[key]
    @property
    def requestedRegressionSpecs(self):
        return self.__requestedRegressionSpecs
    def __tempsStr(self, temps):
        return str([t.value for t in temps])[1:-1]
    def __str__(self):
        s = []
        s.append('RegressionTestPlan(%s' % self.__temperatureUnit)
        if self.__dayNormalization != DayNormalization.WEIGHTED:
            s.append(', %s' % self.__dayNormalization)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            s.append(', customTestHeatingBaseTemperatures(%s)' %
                self.__tempsStr(self.__customTestHeatingBaseTemperaturesOrNone))
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            s.append(', customTestCoolingBaseTemperatures(%s)' %
                self.__tempsStr(self.__customTestCoolingBaseTemperaturesOrNone))
        if len(self.__extraPredictorSpecs) > 0:
            s.append(', extraPredictorSpecs(')
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorSpecs):
                s.append('%s(%s)' % (k, v._getInnerString()))
                s.append(', ')
            s[-1] = ')'
        if len(self.__requestedRegressionSpecs) > 0:
            s.append(', requestedRegressionSpecs(')
            for spec in self.__requestedRegressionSpecs:
                s.append('(')
                spec._appendInnerString(s)
                s.append(')')
                s.append(', ')
            s[-1] = ')'
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = []
        s.append('RegressionTestPlan(%r' % self.__temperatureUnit)
        if self.__dayNormalization != DayNormalization.WEIGHTED:
            s.append(', dayNormalization=%r' % self.__dayNormalization)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            # Use %s instead of %r cos %r will add quotes around the string.
            s.append(', customTestHeatingBaseTemperaturesOrNone=(%s)' %
                self.__tempsStr(self.__customTestHeatingBaseTemperaturesOrNone))
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            s.append(', customTestCoolingBaseTemperaturesOrNone=(%s)' %
                self.__tempsStr(self.__customTestCoolingBaseTemperaturesOrNone))
        if len(self.__extraPredictorSpecs) > 0:
            s.append(', extraPredictorSpecs=')
            s.append(repr(self.__extraPredictorSpecs))
        if len(self.__requestedRegressionSpecs) > 0:
            s.append(', requestedRegressionSpecs=')
            s.append(repr(self.__requestedRegressionSpecs))
        s.append(')')
        return ''.join(s)
    def _toXml(self):
        e = XmlElement('RegressionTestPlan')
        e.newChild('TemperatureUnit').setValue(self.__temperatureUnit)
        e.newChild('DayNormalization').setValue(self.__dayNormalization)
        def addCustomTemps(temps, parent, name):
            wrapper = XmlElement(name)
            for temp in temps:
                wrapper.newChild('T').setValue(temp._toNumericString())
            parent.addChild(wrapper)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            addCustomTemps(self.customTestHeatingBaseTemperaturesOrNone, e,
                'CustomTestHeatingBaseTemperatures')
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            addCustomTemps(self.customTestCoolingBaseTemperaturesOrNone, e,
                'CustomTestCoolingBaseTemperatures')
        if len(self.__extraPredictorSpecs) > 0:
            epSpecs = e.newChild('ExtraPredictorSpecs')
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorSpecs):
                epSpecs.addChild(v._toXml(k))
        if len(self.__requestedRegressionSpecs) > 0:
            rSpecs = e.newChild('RequestedRegressionSpecs')
            for s in self.__requestedRegressionSpecs:
                rSpecs.addChild(s._toXml())
        return e
    @classmethod
    def _check(cls, param, paramName='regressionTestPlan'):
        if type(param) is not RegressionTestPlan:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionTestPlan))
        return param


class RegressionRequest(Immutable):
    __slots__ = ('__location', '__inputData', '__testPlan')
    def __init__(self, location, inputData, testPlan):
        self.__location = Location._check(location)
        self.__inputData = InputData._check(inputData)
        self.__testPlan = RegressionTestPlan._check(testPlan, 'testPlan')
        inputDataKeys = inputData.extraPredictorKeys
        testPlanKeys = testPlan.extraPredictorKeys
        for key in inputDataKeys:
            if not key in testPlanKeys:
                raise ValueError('inputData has data for extra-predictor key '
                    '%s but testPlan contains no ExtraPredictorSpec for that '
                    'key.' % key)
        for spec in testPlan.requestedRegressionSpecs:
            for key in spec.extraPredictorKeys:
                if not key in inputDataKeys:
                    raise ValueError('testPlan contains a requested Regression '
                        'spec with extra-predictor key %s but inputData does '
                        'not have any figures for that extra predictor.' % key)
    def _equalityFields(self):
        return (self.__location, self.__inputData, self.__testPlan)
    @property
    def location(self):
        return self.__location
    @property
    def inputData(self):
        return self.__inputData
    @property
    def testPlan(self):
        return self.__testPlan
    def __str__(self):
        return ('RegressionRequest(%s, %s, %s)' %
            (self.__location, self.__inputData, self.__testPlan))
    def __repr__(self):
        return ('RegressionRequest(%r, %r, %r)' %
            (self.__location, self.__inputData, self.__testPlan))
    def _toXml(self):
        return XmlElement('RegressionRequest') \
            .addChild(self.__location._toXml()) \
            .addChild(self.__testPlan._toXml()) \
            .addChild(self.__inputData._toXml())
    @classmethod
    def _check(cls, param, paramName='regressionRequest'):
        if type(param) is not RegressionRequest:
            raise TypeError(private.wrongTypeString(
                param, paramName, RegressionRequest))
        return param


def _checkStandardError(param, paramName):
    private.checkNumeric(param, paramName)
    if param < 0:
        raise ValueError('Invalid %s value (%g) - cannot be less than 0.' %
            (param, paramName))
    return param


class RegressionComponent(Immutable):
    __slots__ = ('__coefficient', '__coefficientStandardError',
        '__coefficientPValue')
    def __init__(self, coefficient, coefficientStandardError,
            coefficientPValue):
        self.__coefficient = private.checkNumeric(coefficient, 'coefficient')
        self.__coefficientStandardError = _checkStandardError(
            coefficientStandardError, 'coefficientStandardError')
        private.checkNumeric(coefficientPValue, coefficientPValue)
        if coefficientPValue > 1 or coefficientPValue < 0:
            raise ValueError('Invalid coefficientPValue (%g) - cannot be less '
                'than 0 or greater than 1.' % coefficientPValue)
        self.__coefficientPValue = coefficientPValue
    def _equalityFieldsExtra(self):
        raise NotImplementedError()
    def _equalityFields(self):
        return (self.__coefficient, self.__coefficientStandardError,
            self.__coefficientPValue) + self._equalityFieldsExtra()
    @property
    def coefficient(self):
        return self.__coefficient
    @property
    def coefficientStandardError(self):
        return self.__coefficientStandardError
    @property
    def coefficientPValue(self):
        return self.__coefficientPValue
    def _appendFormula(self, s):
        # Don't use the +- together unicode symbol cos it causes too many
        # problems in python 2.
        s.append('%g[+-%.4g,p=%.4g]' % (self.__coefficient,
            self.__coefficientStandardError, self.__coefficientPValue))


class BaseloadRegressionComponent(RegressionComponent):
    __slots__ = ('__multiplyByNumberOfDays',)
    def __init__(self, coefficient, coefficientStandardError, coefficientPValue,
            multiplyByNumberOfDays):
        super(BaseloadRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__multiplyByNumberOfDays = private.checkBoolean(
            multiplyByNumberOfDays, 'multiplyByNumberOfDays')
    def _equalityFieldsExtra(self):
        return (self.__multiplyByNumberOfDays,)
    @property
    def multiplyByNumberOfDays(self):
        return self.__multiplyByNumberOfDays
    def __str__(self):
        s = []
        s.append('BaseloadRegressionComponent(')
        self._appendFormula(s)
        if self.__multiplyByNumberOfDays:
            s.append(' * days')
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('BaseloadRegressionComponent(%r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__multiplyByNumberOfDays))
    @classmethod
    def _check(cls, param, paramName='baseload'):
        if type(param) is not BaseloadRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                BaseloadRegressionComponent))
        return param


class ExtraRegressionComponent(RegressionComponent):
    __slots__ = ('__multiplyByNumberOfDays',)
    def __init__(self, coefficient, coefficientStandardError, coefficientPValue,
            multiplyByNumberOfDays):
        super(ExtraRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__multiplyByNumberOfDays = private.checkBoolean(
            multiplyByNumberOfDays, 'multiplyByNumberOfDays')
    def _equalityFieldsExtra(self):
        return (self.__multiplyByNumberOfDays,)
    @property
    def multiplyByNumberOfDays(self):
        return self.__multiplyByNumberOfDays
    def __str__(self):
        s = []
        s.append('ExtraRegressionComponent(')
        self._appendFormula(s)
        if self.__multiplyByNumberOfDays:
            s.append(' * days')
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('ExtraRegressionComponent(%r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__multiplyByNumberOfDays))
    @classmethod
    def _check(cls, param, paramName):
        if type(param) is not ExtraRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExtraRegressionComponent))
        return param


class DegreeDaysRegressionComponent(RegressionComponent):
    __slots__ = ('__baseTemperature', '__sampleDegreeDaysDataSet',
        '__sampleDegreeDaysTotal')
    def __init__(self, coefficient, coefficientStandardError, coefficientPValue,
            baseTemperature, sampleDegreeDaysDataSet, sampleDegreeDaysTotal):
        super(DegreeDaysRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__baseTemperature = Temperature._check(
            baseTemperature, 'baseTemperature')
        self.__sampleDegreeDaysDataSet = DatedDataSet._check(
            sampleDegreeDaysDataSet, 'sampleDegreeDaysDataSet')
        self.__sampleDegreeDaysTotal = DataValue._check(
            sampleDegreeDaysTotal, 'sampleDegreeDaysTotal')
    def _equalityFieldsExtra(self):
        return (self.__baseTemperature, self.__sampleDegreeDaysTotal,
            self.__sampleDegreeDaysDataSet)
    @property
    def baseTemperature(self):
        return self.__baseTemperature
    @property
    def sampleDegreeDaysDataSet(self):
        return self.__sampleDegreeDaysDataSet
    @property
    def sampleDegreeDaysTotal(self):
        return self.__sampleDegreeDaysTotal
    def __str__(self):
        s = []
        s.append('DegreeDaysRegressionComponent(')
        self._appendFormula(s)
        s.append(', base %s, %s, total %s)' % (self.__baseTemperature,
            self.__sampleDegreeDaysDataSet, self.__sampleDegreeDaysTotal))
        return ''.join(s)
    def __repr__(self):
        return ('DegreeDaysRegressionComponent(%r, %r, %r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__baseTemperature,
                self.__sampleDegreeDaysDataSet, self.__sampleDegreeDaysTotal))
    @classmethod
    def _check(cls, param, paramName):
        if type(param) is not DegreeDaysRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                DegreeDaysRegressionComponent))
        return param

# This class exists only to simplify the __init__ method of Regression.
class RegressionComponents(Immutable):
    __slots__ = ('__baseload', '__heatingDegreeDaysOrNone',
        '__coolingDegreeDaysOrNone', '__extras')
    def __init__(self, baseload, heatingDegreeDaysOrNone=None,
            coolingDegreeDaysOrNone=None, extras={}):
        self.__baseload = BaseloadRegressionComponent._check(baseload)
        if heatingDegreeDaysOrNone is None:
            self.__heatingDegreeDaysOrNone = None
        else:
            self.__heatingDegreeDaysOrNone = \
                DegreeDaysRegressionComponent._check(
                    heatingDegreeDaysOrNone, 'heatingDegreeDaysOrNone')
        if coolingDegreeDaysOrNone is None:
            self.__coolingDegreeDaysOrNone = None
        else:
            self.__coolingDegreeDaysOrNone = \
                DegreeDaysRegressionComponent._check(
                    coolingDegreeDaysOrNone, 'coolingDegreeDaysOrNone')
        if self.__heatingDegreeDaysOrNone is not None and \
                self.__coolingDegreeDaysOrNone is not None and \
                (self.__heatingDegreeDaysOrNone.baseTemperature.unit !=
                    self.__coolingDegreeDaysOrNone.baseTemperature.unit):
            raise ValueError('The heating degree days and cooling degree days '
                'must have the same temperature unit.')                
        # Create a defensive copy of the dict for usual reasons but also so the
        # default {} value cannot be modified for future calls.
        self.__extras = private.checkDict(extras, 'extras').copy()
        if len(self.__extras) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('extras has %d extra components, when'
                ' the maximum allowed is %d.' %
                    (len(self.__extras), _MAX_EXTRA_PREDICTORS))
        for k, v in private.getDictItemsIterable(self.__extras):
            _checkExtraPredictorKey(k,
                'Problem key in extraPredictorSpecs dict.  ')
            ExtraRegressionComponent._check(v, 'A value in extras dict')
    def _equalityFields(self):
        return (self.__baseload, self.__heatingDegreeDaysOrNone,
            self.__coolingDegreeDaysOrNone, self.__extras)
    def __hash__(self):
        h = hash((self.__class__, self.__baseload,
            self.__heatingDegreeDaysOrNone, self.__coolingDegreeDaysOrNone))
        return private.getDictHash(self.__extras, h)
    @property
    def baseload(self):
        return self.__baseload
    @property
    def heatingDegreeDaysOrNone(self):
        return self.__heatingDegreeDaysOrNone
    @property
    def coolingDegreeDaysOrNone(self):
        return self.__coolingDegreeDaysOrNone
    @property
    def extraPredictorKeys(self):
        # Like elsewhere, use a tuple to maintain order, as in Python 3.7+ the
        # dict will maintain order by default.
        return tuple(self.__extras)
    @property
    def spec(self):
        hdd = None
        cdd = None
        if self.__heatingDegreeDaysOrNone is not None:
            hdd = self.__heatingDegreeDaysOrNone.baseTemperature
        if self.__coolingDegreeDaysOrNone is not None:
            cdd = self.__coolingDegreeDaysOrNone.baseTemperature
        return RegressionSpec(heatingBaseTemperatureOrNone=hdd,
            coolingBaseTemperatureOrNone=cdd,
            extraPredictorKeys=self.extraPredictorKeys)
    def hasExtraComponent(self, extraPredictorKey):
        return extraPredictorKey in self.__extras
    def getExtraComponent(self, extraPredictorKey):
        # Following will throw a KeyError if key isn't found.
        return self.__extras[extraPredictorKey]
    def __appendDegreeDays(self, s, component, name):
        s.append('(')
        component._appendFormula(s)
        s.append(' * %s%s[%s])' % (name,
            str(component.baseTemperature).replace(' ', ''),
            component.sampleDegreeDaysTotal))
        return ''.join(s)
    def __str__(self):
        s = []
        s.append('E = ')
        if self.__baseload.multiplyByNumberOfDays:
            s.append('(')
        self.__baseload._appendFormula(s)
        if self.__heatingDegreeDaysOrNone is not None:
            s.append(' + ')
            self.__appendDegreeDays(s, self.__heatingDegreeDaysOrNone, 'HDD')
        if self.__coolingDegreeDaysOrNone is not None:
            s.append(' + ')
            self.__appendDegreeDays(s, self.__coolingDegreeDaysOrNone, 'CDD')
        for k, v in private.getDictItemsIterable(self.__extras):
            s.append(' + (')
            v._appendFormula(s)
            s.append(' * ')
            s.append(k)
            if v.multiplyByNumberOfDays:
                s.append(' * days')
            s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = []
        s.append('RegressionComponents(%r' % self.__baseload)
        if self.__heatingDegreeDaysOrNone is not None:
            s.append(', heatingDegreeDaysOrNone=%r' %
                self.__heatingDegreeDaysOrNone)
        if self.__coolingDegreeDaysOrNone is not None:
            s.append(', coolingDegreeDaysOrNone=%r' %
                self.coolingDegreeDaysOrNone)
        if len(self.__extras) > 0:
            s.append(', extras=%r' % self.__extras)
        s.append(')')
        return ''.join(s)
    @classmethod
    def _check(cls, param, paramName='components'):
        if type(param) is not RegressionComponents:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionComponents))
        return param


def _checkRSquared(param, paramName):
    private.checkNumeric(param, paramName)
    if param > 1:
        raise ValueError('Invalid %s (%g) - cannot be greater than 1.' %
            (paramName, param))
    return param


class Regression(Immutable):
    __slots__ = ('__tags', '__components', '__sampleSize', '__sampleDays',
        '__sampleSpan', '__rSquared', '__adjustedRSquared',
        '__crossValidatedRSquared', '__standardError', '__cvrmse')
    def __init__(self, tags, components, sampleSize, sampleDays, sampleSpan,
            rSquared, adjustedRSquared, crossValidatedRSquared, standardError,
            cvrmse):
        self.__tags = private.checkTupleItems(
            tuple(tags), RegressionTag._check, 'tags')
        self.__tags = frozenset(self.__tags)
        self.__components = RegressionComponents._check(components)
        self.__sampleSize = private.checkInt(sampleSize, 'sampleSize')
        if self.__sampleSize <= 0:
            raise ValueError(
                'Invalid sampleSize (%d) - must be greater than 0.' %
                    self.__sampleSize)
        self.__sampleDays = private.checkInt(sampleDays, 'sampleDays')
        if self.__sampleDays <= 0:
            raise ValueError(
                'Invalid sampleDays (%d) - must be greater than 0.' %
                    self.__sampleDays)
        self.__sampleSpan = degreedays.time.DayRange._check(
            sampleSpan, 'sampleSpan')
        if sampleDays > len(sampleSpan):
            raise ValueError('sampleDays cannot be %d when the sampleSpan (%s) '
                'is %d days long.' % (self.__sampleDays, self.__sampleSpan,
                    len(self.__sampleSpan)))
        self.__rSquared = _checkRSquared(rSquared, 'rSquared')
        self.__adjustedRSquared = _checkRSquared(
            adjustedRSquared, 'adjustedRSquared')
        self.__crossValidatedRSquared = _checkRSquared(
            crossValidatedRSquared, 'crossValidatedRSquared')
        self.__standardError = _checkStandardError(
            standardError, 'standardError')
        self.__cvrmse = private.checkNumeric(cvrmse, 'cvrmse')
    def _equalityFields(self):
        # tags are not included cos they are like metadata
        return (self.__components, self.__sampleSize,
            self.__sampleDays, self.__sampleSpan, self.__rSquared,
            self.__adjustedRSquared, self.__crossValidatedRSquared,
            self.__standardError, self.__cvrmse)
    @property
    def tags(self):
        return self.__tags
    def hasTag(self, regressionTag):
        RegressionTag._check(regressionTag)
        return regressionTag in self.__tags
    @property
    def baseload(self):
        return self.__components.baseload
    @property
    def heatingDegreeDaysOrNone(self):
        return self.__components.heatingDegreeDaysOrNone
    @property
    def coolingDegreeDaysOrNone(self):
        return self.__components.coolingDegreeDaysOrNone
    @property
    def extraPredictorKeys(self):
        return self.__components.extraPredictorKeys
    def hasExtraComponent(self, extraPredictorKey):
        return self.__components.hasExtraComponent(extraPredictorKey)
    def getExtraComponent(self, extraPredictorKey):
        return self.__components.getExtraComponent(extraPredictorKey)
    @property
    def sampleSize(self):
        return self.__sampleSize
    @property
    def sampleDays(self):
        return self.__sampleDays
    @property
    def sampleSpan(self):
        return self.__sampleSpan
    @property
    def sampleSpanDays(self):
        return len(self.__sampleSpan)
    @property
    def standardError(self):
        return self.__standardError
    @property
    def rSquared(self):
        return self.__rSquared
    @property
    def adjustedRSquared(self):
        return self.__adjustedRSquared
    @property
    def crossValidatedRSquared(self):
        return self.__crossValidatedRSquared
    @property
    def cvrmse(self):
        return self.__cvrmse
    @property
    def spec(self):
        return self.__components.spec
    def __str__(self):
        s = []
        s.append('Regression(%s, R2=%g, adj-R2=%g, cv-R2=%g, S=%g, CVRMSE=%g, '
            'from a sample of %d values covering ' % (self.__components,
                self.__rSquared, self.__adjustedRSquared,
                self.__crossValidatedRSquared, self.__standardError,
                self.__cvrmse, self.__sampleSize))
        sampleSpanDays = self.sampleSpanDays
        if sampleSpanDays == self.__sampleDays:
            s.append('all %d' % self.__sampleDays)
        else:
            s.append('%d of the %d' % (self.__sampleDays, sampleSpanDays))
        s.append(' days within %s)' % self.__sampleSpan)
        return ''.join(s)
    def __repr__(self):
        return ('Regression(%r, %r, %d, %d, %r, %r, %r, %r, %r, %r)' %
            (self.__tags, self.__components, self.__sampleSize,
                self.__sampleDays, self.__sampleSpan,
                self.__rSquared, self.__adjustedRSquared,
                self.__crossValidatedRSquared, self.__standardError,
                self.__cvrmse))
    @classmethod
    def _check(cls, param, paramName):
        if type(param) is not Regression:
            raise TypeError(private.wrongTypeString(
                param, paramName, Regression))
        return param


class RegressionResponse(degreedays.api.Response):
    __slots__ = ('__metadata', '__stationId', '__targetLongLat', '__sources',
        '__regressionsResult')
    def __init__(self, metadata, stationId, targetLongLat, sources,
            regressionsOrFailure):
        self.__metadata =  degreedays.api.ResponseMetadata._check(
            metadata, 'metadata')
        self.__stationId = private.checkStationId(stationId, False)
        self.__targetLongLat = degreedays.geo.LongLat._check(
            targetLongLat, 'targetLongLat')
        self.__sources = private.checkTupleItems(
            tuple(sources), degreedays.api.data.Source._check, 'sources')
        if type(regressionsOrFailure) is degreedays.api.Failure:
            self.__regressionsResult = regressionsOrFailure
        else:
            self.__regressionsResult = private.checkTupleItems(
                tuple(regressionsOrFailure), Regression._check,
                'regressionsOrFailure')
    def _equalityFields(self):
        # metadata isn't included in equality check.
        return (self.__stationId, self.__targetLongLat, self.__sources,
            self.__regressionsResult)
    @property
    def metadata(self):
        return self.__metadata
    @property
    def stationId(self):
        return self.__stationId
    @property
    def targetLongLat(self):
        return self.__targetLongLat
    @property
    def sources(self):
        return self.__sources
    def getRegressions(self):
        if type(self.__regressionsResult) is degreedays.api.Failure:
            raise SourceDataError(self.__regressionsResult)
        return self.__regressionsResult
    def __str__(self):
        s = degreedays.api.data._getLocationResponseStringStart(self)
        s.append(', ')
        if type(self.__regressionsResult) is degreedays.api.Failure:
            s.append(str(self.__regressionsResult))
        else:
            count = len(self.__regressionsResult)
            if count > 1:
                s.append('%d regressions starting with ' % count)
            else:
                s.append('1 regression ')
            s.append(str(self.__regressionsResult[0]))
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ("RegressionResponse(%r, '%s', %r, %r, %r)" %
            (self.__metadata, self.__stationId, self.__targetLongLat,
                self.__sources, self.__regressionsResult))


class RegressionApi(object):
    def __init__(self, requestProcessor):
        self.__requestProcessor = requestProcessor
    def __checkAndGet(self, request, expectedResponseType):
        response = self.__requestProcessor.process(request)
        if isinstance(response, expectedResponseType):
            return response
        elif isinstance(response, degreedays.api.FailureResponse):
            code = response.failure.code
            if code.startswith('Location'):
                raise degreedays.api.data.LocationError(response)
            # for general exceptions
            raise degreedays.api.RequestFailureError._create(response)
        else:
            raise ValueError('For a request of type %r, the RequestProcessor '
                'should return a response of type %r or a FailureResponse, not '
                '%r' % (type(request), expectedResponseType, type(response)))
    def runRegressions(self, regressionRequest):
        RegressionRequest._check(regressionRequest)
        return self.__checkAndGet(regressionRequest, RegressionResponse)
