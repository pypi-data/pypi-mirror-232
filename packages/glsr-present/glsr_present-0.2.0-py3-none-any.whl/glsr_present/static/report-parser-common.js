/*
 * report-parser-common.js
 *
 * Pretty-print a GitLab security report
 *
 * (c) 2023 Oliver Haase / Rainer Schwarzbach
 *
 */


function changeStyle(selector, new_style) {
    // Replace an existing CSS rule by a new one
    const stylesheet = document.styleSheets[0];
    const rules = stylesheet.cssRules;
    let deletable = null;
    for (let index=0; index < rules.length; index++) {
        if (rules.item(index).selectorText == selector) {
            deletable = index;
            break;
        }
    }
    if (deletable != null) {
        stylesheet.deleteRule(deletable);
    }
    stylesheet.insertRule(`${selector} { ${new_style} }`);
}


function toggleRowsVisibility(severity) {
    // Toggle rows visibility depending on the appropriate checkbox state
    const checkbox = document.querySelector(`#display${severity}`);
    if (checkbox.checked) {
        changeStyle(`.row${severity}`, "display: table-row");
    } else {
        changeStyle(`.row${severity}`, "display: none");
    }
    return true;        
}


function setAttribute(element, attribute_name, value) {
    // Set one named attribute
    const attribute = document.createAttribute(attribute_name);
    if (value != null) {
        attribute.value = value;
    }
    element.setAttributeNode(attribute);
}


function setMultipleAttributes(element, attributes_map) {
    // Set multiple named attributes of the element
    for ([attribute_name, value] of attributes_map.entries()) {
        setAttribute(element, attribute_name, value);
    }
}


function getHeadline(level, text) {
    // Return a headline
    const headline = document.createElement(`h${level}`);
    headline.appendChild(document.createTextNode(text));
    return headline;
}


function getParagraph(text) {
    // Return a paragraph
    const paragraph = document.createElement("p");
    paragraph.appendChild(document.createTextNode(text));
    return paragraph;
}


function getTableCell(contents) {
    // Return a table cell with each contents item appended as a child
    const cell = document.createElement("td");
    for (let item of contents) {
        cell.appendChild(item);
    }
    return cell;
}


function getSeverityCell(severity) {
    // Create a table cell for a vulnerability
    const cell = document.createElement("td");
    setAttribute(cell, "class", severity);
    cell.appendChild(document.createTextNode(severity));
    return cell;
}


function getTextCell(text) {
    // Create a simple table cell containing text only
    return getTableCell([document.createTextNode(text)]);
}


function getLink(text, url) {
    // Create a link
    const link = document.createElement("a");
    setAttribute(link, "href", url);
    link.appendChild(document.createTextNode(text));
    return link;
}


function getLinkCell(text, url) {
    // Create a simple table cell containing text linking to the url
    return getTableCell([getLink(text, url)]);
}


function getTextHeaderCell(text) {
    // Create a simple table header cell containing text only
    const cell = document.createElement("th");
    cell.appendChild(document.createTextNode(text));
    return cell;
}


function getTabularDataRow(th_text, table_cell) {
    // Create a simple table row containing one
    // header cell containing th text, followed by table_cell
    const line = document.createElement("tr");
    line.appendChild(getTextHeaderCell(th_text));
    line.appendChild(table_cell);
    return line;
}


function getDetails(summary_text) {
    // return a <details> element
    const details = document.createElement("details"); 
    const summary = document.createElement("summary"); 
    details.appendChild(summary);
    summary.appendChild(document.createTextNode(summary_text));
    return details;
}


function getTable(headings) {
    // Create a table with one row containing
    // one <th> element per headings item in the <thead>,
    // and return it.
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const thead_row = document.createElement("tr");
    // Create table header
    for (let single_item of headings) {
        thead_row.appendChild(getTextHeaderCell(single_item));
    }
    thead.appendChild(thead_row);
    table.appendChild(thead);
    return table;
}


function getSeverityMap(severity, vulnerability_id) {
    // Return a Map of arrays per severity,
    // initialized with the provided severity and vulnerability_id
    const severity_map = new Map();
    severity_map.set("Critical", []);
    severity_map.set("High", []);
    severity_map.set("Medium", []);
    severity_map.set("Low", []);
    severity_map.set("Info", []);
    severity_map.get(severity).push(vulnerability_id);
    return severity_map
}


