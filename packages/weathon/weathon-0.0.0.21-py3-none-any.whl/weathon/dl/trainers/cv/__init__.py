from typing import TYPE_CHECKING

from weathon.dl.utils.import_utils import LazyImportModule

if TYPE_CHECKING:
    from .ocr import OcrDetectionTrainer

else:
    _import_structure = {
        'ocr': ['OcrDetectionTrainer'],
    }

    import sys

    sys.modules[__name__] = LazyImportModule(
        __name__,
        globals()['__file__'],
        _import_structure,
        module_spec=__spec__,
        extra_objects={},
    )
