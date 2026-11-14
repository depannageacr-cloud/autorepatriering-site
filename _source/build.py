from pathlib import Path
from html import escape
import base64, hashlib, json, re

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent
ASSETS=OUT/'assets'; ASSETS.mkdir(exist_ok=True)
BASE='https://www.autorepatriering.be'
pages=['home','italie','frankrijk','duitsland','luxemburg']
extra='''html,body{margin:0;padding:0}.ar-site{min-height:100%}body{padding-bottom:65px}.ar-request{background:#17191d;padding:28px;border:1px solid #45484f;margin:25px 0}.ar-request-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.ar-request label{display:flex;flex-direction:column;gap:8px;font-size:15px;font-weight:700}.ar-request input,.ar-request textarea{width:100%;min-width:0;padding:13px;border:1px solid #62656d;border-radius:3px;font:inherit;background:#0c0d0f;color:#fff;box-sizing:border-box}.ar-request .full{grid-column:1/-1}.ar-request textarea{min-height:150px}.ar-request button{font:inherit;cursor:pointer;border:0}.ar-trap{position:absolute;left:-10000px}.ar-notice{border:2px solid #8acb81;background:#19341d;padding:20px;margin:22px 0}.ar-error{background:#471f19;border-color:#e2a091}.ar-sticky{position:fixed;right:22px;bottom:18px;z-index:9999;display:flex;box-shadow:0 5px 24px #0008;font:700 15px Arial,sans-serif}.ar-sticky a{padding:18px 23px;background:#ffd23e;color:#111;text-decoration:none}.ar-sticky a:last-child{background:#075e54;color:#fff}.ar-sticky a:hover{filter:brightness(1.12)}@media(max-width:680px){.ar-request-grid{grid-template-columns:1fr}.ar-request{padding:20px}.ar-sticky{left:0;right:0;bottom:0}.ar-sticky a{width:50%;padding:18px 8px;text-align:center}}'''
sticky='<nav class="ar-sticky" aria-label="Snel contact"><a href="tel:+32471379064">Bel 0471 37 90 64</a><a href="https://wa.me/32471379064?text=Ik%20wil%20internationaal%20voertuigtransport%20aanvragen.">WhatsApp ↗</a></nav>'
form='''<div class="ar-request">
<?php if ($sent): ?><div class="ar-notice" role="status"><strong>Bedankt voor je transportaanvraag.</strong><p>De mailserver heeft je aanvraag aangenomen voor verzending naar ACR. Je transport is pas geboekt na onze bevestiging. Dringend of nog geen antwoord? Bel <a href="tel:+32471379064">0471 37 90 64</a>.</p></div><?php endif; ?>
<?php if ($error!==''): ?><div class="ar-notice ar-error" role="alert"><?=h($error)?></div><?php endif; ?>
<form action="/#offerte" method="post"><input type="hidden" name="token" value="<?=h($_SESSION['token'])?>"><div class="ar-trap" aria-hidden="true"><label>Laat leeg<input name="website" tabindex="-1" autocomplete="off"></label></div><div class="ar-request-grid"><label>Uw naam *<input name="naam" maxlength="120" autocomplete="name" required value="<?=h($values['naam'])?>"></label><label>E-mailadres *<input name="email" type="email" maxlength="254" autocomplete="email" required value="<?=h($values['email'])?>"></label><label>Telefoonnummer<input name="telefoon" type="tel" maxlength="50" autocomplete="tel" value="<?=h($values['telefoon'])?>"></label><label>Gewenste periode<input name="tijd" maxlength="200" value="<?=h($values['tijd'])?>"></label><label class="full">Voertuig of lading<input name="wagen" maxlength="350" placeholder="Merk, model, afmetingen, massa en rijdbaarheid" value="<?=h($values['wagen'])?>"></label><label class="full">Bericht *<textarea name="bericht" rows="7" maxlength="5000" required placeholder="Vermeld laad- en afleveradres, voertuiggegevens en eventuele afhaaldeadline."><?=h($values['bericht'])?></textarea></label></div><p class="ar-mini" style="margin-top:18px">Je gegevens gaan per e-mail naar ACR om je aanvraag te behandelen. Foto’s kun je via WhatsApp delen. Velden met * zijn verplicht.</p><button class="ar-btn" type="submit">Verstuur transportaanvraag</button></form></div>'''
backend=(ROOT/'source'/'mail-handler.php').read_text()
urls=[]; manifest=[]
for name in pages:
    d=json.loads((ROOT/'source'/(name+'.json')).read_text())
    body=''.join(d['roots'])
    # Keep all original sections and native details, with the normal collapsed initial state.
    body=re.sub(r'(<details\b[^>]*?)\sopen(?:="[^"]*")?',r'\1',body)
    def image(m):
        data=base64.b64decode(m.group(2)); filename=hashlib.sha256(data).hexdigest()[:16]+'.'+m.group(1)
        (ASSETS/filename).write_bytes(data)
        return '/assets/'+filename
    body=re.sub(r'data:image/(\w+);base64,([A-Za-z0-9+/=]+)',image,body)
    css='\n'.join(d['styles'])+'\n'+extra
    cssname=name+'.css';(ASSETS/cssname).write_text(css)
    if name=='home':
        # Insert inside the existing offer section, before the closing section tag.
        start=body.index('<section class="ar-section ar-quote" id="offerte">')
        end=body.index('</section>',start)
        body=body[:end]+form+body[end:]
    slug='' if name=='home' else 'autotransport-'+name+'/'
    url=BASE+'/'+slug; urls.append(url)
    schema=''.join('<script type="application/ld+json">'+s.replace('</','<\\/')+'</script>' for s in d['schema'])
    html='<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(d['title'])+'</title><meta name="description" content="'+escape(d['description'],quote=True)+'"><link rel="canonical" href="'+url+'"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:type" content="website"><meta property="og:title" content="'+escape(d['title'],quote=True)+'"><meta property="og:description" content="'+escape(d['description'],quote=True)+'"><meta property="og:url" content="'+url+'"><link rel="stylesheet" href="/assets/'+cssname+'">'+schema+'</head><body>'+body+sticky+'</body></html>'
    dest=OUT/slug;dest.mkdir(exist_ok=True)
    (dest/('index.php' if name=='home' else 'index.html')).write_text((backend if name=='home' else '')+html)
    manifest.append({'url':url,'title':d['title'],'h1':len(re.findall('<h1',html)),'sections':len(re.findall('<details',html))})
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>')
(OUT/'404.html').write_text('<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pagina niet gevonden | ACR</title></head><body><h1>Pagina niet gevonden</h1><p><a href="/">Naar ACR voertuigtransport</a></p><p><a href="/#offerte">Vraag transport aan</a></p></body></html>')
(OUT/'.htaccess').write_text('''Options -Indexes
DirectoryIndex index.php index.html
ErrorDocument 404 /404.html
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule ^\\.git(?:/|$) - [F,L]
RewriteRule ^_source(?:/|$) - [F,L]
RewriteRule ^\\.well-known/acme-challenge/ - [L]
RewriteCond %{HTTP_HOST} ^ovh-test\.autorepatriering\.be$ [NC]
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://ovh-test.autorepatriering.be%{REQUEST_URI} [R=301,L,NE]
RewriteCond %{HTTP_HOST} !^ovh-test\.autorepatriering\.be$ [NC]
RewriteCond %{HTTPS} !=on [OR]
RewriteCond %{HTTP_HOST} !^www\\.autorepatriering\\.be$ [NC]
RewriteRule ^ https://www.autorepatriering.be%{REQUEST_URI} [R=301,L,NE]
</IfModule>
<IfModule mod_setenvif.c>
SetEnvIf Host "^ovh-test\.autorepatriering\.be$" REPAT_STAGING
</IfModule>
<IfModule mod_headers.c>
Header always set X-Robots-Tag "noindex, nofollow" env=REPAT_STAGING
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>
''')
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'pages':len(urls),'assets':len(list(ASSETS.iterdir())),'all_h1_valid':all(p['h1']==1 for p in manifest)}))