function updateItemsMap(items_map, item, severity, vulnerability_id) {
    // Update the items map (in place):
    // append vulnerability to the severity entry belonging to item
    if (items_map.has(item)) {
        const sev_by_item = items_map.get(item);
        if (sev_by_item.has(severity)) {
            sev_by_item.get(severity).push(vulnerability_id);
        } else {
            sev_by_item.set(severity, [vulnerability_id]);
        }
    } else {
        items_map.set(item, getSeverityMap(severity, vulnerability_id));
    }
    
}


function getMetadataTable(scan_data, report_url, build_info) {
    // Return a table containing scan metadata
    // const metadata = document.getElementById("metadata");
    const meta_table = document.createElement("table");
    const meta_tbody = document.createElement("tbody");
    // Analyzer (GitLab security product name)
    meta_tbody.appendChild(
        getTabularDataRow(
            "Analyzer",
            getTextCell(
                `${scan_data.analyzer.name} ${scan_data.analyzer.version}`
            )
        )
    );
    // Scanner (original security product used)
    meta_tbody.appendChild(
        getTabularDataRow(
            "Scanner",
            getLinkCell(
                `${scan_data.scanner.name} ${scan_data.scanner.version}`,
                scan_data.scanner.url
            )
        )
    );
    // Start and End Times
    meta_tbody.appendChild(
        getTabularDataRow("Start Time", getTextCell(scan_data.start_time))
    );
    meta_tbody.appendChild(
        getTabularDataRow("End Time", getTextCell(scan_data.end_time))
    );
    // Status
    meta_tbody.appendChild(
        getTabularDataRow("Status", getTextCell(scan_data.status))
    );
    // Report Source
    meta_tbody.appendChild(
        getTabularDataRow(
            "Generated Report",
            getLinkCell("original JSON format", report_url)
        )
    );
    // Link pipeline if defined
    if (build_info.ci_project_url != null) {
        meta_tbody.appendChild(
            getTabularDataRow(
                "CI Pipeline",
                getLinkCell(
                    build_info.ci_pipeline_id, build_info.ci_pipeline_url
                )
            )
        );
    }
    // Close table body
    meta_table.appendChild(meta_tbody);
    return meta_table;
}


function getVulnerabilityStatistics(items_map) {
    // Return a block containing vulnerability statistics per item
    // (ie. container image, file, ...) and severity
    const stats_block = document.createElement("div");
    const stats_heading = document.createElement("h2");
    stats_block.appendChild(stats_heading);
    if (items_map.size == 0) {
        stats_heading.appendChild(
            document.createTextNode("No vulnerabilities found!")
        );
        return stats_block;
    }
    stats_heading.appendChild(document.createTextNode("Per-item statistics"));
    // Find all possible severities
    const severities = []
    items_map.forEach(
        function(sev_map, image_name, map) {
            sev_map.forEach(
                function (cves, sev_name, map2) {
                    if (severities.indexOf(sev_name) == -1) {
                        severities.push(sev_name);
                    }
                }
            );
        }
    );
    const vuln_table = document.createElement("table");
    const vuln_tbody = document.createElement("tbody");
    const first_line = document.createElement("tr");
    first_line.appendChild(getTextHeaderCell("↓ items / severities →"));
    for (let single_sev of severities) {
        let display_toggle = document.createElement("input");
        let display_toggle_id = `display${single_sev}`
        setAttribute(display_toggle, "type", "checkbox");
        setAttribute(display_toggle, "id", display_toggle_id);
        setAttribute(display_toggle, "checked", null);
        setAttribute(
            display_toggle, 
            "onclick", 
            `return toggleRowsVisibility('${single_sev}');`
        );
        let display_label = document.createElement("label");
        setAttribute(display_label, "for", display_toggle_id);
        display_label.appendChild(document.createTextNode(single_sev));
        first_line.appendChild(getTableCell([display_toggle, display_label]));
    }
    vuln_tbody.appendChild(first_line);
    items_map.forEach(
        function(sev_map, item_name, map) {
            const vuln_line = document.createElement("tr"); 
            vuln_line.appendChild(getTextHeaderCell(item_name));
            for (let single_sev of severities) {
                let sev_text = "";
                if (sev_map.has(single_sev)) {
                    sev_text = sev_map.get(single_sev).length.toString();
                }
                vuln_line.appendChild(getTextCell(sev_text));
            }
            vuln_tbody.appendChild(vuln_line);
        }
    );
    vuln_table.appendChild(vuln_tbody);
    stats_block.appendChild(vuln_table);
    return stats_block;
}

