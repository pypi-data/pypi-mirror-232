# Makes the AcTag class immediately available, instead of having to call actag_src.AcTag
from .actag_src import AcTag

# This actag is the rust module, so we rename it to rust_impl
from actag import rust_impl

__doc__ = actag_src.__doc__
if hasattr(actag_src, "__all__"):
	__all__ = actag_src.__all__