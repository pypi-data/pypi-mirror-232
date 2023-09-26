use color_eyre::eyre::Result;
use numpy::IntoPyArray;
use openh264::decoder::Decoder;
use openh264::nal_units;
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pyfunction]
fn __setup() -> Result<()> {
    color_eyre::install()?;
    Ok(())
}

fn h264_to_ndarrays(raw: &[u8]) -> Result<Vec<(Vec<u8>, (usize, usize))>> {
    let mut dec = Decoder::new()?;
    let mut frames = Vec::new();
    for packet in nal_units(raw) {
        if let Some(yuv) = dec.decode(&packet)? {
            let (w, h) = yuv.dimension_rgb();
            let mut frame = vec![0u8; w * h * 3];
            yuv.write_rgb8(&mut frame);
            frames.push((frame, (w, h)));
        }
    }
    Ok(frames)
}

#[pyfunction]
#[pyo3(name = "h264_to_ndarrays")]
fn nogil_h264_to_ndarrays(py: Python, raw: &[u8]) -> Result<PyObject> {
    let frames = py.allow_threads(|| h264_to_ndarrays(raw))?.into_iter()
        .map(|(frame, (w, h))| frame
            .into_pyarray(py)
            .reshape([h as usize, w as usize, 3])
            .unwrap()
        );
    Ok(PyList::new(py, frames).into())
}

#[pymodule]
fn cvproc(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(__setup, m)?)?;
    m.add_function(wrap_pyfunction!(nogil_h264_to_ndarrays, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::fs::File;
    use std::io::Read;

    use super::*;

    #[test]
    fn test_h264_to_tensor() {
        let mut f = File::open("test/test.mp4").unwrap();
        let mut buf = Vec::new();
        f.read_to_end(&mut buf).unwrap();
        let frames = h264_to_ndarrays(&buf).unwrap();
    }
}