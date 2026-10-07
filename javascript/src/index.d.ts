import type {
  CrawloraGeneratedGroups,
  OperationId,
  OperationParamsMap,
  OperationRequestArgs,
  OperationResponseMap
} from "./types.js";

export type CrawloraParams = Record<string, unknown>;
export type CrawloraLogEvent = { event: string; [key: string]: unknown };
export interface CrawloraRequestContext { operationId: string; method: string; url: string; headers: Record<string, string> }
export type CrawloraBeforeRequest = (ctx: CrawloraRequestContext) => void | Promise<void>;
export type CrawloraAfterResponse = (operationId: string, status: number, headers: Record<string, string>, body: unknown) => unknown;

export interface CrawloraClientOptions {
  apiKey?: string;
  jwtToken?: string;
  baseUrl?: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  maxRetryDelay?: number;
  retryStatuses?: Iterable<number>;
  isRetryable?: (status: number, error: CrawloraError) => boolean;
  onRetry?: (attempt: number, error: CrawloraError, delay: number) => void;
  requestId?: boolean;
  idempotencyKeys?: boolean;
  rateLimit?: number;
  maxConcurrency?: number;
  logger?: (event: CrawloraLogEvent) => void;
  beforeRequest?: CrawloraBeforeRequest | Iterable<CrawloraBeforeRequest>;
  afterResponse?: CrawloraAfterResponse | Iterable<CrawloraAfterResponse>;
  headers?: Record<string, string>;
  userAgent?: string | false;
  fetch?: typeof globalThis.fetch;
}

export interface CrawloraRequestOptions {
  headers?: Record<string, string>;
  responseType?: "auto" | "json" | "text" | "stream";
  timeout?: number;
  signal?: AbortSignal;
  retries?: number;
  isRetryable?: (status: number, error: CrawloraError) => boolean;
}

export interface OperationDefinition {
  id: string; method: string; path: string; pathParams: string[];
  queryParams: Array<{ name: string; in?: "query"; collectionFormat?: string; type?: string; required?: boolean; enum?: string[] }>;
  formParams: Array<{ name: string; in?: "formData"; type?: string; required?: boolean; enum?: string[] }>;
  bodyParam?: string; bodyRequired?: boolean; consumes: string[]; produces: string[]; security: string[];
  paginatable?: boolean; cursorParams?: string[];
}

export class CrawloraError extends Error {
  status: number; code?: number; body: unknown; headers: Record<string, string>;
  response?: Response; cause?: unknown; retryable?: boolean; requestId?: string;
}
export class CrawloraClientError extends CrawloraError {}
export class CrawloraServerError extends CrawloraError {}
export class CrawloraNetworkError extends CrawloraError {}

export interface CrawloraPaginateOptions extends CrawloraRequestOptions {
  pageParam?: string; cursorParam?: string; nextCursor?: (page: unknown) => unknown;
  start?: unknown; step?: number; maxPages?: number;
}
export interface CrawloraPaginateItemsOptions extends CrawloraPaginateOptions {
  items?: (page: unknown) => Iterable<unknown>;
}

export class CrawloraClient {
  constructor(options?: CrawloraClientOptions);
  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  request<I extends OperationId>(operationId: I, ...args: OperationRequestArgs<I>): Promise<OperationResponseMap[I]>;
  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  operation<I extends OperationId>(operationId: I, ...args: OperationRequestArgs<I>): Promise<OperationResponseMap[I]>;
  paginate<I extends OperationId>(operationId: I, params?: OperationParamsMap[I], options?: CrawloraPaginateOptions): AsyncGenerator<OperationResponseMap[I], void, unknown>;
  paginateItems<I extends OperationId>(operationId: I, params?: OperationParamsMap[I], options?: CrawloraPaginateItemsOptions): AsyncGenerator<unknown, void, unknown>;
  [group: string]: unknown;
}
export interface CrawloraClient extends CrawloraGeneratedGroups {}

