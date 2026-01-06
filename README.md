# mapf

MAPF (Multi-Agent Path Finding) environment and tools for working with MovingAI benchmark maps.

## Features

- Load and visualize MovingAI MAPF benchmark maps
- Sample MAPF instances from scenario files
- Validate paths for MAPF problems
- Animate and playback paths as GIFs
- Random rollout visualization
- Environment for running MAPF algorithms

## Installation

### Using Conda (Recommended)

```bash
conda env create -f environment.yml
conda activate mapf
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### Preview a map

```bash
python -m scripts.preview_map data/mapf-map/empty-32-32.map
```

### Sample an instance

```bash
python -m scripts.sample_instance --map empty-32-32 --k 10
```

### Validate paths

```bash
python -m scripts.validate_paths paths.npy --map empty-32-32 --k 10
```

### Playback paths as GIF

```bash
python -m scripts.playback_paths --map empty-32-32 --paths paths.npy --k 10 --out demo.gif --fps 6
```

### Random rollout

```bash
python -m scripts.random_rollout --map empty-32-32 --k 10 --steps 20 --motion 4
```

## Data

Download MovingAI MAPF benchmark maps and scenarios from:
https://www.movingai.com/benchmarks/mapf/index.html

Place map files in `data/mapf-map/` and scenario files in `data/scens/`.

## Testing

Run the test suite:

```bash
./test_all.sh
```

Or run individual test scripts:

```bash
./test_quick.sh
./test_sample_instance.sh
./test_validate_paths.sh
```

## Structure

- `mapf_env/` - Core MAPF environment code
  - `io/` - Map and scenario file loading
  - `viz/` - Visualization and animation
- `core/` - Core MAPF functionality
  - `instance.py` - MAPF instance representation
  - `env.py` - MAPF environment
  - `validate.py` - Path validation
- `scripts/` - Command-line tools
- `tests/` - Test files
- `data/` - Map and scenario data

## License

See LICENSE file for details.

# mapf

