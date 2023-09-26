use std::borrow::Cow;
use std::collections::HashMap;

use async_trait::async_trait;
use color_eyre::eyre;
use reqwest::Client;

use crate::msg::Web;
use crate::scraper::base_scraper::BaseScraper;
use crate::scraper::{get_html_body, Cleaner, Scraper};
use crate::CLIENT;

pub struct WebScraper {
    base: BaseScraper,
    params: HashMap<Cow<'static, str>, Cow<'static, str>>,
}

#[async_trait]
impl Scraper for WebScraper {
    async fn parse_html(&mut self) -> eyre::Result<Vec<String>> {
        let tup = self.total_list().await?;
        let mut res = Vec::new();
        let mut limit = 0;
        for t in tup.iter() {
            let title = &t.2;
            if limit >= self.base.limit {
                break;
            }
            if self.base.config.permits.iter().any(|p| title.contains(p)) {
                limit += 1;
                println!("going to page {}", t.1);
                let http_body =
                    get_html_body(CLIENT.get().unwrap(), &t.1).await?;
                let result = http_body
                    .rm_scripts()
                    .rm_english()
                    .rm_lines(&self.base.config.excludes);
                println!("title: {}, content:{}", title, result);
                res.push(result);
            }
        }
        Ok(res)
    }
}

impl WebScraper {
    pub fn new(
        scraper: BaseScraper,
        token: &'static str,
        fakeid: &'static str,
        query: &'static str,
    ) -> Self {
        Self {
            params: HashMap::from([
                ("f".into(), "json".into()),
                ("action".into(), "list_ex".into()),
                ("fakeid".into(), fakeid.into()),
                ("count".into(), "5".into()),
                ("type".into(), "9".into()),
                ("token".into(), token.into()),
                ("ajax".into(), "1".into()),
            ]),
            base: scraper,
        }
    }

    async fn five_items_from_list(
        &mut self,
        offset: usize,
        client: &Client,
    ) -> eyre::Result<Vec<(usize, String, String)>> {
        let origin_url = "https://mp.weixin.qq.com/cgi-bin/appmsg";
        self.params
            .insert("begin".into(), offset.to_string().into());
        let request = client
            .get(origin_url)
            .headers(self.base.headers.clone())
            .query(&self.params)
            .build()?;
        println!("Sending request to URL: {}", request.url());

        let resp: Web = client.execute(request).await?.json().await?;
        dbg!(&resp);

        Ok(resp
            .app_msg_list
            .into_iter()
            .map(|item| {
                (item.create_time, item.link.unwrap(), item.title.unwrap())
            })
            .collect())
    }

    async fn total_list(
        &mut self,
    ) -> eyre::Result<Vec<(usize, String, String)>> {
        let mut start_count = 0;
        let mut res = Vec::new();
        loop {
            println!("{start_count}");
            let url_tuple = self
                .five_items_from_list(start_count, CLIENT.get().unwrap())
                .await?;
            // let date_time = url_tuple.0;
            start_count += 5;
            res.extend(url_tuple);
            if start_count > self.base.count {
                return Ok(res);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    // #[tokio::test]
    // async fn test_web() -> anyhow::Result<()> {
    //     let setting = get_configuration()?;
    //     let mut vec = Vec::new();
    //
    //     for (biz, key) in &setting.biz {
    //         println!("key:{key}");
    //         println!("biz:{biz}");
    //         let mut scraper = BaseScraperBuilder::default()
    //             .config(setting.clone())
    //             .count(10)
    //             .biz(biz.into())
    //             .build()?;
    //
    //         // let handle = tokio::spawn(async move { WebScraper::new(scraper.parse_html().await });
    //         // vec.push(handle);
    //     }
    //     for handle in vec {
    //         let _ = handle.await;
    //     }
    //     Ok(())
    // }
    #[test]
    fn foo() {
        let s = "asdasd".to_string();
        dbg!(&s);
        s.contains("asdas");
    }
}