function writeContainerScanTable(body_main, vulnerabilities, build_info) {
    // Write a table containing the found vulnerabilities
    // from the container scan,
    // and return a mapping of cve lists per severity per image
    const items_map = new Map();
    const table = getTable(
        [
            "#", 
            "Library", 
            "Vulnerability", 
            "Severity", 
            "Installed Version", 
            "Solution", 
            "Description"
        ]
    );
    const tbody = document.createElement("tbody");
    vulnerabilities.forEach(
        function(vulnerability, vuln_idx, ar) {
            // Track vulnerabilities by container image
            const current_image = vulnerability.location.image;
            updateItemsMap(
                items_map, 
                current_image, 
                vulnerability.severity, 
                vulnerability.cve
            );
            // Output one row per vulnerability
            const row = document.createElement("tr");
            setAttribute(row, "class", `row${vulnerability.severity}`);
            // Column 0: Numerical index
            row.appendChild(getTextCell(vuln_idx.toString()));
            // Column 1: Package name
            const package_cell = getTextCell(
                vulnerability.location.dependency.package.name
            )
            setAttribute(
                package_cell, "title", `[image: ${current_image}]`
            );
            row.appendChild(package_cell);
            // Column 2: CVE ID and all links belonging to it
            const cve_cell = document.createElement("td");
            const cve_primary = document.createElement("p");
            cve_cell.appendChild(cve_primary)
            vulnerability.identifiers.forEach(
                function(identifier, idx, ar) {
                    const id_link = getLink(identifier.name, identifier.url);
                    setAttribute(
                        id_link, "title", `[type: ${identifier.type}]`
                    );
                    cve_primary.appendChild(id_link);
                    cve_primary.appendChild(document.createTextNode(", "));
                }
            );
            const other_links_details = getDetails("see also:"); 
            const cve_see_also_list = document.createElement("ul");
            vulnerability.links.forEach(
                function(link, idx, ar) {
                    // the first link is the same as the first identifier URL,
                    // so we do not need to link it again here.
                    if (idx == 0) {
                        return;
                    }
                    const link_item = document.createElement("li");
                    link_item.appendChild(
                        getLink(
                            link.url.match(/^https?:\/\/([^\/]+)/)[1], link.url
                        )
                    );
                    cve_see_also_list.appendChild(link_item);
                }
            );
            other_links_details.appendChild(cve_see_also_list)
            cve_cell.appendChild(other_links_details)
            row.appendChild(cve_cell);
            // Column 3: Severity, colored
            row.appendChild(getSeverityCell(vulnerability.severity));
            // Column 4: Installed (= vulnerable) package version
            row.appendChild(
                getTextCell(vulnerability.location.dependency.version)
            );
            // Column 5: Solution
            row.appendChild(getTextCell(vulnerability.solution));
            // Column 6: Long description
            row.appendChild(getTextCell(vulnerability.description));
            tbody.appendChild(row);
        }
    );
    table.appendChild(tbody);
    // Write table output only if any vulnerability was found
    if (items_map.size > 0) {
        body_main.appendChild(getHeadline(2, "Found vulnerabilities:"));
        body_main.appendChild(table);
    }
    return items_map;
}

