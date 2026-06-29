from scripts.materialize_v3_4_stratified_text_sample import iter_offsets, parse_size


def test_parse_size_accepts_binary_suffixes() -> None:
    assert parse_size("1KB") == 1024
    assert parse_size("1.5MB") == 1572864
    assert parse_size("2gb") == 2147483648


def test_iter_offsets_returns_one_offset_per_chunk() -> None:
    class FakeRandom:
        def randint(self, start: int, _end: int) -> int:
            return start

    offsets = iter_offsets(file_size=1000, chunks=4, rng=FakeRandom())

    assert offsets == [0, 250, 500, 750]
