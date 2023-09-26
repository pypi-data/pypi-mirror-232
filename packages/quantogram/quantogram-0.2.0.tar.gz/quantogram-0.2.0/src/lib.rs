use pyo3::prelude::*;

use zw_fast_quantile::UnboundEpsilonSummary;

#[pyclass(name = "UnboundQuantileSummary")]
struct UnboundQuantileSummary {
    qg: UnboundEpsilonSummary<i64>,
}

#[pymethods]
impl UnboundQuantileSummary {
    #[new]
    fn new(epsilon: f64) -> Self {
        UnboundQuantileSummary {
            qg: UnboundEpsilonSummary::new(epsilon),
        }
    }

    fn update(&mut self, sample: i64) {
        self.qg.update(sample);
    }

    fn query(&mut self, quantile: f64) -> i64 {
        self.qg.query(quantile)
    }

    fn batch_update(&mut self, samples: Vec<i64>) {
        for sample in samples {
            self.qg.update(sample);
        }
    }

    fn batch_query(&mut self, samples: Vec<f64>) -> Vec<i64> {
        samples.iter().map(|&q| self.qg.query(q)).collect()
    }

    fn size(&self) -> usize {
        self.qg.size()
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn quantogram(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<UnboundQuantileSummary>()?;
    Ok(())
}
