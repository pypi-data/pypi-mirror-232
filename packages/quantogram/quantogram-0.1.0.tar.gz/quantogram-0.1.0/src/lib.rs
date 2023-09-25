use pyo3::prelude::*;

use ::quantogram as qg;

#[pyclass(name = "Quantogram")]
struct PyQuantogram {
    qg: qg::Quantogram,
}

#[pymethods]
impl PyQuantogram {
    #[new]
    fn new() -> Self {
        PyQuantogram {
            qg: qg::Quantogram::new(),
        }
    }

    fn add(&mut self, sample: f64) {
        self.qg.add(sample);
    }

    fn remove(&mut self, sample: f64) {
        self.qg.remove(sample);
    }

    fn add_weighted(&mut self, sample: f64, weight: f64) {
        self.qg.add_weighted(sample, weight);
    }

    fn add_unweighted_samples(&mut self, samples: Vec<f64>) {
        self.qg.add_unweighted_samples(samples.iter());
    }

    fn quantile(&self, quantile: f64) -> Option<f64> {
        self.qg.quantile(quantile)
    }

    fn fussy_quantile(&self, quantile: f64, threshold_ratio: f64) -> Option<f64> {
        self.qg.fussy_quantile(quantile, threshold_ratio)
    }

    fn count(&self) -> usize {
        self.qg.count()
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn quantogram(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyQuantogram>()?;
    Ok(())
}