function writeSASTTable(body_main, vulnerabilities, build_info) {
    // Write a table containing the found vulnerabilities from the SAST report,
    // and return a mapping of cve lists per severity per file name
    let base_url = null;
    if (build_info.ci_project_url != null) {
        base_url = `${build_info.ci_project_url}/-/blob/${build_info.ci_commit_sha}`
    }
    const items_map = new Map();
    const table = getTable(
        ["#", "Location", "Vulnerability", "Severity", "Message", "Description"]
    );
    const tbody = document.createElement("tbody");
    vulnerabilities.forEach(
        function(vulnerability, vuln_idx, ar) {
            // Track vulnerabilities by file names
            updateItemsMap(
                items_map, 
                vulnerability.location.file, 
                vulnerability.severity, 
                vulnerability.cve
            );
            // Output one row per vulnerability
            const row = document.createElement("tr");
            setAttribute(row, "class", `row${vulnerability.severity}`);
            // Column 0: Numerical index
            row.appendChild(getTextCell(vuln_idx.toString()));
            // Column 1: File name (links to source if build-info is present)
            const file_display = `${vulnerability.location.file}:${vulnerability.location.start_line}`;
            if (base_url != null) {
                row.appendChild(
                    getLinkCell(
                        file_display,
                        `${base_url}/${vulnerability.location.file}#L${vulnerability.location.start_line}`
                    )
                );
            } else {
                row.appendChild(getTextCell(file_display));
            }
            // Column 2: Vulnerability identifier(s)
            const cve_cell = document.createElement("td");
            cve_cell.appendChild(getParagraph(vulnerability.cve));
            const other_links_details = getDetails("identifiers:"); 
            const cve_see_also_list = document.createElement("ul");
            vulnerability.identifiers.forEach(
                function(identifier, idx, ar) {
                    const id_label = `${identifier.type}:${identifier.value}`;
                    const id_item = document.createElement("li");
                    setAttribute(id_item, "title", identifier.name);
                    if (identifier.url != null) {
                        id_item.appendChild(getLink(id_label, identifier.url));
                    } else {
                        id_item.appendChild(document.createTextNode(id_label));
                    }
                    cve_see_also_list.appendChild(id_item);
                }
            );
            other_links_details.appendChild(cve_see_also_list)
            cve_cell.appendChild(other_links_details)
            row.appendChild(cve_cell);
            // Column 3: Severity, colored
            row.appendChild(getSeverityCell(vulnerability.severity));
            // Column 4: Message
            row.appendChild(getTextCell(vulnerability.message));
            // Column 5: Long description
            row.appendChild(getTextCell(vulnerability.description));
            tbody.appendChild(row);
        }
    );
    table.appendChild(tbody);
    // Write table output only if any vulnerability was found
    if (items_map.size > 0) {
        body_main.appendChild(getHeadline(2, "Found vulnerabilities:"));
        body_main.appendChild(table);
    }
    return items_map;
}
  
function writeSecretDetectionTable(body_main, vulnerabilities, build_info) {
    // Write a table containing the found vulnerabilities
    // from the secret detection report,
    // and return a mapping of cve lists per severity per file name
    const items_map = new Map();
    const table = getTable(
        ["#", "Location", "Vulnerability", "Severity", "Message", "Description"]
    );
    const tbody = document.createElement("tbody");
    vulnerabilities.forEach(
        function(vulnerability, vuln_idx, ar) {
            // Build base URL per vulnerability if build info is available
            let base_url = null;
            if (
                (build_info.ci_project_url != null) && (vulnerability.location.commit != null)
            ) {
                base_url = `${build_info.ci_project_url}/-/blob/${vulnerability.location.commit.sha}`
            }
            // Track vulnerabilities by file names
            updateItemsMap(
                items_map,
                vulnerability.location.file,
                vulnerability.severity,
                vulnerability.cve
            );
            // Output one row per vulnerability
            const row = document.createElement("tr");
            setAttribute(row, "class", `row${vulnerability.severity}`);
            // Column 0: Numerical index
            row.appendChild(getTextCell(vuln_idx.toString()));
            // Column 1: File name (links to source if build-info is present)
            const file_display = `${vulnerability.location.file}:${vulnerability.location.start_line}`;
            if (base_url != null) {
                row.appendChild(
                    getLinkCell(
                        file_display,
                        `${base_url}/${vulnerability.location.file}#L${vulnerability.location.start_line}`
                    )
                );
            } else {
                row.appendChild(getTextCell(file_display));
            }
            // Column 2: Vulnerability name
            row.appendChild(getTextCell(vulnerability.name));
            // Column 3: Severity, colored
            row.appendChild(getSeverityCell(vulnerability.severity));
            // Column 4: Message
            row.appendChild(getTextCell(vulnerability.message));
            // Column 5: Long description
            row.appendChild(getTextCell(vulnerability.description));
            tbody.appendChild(row);
        }
    );
    table.appendChild(tbody);
    // Write table output only if any vulnerability was found
    if (items_map.size > 0) {
        body_main.appendChild(getHeadline(2, "Found vulnerabilities:"));
        body_main.appendChild(table);
    }
    return items_map;
}

