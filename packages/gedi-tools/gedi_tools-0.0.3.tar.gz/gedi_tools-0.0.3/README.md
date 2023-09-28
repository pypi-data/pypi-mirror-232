# GEDI Tools Library

__This library is currently experimental and is under heavy development.__

## Overview

GEDI Tools is a Python library designed to facilitate the transformation and processing of GEDI (Global Ecosystem Dynamics Investigation) data. It is especially geared towards converting GEDI data in HDF5 format to L2B objects for easier manipulation and analysis.

## Features

- **Single File Transformation**: Convert a single HDF5 file to L2B format with ease.
- **Batch File Transformation**: Efficiently convert a list of HDF5 files to L2B format.
- **Data Clipping**: Optionally clip data using a GeoDataFrame.

## Installation

To install the GEDI Tools library, run:

```bash
pip install gedi-tools
```

## Usage

### Single File Transformation

Here's a simple example to transform a single HDF5 file to L2B format:

```python
from gedi_tools import GediTransformer

l2b_single = GediTransformer.hd5_to_l2b("path/to/hd5_file.hd5")
```

### Multiple File Transformation with Clipping

Transform multiple HDF5 files and clip data using a GeoDataFrame:

```python
from gedi_tools import GediTransformer

clip_gdf = ...  # Your GeoDataFrame for clipping
l2b_multiple = GediTransformer.hd5_list_to_l2b(["path1.hd5", "path2.hd5"], clip_gdf=clip_gdf)
```

## Documentation

For more details, please refer to the [Full Documentation](https://geditools.readthedocs.io/en/latest/).

## Contributing

We welcome contributions! Please see the [Contributing Guidelines](https://github.com/iosefa/gediTools/blob/main/CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/iosefa/gediTools/blob/main/LICENSE.md) file for details.
