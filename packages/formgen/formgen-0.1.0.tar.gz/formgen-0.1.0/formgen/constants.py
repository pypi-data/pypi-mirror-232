# Package-wide constants

# Maximum number of processes to run in parallel: None uses the number returned
#   by os.cpu_count() is used.
MAX_PROCESSES = None

# Minimum and maximum segment cardinalities.
MIN_SEG_CARD = 2
MAX_SEG_CARD = 4

# MaxDiff for CCV1 and CCV2: list index = cseg cardinality.
MAX_DIFF_CCV1 = [None, None, 2, 8, 20, 40, 70, 112]
MAX_DIFF_CCV2 = [None, None, 2, 6, 12, 20, 30, 42]

# Minimum and maximum pitches in psegs.
MIN_PITCH = 21
MAX_PITCH = 108

# Pitch varieties per pc (pitches are between MINPITCH and MAXPITCH inclusive).
_pitches = [[], [], [], [], [], [], [], [], [], [], [], []]
_pcs = range(12)
for pc in _pcs:
    p = pc
    while p <= MAX_PITCH:
        if p >= MIN_PITCH:
            _pitches[pc].append(p)
        p += 12
PITCHES = _pitches

# Quantization interval for mdurs.
QUANTIZATION_INTERVAL = 0.125  # 32nd note or 0.125 seconds.