mod configuration;
mod msg;
mod openai;
mod scraper;

use crate::configuration::{get_configuration, Settings};
use crate::scraper::base_scraper::BaseScraperBuilder;
use crate::scraper::get_clean_httpd;
use crate::scraper::web_scraper::WebScraper;
use color_eyre::eyre;
use pyo3::prelude::*;
use reqwest::Client;
use std::collections::HashMap;
use std::hash::Hash;
use std::sync::OnceLock;

static CONFIG: OnceLock<Settings> = OnceLock::new();
static CLIENT: OnceLock<Client> = OnceLock::new();

#[pyfunction]
fn get_scrap_result(path: String) -> PyResult<HashMap<String, Vec<String>>> {
    let rt = tokio::runtime::Runtime::new().unwrap();
    let result = rt.block_on(scraper(path)).unwrap();
    Ok(result)
}

async fn scraper(path: String) -> eyre::Result<HashMap<String, Vec<String>>> {
    color_eyre::install().unwrap();
    CLIENT.get_or_init(Client::new);
    let config = CONFIG.get_or_init(|| get_configuration(path).unwrap());
    let mut res = HashMap::new();
    for (fackid, query) in &config.fackid_name {
        let base = BaseScraperBuilder::default()
            .config(config)
            .count(config.count)
            .limit(config.limit)
            .build()
            .unwrap();
        let handle = tokio::spawn(get_clean_httpd(WebScraper::new(
            base,
            &config.token,
            fackid,
            query,
        )));
        res.insert(query.clone(), handle.await.unwrap().unwrap());
    }
    Ok(res)
}
/// A Python module implemented in Rust.
#[pymodule]
fn wx_spider_xzb(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_scrap_result, m)?)?;
    Ok(())
}
