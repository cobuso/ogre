from __future__ import unicode_literals

from .printer import CoreException


class OgreException(CoreException):
    pass

class OgreWarning(Exception):
    def __init__(self, message=None):
        super(OgreWarning, self).__init__(message)

class BaseEbookError(OgreException):
    def __init__(self, ebook_obj, message=None, inner_excp=None):
        self.ebook_obj = ebook_obj
        super(BaseEbookError, self).__init__(message, inner_excp)

class BaseEbookWarning(OgreWarning):
    def __init__(self, ebook_obj, message=None):
        self.ebook_obj = ebook_obj
        super(BaseEbookWarning, self).__init__(message)


class ConfigSetupError(OgreException):
    pass

class AuthDeniedError(OgreException):
    pass

class AuthError(OgreException):
    pass

class OgreserverDownError(OgreException):
    def __init__(self):
        super(OgreserverDownError, self).__init__('Please try again later :(')

class NoEbooksError(OgreWarning):
    def __init__(self):
        super(NoEbooksError, self).__init__('No ebooks found.. Cannot continue!')

class SyncError(OgreException):
    pass


class UploadError(BaseEbookError):
    pass

class CorruptEbookError(BaseEbookError):
    pass

class FailedWritingMetaDataError(BaseEbookError):
    pass

class FailedConfirmError(BaseEbookError):
    pass


class FailedDebugLogsError(OgreException):
    pass

class PrereqsBaseError(OgreException):
    pass

class KindlePrereqsError(PrereqsBaseError):
    pass

class ADEPrereqsError(PrereqsBaseError):
    pass

class NoEbookSourcesFoundError(OgreException):
    pass

class DeDrmNotAvailable(OgreException):
    pass


class DuplicateEbookBaseError(OgreWarning):
    def __init__(self, kind, ebook_obj, path2):
        super(DuplicateEbookBaseError, self).__init__(
            u"Duplicate ebook found ({}) '{}':\n  {}\n  {}".format(kind, ebook_obj.path, path2)
        )

class ExactDuplicateEbookError(DuplicateEbookBaseError):
    def __init__(self, ebook_obj, path2):
        super(ExactDuplicateEbookError, self).__init__('exact', ebook_obj, path2)

class AuthortitleDuplicateEbookError(DuplicateEbookBaseError):
    def __init__(self, ebook_obj, path2):
        super(AuthortitleDuplicateEbookError, self).__init__('author/title', ebook_obj, path2)

class EbookIdDuplicateEbookError(DuplicateEbookBaseError):
    def __init__(self, ebook_obj, path2):
        super(EbookIdDuplicateEbookError, self).__init__('ebook_id', ebook_obj, path2)


class MissingFromCacheError(OgreException):
    pass

class FailedUploadsQueryError(OgreException):
    pass

class FailedGettingDefinitionsError(OgreException):
    pass


class DeDrmMissingError(BaseEbookWarning):
    # DeDrmMissing exception must support a missing ebook_obj when raised in
    # the initialisation of dedrm.py
    def __init__(self, ebook_obj=None):
        super(DeDrmMissingError, self).__init__(ebook_obj, message='DeDRM package unavailable!')

class DecryptionFailed(BaseEbookWarning):
    pass

class DecryptionError(BaseEbookWarning):
    pass