function writeResults(json_data, report_type, header, report_url, build_info) {
    // Append the metadata table to the header,
    // write scan results to main (according to the report type),
    // then append statistics to the headee
    header.appendChild(
        getMetadataTable(json_data.scan, report_url, build_info)
    );
    const body_main = document.getElementsByTagName("main")[0];
    let items_map = null;
    switch (report_type) {
        case "container-scanning":
            items_map = writeContainerScanTable(
                body_main, json_data.vulnerabilities, build_info
            );
            break;
        case "sast":
            items_map = writeSASTTable(
                body_main, json_data.vulnerabilities, build_info
            );
            break;
        case "secret-detection":
            items_map = writeSecretDetectionTable(
                body_main, json_data.vulnerabilities, build_info
            );
            break;
        default:
            items_map = new Map();
            const error_paragraph = getParagraph(
                `Report type "${report_type}" support is planned, but not implemented yet.`
            );
            setAttribute(error_paragraph, "class", "error");
            body_main.appendChild(error_paragraph);
            break;
    }
    header.appendChild(getVulnerabilityStatistics(items_map));
}

function writeError(error_data, header, report_url) {
    // Print an error message in the header area
    const error_paragraph = document.createElement("p");
    setAttribute(error_paragraph, "class", "error");
    error_paragraph.appendChild(
        document.createTextNode('Report JSON file "')
    );
    error_paragraph.appendChild(getLink(report_url, report_url));
    error_paragraph.appendChild(
        document.createTextNode(`" could not be loaded (${error_data})`)
    );
    header.appendChild(error_paragraph);
}

function visualizeReport() {
    // Parse the query string and process the report accordingly
    const params = (new URL(document.location)).searchParams;
    const report_type = params.get("type");
    let report_url = `gl-${report_type}-report.json`;
    if (params.has("filename")) {
        report_url = params.get("filename");
    }
    let supported_report_type = true;
    let page_title = "Unsupported report type";
    switch (report_type) {
        case "container-scanning":
            page_title = "Container Scanning Report";
            break;
        case "sast":
            page_title = "SAST Report";
            break;
        case "secret-detection":
            page_title = "Secret Detection Report";
            break;
        default:
            supported_report_type = false;
            break;
    }
    const header = document.getElementsByTagName("header")[0];
    header.appendChild(getHeadline(1, page_title));
    document.title = page_title;
    if (! supported_report_type) {
        const error_paragraph = getParagraph(
            `Report type "${report_type}" is not supported.`
        );
        setAttribute(error_paragraph, "class", "error");
        header.appendChild(error_paragraph);
        return;
    }
    fetch(
        "build-info.json", {cache: "no-cache"}
    ).then(
        bi_response => bi_response.json()
    ).then(
        build_info_json => {
            fetch(
                report_url, {cache: "no-cache"}
            ).then(
                (response) => response.json()
            ).then(
                (json_data) => writeResults(
                    json_data, report_type, header, report_url, build_info_json
                )
            ).catch(
                (err) => {
                    writeError(err, header, report_url);
                    return;
                }
            );
        }
    ).catch(
        (err) => {
            fetch(
                report_url, {cache: "no-cache"}
            ).then(
                (response) => response.json()
            ).then(
                (json_data) => writeResults(
                    json_data,
                    report_type,
                    header,
                    report_url,
                    {"ci_project_url": null}
                )
            ).catch(
                (err) => {
                    writeError(err, header, report_url);
                    return;
                }
            );
        }
    );
}

