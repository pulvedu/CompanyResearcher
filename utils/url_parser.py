from urllib.parse import urlparse
from urllib.parse import urlparse
from collections import defaultdict
import re

def extract_domain_parts(url):
    """
    This is a helper function used to group URLs based on their domain patterns.
    The function extracts the main domain, subdomain, and tld from a URL.
    """
    parsed = urlparse(url)
    if not parsed.netloc:
        return None, None, None
    
    # Split domain into parts
    parts = parsed.netloc.split('.')
    
    # Remove 'www' if present
    if parts[0] == 'www':
        parts = parts[1:]
    
    # Handle cases with subdomain
    if len(parts) > 2:
        subdomain = parts[0]
        main_domain = parts[1]
        tld = '.'.join(parts[2:])
    else:
        subdomain = ''
        main_domain = parts[0]
        tld = parts[1] if len(parts) > 1 else ''
    
    return main_domain, subdomain, tld

def group_urls(urls):
    """
    This is a helper function used to group URLs based on their domain patterns.
    """
    # Remove duplicates while maintaining order
    urls = list(dict.fromkeys(urls))
    
    # Initialize grouping structures
    domain_groups = defaultdict(list)
    domain_info = {}
    
    # First pass: collect domain information
    for url in urls:
        main_domain, subdomain, tld = extract_domain_parts(url)
        if main_domain:
            domain_info[url] = {
                'main_domain': main_domain,
                'subdomain': subdomain,
                'tld': tld,
                'full_domain': f"{subdomain}.{main_domain}.{tld}" if subdomain else f"{main_domain}.{tld}"
            }
    # Find similar domain patterns
    domain_patterns = defaultdict(list)
    for url, info in domain_info.items():
        main_domain = info['main_domain']
        # Create a simplified version of the domain for pattern matching
        simplified = re.sub(r'[0-9]', '', main_domain.lower())
        domain_patterns[simplified].append(url)
    # Group URLs based on patterns
    for urls in domain_patterns.values():
        if urls:
            # Use the first URL's main domain as the group name
            sample_info = domain_info[urls[0]]
            group_name = sample_info['main_domain'].capitalize()
            # Add all related URLs to this group
            for url in urls:
                domain_groups[group_name].append(url)
    
    # Add remaining URLs to 'Others' group
    all_grouped = set(url for group in domain_groups.values() for url in group)
    remaining = set(urls) - all_grouped
    if remaining:
        domain_groups['Others'] = list(remaining)
    
    return dict(domain_groups)