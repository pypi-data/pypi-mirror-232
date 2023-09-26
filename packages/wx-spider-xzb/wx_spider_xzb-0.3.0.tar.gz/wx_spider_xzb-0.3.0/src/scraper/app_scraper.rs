use std::collections::HashMap;

use async_trait::async_trait;
use color_eyre::eyre;

use crate::msg::{CommMsgInfo, GeneralMsgList, Root};
use crate::scraper::base_scraper::BaseScraper;
use crate::scraper::{get_html_body, Cleaner, Scraper};
use crate::CLIENT;

pub struct AppScraper {
    base: BaseScraper,
    params: HashMap<String, String>,
}

#[async_trait]
impl Scraper for AppScraper {
    async fn parse_html(&mut self) -> eyre::Result<Vec<String>> {
        let url_title_tup = self.total_list().await?;
        let mut res = Vec::new();
        for t in url_title_tup.iter() {
            let title = &t.1;
            if self.base.config.permits.iter().any(|p| title.contains(p)) {
                println!("going to page {}", t.0);
                let http_body =
                    get_html_body(CLIENT.get().unwrap(), &t.0).await?;

                let result = http_body
                    .rm_scripts()
                    .rm_english()
                    .rm_lines(&self.base.config.excludes);

                // log::trace!("title: {}, content:{}", title, result);
                res.push(result.clone());
            }
        }
        Ok(res)
    }
}

impl AppScraper {
    pub fn new(key: String, base: BaseScraper, biz: String) -> Self {
        Self {
            params: HashMap::from([
                ("f".into(), "json".into()),
                ("action".into(), "getmsg".into()),
                ("__biz".into(), biz),
                ("uin".into(), base.config.uin.clone()),
                ("key".into(), key),
                ("count".into(), "10".into()),
            ]),
            base,
        }
    }

    async fn ten_items_from_list(
        &mut self,
        offset: usize,
    ) -> eyre::Result<(usize, Vec<(String, String)>)> {
        let origin_url = "https://mp.weixin.qq.com/mp/profile_ext";
        self.params.insert("offset".to_string(), offset.to_string());
        let client = CLIENT.get().unwrap();
        let request = client
            .get(origin_url)
            .headers(self.base.headers.clone())
            .query(&self.params)
            .build()?;
        println!("Sending request to URL: {}", request.url());
        let resp = client.execute(request).await?.json::<Root>().await?;
        println!("resp:{:?}", resp);
        let general_msg_list: GeneralMsgList = serde_json::from_str(
            &resp.general_msg_list.expect("general_msg_list is None"),
        )?;

        let mut res = Vec::new();
        let mut msg_info: Option<CommMsgInfo> = None;

        for item in general_msg_list.list {
            let ext_info =
                item.app_msg_ext_info.expect("app_msg_ext_info is None");
            msg_info = item.comm_msg_info;
            res.push((
                ext_info.content_url.expect("content_url is None"),
                ext_info.title.expect("title should not be None"),
            ));

            if let Some(multi_app_msg_item_list) =
                ext_info.multi_app_msg_item_list
            {
                for item in multi_app_msg_item_list {
                    res.push((
                        item.content_url.expect("content_url is None"),
                        item.title.expect("title is None"),
                    ));
                }
            }
        }
        Ok((msg_info.expect("no msg info").datetime, res))
    }

    async fn total_list(&mut self) -> eyre::Result<Vec<(String, String)>> {
        let mut start_count = 0;
        let mut res = Vec::new();
        loop {
            println!("{start_count}");
            let url_tuple = self.ten_items_from_list(start_count).await?;
            let date_time = url_tuple.0;
            start_count += 10;
            res.extend(url_tuple.1);
            if date_time <= self.base.start_timestamp
                || start_count > self.base.count
            {
                return Ok(res);
            }
            // tokio::time::sleep(Duration::from_secs(3)).await;
        }
    }
}

#[cfg(test)]
mod tests {
    use std::fs::{read_to_string, File};
    use std::io::Write;

    use spider::packages::scraper::{Html, Selector};

    use crate::configuration::get_configuration;
    use crate::scraper::Cleaner;

    #[test]
    fn html_raw() {
        let mut f1 = File::create("out1").unwrap();
        let mut f2 = File::create("out2").unwrap();
        let mut f3 = File::create("out3").unwrap();
        let s = read_to_string("/Users/xzb/Project/Rust/wechat-spider/ht.txt")
            .unwrap();
        // let config = get_configuration().unwrap();
        let mut result = s.rm_scripts();
        f1.write_all(result.as_bytes()).unwrap();
        result = result.rm_english();

        f2.write_all(result.as_bytes()).unwrap();
        // result = result.rm_lines(&config.excludes);
        // println!("{}", result);
        f3.write_all(result.as_bytes()).unwrap();
    }

    #[test]
    fn html_raw_pretty() {
        let mut f = File::create("out_pretty").unwrap();
        let s =
            read_to_string("/Users/xzb/Project/Rust/wechat-spider/wechat.txt")
                .unwrap();
        // let config = get_configuration().unwrap();
        let mut result = s.rm_scripts();
        f.write_all(result.as_bytes()).unwrap();
        result = result.rm_english();
        f.write_all(result.as_bytes()).unwrap();
        // result = result.rm_lines(&config.excludes);
        // println!("{}", result);
        f.write_all(result.as_bytes()).unwrap();
    }

    #[test]
    fn select() {
        let s = read_to_string("/Users/xzb/Project/Rust/wechat-spider/ht.txt")
            .unwrap();
        let document = Html::parse_document(&s);
        let _selector1 =
            Selector::parse(r#"p[style="outline: 0px;text-indent: 0em;"]"#)
                .unwrap();
        let _selector2 =
            Selector::parse(r#"p[style="outline: 0px;text-indent: 2em;"]"#)
                .unwrap();
        let selector3 = Selector::parse("p").unwrap();
        // let input = document.select(&selector).next().unwrap();
        let mut f = File::create("inner").unwrap();
        // for input in document.select(&selector1) {
        //     f.write(input.inner_html().as_bytes());
        // }
        // for input in document.select(&selector2) {
        //     f.write(input.inner_html().as_bytes());
        // }
        for input in document.select(&selector3) {
            f.write_all(input.inner_html().as_bytes()).unwrap();
            f.write_all(b"\n").unwrap();
        }
    }

    // #[test]
    // fn foo() {
    //     // let e = get_configuration().unwrap().excludes;
    //     let s = r#"微信扫一扫关注该公众号
    //
    //     j
    //
    //
    //     "#
    //     .to_string();
    //     let x = s
    //         .lines()
    //         .inspect(|s| println!("get one line before:{s}"))
    //         .filter(move |line| {
    //             !e.iter().any(|exclude| line.contains(exclude))
    //                 && !line.is_empty()
    //         })
    //         // .filter(|line| !line.is_empty())
    //         .inspect(|s| println!("get one line after:{s}"))
    //         .collect::<Vec<&str>>()
    //         .join("\n")
    //         .trim()
    //         .to_string();
    //     println!("{x}");
    // }
}
