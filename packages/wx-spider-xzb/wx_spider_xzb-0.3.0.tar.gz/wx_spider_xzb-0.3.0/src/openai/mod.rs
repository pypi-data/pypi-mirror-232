use color_eyre::eyre;
use color_eyre::eyre::eyre;
use openai::{
    chat::{ChatCompletion, ChatCompletionMessage, ChatCompletionMessageRole},
    set_key,
};

pub async fn parse_openai_response(
    key: String,
    content: String,
) -> eyre::Result<()> {
    let res = openai_response(key, content).await?;
    println!("openai response:{}", res);
    parse_csv(res)
}

async fn openai_response(key: String, content: String) -> eyre::Result<String> {
    set_key(key);
    let messages = vec![ChatCompletionMessage {
        role: ChatCompletionMessageRole::Assistant,
        content: Some(format!(
            "{},{}\n",
            "阅读以下通告,帮我提炼一个csv文件,每列用分号做分隔符\
            .每列依次为施工时间;施工地点;管制原因;补充信息",
            content
        )),
        name: None,
        function_call: None,
    }];

    let mut response = ChatCompletion::builder("gpt-3.5-turbo", messages)
        .create()
        .await?;

    response
        .choices
        .swap_remove(0)
        .message
        .content
        .ok_or(eyre!("choice has no content"))
}

fn parse_response(raw: String) -> Vec<Vec<String>> {
    let s: Vec<_> = raw.lines().skip(1).collect();
    let mut res = Vec::new();
    for cur_line in s {
        let x: Vec<_> = cur_line.split(';').map(|x| x.to_string()).collect();
        res.push(x);
    }
    res
}

