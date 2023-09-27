use pyo3::{FromPyObject, IntoPy, PyObject, Python, types::PyDict};

#[derive(Clone)]
#[derive(FromPyObject)]
pub struct UserDecision {
    #[pyo3(item)]
    pub event_id: i32,
    #[pyo3(item)]
    pub node_id: i32,
    #[pyo3(item)]
    pub user_id: i32,
    #[pyo3(item)]
    pub next: Option<i32>,
    #[pyo3(item)]
    pub id: i32,
}

#[derive(Clone)]
#[derive(FromPyObject)]
pub struct Choice {
    #[pyo3(item)]
    pub probability_impact: f64,
    #[pyo3(item)]
    pub source_node_id: i32,
    #[pyo3(item)]
    pub popularity_impact: f64,
    #[pyo3(item)]
    pub id: i32,
    #[pyo3(item)]
    pub funds_impact: i32,
    #[pyo3(item)]
    pub target_node_id: i32,
}

impl IntoPy<PyObject> for Choice {
    fn into_py(self, py: Python) -> PyObject {
        let dict = PyDict::new(py);
        let _ = dict.set_item("probability_impact", self.probability_impact);
        let _ = dict.set_item("source_node_id", self.source_node_id);
        let _ = dict.set_item("popularity_impact", self.popularity_impact);
        let _ = dict.set_item("id", self.id);
        let _ = dict.set_item("funds_impact", self.funds_impact);
        let _ = dict.set_item("target_node_id", self.target_node_id);
        
        dict.into_py(py)
    }
}


#[derive(FromPyObject)]
pub struct StoryNode {
    #[pyo3(item)]
    pub sub_narrative: Option<String>,
    #[pyo3(item)]
    pub narrative: String,
    #[pyo3(item)]
    pub subflow_id: Option<i32>,
    #[pyo3(item)]
    pub id: i32,
    #[pyo3(item)]
    pub choices: Vec<Choice>,
}