export class YouTubeClient extends CrawloraClient {
  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  captions(params: OperationParamsMap["youtube-captions"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  channelPlaylists(params: OperationParamsMap["youtube-channel-playlists"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  channelSearch(params: OperationParamsMap["youtube-channel-search"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  channelShorts(params: OperationParamsMap["youtube-channel-shorts"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  channelVideos(params: OperationParamsMap["youtube-channel-videos"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  comments(params: OperationParamsMap["youtube-comments"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  playlist(params: OperationParamsMap["youtube-playlist"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  profile(params: OperationParamsMap["youtube-profile"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  search(params?: OperationParamsMap["youtube-search"], options?: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  suggest(params: OperationParamsMap["youtube-suggest"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  tag(params: OperationParamsMap["youtube-tag"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  transcript(params: OperationParamsMap["youtube-transcript"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  transcriptLanguages(params: OperationParamsMap["youtube-transcript-languages"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  video(params: OperationParamsMap["youtube-video"], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  captions(params: OperationParamsMap["youtube-captions"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  channelPlaylists(params: OperationParamsMap["youtube-channel-playlists"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  channelSearch(params: OperationParamsMap["youtube-channel-search"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  channelShorts(params: OperationParamsMap["youtube-channel-shorts"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  channelVideos(params: OperationParamsMap["youtube-channel-videos"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  comments(params: OperationParamsMap["youtube-comments"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  playlist(params: OperationParamsMap["youtube-playlist"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  profile(params: OperationParamsMap["youtube-profile"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  search(params?: OperationParamsMap["youtube-search"], options?: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  suggest(params: OperationParamsMap["youtube-suggest"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  tag(params: OperationParamsMap["youtube-tag"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  transcript(params: OperationParamsMap["youtube-transcript"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  transcriptLanguages(params: OperationParamsMap["youtube-transcript-languages"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  video(params: OperationParamsMap["youtube-video"], options: CrawloraRequestOptions & { responseType: "text" }): Promise<string>;
  transcript(params: OperationParamsMap["youtube-transcript"] & { format: "text" | "srt" | "vtt" }, options?: Omit<CrawloraRequestOptions, "responseType"> & { responseType?: "auto" | "text" }): Promise<string>;
  request(operationId: "youtube-transcript", params: OperationParamsMap["youtube-transcript"] & { format: "text" | "srt" | "vtt" }, options?: Omit<CrawloraRequestOptions, "responseType"> & { responseType?: "auto" | "text" }): Promise<string>;
  operation(operationId: "youtube-transcript", params: OperationParamsMap["youtube-transcript"] & { format: "text" | "srt" | "vtt" }, options?: Omit<CrawloraRequestOptions, "responseType"> & { responseType?: "auto" | "text" }): Promise<string>;
  request<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  request<I extends OperationId>(operationId: I, ...args: OperationRequestArgs<I>): Promise<OperationResponseMap[I]>;
  operation<I extends OperationId>(operationId: I, params: OperationParamsMap[I], options: CrawloraRequestOptions & { responseType: "stream" }): Promise<Response>;
  operation<I extends OperationId>(operationId: I, ...args: OperationRequestArgs<I>): Promise<OperationResponseMap[I]>;
  captions(...args: OperationRequestArgs<"youtube-captions">): Promise<OperationResponseMap["youtube-captions"]>;
  channelPlaylists(...args: OperationRequestArgs<"youtube-channel-playlists">): Promise<OperationResponseMap["youtube-channel-playlists"]>;
  channelSearch(...args: OperationRequestArgs<"youtube-channel-search">): Promise<OperationResponseMap["youtube-channel-search"]>;
  channelShorts(...args: OperationRequestArgs<"youtube-channel-shorts">): Promise<OperationResponseMap["youtube-channel-shorts"]>;
  channelVideos(...args: OperationRequestArgs<"youtube-channel-videos">): Promise<OperationResponseMap["youtube-channel-videos"]>;
  comments(...args: OperationRequestArgs<"youtube-comments">): Promise<OperationResponseMap["youtube-comments"]>;
  playlist(...args: OperationRequestArgs<"youtube-playlist">): Promise<OperationResponseMap["youtube-playlist"]>;
  profile(...args: OperationRequestArgs<"youtube-profile">): Promise<OperationResponseMap["youtube-profile"]>;
  search(...args: OperationRequestArgs<"youtube-search">): Promise<OperationResponseMap["youtube-search"]>;
  suggest(...args: OperationRequestArgs<"youtube-suggest">): Promise<OperationResponseMap["youtube-suggest"]>;
  tag(...args: OperationRequestArgs<"youtube-tag">): Promise<OperationResponseMap["youtube-tag"]>;
  transcript(...args: OperationRequestArgs<"youtube-transcript">): Promise<OperationResponseMap["youtube-transcript"]>;
  transcriptLanguages(...args: OperationRequestArgs<"youtube-transcript-languages">): Promise<OperationResponseMap["youtube-transcript-languages"]>;
  video(...args: OperationRequestArgs<"youtube-video">): Promise<OperationResponseMap["youtube-video"]>;
}
export { YouTubeClient as Client };
export const operations: Record<string, OperationDefinition>;
export const groups: Record<string, Record<string, string>>;
export const operationCount: number;
export const OperationIds: Readonly<Record<string, OperationId>>;
export const VERSION: string;
export * from "./types.js";
export default YouTubeClient;
