from typing import TYPE_CHECKING

from weathon.dl.utils.import_utils import LazyImportModule

if TYPE_CHECKING:
    from .configuration import LlamaConfig
    from .text_generation import LlamaForTextGeneration
    from .backbone import LlamaModel
    from .tokenization import LlamaTokenizer
    from .tokenization_fast import LlamaTokenizerFast
else:
    _import_structure = {
        'configuration': ['LlamaConfig'],
        'text_generation': ['LlamaForTextGeneration'],
        'backbone': ['LlamaModel'],
        'tokenization': ['LlamaTokenizer'],
        'tokenization_fast': ['LlamaTokenizerFast'],
    }

    import sys

    sys.modules[__name__] = LazyImportModule(
        __name__,
        globals()['__file__'],
        _import_structure,
        module_spec=__spec__,
        extra_objects={},
    )
