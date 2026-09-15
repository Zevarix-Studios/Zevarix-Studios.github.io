# Public Site Publication Boundary

`Zevarix-Studios/Zevarix-Studios.github.io` is the public publication repository for `https://zevarix.com/`.

The private `Zevarix-Studios/brand` repository remains the source of truth for the locked Zevarix Studios visual identity and canonical private brand assets. The two repositories are related, but they are not byte-for-byte mirrors.

## Intentional public-only state

This repository owns publication-specific state including:

- `CNAME` for `zevarix.com`;
- `robots.txt` and `sitemap.xml`;
- canonical/Open Graph/Twitter metadata;
- the IndexNow key and notification workflow;
- `.nojekyll`;
- `site-public-brand.css`;
- public rendering choices that use the organization avatar rather than publishing the private canonical asset tree wholesale.

These differences are deliberate and must survive ordinary site updates.

## Sync rule

Do not blindly mirror the private Brand repository into this repository.

Any future automated Brand-to-public-site synchronization must define an explicit allowlist or transformation contract that states:

- which source files are shared;
- which public files are preserved;
- how public metadata/adaptations are applied;
- what validation proves the resulting site source;
- what authority is allowed to open/update the publication change.

A source synchronization operation must not itself gain Pages deployment authority.

## CI placement

This repository is public, so repository validation stays on GitHub-hosted runners under the current Zevarix Studios trust model. The private `home-ci` organization runner group remains public-repository-disabled.

Static source validation protects repository invariants only. Browser rendering, accessibility quality, search ranking, and live Pages health require separate evidence when those surfaces materially change.
