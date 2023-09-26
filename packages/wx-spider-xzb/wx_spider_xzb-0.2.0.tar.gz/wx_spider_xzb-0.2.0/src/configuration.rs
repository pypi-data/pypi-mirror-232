use std::collections::HashMap;

use color_eyre::eyre;
use serde::Deserialize;

#[derive(Deserialize, Clone, Debug)]
pub struct Settings {
    pub count: usize,
    pub limit: usize,
    pub uin: String,
    pub fackid_name: HashMap<String, String>,
    pub agent: String,
    pub excludes: Vec<String>,
    pub permits: Vec<String>,
    pub cookie: String,
    pub token: String,
    pub openai_key: String,
}

pub fn get_configuration(path: String) -> eyre::Result<Settings> {
    let mut settings = config::Config::default();
    settings.merge(config::File::with_name(&path))?;
    Ok(settings.try_into()?)
}
