---
schema_version: 4.2.0
id: T-DEMO-0001
entity_type: task
title: 'DEMO: Verify the tracker'
revision: 1
status: inbox
demo: true
aliases: []
summary: 'DEMO: Verify the tracker'
sources: []
links:
- rel: implements
  to: I-DEMO-0001.1
signal_refs: []
trackerStatus:
  type: pm-task
priority: low
idea_id: I-DEMO-0001.1
agent: coordinator
procedure: setup
model_profile: standard
goal: Verify full-document cards
output_format: setup report
input_manifest: []
tools_allowed:
- Read
allowed_write_paths:
- artifacts/I-DEMO-0001/
no_gos:
- external writes
acceptance:
- 4 types and 5 tracked cards visible
budget:
  max_retries: 0
  max_parallel: 1
stop_conditions:
- missing access
---

# DEMO: Verify the tracker
Synthetic structural fixture, NOT evidence about actual product. Owner quote/real baseline/code not provided. Signals table deliberately empty; signal_refs=[].
For idea/iteration links see frontmatter. Planned work never becomes current feature automatically.
