"""Lightweight tech-stack fingerprint (a tiny, offline Wappalyzer).

Markers are distinctive substrings — script/CDN URLs, framework runtime hooks,
CMS paths — matched against the already-downloaded HTML. It's a heuristic, not a
guarantee, but it's a cheap signal of how modern/technical a company's site is.
Detection is limited to what shows up in HTML (we don't keep response headers).
"""
import re

# tech name -> list of lowercase markers; any hit tags the tech.
TECH_MARKERS = {
    # Frontend frameworks
    "Next.js": ["/_next/", "__next_data__"],
    "React": ["data-reactroot", "react-dom", "reactdom"],
    "Vue.js": ["data-v-", "__vue__", "vue.runtime"],
    "Nuxt": ["__nuxt", "/_nuxt/"],
    "Angular": ["ng-version", "ng-app", "angular.js"],
    "Svelte": ["svelte-", "__sveltekit"],
    "Gatsby": ["___gatsby", "gatsby-"],
    "Ember.js": ["ember-application", "ember.js"],
    # Site builders / CMS
    "WordPress": ["wp-content", "wp-includes", "wp-json"],
    "Webflow": ["assets.website-files.com", "assets-global.website-files.com", "wf-"],
    "Wix": ["wixstatic.com", "static.wixstatic", "_wix"],
    "Squarespace": ["squarespace.com", "static1.squarespace"],
    "Shopify": ["cdn.shopify.com", "shopify.com/s/"],
    "Ghost": ["ghost.io", "content=\"ghost"],
    "HubSpot CMS": ["hs-scripts.com", "hubspotusercontent"],
    "Framer": ["framerusercontent.com", "framer.com"],
    # Analytics / marketing
    "Google Analytics": ["google-analytics.com", "gtag(", "ga('create'"],
    "Google Tag Manager": ["googletagmanager.com", "gtm.js"],
    "Segment": ["cdn.segment.com", "analytics.min.js"],
    "Hotjar": ["static.hotjar.com", "hotjar.com"],
    "Mixpanel": ["cdn.mxpnl.com", "mixpanel"],
    "Amplitude": ["cdn.amplitude.com", "amplitude.js"],
    "Facebook Pixel": ["connect.facebook.net", "fbq("],
    # Support / chat / CRM widgets
    "Intercom": ["widget.intercom.io", "intercomcdn"],
    "Drift": ["js.driftt.com", "drift.com"],
    "Zendesk": ["zdassets.com", "zendesk.com"],
    "HubSpot": ["js.hs-scripts.com", "js.hsforms.net"],
    # Infra / CDN (HTML-visible only)
    "Cloudflare": ["cdn-cgi/", "cloudflareinsights.com"],
    "jsDelivr": ["cdn.jsdelivr.net"],
    "cdnjs": ["cdnjs.cloudflare.com"],
    "AWS CloudFront": ["cloudfront.net"],
    # Libraries / UI
    "jQuery": ["jquery.min.js", "jquery/"],
    "Bootstrap": ["bootstrap.min.css", "bootstrap.bundle"],
    "Tailwind CSS": ["tailwindcss", "cdn.tailwindcss.com"],
    "Font Awesome": ["font-awesome", "fontawesome"],
    # Payments / scheduling / forms
    "Stripe": ["js.stripe.com"],
    "Calendly": ["calendly.com"],
    "Typeform": ["typeform.com"],
}

# schema.org / <meta name="generator"> content keyword -> normalized name.
_GENERATOR_RE = re.compile(
    r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_GENERATOR_MAP = {
    "wordpress": "WordPress",
    "wix": "Wix",
    "webflow": "Webflow",
    "squarespace": "Squarespace",
    "shopify": "Shopify",
    "ghost": "Ghost",
    "hugo": "Hugo",
    "jekyll": "Jekyll",
    "gatsby": "Gatsby",
    "drupal": "Drupal",
    "joomla": "Joomla",
    "framer": "Framer",
}


def detect_tech(html):
    """Return a sorted list of detected technologies (empty on no match)."""
    if not html:
        return []
    low = html.lower()
    found = set()

    for tech, markers in TECH_MARKERS.items():
        if any(m in low for m in markers):
            found.add(tech)

    for gen in _GENERATOR_RE.findall(html):
        g = gen.lower()
        for key, name in _GENERATOR_MAP.items():
            if key in g:
                found.add(name)

    return sorted(found)
