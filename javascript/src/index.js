import { groups } from "./operations.js";
import {
  CrawloraClient,
  CrawloraClientError,
  CrawloraError,
  CrawloraNetworkError,
  CrawloraServerError
} from "./client.js";

export class YouTubeClient extends CrawloraClient {
  constructor(options = {}) {
    super({ ...options, userAgent: options.userAgent ?? "crawlora-youtube-js/0.1.5" });
    this["captions"] = (...args) => this.request("youtube-captions", ...args);
    this["channelPlaylists"] = (...args) => this.request("youtube-channel-playlists", ...args);
    this["channelSearch"] = (...args) => this.request("youtube-channel-search", ...args);
    this["channelShorts"] = (...args) => this.request("youtube-channel-shorts", ...args);
    this["channelVideos"] = (...args) => this.request("youtube-channel-videos", ...args);
    this["comments"] = (...args) => this.request("youtube-comments", ...args);
    this["playlist"] = (...args) => this.request("youtube-playlist", ...args);
    this["profile"] = (...args) => this.request("youtube-profile", ...args);
    this["search"] = (...args) => this.request("youtube-search", ...args);
    this["suggest"] = (...args) => this.request("youtube-suggest", ...args);
    this["tag"] = (...args) => this.request("youtube-tag", ...args);
    this["transcript"] = (...args) => this.request("youtube-transcript", ...args);
    this["transcriptLanguages"] = (...args) => this.request("youtube-transcript-languages", ...args);
    this["video"] = (...args) => this.request("youtube-video", ...args);
  }
}

export { YouTubeClient as Client };
export {
  CrawloraClient,
  CrawloraClientError,
  CrawloraError,
  CrawloraNetworkError,
  CrawloraServerError
};
export { groups, operations, operationCount, OperationIds } from "./operations.js";
export const VERSION = "0.1.5";
export default YouTubeClient;
