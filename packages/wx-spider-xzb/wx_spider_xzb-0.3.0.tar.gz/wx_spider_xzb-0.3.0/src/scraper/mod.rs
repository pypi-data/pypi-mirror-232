use async_trait::async_trait;
use color_eyre::eyre;
use color_eyre::eyre::WrapErr;
use regex::Regex;
use reqwest::Client;
use spider::packages::scraper::{Html, Selector};

pub mod app_scraper;
pub mod base_scraper;
pub mod web_scraper;

pub async fn get_clean_httpd(
    mut scrapper: impl Scraper,
) -> eyre::Result<Vec<String>> {
    scrapper.parse_html().await
}

async fn get_html_body(client: &Client, url: &str) -> eyre::Result<String> {
    client
        .get(url)
        .send()
        .await?
        .text()
        .await
        .wrap_err("failed to parse response")
}

#[async_trait]
pub trait Scraper {
    async fn parse_html(&mut self) -> eyre::Result<Vec<String>>;
}

trait Cleaner {
    fn rm_scripts(self) -> Self;
    fn rm_english(self) -> Self;
    fn rm_lines<I, T>(self, excludes: &I) -> Self
    where
        for<'a> &'a I: IntoIterator<Item = &'a T>,
        T: AsRef<str>;
}

impl Cleaner for String {
    fn rm_scripts(mut self) -> Self {
        let document = Html::parse_document(&self);
        let selector = Selector::parse("p").unwrap();
        self = String::new();
        for element in document.select(&selector) {
            self.push_str(&format!(
                "{}\n",
                Regex::new(r"<[^>]*>")
                    .unwrap()
                    .replace_all(&element.inner_html(), "")
            ));
        }
        self
    }

    fn rm_english(self) -> Self {
        Regex::new(r"[a-zA-Z]+")
            .unwrap()
            .replace_all(&self, "")
            .to_string()
    }

    fn rm_lines<I, T>(self, exclude: &I) -> Self
    where
        for<'a> &'a I: IntoIterator<Item = &'a T>,
        T: AsRef<str>,
    {
        self.lines()
            .filter(|line| {
                !exclude
                    .into_iter()
                    .any(|exclude| line.contains(exclude.as_ref()))
                    && !line.trim().is_empty()
            })
            .collect::<Vec<_>>()
            .join("\n")
    }
}
