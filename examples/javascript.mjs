import { YouTubeClient } from "@crawlora-org/youtube";

const apiKey = process.env.CRAWLORA_API_KEY;
if (!apiKey) throw new Error("Set CRAWLORA_API_KEY before running this example.");
const client = new YouTubeClient({ apiKey });

  const search = await client.search({ q: "science explainers", type: "video" });
  console.log("search", search);
  const video = await client.video({ id: "dQw4w9WgXcQ" });
  console.log("video", video);
  const transcript = await client.transcript({ id: "dQw4w9WgXcQ", format: "text" });
  console.log("transcript", transcript);
