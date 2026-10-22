use crawlora_youtube::{Client, ModelYoutubeSearchResponseDoc, YoutubeSearchParams};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let api_key = std::env::var("CRAWLORA_API_KEY")?;
    let client = Client::new(api_key)?;
    let response = client
        .youtube
        .search(YoutubeSearchParams {
            q: Some("science explainers".to_owned()),
            type_: Some("video".to_owned()),
            ..Default::default()
        })
        .await?;
    let data: ModelYoutubeSearchResponseDoc = response.into_json()?;
    println!("{data:#?}");
    Ok(())
}
