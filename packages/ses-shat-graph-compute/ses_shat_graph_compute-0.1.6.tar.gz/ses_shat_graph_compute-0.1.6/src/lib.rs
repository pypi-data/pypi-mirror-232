mod models;

use std::collections::{HashMap, HashSet};

use models::{StoryNode, UserDecision, Choice};
use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn build_user_graph(current_node_id: i32, story_nodes: Vec<StoryNode>, user_decisions: Vec<UserDecision>, sf_user_decisions: Vec<UserDecision>) -> PyResult<(Vec<i32>, Vec<Choice>, Vec<Vec<i32>>)> {
    let mut nodes_dict: HashMap<i32, StoryNode> = HashMap::new();
    let mut user_decision_dict: HashMap<i32, UserDecision> = HashMap::new();

    for item in story_nodes {
        nodes_dict.insert(item.id, item);
    }

    for item in user_decisions {
        user_decision_dict.insert(item.id, item);
    }

    let mut node_ids: HashSet<i32> = HashSet::new();
    let mut choices: Vec<Choice> = vec![];
    let mut decision_edges: Vec<Vec<i32>> = vec![];
    
    let mut current_node: &StoryNode;
    let mut update_choices: Vec<i32>;

    let start_ud = user_decision_dict.values().find(|&decision| decision.node_id == 1).unwrap();

    let starting_nodes: Vec<&UserDecision> = std::iter::once(start_ud).chain(sf_user_decisions.iter()).collect::<Vec<&UserDecision>>();

    node_ids.insert(current_node_id);
    decision_edges.push(vec![1, 1]);

    for start_node in starting_nodes{
        let mut current_ud = start_node;
        while current_ud.next.is_some() {
            let temp = user_decision_dict.get(&current_ud.next.unwrap()).unwrap();
            decision_edges.push(vec![current_ud.node_id, temp.node_id]);
    
            current_node = nodes_dict.get(&current_ud.node_id).unwrap();
            node_ids.insert(current_node.id);
            update_choices = current_node.choices.iter().map(|x| x.target_node_id).collect::<Vec<i32>>();
            node_ids.extend(update_choices.iter());
            choices.extend(current_node.choices.iter().cloned());
    
            current_ud = temp;
        }
    }

    let node_ids_vec: Vec<i32> = node_ids.iter().cloned().collect();

    Ok((node_ids_vec, choices, decision_edges))
}

/// A Python module implemented in Rust.
#[pymodule]
fn ses_shat_graph_compute(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_user_graph, m)?)?;
    Ok(())
}