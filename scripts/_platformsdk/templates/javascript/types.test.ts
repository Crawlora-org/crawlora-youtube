import { {{class_name}} } from "../src/index.js";

const client = new {{class_name}}({ apiKey: "test-key" });
void client.{{first_method}}({{first_params_ts}});
void client.request({{first_operation_json}}, {{first_params_json}});
const streamResponse: Promise<Response> = client.request({{first_operation_json}}, {{first_params_json}}, { responseType: "stream" });
const operationStream: Promise<Response> = client.operation({{first_operation_json}}, {{first_params_json}}, { responseType: "stream" });
const directStream: Promise<Response> = client.{{first_method}}({{first_params_json}}, { responseType: "stream" });
void streamResponse; void operationStream; void directStream;
void client.request({{text_operation_json}}, {{text_params_ts}}, { responseType: "text" });
const rawText: Promise<string> = client.request({{first_operation_json}}, {{first_params_json}}, { responseType: "text" });
void rawText;
{{transcript_type_test}}
{{transcript_stream_type_test}}
{{optional_method_test}}
// @ts-expect-error The selected operation requires its documented params.
void client.{{first_method}}();
