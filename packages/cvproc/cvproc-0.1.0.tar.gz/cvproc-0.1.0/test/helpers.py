import av
from cvproc import h264_to_ndarrays


av.logging.set_level(av.logging.ERROR)


def decode_raw(raw: bytes):
    return h264_to_ndarrays(raw)


def decode_raw_av(path):
    container = av.open(path, mode='rb')
    container.streams.video[0].thread_count = 1
    return [frame.to_rgb().to_ndarray() for frame in container.decode(video=0)]
