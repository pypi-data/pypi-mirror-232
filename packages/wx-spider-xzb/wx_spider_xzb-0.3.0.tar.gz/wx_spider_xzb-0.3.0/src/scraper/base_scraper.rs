use derive_builder::Builder;
use reqwest::header::{HeaderMap, COOKIE, USER_AGENT};

use crate::configuration::Settings;

#[derive(Builder)]
pub struct BaseScraper {
    pub config: &'static Settings,
    #[builder(default = "0")]
    pub start_timestamp: usize,
    #[builder(default = "10")]
    pub count: usize,
    #[builder(default = "2")]
    pub limit: usize,
    #[builder(default = "self.default_header()")]
    #[builder(setter(skip))]
    pub headers: HeaderMap,
}

impl BaseScraperBuilder {
    fn default_header(&self) -> HeaderMap {
        HeaderMap::from_iter([
            (USER_AGENT, self.config.unwrap().agent.parse().unwrap()),
            (COOKIE, self.config.unwrap().cookie.parse().unwrap()),
        ])
    }
}
