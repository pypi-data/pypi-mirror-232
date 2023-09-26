use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Web {
    pub app_msg_list: Vec<Item>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Item {
    pub link: Option<String>,
    pub title: Option<String>,
    pub create_time: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Root {
    pub ret: Option<i32>,
    pub errmsg: Option<String>,
    pub msg_count: Option<i32>,
    pub can_msg_continue: Option<i32>,
    pub general_msg_list: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommMsgInfo {
    pub id: i32,
    #[serde(rename = "type")]
    pub type_: i32,
    pub datetime: usize,
    pub fakeid: String,
    pub status: usize,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GeneralMsgList {
    pub list: Vec<ListItem>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ListItem {
    pub app_msg_ext_info: Option<AppMsgExtInfo>,
    pub comm_msg_info: Option<CommMsgInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AppMsgExtInfo {
    pub title: Option<String>,
    pub digest: Option<String>,
    pub content: Option<String>,
    pub fileid: Option<i32>,
    pub content_url: Option<String>,
    pub source_url: Option<String>,
    pub cover: Option<String>,
    pub subtype: Option<i32>,
    pub is_multi: Option<i32>,
    pub multi_app_msg_item_list: Option<Vec<AppMsgExtInfo>>,
    pub author: Option<String>,
    pub copyright_stat: Option<i32>,
    pub duration: Option<i32>,
    pub del_flag: Option<i32>,
    pub item_show_type: Option<i32>,
    pub audio_fileid: Option<i32>,
    pub play_url: Option<String>,
    pub malicious_title_reason_id: Option<i32>,
    pub malicious_content_type: Option<i32>,
}

#[test]
fn test() {
    let a = 1;
    let a = 1;
    let a = 1;
    let a = 1;
    let a = 1;
}