fn parse_csv(s: String) -> eyre::Result<()> {
    let s = parse_response(s);
    let mut wtr = csv::WriterBuilder::new()
        .delimiter(b';')
        .from_path("response.csv")?;
    wtr.write_record(["施工时间", "施工地点", "管制原因", "补充信息"])?;
    for re in s {
        wtr.write_record(&re)?;
    }
    wtr.flush()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use csv::ReaderBuilder;

    use crate::configuration::get_configuration;

    use super::*;

    #[tokio::test]
    async fn test_reader() -> eyre::Result<()> {
        let data = r#"city,country,pop
Boston,United States,4628910
Concord,United States,42695"#;
        let mut rdr = ReaderBuilder::new()
            .delimiter(b',')
            .from_reader(data.as_bytes());
        for result in rdr.records() {
            let record = result?;
            println!("{}", record.iter().collect::<Vec<&str>>().join(","));
        }
        Ok(())
    }

    #[test]
    fn test_parse_csv() {
        parse_csv(
            r#"公告时间;施工地点;管制原因;项目开始到项目结束时间;补充信息
2023年8月4日;荔兰中路（尚济街-望湖路路段）;因莆田市城区排涝（张镇）泵站工程占道施工,所以管制;2023年8月8日～2023年10月8日;实行占用南侧一车道交通管制，半幅双向通行
2023年8月4日;荔兰中路（尚济街-望湖路路段）;因莆田市城区排涝（张镇）泵站工程占道施工;2023年10月8日～2024年10月8日;实行四车道全封闭交通管制，车辆利用南侧临时车道双向通行
2023年8月4日;荔兰中路（尚济街-望湖路路段）;因莆田市城区排涝（张镇）泵站工程占道施工;2024年10月9日～2025年10月9日;实行四车道恢复通车，两侧人形道全封闭交通管制
2023年7月23日;市区文献路（学园路与文献路交叉路口往文献广场方向）;因莆田市城区道路整治提升改造工程项目施工;2023年7月22日～2023年7月23日;实行局部半幅全封闭交通管制，半幅双向通行
2023年7月23日;黄石镇海滨村;龙舟教度庆典活动;活动当天;请过往驾驶人按照交通标志标线指示牌绕行、自觉服从现场交警指挥有序通行、前往村外停车场规范停车
"#.to_string()).unwrap();
    }

    #[tokio::test]
    async fn test() -> eyre::Result<()> {
        let config = get_configuration().unwrap();
        let res = openai_response(
            config.openai_key,
            r#"因莆田市城区排涝（张镇）泵站工程占道施工需要，为保证施工期间道路交通安全、畅通，决定对荔兰中路（尚济街-望湖路路段）实行临时交通管制。具体通告如下：&;
路段：荔兰中路（尚济街-望湖路路段）
第一阶段管制：
一、管制时间：2023年8月8日～2023年10月8日。
二、管制要求：实行占用南侧一车道交通管制，半幅双向通行。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
第二阶段管制：
一、管制时间：2023年10月8日～2024年10月8日。
二、管制要求：实行四车道全封闭交通管制，车辆利用南侧临时车道双向通行。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
第三阶段管制：
一、管制时间：2024年10月9日～2025年10月9日。
二、管制要求：实行四车道恢复通车，两侧人形道全封闭交通管制。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
特此通告！
&;
莆田市公安局交警支队
2023年8月4日
编&; 辑|&;郑小娅
审&; 核| 赖彩艳
审&; 批|&;陈国平莆田市公安局交警支队关于市区文献路
占道施工交通管制的通告
&; &;因莆田市城区道路整治提升改造工程项目施工需要，为保证施工期间道路交通安全、通畅，根据《中华人民共和国道路交通安全法》第三十九条规定，决定对市区文献路（学园路与文献路交叉路口往文献广场方向）实行临时交通管制。具体通告如下：&;
&; &; &; 文献路（学园路与文献路交叉路口往文献广场方向）
一、管制时间：2023年7月22日～2023年7月23日。
二、管制要求：实行局部半幅全封闭交通管制，半幅双向通行。学园路与文献路交叉路口往文献广场方向车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
编&; 辑|&;林&; &;胜
审&; 核|&;赖彩艳
审&; 批|&;陈国平因莆田市城区排涝（张镇）泵站工程占道施工需要，为保证施工期间道路交通安全、畅通，决定对荔兰中路（尚济街-望湖路路段）实行临时交通管制。具体通告如下：&;
路段：荔兰中路（尚济街-望湖路路段）
第一阶段管制：
一、管制时间：2023年8月8日～2023年10月8日。
二、管制要求：实行占用南侧一车道交通管制，半幅双向通行。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
第二阶段管制：
一、管制时间：2023年10月8日～2024年10月8日。
二、管制要求：实行四车道全封闭交通管制，车辆利用南侧临时车道双向通行。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
第三阶段管制：
一、管制时间：2024年10月9日～2025年10月9日。
二、管制要求：实行四车道恢复通车，两侧人形道全封闭交通管制。该路段车道减少，车流将有所增加，请广大市民提前安排好出行方式和线路，并根据路段路口周边设置的交通标志指示有序通行或提前绕行。
特此通告！
&;
莆田市公安局交警支队
2023年8月4日船桨翻飞
水花四溅
锣鼓齐擂
……
&; &; 2023年7月23日黄石镇海滨村龙舟教度庆典，届时将有较多群众参与活动，为确保活动的有序、安全、顺利进行，保障广大群众的生命财产安全，荔城交警将对以下海滨村周边道路实施交通管制措施。
海滨村赛龙舟
温馨提醒
请过往驾驶人
按照交通标志标线指示牌绕行
自觉服从现场交警指挥有序通行
前往村外停车场规范停车
出行小提示
1
请广大驾驶员合理规划出行时间和路线，非紧急必要，绕行拥堵路段。
2
杜绝路怒，欲速不达。已经驶入拥堵路段的车辆，请自觉排队等候，切勿气恼烦躁，依次有序通行、文明驾驶。
3
提前熟悉，提前检查。一定要提前选择并熟悉线路；根据天气和实际路况，预留足够时间，以防路上遇到特殊情况。
4
乘车合规，佩好盔带。选择正规营运站点和车辆，切勿乘坐非法营运黑包车，拒绝乘坐超员、无牌车辆；驾乘汽车时请系好安全带，骑乘摩托车、电动自行车请佩戴安全头盔。
5
服从指挥，即停即走。开车进入管制路段，请服从交警现场指挥，做到“即停、即下、即走”，按指定地点停车，不得阻碍通行。
蜀黍特别提示
&; &; &;各位驾驶人朋友请提前规划出行时间和线路，避开交通管制和拥堵路段，尽量绕道周边路网出行，减少非必要出行。交通管制期间，请过往驾驶人严格遵照交通指示标识指引，服从现场交警、交通路政及工作人员的指挥，控制车速，谨慎驾驶，安全出行！
感谢您的配合
扩散周知~"#.to_string()).await?;
        dbg!(res);
        Ok(())
    }
}
