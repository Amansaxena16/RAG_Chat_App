# NovaTech Engineering: Architecture Overview

## High-Level Architecture

NovaTech's three products (NovaBoard, NovaChat, NovaSync) are built as separate services that share common infrastructure:

- **Auth Service**: handles login, SSO (SAML/SCIM for Enterprise), and session tokens for all three products. Written in Go.
- **Unified Search Service**: indexes content from all three products into a single Elasticsearch cluster, exposed via an internal gRPC API. Available only to organizations on Growth or Enterprise plans.
- **Event Bus**: a Kafka-based system that carries cross-product events, such as "NovaChat message converted to NovaBoard card" or "NovaSync file shared in NovaChat channel."
- **Billing Service**: tracks seats, plan tier, and usage across all products, and is the source of truth consulted by feature flags that gate plan-specific functionality (e.g., automation rule limits).

## Per-Product Stacks

**NovaBoard** — Ruby on Rails monolith for the core app, with a separate Go service ("rules-engine") that evaluates automation rules asynchronously off the event bus. PostgreSQL is the primary datastore.

**NovaChat** — Elixir/Phoenix backend, chosen originally for WebSocket concurrency at scale. Message storage is in Cassandra, chosen for high write throughput on message history.

**NovaSync** — Python backend for file metadata and sharing logic, with actual file bytes stored in S3-compatible object storage. Real-time co-editing uses a CRDT (conflict-free replicated data type) library run in a separate Node.js service called "sync-rtc."

## Deployment

All services deploy to Kubernetes clusters on AWS, one cluster per region (US, EU, India) to support Enterprise data residency requirements. Deploys go through a shared CI/CD pipeline (GitHub Actions → ArgoCD) regardless of which product or language the service uses.

Engineering pods can deploy independently of each other; there is no company-wide release train. This is the technical backing for the "ship small, ship often" company value.

## Data Residency Implementation Note

Because Enterprise customers can choose US, EU, or India residency, every service that stores customer data must be region-aware: a customer's organization ID maps to a "home region," and requests are routed to that region's cluster at the API gateway layer. Cross-region requests (e.g., a US-based employee accessing an EU-resident organization's NovaSync files as a guest) are proxied through a dedicated cross-region gateway service rather than allowed to hit the regional cluster directly.

## On Unified Search Availability

Because Unified Search depends on the shared Elasticsearch cluster and event bus, and those are only provisioned for organizations on Growth or Enterprise plans (see Pricing and Plans), the Starter-plan code path skips indexing entirely rather than indexing-and-hiding — this was a deliberate cost decision made by Marcus Chen's team in 2023 after Elasticsearch costs for Starter-plan organizations (who could not use search anyway) were found to be disproportionate.
