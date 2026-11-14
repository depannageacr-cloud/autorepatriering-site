# Migration checkpoint — 2026-11-14

Website source is fully copied and deployed to OVH, but the production DNS has NOT been switched.

- Repository: depannageacr-cloud/autorepatriering-site
- OVH service: gxmvgeh.cluster130.hosting.ovh.net
- Website ID: 4332530, directory autorepatriering
- Successful deployment: 183341, commit 569f8369edd174f22fc8cb0fc9e1591da4bd7d72
- Five existing URLs preserved: homepage plus autotransport-italie, -frankrijk, -duitsland and -luxemburg.
- Native PHP quote form on /#offerte; recipient depannageacr@hotmail.com. Not yet tested end to end because HTTPS is pending.

DNS at Combell remains authoritative. Production root A records remain 3.125.172.46 and 3.73.27.108; www remains 2ec9c8c348264a8f8905271bad877bed.webbuilder-online.com. Their TTLs were reduced from 3600 to 300. Mail records and nameservers were not changed. Original records are in dns-before.json.

ovhcontrol TXT was added and publicly verified. A second verification TXT at ovhcontrol.www was also added based on the initial OVH notice. Both production domain attachments are now created (taskId null). Its value is obtained from the authenticated OVH console; do not copy OAuth credentials. A temporary ovh-test.autorepatriering.be A record was moved from 149.202.25.75 (NL) to 145.239.37.162 (FR), TTL 300. Public DNS verified the new address. That hostname is attached to the same directory and is active. A temporary HTTPS-only canonical redirect exception and noindex response header are in .htaccess.

SSL update, 2026-11-14 09:20 UTC: the staging certificate became Active in the OVH panel, but strict browser checks still received ERR_CERT_COMMON_NAME_INVALID. An independent TLS inspection on the original 149.202.25.75 endpoint confirmed the server was presenting the default cluster130.hosting.ovh.net certificate, not the staging hostname. Reapplying ssl=true did not resolve the issue; virtual-host restart is unsupported on hosting-pro. The staging domain ipLocation and its public A record were changed to FR / 145.239.37.162, but strict browser validation still failed. Staging certificate regeneration was requested; current task 508952961 has status regenerating. No security warning was bypassed. Production root/www certificates remain in creation while their A/CNAME still point at Combell.

Continue:
1. Wait for the staging regeneration task to finish and confirm that its actual TLS endpoint serves the correct certificate; if it still serves cluster130.hosting.ovh.net, escalate to OVH with user authorization. Check test-host SSL creation, then open it normally over HTTPS and test all pages plus a clearly labelled request to the owner's mailbox; check Junk folder as well as Inbox.
2. Change production root A to the confirmed OVH hosting IP 145.239.37.162 (FR; use matching ipLocation after confirmation) (replace one old entry and remove the other after preserving it). Change www CNAME to autorepatriering.be. Keep all mail DNS records and nameservers.
3. Confirm both root and www attached domains finish creating; check/regenerate their Let's Encrypt certificates if required, then verify the live production page, redirects, sitemap and form receipt.
4. Remove temporary test DNS and domain mapping once production is verified, and restore the ordinary canonical-host rule by removing the staging exception/noindex block from .htaccess and build source. Keep sources and the original DNS rollback record.
5. Do not cancel Combell products or perform a paid registrar transfer without a separate instruction. This migration changes website hosting, not registrar or mail.
