import { YouTubeClient } from "../src/index.js";

const client = new YouTubeClient({ apiKey: "test-key" });
void client.captions({"id": "sample"});
void client.request("youtube-captions", {"id": "sample"});
const streamResponse: Promise<Response> = client.request("youtube-captions", {"id": "sample"}, { responseType: "stream" });
const operationStream: Promise<Response> = client.operation("youtube-captions", {"id": "sample"}, { responseType: "stream" });
const directStream: Promise<Response> = client.captions({"id": "sample"}, { responseType: "stream" });
void streamResponse; void operationStream; void directStream;
void client.request("youtube-transcript", {"id": "sample", "lang": "sample", "translate_to": "sample", "format": "text", "timestamps": true}, { responseType: "text" });
const rawText: Promise<string> = client.request("youtube-captions", {"id": "sample"}, { responseType: "text" });
void rawText;
const transcriptText: Promise<string> = client.transcript({"id": "sample", "lang": "sample", "translate_to": "sample", "format": "text", "timestamps": true});
const transcriptTextViaRequest: Promise<string> = client.request("youtube-transcript", {"id": "sample", "lang": "sample", "translate_to": "sample", "format": "text", "timestamps": true});
void transcriptText; void transcriptTextViaRequest;
const transcriptStream: Promise<Response> = client.transcript({"id": "sample", "lang": "sample", "translate_to": "sample", "format": "text", "timestamps": true}, { responseType: "stream" });
void transcriptStream;
void client.search();
void client.request("youtube-search");
// @ts-expect-error The selected operation requires its documented params.
void client.captions();
