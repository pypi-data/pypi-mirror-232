from typing import Tuple, Optional, Any, Union
from delayedarray import DelayedArray, chunk_shape, is_sparse, extract_dense_array, extract_sparse_array, is_pristine
from numpy import ceil, prod
from dolomite_base import stage_object
import os

from .choose_dense_chunk_sizes import choose_dense_chunk_sizes
from ._utils import _choose_file_dtype, _translate_array_type, _open_writeable_hdf5_handle, _choose_block_shape
from .stage_sparse import _stage_sparse_matrix


def _stage_DelayedArray_dense(
    x: DelayedArray,
    dir: str,
    path: str,
    is_child: bool = False,
    chunks: Optional[Tuple[int, ...]] = None,
    cache_size: int = 1e8,
    block_size: int = 1e8,
    **kwargs
) -> dict[str, Any]:
    os.mkdir(os.path.join(dir, path))
    newpath = path + "/array.h5"

    # Coming up with a decent chunk size.
    if chunks is None:
        chunks = choose_dense_chunk_sizes(x.shape, x.dtype.itemsize)
    else:
        capped = []
        for i, d in enumerate(x.shape):
            capped.append(min(d, chunks[i]))
        chunks = (*capped,)

    # Transposing it so that we save it in the right order.
    t = x.T
    chunks = (*list(reversed(chunks)),)

    # Saving the matrix in a blockwise fashion. We progress along HDF5's
    # fastest changing dimension (i.e., the last one), and we shift along the
    # other dimensions once we need to wrap around.
    full_shape = t.shape
    ndim = len(full_shape)
    block_shape = _choose_block_shape(t, block_size)

    fpath = os.path.join(dir, newpath)
    with _open_writeable_hdf5_handle(fpath, cache_size) as fhandle:
        dset = fhandle.create_dataset("data", shape=t.shape, chunks=chunks, dtype=_choose_file_dtype(t.dtype), compression="gzip")

        num_chunks = []
        subset_as_slices = []
        for i, s in enumerate(full_shape):
            b = block_shape[i]
            num_chunks.append(int(ceil(s / b)))
            subset_as_slices.append(slice(0, b))

        starts = [0] * len(num_chunks)
        counter = [0] * len(num_chunks)
        subset_as_ranges = [None] * len(num_chunks)

        running = True
        while running:
            for i, sl in enumerate(subset_as_slices):
                subset_as_ranges[i] = range(*(sl.indices(full_shape[i])))
            curblock = extract_dense_array(t, subset_as_ranges)
            dset[(*subset_as_slices,)] = curblock

            for i in range(ndim - 1, -1, -1):
                starts[i] += 1
                block_extent = block_shape[i]
                if starts[i] < num_chunks[i]:
                    new_start = starts[i] * block_extent
                    subset_as_slices[i] = slice(new_start, min(new_start + block_extent, full_shape[i]))
                    break
                if i == 0:
                    running = False
                    break
                starts[i] = 0
                subset_as_slices[i] = slice(0, block_extent)

    return {
        "$schema": "hdf5_dense_array/v1.json",
        "path": newpath,
        "is_child": is_child,
        "array": {
            "type": _translate_array_type(x.dtype),
            "dimensions": list(x.shape),
        },
        "hdf5_dense_array": {
            "dataset": "data",
        }
    }


@stage_object.register
def stage_DelayedArray(
    x: DelayedArray,
    dir: str,
    path: str,
    is_child: bool = False,
    chunks: Optional[Union[Tuple[int, ...], int]] = None,
    cache_size: int = 1e8,
    block_size: int = 1e8,
    **kwargs
) -> dict[str, Any]:
    """Method for saving :py:class:`~delaydearray.DelayedArray.DelayedArray`
    objects to file, see :py:meth:`~dolomite_base.stage_object.stage_object`
    for details.

    Args:
        x: Array to be saved.

        dir: Staging directory.

        path: Relative path inside ``dir`` to save the object.

        is_child: Is ``x`` a child of another object?

        chunks:
            For dense ``x``, a tuple of chunk dimensions. If None, we
            automatically choose some chunk sizes with
            :py:meth:`~dolomite_matrix.choose_dense_chunk_sizes.choose_dense_chunk_sizes`.

            For sparse ``x``, an integer specifying the chunk dimension in
            :py:meth:`~dolomite_matrix.write_sparse_matrix.write_sparse_matrix`.
            If None, a suitable chunk size is chosen.

        cache_size:
            Size of the HDF5 cache size, in bytes. Larger values improve speed
            at the cost of memory.

        block_size:
            Size of each block in bytes. Staging is performed by iterating over
            ``x``, extracting one block at a time, and saving it to the HDF5
            file. Larger values improve speed at the cost of memory.

        kwargs: 
            Further arguments, ignored for dense ``x``. For sparse ``x``, these
            are passed to
            :py:meth:`~dolomite_matrix.write_sparse_matrix.write_sparse_matrix`.

    Returns:
        Metadata that can be edited by calling methods and then saved with
        :py:meth:`~dolomite_base.write_metadata.write_metadata`.
    """
    # Seeing if we can call specialized method for the seed in pristine objects.
    if is_pristine(x) and isinstance(x, DelayedArray):
        candidate = stage_object.dispatch(type(x.seed))
        if stage_object.dispatch(object) != candidate:
            return candidate(
                x.seed,
                dir=dir,
                path=path,
                is_child=is_child,
                chunks=chunks,
                cache_size=cache_size,
                block_size=block_size,
                **kwargs
            )

    if is_sparse(x):
        return _stage_sparse_matrix(
            x,
            dir=dir,
            path=path,
            is_child=is_child,
            chunks=chunks,
            block_size=block_size,
            **kwargs,
        )
    else:
        return _stage_DelayedArray_dense(
            x,
            dir=dir,
            path=path,
            is_child=is_child,
            chunks=chunks,
            cache_size=cache_size,
            block_size=block_size,
            **kwargs
        )
