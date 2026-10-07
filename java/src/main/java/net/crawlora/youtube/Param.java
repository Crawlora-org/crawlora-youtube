package net.crawlora.youtube;

import java.util.List;

/** Parameter contract for a selected platform operation. */
public record Param(String name, String location, boolean required, String type, List<String> enumValues, String collectionFormat) {}
