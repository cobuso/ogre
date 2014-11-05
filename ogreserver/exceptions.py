from __future__ import unicode_literals


class OgreException(Exception):
    def __init__(self, message=None, inner_excp=None):
        super(OgreException, self).__init__(message)
        self.inner_excp = inner_excp

class ExactDuplicateError(OgreException):
    pass

class BadMetaDataError(OgreException):
    pass

class NoFormatAvailableError(OgreException):
    pass

class ConversionFailedError(OgreException):
    pass

class EbookNotFoundOnS3Error(OgreException):
    pass

class SameHashSuppliedOnUpdateError(OgreException):
    pass
