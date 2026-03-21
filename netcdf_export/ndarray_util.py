import os
import time
import numpy as np
import blosc2


def generate_ndarray_file(data: np.ndarray, file_path: str):
    """
    Generate a compressed .npz file from numpy data array.
    Parameters:
        data:        a numpy array
        file_path:   the file path to be written
    """
    with open(file_path, "wb+") as fp:
        compressed = compress_data(data)
        fp.write(compressed)


def compress_data(data: np.ndarray) -> np.ndarray:
    """
    Compress a numpy array using blosc2.
     This is high performance compression for floating point data.
    """

    compressed = blosc2.compress(
        data,
        typesize=data.dtype.itemsize,
        clevel=5,
        codec=blosc2.Codec.ZSTD,
        filter=blosc2.Filter.BITSHUFFLE,
    )
    return compressed


def decompress_data(content, shape, dtype) -> np.ndarray:
    """De-compress a numpy array"""

    decompressed = blosc2.decompress(content)
    data = np.frombuffer(decompressed, dtype=dtype).reshape(shape)
    return data


def clean_temp_dir(temp_dir: str, limit_seconds: int, limit_bytes: int) -> int:
    """
    Remove files in `temp_dir` older than `limit_seconds` (non-recursive).

    Parameters:
        temp_dir:   The path name to a temp directory that must be within /tmp.
        limit_seconds:  Remove files from temp_dir that are older than limit_seconds.
        limit_bytes:    Return True from function if total bytes are larger than this.

    Rules:
      - Only operate on the immediate contents of `temp_dir` (no recursion).
      - Require that temp_dir is an absolute path and not too short.
      - Remove only regular files; do NOT remove directories.
      - Symlinks are skipped for safety (not treated as files).
      - If a file cannot be removed due to a transient error, it is skipped.
      - The total bytes in the directory is the sum of sizes of files that *remain* after deletions.

    Args:
        temp_dir:       Path to the temporary directory.
        limit_seconds:  Age threshold in seconds. Older files are removed.

    Returns:
        True if the total bytes in the temp_dir is more than the limit_bytes.
        False if the total bytes in the temp dir is less or equal to limit_bytes.
        None if there are zero bytes in the temp dir.
    """
    if not temp_dir.startswith("/"):
        raise ValueError(f"The directory {temp_dir} must be an absolute path")
    if len(temp_dir) < 5:
        raise ValueError(f"The directory {temp_dir} is questionably short.")
    now = time.time()
    total_bytes = 0

    # Use scandir for efficiency and to avoid extra stat calls where possible.
    try:
        with os.scandir(temp_dir) as it:
            for entry in it:
                # Skip directories and symlinks (we do not remove directories).
                # follow_symlinks=False ensures symlinks are not treated as files.
                try:
                    if not entry.is_file(follow_symlinks=False):
                        continue

                    # Get file stats (one stat call via DirEntry is efficient)
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        # File may have been removed between listing and stat
                        continue

                    file_age = now - st.st_mtime
                    if file_age > limit_seconds:
                        # Attempt to remove old file
                        try:
                            os.remove(entry.path)
                        except (PermissionError, OSError):
                            # Could not remove; treat it as remaining
                            total_bytes += st.st_size
                    else:
                        # Keep file; add its size
                        total_bytes += st.st_size

                except OSError:
                    # If any unexpected filesystem error occurs for this entry, skip it.
                    # (Conservative: we neither delete nor count it.)
                    continue

    except FileNotFoundError:
        # If the directory doesn't exist, there are effectively 0 bytes.
        return 0

    return total_bytes > limit_bytes if total_bytes > 0 else None
